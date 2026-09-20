#!/usr/bin/env bash
set -euo pipefail
PYTHON=${PYTHON:-python3}
VENV_DIR=${VENV_DIR:-.venv}

${PYTHON} -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pre-commit install || true
pre-commit run --all-files || true
pytest -q tests -q
