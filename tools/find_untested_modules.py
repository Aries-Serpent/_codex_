"""Identify modules in ``src`` without matching tests."""

from __future__ import annotations

import argparse
import ast
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


def load_aggregate_modules(tests_root: Path) -> Set[str]:
    """Load module paths declared in aggregate readiness tests, if present."""

    readiness_file = tests_root / "test_readiness_remaining_modules.py"
    if not readiness_file.exists():
        return set()

    try:
        tree = ast.parse(readiness_file.read_text())
    except OSError:
        return set()

    for node in tree.body:
        assign_value = None
        target_ids: Set[str] = set()

        if isinstance(node, ast.Assign):
            assign_value = node.value
            target_ids = {getattr(target, "id", "") for target in node.targets}
        elif isinstance(node, ast.AnnAssign):
            assign_value = node.value
            if isinstance(node.target, ast.Name):
                target_ids = {node.target.id}

        if "MODULE_PATHS" in target_ids and assign_value is not None:
            try:
                value = ast.literal_eval(assign_value)
            except ValueError:
                return set()
            return {str(item) for item in value}
    return set()


def find_missing_tests(source_root: Path, tests_root: Path) -> List[str]:
    missing: List[str] = []
    test_files = {path.name for path in tests_root.rglob("test_*.py")}
    aggregate_modules = load_aggregate_modules(tests_root)

    for module in iter_source_modules(source_root):
        expected = candidate_test_names(module)
        module_name = module.relative_to(source_root).with_suffix("").as_posix().replace("/", ".")
        if module_name in aggregate_modules:
            continue
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
