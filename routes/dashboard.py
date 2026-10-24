"""The analytics dashboard. The charts and aggregates arrive in Phase 3."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/dashboard")
def dashboard():
    """Show the dashboard.

    With no saved analyses the page shows its empty state, which is honest:
    there really are no records yet.
    """
    return render_template("dashboard.html", has_records=False)


@dashboard_bp.get("/api/dashboard-data")
def dashboard_data():
    """Aggregate numbers for the charts, as JSON.

    Deliberately contains no job text at all - only counts.
    """
    return jsonify({"has_records": False, "summary": {}, "charts": {}})
