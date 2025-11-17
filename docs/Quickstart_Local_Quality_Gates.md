# Quickstart: Local Quality Gates

These checks run on your machine (local-only) to catch formatting and fence issues early.

## One-time setup
```bash
pip install pre-commit pytest
pre-commit install
```text

## On each change
```bash
pre-commit run --all-files
python3 validate_fences.py docs/  # or the paths you touched
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```text

## What the fence validator checks
- Opener/closer characters and lengths are consistent.
- No backticks in the *info string* for backtick fences (spec).
- Outer fence is longer than any inner closing run (house rule).
