#!/usr/bin/env python3
"""Convert raw reasoning datasets into StreamingDataModule-ready JSONL."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any

from codex_ml.data.checksums import manifest_for_paths
from codex_ml.data.reasoning_manifest import (
    ReasoningCorpus,
    ReasoningCorpusError,
    build_corpus_selection,
    get_reasoning_corpus,
)


def _corpus_argument(value: str) -> str:
    try:
        corpus = get_reasoning_corpus(value)
    except ReasoningCorpusError as exc:  # pragma: no cover - argument validation
        raise argparse.ArgumentTypeError(str(exc)) from exc
    return corpus.name


def _read_jsonl(path: Path) -> Iterator[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            if isinstance(payload, Mapping):
                yield payload
            else:  # pragma: no cover - defensive
                raise ValueError(f"expected mapping rows in {path}")


def _read_json(path: Path) -> Iterator[Mapping[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, Mapping):
        yield data
    elif isinstance(data, list):
        for entry in data:
            if not isinstance(entry, Mapping):
                raise ValueError(f"expected mapping entries in {path}")
            yield entry
    else:  # pragma: no cover - defensive
        raise ValueError(f"unsupported JSON structure in {path}")


def _read_csv(path: Path) -> Iterator[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield {key: value for key, value in row.items() if value not in (None, "")}


def _iter_raw_records(path: Path) -> Iterable[Mapping[str, Any]]:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return _read_jsonl(path)
    if suffix == ".json":
        return _read_json(path)
    if suffix in {".csv", ".tsv"}:
        return _read_csv(path)
    raise ValueError(f"unsupported input format: {path.suffix}")


def _coerce_metadata(record: Mapping[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    raw_meta = record.get("metadata")
    if isinstance(raw_meta, Mapping):
        metadata.update(raw_meta)
    source = record.get("source") or record.get("dataset")
    if source and "source" not in metadata:
        metadata["source"] = source
    difficulty = record.get("difficulty") or record.get("level")
    if difficulty is not None and "difficulty" not in metadata:
        metadata["difficulty"] = difficulty
    if "id" in record and "example_id" not in metadata:
        metadata["example_id"] = record["id"]
    return metadata


def _transform_proof(record: Mapping[str, Any]) -> Mapping[str, Any]:
    prompt = record.get("input") or record.get("prompt") or record.get("statement")
    target = record.get("target") or record.get("proof") or record.get("output")
    if not prompt or not target:
        raise ValueError(
            "proof_logs records require `input`/`statement` and `target`/`proof` fields"
        )
    metadata = _coerce_metadata(record)
    if "domain" not in metadata and record.get("domain"):
        metadata["domain"] = record["domain"]
    steps = record.get("steps") or record.get("proof_steps")
    if steps is not None and "steps" not in metadata:
        metadata["steps"] = steps
    return {"input": prompt, "target": target, "metadata": metadata}


def _transform_math(record: Mapping[str, Any]) -> Mapping[str, Any]:
    prompt = record.get("input") or record.get("question") or record.get("prompt")
    target = record.get("target") or record.get("answer") or record.get("solution")
    if not prompt or not target:
        raise ValueError("math_word_problems records require `question` and `answer` fields")
    metadata = _coerce_metadata(record)
    if "answer_type" not in metadata and record.get("answer_type"):
        metadata["answer_type"] = record["answer_type"]
    if "units" not in metadata and record.get("units"):
        metadata["units"] = record["units"]
    return {"input": prompt, "target": target, "metadata": metadata}


def _transform_tools(record: Mapping[str, Any]) -> Mapping[str, Any]:
    prompt = record.get("input") or record.get("query") or record.get("prompt")
    target = record.get("target") or record.get("response") or record.get("answer")
    if not prompt or not target:
        raise ValueError("tool_traces records require `query` and `response` fields")
    metadata = _coerce_metadata(record)
    tools = record.get("tools") or record.get("tool_calls")
    if isinstance(tools, list):
        metadata.setdefault("tools", tools)
    return {"input": prompt, "target": target, "metadata": metadata}


_TRANSFORMERS: dict[str, callable[[Mapping[str, Any]], Mapping[str, Any]]] = {
    "proof_logs": _transform_proof,
    "math_word_problems": _transform_math,
    "tool_traces": _transform_tools,
}


def _select_output_name(corpus: ReasoningCorpus, provided: str | None, split: str) -> str:
    if provided:
        return provided
    if len(corpus.artifacts) == 1:
        return corpus.artifacts[0].filename
    return f"{corpus.name}-{split}.jsonl"


def prepare_corpus(
    corpus: ReasoningCorpus,
    inputs: list[Path],
    output_dir: Path,
    *,
    output_name: str | None = None,
    split: str = "train",
    limit: int | None = None,
    write_manifest: bool = False,
) -> dict[str, Any]:
    transformer = _TRANSFORMERS.get(corpus.name)
    if transformer is None:
        raise ValueError(f"no transformer registered for corpus '{corpus.name}'")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = _select_output_name(corpus, output_name, split)
    output_path = output_dir / output_filename

    total = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for path in inputs:
            for record in _iter_raw_records(path):
                payload = transformer(record)
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
                total += 1
                if limit is not None and total >= limit:
                    break
            if limit is not None and total >= limit:
                break

    manifest_path = None
    if write_manifest:
        manifest_path = output_path.with_suffix(".manifest.jsonl")
        manifest_for_paths([output_path], manifest_path)

    selection = build_corpus_selection([corpus.name], root=output_dir, strict=False)
    return {
        "output_path": str(output_path),
        "records": total,
        "manifest": str(manifest_path) if manifest_path else None,
        "corpus": selection,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus", required=True, type=_corpus_argument, help="Reasoning corpus identifier"
    )
    parser.add_argument(
        "--input",
        "-i",
        action="append",
        required=True,
        help="Path(s) to raw dataset files (JSONL/JSON/CSV)",
    )
    parser.add_argument(
        "--output-dir", "-o", required=True, help="Directory to place transformed JSONL"
    )
    parser.add_argument(
        "--output-name", help="Override output filename (defaults to corpus artifact name)"
    )
    parser.add_argument(
        "--split", default="train", help="Split name used when generating default filenames"
    )
    parser.add_argument("--limit", type=int, help="Optional cap on the number of records to emit")
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Write a checksum manifest alongside the generated JSONL",
    )

    args = parser.parse_args(argv)

    corpus = get_reasoning_corpus(args.corpus)
    input_paths = [Path(p).expanduser().resolve() for p in args.input]
    missing_inputs = [str(path) for path in input_paths if not path.exists()]
    if missing_inputs:
        parser.error(f"input files not found: {', '.join(missing_inputs)}")

    summary = prepare_corpus(
        corpus,
        input_paths,
        Path(args.output_dir).expanduser().resolve(),
        output_name=args.output_name,
        split=args.split,
        limit=args.limit,
        write_manifest=bool(args.manifest),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
