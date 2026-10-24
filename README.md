# JobShield AI

**AI-Powered Fake Job Detection System**

> Detect suspicious job postings. Apply with confidence.

JobShield AI is a Flask web application that helps job seekers look more
carefully at a job posting before they reply to it. It gives **two separate,
independent second opinions**:

1. A **machine-learning estimate** from a model trained on real, labelled job
   postings, based on how the advert is worded.
2. A **rule-based warning-sign engine** that flags readable patterns - upfront
   payment requests, requests for sensitive documents, urgent pressure, and so
   on - and shows the exact words that triggered each one.

The two results are shown side by side and are **never blended into a single
"scam score"**.

> **JobShield AI provides automated estimates and warning signs. It cannot
> guarantee whether a job or employer is genuine. Verify opportunities
> independently before taking action.**

---

## Project status

| Phase | Scope | Status |
|---|---|---|
| 1 | Project foundation, design system, landing page | **Complete** (see the Phase 1 report) |
| 2 | Dataset verification, training and evaluation | Not started |
| 3 | Form to backend, warning-sign engine, database, history, dashboard | Not started |
| 4 | Automated tests, accessibility and responsive checks | Not started |
| 5 | Documentation, GitHub and deployment preparation | Not started |

Nothing in this repository contains invented data. Where a number is not
available, the interface says so instead of showing a placeholder.

**Deployment: not yet performed.**

---

## Problem statement

Fraudulent job adverts are cheap to produce and hard to spot. They often promise
high pay for minimal work, request a "registration" or "training" fee, or ask
for identity documents before any interview has taken place. Job seekers
typically have only a few minutes to decide whether to reply.

## Objectives

- Build a real, working web application (not a static mock-up) that analyses job
  postings end to end.
- Train a genuine machine-learning model on a real, licensed, labelled dataset,
  and report only the metrics that were actually measured.
- Explain *why* the tool flagged something, in plain language, so the user learns
  the pattern rather than blindly trusting a score.
- Keep the machine-learning estimate and the rule-based warning signs visibly
  separate, so neither is mistaken for proof.
- Handle the case where the model or dataset is missing honestly: show setup
  instructions, never a substitute result.

## Features

- Landing page with a live model-facts strip read from the model's own metadata.
- Job analysis form with server-authoritative validation and a live character
  counter.
- Results page showing the model estimate and the warning signs in separate
  panels, with evidence for every rule that fired.
- Per-browser analysis history with search, filters and pagination - no account
  required.
- Analytics dashboard built only from real saved records, with accessible chart
  alternatives and an honest empty state.
- An About & methodology page whose evaluation figures are loaded from the saved
  evaluation report, and whose rule list is generated from the rule registry in
  the code.
- Designed error pages for 400, 403, 404, 405, 413, 429, 500 and 503 that never
  leak stack traces or file paths.

---

## Screenshots

No screenshots are stored in this repository yet, because fabricated or mock
images would misrepresent the project. When you have run the app locally:

1. Start the app (`flask --app app run --debug`).
2. Capture each page at 360 px, 768 px and 1280 px wide.
3. Save the files as `docs/screenshots/<page>-<width>.png`.
4. Replace this section with a table of those images and the exact command you
   used to start the app.

_Status: not captured yet._

---

## Technology stack

| Area | Choice |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (no framework, no CDN) |
| Backend | Python 3.11+, Flask, Jinja2 |
| Machine learning | scikit-learn, pandas, NumPy, TF-IDF, Logistic Regression, Joblib |
| Database | SQLite locally, SQLAlchemy (Flask-SQLAlchemy) |
| Charts | Chart.js, self-hosted in `static/vendor/chartjs/` |
| Forms and CSRF | Flask-WTF (CSRFProtect) |
| Testing | Pytest |
| Production server | Gunicorn (Linux hosts such as Render) |

---

## Architecture overview

```
Browser
  |
  v
Flask routes (routes/)          <- thin: read input, call services, render template
  |
  +--> validation_service       <- cleans and length-checks untrusted input
  |
  +--> prediction_service       <- loads the saved pipeline ONCE, predicts
  |        |
  |        +--> ml/text_features.py   <- the SAME text builder used in training
  |
  +--> warning_sign_service     <- independent rule engine, no ML imports
  |
  v
database/ (SQLAlchemy)          <- Analysis + WarningFinding
  |
  v
Jinja2 templates (templates/)   <- autoescaping on, never |safe on user input
```

Two deliberate decisions, in plain language:

- **`routes/` blueprints** stop `app.py` from growing into one enormous file.
  Each blueprint is a small bundle of related pages.
