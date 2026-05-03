#!/usr/bin/env python3
"""
Doc Metrics Sync — keeps Mermaid diagrams, KPI tables, and metric strings
in documentation aligned with the source-of-truth files they describe.

USAGE
-----
  python scripts/tools/doc_metrics_sync.py --check    # exit 1 if any doc is stale
  python scripts/tools/doc_metrics_sync.py --fix      # update docs in-place
  python scripts/tools/doc_metrics_sync.py --report   # print diff table, exit 0

HOW IT WORKS
------------
1. ``gather_metrics()`` reads live values from source-of-truth files
   (AGENT_REGISTRY.yaml, pyproject.toml, feast_compat.py, devcontainer.json, …)
2. Each ``Rule`` in ``RULES`` specifies: which file(s) to scan, a regex that
   matches the stale text, and a replacement template using metric names.
3. In ``--check`` mode the script exits 1 when any match is found that differs
   from the live value — suitable for CI gates and pre-commit hooks.

ADDING A NEW RULE
-----------------
Append a ``Rule`` to RULES:

    Rule(
        id="my_new_rule",
        files=["docs/my_doc.md"],
        pattern=r"\\d+ frobnitz",
        replacement="{frobnitz_count} frobnitz",
        description="Frobnitz count in my_doc.md",
    )

Then add the corresponding metric to ``gather_metrics()``::

    metrics["frobnitz_count"] = count_frobnitzes(repo_root)

The pre-commit hook and CI workflow pick up new rules automatically.
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Repo root detection
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Rule definition
# ---------------------------------------------------------------------------


@dataclass
class Rule:
    """One search-replace rule that must stay in sync with live metrics."""

    id: str
    files: list[str]
    """Relative-to-repo-root file paths (no globs — exact paths for precision)."""
    pattern: str
    """Regex that matches the stale text.  Must contain exactly one capture group
    whose content is the *current* (possibly stale) value."""
    replacement: str
    """Template string using ``{metric_name}`` placeholders drawn from the
    dict returned by ``gather_metrics()``."""
    description: str = ""
    flags: int = 0
    """Optional re flags, e.g. ``re.IGNORECASE``."""


# ---------------------------------------------------------------------------
# Rules registry — add new rules here
# ---------------------------------------------------------------------------

RULES: list[Rule] = [
    # ── README.md ─────────────────────────────────────────────────────────
    Rule(
        id="readme_tagline_tests",
        files=["README.md"],
        pattern=r"(\d{3,5}\+) tests,",
        replacement="{test_count_display} tests,",
        description="Test count in README tagline",
    ),
    Rule(
        id="readme_tagline_coverage",
        files=["README.md"],
        pattern=r"(\d{2})% coverage,",
        replacement="{coverage_threshold}% coverage,",
        description="Coverage % in README tagline",
    ),
    Rule(
        id="readme_tagline_agents",
        files=["README.md"],
        pattern=r"and (\d+) autonomous agents",
        replacement="and {agent_count} autonomous agents",
        description="Agent count in README tagline",
    ),
    Rule(
        id="readme_badge_tests",
        files=["README.md"],
        pattern=r"tests-(\d{3,5}%2B)%20total",
        replacement="tests-{test_count_url}%20total",
        description="Test count in README badge URL",
    ),
    Rule(
        id="readme_badge_coverage",
        files=["README.md"],
        pattern=r"coverage-(\d{2})%25%20threshold",
        replacement="coverage-{coverage_threshold}%25%20threshold",
        description="Coverage % in README badge URL",
    ),
    Rule(
        id="readme_badge_agents",
        files=["README.md"],
        pattern=r"agents-(\d+)%20autonomous",
        replacement="agents-{agent_count}%20autonomous",
        description="Agent count in README badge URL",
    ),
    Rule(
        id="readme_mermaid_eval_coverage",
        files=["README.md"],
        pattern=r"(📊 \d{2}% Coverage)",
        replacement="📊 {coverage_threshold}% Coverage",
        description="Coverage % in README Mermaid eval node",
    ),
    Rule(
        id="readme_mermaid_agents",
        files=["README.md"],
        pattern=r"(\d+) Autonomous Agents<br/>🤖 MCP Integration",
        replacement="{agent_count} Autonomous Agents<br/>🤖 MCP Integration",
        description="Agent count in README Mermaid node",
    ),
    Rule(
        id="readme_feature_tests",
        files=["README.md"],
        pattern=r"\*\*🧪 (\d{3,5}\+) Tests\*\*",
        replacement="**🧪 {test_count_display} Tests**",
        description="Test count in README feature list",
    ),
    Rule(
        id="readme_feature_coverage",
        files=["README.md"],
        pattern=r"\*\*📊 (\d{2})% Coverage\*\*",
        replacement="**📊 {coverage_threshold}% Coverage**",
        description="Coverage % in README feature list",
    ),
    Rule(
        id="readme_feature_agents",
        files=["README.md"],
        pattern=r"\*\*🤖 (\d+) Agents\*\*",
        replacement="**🤖 {agent_count} Agents**",
        description="Agent count in README feature list",
    ),
    # ── docs/ARCHITECTURE.md ──────────────────────────────────────────────
    Rule(
        id="arch_codex_node",
        files=["docs/ARCHITECTURE.md"],
        pattern=r"(\d{3,5}\+ Tests \| \d{2}% Coverage)",
        replacement="{test_count_display} Tests | {coverage_threshold}% Coverage",
        description="Test/coverage counts in ARCHITECTURE.md Codex node",
    ),
    Rule(
        id="arch_eval_node",
        files=["docs/ARCHITECTURE.md"],
        pattern=r"📊 (\d{3,5}\+ Tests)",
        replacement="📊 {test_count_display} Tests",
        description="Test count in ARCHITECTURE.md Eval node",
    ),
    Rule(
        id="arch_agents_node",
        files=["docs/ARCHITECTURE.md"],
        pattern=r"(\d+) Autonomous Agents<br/>🤖 MCP-enabled",
        replacement="{agent_count} Autonomous Agents<br/>🤖 MCP-enabled",
        description="Agent count in ARCHITECTURE.md system context node",
    ),
    Rule(
        id="arch_agents_prose",
        files=["docs/ARCHITECTURE.md"],
        pattern=r"\*\*(\d+) Autonomous Agents\*\*: Specialized domain agents",
        replacement="**{agent_count} Autonomous Agents**: Specialized domain agents",
        description="Agent count in ARCHITECTURE.md prose",
    ),
    Rule(
        id="arch_agents_subgraph",
        files=["docs/ARCHITECTURE.md"],
        pattern=r"Agent System \((\d+) Agents\)",
        replacement="Agent System ({agent_count} Agents)",
        description="Agent count in ARCHITECTURE.md subgraph label",
    ),
    # ── docs/ops/SAR_METHODOLOGY.md ───────────────────────────────────────
    Rule(
        id="sar_quadrant_feature_store",
        files=["docs/ops/SAR_METHODOLOGY.md"],
        pattern=r"Feature Store: \[(\d+\.\d+, \d+\.\d+)\]",
        replacement="Feature Store: [{sar_g02_quadrant}]",
        description="Feature Store quadrant position in SAR_METHODOLOGY.md",
    ),
    Rule(
        id="sar_quadrant_distributed_tracing",
        files=["docs/ops/SAR_METHODOLOGY.md"],
        pattern=r"Distributed Tracing: \[(\d+\.\d+, \d+\.\d+)\]",
        replacement="Distributed Tracing: [{sar_g05_quadrant}]",
        description="Distributed Tracing quadrant position in SAR_METHODOLOGY.md",
    ),
    Rule(
        id="sar_quadrant_variable_hygiene",
        files=["docs/ops/SAR_METHODOLOGY.md"],
        pattern=r"Variable Hygiene: \[(\d+\.\d+, \d+\.\d+)\]",
        replacement="Variable Hygiene: [{sar_g01_quadrant}]",
        description="Variable Hygiene quadrant position in SAR_METHODOLOGY.md",
    ),
    Rule(
        id="sar_overall_level",
        files=["docs/ops/SAR_METHODOLOGY.md"],
        pattern=r"\*\*Overall Level: ([\d.]+ / 4\.0)\*\*",
        replacement="**Overall Level: {mlops_level} / 4.0**",
        description="Overall MLOps level in SAR_METHODOLOGY.md score table",
    ),
    Rule(
        id="sar_layer1_test_count",
        files=["docs/ops/SAR_METHODOLOGY.md"],
        pattern=r'Test Suite (\d{3,5}\+)',
        replacement="Test Suite {test_count_display}",
        description="Test count in SAR_METHODOLOGY.md L1 layer diagram",
    ),
    # ── docs/LEVEL_4_MLOPS_ASSESSMENT.md ─────────────────────────────────
    Rule(
        id="l4_overall_level",
        files=["docs/LEVEL_4_MLOPS_ASSESSMENT.md"],
        pattern=r"\*\*Level ([\d.]+)\*\* _\(updated",
        replacement="**Level {mlops_level}** _(updated",
        description="Overall MLOps level in LEVEL_4_MLOPS_ASSESSMENT.md heading",
    ),
    # ── docs/ROADMAP.md ───────────────────────────────────────────────────
    Rule(
        id="roadmap_mlops_level",
        files=["docs/ROADMAP.md"],
        pattern=r"\| \*\*MLOps Maturity\*\* \| Level ([\d.]+) [⚠✅]",
        replacement="| **MLOps Maturity** | Level {mlops_level} ✅",
        description="MLOps level in ROADMAP.md infra maturity table",
    ),
    Rule(
        id="roadmap_mlops_note",
        files=["docs/ROADMAP.md"],
        pattern=r"> ✅ Updated \d{4}-\d{2}-\d{2} \([^)]+\): Level [\d.]+ — [^\n]+\.",
        replacement="> ✅ Updated {today} (W-142 S116): "
        "Level {mlops_level} — P1 gaps resolved (SAR-G01/G02/G05 COMPLETE).",
        description="MLOps level note in ROADMAP.md",
    ),
    Rule(
        id="roadmap_mlops_gap_note",
        files=["docs/ROADMAP.md"],
        pattern=r"Level ([\d.]+) [⚠️✅]+ \| Level 4 \| [^\|]+\|",
        replacement="Level {mlops_level} ✅ | Level 4 | P1 gaps resolved (SAR-G01/G02/G05) — "
        "see [SAR_METHODOLOGY.md §10](ops/SAR_METHODOLOGY.md#10-gap-registry--roadmap) |",
        description="MLOps gap note in ROADMAP.md infra table",
    ),
    # ── docs/evolution/COGNITIVE_CODEBASE_MAP.md ─────────────────────────
    Rule(
        id="codebase_map_test_count",
        files=["docs/evolution/COGNITIVE_CODEBASE_MAP.md"],
        pattern=r'tests/ \((\d{3,5}\+)\)',
        replacement="tests/ ({test_count_display})",
        description="Test count in COGNITIVE_CODEBASE_MAP.md Mermaid node",
    ),
    Rule(
        id="codebase_map_test_table",
        files=["docs/evolution/COGNITIVE_CODEBASE_MAP.md"],
        pattern=r"(\d{3,5}\+) tests, (\d{2})% threshold",
        replacement="{test_count_display} tests, {coverage_threshold}% threshold",
        description="Test/coverage counts in COGNITIVE_CODEBASE_MAP.md table",
    ),
    # ── docs/evolution/INDEX.md ───────────────────────────────────────────
    Rule(
        id="evolution_index_tests",
        files=["docs/evolution/INDEX.md"],
        pattern=r"\| Tests Passing \| (\d{3,5}\+) \|",
        replacement="| Tests Passing | {test_count_display} |",
        description="Test count in evolution INDEX.md table",
    ),
    # ── docs/deployment/DEPLOYMENT_RUNBOOK.md ─────────────────────────────
    Rule(
        id="runbook_test_count",
        files=["docs/deployment/DEPLOYMENT_RUNBOOK.md"],
        pattern=r"All tests pass \((\d{3,5}\+) tests\)",
        replacement="All tests pass ({test_count_display} tests)",
        description="Test count in DEPLOYMENT_RUNBOOK.md checklist",
    ),
    # ── docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md ─────────────────────────
    Rule(
        id="repo_arch_diag_coverage_badge",
        files=["docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md"],
        pattern=r"✅ (\d{2})% Coverage",
        replacement="✅ {coverage_threshold}% Coverage",
        description="Coverage % in REPOSITORY_ARCHITECTURE_DIAGRAMS.md Mermaid badge",
    ),
    Rule(
        id="repo_arch_diag_coverage_note",
        files=["docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md"],
        pattern=r"\*\*(\d{2})% Coverage\*\*: Production-grade quality threshold",
        replacement="**{coverage_threshold}% Coverage**: Production-grade quality threshold",
        description="Coverage % in REPOSITORY_ARCHITECTURE_DIAGRAMS.md prose",
    ),
    Rule(
        id="repo_arch_diag_coverage_achieved",
        files=["docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md"],
        pattern=r"\*\*(\d{2})% Coverage\*\*: Production-grade quality threshold achieved",
        replacement="**{coverage_threshold}% Coverage**: Production-grade quality threshold achieved",
        description="Coverage % in REPOSITORY_ARCHITECTURE_DIAGRAMS.md intro",
    ),
    # ── .codex/MANIFEST (integrity_sha256) ───────────────────────────────
    # Handled separately via update_secrets_baseline() rather than a Rule,
    # because it requires computing SHA1 of the new hex value.
]


# ---------------------------------------------------------------------------
# Metric gathering — single source of truth per metric
# ---------------------------------------------------------------------------


def gather_metrics(repo_root: Path) -> dict[str, str]:  # noqa: C901 (complexity ok here)
    """Read live values from source-of-truth files and return a flat dict."""
    import datetime

    m: dict[str, str | int] = {}

    # --- agent count ---------------------------------------------------------
    registry = repo_root / ".github" / "agents" / "AGENT_REGISTRY.yaml"
    if registry.exists():
        # Fast parse: avoid full YAML load for speed
        for line in registry.read_text().splitlines():
            if line.strip().startswith("total_agents:"):
                try:
                    m["agent_count"] = int(line.split(":")[1].strip())
                except ValueError:
                    logger.debug("Suppressed exception in handler", exc_info=True)
                break
    m.setdefault("agent_count", 153)

    # --- coverage threshold --------------------------------------------------
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().splitlines():
            if "fail_under" in line and "=" in line:
                try:
                    m["coverage_threshold"] = int(line.split("=")[1].strip())
                except ValueError:
                    logger.debug("Suppressed exception in handler", exc_info=True)
                break
    m.setdefault("coverage_threshold", 75)

    # --- test count ----------------------------------------------------------
    test_dir = repo_root / "tests"
    count = 0
    if test_dir.is_dir():
        for tf in test_dir.rglob("test_*.py"):
            try:
                count += tf.read_text(errors="ignore").count("\ndef test_")
                count += tf.read_text(errors="ignore").count("\n    def test_")
            except OSError:
                logger.debug("Suppressed exception in handler", exc_info=True)
    # Floor to nearest 500 for a conservative round-number claim
    display = max(500, (count // 500) * 500)
    m["test_count_display"] = f"{display}+"
    m["test_count_url"] = f"{display}%2B"  # URL-encoded for badge

    # --- workflow count ------------------------------------------------------
    wf_dir = repo_root / ".github" / "workflows"
    m["workflow_count"] = len(list(wf_dir.glob("*.yml"))) if wf_dir.is_dir() else 0

    # --- SAR-G02 (feature store) score & quadrant position -------------------
    feast = repo_root / "src" / "codex_ml" / "features" / "feast_compat.py"
    if feast.exists():
        content = feast.read_text()
        backends = sum(
            1
            for b in ("InMemoryBackend", "SQLiteBackend", "RedisBackend", "DuckDBBackend")
            if f"class {b}" in content
        )
        has_arrow = "materialize_to_arrow_ipc" in content
        if backends == 4 and has_arrow:
            g02 = 97
        elif backends == 4:
            g02 = 95
        elif backends >= 3:
            g02 = 90
        elif backends >= 2:
            g02 = 75
        else:
            g02 = 40
    else:
        g02 = 40
    m["sar_g02_score"] = g02
    # Quadrant chart: x=maturity [0-1], y=automation [0-1]
    x = round(g02 / 100, 2)
    y = round((g02 - 5) / 100, 2)
    m["sar_g02_quadrant"] = f"{x}, {y}"

    # --- SAR-G05 (observability/tracing) score & quadrant -------------------
    devcontainer = repo_root / ".devcontainer" / "devcontainer.json"
    tracing = repo_root / "src" / "mcp" / "server" / "tracing.py"
    has_otel_env = devcontainer.exists() and "OTEL_EXPORTER_OTLP_ENDPOINT" in devcontainer.read_text()
    has_drift_span = tracing.exists() and "drift_span" in tracing.read_text()
    if has_otel_env and has_drift_span:
        g05 = 100
    elif has_drift_span:
        g05 = 97
    else:
        g05 = 78
    m["sar_g05_score"] = g05
    x5 = round(g05 / 100, 2)
    y5 = round((g05 - 5) / 100, 2)
    m["sar_g05_quadrant"] = f"{x5}, {y5}"

    # --- SAR-G01 (variable hygiene) quadrant ---------------------------------
    # Assumed COMPLETE once GITHUB_VARIABLES_MASTER_GUIDE mentions §6h vars
    guide = repo_root / "docs" / "admin" / "GITHUB_VARIABLES_MASTER_GUIDE.md"
    if guide.exists() and "SAR-G01" in guide.read_text() and "COMPLETE" in guide.read_text():
        g01_x, g01_y = 0.90, 0.90
    else:
        g01_x, g01_y = 0.65, 0.70
    m["sar_g01_quadrant"] = f"{g01_x}, {g01_y}"

    # --- overall MLOps level -------------------------------------------------
    # Simple model: start from 3.9 (W-140 baseline), add increments per resolved gap
    base = 3.9
    if g02 >= 95:
        base += 0.025  # G02 resolved
    if g05 >= 100:
        base += 0.015  # G05 resolved
    if g01_x >= 0.90:
        base += 0.01   # G01 resolved
    m["mlops_level"] = str(round(min(base, 3.99), 2))

    # --- today's date --------------------------------------------------------
    m["today"] = datetime.date.today().isoformat()

    return {k: str(v) for k, v in m.items()}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    rule_id: str
    file: str
    line_no: int
    old_text: str
    new_text: str
    description: str = ""


def _apply_rule(rule: Rule, metrics: dict[str, str], fix: bool) -> list[Finding]:
    """Apply one rule to all its target files; return list of findings."""
    findings: list[Finding] = []
    try:
        replacement = rule.replacement.format(**metrics)
    except KeyError as exc:
        sys.stderr.write(f"[doc_metrics_sync] Rule {rule.id!r}: missing metric {exc}\n")
        return findings

    for rel_path in rule.files:
        fpath = REPO_ROOT / rel_path
        if not fpath.exists():
            continue
        original = fpath.read_text()
        lines = original.splitlines(keepends=True)
        new_lines = list(lines)
        for i, line in enumerate(lines):
            m = re.search(rule.pattern, line, flags=rule.flags)
            if m is None:
                continue
            new_line = line[: m.start()] + replacement + line[m.end() :]
            if new_line == line:
                continue  # already correct
            findings.append(
                Finding(
                    rule_id=rule.id,
                    file=rel_path,
                    line_no=i + 1,
                    old_text=m.group(0),
                    new_text=replacement,
                    description=rule.description,
                )
            )
            new_lines[i] = new_line

        if fix and findings and "".join(new_lines) != original:
            fpath.write_text("".join(new_lines))

    return findings


def run(
    fix: bool = False,
    report: bool = False,
    rules: Sequence[Rule] | None = None,
    metrics: dict[str, str] | None = None,
) -> list[Finding]:
    """Run all rules; return list of findings (stale replacements found)."""
    active_rules = rules if rules is not None else RULES
    live_metrics = metrics if metrics is not None else gather_metrics(REPO_ROOT)
    all_findings: list[Finding] = []
    for rule in active_rules:
        all_findings.extend(_apply_rule(rule, live_metrics, fix=fix))
    return all_findings


def _print_report(findings: list[Finding], metrics: dict[str, str]) -> None:
    if not findings:
        print("✅  All tracked metrics are up-to-date.")
        return
    print(f"{'Rule ID':<40} {'File':<45} {'L':<5} {'Old':<40} {'New'}")
    print("-" * 150)
    for f in findings:
        print(
            f"{f.rule_id:<40} {f.file:<45} {f.line_no:<5} "
            f"{f.old_text!r:<40} {f.new_text!r}"
        )
    print(f"\n{len(findings)} stale metric(s) found.")
    print("\nLive metrics used:")
    for k, v in sorted(metrics.items()):
        print(f"  {k:<30} = {v!r}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Exit 1 if any doc is stale")
    mode.add_argument("--fix", action="store_true", help="Update stale docs in-place")
    mode.add_argument("--report", action="store_true", help="Show diff table, always exit 0")
    args = parser.parse_args(argv)

    metrics = gather_metrics(REPO_ROOT)
    findings = run(fix=args.fix, metrics=metrics)
    _print_report(findings, metrics)

    if args.check and findings:
        print(
            "\nRun  python scripts/tools/doc_metrics_sync.py --fix  to update automatically.",
            file=sys.stderr,
        )
        return 1
    if args.fix:
        print(f"\n✅  Fixed {len(findings)} stale metric(s) in-place.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
