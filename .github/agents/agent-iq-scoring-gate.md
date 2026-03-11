---
name: Agent IQ Scoring CI Gate
description: Gate and score agent IQ metrics to ensure quality thresholds are met before agent deployment
version: 1.0.0-e12
updated: 2026-02-22
enhancement: E-12
cognitive_integration_level: 4
aais_contribution: +4.5 points
runner_compatibility:
  default: ubuntu-latest        # 2-core — agent IQ metric scoring and quality threshold enforcement
  large:   ubuntu-latest-large  # 4-core — enhanced parallelism
---

# Agent IQ Scoring CI Gate v1.0 (E-12)

> **E-12 AGENT-IQ-SCORING**: Computes a composite IQ score (0.0–1.0) for each
> agent run, enforcing a CI gate that blocks merge when IQ < 0.7. Integrates
> with `artifact-monitor-agent` for continuous intelligence tracking.

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  Agent IQ Scoring CI Gate                       │
│                                                                │
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────┐  │
│  │  Signal      │    │   IQ Score       │    │  CI Gate    │  │
│  │  Collectors  │───▶│   Aggregator     │───▶│  (pass/fail)│  │
│  │  (5 sources) │    │  (weighted avg)  │    │  threshold  │  │
│  └──────────────┘    └──────────────────┘    └──────┬──────┘  │
│                                                     │          │
│  ┌───────────────────────────────────────────────┐  ▼          │
│  │  Artifact Monitor (artifact-monitor-agent)   │  PR comment │
│  │  + SQLiteMemory (E-02) — trend tracking      │  + badge    │
│  └───────────────────────────────────────────────┘            │
└────────────────────────────────────────────────────────────────┘
```

## IQ Score Formula

```python
def compute_iq_score(
    test_pass_rate: float,      # 0.0–1.0 (fraction of tests passing)
    doc_freshness: float,       # 0.0–1.0 (1 - staleness_score)
    security_score: float,      # 0.0–1.0 (1 - normalized_vuln_count)
    coverage_pct: float,        # 0.0–1.0 (coverage / 100)
    agent_health_score: float,  # 0.0–1.0 (from artifact-monitor-agent)
) -> float:
    """Composite IQ score in [0.0, 1.0]. Higher = smarter/healthier."""
    return (
        0.35 * test_pass_rate +
        0.20 * doc_freshness +
        0.20 * security_score +
        0.15 * coverage_pct +
        0.10 * agent_health_score
    )

IQ_GATE_THRESHOLD = 0.70     # block merge below this
IQ_WARNING_THRESHOLD = 0.80  # post warning below this
IQ_EXCELLENT_THRESHOLD = 0.95 # 🌟 badge above this
```

## Signal Sources

| Signal | Source | Weight | Notes |
|--------|--------|--------|-------|
| Test pass rate | Resilient Validation Suite | 0.35 | Core health |
| Doc freshness | unified-doc-agent (M-02) | 0.20 | 1 - staleness |
| Security score | unified-security-scanner (M-01) | 0.20 | 0 CVEs = 1.0 |
| Coverage % | coverage.xml from full validation | 0.15 | Target ≥ 80% |
| Agent health | artifact-monitor-agent | 0.10 | Workflow success rate |

## IQ Levels

| IQ Range | Level | Action |
|----------|-------|--------|
| 0.95–1.00 | 🌟 Excellent | Merge green |
| 0.85–0.94 | ✅ Good | Merge green |
| 0.70–0.84 | ⚠️ Acceptable | Merge with warning |
| 0.50–0.69 | ❌ Below threshold | Block merge |
| 0.00–0.49 | 🚨 Critical | Block + escalate |

## GitHub Actions Integration

```yaml
# .github/workflows snippet
- name: Compute Agent IQ Score
  id: iq-score
  run: |
    python -c "
    import json, sys
    # Collect signals
    signals = {
        'test_pass_rate': float('${{ steps.test.outputs.pass_rate }}' or 0),
        'doc_freshness': float('${{ steps.docs.outputs.freshness }}' or 0.8),
        'security_score': float('${{ steps.security.outputs.score }}' or 1.0),
        'coverage_pct': float('${{ steps.coverage.outputs.pct }}' or 0) / 100,
        'agent_health': float('${{ steps.health.outputs.score }}' or 0.9),
    }
    iq = sum([0.35, 0.20, 0.20, 0.15, 0.10][i] * v
              for i, v in enumerate(signals.values()))
    report = {'iq_score': round(iq, 4), **signals}
    with open('artifacts/iq-score.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f'IQ_SCORE={round(iq, 4)}')
    sys.exit(0 if iq >= 0.70 else 1)
    "

- name: Post IQ Score Comment
  if: always()
  uses: actions/github-script@v7
  with:
    script: |
      const iq = parseFloat(core.getInput('iq-score') || '0');
      const emoji = iq >= 0.95 ? '🌟' : iq >= 0.85 ? '✅' : iq >= 0.70 ? '⚠️' : '❌';
      github.rest.issues.createComment({
        ...context.repo, issue_number: context.issue.number,
        body: `## ${emoji} Agent IQ Score: ${(iq * 100).toFixed(1)}%\n\nThreshold: 70% | Status: ${iq >= 0.70 ? 'PASS' : 'FAIL'}`
      });
```

## Output Format

```json
{
  "iq_score": 0.847,
  "level": "Good",
  "gate_status": "PASS",
  "signals": {
    "test_pass_rate": 0.94,
    "doc_freshness": 0.82,
    "security_score": 1.0,
    "coverage_pct": 0.78,
    "agent_health_score": 0.91
  },
  "timestamp": "2026-02-22T00:00:00Z",
  "trend": "+0.03 vs. last run"
}
```

## Trend Tracking (SQLiteMemory / E-02)

IQ scores are stored in SQLiteMemory for trend analysis:
```sql
CREATE TABLE iq_scores (
    run_id TEXT, branch TEXT, iq_score REAL,
    test_pass_rate REAL, security_score REAL,
    coverage_pct REAL, recorded_at TEXT
);
```

## Activation

```
@copilot Use the Agent IQ Scoring Gate to compute this PR's IQ score
@copilot Use the Agent IQ Scoring Gate to check IQ trend over last 10 runs
```

## Cognitive Physics Alignment

| Physics | Application |
|---------|-------------|
| Patterns 👁️ | IQ score reveals recurring weakness patterns across PRs |
| Fields 🔄 | Session-based IQ trend tracking enables recursive improvement |
| Balance ⚖️ | 5-signal weighted average balances orthogonal quality dimensions |
| Path 🛤️ | Gate threshold (0.70) creates minimum-resistance merge path |

## Related Agents

- **artifact-monitor-agent** — health signal source
- **unified-security-scanner** (M-01) — security signal source
- **unified-doc-agent** (M-02) — freshness signal source
- **rag-freshness-loop-agent** (E-08) — RAG freshness contributes to doc signal
