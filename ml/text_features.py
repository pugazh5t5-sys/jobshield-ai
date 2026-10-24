"""Turn a job posting into the single block of text the model reads.

WHY THIS FILE EXISTS
--------------------
A model is only as good as the text you feed it. If the training script built
the text one way and the website built it another way, the model would quietly
get worse without any error message appearing. That problem is called
"train/serve skew".

So both sides call build_model_text() from this one file. There is no second
implementation to drift out of step.

A NOTE ABOUT THE COMPANY NAME
-----------------------------
The EMSCAD dataset has no company-name column, so the model is never trained
on company names. The company name is still shown to the user and is still used
by the rule-based warning-sign engine, but it is not fed to the model. Feeding
the model a column it has never seen during training would be meaningless.
"""

from __future__ import annotations

# The order here decides the order of the labelled lines in the output text.
MODEL_TEXT_FIELDS: tuple[str, ...] = (
    "title",
    "location",
    "employment_type",
    "description",
    "requirements",
    "benefits",
    "company_profile",
    "salary_range",
)

# A short human-readable label printed in front of each value. The model learns
# that the words after "Job title:" are a title, and so on.
FIELD_LABELS: dict[str, str] = {
    "title": "Job title",
    "location": "Location",
    "employment_type": "Employment type",
    "description": "Description",
    "requirements": "Requirements",
    "benefits": "Benefits",
    "company_profile": "About the company",
    "salary_range": "Salary",
}


def build_model_text(**fields: object) -> str:
    """Combine the available fields into one string.

    Missing or blank fields are simply skipped, so the model never sees lines
    like "Location: None".
    """
    lines: list[str] = []
    for name in MODEL_TEXT_FIELDS:
        value = str(fields.get(name) or "").strip()
        if value:
            lines.append(f"{FIELD_LABELS[name]}: {value}")
    return "\n".join(lines)
