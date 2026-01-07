# KPIs: Status Reporting (v1.2)
> Generated: 2025-11-02 15:42:47 UTC | Author: mbaetiong  
🧠 Roles: [Primary: KPI Curator], [Secondary: Reviewer] ⚡ Energy: 5

Purpose
- Track high-level health signals across daily reports.

KPIs
| KPI | Definition | Source | Target |
|---|---|---|---|
| Coverage (overall) | totals.percent_covered | .coverage.json | ≥ fail_under_coverage |
| Schema Drift Rate | FAIL validations / total validations | schema_validation_results.json | 0 |
| Security Findings (high/critical) | Count by severity | pip-audit/bandit | 0 |
| Perf Throughput Δ | Steps/s Δ day-over-day | perf_snapshot.json | ≥ 0 |
| Repro Controls Coverage | Implemented/Total | snapshot.repro.core_controls | ↑ trend |
