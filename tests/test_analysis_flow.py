"""Integration tests for analysis, private history, and real dashboard data."""

import pytest

from app import create_app
from database import db
from database.models import Analysis


@pytest.fixture()
def client():
    app = create_app("testing")
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        STORE_JOB_DESCRIPTION=False,
        ARTIFACTS_DIR="/tmp/jobshield-tests-no-model",
    )
    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_analyze_post_returns_rule_report_and_history(client):
    response = client.post(
        "/analyze",
        data={
            "job_title": "Remote Office Assistant",
            "company_name": "Example Company",
            "job_description": (
                "Please pay a registration fee before the interview. "
                "Applicants should verify every offer before sharing information."
            ),
            "location": "Remote",
            "employment_type": "Full-time",
            "job_url": "",
            "requirements": "",
            "benefits": "",
            "company_profile": "",
            "salary_range": "",
            "recruiter_email": "",
        },
    )

    assert response.status_code == 200
    assert b"no ai probability was generated" in response.data.lower()
    assert b"Upfront fee or deposit mentioned" in response.data

    with client.application.app_context():
        record = Analysis.query.one()
        public_id = record.public_id
        assert record.model_score is None
        assert record.job_description is None
        assert record.findings

    history_response = client.get("/history")
    assert history_response.status_code == 200
    assert b"Remote Office Assistant" in history_response.data

    detail_response = client.get(f"/history/{public_id}")
    assert detail_response.status_code == 200
    assert b"Rule-based review only" in detail_response.data


def test_invalid_submission_renders_server_side_errors(client):
    response = client.post(
        "/analyze",
        data={"job_title": "IT", "job_description": "too short"},
    )

    assert response.status_code == 400
    assert b"Job title must be at least 3 characters" in response.data
    assert b"Job description must be at least 50 characters" in response.data


def test_delete_only_removes_a_browser_owned_record(client):
    client.post(
        "/analyze",
        data={
            "job_title": "Software Engineer",
            "job_description": (
                "A software role building web services and maintaining internal applications."
            ),
        },
    )
    with client.application.app_context():
        public_id = Analysis.query.one().public_id

    response = client.post(f"/history/{public_id}/delete")
    assert response.status_code == 302

    with client.application.app_context():
        assert Analysis.query.count() == 0


def test_dashboard_uses_saved_data(client):
    client.post(
        "/analyze",
        data={
            "job_title": "Recruitment Coordinator",
            "job_description": (
                "Pay a processing fee to confirm your spot before the interview starts."
            ),
        },
    )

    page = client.get("/dashboard")
    data = client.get("/api/dashboard-data")

    assert page.status_code == 200
    assert b"Total reports" in page.data
    assert data.status_code == 200
    payload = data.get_json()
    assert payload["summary"]["total_analyses"] == 1
    assert payload["summary"]["warning_findings"] >= 1
    assert len(payload["charts"]["daily"]) == 7
