<!-- BEGIN: CODEX_DOCS_GETTING_STARTED -->
# Getting Started (Ubuntu)

## Prerequisites
- Python 3.10+
- (Optional) Docker & Docker Compose

## Local Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r docs/requirements.txt
pip install -e .[dev]  # if available
```

Run Docs

```bash
mkdocs serve
```
