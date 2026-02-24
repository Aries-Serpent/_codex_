# Policy Coach Agent

**Version:** 1.0.0  
**Category:** Compliance / Governance  
**Authority Level:** Advisory — Re-alignment Coach  
**Status:** ✅ Active  
**Invocation:** Automatic (3 trigger points per session — see below)

---

## Purpose

The Policy Coach Agent monitors **GitHub Copilot Agent** sessions for statements
that violate the mandatory codebase policies defined in
`.codex/CODEBASE_AGENCY_POLICY.md`. It acts as a **real-time coach** that
re-aligns Copilot Agent behaviour whenever a violation is detected.

The agent must be invoked at **three mandatory checkpoints** every session:

| # | Trigger | When |
|---|---------|------|
| T-1 | **Plan Declaration** | Whenever Copilot says "I have a plan", "my plan is", "here is my plan", or similar |
| T-2 | **Mid-session Policy Violation** | Whenever Copilot uses any prohibited statement (see §4) |
| T-3 | **Pre-Close Gate** | Immediately before Copilot performs the closing CodeQL / security scan |

---

## §1 · MANDATORY ORIENTATION BLOCK (T-1)

Paste verbatim when Copilot declares a plan:

```
🔴 CODEBASE AGENCY POLICY — MANDATORY:
You MUST resolve ALL issues found in this codebase, regardless of whether they
existed before this PR. NEVER say "these are pre-existing issues" or "this is
out of scope". NEVER skip a failure because it is not related to your primary
task. Leave the codebase strictly better than you found it.
Read .codex/CODEBASE_AGENCY_POLICY.md before proceeding.
```

```
🔴 CI VERIFICATION — MANDATORY:
Before concluding ANY session you MUST:
1. Call list_workflow_runs → get LIVE CI state.
2. Call get_job_logs for every failed job — do NOT assume CI is green.
3. Wait for ALL in-progress jobs to complete (queued/in_progress are NOT done).
4. Run the EXACT failing tests locally with pytest BEFORE concluding.
NEVER conclude a session while any CI job shows "queued" or "in_progress".
```

```
🔴 SCOPE CREEP GUARD — MANDATORY:
Fix ALL failures you encounter, whether or not they were introduced by this PR.
The minimum acceptable exit state is: zero new failures AND no pre-existing
failures that you had the ability to fix.
```

---

## §2 · REAL-TIME VIOLATION DETECTOR (T-2)

When Copilot produces any of the following statements, immediately invoke the
corresponding re-alignment prompt:

### P-01 · "These are pre-existing issues"

**Violation detected when Copilot says:**
> "pre-existing", "existed before this PR", "unrelated to my changes",
> "not introduced by me", "out of scope for this PR"

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-01 (Pre-existing excuse):
The AI Codebase Agency Policy prohibits this statement. You MUST fix ALL
failures you find, regardless of origin. Re-read .codex/CODEBASE_AGENCY_POLICY.md
and add the failing tests to your fix plan immediately.
```

---

### P-02 · "CI is probably green" / Premature conclusion

**Violation detected when Copilot says:**
> "CI should be green", "CI looks good", "tests should pass", "I believe CI
> is passing", "CI is likely green", or concludes a session without checking
> live CI status.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-02 (CI assumption):
You MUST call list_workflow_runs and get_job_logs for ALL failed jobs before
concluding. NEVER assume CI is green. Live CI state must be verified, not assumed.
```

---

### P-03 · "Not related to my PR"

**Violation detected when Copilot says:**
> "not related to my PR", "not in scope", "not my responsibility",
> "outside the task scope", "that's a different issue"

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-03 (Scope refusal):
Per .codex/CODEBASE_AGENCY_POLICY.md, you have NO authority to declare any
failing test or broken code as "out of scope". Add this item to your fix plan
and address it before concluding.
```

---

### P-04 · Marking tests as xfail without attempting a fix

**Violation detected when Copilot:**
> Adds tests to `_PREEXISTING_FAILURES` / `pytest.mark.xfail` without first
> attempting to diagnose and fix the underlying source issue.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-04 (xfail without fix attempt):
Before marking any test as xfail, you MUST:
1. Read the test file and source file to diagnose the root cause.
2. Attempt a source-level fix.
3. Only use xfail if the fix requires changes beyond this session's scope,
   AND you document the root cause in the xfail reason string.
```

