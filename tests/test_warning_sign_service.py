"""Regression tests for transparent rule-based job warning indicators."""

from services.warning_sign_service import analyze_warning_signs, get_rule_registry


def test_finds_upfront_fee_and_returns_evidence():
    findings = analyze_warning_signs(
        {
            "job_title": "Remote assistant",
            "job_description": (
                "Pay a registration fee to reserve this role. "
                "We are looking for applicants with basic office skills."
            ),
        }
    )

    fee = next(item for item in findings if item["rule_id"] == "upfront_fee")
    assert fee["severity"] == "high"
    assert "registration fee" in fee["evidence"].lower()


def test_simple_no_fee_denial_does_not_trigger_fee_rule():
    findings = analyze_warning_signs(
        {
            "job_title": "Software Engineer",
            "job_description": (
                "There is no registration fee and no application charge. "
                "Candidates will complete a normal technical interview."
            ),
        }
    )

    assert not any(item["rule_id"] == "upfront_fee" for item in findings)


def test_sensitive_data_request_is_flagged():
    findings = analyze_warning_signs(
        {
            "job_title": "Office Assistant",
            "job_description": "Please send your Aadhaar card before the interview.",
        }
    )

    assert any(item["rule_id"] == "sensitive_documents" for item in findings)


def test_free_email_and_shortened_link_are_advisory_indicators():
    findings = analyze_warning_signs(
        {
            "job_title": "Support associate",
            "job_description": "Join our customer support team.",
            "recruiter_email": "recruiter@gmail.com",
            "job_url": "https://bit.ly/example",
        }
    )

    ids = {item["rule_id"] for item in findings}
    assert "free_mail_recruiter" in ids
    assert "shortened_job_link" in ids


def test_rules_are_explainable_and_have_no_scam_score():
    rules = get_rule_registry()

    assert rules
    assert all(rule["title"] and rule["explanation"] and rule["recommendation"] for rule in rules)
    assert all("score" not in rule for rule in rules)
