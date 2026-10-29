"""Job analysis form and explainable rule-based warning report."""

from __future__ import annotations

from uuid import uuid4

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from database import db
from database.models import Analysis, WarningFinding
from services.prediction_service import get_model_status
from services.validation_service import validate_job_submission
from services.visitor_service import get_or_create_visitor_id
from services.warning_sign_service import analyze_warning_signs

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Validate a posting and show transparent warning indicators.

    Machine-learning inference is not wired into this project yet. This route
    never invents an ML score; it reports the independent rule-based findings
    and explicitly identifies the missing model integration.
    """
    model_status = get_model_status(current_app.config["ARTIFACTS_DIR"])

    if request.method == "GET":
        return render_template(
            "analyze.html",
            model_status=model_status,
            form_data={},
            form_errors=[],
        )

    data, errors = validate_job_submission(request.form)
    if errors:
        return (
            render_template(
                "analyze.html",
                model_status=model_status,
                form_data=data,
                form_errors=errors,
            ),
            400,
        )

    findings = analyze_warning_signs(data)
    public_id = str(uuid4())
    visitor_id = get_or_create_visitor_id()
    record = Analysis(
        public_id=public_id,
        visitor_id=visitor_id,
        job_title=data["job_title"],
        company_name=data["company_name"] or None,
        location=data["location"] or None,
        employment_type=data["employment_type"] or None,
        job_description=(
            data["job_description"]
            if current_app.config.get("STORE_JOB_DESCRIPTION", True)
            else None
        ),
        # No prediction is saved because inference is not implemented yet.
        prediction_label=None,
        model_score=None,
        model_threshold=None,
        model_version=None,
    )

    for finding in findings:
        record.findings.append(
            WarningFinding(
                rule_id=finding["rule_id"],
                category=finding["category"],
                severity=finding["severity"],
                evidence=finding["evidence"],
            )
        )

    saved = False
    try:
        db.session.add(record)
        db.session.commit()
        saved = True
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not save a job analysis")

    return render_template(
        "result.html",
        analysis=record,
        findings=findings,
        model_status=model_status,
        saved=saved,
        analysis_url=(url_for("history.view_analysis", public_id=public_id) if saved else None),
    )
