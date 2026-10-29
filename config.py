"""Configuration for JobShield AI.

Everything that changes between your laptop and a real server is read from
environment variables here. That way no secret is ever written into the code.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# The folder that contains this file, i.e. the project root.
BASE_DIR = Path(__file__).resolve().parent

# Read the ".env" file if it exists. Values already set in the real
# environment always win, which is what cloud hosts rely on.
load_dotenv(BASE_DIR / ".env")


def is_vercel_environment() -> bool:
    """Return True when this process runs inside a Vercel deployment."""
    return os.environ.get("VERCEL", "").strip().lower() in {"1", "true", "yes"}


def _as_bool(name: str, default: bool = False) -> bool:
    """Read an environment variable such as "true", "1", "yes" or "on"."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(name: str, default: int) -> int:
    """Read a whole number from the environment, falling back on a default."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _database_uri() -> str:
    """Choose durable cloud storage when configured, otherwise local SQLite.

    Vercel's function filesystem is not a durable database. The /tmp SQLite
    fallback is only for a bootable preview/demo; its contents can disappear
    between function instances or deployments. Set DATABASE_URL to a managed
    PostgreSQL database before relying on persistent records.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        if is_vercel_environment():
            return "sqlite:////tmp/jobshield.db"
        return f"sqlite:///{(BASE_DIR / 'instance' / 'jobshield.db').as_posix()}"
    # Older hosts hand out "postgres://" which SQLAlchemy no longer accepts.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


# The exact disclaimer that must appear on every page and in the README.
DISCLAIMER_TEXT = (
    "JobShield AI provides automated estimates and warning signs. "
    "It cannot guarantee whether a job or employer is genuine. "
    "Verify opportunities independently before taking action."
)

# Secret keys that are obviously not real. Production refuses to start with one.
PLACEHOLDER_SECRET_KEYS = {
    "",
    "dev-only-change-me",
    "replace-me-with-a-long-random-string",
    "change-me",
    "changeme",
    "replace-me",
    "your-secret-key",
    "secret",
    "placeholder",
}


class Config:
    """Settings shared by every environment."""

    # --- Core Flask settings -------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = False
    TESTING = False
    # Turn off auto-sorting of JSON keys so the API output reads naturally.
    JSON_SORT_KEYS = False

    # --- Database ------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # --- Model artifacts -----------------------------------------------------
    ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", "artifacts")

    # --- Privacy -------------------------------------------------------------
    # When false the pasted description is never written to the database.
    STORE_JOB_DESCRIPTION = _as_bool("STORE_JOB_DESCRIPTION", True)

    # --- Request limits ------------------------------------------------------
    MAX_CONTENT_LENGTH = _as_int("MAX_CONTENT_LENGTH", 512 * 1024)

    # --- Cookies -------------------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _as_bool("SESSION_COOKIE_SECURE", False)

    # --- External links ------------------------------------------------------
    GITHUB_URL = os.environ.get("GITHUB_URL", "").strip()

    # --- Logging -------------------------------------------------------------
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    # --- CSRF ----------------------------------------------------------------
    WTF_CSRF_ENABLED = True

    @property
    def artifacts_path(self) -> Path:
        """Absolute path to the folder that holds the trained model."""
        path = Path(self.ARTIFACTS_DIR)
        return path if path.is_absolute() else BASE_DIR / path


class DevelopmentConfig(Config):
    """Used while developing on your own machine."""

    DEBUG = _as_bool("FLASK_DEBUG", False)


class TestingConfig(Config):
    """Used by the automated tests only."""

    TESTING = True
    # Every test gets a throw-away in-memory database, never the real file.
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS: dict = {}
    WTF_CSRF_ENABLED = True
    SECRET_KEY = "testing-secret-key"


class ProductionConfig(Config):
    """Used on a real server."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"

    @classmethod
    def validate(cls) -> None:
        """Refuse to start with a missing or placeholder secret key.

        A weak secret key lets an attacker forge cookies, so failing loudly
        here is much safer than quietly running anyway.
        """
        key = os.environ.get("SECRET_KEY", "")
        if key.strip().lower() in PLACEHOLDER_SECRET_KEYS or len(key.strip()) < 32:
            raise RuntimeError(
                "Refusing to start in production: SECRET_KEY is missing, is a "
                "placeholder, or is shorter than 32 characters. Generate one "
                'with: python -c "import secrets; print(secrets.token_hex(32))"'
            )


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[Config]:
    """Pick a configuration class by name.

    Vercel deployments are always production by default, even when FLASK_ENV
    is accidentally omitted. Local runs still default to development.
    """
    if name is None and is_vercel_environment():
        chosen = "production"
    else:
        chosen = name or os.environ.get("FLASK_ENV") or os.environ.get("APP_ENV") or "development"

    config_class = _CONFIGS.get(chosen.strip().lower(), DevelopmentConfig)
    if config_class is ProductionConfig:
        ProductionConfig.validate()
    return config_class
