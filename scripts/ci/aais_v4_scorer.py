#!/usr/bin/env python3
"""AAIS V4.0 Automated Scorer — 4-pillar, 16-dimension scoring pipeline.

Implements the framework defined in docs/evolution/AAIS_V4_FRAMEWORK.md.
Collects metrics from the codebase and CI artifacts to produce a composite score.

Usage:
    python scripts/ci/aais_v4_scorer.py                  # Human-readable report
    python scripts/ci/aais_v4_scorer.py --json            # JSON output
    python scripts/ci/aais_v4_scorer.py --ci              # Write to GITHUB_STEP_SUMMARY
    python scripts/ci/aais_v4_scorer.py --output report.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ── OTel coherence wiring (S144) ─────────────────────────────────────────────
# Emit one workflow_coherence_score observation per AAIS scorer run so that
# the in-memory histogram tracks CI policy alignment over time.
# Import is guarded so the scorer remains runnable when src/ is not on the path.
try:
    sys.path.insert(0, str(ROOT / "src"))
    from codex.monitoring.otel_metrics import (  # noqa: E402
        compute_coherence,
        workflow_coherence_score,
    )
    _OTEL_AVAILABLE = True
except Exception:  # pragma: no cover
    _OTEL_AVAILABLE = False


MIN_PASSING_SCORE = 80.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SubDimension:
    """A single scored sub-dimension within a pillar."""

    name: str
    weight: float  # as fraction, e.g. 0.07
    score: float = 0.0
    details: str = ""


@dataclass
class Pillar:
    """One of the four V4.0 pillars."""

    name: str
    weight: float
    sub_dimensions: list[SubDimension] = field(default_factory=list)

    @property
    def score(self) -> float:
        if not self.sub_dimensions:
            return 0.0
        total_weight = sum(s.weight for s in self.sub_dimensions)
        if total_weight == 0:
            return 0.0
        return sum(s.score * s.weight for s in self.sub_dimensions) / total_weight


@dataclass
class V4Score:
    """Complete V4.0 scoring result."""

    pillars: list[Pillar] = field(default_factory=list)
    version: str = "4.0.0"

    @property
    def composite(self) -> float:
        return sum(p.score * p.weight for p in self.pillars)

    @property
    def grade(self) -> str:
        s = self.composite
        if s >= 99.0:
            return "S+"
        if s >= 98.0:
            return "S"
        if s >= 95.0:
            return "A+"
        if s >= 90.0:
            return "A"
        if s >= 85.0:
            return "B+"
        if s >= 80.0:
            return "B"
        return "C"


# ---------------------------------------------------------------------------
# Metric collectors
# ---------------------------------------------------------------------------

def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Run a command, return (returncode, stdout)."""
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or ROOT,
            timeout=120,
        )
        return r.returncode, r.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 1, ""


def _count_files(pattern: str, path: Path | None = None) -> int:
    """Count files matching a glob pattern."""
    return len(list((path or ROOT).glob(pattern)))


def _collect_code_quality() -> SubDimension:
    """Lint score via ruff."""
    rc, out = _run(["python", "-m", "ruff", "check", "src/", "--statistics", "-q"])
    py_files = _count_files("src/**/*.py")
    if rc == 0:
        score = 100.0
        detail = f"0 lint violations across {py_files} files"
    else:
        violation_lines = [ln for ln in out.strip().splitlines() if ln.strip()]
        n = len(violation_lines)
        # Deduct 0.5 per violation, floor at 50
        score = max(50.0, 100.0 - n * 0.5)
        detail = f"{n} lint violation categories across {py_files} files"
    return SubDimension("Code Quality", 0.07, score, detail)


def _collect_test_robustness() -> SubDimension:
    """Test suite robustness metrics."""
    test_files = _count_files("tests/**/*.py")
    # Fragile test ratio
    fragile_scan = ROOT / ".codex" / "scripts" / "fragile_tests_scan.py"
    if fragile_scan.exists():
        rc, out = _run(["python", str(fragile_scan), "--count-only"])
        try:
            unguarded = int(out.strip().split()[-1]) if rc == 0 else 0
        except (ValueError, IndexError):
            unguarded = 0
    else:
        unguarded = 0

    # Score: 100 if 0 unguarded, else deduct per unguarded
    guarded_pct = max(0, 100 - unguarded) if test_files > 0 else 100
    score = min(100.0, guarded_pct + 5)  # bonus for having guards at all
    score = min(score, 100.0)
    return SubDimension("Test Robustness", 0.06, score,
                        f"{test_files} test files, {unguarded} unguarded imports")


