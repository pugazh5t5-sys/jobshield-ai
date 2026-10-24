"""The only place that touches the trained machine-learning model.

Keeping model handling in one module means a normal web page request can never
accidentally retrain anything. The rest of the app only asks two questions:

    "is the model ready?"        -> get_model_status()
    "what does it predict?"      -> (added in Phase 2)

If the model is missing or damaged we raise ModelUnavailableError and the app
shows a setup page. We never invent a prediction to keep the page looking nice.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# The generated files that live in the artifacts folder.
PIPELINE_FILENAME = "jobshield_pipeline.joblib"
METADATA_FILENAME = "model_metadata.json"
EVALUATION_FILENAME = "evaluation_report.json"


class ModelUnavailableError(RuntimeError):
    """The model cannot be used right now. The message says why, in plain words."""


def _read_json(path: Path) -> dict[str, Any] | None:
    """Read a JSON file, returning None if it is missing or unreadable."""
    try:
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_metadata(artifacts_dir: str | Path) -> dict[str, Any] | None:
    """Return the parsed model_metadata.json, or None when it is not there."""
    return _read_json(Path(artifacts_dir) / METADATA_FILENAME)


def read_evaluation_report(artifacts_dir: str | Path) -> dict[str, Any] | None:
    """Return the parsed evaluation_report.json, or None when it is not there.

    The About page uses this so that it can never show invented accuracy
    numbers - if the file is absent, the page says "Model not trained yet".
    """
    return _read_json(Path(artifacts_dir) / EVALUATION_FILENAME)


def get_model_status(artifacts_dir: str | Path) -> dict[str, Any]:
    """Say whether the model is ready to use, and if not, why not.

    Returns a small dictionary so callers (the landing page and /health) can
    display an honest message either way.
    """
    folder = Path(artifacts_dir)
    pipeline_path = folder / PIPELINE_FILENAME
    metadata = read_metadata(folder)

    if not pipeline_path.is_file():
        return {
            "available": False,
            "reason": (
                f"Trained model file '{PIPELINE_FILENAME}' was not found in "
                f"'{folder}'. Train it with: python -m ml.train_model"
            ),
            "metadata": metadata,
            "version": (metadata or {}).get("model_version"),
        }

    if metadata is None:
        return {
            "available": False,
            "reason": (
                f"'{METADATA_FILENAME}' is missing or unreadable, so the model "
                "version cannot be confirmed."
            ),
            "metadata": None,
            "version": None,
        }

    return {
        "available": True,
        "reason": "",
        "metadata": metadata,
        "version": metadata.get("model_version"),
    }
