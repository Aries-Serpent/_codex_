"""Command line interface for offline or host-integrated deep research."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from codex.deep_research.contracts import ResearchBundle
from codex.deep_research.pipeline import ExecutionLimits, run_research


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build an auditable research bundle from supplied/local evidence."
    )
    parser.add_argument("--brief", required=True, type=Path, help="Research brief JSON")
    parser.add_argument(
        "--sources",
        type=Path,
        help="JSON array of supplied evidence objects (locator, content, optional metadata)",
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        type=Path,
        help="Local CSV or JSONL dataset to profile; may be repeated",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        help="Checkpoint JSON from a prior bundle to resume",
    )
    parser.add_argument("--output", required=True, type=Path, help="Bundle output directory")
    parser.add_argument("--max-search-calls", type=int, default=40)
    parser.add_argument("--max-sources", type=int, default=60)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--deadline-seconds", type=float, default=1800)
    args = parser.parse_args(argv)

    try:
        brief = _read_json(args.brief)
        source_items = _read_json(args.sources) if args.sources else []
        if not isinstance(source_items, list):
            raise ValueError("--sources must contain a JSON array")
        checkpoint = _read_json(args.checkpoint) if args.checkpoint else None
        if isinstance(checkpoint, dict) and "checkpoint" in checkpoint:
            checkpoint = checkpoint["checkpoint"]
        bundle = run_research(
            brief,
            local_sources=source_items,
            dataset_paths=args.dataset,
            checkpoint=checkpoint,
            limits=ExecutionLimits(
                max_search_calls=args.max_search_calls,
                max_sources=args.max_sources,
                max_retries=args.max_retries,
                deadline_seconds=args.deadline_seconds,
            ),
        )
        _write_bundle(args.output, bundle)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"{bundle.status}: {args.output.resolve()}")
    return 0 if bundle.status == "complete" else 2


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_bundle(output_dir: Path, bundle: ResearchBundle) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = bundle.to_dict()
    outputs = {
        "bundle.json": _json_bytes(data),
        "query_ledger.jsonl": _jsonl_bytes(data["query_ledger"]),
        "sources.jsonl": _jsonl_bytes(data["sources"]),
        "evidence.jsonl": _jsonl_bytes(data["evidence"]),
        "contradictions.jsonl": _jsonl_bytes(data["contradictions"]),
        "objective_matrix.json": _json_bytes(data["objective_matrix"]),
        "verification.json": _json_bytes(data["verification"]),
        "azimuth.json": _json_bytes(data["azimuth"]),
        "checkpoint.json": _json_bytes(data["checkpoint"]),
        "report.md": data["report"].encode("utf-8"),
    }
    for name, content in outputs.items():
        _atomic_write(output_dir / name, content)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _jsonl_bytes(values: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        for value in values
    )


def _atomic_write(path: Path, content: bytes) -> None:
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except OSError:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(main())
