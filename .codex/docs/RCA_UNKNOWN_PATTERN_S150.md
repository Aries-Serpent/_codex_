# RCA: Every CI Failure Classified as "unknown" — S150

**Date:** 2026-03-18  
**Session:** S150  
**PR:** #3606 (`0D_base_`)  
**Failing Run:** [23248352799](https://github.com/Aries-Serpent/_codex_/actions/runs/23248352799)  
**Workflow:** `agent-auth-delegation.yml` → `iterative-self-healing-ci.yml`  
**Severity:** High — caused self-healing CI to never attempt auto-fix, always escalating to human

---

## 1. Symptom

Every `iterative-self-healing-ci.yml` escalation comment reported:

```
Pattern: unknown
```

Even for well-understood failures (REQ-10 branch-behind-main, ruff lint, YAML parse),
the self-healing CI classified them all as "unknown" and could not auto-fix anything.

---

## 2. Root Cause Analysis

### Root Cause 1 — Missing `--classify-run` flag (PRIMARY)

`iterative-self-healing-ci.yml` calls:

```bash
PATTERN=$(python3 scripts/ci/collect_telemetry.py \
  --classify-run "$TRIGGERING_RUN_ID" \
  --owner Aries-Serpent --repo _codex_ \
  --token "$GH_TOKEN" 2>/dev/null || echo "unknown")
```

However, `collect_telemetry.py` had **no `--classify-run` argument**.  
`argparse` exits with code 2 on unknown flags → `|| echo "unknown"` fires →
**every run gets pattern `unknown`**.

**Evidence:**
- `scripts/ci/collect_telemetry.py` argparse block (lines 363–376): only defined
  `--owner`, `--repo`, `--branch`, `--days`, `--output`, `--token`.
- `iterative-self-healing-ci.yml` `triage` job, step `Classify failure pattern`:
  calls `--classify-run` unconditionally.
- Confirmed by running locally: `python3 scripts/ci/collect_telemetry.py --classify-run 1`
  exits 2 with "unrecognized arguments".

**Fix:** Added `--classify-run <RUN_ID>` argument to `collect_telemetry.py` `main()`.
When provided, it fetches the run + jobs from the GitHub API, calls
`classify_failure()`, and prints the pattern name to stdout — then returns without
running the full report generation path.

**Classification for run 23248352799** (post-fix):  
Run name "Agent Token Delegation" → matches `auth-delegation` keyword "agent token".  
This is the correct result — the workflow is an auth/delegation workflow, not the
rebase gate itself. Both `auth-delegation` and `rebase-gate` are non-fixable patterns;
the self-healing CI escalates in both cases. The fix ensures the escalation comment
now shows the accurate pattern name (e.g., `auth-delegation`) instead of `unknown`.

### Root Cause 2 — REQ-10 Hard Block (branch behind main)

Branch `0D_base_` had a `BRANCH_REBASE_REQUIRED` comment marker present
(posted by `branch-rebase-gate.yml`) and was behind `main`.  
The `agent-auth-delegation.yml` `cognitive-preflight` job step 14 checks for this
marker via the GitHub API and calls `core.setFailed()` when found.

**Evidence:**
- Job log line: `REQ-10 FAIL: A BRANCH_REBASE_REQUIRED marker is present and branch is still behind/diverged.`
- `agent-auth-delegation.yml` step "REQ-10: Branch rebase check (hard block if behind/diverged)".

**Fix (operational):** This failure self-resolves once the agent pushes new commits
that advance the branch tip. The `branch-rebase-gate.yml` then posts a
`BRANCH_REBASE_RESOLVED` comment that clears the gate on the next pre-flight run.
No code change is needed; the gate is working as designed.

### Root Cause 3 — Main branch divergence (informational)

The two commits on `main` that `0D_base_` was missing at the time of the failure:

| SHA | Message | Type |
|-----|---------|------|
| `74f164f` | `chore(vars): auto-sync variable audit report [skip ci]` | Auto-generated |
| `3a4c8c7` | `chore(vars): sync .codex/agent_context.json from repo variables [skip ci]` | Auto-generated |

Both are automated housekeeping commits with **no code changes**.  
**Decision: no cherry-pick required.**

---

## 3. Timeline

| Time (UTC) | Event |
|---|---|
| 2026-03-18T13:58:14Z | `agent-auth-delegation.yml` triggered by `github-code-quality[bot]` review |
| 2026-03-18T13:58:31Z | REQ-10 step begins (step 14) |
| 2026-03-18T13:58:33Z | `core.setFailed()` — REQ-10 hard block fires |
| 2026-03-18T13:58:37Z | Job conclusion: `failure`; `activate-delegation` skipped |
| ~2026-03-18T14:00Z | `iterative-self-healing-ci.yml` triggers; calls `--classify-run` |
| ~2026-03-18T14:01Z | `argparse` exits 2 → pattern "unknown" → escalation comment posted |
| 2026-03-18T14:06Z | S150 session starts; root cause identified |
| 2026-03-18T14:xx | Fix committed: `--classify-run` added to `collect_telemetry.py` |

---

## 4. Fix Applied

**File:** `scripts/ci/collect_telemetry.py`  
**Change:** Added `--classify-run <RUN_ID>` argument to `main()`.

```python
parser.add_argument(
    "--classify-run",
    metavar="RUN_ID",
    help="Classify a single workflow run and print the pattern name to stdout.",
)

# …in the execution block:
if args.classify_run:
    run_id = int(args.classify_run)
    run = requests.get(run_url, headers=collector.headers, timeout=30).json()
    jobs = collector.collect_job_details(run_id)
    pattern = collector.classify_failure(run, jobs)
    print(pattern)
    return
```

On error, prints `"unknown"` and exits 0 (to preserve the `|| echo "unknown"` contract).

**Tests added:** `tests/ci/test_telemetry_collection.py` — class `TestClassifyRunCLI`
(5 new tests: rebase-gate match, auth-delegation match, unknown fallback,
main() entrypoint prints pattern, main() prints unknown on API error).

---

## 5. Prevention

| Measure | Status |
|---------|--------|
| Unit tests for `--classify-run` flag | ✅ Added (S150) |
| Pattern `BRANCH_BEHIND_BASE` in `.codex/patterns/ci_failure_patterns.yaml` | ✅ Already present (S149) |
| `rebase-gate` keyword in `PATTERN_KEYWORDS` | ✅ Already present (S149) |
| `--classify-run` documented in `collect_telemetry.py` CLI help | ✅ Added (S150) |

**Future prevention rule:** When adding a new CLI flag to any script called by a
workflow, verify the workflow call-site uses the correct flag name.  
Add a unit test that invokes `main()` with the same flags the workflow uses.

---

## 6. Lessons Learned

1. **`argparse` silent failures in CI pipelines**: `parser.parse_args()` exits 2 on
   unknown flags; shell `|| echo "fallback"` silently hides this. Always test scripts
   with the exact flags the workflow uses.
2. **REQ-10 is self-clearing**: The BRANCH_REBASE_REQUIRED gate does not require a
   code fix — pushing any commit to the branch triggers `branch-rebase-gate.yml`
   which posts `BRANCH_REBASE_RESOLVED` when the branch is up-to-date.
3. **Auto-generated [skip ci] commits on main never need cherry-picking**: Variable-sync
   and manifest-refresh commits contain no code and cannot conflict.

---

## 8. Update — S150 Run 2 (2026-03-18T14:46Z)

A second escalation (run [23250109072](https://github.com/Aries-Serpent/_codex_/actions/runs/23250109072))
still showed "unknown" after the `--classify-run` fix was merged.

**Root Cause 4 — Missing keywords for GitHub dependency-graph service**

Run name: `"Automatic Dependency Submission (Python)"`  
Actor: `github-advanced-security[bot]` (event: `dynamic`)  
Failure: transient GitHub API error — `"An error occurred while processing your request. Please try again later."`

Even with `--classify-run` working, the run name contained none of the existing
`PATTERN_KEYWORDS` entries, so `classify_failure()` returned `"unknown"`.

**Fix:** Added to the `security-scan` pattern:
```python
"dependency submission", "dependency-submission",
"automatic dependency", "component-detection",
```

**Note:** This is a GitHub-managed service failure (GitHub API transient error),
not a code defect. It is correctly non-fixable; the self-healing CI escalates.
The fix ensures the escalation comment now shows `security-scan` instead of `unknown`.

**Prevention:** Added `test_classify_run_dependency_submission` to `TestClassifyRunCLI`.

---

## 7. Related Documents

- `scripts/ci/collect_telemetry.py` — fixed file
- `.github/workflows/iterative-self-healing-ci.yml` — caller workflow
- `.github/workflows/branch-rebase-gate.yml` — REQ-10 enforcement
- `.codex/patterns/ci_failure_patterns.yaml` — pattern library (BRANCH_BEHIND_BASE)
- `scripts/ci/ci_triage_repro.sh` — 7-check local repro toolkit
- `docs/ci/CI_TRIAGE_REPRO_S145.md` — triage repro guide
