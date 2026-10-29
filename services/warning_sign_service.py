"""Transparent warning-sign rules for job postings.

These rules are advisory indicators, not a verdict or a calibrated scam score.
They deliberately do not fetch URLs or contact employers.
"""

from __future__ import annotations

import re
from typing import Any

_RULES: tuple[dict[str, Any], ...] = (
    {
        "id": "upfront_fee",
        "category": "Payment request",
        "severity": "high",
        "title": "Upfront fee or deposit mentioned",
        "pattern": re.compile(
            r"\b(?:registration|application|processing|training|security|verification|placement|interview|onboarding|equipment)\s+(?:fee|fees|charge|charges|deposit|payment)s?\b|\brefundable\s+(?:fee|deposit|payment)\b|\bpay\s+(?:a|an|the)\s+(?:fee|deposit|charge)\b",
            re.IGNORECASE,
        ),
        "explanation": "Legitimate employers generally do not require applicants to pay to apply, interview, or receive a job offer.",
        "recommendation": "Do not pay or share payment credentials. Verify the employer through contact details found independently.",
    },
    {
        "id": "sensitive_documents",
        "category": "Sensitive information",
        "severity": "high",
        "title": "Sensitive identity or banking details requested",
        "pattern": re.compile(
            r"\b(?:send|share|upload|submit|provide|email|whatsapp)\s+(?:(?:us|me)\s+)?(?:your\s+)?(?:aadhaar(?:\s+card)?|pan(?:\s+card)?|passport|bank\s+(?:account|details|statement)|account\s+number|otp|one[- ]time\s+password|upi\s+pin|debit\s+card|credit\s+card)\b",
            re.IGNORECASE,
        ),
        "explanation": "Identity documents, one-time passwords, UPI PINs, and banking details can be misused when shared with an unverified recruiter.",
        "recommendation": "Do not share OTPs, PINs, card credentials, or identity documents before independently verifying the employer and the need for the information.",
    },
    {
        "id": "guaranteed_income",
        "category": "Unrealistic promise",
        "severity": "medium",
        "title": "Guaranteed earnings or placement promised",
        "pattern": re.compile(
            r"\b(?:guaranteed|assured)\s+(?:income|earnings|salary|job|placement|selection)\b|\b100\s*%\s*(?:guaranteed|assured)\b",
            re.IGNORECASE,
        ),
        "explanation": "Claims of guaranteed pay, selection, or placement can be used to pressure applicants into paying fees or sharing data.",
        "recommendation": "Ask for a written job description and verify the opening on the company's official careers site.",
    },
    {
        "id": "urgent_pressure",
        "category": "Pressure tactics",
        "severity": "medium",
        "title": "Urgent or high-pressure language found",
        "pattern": re.compile(
            r"\b(?:act now|apply immediately|respond immediately|limited slots?|today only|urgent hiring|within\s+\d+\s+hours?|pay today|offer expires today)\b",
            re.IGNORECASE,
        ),
        "explanation": "Artificial deadlines can discourage applicants from checking the employer or reading the terms carefully.",
        "recommendation": "Take time to verify the employer and offer. A deadline is not a reason to skip basic checks.",
    },
    {
        "id": "messaging_app_only",
        "category": "Recruitment channel",
        "severity": "low",
        "title": "Recruitment may be routed through a messaging app",
        "pattern": re.compile(
            r"\b(?:contact|message|interview|apply|send (?:your )?details)\s+(?:us\s+)?(?:only\s+)?(?:on\s+)?(?:whatsapp|telegram)\b|\bwhatsapp\s+only\b|\btelegram\s+only\b",
            re.IGNORECASE,
        ),
        "explanation": "Messaging apps are used by legitimate recruiters too, but a process with no independently verifiable company contact deserves extra checking.",
        "recommendation": "Confirm the recruiter and vacancy through the employer's official website or published phone number.",
    },
)

_FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "yahoo.co.in",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "rediffmail.com",
    "icloud.com",
}
_SHORT_LINK_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at",
}


def _is_negated(text: str, start: int) -> bool:
    """Skip simple denials such as 'no registration fee'."""
    prefix = text[max(0, start - 45):start].lower()
    return bool(
        re.search(
            r"\b(?:no|not|never|without|don't|doesn't|do not|does not)\s+(?:(?:require|charge|pay|any|a|an|the|registration|application|processing|training)\s+){0,4}$",
            prefix,
        )
    )


def _evidence_match(pattern: re.Pattern[str], text: str) -> re.Match[str] | None:
    for match in pattern.finditer(text):
        if not _is_negated(text, match.start()):
            return match
    return None


