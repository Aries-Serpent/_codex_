# [Diff]: Capability Score Comparison (Advisory)
> Generated: 2025-12-06 04:45:00Z | Author: Comprehensive Audit System  
> 🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Inputs
| Field | Value |
|-------|-------|
| Old | reports/capability_matrix_prev.md (not provided) |
| New | reports/capability_matrix_20251206_044500.md |

## Result
Advisory-only: No old report provided; regression gate not applied.  
To run a diff:
```bash
python scripts/space_traversal/audit_runner.py diff --old reports/capability_matrix_prev.md --new reports/capability_matrix_20251206_044500.md
```

## Guidance
- Commit baseline matrix as `reports/capability_matrix_prev.md` to enable regression checking.
- Enable `options.fail_on_score_regression: true` for hard failure on score drops.
- Set `regression_delta_threshold` to a non-trivial value (e.g., 0.02).

## Establishing Baseline
To establish a baseline for future comparisons:
```bash
cp reports/capability_matrix_20251206_044500.md reports/capability_matrix_baseline.md
git add reports/capability_matrix_baseline.md
git commit -m "Establish capability matrix baseline for regression tracking"
```

*End of Diff*
