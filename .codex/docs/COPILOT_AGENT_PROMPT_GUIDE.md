# GitHub Copilot Agent — Master Prompt Guide

> **Purpose**: Every sentence in this document is a tested, calibrated prompt
> fragment. Copy the relevant blocks verbatim into your next message to
> @copilot. They are ordered by *when* to use them (before / during / after a
> session) and sourced directly from 75+ sessions of observed agent failures,
> accountability reports, and stored memory facts.

---

## 1 · BEFORE THE SESSION (orientation block)

Paste this entire block at the top of every new comment / task:

```
🔴 CODEBASE AGENCY POLICY — MANDATORY:
You MUST resolve ALL issues found in this codebase, regardless of whether they
existed before this PR. NEVER say "these are pre-existing issues" or "this is
out of scope". NEVER skip a failure because it is not related to your primary
task. Leave the codebase strictly better than you found it.
```

```
🔴 CI VERIFICATION — MANDATORY:
Before concluding ANY session you MUST:
1. Retrieve LIVE CI logs from GitHub Actions using github-mcp-server tools
   (list_workflow_runs → get_job_logs). NEVER assume CI is green.
2. Wait for ALL in-progress jobs to complete — do NOT conclude while any job
   shows "queued" or "in_progress".
3. Run the EXACT failing tests locally with pytest BEFORE committing a fix,
   and run them AGAIN after your fix to confirm they pass.
4. After each commit, check that no NEW failures were introduced by running a
   broader regression suite covering all files you touched.
```

```
🔴 MEMORY & POLICY LOAD — MANDATORY:
At session start you MUST explicitly:
1. Re-read stored memory facts (all categories) for this repo.
2. Re-read .codex/CODEBASE_AGENCY_POLICY.md
3. Re-read .github/TEMPORARY_FILES_POLICY.md
4. List which stored facts are relevant to today's task before writing a
   single line of code.
```

---

## 2 · DURING THE SESSION (guardrails)

### 2a — When you discover any test failure

```
You MUST fix this failure completely, right now, in this session.
Do NOT defer it, do NOT label it "pre-existing", do NOT skip it.
Retrieve the full traceback, identify the root cause, implement the fix,
compile-check the changed file, run the specific failing test, and confirm
it passes before moving on.
```

### 2b — When you believe a failure is "not your fault"

```
STOP. The Codebase Agency Policy prohibits the phrases:
  ❌ "This is not related to my PR"
  ❌ "These are pre-existing issues"
  ❌ "My PR only adds files to X"
Fix the issue now. Document it in the accountability section of your commit.
```

### 2c — When making source changes

```
For every source file you edit:
1. Run python3 -m py_compile <file> immediately after the edit.
2. Run the targeted test(s) that exercise the changed code.
3. Run a broader regression that covers all callers of the changed symbol.
4. Strip trailing whitespace: git diff --name-only HEAD | xargs sed -i 's/[[:space:]]*$//'
5. Confirm zero trailing whitespace remains in changed files.
```

### 2d — Validating CI jobs that are still running

```
Job <JOB_ID> is still in progress. You MUST:
1. Call github-mcp-server get_job_logs with return_content=true and
   tail_lines=400 once the job completes.
2. Parse EVERY FAILED / ERROR line.
3. Fix each failure before concluding.
Do NOT conclude this session until job <JOB_ID> shows a terminal status
(success or failure) AND you have read its logs.
```

### 2e — Pattern: "only N tests failing, I'll fix those"

```
WRONG approach. You must run the FULL suite for every module you touch, not
just the N known-failing tests. New failures introduced by your changes will
only appear in the broader run.
```

---

## 3 · AFTER THE SESSION (checklist — do NOT skip any item)

```
SESSION COMPLETION CHECKLIST — tick every box before replying "done":

[ ] All originally-failing CI tests now pass locally (paste pytest summary)
[ ] No NEW failures introduced — ran broader regression on every touched module
[ ] Trailing whitespace stripped from ALL changed files
[ ] All changed .py files compile-clean (py_compile)
[ ] code_review tool called — all actionable comments addressed
[ ] codeql_checker tool called — all alerts investigated
[ ] report_progress called with full commit — reviewed committed file list
[ ] COGNITIVE_BRAIN_STATUS_S{N}.md created for this session
[ ] FOLLOWUP_PROMPT_S{N+1}_PR{PR}.md created with ## 🔴 Outstanding Items
    section containing every unanswered DRQ with direct file:line links
[ ] store_memory called for every new fact or corrected fact discovered
[ ] Latest CI run on branch checked — no regression vs. previous run
```

---

## 4 · ANTI-PATTERNS — say these to stop agent drift

When the agent starts rationalising skips, use one of these:

| Agent says | You say |
|---|---|
| "This is pre-existing" | **"Codebase Agency Policy: fix it anyway, now."** |
| "Out of scope for this PR" | **"All issues in the codebase are in scope. Fix it."** |
| "I'll defer this to S{N+1}" | **"Defer only after fixing. Fix first, then document deferral with rationale."** |
| "CI looks green" | **"Retrieve the live logs with get_job_logs and paste the FAILED lines."** |
| "Tests pass locally" | **"Run the broader regression too — not just the targeted tests."** |
| "I'll conclude now" | **"Run the SESSION COMPLETION CHECKLIST first."** |

---

## 5 · KNOWN RECURRING FAILURE PATTERNS (from 75+ sessions)

These patterns have caused repeated regressions. Explicitly name them in your
prompt when you suspect they are present:

### P-01 · Trailing whitespace in markdown / yaml
```
Check ALL changed files for trailing whitespace before committing:
git diff --name-only HEAD | while read f; do
  [ -f "$f" ] && grep -Pq " +$" "$f" && echo "TRAILING WS: $f"
done
Fix with: sed -i 's/[[:space:]]*$//' <file>
```