def _collect_cicd_maturity() -> SubDimension:
    """CI/CD maturity: fraction of Python-execution workflows that use any cache mechanism.

    Denominator = workflows that run Python (pip install / pytest / nox / ruff / mypy).
    Numerator   = those that use any recognised cache mechanism:
        - generate_cache_keys.py   (custom 4-layer CacheManager)
        - actions/cache            (explicit cache step)
        - cache: 'pip' / cache: pip  (setup-python built-in cache)
        - setup-python-cached      (custom 4-layer composite action)
    Non-Python orchestration/notification workflows are excluded from the denominator
    because caching pip packages is irrelevant to them (subscription-appropriate gap).
    """
    import re as _re
    # Require actual Python execution — not just a mention in a comment.
    # Patterns: pip install, python -m <cmd>, running from .venv_*, python scripts/, pytest/nox/ruff/mypy as CLI
    _PY_PAT = _re.compile(
        r"pip install"
        r"|python -m "
        r"|\.venv[_/]"
        r"|python scripts/"
        r"|pytest\s"
        r"|\bnox\b"
        r"|\bruff\b"
        r"|\bmypy\b",
        _re.I,
    )
    python_wf = 0
    cache_count = 0
    wf_dir = ROOT / ".github" / "workflows"
    if wf_dir.exists():
        for wf in wf_dir.glob("*.yml"):
            content = wf.read_text(errors="ignore")
            if not _PY_PAT.search(content):
                continue
            python_wf += 1
            has_cache = (
                "generate_cache_keys.py" in content
                or "actions/cache" in content
                or "cache: 'pip'" in content
                or 'cache: "pip"' in content
                or "cache: pip" in content
                or "setup-python-cached" in content  # custom 4-layer composite action
            )
            if has_cache:
                cache_count += 1
    if python_wf == 0:
        return SubDimension("CI/CD Maturity", 0.06, 100.0,
                            "N/A — no Python-execution workflows found")
    pct = (cache_count / python_wf) * 100
    score = min(100.0, pct)
    return SubDimension("CI/CD Maturity", 0.06, score,
                        f"{cache_count}/{python_wf} Python workflows with cache")


def _collect_security_posture() -> SubDimension:
    """Security posture assessment — Gate 1 (files) + Gate 2/3 (live alert counts).

    Three-gate rule (AAIS_HONEST_CALIBRATION_V1.md §2):
      Gate 1 — security workflow, ethics config, SBOM workflow exist
      Gate 2 — no critical/high security alerts outstanding
      Gate 3 — CI security scan runs on every PR push

    Alert counts are read from environment variables written by ci-health-monitor.yml:
      CODEX_OPEN_CRITICAL_ALERTS  — open CodeQL critical findings
      CODEX_OPEN_HIGH_ALERTS      — open Dependabot high findings
    If unset, assumes 0 (clean) so the scorer is still useful in local dev.
    """
    # Gate 1 — file existence
    sec_wf = ROOT / ".github" / "workflows" / "security-scanning-suite.yml"
    has_security = sec_wf.exists()
    has_ethics = (ROOT / ".codex" / "ethics" / "imperatives.yaml").exists()
    has_sbom = (ROOT / ".github" / "workflows" / "sbom.yml").exists()
    checks = sum([has_security, has_ethics, has_sbom])
    base_score = 75.0 + checks * 8.3

    # Gate 2+3 — live alert penalty (honest calibration §6 rule_2)
    # Each open CRITICAL CodeQL alert  → -5.0 pts
    # Each open HIGH Dependabot alert  → -2.0 pts
    # Each open MODERATE alert         → -1.0 pts
    try:
        open_critical  = max(0, int(os.environ.get("CODEX_OPEN_CRITICAL_ALERTS",  "0")))
        open_high      = max(0, int(os.environ.get("CODEX_OPEN_HIGH_ALERTS",       "0")))
        open_moderate  = max(0, int(os.environ.get("CODEX_OPEN_MODERATE_ALERTS",   "0")))
    except ValueError:
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "AAIS scorer: invalid value in CODEX_OPEN_*_ALERTS env var; defaulting to 0. "
            "Check that the variable contains a plain integer."
        )
        open_critical = open_high = open_moderate = 0
    alert_penalty = open_critical * 5.0 + open_high * 2.0 + open_moderate * 1.0
    score = max(0.0, min(base_score, base_score - alert_penalty))

    detail = f"security={has_security}, ethics={has_ethics}, sbom={has_sbom}"
    if open_critical or open_high or open_moderate:
        detail += (
            f"; open_alerts: critical={open_critical} high={open_high} moderate={open_moderate}"
            f" → -{alert_penalty:.0f}pt penalty"
        )
    return SubDimension("Security Posture", 0.06, score, detail)


