"""The two database tables used by JobShield AI.

"Analysis" is one submitted job posting and what the app concluded about it.
"WarningFinding" is one rule that fired for that posting. Keeping them in two
tables means one analysis can have zero, one or many findings.

Only the minimum needed is stored. The pasted description can be switched off
entirely with the STORE_JOB_DESCRIPTION setting.
"""

from __future__ import annotations

from datetime import datetime, timezone

from database import db


def utc_now() -> datetime:
    """Current time in UTC.

    Storing times in UTC avoids time-zone confusion when the app runs on a
    server in another country.
    """
    return datetime.now(timezone.utc)


class Analysis(db.Model):
    """One job posting that was analysed."""

    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)

    # A random-looking ID (UUID) is used in URLs instead of 1, 2, 3, so that
    # nobody can guess somebody else's record just by changing the number.
    public_id = db.Column(db.String(36), unique=True, nullable=False, index=True)

    # A random cookie value identifying this browser only. No accounts, no login.
    visitor_id = db.Column(db.String(64), nullable=False, index=True)

    created_at = db.Column(
        db.DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    # --- What the user submitted --------------------------------------------
    job_title = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    employment_type = db.Column(db.String(50), nullable=True)
    # Nullable because STORE_JOB_DESCRIPTION may be turned off for privacy.
    job_description = db.Column(db.Text, nullable=True)

    # --- What the machine-learning model said --------------------------------
    prediction_label = db.Column(db.String(32), nullable=True)
    model_score = db.Column(db.Float, nullable=True)
    model_threshold = db.Column(db.Float, nullable=True)
    model_version = db.Column(db.String(64), nullable=True)
    # A short list of the terms that pushed the prediction, stored as JSON text.
    top_terms = db.Column(db.JSON, nullable=True)

    findings = db.relationship(
        "WarningFinding",
        backref="analysis",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Analysis {self.public_id} {self.job_title!r}>"


class WarningFinding(db.Model):
    """One rule-based warning sign that fired for an analysis."""

    __tablename__ = "warning_findings"

    id = db.Column(db.Integer, primary_key=True)

    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rule_id = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    severity = db.Column(db.String(16), nullable=False)
    # A very short quoted snippet showing what matched (escaped by the template).
    evidence = db.Column(db.String(300), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<WarningFinding {self.rule_id} {self.severity}>"
