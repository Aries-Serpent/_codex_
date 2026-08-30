
#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
export ITA_API_KEY=$(python scripts/issue_api_key.py)
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