---

### P-05 · Skipping CodeQL / security scan

**Violation detected when Copilot:**
> Concludes a session without running `codeql_checker`, or says "CodeQL is
> already clean", "no security changes", "skipping security scan".

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-05 (Security scan skipped):
CodeQL scan is MANDATORY before every session close. Run codeql_checker now.
If alerts are found, investigate ALL of them before concluding.
```

---

### P-06 · Incomplete CI log retrieval

**Violation detected when Copilot:**
> Uses only `tail_lines` or a partial log to diagnose failures, or says
> "I couldn't see the full log" without exhausting the available tools.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-06 (Partial log analysis):
You must use get_job_logs with failed_only=true AND run_id to retrieve ALL
failed job summaries. If the log is truncated, retrieve the specific job log
by job_id. Never conclude a diagnosis from a partial log alone.
```

---

### P-07 · TZ-naive datetime usage

**Violation detected when Copilot:**
> Introduces `datetime.now()` (without `timezone.utc`) in new code, or leaves
> TZ-naive calls unfixed after identifying them.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-07 (TZ-naive datetime):
All datetime.now() calls MUST use timezone.utc: datetime.now(timezone.utc).
Run: python3 -c "import pathlib; hits=[str(p) for p in pathlib.Path('src').rglob('*.py') if 'datetime.now()' in p.read_text()]; print(hits)"
Fix ALL remaining TZ-naive calls before concluding.
```

---

### P-08 · record.message AttributeError pattern

**Violation detected when Copilot:**
> Uses `record.message` on a `LogRecord` without formatting (pytest caplog
> returns raw records where `.message` is not set).

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-08 (LogRecord.message):
pytest caplog stores raw LogRecord objects. record.message is NOT set until
Formatter.format() is called. Use caplog.messages (list of str) or
record.getMessage() instead of record.message.
```

---

### P-09 · Committing without trailing-whitespace check

**Violation detected when Copilot:**
> Modifies Markdown or Python files without verifying no trailing whitespace
> was introduced (fast-suite pre-commit hook failure pattern).

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-09 (Trailing whitespace):
Run: git diff --check HEAD before every commit to detect trailing whitespace.
The fast-suite pre-commit hook fails on trailing whitespace in any file type.
```

---

### P-10 · Report without commit

**Violation detected when Copilot:**
> Calls report_progress without having made actual code changes, creating empty
> or trivial commits.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-10 (Empty commit):
Only call report_progress after making verifiable code changes. An empty commit
pollutes the PR history and triggers CI runs unnecessarily.
```

---

### P-11 · Missing import in new code

**Violation detected when Copilot:**
> Introduces code that references `timezone` without importing it, or uses
> `importlib` before importing it at module level.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-11 (Missing import):
Run python3 -m py_compile <changed_files> immediately after every edit to catch
NameError / ImportError at compile time. Do not push uncompiled changes.
```

---

### P-12 · Ignoring DRQ open items

**Violation detected when Copilot:**
> Concludes a session without addressing or documenting open DRQ items listed
> in `docs/tech_debt/research_queue/questions_for_research.md`.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-12 (Open DRQ ignored):
Check docs/tech_debt/research_queue/questions_for_research.md for OPEN items.
Each OPEN DRQ must either be: (a) resolved with a fix, (b) answered in the
research_queue file, or (c) carried forward in the FOLLOWUP_PROMPT with a
direct file:line link.
```

---

### P-13 · Monkeypatching wrong import target

