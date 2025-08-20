#!/usr/bin/env bash
set -euo pipefail

pre-commit run --all-files
pytest
python -m build -n
