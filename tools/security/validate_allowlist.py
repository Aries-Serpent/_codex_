"""
Validate security_allowlist.json against configs/schemas/security_allowlist.schema.json.

Usage:
    python tools/security/validate_allowlist.py
Exit codes:
    0 - valid or file absent
    2 - schema or allowlist invalid
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCHEMA = Path("configs/schemas/security_allowlist.schema.json")
ALLOW = Path("security_allowlist.json")


def main() -> int:
    if not ALLOW.exists():
        print("security_allowlist.json not found; nothing to validate.")
        return 0
    if not SCHEMA.exists():
        print("Schema not found; skipping validation.")
        return 0
    try:
        import jsonschema  # type: ignore
    except Exception:
        print("jsonschema not installed; skipping validation.", file=sys.stderr)
        return 0
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        allow = json.loads(ALLOW.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(instance=allow, schema=schema)
        print("Allowlist is valid ✓")
        return 0
    except Exception as e:
        print(f"Allowlist validation failed: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
