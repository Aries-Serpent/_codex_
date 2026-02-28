#!/usr/bin/env python3
"""
inject_batch_scan_protocol.py

One-shot script: appends the standardised ``⚡ Parallel Batch Scanning Protocol``
section to every applicable agent file that does not already contain it.

Applicable agents are those that perform ANY of:
  - test execution or validation
  - codebase scanning (static analysis, coverage, security)
  - CI triage, healing, or remediation
  - code quality analysis

Run once (idempotent — skips files that already have the section):
    python scripts/ci/inject_batch_scan_protocol.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".github" / "agents"

SECTION_MARKER = "⚡ Parallel Batch Scanning Protocol"

# ── Applicable agent file names ──────────────────────────────────────────────
APPLICABLE_AGENTS: list[str] = [
    # CI triage / healing / fixing
    "ci-testing-agent.md",
    "ci-auto-healer-agent.md",
    "ci-emergency-response-agent.md",
    "ci-failure-resolution-agent.md",
    "ci-importerror-agent.md",
    "ci-optimization-agent.md",
    "ci-parameter-mismatch-healer.md",
    "ci-resilience-emergency-response-agent.md",
    "ci-triage-pipeline-agent.md",
    "pr-check-remediation-agent.md",
    "pr-test-infrastructure-fixer.md",
    # Test execution / healing / analysis
    "autonomous-test-healer-agent.md",
    "test-failure-analyzer-agent.md",
    "test-alignment-fixer-enhanced.md",
    "test-alignment-fixer.agent.md",
    "test-coverage-agent.md",
    "test-coverage-monitor.agent.md",
    "test-enhancement-agent.md",
    "test-pattern-guardian.md",
    "fragile-test-guardian.md",
    "mutation-testing-agent.md",
    "integration-test-runner.agent.md",
    "tokenization-coverage-agent.md",
    # Coverage analysis
    "coverage-gapfill-agent.md",
    "coverage-maintenance-agent.md",
    "coverage-roadmap-agent.md",
    # Code quality & security scanning
    "code-analysis-agent.md",
    "code-scanning-remediation-agent.md",
    "codebase-health-guardian.md",
    "codeql-alert-resolution-agent.md",
    "security-audit-agent.md",
    "unified-security-scanner.md",
    "dependency-vulnerability-scanner.agent.md",
    # QA / validation
    "qa-walkthrough-agent.md",
    "ml-validation-suite-agent.md",
    "artifact-monitor-agent.md",
    # Workflow / CI infra
    "workflow-ci-fixer.agent.md",
    "workflow-health-monitor.md",
    "workflow-health-monitor.agent.md",
    # Language-specific fixers that scan the whole codebase
    "python-312-type-fixer.md",
    "datetime-modernizer.agent.md",
    "recon-scout-agent.md",
]

# ── Section template ──────────────────────────────────────────────────────────
SECTION_TEMPLATE = """
---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** This agent MUST use `scripts/ci/rvs_preflight.py` (or the
> `BatchScanRunner` Python API) for all codebase scans.  Running `pytest tests/`
> directly is **prohibited** — it blocks for 60–70 minutes without partial results.

### Quick Reference

```bash
# 1. Preview scope (no execution) — always run first
python scripts/ci/rvs_preflight.py --group quick --preview

# 2. Incremental scan — changed files only (fastest, use during active work)
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# 3. Full pre-commit sweep (parallel batches of 30 files, 6 workers)
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# 4. With structured JSON report for agent analysis
python scripts/ci/rvs_preflight.py --group quick --workers 6 \\
    --report /tmp/rvs_report.json

# 5. Fail-fast triage (stop all batches on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
```

### Python API

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)
result = runner.scan(group="quick", changed_only=True)
# result.ok, result.failures, result.summary_line, result.batches_run
if not result.ok:
    for failure in result.failures[:10]:
        print(f"  FAILED: {failure}")
```

### Decision Flow

1. `--preview` → confirm test scope
2. `--changed-only` → validate your specific changes
3. `--group quick --workers 6` → full sweep before commit
4. Parse `--report` JSON for structured failure analysis

**Full protocol**: `.github/agents/BATCH_SCAN_PROTOCOL.md`
"""


def inject(agent_path: Path, dry_run: bool) -> bool:
    """Return True if the file was (would be) modified."""
    content = agent_path.read_text(encoding="utf-8")
    if SECTION_MARKER in content:
        return False   # already injected

    new_content = content.rstrip("\n") + "\n" + SECTION_TEMPLATE
    if not dry_run:
        agent_path.write_text(new_content, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true",
                   help="Show which files would be modified without changing them")
    args = p.parse_args(argv)

    modified = 0
    skipped_missing = 0
    already_done = 0

    for filename in APPLICABLE_AGENTS:
        path = AGENTS_DIR / filename
        if not path.exists():
            print(f"  [SKIP-MISSING] {filename}")
            skipped_missing += 1
            continue

        changed = inject(path, dry_run=args.dry_run)
        if changed:
            tag = "DRY-RUN" if args.dry_run else "INJECTED"
            print(f"  [{tag}] {filename}")
            modified += 1
        else:
            print(f"  [ALREADY-DONE] {filename}")
            already_done += 1

    print(
        f"\nDone. Modified={modified}  AlreadyDone={already_done}"
        f"  MissingFile={skipped_missing}"
        + (" (dry-run — no changes written)" if args.dry_run else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
