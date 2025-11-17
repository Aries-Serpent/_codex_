#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    import yaml  # optional
except Exception:
    yaml = None


def _load_schema():
    sp = Path("docs/templates/status/codex_status_template.schema.yaml")
    if not sp.exists():
        print(
            "schema not found at docs/templates/status/codex_status_template.schema.yaml",
            file=sys.stderr,
        )
        return None
    txt = sp.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(txt)
    # minimal shim: schema present → act as sentinel
    return {"$schema": "shim", "__raw__": txt}


def _soft_validate(obj: dict) -> bool:
    # required top-level keys (per v1.1)
    required = [
        "metadata",
        "snapshot",
        "delta",
        "patches",
        "automation",
        "security",
        "questions",
        "decisions",
    ]
    ok = all(k in obj for k in required)
    if not ok:
        missing = [k for k in required if k not in obj]
        print(f"[soft-validate] missing keys: {missing}", file=sys.stderr)
    return ok


def _jsonschema_validate(schema: dict, obj: dict) -> bool:
    try:
        import jsonschema  # optional
    except Exception:
        return _soft_validate(obj)
    try:
        jsonschema.validate(obj, schema)  # raises on error
        return True
    except Exception as e:
        print(f"[jsonschema] {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print("usage: validate_status_update.py <path-to-status.json>", file=sys.stderr)
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"file not found: {p}", file=sys.stderr)
        return 2
    data = json.loads(p.read_text(encoding="utf-8"))
    schema = _load_schema()
    ok = _jsonschema_validate(schema, data) if schema else _soft_validate(data)
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