- **`ml/text_features.build_model_text()`** is shared by the training script and
  the live website. If the two built the input text differently, the model would
  quietly get worse with no error message at all. That failure has a name:
  *train/serve skew*.

A fuller diagram lives in `docs/architecture.md`.

---

## Directory structure

```
jobshield-ai/
├── app.py                  # create_app() factory + entry point
├── config.py               # dev / production / testing settings from env vars
├── requirements.txt        # what the running app and training need
├── requirements-dev.txt    # adds pytest, coverage, matplotlib and kaggle
├── .env.example            # safe placeholders - copy to .env
├── routes/                 # main, analysis, history, dashboard blueprints
├── services/               # prediction, warning signs, validation, analytics
├── database/               # db object + SQLAlchemy tables
├── ml/                     # text_features, train_model, evaluate_model
├── data/                   # dataset README + raw/ (never committed)
├── artifacts/              # generated model + reports
├── templates/              # Jinja2 templates and shared partials
├── static/                 # css, js, self-hosted chartjs, svg images
├── tests/                  # pytest suite + tiny synthetic fixtures
└── docs/                   # architecture and methodology notes
```

---

## Prerequisites

- **Python 3.11 or newer.** (This project was set up and run with Python 3.11.9.)
- Git.
- A free Kaggle account, only if you want to download the dataset yourself.

## Windows PowerShell setup

```powershell
python --version                      # needs 3.11 or newer
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste the output into SECRET_KEY in .env
```

### Dataset (Phase 2 - check the terms first)

Download `kaggle.json` from your Kaggle account page and place it in
`%USERPROFILE%\.kaggle\`, then:

```powershell
kaggle datasets download -d shivamb/real-or-fake-fake-jobposting-prediction -p data/raw --unzip
```

A manual browser download works too - see [data/README.md](data/README.md),
which also records the source, the licence as found, and the schema.

### Train and evaluate

```powershell
python -m ml.train_model              # trains and saves the pipeline into artifacts/
python -m ml.evaluate_model           # writes the evaluation report and plots
```

### Run locally

```powershell
flask --app app run --debug           # local development only
```

Then open <http://127.0.0.1:5000/>.

### Run the tests

```powershell
python -m pytest -q
```

### Useful endpoints

| Path | What it gives you |
|---|---|
| `/` | Landing page |
| `/analyze` | The job analysis form |
| `/dashboard` | Analytics dashboard |
| `/history` | Your saved analyses |
| `/about` | Methodology and limitations |
| `/health` | JSON status, including whether the model is available |

---

## How the model is trained (short version)

1. Load the real dataset and check its columns against the expected schema.
2. Validate that the target column holds only 0 and 1.
3. Remove duplicate postings **before** splitting, so the same advert cannot
   appear in both halves.
4. Make a **stratified** train/test split. ("Stratified" means both halves keep
   the same proportion of fraudulent postings as the full dataset.)
5. Fit TF-IDF **only on the training half**, inside a scikit-learn `Pipeline`, so
   no information from the test set leaks in.
6. Train Logistic Regression with balanced class weights.
7. Choose the decision threshold from cross-validated **training** predictions.
8. Evaluate **once** on the held-out test set, and save every number.

Full detail, and the real measured results, live in `docs/methodology.md` and
`artifacts/reports/`.

---

## Notes for Windows users

- **Gunicorn does not run on Windows.** It is installed for deployment on Linux
  hosts such as Render; use `flask --app app run --debug` locally instead.
- `kaggle.json` belongs in `%USERPROFILE%\.kaggle\`, not in this project folder.
- If PowerShell refuses to run the activation script, run
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

---

## Limitations

- The model learns from past adverts, so it will not recognise genuinely new
  scam wording.
- Genuine adverts that happen to be worded oddly can look suspicious, and
  well-written scams can look normal. Errors happen in both directions.
- The dataset under-represents non-English postings, so results for those are
  less reliable.
- **Nothing here verifies a company.** There is no registry lookup, no business
  database and no link-reputation check connected to this project, and the app
  never opens or fetches a submitted URL.
- History is tied to a random cookie in your browser. Clearing browser data
  removes access to your saved analyses; there are no accounts.
- If `STORE_JOB_DESCRIPTION=false`, the pasted description is not saved at all.

---

## Responsible use

JobShield AI is a decision-support tool. It does not verify employers, and its
output is not evidence that a crime has occurred. Always confirm an opportunity
through independent official sources, and never pay money to obtain a job.

> **JobShield AI provides automated estimates and warning signs. It cannot
> guarantee whether a job or employer is genuine. Verify opportunities
> independently before taking action.**

---

## Licence

MIT - see [LICENSE](LICENSE). Replace the copyright holder with your own name
before publishing the repository.
