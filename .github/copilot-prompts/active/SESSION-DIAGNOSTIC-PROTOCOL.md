# Agent Session Diagnostic Protocol (ASDP)

> **Version:** 1.0 | **Established:** 2026-03-17 (S145 / PR #3606)
> **Applies to:** Every GitHub Copilot Coding Agent session on this repository
> **Policy ref:** `.codex/CODEBASE_AGENCY_POLICY.md §0`

---

## Purpose

Every agent session **MUST** begin with this diagnostic protocol before making
any code changes.  It ensures the agent has full situational awareness of the
repository health, avoids working on a broken baseline, and produces a traceable
record of what was known at session start.

Failure to run this protocol is a **§0 violation** per `CODEBASE_AGENCY_POLICY.md`.

---

## Protocol Checklist (§0 Gate)

Run in this exact order.  Do not skip items.

```
[ ] D-00  Run session_bootstrap.py — extract URLs, fetch context, run triage  ← NEW
[ ] D-01  Load stored memories (store_memory recall)
[ ] D-02  Load CODEBASE_AGENCY_POLICY.md
[ ] D-03  Load AGENT_ACCOUNTABILITY_REPORT.md (last 3 sessions)
[ ] D-04  Load CHANGELOG.md ([Unreleased] section)
[ ] D-05  Check open PR comments / review threads
[ ] D-06  Check CI status — branch + base branch
[ ] D-07  Run ci_triage_repro.sh (read-only check pass)
[ ] D-08  Document baseline state in accountability report
```

---

## D-00 — Session Bootstrap (URL Pre-Process) ← Run FIRST

**Why:** Any links in the request body contain critical context (issue bodies,
PR review threads, CI failure logs) that the agent needs before touching code.
Pre-fetching them eliminates the round-trips that would otherwise be needed
mid-session, and surfaces blocking CI failures before any edits are made.

```bash
# If URLs are in a file:
python scripts/ci/session_bootstrap.py --context-file /tmp/session_prompt.txt

# If piping from stdin (CI / agent invocation):
echo "<full session text with github.com URLs>" \
  | python scripts/ci/session_bootstrap.py

# Offline (no token) — still runs triage, skips URL fetching:
python scripts/ci/session_bootstrap.py --offline

# Full JSON output for downstream tools:
python scripts/ci/session_bootstrap.py \
  --context-file /tmp/session.txt \
  --json-out .codex/session_context.json

# Skip triage (fast context-only, useful when triage was just run):
python scripts/ci/session_bootstrap.py --context-file /tmp/session.txt --skip-triage
```

**Output written to:**
- `.codex/session_context_latest.md` — always overwritten; read this at session start
- `.codex/sessions/session_<ISO>.md` — archive copy per session

**The digest contains:**
1. Structured data for every GitHub URL found (issue/PR/workflow/review)
2. Unresolved review threads with file:line + author + comment body
3. Failed CI job names + first error lines from logs
4. All 7 triage check results
5. Pre-filled §0 checklist snippet for the accountability report

**What to look for in the digest:**
- `🚨 BLOCKING ISSUES` section — fix these before any other work
- `❌ Failed checks` in PR entries — these are the CI gates to clear
- `💬 Unresolved review thread(s)` — these must all be addressed
- Triage rows with `❌` — see `docs/ci/CI_TRIAGE_REPRO_S145.md` for each fix



**Why:** Recent memories encode known bugs, patterns, and CI policy that are
not visible from code alone.  Missing a stored memory is the most common cause
of re-introducing known bugs.

```bash
# No shell command — use the store_memory tool's recall before any code change.
# In agent context: "retrieve memories for Aries-Serpent/_codex_"
```

**What to look for:**
- Session IDs (S1xx) and what was fixed/changed
- CI policy rules (e.g., "never add pip cache when no packages installed")
- Known baseline values (`.mypy_baseline`, coverage thresholds)
- Recurring failure patterns

---

## D-02 — Load Codebase Agency Policy

```bash
cat .codex/CODEBASE_AGENCY_POLICY.md
```

**Key rules to internalise:**
- ALL issues found must be fixed — origin/PR/session is irrelevant
- Every commit must touch `CHANGELOG.md` (REQ-5) and `AGENT_ACCOUNTABILITY_REPORT.md` (REQ-4)
- No deferral language in any file or commit message

---

## D-03 — Load Recent Accountability Sessions

```bash
# Read last 3 sessions from accountability report
grep -n "^## SESSION SUMMARY" docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md | tail -3
# Then read each referenced section
```

**What to look for:**
- Work completed in prior session (avoid duplicate effort)
- Open items or carry-forwards
- Lessons learned / violations acknowledged

---

## D-04 — Load Unreleased CHANGELOG

```bash
sed -n '/^## \[Unreleased\]/,/^## \[/p' CHANGELOG.md | head -60
```

**What to look for:**
- Most recent S-ID and which files were touched
- Any "TODO" or incomplete items in the unreleased section

---

## D-05 — Check Open PR Comments & Review Threads

Use GitHub MCP tools (not bash):

```
github-mcp-server-pull_request_read method=get_review_comments
github-mcp-server-pull_request_read method=get_comments
```

**What to look for:**
- Unresolved review threads (must all be addressed)
- New `@copilot continue` or `@copilot fix` directives
- Auto-generated self-healing escalation messages

---

## D-06 — Check CI Status

Use GitHub MCP tools (not bash):

```
github-mcp-server-actions_list method=list_workflow_runs  branch=<current>
github-mcp-server-actions_list method=list_workflow_runs  branch=<base>
```

**If failures found:**

```bash
# Retrieve failure logs:
github-mcp-server-get_job_logs  failed_only=true  run_id=<ID>
```

**Classification:**

| Pattern | Likely Cause | First Command |
|---------|-------------|---------------|
| `I001` | unsorted imports | `ruff check --select I --fix .` |
| `E302/E303` | blank lines | `ruff check --select E --fix .` |
| `SC2072` | decimal comparison | Replace `[ x \> y ]` with `awk` |
| `mypy regression` | baseline stale | `python scripts/ci/mypy_baseline.py` |
| `chr(34) bug` | key obfuscation | See `docs/ci/CI_TRIAGE_REPRO_S145.md#check-5` |
| `threshold mismatch` | dashboard ≠ enforcement | Compare `s+0` expr vs `threshold =` |
| `auto-fix pattern N` | see pattern list | `python scripts/ci/auto_fix_common_issues.py --pattern N` |

---

## D-07 — Run ci_triage_repro.sh

```bash
bash scripts/ci/ci_triage_repro.sh
```

Expected output when baseline is healthy:
```
✅ PASS — 1_actionlint: 0 errors
✅ PASS — 2_ruff_i001: 0 issues
✅ PASS — 3_mypy_baseline: 282 <= 282
✅ PASS — 4_autofix: 0 issues
✅ PASS — 5_telemetry: all 3 fields correct
✅ PASS — 6_threshold: both=99.7
✅ PASS — 7_changelog: consistent

All checks passed ✅
```

**If any check fails**, fix it before proceeding with session work.
Use `--fix` mode for auto-remediation, then re-run to verify:

```bash
bash scripts/ci/ci_triage_repro.sh --fix
bash scripts/ci/ci_triage_repro.sh         # must be clean before continuing
```

---

## D-08 — Document Baseline State

Add a pre-flight entry to `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`:

```markdown
## SESSION SUMMARY — <ISO timestamp> SESSION <branch> S<NNN> (<PR title>)

### Pre-flight Checklist (§0 CODEBASE_AGENCY_POLICY.md)
- [x] D-01 Memories loaded — last session: S<N>
- [x] D-02 CODEBASE_AGENCY_POLICY.md reviewed
- [x] D-03 Accountability report loaded (last 3 sessions)
- [x] D-04 CHANGELOG [Unreleased] reviewed
- [x] D-05 PR comments reviewed — N open threads
- [x] D-06 CI status: <branch>=<green/red>, <base>=<green/red>
- [x] D-07 ci_triage_repro.sh → all 7 checks passed / N failed (listed below)
- [x] D-08 Baseline documented here
```

---

## CI Failure Triage Quick-Reference

Complete root-cause and repro steps: `docs/ci/CI_TRIAGE_REPRO_S145.md`

| Check | Repro | Fix |
|-------|-------|-----|
| actionlint SC2072 | `ci_triage_repro.sh --check 1` | Replace `[ x \> y ]` with awk |
| ruff I001 | `ci_triage_repro.sh --check 2` | `ruff check --select I --fix .` |
| mypy baseline stale | `ci_triage_repro.sh --check 3` | `python scripts/ci/mypy_baseline.py --update` |
| auto-fix patterns | `ci_triage_repro.sh --check 4` | `auto_fix_common_issues.py --fix` |
| telemetry chr(34) | `ci_triage_repro.sh --check 5` | Re-encode b64 with plain string keys |
| threshold mismatch | `ci_triage_repro.sh --check 6` | Align awk expr ≥ enforcement value |
| changelog cross-ref | `ci_triage_repro.sh --check 7` | Remove cross-PR bullets |

---

## Cognitive Brain Knowledge Capture

After each session, store resolutions using `store_memory`:

```
store_memory(
  subject   = "<area>",
  fact      = "S<NNN>: <one-line description of resolution>",
  citations = "<file:line> — PR #<N> S<NNN>",
  reason    = "<why this matters for future sessions>",
  category  = "general"
)
```

**What qualifies for a knowledge fact:**
- A recurring failure pattern and its fix
- A CI gate rule or policy constraint
- A non-obvious file/function relationship
- A baseline value that must be maintained

**What does NOT qualify:**
- One-off cosmetic fixes
- Changes that are obvious from reading the code
- Secrets, credentials, or PII

---

## Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-03-17 | S145/copilot | Initial protocol — established from S145 triage session |