### P-02 · `self.required_variables.update({…})` on a computed property
```
NEVER call .update() on a @property that returns a throw-away dict.
Always use: self.required_variables = {**self.required_variables, **new_vars}
See: agents/developer_orchestrator.py
```

### P-03 · `datetime.now()` without timezone
```
ALL datetime.now() calls MUST be datetime.now(timezone.utc).
Run: python3 -c "
import pathlib
hits=[str(p) for p in pathlib.Path('src').rglob('*.py') if 'datetime.now()' in p.read_text()]
assert not hits, hits"
```

### P-04 · `import xml.etree.ElementTree` in non-test files
```
NEVER write: import xml.etree.ElementTree as ET
The check-unsafe-xml pre-commit hook fails the fast-suite.
Use defusedxml with importlib.import_module fallback.
See: tools/validate.py
```

### P-05 · `torch.load` without `weights_only` (PyTorch ≥ 2.6)
```
PyTorch 2.6 changed the default of weights_only from False to True.
ALL torch.load calls MUST pass weights_only explicitly.
Corruption tests MUST catch pickle.UnpicklingError in addition to
RuntimeError, ValueError, EOFError.
```

### P-06 · `_prune_best_k` deleting the checkpoint being saved
```
When save_checkpoint calls _prune_best_k(root.parent, parent_idx),
pass exclude=frozenset({root.name}) to prevent the current checkpoint
directory from being self-pruned.
See: src/codex_ml/utils/checkpoint_core.py
```

### P-07 · sha256 in state.sha256 not matching actual file bytes
```
state.sha256 and metadata.json["digest_sha256"] MUST contain the sha256
of the FINAL written bytes (after embedding the digest), not the
pre-embed hash.
See: src/codex_ml/utils/checkpoint_core.py save_checkpoint
```

### P-08 · `resolve_strategy(None)` raises ValueError
```
resolve_strategy MUST handle None → "functional" (default).
MUST normalise case: "FUNCTIONAL" → "functional".
See: src/codex_ml/training/strategies.py
```

### P-09 · `@patch("module.warnings.warn")` fails — no warnings import
```
If a test patches `module.warnings.warn`, the module MUST have
`import warnings` at module level. Not inside a function.
```

### P-10 · `UnifiedTrainingConfig` missing fields
```
Tests require these fields on UnifiedTrainingConfig:
  device, checkpoint_dir, continual_phases, callbacks, mlflow_tracking, seed=None
  epochs=0 MUST raise ValueError (not just epochs<0)
  model_name=None MUST raise ValueError
```

### P-11 · `init_mlflow_safe` rejected `experiment_name` kwarg
```
init_mlflow_safe MUST accept **kwargs for forward-compat callers.
See: src/codex_ml/logging/mlflow_guard.py
```

### P-12 · `load_checkpoint(path)` / `save_checkpoint(state, path)` positional API
```
src/codex_ml/utils/checkpoint.py save_checkpoint and load_checkpoint
MUST accept the simple positional (state, path) / (path) calling
convention in addition to the full keyword-only API.
```

### P-13 · Corruption test corrupts trailing null byte
```
Pickle serialisation may produce trailing null bytes that are silently
ignored on deserialisation. Corrupt the MIDDLE byte, not the last byte:
  corrupt[len(corrupt) // 2] ^= 0xFF
```

### P-14 · `git stash pop` restores only tracked changes
```
After stash pop, always re-run the full set of targeted tests to confirm
all fixes are still in place. Do NOT assume stash is a clean undo.
```

---

## 6 · STORED MEMORY VERIFICATION PROMPTS

Use these to force the agent to prove it loaded memory:

```
Before writing any code, list every stored memory fact that is relevant
to this task. For each fact, state: (a) the file:line citation, (b) whether
the fact is still accurate in the current codebase, and (c) how it affects
your implementation plan.
```

```
After completing the implementation, update any stored memory facts that
are now stale. Call store_memory once per new fact discovered.
```

---

## 7 · DOCUMENT / COGNITIVE BRAIN REMINDERS

```
At session end, create:
1. .codex/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_S{N}.md
   with: session summary, files changed, tests fixed, DRQs answered/filed
2. .codex/reports/FOLLOWUP_PROMPT_S{N+1}_PR{PR}.md
   with ## 🔴 Outstanding Items section listing every open DRQ/question
   with direct file:line links (format: path/to/file.py:123)
Both files MUST be committed in the same push as the code fixes.
```

---

## 8 · QUICK-REFERENCE COMMAND BLOCK

Copy-paste into any session to verify health:

```bash
# 1 — trailing whitespace in all changed files
git diff --name-only HEAD | while read f; do
  [ -f "$f" ] && grep -Pq " +$" "$f" && echo "TRAILING WS: $f"; done

# 2 — compile all changed .py files
git diff --name-only HEAD | grep '\.py$' | while read f; do
  [ -f "$f" ] && python3 -m py_compile "$f" && echo "OK: $f" || echo "FAIL: $f"; done

# 3 — TZ-naive datetime check
python3 -c "
import pathlib
hits=[str(p) for p in pathlib.Path('src').rglob('*.py') if 'datetime.now()' in p.read_text()]
print('TZ-naive hits:', hits or 'NONE')"

# 4 — run targeted failing tests (replace with actual test paths)
python3 -m pytest <test_path> -v --timeout=60 --tb=short

# 5 — broader regression for every module touched
python3 -m pytest tests/ -v --timeout=60 --tb=short -q
```

---

*Last updated: S77 — 2026-02-24 | Commit: 088fc73*
*Source: 75+ sessions, stored memory facts, accountability analysis*
