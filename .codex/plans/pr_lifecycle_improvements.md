# PR Lifecycle Automation Improvement Plan

> **Created:** 2026-04-03 (S293)  
> **Branch:** `0D_base_`  
> **Owner:** @mbaetiong  
> **Tracked by:** Issue [#3853](https://github.com/Aries-Serpent/_codex_/issues/3853)  
> **Status key:** ✅ Done · 🔄 In progress · 📋 Planned · 💡 Future

This plan captures every improvement identified during the S293 PR_LIFECYCLE review.
Each item is self-contained — a future Copilot session can start at any Priority level
and execute the item using only the information in this file.

---

## How to Resume This Plan

```
SESSION START CHECKLIST:
1. Load docs/ci/PR_LIFECYCLE.md
2. Load .codex/CODEBASE_AGENCY_POLICY.md
3. Run: python scripts/ci/pda_failure_logger.py summarize
4. Pick the highest-priority 📋 Planned item below
5. Implement → verify → commit → update status in this file
6. Run /tmp/actionlint .github/workflows/*.yml before every push
```

---

## Priority 1 — Critical Bugs (breaks automation chain)

### P1-A ✅ S221 guard blind to `validate.yml` rescue marker
**File:** `.github/workflows/copilot-agent-checkin.yml`  
**Problem:** `rescueMarkerRe` matched `ci-rescue:NNN` and `ci-rescue:NNN:sha` but NOT
`ci-rescue-sha:NNN:sha` (format used by `validate.yml`). The S221 missed-trigger guard
never found validate.yml rescue comments → Copilot sessions were not re-triggered when
validate.yml rescue was the only rescue present.  
**Fix applied S293:**
```js
// Before:
const rescueMarkerRe = /<!--\s*ci-rescue:\d+(?::[0-9a-f]+)?\s*-->/;
// After:
const rescueMarkerRe = /<!--\s*ci-rescue(?:-sha)?:\d+(?::[0-9a-f]+)?\s*-->/;
```
Also updated `markerMatch` extractor regex on the same pattern.  
**Verification:** `node -e "const r=/<!--\s*ci-rescue(?:-sha)?:\d+(?::[0-9a-f]+)?\s*-->/; ['<!-- ci-rescue:3854 -->','<!-- ci-rescue:3854:abc123 -->','<!-- ci-rescue-sha:3854:abc123 -->'].forEach(s=>console.log(r.test(s),s))"`  
**PDA pattern:** `RP-S221-BLIND-MARKER`

---

### P1-B ✅ `test-rag.yml` rescue PATCH causes 403 when token rotates
**File:** `.github/workflows/test-rag.yml`  
**Problem:** PR-scoped marker `<!-- ci-rescue:{pr} -->` meant all SHAs appended to one
comment. When `CODEX_MASTER_KEY` expired after the initial POST (by `@mbaetiong`), the
PATCH (403 — can't edit another user's comment) silently fell through to POST as
`github-actions[bot]`, breaking the Copilot trigger chain.  
**Fix applied S293:** Changed to SHA-scoped marker `<!-- ci-rescue-sha:{pr}:{sha12} -->`,
removed PATCH/append entirely — each SHA creates exactly one fresh comment (idempotent on reruns).  
**Verification:** `grep -n "ci-rescue-sha\|PATCH\|append" .github/workflows/test-rag.yml`  
**PDA pattern:** `RP-RESCUE-IDENTITY`

---

### P1-C ✅ `actionlint-audit.yml` inline rescue step posted as bot
**File:** `.github/workflows/actionlint-audit.yml`  
**Problem:** `actions/github-script@v8` step had no `github-token:` key — used default
`github.token` (= `github-actions[bot]`). Copilot ignores `@copilot` from bots.  
**Fix applied S293:** Added `github-token: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || secrets.GITHUB_TOKEN }}`  
**Verification:** `grep "github-token" .github/workflows/actionlint-audit.yml`  
**PDA pattern:** `RP-RESCUE-IDENTITY`

---

### P1-D ✅ SC2269 self-assignment in `workflow-execution-gate.yml`
**File:** `.github/workflows/workflow-execution-gate.yml` line ~328  
**Problem:** `PR="${PR}"` in "Post fast-forward result comment" step — shellcheck SC2269.
Caused `actionlint-audit.yml` to fail on every push.  
**Fix applied S293:** Removed the redundant line.  
**Verification:** `/tmp/actionlint .github/workflows/workflow-execution-gate.yml`  
**PDA pattern:** `RP-ACTIONLINT-SC2269`

---

## Priority 2 — High Impact (automation reliability)

### P2-A 📋 `copilot-agent-session-done.yml` creates duplicate comments
**File:** `.github/workflows/copilot-agent-session-done.yml`  
**Problem (§16.4 🔴 High):** Fires on `workflow_run` completion for every watcher job.
Uses `createComment` (not upsert-by-marker) → each job completion creates a new comment.
Multiple parallel job completions → 3–4 duplicate `@copilot review` comments per push.  
**Target:** Replace all `createComment` calls with upsert-by-marker pattern.
Use marker `<!-- session-done-dedup:{sha12} -->`.  
**Implementation guide:**
```js
// In each "Post @copilot review" step:
const MARKER = `<!-- session-done-dedup:${sha.slice(0,12)} -->`;
// Find existing by marker, PATCH if found, POST if not
// (same pattern as comment-review-gate.yml rescue-comment job)
```
**Effort:** Medium (2–3 steps to update)  
**Verification:** Push a commit and confirm only ONE session-done comment appears.

---

### P2-B 📋 `comment-review-gate.yml` cascade risk on `issue_comment`
**File:** `.github/workflows/comment-review-gate.yml`  
**Problem (§16.4 🟡 Medium):** When the gate posts its checklist comment (via `github-actions[bot]`),
this `issue_comment` event re-triggers the gate. The `scan-and-post` job's `if:` condition
filters to `mbaetiong`-authored comments only, so a direct infinite loop is prevented.
BUT: if `CODEX_MASTER_KEY` expires and the gate comment is posted as `github-actions[bot]`,
the filter doesn't apply and a cascade becomes possible.  
**Target:** Strengthen the `issue_comment` guard to skip when
`github.event.comment.user.login` ends with `[bot]` OR equals known bot logins.  
**Implementation guide:**
```yaml
if: |
  (github.event_name == 'pull_request' || github.event_name == 'pull_request_review') ||
  (github.event_name == 'issue_comment' &&
   github.event.issue.pull_request != null &&
   github.event.comment.user.login == 'mbaetiong' &&
   !endsWith(github.event.comment.user.login, '[bot]'))
```
**Effort:** Low (single `if:` condition change)  
**Verification:** Post a bot comment on a test PR and verify gate does NOT re-run.

---

### P2-C 📋 Phase detection output in `workflow-execution-gate.yml`
**File:** `.github/workflows/workflow-execution-gate.yml`  
**Problem:** The document describes 4 PR phases (Pre-Approval → WEC-Approved → Agent-Active
→ Ready-to-Review) but the WEC gate doesn't output the current phase. Debugging requires
manual inspection of which WEC items are checked.  
**Target:** Add a `detect-phase` step that:
1. Reads the PR body WEC checklist
2. Outputs `phase` = `pre-approval` | `wec-approved` | `agent-active` | `ready-to-review`
3. Includes phase in the gate summary comment body  
**Implementation guide:**
```python
# Phase detection logic:
always_required = {'pre-merge-validation.yml', 'comment-review-gate.yml', ...}
cheap_gates = {'validate.yml', 'mypy-baseline.yml', 'actionlint-audit.yml'}
# If only always_required checked: pre-approval
# If cheap_gates checked: wec-approved
# If agent-auth-delegation approved: agent-active
# If all required checks green: ready-to-review
```
**Effort:** Medium (new step + output variable)  
**Verification:** Check gate summary comment includes phase label.

---

### P2-D 📋 Mermaid diagram §8 inaccurately shows `ci-rescue.yml` as Tier 1
**File:** `docs/ci/PR_LIFECYCLE.md` §8 (lines ~386–455)  
**Problem:** Flowchart shows `F →|Fail| K[ci-rescue.yml posts 🚨 rescue comment]` as if
`ci-rescue.yml` fires directly when a check fails. In reality it's Tier 2 (needs approval).
The correct Tier 1 path is `validate.yml` / `test-rag.yml` / `actionlint-audit.yml` rescue jobs.  
**Target:** Update the mermaid node `K` to:
```
K[TIER 1: validate.yml / test-rag.yml / actionlint-audit.yml\npost SHA-scoped @copilot rescue comment]
K2[TIER 2 (needs approval): ci-rescue.yml\ndeep RCA + RP-pattern match]
```
**Effort:** Low (mermaid edit only, no workflow changes)  
**Verification:** Render the mermaid diagram and confirm Tier 1/2 distinction is visible.

---

## Priority 3 — Medium Impact (noise reduction)

### P3-A 📋 `workflow_run` fan-out: collapse same-SHA failures into one RCA
**File:** `.github/workflows/ci-rescue.yml`  
**Problem (§16.6 rec #6):** When ≥5 `workflow_run` failures fire for the same SHA within
2 minutes, each triggers a separate `ci-rescue.yml` run. While each uses the upsert marker
`<!-- ci-rescue:{pr}:sha-{sha12} -->`, rapid concurrent fires can create multiple comments
before any run sees the existing marker (race condition).  
**Target:** Add a 90-second initial delay in `ci-rescue.yml` with a check: if the SHA-scoped
marker already exists when the delay expires, skip posting a new comment.  
**Implementation guide:**
```yaml
- name: Dedup delay (collapse concurrent failures)
  run: |
    sleep 90
    # Then check if marker already exists before posting
```
**Effort:** Low (add sleep + marker check)  
**Verification:** Trigger 3 simultaneous failures on same SHA; confirm only 1 RCA comment.

---

### P3-B 📋 `auto_fix_common_issues.py` CHANGELOG staleness check
**File:** `scripts/ci/auto_fix_common_issues.py`  
**Problem (§14.1 ongoing):** `agent-auth-delegation.yml` cognitive pre-flight fails when
`CHANGELOG.md` hasn't been updated in the current session. There's no auto-fix for this.  
**Target:** Add Pattern 24 that checks:
1. Whether `CHANGELOG.md` has an entry under `## [Unreleased]` updated within the last
   24 hours (using `git log --since=1.day -- CHANGELOG.md`)
2. If stale: writes a templated `### Fixed (S___)` entry with `<FILL_IN>` placeholder
3. Outputs a warning that the agent must fill in the entry  
**Implementation guide:**
```python
# Pattern 24: CHANGELOG staleness
import subprocess
result = subprocess.run(['git', 'log', '--since=1.day', '--oneline', '--', 'CHANGELOG.md'],
                       capture_output=True, text=True)
if not result.stdout.strip():
    # CHANGELOG not updated today — issue warning
    issues.append(Issue(pattern=24, type='changelog_stale', auto_fix_available=False,
                        message='CHANGELOG.md not updated in last 24h'))
```
**Effort:** Medium (new pattern in auto_fix_common_issues.py + tests)  
**Verification:** `python scripts/ci/auto_fix_common_issues.py --check-only --pattern 24`

---

### P3-C 📋 Proactive CI monitor: per-PR-per-day throttle
**File:** `scripts/ci/proactive_ci_monitor.py`  
**Problem (§16.6 rec #5):** The 30-min schedule can post 2+ `@copilot` comments per hour
on a long-failing PR. No per-PR daily cap exists.  
**Target:** Add a state file `.codex/ci_monitor_state.json` tracking `{pr_number: {date: "YYYY-MM-DD", count: N}}`.
Cap at 5 proactive posts per PR per calendar day.  
**Implementation guide:**
```python
STATE_FILE = Path('.codex/ci_monitor_state.json')
def check_and_increment_daily_cap(pr_number: int, cap: int = 5) -> bool:
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    today = datetime.date.today().isoformat()
    key = str(pr_number)
    entry = state.get(key, {})
    if entry.get('date') != today:
        entry = {'date': today, 'count': 0}
    if entry['count'] >= cap:
        return False  # cap reached
    entry['count'] += 1
    state[key] = entry
    STATE_FILE.write_text(json.dumps(state, indent=2))
    return True
```
**Effort:** Medium  
**Verification:** Mock 6 calls in one day; confirm only 5 posts.

---

### P3-D 📋 Add `ci-rescue-sha` to §21.9 rescue marker reference
**File:** `docs/ci/PR_LIFECYCLE.md` §21.9  
**Problem:** The marker reference table in §21.9 currently shows `test-rag.yml` with the
old PR-scoped `<!-- ci-rescue:{pr_number} -->`. After P1-B fix it now uses
`<!-- ci-rescue-sha:{pr}:{sha12} -->`.  
**Target:** Update the §21.9 table row for `test-rag.yml`.  
**Effort:** Trivial (doc update only, no workflow change)  
**Verification:** `grep "ci-rescue-sha" docs/ci/PR_LIFECYCLE.md | grep "test-rag"`

---

## Priority 4 — Enhancement (future scope)

> Items in P4 are aspirational and require design work before implementation.
> They should be evaluated against the Cognitive Brain roadmap before scheduling.



### P4-A 💡 Phase-gated WEC auto-check
**Concept:** When the WEC gate detects the PR is in `pre-approval` phase and all cheap gates
(`validate.yml`, `mypy-baseline.yml`, `actionlint-audit.yml`) are already green, automatically
suggest (or auto-check) the medium-cost gates in the PR body comment.  
**Depends on:** P2-C (phase detection)  
**Effort:** High

---

### P4-B 💡 `comment-review-gate.yml` auto-extract blocking comment context
**Concept (§14.1 ongoing):** When the gate fails, extract the blocking comment ID, author,
and first 200 chars. Append a structured reply template directly to the gate failure comment:
```
## 🔴 Blocking comments requiring reply:
| Comment | Author | Summary | Reply format |
| #12345 | @mbaetiong | "Please fix the..." | "Fixed at <SHA>: ..." |
```
This removes the agent's need to manually scan the PR for outstanding comments.  
**Effort:** High (requires parsing comment content)

---

### P4-C 💡 Global per-PR hourly comment budget cap
**Concept (§16.6 rec #3):** If a PR receives >50 automation comments in one hour, suppress
non-critical posts (info/status only) for 30 minutes.  
**Implementation:** Shared state in repo variable `COPILOT_PR_COMMENT_COUNTS` (JSON).
Each comment-posting workflow checks before posting.  
**Effort:** Very High (cross-workflow coordination)

---

### P4-D 💡 Session identity attestation in rescue comments
**Concept:** Each rescue comment should include a small block:
```
<!-- rescue-token-identity: mbaetiong -->
```
that the S221 guard and Copilot can verify. If the identity is `github-actions[bot]`,
the session-done workflow posts an admin alert instead of an `@copilot` retrigger.  
**Effort:** Medium

---

### P4-E 💡 Tier 2 auto-approval for trusted SHA patterns
**Concept:** When all Tier 1 rescue indicators show a known-safe pattern (e.g. RP-007
detect-secrets staleness), automatically approve the Tier 2 `workflow_run` run via
the `gh run approve` command in `agent-auth-delegation.yml`.  
**Risk:** High — auto-approving `workflow_run` runs with `contents: write` requires
careful actor + pattern validation.  
**Effort:** Very High

---

## Improvement Plan Status Summary

| ID | Title | Priority | Status | Session |
|----|-------|----------|--------|---------|
| P1-A | S221 guard regex | P1 | ✅ Done | S293 |
| P1-B | test-rag.yml SHA-scoped marker | P1 | ✅ Done | S293 |
| P1-C | actionlint-audit.yml github-token | P1 | ✅ Done | S293 |
| P1-D | SC2269 self-assignment | P1 | ✅ Done | S293 |
| P2-A | session-done upsert dedup | P2 | 📋 Planned | — |
| P2-B | comment-gate cascade guard | P2 | 📋 Planned | — |
| P2-C | Phase detection output | P2 | 📋 Planned | — |
| P2-D | Mermaid diagram Tier accuracy | P2 | 📋 Planned | — |
| P3-A | fan-out RCA dedup delay | P3 | 📋 Planned | — |
| P3-B | CHANGELOG staleness auto-fix | P3 | 📋 Planned | — |
| P3-C | proactive monitor daily cap | P3 | 📋 Planned | — |
| P3-D | §21.9 marker table update | P3 | 📋 Planned | — |
| P4-A | Phase-gated WEC auto-check | P4 | 💡 Future | — |
| P4-B | comment-gate context extraction | P4 | 💡 Future | — |
| P4-C | Global hourly comment budget | P4 | 💡 Future | — |
| P4-D | Session identity attestation | P4 | 💡 Future | — |
| P4-E | Tier 2 auto-approval safe patterns | P4 | 💡 Future | — |

---

## Session Resumption Prompt

When picking up this plan, start a new Copilot session with:

```
@copilot Resume .codex/plans/pr_lifecycle_improvements.md — implement the next
📋 Planned item in priority order. Start with P2-A (session-done upsert dedup).

Pre-session loads required:
1. docs/ci/PR_LIFECYCLE.md
2. .codex/CODEBASE_AGENCY_POLICY.md
3. .codex/plans/pr_lifecycle_improvements.md (this file)
4. python scripts/ci/pda_failure_logger.py summarize

After implementing each item:
1. Run /tmp/actionlint .github/workflows/*.yml
2. Update the Status column in this file
3. Commit with message: "feat(automation): <item-title> [<ID>]"
4. Report progress
```

---

## Cognitive Brain Objective Cross-Reference

Every item in this plan maps to one or more Cognitive Brain objectives.
The Cognitive Brain architecture has four layers: **Perception → Decision → Action → AfterMath**.
All CI automation improvements ultimately serve these layers.

### Layer Mapping

| Plan ID | CB Layer | CB Objective | Source Document |
|---------|----------|-------------|-----------------|
| P1-A | Action | S221 guard enables rescue re-triggers → agent sessions restart | `COGNITIVE_BRAIN_LIVE_STATUS.md` §Process Transparency |
| P1-B | Action | RAG test-rag rescue chain reliability → supports CB-002 RAG coverage | `AGENT_ACCOUNTABILITY_REPORT.md` CB-002 |
| P1-C | Action | actionlint-audit.yml identity fix → CB-003 compliance | `AGENT_ACCOUNTABILITY_REPORT.md` CB-003 |
| P1-D | Action | SC2269 removal → CB-003 actionlint compliance | `AGENT_ACCOUNTABILITY_REPORT.md` CB-003 |
| P2-A | AfterMath | Session-done dedup → clean AfterMath session completion detection | `cognitive_brain_phase_implementation.md` Pre-commit 13-16 |
| P2-B | Perception | Comment-gate cascade guard → clean perception input, no self-noise | `COGNITIVE_BRAIN_LIVE_STATUS.md` §Process Transparency |
| P2-C | Decision | Phase detection output → feeds Decision Engine with PR lifecycle state | `cognitive_brain_phase_implementation.md` Pre-commit 9-12 |
| P2-D | Perception | Accurate Mermaid diagram → corrects perception model for agents reading docs | `COGNITIVE_BRAIN_LIVE_STATUS.md` §Documentation Gaps |
| P3-A | Perception | Fan-out dedup → consolidated failure signal for ci.health.analyzer (CB-006) | `AGENT_ACCOUNTABILITY_REPORT.md` CB-006 |
| P3-B | AfterMath | CHANGELOG auto-fix → REQ-4/REQ-5 pre-flight (agent-auth-delegation) | `COGNITIVE_BRAIN_LIVE_STATUS.md` §Next Milestones |
| P3-C | AfterMath | Proactive monitor cap → CB-006 proactive_ci_monitor improvement | `AGENT_ACCOUNTABILITY_REPORT.md` CB-006 |
| P3-D | Perception | §21.9 marker table accuracy → correct perception of rescue state | `docs/ci/PR_LIFECYCLE.md` §21.9 |
| P4-A | Decision | Phase-gated WEC → Decision Engine gates expensive workflows by phase | `cognitive_brain_phase_implementation.md` Decision Engine |
| P4-B | Perception | Comment context extraction → structured perception of unresolved blockers | `COGNITIVE_BRAIN_LIVE_STATUS.md` §Process Transparency |
| P4-C | Action | Global comment budget → Action throttling (rate-limit controls §16) | `docs/ci/PR_LIFECYCLE.md` §16.3 |
| P4-D | AfterMath | Session identity attestation → AfterMath knows WHO closed the loop | `cognitive_brain_phase_implementation.md` AfterMath Evaluator |
| P4-E | Decision | Tier 2 auto-approval → Decision Engine approves safe patterns autonomously | `COGNITIVE_BRAIN_PRODUCTION_ROADMAP.md` Phase 8.3 |
| P5-A–H | All layers | Open milestones from COGNITIVE_BRAIN_LIVE_STATUS.md | See P5 section below |

---

## Priority 5 — Open Cognitive Brain Milestones (from LIVE_STATUS)

> These items come directly from `.codex/plans/COGNITIVE_BRAIN_LIVE_STATUS.md` §Next Milestones
> (last updated 2026-03-30). They were not in the original improvement plan because they are
> architectural/infrastructure concerns rather than PR lifecycle automation concerns.
> They are included here so a future session has a single complete backlog.

### P5-A 📋 Create `docs/admin/D_ACTIVATION_CHECKLIST.md`
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🔴 High  
**CB Layer:** Decision (gates E→D transition)  
**Problem:** No formal checklist documents what a human admin must do to activate the D model.
The 5/5 E→D gate conditions all pass, but human activation is still pending because the steps
are not documented anywhere actionable.  
**Target:** Create `docs/admin/D_ACTIVATION_CHECKLIST.md` with:
- Pre-activation checklist (all 5 gate conditions verified)
- GitHub Actions steps (approve `genesis-bootstrap.yml`, set `SAFE_MODE=False`)
- Post-activation verification commands
- Rollback procedure  
**Effort:** Medium (documentation, 1-2h)  
**Verification:** `test -f docs/admin/D_ACTIVATION_CHECKLIST.md && echo "✅"`

---

### P5-B 📋 Trigger FAISS index rebuild post-merge
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🔴 High  
**CB Layer:** Perception (FAISS corpus feeds orchestrator_routing.py)  
**Problem:** `orchestrator_routing.py` falls back to keyword search because `.faiss` binary
is not seeded in CI. The first-run agents that depend on semantic routing get degraded results.  
**Target:** After each merge to `0D_base_`, automatically trigger `embedding-index-rebuild.yml`
via a `workflow_run` trigger on the merge commit.  
**Implementation guide:**
```yaml
# In embedding-index-rebuild.yml, add trigger:
on:
  workflow_run:
    workflows: ["Merge to 0D_base_"]   # or the actual merge workflow name
    types: [completed]
    branches: [0D_base_]
```
**Effort:** Low (add trigger, 30min)  
**Verification:** After next merge, confirm FAISS index is rebuilt (no "keyword fallback" log).

---

### P5-C 📋 Reduce `COPILOT_ACTIVE_SESSION` TTL from 4h → 1h
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🔴 High  
**CB Layer:** Action (session management)  
**Problem:** When a Copilot session is queued and another session finishes, the 4h TTL means
the new session waits up to 4 hours before the queue clears. 1h is the practical max session length.  
**Target:** Update the `COPILOT_ACTIVE_SESSION` variable or the workflow logic that reads it
to use 3600 seconds (1h) instead of 14400 seconds (4h).  
**Files to check:** `copilot-agent-checkin.yml`, `copilot-agent-session-done.yml`,
any workflow that reads `COPILOT_ACTIVE_SESSION`.  
**Effort:** Low (variable update or workflow constant, 30min)  
**Verification:** `grep -rn "COPILOT_ACTIVE_SESSION\|14400\|TTL" .github/workflows/`

---

### P5-D 📋 Fix SC2086/SC2129 in `admin_setup_verification.yml`
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🟡 Medium  
**CB Layer:** Action (actionlint compliance — clears persistent audit failures)  
**Problem:** `admin_setup_verification.yml` lines 57 and 107 have unquoted variable
expansions (SC2086) and `echo` >> append patterns (SC2129). These cause `actionlint-audit.yml`
to fail on every run even after CB-003 fixes.  
**Fix:** Quote variables: `"${VAR}"` not `${VAR}`. Replace `echo X >> file` with
`printf '%s\n' X >> file` for SC2129.  
**Effort:** Low (targeted sed, 20min)  
**Verification:** `/tmp/actionlint .github/workflows/admin_setup_verification.yml`

---

### P5-E 📋 Add `pre-commit-failure` CI pattern to pattern library
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🟡 Medium  
**CB Layer:** Perception (ci.health.analyzer pattern recognition)  
**Problem:** `iterative-self-healing-ci.yml` classifies pre-commit validation failures as
"unknown" pattern because `.codex/patterns/ci_failure_patterns.yaml` has no entry for it.
This means CB-006's `ci.health.analyzer` gets no signal from pre-commit failures.  
**Target:** Add entry to `.codex/patterns/ci_failure_patterns.yaml`:
```yaml
- id: RP-PRECOMMIT-FAILURE
  pattern: "pre-commit.*failed|detect-secrets.*exit.*3|end-of-file-fixer.*fixed"
  category: code-fix-required
  fix_template: "pre-commit run --all-files; git add -A && git commit --amend --no-edit"
  auto_fix: true
  verification_cmd: "pre-commit run --all-files"
```
**Effort:** Low (YAML addition + test, 20min)  
**Verification:** `python scripts/ci/pda_failure_logger.py summarize --pattern-id RP-PRECOMMIT-FAILURE`

---

### P5-F 📋 Wire `auto_promote_tier.py` into chatops `/copilot tier-promote`
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🟡 Medium  
**CB Layer:** Decision (autonomous tier promotion)  
**Problem:** `auto_promote_tier.py` is deployed but not wired into the chatops command
`/copilot tier-promote`. Tier promotion currently requires manual script execution.  
**Target:** Add a chatops handler in `chatops_copilot_trigger.yml` that:
1. Parses `/copilot tier-promote <agent-name>`
2. Calls `python scripts/cognitive/auto_promote_tier.py --agent <name> --dry-run` first
3. On confirmation: removes `--dry-run` and commits the registry update  
**Effort:** Medium (chatops parser + workflow step, 2h)  
**Verification:** Post `/copilot tier-promote` comment on a test PR.

---

### P5-G 📋 Link 5 ADRs from `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` Section 12
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🟡 Medium  
**CB Layer:** Perception (documentation completeness for agent context loading)  
**Problem:** 5 Architecture Decision Records (ADRs) in `docs/arch/ADR-*.md` are not linked
from `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` Section 12. Agents loading context miss these decisions.  
**Target:** Find all `docs/arch/ADR-*.md` files and add linked references in Section 12.  
**Effort:** Low (find + edit, 20min)  
**Verification:** `grep -c "ADR-" docs/AGENTIC_REPO_SYSTEM_GUIDE.md`

---

### P5-H 📋 Sprint 2: Top-3 unknown CI patterns → `collect_telemetry.py`
**Source:** COGNITIVE_BRAIN_LIVE_STATUS.md 🟡 Medium  
**CB Layer:** Perception (telemetry classification improvements)  
**Problem:** A significant portion of CI failures (est. ~40%) are classified as "unknown"
by the telemetry classifier. Sprint 2 of the unknown-bucket reduction campaign targets
identifying the top-3 unknown patterns and adding classifiers for them.  
**Related:** `telemetry-classifier-agent` custom agent; `scripts/ci/collect_telemetry.py`  
**Target:** Run `telemetry-classifier-agent` to identify top-3 unknown patterns,
add classifier patches to `collect_telemetry.py`, verify unknown bucket drops.  
**Effort:** Medium (agent run + patch + verification, 1h)  
**Verification:** `python scripts/ci/collect_telemetry.py --summary | grep "unknown"`

---

## Updated Status Summary (includes P5)

| ID | Title | Priority | CB Layer | Status | Session |
|----|-------|----------|----------|--------|---------|
| P1-A | S221 guard regex | P1 | Action | ✅ Done | S293 |
| P1-B | test-rag SHA-scoped marker | P1 | Action | ✅ Done | S293 |
| P1-C | actionlint-audit github-token | P1 | Action | ✅ Done | S293 |
| P1-D | SC2269 self-assignment | P1 | Action | ✅ Done | S293 |
| P2-A | session-done upsert dedup | P2 | AfterMath | 📋 Planned | — |
| P2-B | comment-gate cascade guard | P2 | Perception | 📋 Planned | — |
| P2-C | Phase detection output | P2 | Decision | 📋 Planned | — |
| P2-D | Mermaid diagram Tier accuracy | P2 | Perception | 📋 Planned | — |
| P3-A | fan-out RCA dedup delay | P3 | Perception | 📋 Planned | — |
| P3-B | CHANGELOG staleness auto-fix | P3 | AfterMath | 📋 Planned | — |
| P3-C | proactive monitor daily cap | P3 | AfterMath | 📋 Planned | — |
| P3-D | §21.9 marker table update | P3 | Perception | ✅ Done | S293 |
| P4-A | Phase-gated WEC auto-check | P4 | Decision | 💡 Future | — |
| P4-B | comment-gate context extraction | P4 | Perception | 💡 Future | — |
| P4-C | Global hourly comment budget | P4 | Action | 💡 Future | — |
| P4-D | Session identity attestation | P4 | AfterMath | 💡 Future | — |
| P4-E | Tier 2 auto-approval safe patterns | P4 | Decision | 💡 Future | — |
| P5-A | D_ACTIVATION_CHECKLIST.md | P5/🔴High | Decision | 📋 Planned | — |
| P5-B | FAISS index rebuild post-merge | P5/🔴High | Perception | 📋 Planned | — |
| P5-C | COPILOT_ACTIVE_SESSION TTL 4h→1h | P5/🔴High | Action | 📋 Planned | — |
| P5-D | SC2086 admin_setup_verification | P5/🟡Med | Action | 📋 Planned | — |
| P5-E | pre-commit-failure CI pattern | P5/🟡Med | Perception | 📋 Planned | — |
| P5-F | auto_promote_tier chatops wiring | P5/🟡Med | Decision | 📋 Planned | — |
| P5-G | ADR links in system guide §12 | P5/🟡Med | Perception | 📋 Planned | — |
| P5-H | Sprint 2 unknown CI patterns | P5/🟡Med | Perception | 📋 Planned | — |

---

## Next Session Priority Order (recommended)

```
1. P5-A — D_ACTIVATION_CHECKLIST.md (🔴 High, 1-2h, unblocks D model activation)
2. P5-C — COPILOT_ACTIVE_SESSION TTL (🔴 High, 30min, reduces queue wait)
3. P2-A — session-done upsert dedup (P2, reduces noise from duplicate comments)
4. P5-D — admin_setup_verification SC2086 (clears last persistent actionlint failure)
5. P5-E — pre-commit-failure pattern (🟡 Medium, improves CB-006 perception)
6. P2-C — Phase detection output (P2, Decision Engine improvement)
7. P5-B — FAISS index rebuild trigger (🔴 High but needs merge first)
```

---

## S295 Fixes Applied

| ID | Item | Priority | OODA | Status | Session |
|----|-------|----------|------|--------|---------|
| S295-A | compiled-bot-feedback dedup via GraphQL last:50 | P2 | AfterMath | ✅ Done | S295 |
| S295-B | append-code-quality-to-rescue new job | P2 | Perception | ✅ Done | S295 |
| S295-C | Missed-trigger body uses dynamic link+quote | P3 | Perception | ✅ Done | S295 |
| S295-D | `<details>`/`<summary>` collapsed rescue sections | P3 | Perception | ✅ Done | S295 |
| S295-E | FixedSizeChunker infinite-loop guard | Bug | Action | ✅ Done | S295 |
| S295-F | S294 RAG test fixes (ValidationResult, fallback, sliding) | Bug | Action | ✅ Done | S295 |
| S295-G | `_STEP_TEMPLATE` CodeQL alert removed | Security | Action | ✅ Done | S295 |
| S295-H | PR_LIFECYCLE.md §14.1 Gap Analysis + §14.2 cascade updated | Doc | Perception | ✅ Done | S295 |

---

## P6 — Grounded Failing-Workflow Scanner

### P6-A — Copilot-native `scan-failing-workflows` grounded method (**NEW — S295**)

**Priority:** P1 (blocks automated rescue chain from being fully grounded)  
**OODA Phase:** Observe  
**Estimated effort:** 2–3 hours  
**Tracked by:** PR #3854 comment, issue #3853

**Problem:**
When a Copilot Coding Agent session starts (whether triggered by a rescue comment,
a missed-trigger re-trigger, or a direct `@copilot` mention), it has **no reliable way
to know which CI checks are currently failing on the HEAD commit** without being told
explicitly. Sessions frequently address the single failure mentioned in the trigger comment
but miss other simultaneously failing checks that were not yet commented on.

**Target behaviour:**
At the start of every session, the agent SHALL:

1. Call a grounded `scan_failing_workflows(pr, sha)` method that:
   - Fetches all check runs for `HEAD` SHA via GitHub Checks API (`GET /repos/{owner}/{repo}/commits/{sha}/check-runs`)
   - Filters `conclusion != 'success'` AND `status == 'completed'`
   - Groups by workflow name
   - Returns a structured dict: `{workflow_name: {run_id, conclusion, url, started_at}}`

2. For each failing workflow in the result:
   - Classify against the PDA pattern library (22 patterns as of S292)
   - If pattern known: prepare fix steps
   - If pattern unknown: log to `RP-UNKNOWN` and escalate via PDA loop

3. Summarise in the session-startup output:

```
🔍 Failing checks on {sha12} ({N} failing, {M} pending):
  ❌ Auto-Fix Common Issues  — run #XXXXX  →  RP-TRACKED-DRIFT (auto-fixable)
  ❌ RAG Module Tests        — run #XXXXX  →  RP-RAG-CHRONIC   (test fix needed)
  ⏳ Workflow Compliance     — pending
```

**Implementation Plan:**

```
FILE: scripts/ci/scan_failing_workflows.py
  ├── scan_failing_checks(owner, repo, sha) → list[CheckRun]
  ├── classify_check(run, pattern_library) → PatternMatch | None
  └── format_summary(runs, matches) → str  (markdown table)

FILE: src/codex/skills/scan_failing_workflows/handler.py
  └── run(inputs) → {failing: [...], summary: str, auto_fixable: [...]}

FILE: .github/copilot-prompts/grounded-session-startup.md
  └── Instructs agent to call scan_failing_workflows skill at session start
      before reading any rescue comment

WIRING: .codex/skills_manifest.yml
  └── Add scan_failing_workflows skill entry

WIRING: .github/workflows/copilot-agent-checkin.yml
  └── session-startup step calls scan_failing_workflows before posting re-trigger
      (so the re-trigger comment is pre-populated with ALL current failures,
       not just the one that triggered the S221 guard)
```

**Acceptance criteria:**
- `python scripts/ci/scan_failing_workflows.py --pr 3854 --sha HEAD` exits 0 and prints table
- `pytest tests/ci/test_scan_failing_workflows.py` all pass
- `copilot-agent-checkin.yml` S221 re-trigger comment body includes the full failures table
- Skill callable from `src/codex/skills/scan_failing_workflows/handler.py`

**Why grounded:** The method calls the live GitHub Checks API against the actual HEAD SHA.
It never embeds static failure lists or assumptions. Every scan is idempotent and
re-runnable. Failures that resolve between the scan and the session start are correctly
shown as passing in a re-scan.

---

## Updated Next Session Priority Order (recommended)

```
1. P6-A — scan-failing-workflows grounded method (🔴 P1, ~3h, unblocks full rescue awareness)
2. P5-A — D_ACTIVATION_CHECKLIST.md (🔴 High, 1-2h, unblocks D model activation)
3. P5-C — COPILOT_ACTIVE_SESSION TTL (🔴 High, 30min, reduces queue wait)
4. P5-D — admin_setup_verification SC2086 (clears last persistent actionlint failure)
5. P5-E — pre-commit-failure pattern (🟡 Medium, improves CB-006 perception)
6. P2-C — Phase detection output (P2, Decision Engine improvement)
7. P5-B — FAISS index rebuild trigger (🔴 High but needs merge first)
```
