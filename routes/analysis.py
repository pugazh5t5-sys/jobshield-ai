"""The job analysis form and (from Phase 3) the analysis itself."""

from __future__ import annotations

from flask import Blueprint, current_app, render_template, request

from services.prediction_service import get_model_status

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Show the form, and in Phase 3 run the real pipeline on submit.

    Right now, if the trained model is missing we return HTTP 503 with a setup
    page - exactly what the specification asks for. We never show a made-up
    result just to keep the page looking complete.
    """
    status = get_model_status(current_app.config["ARTIFACTS_DIR"])

    if request.method == "POST" and not status["available"]:
        return (
            render_template(
                "error.html",
                code=503,
                title="Model not set up yet",
                message=(
                    "The analysis service needs a trained model before it can "
                    "score a job posting."
                ),
                model_reason=status["reason"],
                show_setup=True,
            ),
            503,
        )

    return render_template("analyze.html", model_status=status)
