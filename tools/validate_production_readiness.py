"""Composite validation script for production readiness checks."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

STRICT = os.getenv("CODEX_VALIDATION_STRICT", "0") == "1"

from tools import detect_gaps
from tools.analyze_code_entropy import analyze_paths, iter_files
from tools.analyze_import_paths import analyze_coupling
from tools.find_untested_modules import find_missing_tests


@dataclass
class ValidationResult:
    name: str
    status: str
    details: Dict[str, object]


def validate_configs(repo_root: Path) -> ValidationResult:
    missing = []
    for required in ["pyproject.toml", "bandit.yaml", "pytest.ini"]:
        if not (repo_root / required).exists():
            missing.append(required)
    status = "fail" if STRICT and missing else "pass"
    return ValidationResult("config_files", status, {"missing": missing})


def validate_entropy(repo_root: Path, threshold: float = 4.0) -> ValidationResult:
    paths = iter_files(repo_root / "src", [".py"])
    analyzed = analyze_paths(paths)
    low_entropy = [str(path) for path, entropy, _ in analyzed if entropy < threshold]
    status = "fail" if STRICT and low_entropy else "pass"
    return ValidationResult(
        "entropy",
        status,
        {"threshold": threshold, "low_entropy_files": low_entropy},
    )


def validate_coupling(repo_root: Path, energy_limit: int = 20) -> ValidationResult:
    coupling = analyze_coupling(repo_root / "src")
    over_limit = [asdict(item) for item in coupling if item.coupling_energy > energy_limit]
    status = "fail" if STRICT and over_limit else "pass"
    return ValidationResult(
        "coupling",
        status,
        {"energy_limit": energy_limit, "over_limit": over_limit[:20]},
    )


def validate_tests(repo_root: Path) -> ValidationResult:
    missing = find_missing_tests(repo_root / "src", repo_root / "tests")
    status = "fail" if STRICT and missing else "pass"
    return ValidationResult("tests", status, {"missing": missing})


def validate_gaps(repo_root: Path) -> ValidationResult:
    gaps = detect_gaps.discover_gaps(repo_root)
    return ValidationResult(
        "gaps", "fail" if gaps else "pass", {"gaps": [asdict(gap) for gap in gaps]}
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate production readiness")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root directory",
    )
    parser.add_argument("--json", action="store_true", help="Emit results as JSON")
    args = parser.parse_args()

    checks = [
        validate_configs,
        validate_gaps,
        validate_tests,
        validate_entropy,
        validate_coupling,
    ]

    results: List[ValidationResult] = [check(args.repo_root) for check in checks]

    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2))
        return

    for result in results:
        print(f"[{result.status.upper()}] {result.name}")
        if result.details:
            print(json.dumps(result.details, indent=2))


if __name__ == "__main__":
    main()
