"""Regression tests for server-side job form validation."""

from services.validation_service import validate_job_submission


def valid_form(**overrides):
    data = {
        "job_title": "Software Engineer",
        "job_description": "We are hiring a software engineer to build and maintain web applications.",
    }
    data.update(overrides)
    return data


def test_accepts_valid_job_form():
    data, errors = validate_job_submission(valid_form(job_url="https://example.com/jobs/1"))

    assert errors == []
    assert data["job_title"] == "Software Engineer"


def test_rejects_short_required_fields():
    _, errors = validate_job_submission(valid_form(job_title="IT", job_description="short"))

    assert any("Job title" in error for error in errors)
    assert any("Job description" in error for error in errors)


def test_rejects_invalid_or_unsafe_url_syntax():
    _, errors = validate_job_submission(valid_form(job_url="javascript:alert(1)"))

    assert any("Job application URL" in error for error in errors)


def test_rejects_invalid_email_and_unknown_employment_type():
    _, errors = validate_job_submission(
        valid_form(recruiter_email="not-an-email", employment_type="unknown")
    )

    assert any("Recruiter email" in error for error in errors)
    assert any("employment type" in error for error in errors)


def test_rejects_values_over_field_limits():
    _, errors = validate_job_submission(valid_form(job_title="x" * 201))

    assert any("at most 200 characters" in error for error in errors)
