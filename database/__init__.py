"""Database layer for JobShield AI.

The "db" object created here is the one shared connection point that Flask
and every table use. The actual tables live in "models.py" so that the word
"models" never gets confused with the machine-learning model.
"""

from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """Create any missing tables.

    This is safe to run repeatedly: it only creates tables that do not exist
    yet and never touches existing data.
    """
    with app.app_context():
        # Importing the module registers the tables with SQLAlchemy.
        from database import models  # noqa: F401

        db.create_all()
