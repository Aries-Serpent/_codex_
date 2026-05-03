#!/usr/bin/env python3
"""Utility to convert raw reasoning datasets into StreamingDataModule JSONL."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable, Iterator, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any

# Ensure the repo's ``src`` directory is importable when running as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if SRC_DIR.exists():
    import sys

    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

from codex_ml.data.checksums import manifest_for_paths  # noqa: E402

SUPPORTED_TASKS = {"proof_logs", "math_word_problems", "tool_traces"}


def _load_records(path: Path, input_format: str | None = None) -> list[Mapping[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    fmt = (input_format or path.suffix.lstrip(".")).lower()
    if fmt in {"jsonl", "ndjson"}:
        records: list[Mapping[str, Any]] = []
        for raw in path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            obj = json.loads(raw)
            if isinstance(obj, Mapping):
                records.append(dict(obj))
            else:
                records.append({"raw": obj})
        return records
    if fmt == "json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            normalised: list[Mapping[str, Any]] = []
            for entry in data:
                if isinstance(entry, Mapping):
                    normalised.append(dict(entry))
                else:
                    normalised.append({"raw": entry})
            return normalised
        raise ValueError(f"Unsupported JSON structure in {path}")
    if fmt in {"csv", "tsv"}:
        delimiter = "," if fmt == "csv" else "\t"
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            return [dict(row) for row in reader]
    raise ValueError(f"Unsupported input format '{fmt}' for {path}")


def _ensure_identifier(prefix: str, record: Mapping[str, Any], index: int) -> str:
    for key in ("id", "example_id", "uid", "problem_id", "source_id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
        if isinstance(value, (int, float)):
            return f"{prefix}-{value}"
    return f"{prefix}-{index:05d}"


def _coerce_steps(record: Mapping[str, Any]) -> Sequence[str]:
    steps = record.get("proof_steps") or record.get("steps") or record.get("scratchpad")
    if isinstance(steps, str):
        return [step.strip() for step in steps.split("\n") if step.strip()]
    if isinstance(steps, Sequence):
        return [str(step) for step in steps]
    return []


def _transform_proof_logs(records: list[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
    for index, record in enumerate(records):
        prompt = record.get("problem") or record.get("statement") or record.get("prompt")
        completion = record.get("result") or record.get("answer") or record.get("conclusion")
        yield {
            "id": _ensure_identifier("proof", record, index),
            "source": "proof_logs",
            "prompt": prompt,
            "response": completion,
            "proof_steps": list(_coerce_steps(record)),
            "metadata": {
                "difficulty": record.get("difficulty"),
                "tags": record.get("tags"),
                "original": record,
            },
        }


def _transform_math_word_problems(records: list[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
    for index, record in enumerate(records):
        question = record.get("question") or record.get("prompt")
        answer = record.get("answer") or record.get("solution")
        rationale = record.get("rationale") or record.get("reasoning")
        yield {
            "id": _ensure_identifier("mwp", record, index),
            "source": "math_word_problems",
            "prompt": question,
            "response": answer,
            "rationale": rationale,
            "metadata": {
                "difficulty": record.get("difficulty"),
                "category": record.get("category"),
                "original": record,
            },
        }


def _transform_tool_traces(records: list[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
    for index, record in enumerate(records):
        calls = record.get("tool_calls") or record.get("calls") or record.get("trace")
        if isinstance(calls, Mapping):
            calls = [calls]
        elif isinstance(calls, Sequence) and not isinstance(calls, (str, bytes)):
            calls = [dict(call) if isinstance(call, Mapping) else {"raw": call} for call in calls]
        else:
            calls = []
        yield {
            "id": _ensure_identifier("trace", record, index),
            "source": "tool_traces",
            "task": record.get("task") or record.get("query"),
            "tool_calls": calls,
            "response": record.get("final_answer")
            or record.get("answer")
            or record.get("response"),
            "metadata": {
                "difficulty": record.get("difficulty"),
                "original": record,
            },
        }


def _write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, choices=sorted(SUPPORTED_TASKS))
    parser.add_argument("--input", required=True, type=Path, help="Path to raw dataset file")
    parser.add_argument("--output", required=True, type=Path, help="Destination JSONL path")
    parser.add_argument(
        "--input-format", help="Override input format detection (jsonl/json/csv/tsv)"
    )
    parser.add_argument("--name", help="Optional dataset name annotation")
    parser.add_argument(
        "--write-manifest",
        type=Path,
        help="Optional path to write a checksum manifest for the transformed dataset",
    )
    return parser


def _transform(task: str, records: list[Mapping[str, Any]]) -> Iterator[Mapping[str, Any]]:
    if task == "proof_logs":
        return _transform_proof_logs(records)
    if task == "math_word_problems":
        return _transform_math_word_problems(records)
    if task == "tool_traces":
        return _transform_tool_traces(records)
    raise ValueError(f"Unsupported task '{task}'")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    records = _load_records(args.input, args.input_format)
    transformed = list(_transform(args.task, records))
    if not transformed:
        raise RuntimeError("No records were produced; check the input payload")

    for record in transformed:
        if args.name and isinstance(record, MutableMapping):
            record.setdefault("dataset", args.name)

    written = _write_jsonl(args.output, transformed)
    print(f"Wrote {written} examples to {args.output}")

    if args.write_manifest:
        manifest_for_paths([args.output], args.write_manifest)
        print(f"Manifest written to {args.write_manifest}")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
