#!/usr/bin/env python3
"""
Gap 35 — GitHub Actions workflow YAML validator.

Called by the ``check-github-workflows`` pre-commit hook.
Validates each workflow file passed as a CLI argument by:

  1. Parsing it with ``yaml.safe_load`` (always — catches syntax errors).
  2. Validating against the GitHub Actions JSON Schema using
     ``check-jsonschema`` when that package is available; otherwise only
     the YAML-syntax check is performed (non-blocking degradation).

Usage::

    python scripts/ci/check_workflow_yaml.py .github/workflows/ci.yml ...
    pre-commit run check-github-workflows --all-files
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

GITHUB_ACTIONS_SCHEMA = "https://json.schemastore.org/github-workflow.json"


def _check_jsonschema_available() -> bool:
    try:
        import check_jsonschema  # noqa: F401  # type: ignore[import]
        return True
    except ImportError:
        return False


def validate_syntax(paths: list[str]) -> list[str]:
    """Return a list of error strings for files with invalid YAML."""
    errors: list[str] = []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            errors.append(f"{path}: YAML syntax error — {exc}")
        except OSError as exc:
            errors.append(f"{path}: cannot open file — {exc}")
    return errors


def validate_schema(paths: list[str]) -> list[str]:
    """
    Validate *paths* against the GitHub Actions JSON Schema.

    Returns error strings on failure; empty list on success.
    Requires ``check-jsonschema`` to be installed.
    """
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "check_jsonschema",
            "--schemafile",
            GITHUB_ACTIONS_SCHEMA,
            *paths,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [result.stdout.strip() or result.stderr.strip()]
    return []


def main() -> None:
    paths = sys.argv[1:]
    if not paths:
        print("check-workflow-yaml: no files to check.")
        sys.exit(0)

    # Step 1: YAML syntax
    syntax_errors = validate_syntax(paths)
    if syntax_errors:
        for err in syntax_errors:
            print(f"  ❌ {err}", file=sys.stderr)
        sys.exit(1)

    # Step 2: JSON Schema (if available)
    if _check_jsonschema_available():
        schema_errors = validate_schema(paths)
        if schema_errors:
            for err in schema_errors:
                print(f"  ❌ {err}", file=sys.stderr)
            sys.exit(1)
        print(
            f"  ✅ {len(paths)} workflow file(s) passed YAML syntax + schema validation."
        )
    else:
        print(
            f"  ✔  {len(paths)} workflow file(s) passed YAML syntax check.  "
            "Install check-jsonschema for full schema validation: "
            "pip install check-jsonschema"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
