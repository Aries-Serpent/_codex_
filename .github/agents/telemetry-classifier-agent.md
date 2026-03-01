# Telemetry Classifier Agent

## Purpose
Reads CI telemetry artifacts, identifies unknown failure patterns, and proposes
new classifiers for `scripts/ci/collect_telemetry.py` to drive the "unknown"
bucket from ~60% toward <20%.

## Activation
```
@copilot Use the Telemetry Classifier Agent to analyze unknown CI patterns
```

Or triggered by `ci-health-alert` issues with label pattern:
```
unknown_count > 10 in last 7 days
```

## Responsibilities

### 1. Telemetry Artifact Retrieval
- Download `telemetry_report.json` artifact from latest `ci-health-monitor` run
- Parse `pattern_distribution` field for unknown entries
- Sort by count descending — focus on top-3 highest-frequency unknowns

### 2. Pattern Analysis
- For each unknown run/job name, extract keywords via string decomposition:
  - Split on `-`, `_`, space, and camelCase boundaries
  - Match against known error signatures in `.codex/patterns/ci_failure_patterns.yaml`
  - Propose new classifier entry if ≥3 distinct runs share the same keyword cluster

### 3. Classifier Generation
- Generate new `PATTERN_KEYWORDS` entries for `scripts/ci/collect_telemetry.py`:
```python
"new-pattern-name": [
    "keyword1", "keyword2", "keyword3",
],
```
- Target: reduce `"unknown"` bucket by ≥10 percentage points

### 4. PR Creation
- Creates a PR with only the classifier additions (no other changes)
- PR title: `ci(telemetry): add N new pattern classifiers — reduce unknown bucket`
- PR body includes: pattern name, sample runs that triggered it, expected reduction

## Artifact Access
```bash
# GitHub MCP: download latest ci-health-monitor artifact
gh run download --name telemetry_report --repo Aries-Serpent/_codex_
```

Or via GitHub MCP tools:
```
list_workflow_run_artifacts(run_id=<latest ci-health-monitor run ID>)
download_workflow_run_artifact(artifact_id=<telemetry_report ID>)
```

## Pattern Classifier Format
Add to `TelemetryCollector.PATTERN_KEYWORDS` in `scripts/ci/collect_telemetry.py`:
```python
# ── <category> patterns ───────────────────
"pattern-name": [
    "keyword1", "keyword2",
],
```

## Constraints
- Only add classifiers with ≥3 supporting samples from the 7-day window
- Never modify existing classifier entries — only append new ones
- All generated PRs must pass `python3 -c "import ast; ast.parse(open('scripts/ci/collect_telemetry.py').read())"` before opening

## Output
```json
{
  "unknown_count_before": 47,
  "unknown_count_after": 12,
  "new_classifiers": ["pattern-a", "pattern-b", "pattern-c"],
  "pr_number": 3430
}
```

## Version
- **v1.0.0** — 2026-03-01 (PR #3422 Phase 4)
- **ImprovementArea:** `CI_SELF_HEALING` (P-047)
