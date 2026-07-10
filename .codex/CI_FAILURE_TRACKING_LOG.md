# CI Failure Tracking Log

Tracks recurring CI failure patterns, root causes, and resolutions across all sessions.

## Purpose

This log is referenced by `.github/workflows/pre-flight-validation.yml` as a quick-reference
resource when rescue-comment jobs fire. For per-session remediation history, see:

- [`docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md`](../docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md)
- [`docs/ci/CI_FAILURE_ANALYSIS.md`](../docs/ci/CI_FAILURE_ANALYSIS.md)
- [`.codex/CI_FAILURE_PATTERN_ANALYSIS.md`](CI_FAILURE_PATTERN_ANALYSIS.md)

## Common Patterns

| Pattern | Root Cause | Resolution |
|---------|-----------|------------|
| `end-of-file-fixer` | Workflow YAML missing trailing newline **or has a trailing blank line** | Ensure file ends with exactly one `\n` (strip trailing blank lines) |
| `check-cross-references` | Internal link targets missing | Create file or update reference |
| `Deferral Language Gate` | PR body/comment contains deferral phrase | Add `EXEMPTION_PATTERNS` or remove phrase |
| `detect-secrets` | New hex string in docs without pragma | Add `# pragma: allowlist secret` |
| `stale-commit CI run` | Automated commits (chore(auth)/chore(d00)) advance branch HEAD after agent code commit; CI ran on superseded SHA | Still fix the underlying defect — it will re-trigger on HEAD. Check `run.head_sha != PR head.sha`. See pattern: `stale_commit_ci_run_20260327.json` |

## PDA Loop+ AfterMath Patterns

Patterns captured in `.codex/cognitive_brain/patterns/` for agent auto-fix learning:

| Pattern ID | Trigger | Auto-Fix Eligible | Confidence |
|------------|---------|-------------------|------------|
| `end_of_file_fixer_yaml_trailing_blank` | `end-of-file-fixer` fails on `*.yml` | ✅ Yes | 0.97 |
| `stale_commit_ci_run` | `run.head_sha != PR head.sha` in rescue event | ✅ Yes (still fix underlying defect) | 0.95 |
| `check_cross_references_missing_file` | `check-cross-references` fails on new link | ⚠️ Semi (create stub file) | 0.85 |
| `deferral_language_false_positive` | Deferral gate triggers on documentation prose | ✅ Yes (add EXEMPTION_PATTERNS) | 0.90 |

## Last Updated

2026-03-27 — S236: Added stale-commit CI run pattern and PDA Loop+ AfterMath pattern table. S230: Created to satisfy `check-cross-references` hook in `pre-flight-validation.yml`.

## Pre-commit Hook Failure Diagnostics — OBJ-001 (S236)

### Problem
When `validate.yml` Fast Validation fails with `pre-commit checks failed`, the job log only shows that summary line. Agents previously had to download the `validation-log-fast-{run_id}` artifact (zip) to identify the failing hook — causing a 1–2 tool-call delay and potential "I don't know" diagnosis.

### Fix Applied (S236)
`validate.yml` now emits a `$GITHUB_STEP_SUMMARY` block on failure that shows:
- The failing hook name (e.g., `fix end of files.......Failed`)
- The hook ID (`- hook id: end-of-file-fixer`)
- Files modified by the hook (`Fixing .github/workflows/resilient_validation.yml`)

This summary is **visible directly in `get_job_logs` output** without downloading any artifact.

### Fast-Path Diagnostic Protocol (for future agents)

When `validate.yml / Fast Validation` fails:
1. Call `get_job_logs(run_id=..., failed_only=True, return_content=True)` — step summary now included
2. Look for `## ❌ Pre-commit Failure Summary` block in the log content
3. The hook ID and affected files are right there — no artifact download needed
4. Cross-reference with the 28-hook catalog in `.codex/cognitive_brain/objectives_tracker.md` OBJ-001