def get_rule_registry() -> list[dict[str, str]]:
    """Return public metadata for every active rule, without regex internals."""
    rules = [
        {
            "id": str(rule["id"]),
            "category": str(rule["category"]),
            "severity": str(rule["severity"]),
            "title": str(rule["title"]),
            "explanation": str(rule["explanation"]),
            "recommendation": str(rule["recommendation"]),
        }
        for rule in _RULES
    ]
    rules.extend(
        [
            {
                "id": "free_mail_recruiter",
                "category": "Recruiter identity",
                "severity": "low",
                "title": "Recruiter uses a public email provider",
                "explanation": "A public email provider does not prove fraud, but the recruiter's identity and relationship to the employer need independent verification.",
                "recommendation": "Look up the employer's official domain and contact its published recruitment team to confirm the person and vacancy.",
            },
            {
                "id": "shortened_job_link",
                "category": "Link transparency",
                "severity": "medium",
                "title": "Job link uses a URL shortener",
                "explanation": "A shortened link hides its destination until it is opened. This tool does not open or inspect links.",
                "recommendation": "Ask for the direct employer careers URL and inspect the destination safely before entering any personal information.",
            },
        ]
    )
    return rules


def analyze_warning_signs(data: dict[str, str]) -> list[dict[str, str]]:
    """Find explainable warning indicators in submitted, untrusted text."""
    combined_text = "\n".join(
        data.get(field, "")
        for field in (
            "job_title",
            "job_description",
            "requirements",
            "benefits",
            "company_profile",
            "salary_range",
        )
        if data.get(field)
    )
    findings: list[dict[str, str]] = []

    for rule in _RULES:
        match = _evidence_match(rule["pattern"], combined_text)
        if match:
            findings.append(
                {
                    "rule_id": str(rule["id"]),
                    "category": str(rule["category"]),
                    "severity": str(rule["severity"]),
                    "title": str(rule["title"]),
                    "explanation": str(rule["explanation"]),
                    "recommendation": str(rule["recommendation"]),
                    "evidence": match.group(0)[:300],
                }
            )

    recruiter_email = data.get("recruiter_email", "").strip()
    if "@" in recruiter_email:
        domain = recruiter_email.rsplit("@", 1)[-1].lower().rstrip(".")
        if domain in _FREE_EMAIL_DOMAINS:
            findings.append(
                {
                    "rule_id": "free_mail_recruiter",
                    "category": "Recruiter identity",
                    "severity": "low",
                    "title": "Recruiter uses a public email provider",
                    "explanation": "A public email provider does not prove fraud, but the recruiter's identity and relationship to the employer need independent verification.",
                    "recommendation": "Look up the employer's official domain and contact its published recruitment team to confirm the person and vacancy.",
                    "evidence": recruiter_email[:300],
                }
            )

    job_url = data.get("job_url", "").strip()
    if job_url:
        try:
            from urllib.parse import urlsplit

            hostname = (urlsplit(job_url).hostname or "").lower().rstrip(".")
        except ValueError:
            hostname = ""
        if hostname in _SHORT_LINK_DOMAINS:
            findings.append(
                {
                    "rule_id": "shortened_job_link",
                    "category": "Link transparency",
                    "severity": "medium",
                    "title": "Job link uses a URL shortener",
                    "explanation": "A shortened link hides its destination until it is opened. This tool does not open or inspect links.",
                    "recommendation": "Ask for the direct employer careers URL and inspect the destination safely before entering any personal information.",
                    "evidence": hostname,
                }
            )

    return findings


def enrich_stored_findings(findings: list[Any]) -> list[dict[str, str]]:
    """Rebuild explanation text for saved findings using the current registry."""
    registry = {rule["id"]: rule for rule in get_rule_registry()}
    extras = {
        "free_mail_recruiter": {
            "category": "Recruiter identity",
            "severity": "low",
            "title": "Recruiter uses a public email provider",
            "explanation": "A public email provider does not prove fraud, but the recruiter's identity and relationship to the employer need independent verification.",
            "recommendation": "Look up the employer's official domain and contact its published recruitment team to confirm the person and vacancy.",
        },
        "shortened_job_link": {
            "category": "Link transparency",
            "severity": "medium",
            "title": "Job link uses a URL shortener",
            "explanation": "A shortened link hides its destination until it is opened. This tool does not open or inspect links.",
            "recommendation": "Ask for the direct employer careers URL and inspect the destination safely before entering any personal information.",
        },
    }
    enriched: list[dict[str, str]] = []
    for item in findings:
        rule_id = str(item.rule_id)
        metadata = registry.get(rule_id, extras.get(rule_id))
        if not metadata:
            continue
        enriched.append(
            {
                "rule_id": rule_id,
                "category": str(item.category or metadata["category"]),
                "severity": str(item.severity or metadata["severity"]),
                "title": str(metadata["title"]),
                "explanation": str(metadata["explanation"]),
                "recommendation": str(metadata["recommendation"]),
                "evidence": str(item.evidence or ""),
            }
        )
    return enriched
