"""Per-browser analysis history and saved report details."""

from __future__ import annotations

from math import ceil

from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from database import db
from database.models import Analysis
from services.prediction_service import get_model_status
from services.warning_sign_service import enrich_stored_findings

history_bp = Blueprint("history", __name__)
PER_PAGE = 10


@history_bp.get("/history")
def history():
    """List only records associated with the current browser session."""
    visitor_id = session.get("visitor_id")
    query = Analysis.query.filter_by(visitor_id=visitor_id) if visitor_id else Analysis.query.filter(False)
    total = query.count()
    total_pages = max(1, ceil(total / PER_PAGE))

    try:
        page = max(1, int(request.args.get("page", "1")))
    except (TypeError, ValueError):
        page = 1
    page = min(page, total_pages)

    analyses = (
        query.order_by(Analysis.created_at.desc(), Analysis.id.desc())
        .offset((page - 1) * PER_PAGE)
        .limit(PER_PAGE)
        .all()
    )

    return render_template(
        "history.html",
        analyses=analyses,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@history_bp.get("/history/<public_id>")
def view_analysis(public_id: str):
    """Open a saved report only if it belongs to this browser."""
    visitor_id = session.get("visitor_id")
    if not visitor_id:
        abort(404)

    analysis = Analysis.query.filter_by(
        public_id=public_id,
        visitor_id=visitor_id,
    ).first_or_404()

    return render_template(
        "result.html",
        analysis=analysis,
        findings=enrich_stored_findings(analysis.findings),
        model_status=get_model_status(current_app.config["ARTIFACTS_DIR"]),
        saved=True,
        analysis_url=url_for("history.view_analysis", public_id=analysis.public_id),
    )


@history_bp.post("/history/<public_id>/delete")
def delete_analysis(public_id: str):
    """Delete one saved report, scoped to the current browser."""
    visitor_id = session.get("visitor_id")
    if not visitor_id:
        abort(404)

    analysis = Analysis.query.filter_by(
        public_id=public_id,
        visitor_id=visitor_id,
    ).first_or_404()

    try:
        db.session.delete(analysis)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not delete an analysis")
    return redirect(url_for("history.history"))