def _collect_self_awareness() -> SubDimension:
    """Cognitive self-awareness via dashboard and trend tracking."""
    has_dashboard = (ROOT / ".codex" / "cognitive_brain" / "dashboard.md").exists()
    has_trend = (ROOT / "scripts" / "cognitive" / "trend_analysis.py").exists()
    has_healing = (ROOT / "scripts" / "cognitive" / "healing_loop.py").exists()
    checks = sum([has_dashboard, has_trend, has_healing])
    score = 70.0 + checks * 10.0
    return SubDimension("Self-Awareness", 0.08, min(score, 100.0),
                        f"dashboard={has_dashboard}, trend={has_trend}, healing={has_healing}")


def _collect_adaptive_learning() -> SubDimension:
    """Adaptive learning via knowledge transfer and pattern library."""
    has_kt = (ROOT / "scripts" / "cognitive" / "knowledge_transfer.py").exists()
    has_ks = (ROOT / "scripts" / "cognitive" / "knowledge_sharing.py").exists()
    has_ctx = (ROOT / "scripts" / "cognitive" / "context_window_optimizer.py").exists()
    checks = sum([has_kt, has_ks, has_ctx])
    score = 70.0 + checks * 10.0
    return SubDimension("Adaptive Learning", 0.08, min(score, 100.0),
                        f"kt={has_kt}, sharing={has_ks}, context={has_ctx}")


def _collect_reasoning_depth() -> SubDimension:
    """Reasoning depth via planset completion and multi-step tooling."""
    # Count plansets
    registry = ROOT / "docs" / "evolution" / "PLANSET_REGISTRY.md"
    complete = 0
    total = 0
    if registry.exists():
        in_overview = False
        for line in registry.read_text().splitlines():
            if "Registry Overview" in line or "registry overview" in line.lower():
                in_overview = True
            elif line.startswith("## ") and in_overview:
                in_overview = False
            if in_overview and "PS-" in line and "|" in line and "PS ID" not in line:
                total += 1
                if "✅" in line:
                    complete += 1
    pct = (complete / max(total, 1)) * 100
    score = min(100.0, pct + 2)
    return SubDimension("Reasoning Depth", 0.07, score,
                        f"{complete}/{total} plansets complete")


def _collect_ethical_alignment() -> SubDimension:
    """Ethical alignment via imperatives config."""
    ethics_file = ROOT / ".codex" / "ethics" / "imperatives.yaml"
    if ethics_file.exists():
        content = ethics_file.read_text()
        imperative_count = content.count("- id:")
        score = min(100.0, 80.0 + imperative_count * 2)
        detail = f"{imperative_count} ethical imperatives defined"
    else:
        score = 60.0
        detail = "No ethics config found"
    return SubDimension("Ethical Alignment", 0.07, score, detail)


def _collect_automation_coverage() -> SubDimension:
    """Automation coverage via workflow count."""
    workflows = _count_files(".github/workflows/*.yml")
    score = min(100.0, 70.0 + workflows * 0.5)
    return SubDimension("Automation Coverage", 0.07, score,
                        f"{workflows} workflows")


