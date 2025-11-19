from __future__ import annotations

import argparse
import base64
import gzip
import json
from pathlib import Path
from typing import Any

from scripts.space_traversal import extract_validate_gaps
from scripts.space_traversal import stable_manifest
from scripts.space_traversal import validate_snapshot_schema

DEFAULT_INPUT = Path("tests/fixtures/pasted.txt")
DEFAULT_DECODED = Path("audit_artifacts/decoded_snapshot.json")
DEFAULT_EXTRACT = Path("audit_artifacts/gaps_extracted.json")


def decode_base64_gzip(input_path: Path) -> dict[str, Any]:
    payload = input_path.read_text(encoding="utf-8").strip()
    data = base64.b64decode(payload)
    decompressed = gzip.decompress(data)
    return json.loads(decompressed.decode("utf-8"))


def _write_json(data: Any, output_path: Path, stable: bool) -> Path:
    if stable:
        return stable_manifest.write_stable_json(data, output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return output_path


def decode_and_validate(
    input_path: Path,
    output_path: Path,
    extract_path: Path | None,
    schema_path: Path | None,
    stable_output: bool,
    generate_baseline: bool,
) -> dict[str, Any]:
    decoded = decode_base64_gzip(input_path)

    if schema_path:
        validate_snapshot_schema.validate_snapshot(decoded, schema_path)

    written_outputs = {"decoded": _write_json(decoded, output_path, stable_output)}

    if extract_path:
        extracted = extract_validate_gaps.extract_gaps(decoded)
        written_outputs["extracted"] = _write_json(extracted, extract_path, stable_output)

    if generate_baseline:
        from scripts.space_traversal import generate_baseline

        baseline_path = generate_baseline.build_baseline(decoded, stable_output)
        written_outputs["baseline"] = baseline_path

    return {
        "decoded": decoded,
        "paths": written_outputs,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decode artifact and validate schema")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Base64+gzip input file")
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_DECODED, help="Destination for decoded JSON"
    )
    parser.add_argument(
        "--extract",
        type=Path,
        default=DEFAULT_EXTRACT,
        help="Optional destination for extracted gaps",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("scripts/space_traversal/schemas/validate_report_schema.json"),
        help="Schema path used for validation",
    )
    parser.add_argument(
        "--stable-output",
        action="store_true",
        help="Write JSON deterministically for reproducible pipelines",
    )
    parser.add_argument(
        "--generate-baseline",
        action="store_true",
        help="Also produce a baseline summary via generate_baseline.py",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decode_and_validate(
        input_path=args.input,
        output_path=args.output,
        extract_path=args.extract,
        schema_path=args.schema,
        stable_output=args.stable_output,
        generate_baseline=args.generate_baseline,
    )
    print(f"Decoded report written to {args.output}")
    if args.extract:
        print(f"Gaps extracted to {args.extract}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