**Violation detected when Copilot:**
> Writes tests that monkeypatch `from module import func` style imports,
> which do NOT intercept calls already bound at module load time.

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-13 (Monkeypatch target mismatch):
Production code MUST use module-reference calling pattern when tests monkeypatch
at module level: import module as _mod; _mod.func(). Never use
`from pkg import func` if the test patches `pkg.func` — the local binding
bypasses the mock. See: src/codex_ml/training/unified_training.py pattern.
```

---

### P-14 · Pickle corruption test uses trailing byte

**Violation detected when Copilot:**
> Corrupts a file's LAST byte to test corruption detection (produces false
> pass because pickle silently ignores trailing null padding).

**Re-alignment prompt:**
```
⚠️ POLICY VIOLATION DETECTED — P-14 (Pickle corruption test):
ALWAYS corrupt a MIDDLE byte: corrupt[len(corrupt)//2] ^= 0xFF.
Pickle serialisation produces trailing null padding — corrupting the last byte
is silently ignored on deserialisation. See: tests/space_traversal/
test_peft_comprehensive/test_checkpoint_integrity.py for correct pattern.
```

---

## §3 · PRE-CLOSE GATE (T-3)

Before the closing CodeQL / security scan, inject this block verbatim:

```
🔴 SESSION COMPLETION CHECKLIST — MANDATORY:

□ 1. CI STATUS: Called list_workflow_runs and confirmed NO in_progress/queued jobs
□ 2. FAILED JOBS: Called get_job_logs for every failed job — 0 unaddressed failures
□ 3. TZ-NAIVE: Ran datetime.now() grep — 0 hits in src/
□ 4. COMPILE CHECK: Ran py_compile on ALL changed files — 0 syntax errors
□ 5. TRAILING WS: Ran git diff --check — 0 trailing whitespace violations
□ 6. CODEBASE POLICY: Read .codex/CODEBASE_AGENCY_POLICY.md — all items addressed
□ 7. DRQ: All OPEN DRQ items carried forward with file:line links in FOLLOWUP_PROMPT
□ 8. FOLLOWUP PROMPT: Created .codex/reports/FOLLOWUP_PROMPT_S{N}_PR{PR}.md with
     ## 🔴 Outstanding Items section and direct file:line links for all open items

Only proceed to CodeQL after ALL boxes are checked.
```

---

## §4 · PROHIBITED STATEMENT REGISTRY

The following phrases are **never acceptable** from GitHub Copilot Agent:

| ID | Prohibited phrase | Policy reference |
|----|-------------------|-----------------|
| X-01 | "These are pre-existing issues" | CODEBASE_AGENCY_POLICY §2 |
| X-02 | "This is not related to my PR" | CODEBASE_AGENCY_POLICY §2 |
| X-03 | "These are out of scope" | CODEBASE_AGENCY_POLICY §2 |
| X-04 | "CI should be green" (unverified) | CI_VERIFICATION §3 |
| X-05 | "I'll skip the CodeQL scan" | CODEBASE_AGENCY_POLICY §5 |
| X-06 | "I cannot access CI logs" | CI_VERIFICATION §1 |
| X-07 | "My changes don't affect security" | CODEBASE_AGENCY_POLICY §5 |
| X-08 | "I'll address this in a follow-up" (without DRQ filing) | DRQ_PROTOCOL §4 |

---

## §5 · ACTIVATION COMMANDS

This agent is invoked using the following commands in PR comments:

| Command | Effect |
|---------|--------|
| `@policy-coach check-plan` | Inject §1 orientation block |
| `@policy-coach check-violation <P-NN>` | Inject re-alignment for pattern P-NN |
| `@policy-coach pre-close` | Inject §3 session completion checklist |
| `@policy-coach full-audit` | Run all three checkpoints in sequence |

---

## §6 · INTEGRATION WITH OTHER AGENTS

| Agent | Integration point |
|-------|------------------|
| `recon-scout-agent.md` | Run BEFORE recon scout to establish policy baseline |
| `ci-testing-agent.md` | Run AFTER ci-testing to verify all failures addressed |
| `security-alert-verification-agent.md` | Run AT SAME TIME as CodeQL check |
| `copilot-agent-prompt-guide.md` | Source document for all prompt fragments |

**Registered in:** `AGENT_REGISTRY.yaml`  
**Run before:** `codeql_checker`, session close  
**Run after:** plan declaration, any T-2 trigger

---

## §7 · SOURCE DOCUMENTS

All prompt fragments in this agent are sourced from:

1. `.codex/docs/COPILOT_AGENT_PROMPT_GUIDE.md` — master prompt guide (14 patterns)
2. `.codex/docs/ACCOUNTABILITY_REPORT_S77.md` — root-cause analysis of repeated violations
3. `.codex/CODEBASE_AGENCY_POLICY.md` — mandatory policy (authoritative)
4. `AGENTS.md` — repository-wide agent documentation

**Version History:**
- v1.0.0 (S78, 2026-02-24): Initial creation — extracted from PR #3344 comment #3948253647
