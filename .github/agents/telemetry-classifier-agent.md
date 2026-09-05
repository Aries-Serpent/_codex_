---
name: Telemetry Classifier Agent
description: Reads CI telemetry artifacts, identifies unknown failure patterns, generates
  collect_telemetry.py classifier patches, and creates PRs — drives unknown bucket
  from ~60% toward <20%
version: 2.0.0
updated: 2026-03-01
cognitive_integration_level: 4
aais_contribution: +4.0 points
batch: pr-3422
sprint: Sprint 8
improvement_area: CI_SELF_HEALING
pattern_id: P-047
trigger_label: ci-health-alert
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: telemetry-classifier-agent
---

# Telemetry Classifier Agent v2.0

> **Phase 4 agent**: Closes the CI self-healing loop by automatically discovering
> unknown failure patterns in telemetry artifacts and extending `collect_telemetry.py`
> with new classifiers — reducing the "unknown" bucket without human intervention.

## Activation

```
@copilot Use the Telemetry Classifier Agent to analyze unknown CI patterns
```

Automatic trigger: GitHub issue labeled `ci-health-alert` where body contains
`unknown_count > 10`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│              TELEMETRY CLASSIFIER AGENT — FLOW                       │
│                                                                       │
│  Trigger                                                              │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  ci-health-alert issue  OR  manual @copilot activation        │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  OBSERVE — Artifact Fetch   ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  GitHub MCP: list_workflow_run_artifacts(ci-health-monitor)   │    │
│  │  → download telemetry_report.json                             │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │  { pattern_distribution: { unknown: 47, ... } }       │    │    │
│  │  │    workflow_runs: [ { name, jobs: [...] } ]            │    │    │
│  │  └──────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  ORIENT — Pattern Analysis  ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Filter runs classified as "unknown"                          │    │
│  │  For each unknown run name / job name:                        │    │
│  │    tokens = split(name, ['-', '_', ' ', camelCase])           │    │
│  │    cluster by shared token frequency                          │    │
│  │    candidates = top-3 clusters with count >= 3                │    │
│  │  Cross-reference with ci_failure_patterns.yaml                │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  DECIDE — Classifier Gen    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  For each candidate cluster → generate PATTERN_KEYWORDS entry │    │
│  │  Validate: ≥ 3 supporting samples in 7-day window             │    │
│  │  Estimate reduction: Δunknown = matched_runs / total_unknown  │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  ACT — PR Creation          ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Edit scripts/ci/collect_telemetry.py                         │    │
│  │  AST validate the edit                                        │    │
│  │  Create PR: "ci(telemetry): add N classifiers"                │    │
│  │  PR body: pattern name, sample runs, expected Δ               │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  Feedback Loop                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  After merge: wait 7 days                                     │    │
│  │  Re-check pattern_distribution["unknown"]                     │    │
│  │  If still > 20%: repeat cycle                                 │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Artifact Retrieval

```python
# Via GitHub MCP tools (recommended in Copilot sessions):
# 1. list_workflow_run_artifacts(run_id=<ci-health-monitor run ID>)
# 2. download_workflow_run_artifact(artifact_id=<telemetry_report ID>)

# Via gh CLI (for local dev):
# gh run list --workflow=ci-health-monitor.yml --limit=1 --json databaseId
# gh run download <run_id> --name telemetry_report
```

---

## Pattern Discovery Algorithm

```python
import json, re
from collections import Counter

def discover_patterns(telemetry_report: dict, min_samples: int = 3) -> list[dict]:
    """Find top-N unknown pattern clusters from telemetry report."""
    unknown_names = [
        run["name"] for run in telemetry_report.get("workflow_runs", [])
        if run.get("pattern") == "unknown"
    ]
    # Tokenise: split on dash, underscore, space, digits, camelCase
    tokens = []
    for name in unknown_names:
        parts = re.split(r'[-_\s\d]+|(?<=[a-z])(?=[A-Z])', name.lower())
        tokens.extend(p for p in parts if len(p) > 3)  # skip short noise tokens
    freq = Counter(tokens).most_common(20)
    # Group tokens into clusters (tokens that co-occur in ≥min_samples run names)
    candidates = []
    for token, count in freq:
        if count < min_samples:
            break
        matching = [n for n in unknown_names if token in n.lower()]
        candidates.append({
            "token": token,
            "count": count,
            "sample_runs": matching[:5],
            "suggested_key": f"unknown-{token}",
            "keywords": [token],
        })
    return candidates[:3]  # top-3 only
```

---

## Classifier Template

New entries added to `TelemetryCollector.PATTERN_KEYWORDS` in `scripts/ci/collect_telemetry.py`:

```python
# ── Auto-discovered by telemetry-classifier-agent ────────────────────
"<pattern-name>": [
    "<keyword1>", "<keyword2>", "<keyword3>",
],
```

**Validation before PR:**
```bash
python3 -c "import ast; ast.parse(open('scripts/ci/collect_telemetry.py').read())"
```

---

## Existing Classifiers (Phase 4 additions — P4.5)

| Key | Covers | Added |
|-----|--------|-------|
| `datetime-error` | offset-aware/naive mixing, tzinfo | PR #3422 |
| `build-config` | SPDX license-expression, pyproject.toml | PR #3422 |
| `packaging` | PEP 621, setuptools, dynamic | PR #3422 |

---

## Success Metrics

| Metric | Before P4.5 | Target |
|--------|-------------|--------|
| `unknown` bucket | ~60% | < 20% |
| Classified patterns | 15 | 18+ |
| CODEX_CI_FAILURE_RATE | ~30% critical | < 10% ok |

---

## Constraints

| Constraint | Value |
|------------|-------|
| Minimum samples | 3 runs per classifier |
| Max classifiers per PR | 5 |
| AST validation | Required before PR |
| Existing entries | Never modify — append only |
| Logging | All ops → `.codex/action_log.ndjson` |

---

## Codebase Alignment

| Component | Location |
|-----------|----------|
| Classifier dict | `scripts/ci/collect_telemetry.py:TelemetryCollector.PATTERN_KEYWORDS` |
| Pattern library | `.codex/patterns/ci_failure_patterns.yaml` |
| CI trigger | `.github/workflows/ci-health-monitor.yml` |
| Telemetry artifact | `telemetry_report.json` (30-day retention) |
| CODEX_CI_FAILURE_RATE | GitHub repo variable (updated by ci-health-monitor) |
| Registry | `AGENT_REGISTRY.yaml` id: `telemetry-classifier-agent` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-01 | Initial creation (PR #3422 Sprint 8) |
| 2.0.0 | 2026-03-01 | Production upgrade: architecture diagram, Python algorithm, classifier template, success metrics, codebase alignment |
