"""Simple tokenizer micro-benchmark helper."""

from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path
from typing import Iterable, List

from codex_ml.tokenization.api import WhitespaceTokenizer

_SAMPLE_TEXT = [
    "Codex ML focuses on reproducible training pipelines.",
    "Tokenizer benchmarks ensure throughput regressions are visible.",
    "Deterministic behaviour keeps evaluation comparable across runs.",
]


def _load_corpus(path: Path | None) -> List[str]:
    if path is None:
        return list(_SAMPLE_TEXT)
    try:
        return [
            line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
    except FileNotFoundError as exc:
        raise SystemExit(f"corpus not found: {path}") from exc


def bench(tokenizer: WhitespaceTokenizer, texts: Iterable[str], rounds: int) -> dict[str, float]:
    durations: List[float] = []
    texts = list(texts)
    if not texts:
        raise SystemExit("corpus is empty")
    for _ in range(rounds):
        start = time.perf_counter()
        tokens = 0
        for t in texts:
            tokens += len(tokenizer.encode(t))
        durations.append(time.perf_counter() - start)
    total_tokens = sum(len(tokenizer.encode(t)) for t in texts)
    mean = statistics.mean(durations)
    return {
        "rounds": rounds,
        "mean_s": mean,
        "median_s": statistics.median(durations),
        "min_s": min(durations),
        "max_s": max(durations),
        "tokens_per_second": total_tokens / mean if mean else float("inf"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        help="Optional newline-delimited text file to tokenize.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=5,
        help="Number of repetitions to average (default: 5).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    texts = _load_corpus(args.corpus)
    tokenizer = WhitespaceTokenizer()
    stats = bench(tokenizer, texts, max(1, args.rounds))
    for key, value in stats.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
