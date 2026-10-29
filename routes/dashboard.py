"""Browser-scoped analytics built only from actual saved records."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, render_template, session

from database.models import Analysis, WarningFinding

dashboard_bp = Blueprint("dashboard", __name__)
SEVERITIES = ("high", "medium", "low")


def _visitor_queries():
    """Return SQLAlchemy queries constrained to the current browser."""
    visitor_id = session.get("visitor_id")
    if not visitor_id:
        return Analysis.query.filter(False), WarningFinding.query.filter(False)
    return (
        Analysis.query.filter_by(visitor_id=visitor_id),
        WarningFinding.query.join(Analysis, WarningFinding.analysis_id == Analysis.id).filter(
            Analysis.visitor_id == visitor_id
        ),
    )


def _daily_counts(analysis_query) -> list[dict[str, int | str]]:
    """Count real saved analyses over the last seven UTC calendar days."""
    today = datetime.now(timezone.utc).date()
    day_keys = [(today - timedelta(days=offset)).isoformat() for offset in range(6, -1, -1)]
    counts = {key: 0 for key in day_keys}

    # A browser normally has a modest number of records. A bounded read avoids
    # turning the chart endpoint into an unbounded export.
    records = analysis_query.order_by(Analysis.created_at.desc()).limit(1000).all()
    for record in records:
        if record.created_at:
            key = record.created_at.date().isoformat()
            if key in counts:
                counts[key] += 1
    return [{"date": key, "count": counts[key]} for key in day_keys]


def _dashboard_payload() -> dict:
    analysis_query, finding_query = _visitor_queries()
    total = analysis_query.count()
    with_warnings = analysis_query.filter(Analysis.findings.any()).count()
    findings_total = finding_query.count()
    severity_counts = {
        severity: finding_query.filter(WarningFinding.severity == severity).count()
        for severity in SEVERITIES
    }
    return {
        "has_records": total > 0,
        "summary": {
            "total_analyses": total,
            "analyses_with_warnings": with_warnings,
            "warning_findings": findings_total,
            "high_severity": severity_counts["high"],
            "medium_severity": severity_counts["medium"],
            "low_severity": severity_counts["low"],
        },
        "charts": {
            "severity": [
                {"severity": severity, "count": severity_counts[severity]}
                for severity in SEVERITIES
            ],
            "daily": _daily_counts(analysis_query),
        },
    }


@dashboard_bp.get("/dashboard")
def dashboard():
    """Show summary cards and the latest real analyses."""
    payload = _dashboard_payload()
    analysis_query, _ = _visitor_queries()
    recent = analysis_query.order_by(Analysis.created_at.desc()).limit(10).all()
    return render_template(
        "dashboard.html",
        has_records=payload["has_records"],
        summary=payload["summary"],
        charts=payload["charts"],
        recent=recent,
    )


@dashboard_bp.get("/api/dashboard-data")
def dashboard_data():
    """A JSON summary containing counts only, not pasted job descriptions."""
    return jsonify(_dashboard_payload())
