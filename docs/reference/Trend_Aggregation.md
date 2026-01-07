# [Reference]: Trend Aggregation (P5)

> Generated: 2025-11-06 19:02:11 UTC | Author: mbaetiong  
> Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1. Purpose

Track longitudinal maturity improvements per capability across archived runs.

## 2. Data Source

Historical `capabilities_scored*.json` snapshots under `audit_artifacts/`.

## 3. Output

`trend_scores.json`:

```json
{
  "snapshots": ["capabilities_scored_0.json","capabilities_scored_1.json"],
  "capabilities": [
    {"id":"alpha","scores":[0.50,0.55,0.60],"delta":0.10,"pct_change":0.20,"sparkline":"▁▄█"}
  ]
}
```text

## 4. Sparkline Encoding

Unicode block characters represent normalized position within min-max range.

## 5. Interpretation

| Field | Meaning |
|-------|---------|
| delta | Raw score improvement |
| pct_change | Relative improvement vs first snapshot |
| sparkline | Quick visual trajectory |

## 6. Usage

```bash
TREND_SPARKLINE=1 python scripts/archive/trend_aggregate.py
jq '.capabilities[] | select(.delta > 0)' audit_artifacts/trend_scores.json
```text

## 7. Alerts (Future)

| Condition | Alert |
|----------|-------|
| Negative delta beyond threshold | Regression warning |
| Stagnant scores (±0.01) across N runs | Improvement stall notice |
| Volatile swings (>0.15 change) | Stability review |

## 8. Planned Extensions

- Weighted rate-of-change factoring recency.
- Multi-dimensional trend (component-specific trajectories).
- Export CSV for BI dashboards.

*End of Trend Aggregation Reference*