### Deep-Research Protocol (when hook is still unknown after step 1-4)
If step summary is absent (e.g., workflow ran before S236 fix):
1. Download `validation-log-fast-{run_id}` artifact: `github-mcp-server-actions_get(method=download_workflow_run_artifact, resource_id={artifact_id})`
2. Fetch URL with `web_fetch` tool and extract to a workspace-relative scratch location (e.g., `.codex/scratch/`) via bash `curl | unzip` — acceptable transient use per `.github/TEMPORARY_FILES_POLICY.md §3`. **Never use `/tmp/`** for this output.
3. `grep -E "\.{3,}\s*Failed$|^- hook id:|^- exit code:|^- files were modified|^Fixing " validation.log`
   (The trailing `$` matches end-of-line in the shell; no backslash needed inside single-quoted regex strings.)

### "I Don't Know" Policy
Per codebase agency policy (S236 new requirement): **any "I don't know" situation must trigger:**
1. Deep codebase-wide research to understand the unknown
2. A detailed plan set in `.codex/cognitive_brain/objectives_tracker.md`
3. Immediate implementation of the research-identified fix
4. Documentation in this log and in the AfterMath pattern store

Never proceed with speculative fixes. Always investigate first.

---

## Branch Divergence Failure Patterns (S237 — 2026-03-27)

Recurring failures from triage report #3737. **5 workflows affected by 2 distinct root causes.**

### Pattern: `grep_c_double_output` (RC-1)

| Field | Value |
|-------|-------|
| **Workflow** | `branch-divergence-monitor.yml` |
| **Root cause** | `COUNT=$(echo "$VAR" \| grep -c . \|\| echo 0)` — `grep -c` outputs `0` AND exits 1; `\|\| echo 0` appends a second `0`. Result: `COUNT="0\n0"` |
| **Downstream** | `GITHUB_OUTPUT` gets `key=0\n0` → `##[error]Invalid format '0'`; Python heredoc sees `"key": 0\n0,` → SyntaxError |
| **Fix** | Replace `\|\| echo 0` with `\|\| true` + use `int("$VAR".strip() or "0")` in Python |
| **Status** | ✅ Fixed S237 |
| **Auto-fix eligible** | YES — `sed -i 's/grep -c \. || echo 0/grep -c . || true/g'` |

### Pattern: `git_checkout_without_force` (RC-2)

| Field | Value |
|-------|-------|
| **Workflows** | `cognitive-analysis-feed.yml`, `repo-var-sync-schedule.yml`, `embedding-index-rebuild.yml`, `vars-guide-sync.yml` |
| **Root cause** | `git checkout -B _autogen_sync_ origin/$TARGET` with uncommitted local changes → git refuses, exits 1 |
| **Context** | Files already copied to `/tmp` before checkout — force is safe |
| **Fix** | `git checkout -fB _autogen_sync_ origin/"$_TARGET"` |
| **Status** | ✅ Fixed S237 |

### Pattern: `auto_gen_routing_on_main` (RC-3)

| Field | Value |
|-------|-------|
| **Cause** | Scheduled workflows always run from `main`. Routing fix (push to `0D_base_` when branch exists) lives on `0D_base_` but not yet on `main` until staging-gate PR merges. |
| **Effect** | Auto-gen commits accumulate on `main` each scheduled run, widening divergence |
| **Self-healing** | RC-2 fix allows routing to succeed once `git checkout -fB` works correctly |
| **Long-term** | Resolved automatically when current staging-gate PR (`0D_base_` → `main`) merges |
| **Status** | 🔄 In progress — RC-2 fix applied, awaiting merge |

### Full Plan Set
See `.codex/plans/BRANCH_DIVERGENCE_PLAN_SET.md` for the complete investigation, taxonomy, and remediation roadmap.

## Last Updated

2026-03-27 — S237: Added branch divergence pattern section (RC-1, RC-2, RC-3). Fixed 5 workflows.
2026-03-27 — S236: Added pre-commit hook diagnostics section (OBJ-001) and stale-commit pattern.