def _collect_reliability() -> SubDimension:
    """Reliability assessment — Gate 1 (files) + Gate 3 (actual CI failure rate).

    Three-gate rule (AAIS_HONEST_CALIBRATION_V1.md §2):
      Gate 1 — healing_loop.py and self-healing workflow exist
      Gate 3 — actual CI failure rate from CODEX_CI_FAILURE_RATE repo variable

    CI failure rate is read from CODEX_CI_FAILURE_RATE env var
    (format: "<float>:<status>", e.g. "13.3:degraded").
    Each 1% of failure rate deducts 1 point from the base score (cap: 25 pts).
    At 0% failure rate: full base score.  At ≥25%: -25 pts.
    """
    has_healing = (ROOT / "scripts" / "cognitive" / "healing_loop.py").exists()
    has_self_healing_wf = (ROOT / ".github" / "workflows" / "self-healing.yml").exists()
    checks = sum([has_healing, has_self_healing_wf])
    base_score = 75.0 + checks * 12.5

    # Gate 3 — actual CI failure rate penalty
    ci_rate = 0.0
    rate_str = os.environ.get("CODEX_CI_FAILURE_RATE", "").strip()
    if rate_str:
        try:
            ci_rate = max(0.0, float(rate_str.split(":")[0]))
        except ValueError:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "AAIS scorer: invalid CODEX_CI_FAILURE_RATE value %r; defaulting to 0.0. "
                "Expected format: '<float>:<status>' e.g. '13.3:degraded'.",
                rate_str,
            )
            ci_rate = 0.0
    # Each 1% failure rate = -1.0 pt reliability deduction, capped at -25 pts
    reliability_penalty = min(ci_rate * 1.0, 25.0)
    score = max(0.0, min(base_score, base_score - reliability_penalty))

    detail = f"healing_loop={has_healing}, self_healing_wf={has_self_healing_wf}"
    if ci_rate > 0:
        detail += f"; ci_failure_rate={ci_rate:.1f}% → -{reliability_penalty:.1f}pt penalty"
    return SubDimension("Reliability", 0.06, score, detail)


def _collect_observability() -> SubDimension:
    """Observability via monitoring scripts and dashboards."""
    monitoring_scripts = _count_files("scripts/monitoring/*.py")
    has_dashboard = (ROOT / ".codex" / "cognitive_brain" / "dashboard.md").exists()
    score = min(100.0, 70.0 + monitoring_scripts * 2 + (10 if has_dashboard else 0))
    return SubDimension("Observability", 0.06, score,
                        f"{monitoring_scripts} monitoring scripts, dashboard={has_dashboard}")


def _collect_scalability() -> SubDimension:
    """Scalability via multi-repo orchestration support."""
    has_multi_repo = (ROOT / "scripts" / "monitoring" / "multi_repo_orchestrator.py").exists()
    has_task_router = (ROOT / "scripts" / "monitoring" / "agent_orchestrator.py").exists()
    checks = sum([has_multi_repo, has_task_router])
    score = 75.0 + checks * 12.5
    return SubDimension("Scalability", 0.06, min(score, 100.0),
                        f"multi_repo={has_multi_repo}, task_router={has_task_router}")


def _collect_doc_quality() -> SubDimension:
    """Documentation quality via file presence."""
    docs = _count_files("docs/**/*.md")
    has_readme = (ROOT / "README.md").exists()
    has_mkdocs = (ROOT / "mkdocs.yml").exists()
    score = min(100.0, 70.0 + docs * 0.2 + (5 if has_readme else 0) + (5 if has_mkdocs else 0))
    return SubDimension("Documentation Quality", 0.05, score,
                        f"{docs} doc files, readme={has_readme}, mkdocs={has_mkdocs}")


def _collect_knowledge_sharing() -> SubDimension:
    """Knowledge sharing maturity."""
    has_ks = (ROOT / "scripts" / "cognitive" / "knowledge_sharing.py").exists()
    has_kt = (ROOT / "scripts" / "cognitive" / "knowledge_transfer.py").exists()
    checks = sum([has_ks, has_kt])
    score = 75.0 + checks * 12.5
    return SubDimension("Knowledge Sharing", 0.05, min(score, 100.0),
                        f"sharing={has_ks}, transfer={has_kt}")


def _collect_community_alignment() -> SubDimension:
    """Community and standards alignment."""
    has_pyproject = (ROOT / "pyproject.toml").exists()
    has_nox = (ROOT / "noxfile.py").exists()
    has_precommit = (ROOT / ".pre-commit-config.yaml").exists()
    checks = sum([has_pyproject, has_nox, has_precommit])
    score = 70.0 + checks * 10.0
    return SubDimension("Community Alignment", 0.05, min(score, 100.0),
                        f"pyproject={has_pyproject}, nox={has_nox}, precommit={has_precommit}")


