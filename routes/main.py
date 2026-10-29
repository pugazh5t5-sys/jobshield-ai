"""Public pages: landing page, About page and the health check."""

from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, current_app, jsonify, render_template

from config import DISCLAIMER_TEXT, is_vercel_environment
from services.prediction_service import (
    get_model_status,
    read_evaluation_report,
    read_metadata,
)

main_bp = Blueprint("main", __name__)


def _model_facts(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Pick the few numbers the landing page is allowed to show.

    Every value comes from the real model_metadata.json. If the file is not
    there yet, we return empty values so the page can say "not set up yet"
    instead of inventing anything.
    """
    if not metadata:
        return {"available": False}

    dataset = metadata.get("dataset") or {}
    metrics = (metadata.get("metrics") or {}).get("test") or {}

    return {
        "available": True,
        "dataset_name": dataset.get("name") or dataset.get("file_name"),
        "model_version": metadata.get("model_version"),
        "recall_fraud": metrics.get("recall_fraud"),
        "f1_fraud": metrics.get("f1_fraud"),
        "trained_at_utc": metadata.get("trained_at_utc"),
    }


@main_bp.get("/")
def index():
    """The landing page."""
    status = get_model_status(current_app.config["ARTIFACTS_DIR"])
    return render_template(
        "index.html",
        model_status=status,
        model_facts=_model_facts(status.get("metadata")),
    )


@main_bp.get("/about")
def about():
    """What the project does, how it works and what it cannot do."""
    report = read_evaluation_report(current_app.config["ARTIFACTS_DIR"])
    metadata = read_metadata(current_app.config["ARTIFACTS_DIR"])
    return render_template(
        "about.html",
        evaluation=report,
        model_facts=_model_facts(metadata),
        disclaimer=DISCLAIMER_TEXT,
    )


@main_bp.get("/health")
def health():
    """A small JSON check used by hosting platforms and by us.

    Note: this always returns HTTP 200 so that a hosting platform's health
    check does not mark the service as dead - the "status" field carries the
    real news instead.
    """
    status = get_model_status(current_app.config["ARTIFACTS_DIR"])
    persistent_storage = bool(current_app.config.get("SQLALCHEMY_DATABASE_URI")) and bool(
        os.environ.get("DATABASE_URL", "").strip()
    )
    using_ephemeral_fallback = is_vercel_environment() and not persistent_storage

    payload: dict[str, Any] = {
        "app": "JobShield AI",
        "status": "ok" if status["available"] else "degraded",
        "model": "available" if status["available"] else "unavailable",
        "storage": "ephemeral" if using_ephemeral_fallback else (
            "configured" if persistent_storage else "local-sqlite"
        ),
    }
    if using_ephemeral_fallback:
        payload["storage_warning"] = (
            "DATABASE_URL is not configured. Vercel is using temporary SQLite "
            "storage; records are not durable across function instances or deployments."
        )
    if status["available"]:
        payload["model_version"] = status.get("version")
    else:
        payload["reason"] = status["reason"]
    return jsonify(payload), 200
