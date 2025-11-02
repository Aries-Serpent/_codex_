"""Performance snapshot CLI to normalize simple metric logs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Sequence, Tuple

MetricSpec = Tuple[str, str]

# Mapping from raw metric keys to (section, normalized_key).
METRIC_MAP: Mapping[str, MetricSpec] = {
    "steps/s": ("training", "throughput_steps_per_sec"),
    "samples/s": ("training", "throughput_samples_per_sec"),
    "epoch_time_s": ("training", "epoch_time_seconds"),
    "loss": ("training", "loss"),
    "latency_p50_ms": ("inference", "latency_p50_ms"),
    "latency_p90_ms": ("inference", "latency_p90_ms"),
    "latency_p99_ms": ("inference", "latency_p99_ms"),
}


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a perf log to structured JSON")
    parser.add_argument("--log", type=Path, required=True, help="Path to perf metrics log")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("perf_snapshot.json"),
        help="Destination JSON file (default: perf_snapshot.json)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _ensure_section(
    store: MutableMapping[str, MutableMapping[str, float]], section: str
) -> MutableMapping[str, float]:
    if section not in store:
        store[section] = {}
    return store[section]


def parse_perf_log(text: str) -> Dict[str, Any]:
    structured: Dict[str, MutableMapping[str, float]] = {}
    raw: Dict[str, float] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = (item.strip() for item in line.split(":", 1))
        try:
            numeric = float(value)
        except ValueError:
            continue
        raw[key] = numeric
        spec = METRIC_MAP.get(key)
        if spec:
            section, normalized_key = spec
            section_store = _ensure_section(structured, section)
            section_store[normalized_key] = numeric
    structured["raw"] = raw
    return structured


def write_snapshot(out_path: Path, snapshot: Mapping[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> Mapping[str, Any]:
    args = _parse_args(argv)
    text = args.log.read_text(encoding="utf-8")
    snapshot = parse_perf_log(text)
    write_snapshot(args.out, snapshot)
    print(f"Performance snapshot written to {args.out}")
    return snapshot


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
