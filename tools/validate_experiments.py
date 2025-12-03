"""
Validate experiment configs (JSON or TOML) against JSONSchema.

Usage:
    python tools/validate_experiments.py --schema configs/schemas/experiments.schema.json --paths configs/experiments

Exit codes:
    0 success
    2 schema invalid
    3 IO or validation error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None


def load_schema(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"Failed to read schema: {e}", file=sys.stderr)
        sys.exit(2)


def load_config(path: Path):
    try:
        if path.suffix == ".json":
            return json.loads(path.read_text())
        elif path.suffix == ".toml":
            # Proper fallback for tomllib (Python 3.11+) vs tomli (Python <3.11)
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib  # type: ignore
            return tomllib.loads(path.read_text())
        else:
            raise ValueError("Unsupported file extension.")
    except Exception as e:
        raise RuntimeError(f"Failed to load {path}: {e}")


def validate(schema, config, path: Path):
    try:
        jsonschema.validate(config, schema)
        return True, None
    except jsonschema.ValidationError as ve:
        return False, f"{path}: {ve.message} at {list(ve.path)}"
    except Exception as e:
        return False, f"{path}: {e}"


def discover(paths: List[Path]) -> List[Path]:
    """
    Discover config files, excluding schema files.
    Skips files named like 'schema*.json', '*.schema.json', or in 'schemas/' directories.
    """
    result = []
    for p in paths:
        if p.is_dir():
            for ext in (".json", ".toml"):
                for candidate in p.rglob(f"*{ext}"):
                    # Skip schema files by name pattern or directory
                    if "schema" in candidate.name.lower():
                        continue
                    if any(part.lower() == "schemas" for part in candidate.parts):
                        continue
                    result.append(candidate)
        elif p.is_file():
            # Only add file if it's not a schema file
            if "schema" not in p.name.lower() and not any(
                part.lower() == "schemas" for part in p.parts
            ):
                result.append(p)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True, type=Path)
    ap.add_argument("--paths", required=True, type=Path, nargs="+")
    args = ap.parse_args()

    if jsonschema is None:
        print("jsonschema package not installed.", file=sys.stderr)
        sys.exit(2)

    schema = load_schema(args.schema)
    files = discover(args.paths)
    if not files:
        print("No config files found; validated 0 config file(s).")
        sys.exit(0)

    failures = []
    for f in files:
        try:
            cfg = load_config(f)
        except Exception as e:
            failures.append(f"{f}: {e}")
            continue
        ok, err = validate(schema, cfg, f)
        if not ok:
            failures.append(err)

    if failures:
        print("Validation failures:", file=sys.stderr)
        for fmsg in failures:
            print(f" - {fmsg}", file=sys.stderr)
        sys.exit(3)

    print(f"Validated {len(files)} config file(s) successfully.")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
