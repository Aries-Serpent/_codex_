"""Identify modules in ``src`` without matching tests."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Set


def iter_source_modules(source_root: Path) -> Iterable[Path]:
    for path in source_root.rglob("*.py"):
        if path.name.startswith("__"):
            continue
        yield path


def candidate_test_names(module_path: Path) -> Set[str]:
    stem = module_path.stem
    return {f"test_{stem}.py", f"{stem}_test.py"}


def find_missing_tests(source_root: Path, tests_root: Path) -> List[str]:
    missing: List[str] = []
    test_files = {path.name for path in tests_root.rglob("test_*.py")}

    for module in iter_source_modules(source_root):
        expected = candidate_test_names(module)
        if not expected & test_files:
            missing.append(str(module.relative_to(source_root)))
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Locate untested modules")
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "src",
        help="Root of source tree",
    )
    parser.add_argument(
        "--tests-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "tests",
        help="Root of tests tree",
    )
    args = parser.parse_args()

    missing = find_missing_tests(args.source_root, args.tests_root)
    if not missing:
        print("All modules appear to have corresponding tests.")
        return

    print("Modules without discovered tests:")
    for module in missing:
        print(f"- {module}")


if __name__ == "__main__":
    main()
