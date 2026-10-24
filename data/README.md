# Dataset

This folder holds the training data. **Nothing in `raw/` is committed to Git**
(see `.gitignore`), because the dataset is large and is not ours to redistribute.

## Where the data comes from

- **Name:** EMSCAD - Employment Scam Aegean Dataset (University of the Aegean,
  Laboratory of Information and Communication Systems Security).
- **Common mirror:** Kaggle - "Real / Fake Job Posting Prediction"
  (`shivamb/real-or-fake-fake-jobposting-prediction`), file `fake_job_postings.csv`.

> **Status: NOT YET VERIFIED.**
> The source page, its licence and the exact schema have not been opened and
> checked yet. They are verified in Phase 2 before any training happens, and the
> findings - including the exact licence wording, the URL and the date checked -
> are recorded here. Nothing about the licence is assumed.

## How to download

Put your Kaggle API token at `%USERPROFILE%\.kaggle\kaggle.json` (download it
from your Kaggle account page), then run from the project root:

```powershell
kaggle datasets download -d shivamb/real-or-fake-fake-jobposting-prediction -p data/raw --unzip
```

Manual alternative: open the dataset page in a browser, download
`fake_job_postings.csv`, and place it in `data/raw/`.

## Expected schema

The training script checks the real file against this list before doing anything.
If a column is missing or the target is not what we expect, training stops and
reports the mismatch instead of guessing.

| Column | Type | Notes |
|---|---|---|
| `job_id` | integer | Identifier |
| `title` | text | Job title |
| `location` | text | Often blank |
| `department` | text | Often blank |
| `salary_range` | text | Often blank |
| `company_profile` | text | Often blank |
| `description` | text | Main body text |
| `requirements` | text | Often blank |
| `benefits` | text | Often blank |
| `telecommuting` | 0/1 | Flag |
| `has_company_logo` | 0/1 | Flag |
| `has_questions` | 0/1 | Flag |
| `employment_type` | text | Often blank |
| `required_experience` | text | Often blank |
| `required_education` | text | Often blank |
| `industry` | text | Often blank |
| `function` | text | Often blank |
| `fraudulent` | 0/1 | **Target**: 1 = fraudulent, 0 = genuine |

Note: EMSCAD has **no company-name column**. The company name is therefore shown
to the user and used by the warning-sign rules, but it is not fed to the model.

## Verified facts

Filled in during Phase 2 with the real numbers:

- Rows: _not checked yet_
- Class counts: _not checked yet_
- Licence, as written on the source page: _not checked yet_
- Source URL and date checked: _not checked yet_
