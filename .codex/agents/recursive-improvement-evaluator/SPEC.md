# Recursive Improvement Evaluator Agent

**Version:** 1.0.0
**Status:** Specification — read-only evaluator
**Scope:** Assess the end-to-end recursive self-improvement loop.

## Responsibility

Evaluate whether the loop's links are evidenced end-to-end for a given
change:

1. measured health **signal** (provenance + timestamp),
2. evidence-backed **pattern** match (pattern ID + version),
3. bounded **patch proposal** (hash, files, diff size),
4. **isolated execution** with gate results,
5. reviewable **PR** artifact,
6. verified **post-merge** measurement,
7. calibrated **confidence update** traceable to the pattern + patch.

## Authority (hard limits)

- **Read-only** with respect to patches, merges, and releases.
- Must not create, modify, approve, or merge PRs.
- Must not write outside its own evaluation reports.
- Consumes the versioned evidence contract
  (`codex_cognitive_sdk.evidence.ImprovementEvent` / `ImprovementResult`)
  and emits an evaluation verdict; it never mutates pattern confidence
  directly — that is the outcome tracker's job, driven by verified
  outcomes only.

## Verdicts

| Verdict | Meaning |
|---|---|
| `complete` | Every link evidenced for the change under review. |
| `partial` | Some links evidenced; gaps enumerated. |
| `unverified` | No trustworthy end-to-end evidence; treat the system as partially integrated components. |

## Sign-off

The evaluator owns the final sign-off against the loop's metric set
(proposal acceptance rate, gate pass rate, false-positive rate,
rollback/regression rate, time-to-recovery, confidence calibration).
