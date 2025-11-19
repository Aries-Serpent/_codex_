from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.space_traversal import stable_manifest

DEFAULT_OUTPUT = Path("audit_artifacts/baseline_summary.json")


def _load_decoded(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(decoded: dict[str, Any]) -> dict[str, Any]:
    report = decoded.get("report", {})
    if not isinstance(report, dict):
        return {}
    return {
        "id": report.get("id", ""),
        "generated_at": report.get("generated_at", ""),
    }


def build_baseline(
    decoded: dict[str, Any], stable_output: bool, output_path: Path | None = None
) -> Path:
    summary = {
        "report": _ensure_report(decoded),
        "gap_count": len(decoded.get("gaps", [])),
    }
    destination = output_path or DEFAULT_OUTPUT
    if stable_output:
        return stable_manifest.write_stable_json(summary, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate baseline summary from decoded report")
    parser.add_argument("input", type=Path, help="Path to decoded JSON file")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination for baseline summary",
    )
    parser.add_argument(
        "--stable-output",
        action="store_true",
        help="Write deterministic JSON output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decoded = _load_decoded(args.input)
    build_baseline(decoded, args.stable_output, args.output)
    print(f"Baseline written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
