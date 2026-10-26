"""JobShield AI - application factory.

This is the file that starts everything. Instead of creating one global Flask
object at import time, we use a "factory" function (create_app). A factory
makes testing easier, because each test can build a fresh, isolated app.

Run it locally with:
    flask --app app run --debug
On a server (Render) it is started with Gunicorn, see the README.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import click
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import HTTPException

from config import BASE_DIR, DISCLAIMER_TEXT, get_config
from database import db, init_db
from routes.analysis import analysis_bp
from routes.dashboard import dashboard_bp
from routes.history import history_bp
from routes.main import main_bp

csrf = CSRFProtect()

APP_NAME = "JobShield AI"
APP_TAGLINE = "Detect suspicious job postings. Apply with confidence."

# A strict Content-Security-Policy: only files from our own site may load.
# "no inline script" is why every bit of JavaScript lives in static/js.
CONTENT_SECURITY_POLICY = "; ".join(
    (
        "default-src 'self'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "img-src 'self' data:",
        "script-src 'self'",
        "style-src 'self'",
        "font-src 'self'",
        "connect-src 'self'",
        "object-src 'none'",
    )
)

# Every error code that has a friendly page of its own.
HANDLED_ERROR_CODES = (400, 403, 404, 405, 413, 429, 500, 503)


def _configure_logging(app: Flask) -> None:
    """Send logs to the console at the level chosen in .env."""
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    app.logger.setLevel(level)


def _register_context(app: Flask) -> None:
    """Values that every template can use without being passed in."""

    @app.context_processor
    def inject_globals() -> dict:
        return {
            "app_name": APP_NAME,
            "app_tagline": APP_TAGLINE,
            "disclaimer_text": DISCLAIMER_TEXT,
            "github_url": app.config.get("GITHUB_URL", ""),
            "current_year": datetime.now(timezone.utc).year,
        }


def _register_error_handlers(app: Flask) -> None:
    """One designed error page for every code. Never leak internals."""

    def _render_error(code: int):
        friendly = {
            400: ("Bad request", "Some of the information sent was not in the expected format."),
            403: ("Not allowed", "This action is not permitted. The page may have expired."),
            404: ("Page not found", "We could not find that page or record."),
            405: ("Method not allowed", "That page does not accept this kind of request."),
            413: ("Upload too large", "The job posting you submitted is larger than the limit."),
            429: ("Too many requests", "You have made a lot of requests very quickly. Please wait a moment."),
            500: ("Something went wrong", "An unexpected error happened on our side."),
            503: ("Service unavailable", "A required part of the service is not ready yet."),
        }
        title, message = friendly.get(code, ("Unexpected error", "An unexpected error happened."))
        return render_template("error.html", code=code, title=title, message=message)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        code = error.code if error.code in HANDLED_ERROR_CODES else 500
        # Log the real reason server-side, but never show it to the visitor.
        app.logger.warning("HTTP %s on %s", code, request.path)
        return _render_error(code), code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        app.logger.exception("Unhandled exception on %s", request.path)
        return _render_error(500), 500


def _register_security_headers(app: Flask) -> None:
    """Add defensive headers to every single response."""

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        return response


def create_app(config_name: str | None = None) -> Flask:
    """Build and return a configured Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))

    # Make sure the folder that holds the local SQLite file exists.
    os.makedirs(BASE_DIR / "instance", exist_ok=True)

    _configure_logging(app)

    db.init_app(app)
    init_db(app)
    csrf.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(dashboard_bp)

    _register_context(app)
    _register_error_handlers(app)
    _register_security_headers(app)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Create any missing database tables."""
        init_db(app)
        click.echo("Database tables are ready.")

    return app


# Create the Flask application instance for Vercel
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
