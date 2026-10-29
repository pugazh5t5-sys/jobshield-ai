"""Anonymous per-browser identity helper."""

from __future__ import annotations

import secrets

from flask import session


def get_or_create_visitor_id() -> str:
    """Return a random opaque browser ID stored in Flask's signed session."""
    visitor_id = session.get("visitor_id")
    if not isinstance(visitor_id, str) or len(visitor_id) < 32:
        visitor_id = secrets.token_urlsafe(32)
        session["visitor_id"] = visitor_id
    return visitor_id