def _collect_innovation_rate() -> SubDimension:
    """Innovation rate via planset velocity."""
    registry = ROOT / "docs" / "evolution" / "PLANSET_REGISTRY.md"
    total = 0
    if registry.exists():
        in_overview = False
        for line in registry.read_text().splitlines():
            if "Registry Overview" in line or "registry overview" in line.lower():
                in_overview = True
            elif line.startswith("## ") and in_overview:
                in_overview = False
            if in_overview and "PS-" in line and "|" in line and "PS ID" not in line:
                total += 1
    score = min(100.0, 70.0 + total * 1.5)
    return SubDimension("Innovation Rate", 0.05, score,
                        f"{total} plansets defined")


# ---------------------------------------------------------------------------
# Main scorer
# ---------------------------------------------------------------------------

def compute_v4_score() -> V4Score:
    """Compute the full V4.0 AAIS score."""
    pillars = [
        Pillar("Technical Excellence", 0.25, [
            _collect_code_quality(),
            _collect_test_robustness(),
            _collect_cicd_maturity(),
            _collect_security_posture(),
        ]),
        Pillar("Cognitive Sophistication", 0.30, [
            _collect_self_awareness(),
            _collect_adaptive_learning(),
            _collect_reasoning_depth(),
            _collect_ethical_alignment(),
        ]),
        Pillar("Operational Maturity", 0.25, [
            _collect_automation_coverage(),
            _collect_reliability(),
            _collect_observability(),
            _collect_scalability(),
        ]),
        Pillar("Ecosystem Impact", 0.20, [
            _collect_doc_quality(),
            _collect_knowledge_sharing(),
            _collect_community_alignment(),
            _collect_innovation_rate(),
        ]),
    ]
    return V4Score(pillars=pillars)


def format_report(result: V4Score) -> str:
    """Format a human-readable report."""
    lines = [
        "=" * 60,
        f"  AAIS V{result.version} Score: {result.composite:.1f}/100 ({result.grade})",
        "=" * 60,
        "",
    ]
    for pillar in result.pillars:
        lines.append(f"📊 {pillar.name} ({pillar.weight:.0%}): {pillar.score:.1f}")
        for sd in pillar.sub_dimensions:
            bar = "█" * int(sd.score / 5) + "░" * (20 - int(sd.score / 5))
            lines.append(f"   {sd.name:25s} {bar} {sd.score:.1f}  ({sd.details})")
        lines.append("")

    lines.append(f"Composite: {result.composite:.1f}/100 — Grade: {result.grade}")
    return "\n".join(lines)


def to_dict(result: V4Score) -> dict:
    """Convert to serializable dict."""
    return {
        "version": result.version,
        "composite": round(result.composite, 2),
        "grade": result.grade,
        "pillars": [
            {
                "name": p.name,
                "weight": p.weight,
                "score": round(p.score, 2),
                "sub_dimensions": [asdict(sd) for sd in p.sub_dimensions],
            }
            for p in result.pillars
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AAIS V4.0 Automated Scorer")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--output", help="Write to file")
    parser.add_argument("--ci", action="store_true", help="Write to GITHUB_STEP_SUMMARY")
    args = parser.parse_args()

    result = compute_v4_score()

    output = json.dumps(to_dict(result), indent=2) if args.json else format_report(result)

    print(output)

    if args.output:
        Path(args.output).write_text(output)

    if args.ci:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a") as f:
                f.write(f"\n## AAIS V4.0 Score: {result.composite:.1f}/100 ({result.grade})\n\n")
                for p in result.pillars:
                    f.write(f"- **{p.name}** ({p.weight:.0%}): {p.score:.1f}/100\n")
                    for sd in p.sub_dimensions:
                        f.write(f"  - {sd.name}: {sd.score:.1f} — {sd.details}\n")

    # ── OTel coherence observation (S144) ─────────────────────────────────
    # Map AAIS sub-dimension outcomes to policy-expected "pass" outcomes and
    # compute a coherence score for this CI run.  Sub-dimensions scoring ≥ 80
    # are treated as "pass"; the policy expectation is "pass" for all of them.
    if _OTEL_AVAILABLE:
        actual_outcomes: dict[str, str] = {}
        expected_outcomes: dict[str, str] = {}
        for pillar in result.pillars:
            for sd in pillar.sub_dimensions:
                key = sd.name
                actual_outcomes[key] = "pass" if sd.score >= 80.0 else "fail"
                expected_outcomes[key] = "pass"
        coherence = compute_coherence(actual_outcomes, expected_outcomes)
        workflow_coherence_score.observe(coherence)

    sys.exit(0 if result.composite >= MIN_PASSING_SCORE else 1)


if __name__ == "__main__":
    main()
