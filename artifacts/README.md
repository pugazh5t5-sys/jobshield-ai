# Artifacts

Files in this folder are **generated**, not written by hand. They are produced by
the training and evaluation scripts.

| File | Created by | What it is |
|---|---|---|
| `jobshield_pipeline.joblib` | `python -m ml.train_model` | The complete fitted pipeline: the TF-IDF vectorizer **and** the Logistic Regression classifier, saved together as one object. |
| `model_metadata.json` | `python -m ml.train_model` | Everything needed to trust the model: version, training date, dataset name and SHA-256, row counts before and after de-duplication, class counts, split sizes, random seed, hyperparameters, the decision threshold and how it was chosen, whether the model is calibrated, library versions, and the test metrics. |
| `evaluation_report.json` | `python -m ml.train_model` | The machine-readable evaluation summary that the About page reads. |
| `test_split_ids.json` | `python -m ml.train_model` | The identifiers of the held-out test rows only - no text - so the evaluation can be repeated exactly. |
| `reports/` | `python -m ml.evaluate_model` | A Markdown report plus plots (confusion matrix, ROC curve, precision-recall curve). |

## Why the versions matter

The `.joblib` file is a Python pickle, and pickles are not guaranteed to load
across different library versions. A model saved with one scikit-learn version
may load incorrectly - or refuse to load - with another. That is why the exact
scikit-learn version is pinned in `requirements.txt`, recorded in
`model_metadata.json`, and checked again when the app loads the model.

## Security note

Joblib files are pickles, which means loading one executes Python code from
inside it. Only ever load the model from this configured folder, and never load
a `.joblib` file that came from somewhere you do not trust.

## Current status

**Empty.** No model has been trained yet, so the app currently reports
`"model": "unavailable"` at `/health` and shows setup instructions at `/analyze`.
