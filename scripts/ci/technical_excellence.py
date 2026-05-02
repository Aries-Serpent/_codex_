#!/usr/bin/env python3
"""Technical Excellence Pillar Assessment (PS-20b).

Measures the 4 sub-dimensions of the Technical Excellence pillar:
1. Code Quality — lint compliance via ruff
2. Test Robustness — fragile test coverage and guard status
3. CI/CD Maturity — workflow count, CacheManager integration
4. Security Posture — scanning, ethics, SBOM presence

Usage:
    python scripts/ci/technical_excellence.py           # Human report
    python scripts/ci/technical_excellence.py --json    # JSON output
    python scripts/ci/technical_excellence.py --ci      # GITHUB_STEP_SUMMARY
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class DimensionResult:
    """Result for a single sub-dimension."""

    name: str
    score: float
    max_score: float
    details: str


@dataclass
class PillarReport:
    """Full pillar assessment report."""

    pillar: str
    weight: float
    dimensions: list[DimensionResult]

    @property
    def score(self) -> float:
        if not self.dimensions:
            return 0.0
        return sum(d.score for d in self.dimensions) / sum(
            d.max_score for d in self.dimensions
        ) * 100

    def to_dict(self) -> dict:
        return {
            "pillar": self.pillar,
            "weight": self.weight,
            "score": round(self.score, 1),
            "dimensions": [asdict(d) for d in self.dimensions],
        }


def _run(cmd: list[str]) -> tuple[int, str]:
    """Run command safely."""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, cwd=ROOT, timeout=120
        )
        return r.returncode, r.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 1, ""


def assess_code_quality() -> DimensionResult:
    """Lint compliance via ruff."""
    rc, out = _run(["python", "-m", "ruff", "check", "src/", "--statistics", "-q"])
    py_files = len(list(ROOT.glob("src/**/*.py")))
    if rc == 0:
        score = 25.0
        detail = f"0 lint violations across {py_files} files"
    else:
        violations = len([ln for ln in out.strip().splitlines() if ln.strip()])
        score = max(12.5, 25.0 - violations * 0.5)
        detail = f"{violations} violation categories across {py_files} files"
    return DimensionResult("Code Quality", score, 25.0, detail)


def assess_test_robustness() -> DimensionResult:
    """Test suite robustness — guards, coverage, file count."""
    test_files = len(list(ROOT.glob("tests/**/*.py")))
    # Check fragile test status
    scan = ROOT / ".codex" / "scripts" / "fragile_tests_scan.py"
    unguarded = 0
    if scan.exists():
        rc, out = _run(["python", str(scan), "--count-only"])
        try:
            unguarded = int(out.strip().split()[-1]) if rc == 0 else 0
        except (ValueError, IndexError):
            unguarded = 0
    guard_pct = ((test_files - unguarded) / max(test_files, 1)) * 100
    score = min(25.0, guard_pct / 100 * 25)
    return DimensionResult(
        "Test Robustness", score, 25.0,
        f"{test_files} test files, {unguarded} unguarded, {guard_pct}% guarded"
    )


def assess_cicd_maturity() -> DimensionResult:
    """CI/CD maturity — workflows + CacheManager."""
    wf_dir = ROOT / ".github" / "workflows"
    workflows = len(list(wf_dir.glob("*.yml"))) if wf_dir.exists() else 0
    cache_count = 0
    if wf_dir.exists():
        for wf in wf_dir.glob("*.yml"):
            if "generate_cache_keys.py" in wf.read_text(errors="ignore"):
                cache_count += 1
    pct = (cache_count / max(workflows, 1)) * 100
    score = min(25.0, pct / 100 * 25)
    return DimensionResult(
        "CI/CD Maturity", score, 25.0,
        f"{cache_count}/{workflows} workflows with CacheManager ({pct:.0f}%)"
    )


def assess_security_posture() -> DimensionResult:
    """Security posture — scanning, ethics, SBOM."""
    checks = {
        "security_workflow": (ROOT / ".github/workflows/security-scanning-suite.yml").exists(),
        "ethics_config": (ROOT / ".codex/ethics/imperatives.yaml").exists(),
        "sbom_workflow": (ROOT / ".github/workflows/sbom.yml").exists(),
        "codeql": (ROOT / ".github/workflows/codeql-analysis.yml").exists(),
    }
    passed = sum(checks.values())
    score = passed / len(checks) * 25
    detail = ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in checks.items())
    return DimensionResult("Security Posture", score, 25.0, detail)


def run_assessment() -> PillarReport:
    """Run full Technical Excellence assessment."""
    return PillarReport(
        pillar="Technical Excellence",
        weight=0.25,
        dimensions=[
            assess_code_quality(),
            assess_test_robustness(),
            assess_cicd_maturity(),
            assess_security_posture(),
        ],
    )


def format_report(report: PillarReport) -> str:
    """Format human-readable report."""
    lines = [
        f"═══ {report.pillar} Pillar Assessment ═══",
        f"Weight: {report.weight * 100:.0f}%",
        f"Score: {report.score:.1f}/100",
        "",
    ]
    for d in report.dimensions:
        bar = "█" * int(d.score / d.max_score * 20) + "░" * (20 - int(d.score / d.max_score * 20))
        lines.append(f"  {d.name}: {d.score:.1f}/{d.max_score:.1f} {bar}")
        lines.append(f"    {d.details}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Technical Excellence Assessment")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--output", type=str, help="Write to file")
    parser.add_argument("--ci", action="store_true", help="Write GITHUB_STEP_SUMMARY")
    args = parser.parse_args()

    report = run_assessment()

    out = json.dumps(report.to_dict(), indent=2) if args.json else format_report(report)

    if args.output:
        Path(args.output).write_text(out)

    if args.ci:
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a") as f:
                f.write(f"\n## Technical Excellence: {report.score:.1f}/100\n")

    print(out)


if __name__ == "__main__":
    main()
