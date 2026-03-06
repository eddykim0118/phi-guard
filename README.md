[🇺🇸 English](./README.md) | [🇰🇷 한국어](./README.ko.md)

# PHI Guard

> HIPAA PHI scanner for CI/CD pipelines — like gitleaks, but for healthcare data.

<!-- Badges (activate when published) -->
<!-- ![PyPI](https://img.shields.io/pypi/v/phi-guard) -->
<!-- ![Python](https://img.shields.io/pypi/pyversions/phi-guard) -->
<!-- ![License](https://img.shields.io/github/license/eddykim/phi-guard) -->
<!-- ![CI](https://img.shields.io/github/actions/workflow/status/eddykim/phi-guard/ci.yml) -->

## The Problem

Developers working on healthcare applications accidentally commit Protected Health Information (PHI) into code repositories:

```python
# test_patient.py
def test_create_patient():
    patient = Patient(
        name="John Doe",
        ssn="123-45-6789",           # Real SSN in test fixture
        mrn="MRN-00012345",          # Real Medical Record Number
        email="patient@email.com"
    )
```

**This is a HIPAA violation.** Fines range from $50,000 to $1,500,000 per incident.

GitHub's Secret Scanning catches API keys and passwords — but it has **zero support for HIPAA's 18 PHI identifiers**. PHI Guard fills that gap.

## What PHI Guard Does

PHI Guard scans your codebase for all 18 types of Protected Health Information defined by HIPAA:

| # | PHI Type | Status |
|---|----------|--------|
| 1 | Names | Planned |
| 2 | Geographic data | Planned |
| 3 | Dates (birth, admission, etc.) | Planned |
| 4 | Phone numbers | Planned |
| 5 | Fax numbers | Planned |
| 6 | Email addresses | Planned |
| 7 | **Social Security Numbers** | **Supported** |
| 8 | Medical Record Numbers | Planned |
| 9 | Health plan beneficiary numbers | Planned |
| 10 | Account numbers | Planned |
| 11 | Certificate/license numbers | Planned |
| 12 | Vehicle identifiers | Planned |
| 13 | Device identifiers | Planned |
| 14 | URLs | Planned |
| 15 | IP addresses | Planned |
| 16 | Biometric identifiers | Planned |
| 17 | Full-face photographs | Out of scope |
| 18 | Other unique identifiers | Planned |

## Use Cases

### Pre-commit Hook (Fast Mode)
Block PHI before it reaches the repository. Regex-only scanning completes in under 3 seconds.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/eddykim/phi-guard
    rev: v0.1.0
    hooks:
      - id: phi-guard
```

### CI/CD Pipeline (Full Mode)
Scan every pull request with NLP-powered detection. Catches names, locations, and other unstructured PHI that regex can't detect.

```yaml
# .github/workflows/phi-guard.yml
- uses: eddykim/phi-guard-action@v1
  with:
    mode: full
```

## Installation

> Coming soon — not yet published to PyPI

```bash
pip install phi-guard
```

## Usage

> Coming soon — CLI in development

```bash
# Scan current directory
phi-guard scan ./

# Scan specific file
phi-guard scan ./tests/fixtures/sample.py

# Output as SARIF (for GitHub Security tab)
phi-guard scan ./ --format sarif
```

## How It Works

PHI Guard uses [Microsoft Presidio](https://github.com/microsoft/presidio) for PII detection, enhanced with:

- **Custom recognizers** for healthcare-specific patterns (MRN, insurance IDs)
- **Stricter SSN detection** — Presidio's default has a bug that filters out valid SSNs
- **Dual-mode architecture** — fast regex for pre-commit, full NLP for CI/CD
- **SARIF output** — integrates with GitHub Security tab

### Architecture

```
┌─────────────────────────────────────────────────┐
│                   PHI Guard                      │
├─────────────────────────────────────────────────┤
│  CLI (Typer)                                    │
│    └── phi-guard scan <path>                    │
├─────────────────────────────────────────────────┤
│  Engine                                          │
│    └── scan_text() / scan_file() / scan_dir()   │
├─────────────────────────────────────────────────┤
│  Recognizers                                     │
│    ├── SSN Recognizer (regex, score 0.85)       │
│    ├── MRN Recognizer (planned)                 │
│    ├── Phone Recognizer (planned)               │
│    └── ... 18 HIPAA identifiers                 │
├─────────────────────────────────────────────────┤
│  Presidio AnalyzerEngine                         │
│    ├── RecognizerRegistry                       │
│    └── SpacyNlpEngine (en_core_web_sm)          │
└─────────────────────────────────────────────────┘
```

## Why Not Just Use Presidio Directly?

You could! But PHI Guard provides:

1. **Healthcare focus** — Only HIPAA PHI, not generic PII
2. **CI/CD integration** — Pre-commit hooks, GitHub Actions, SARIF output
3. **Fixes Presidio bugs** — Default SSN recognizer has score 0.05 (too low to detect)
4. **Incremental scanning** — Only scan changed files in PRs

## Development

```bash
# Clone and setup
git clone https://github.com/eddykim/phi-guard.git
cd phi-guard
poetry install

# Download spaCy model
poetry run python -m spacy download en_core_web_sm

# Run tests
poetry run pytest

# Run the CLI
poetry run phi-guard scan ./
```

## License

Apache 2.0

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

Built with Microsoft [Presidio](https://github.com/microsoft/presidio) and [spaCy](https://spacy.io/).
