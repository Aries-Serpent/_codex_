"""Compute simple entropy metrics for source files.

The goal is to approximate information density to highlight overly repetitive
modules. Lower entropy can signal boilerplate or duplication, while higher
entropy often indicates dense logic that may benefit from refactoring.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable, List, Tuple

DEFAULT_EXTENSIONS = (".py", ".md", ".yaml", ".yml")


def shannon_entropy(text: str) -> float:
    """Calculate Shannon entropy in bits for a given string."""

    if not text:
        return 0.0

    frequencies = {ch: text.count(ch) for ch in set(text)}
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in frequencies.values())


def iter_files(base_dir: Path, extensions: Iterable[str]) -> Iterable[Path]:
    for path in base_dir.rglob("*"):
        if path.is_file() and path.suffix in extensions:
            yield path


def analyze_paths(paths: Iterable[Path]) -> List[Tuple[Path, float, int]]:
    results: List[Tuple[Path, float, int]] = []
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        entropy = shannon_entropy(content)
        results.append((path, entropy, len(content)))
    return sorted(results, key=lambda item: item[1])


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze code entropy")
    parser.add_argument(
        "base_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "src",
        help="Directory to scan (defaults to src)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=4.0,
        help="Entropy threshold to flag low-information files",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=list(DEFAULT_EXTENSIONS),
        help="File extensions to include",
    )
    args = parser.parse_args()

    files = list(iter_files(args.base_dir, args.extensions))
    results = analyze_paths(files)

    if not results:
        print("No files analyzed.")
        return

    print(f"Analyzed {len(results)} files in {args.base_dir}.")
    print(f"Flagging files with entropy below {args.threshold} bits.")

    for path, entropy, length in results:
        if entropy < args.threshold:
            print(f"[LOW] {entropy:.2f} bits - {path} ({length} chars)")

    average_entropy = sum(item[1] for item in results) / len(results)
    print(f"Average entropy: {average_entropy:.2f} bits")


if __name__ == "__main__":
    main()
