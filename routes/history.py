"""Past analyses for this browser. The list, detail and delete actions are
completed in Phase 3 once the database is wired to the analysis flow."""

from __future__ import annotations

from flask import Blueprint, render_template

history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
def history():
    """List previous analyses for this visitor.

    Phase 1 shows the empty state, which is the true state: nothing has been
    saved yet because the analysis flow arrives in Phase 3.
    """
    return render_template(
        "history.html",
        analyses=[],
        page=1,
        total_pages=1,
        total=0,
    )
