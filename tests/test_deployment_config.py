"""Deployment and environment configuration regression tests."""

import pytest

from config import ProductionConfig, _database_uri, get_config


def test_vercel_uses_temporary_sqlite_only_as_fallback(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert _database_uri() == "sqlite:////tmp/jobshield.db"


def test_postgres_url_is_normalized(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@host/db")

    assert _database_uri() == "postgresql://user:pass@host/db"


def test_vercel_defaults_to_production(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)

    assert get_config() is ProductionConfig


def test_vercel_refuses_to_start_without_a_secret(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("SECRET_KEY", "")
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        get_config()


def test_local_default_stays_development(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)

    assert get_config().__name__ == "DevelopmentConfig"
