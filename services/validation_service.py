"""Server-side validation for untrusted job-posting form data."""

from __future__ import annotations

import re
from urllib.parse import urlsplit
from typing import Any

FIELD_LIMITS = {
    "job_title": 200,
    "company_name": 200,
    "job_description": 15000,
    "location": 200,
    "employment_type": 50,
    "job_url": 2000,
    "requirements": 10000,
    "benefits": 5000,
    "company_profile": 10000,
    "salary_range": 200,
    "recruiter_email": 254,
}

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_job_submission(form: Any) -> tuple[dict[str, str], list[str]]:
    """Return cleaned fields and human-readable validation errors.

    Only syntax and length are validated here. Job URLs are never opened or
    fetched, avoiding accidental server-side requests to untrusted addresses.
    """
    data: dict[str, str] = {}
    errors: list[str] = []

    for field, maximum in FIELD_LIMITS.items():
        value = str(form.get(field, "") or "").strip()
        if len(value) > maximum:
            errors.append(f"{field.replace('_', ' ').title()} must be at most {maximum} characters.")
            value = value[:maximum]
        data[field] = value

    if len(data["job_title"]) < 3:
        errors.append("Job title must be at least 3 characters.")
    if len(data["job_description"]) < 50:
        errors.append("Job description must be at least 50 characters.")

    email = data["recruiter_email"]
    if email and not EMAIL_PATTERN.fullmatch(email):
        errors.append("Recruiter email must be a valid email address.")

    job_url = data["job_url"]
    if job_url:
        try:
            parsed = urlsplit(job_url)
            valid_url = (
                parsed.scheme.lower() in {"http", "https"}
                and bool(parsed.hostname)
                and not parsed.username
                and not parsed.password
            )
        except ValueError:
            valid_url = False
        if not valid_url:
            errors.append("Job application URL must be a valid http:// or https:// URL.")

    allowed_employment_types = {
        "",
        "Full-time",
        "Part-time",
        "Contract",
        "Temporary",
        "Internship",
        "Other / not specified",
    }
    if data["employment_type"] not in allowed_employment_types:
        errors.append("Choose a valid employment type.")

    return data, errors
