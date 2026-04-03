# Session Resumption Prompt — PR #3854 (0D_base_)

> **Purpose:** Paste this entire block as a comment on PR #3854 to resume the
> next Copilot session. Updated after every session until merge.
> **Latest session:** S300 — 2026-04-03

---

## 🔁 Resumption Command

```
@copilot+claude-sonnet-4.6 Resume PR #3854, branch 0D_base_ — S301.

Latest commit: S300 (HEAD)
Context files to load FIRST (mandatory pre-session protocol — §14.5 PR_LIFECYCLE):
0. python scripts/ci/pre_session_context.py --repo Aries-Serpent/_codex_ --pr 3854
1. .codex/CODEBASE_AGENCY_POLICY.md
2. docs/ci/PR_LIFECYCLE.md
3. .codex/plans/pr_lifecycle_improvements.md   ← improvement plan (P1–P6)
4. .codex/plans/COGNITIVE_BRAIN_LIVE_STATUS.md ← CB live status
5. python scripts/ci/pda_failure_logger.py summarize
```

---

## ✅ S300 Completed

| Item | Fix | Files |
|------|-----|-------|
| RC-3 `discussion-response-bridge.yml` | New workflow: `discussion_comment` → PR notification bridge with dedup marker | `.github/workflows/discussion-response-bridge.yml` |
| RC-4 `post-accountability-to-discussion.yml` | Dynamic per-PR discussion lookup; falls back to #3673; uses `last:50` dedup | `.github/workflows/post-accountability-to-discussion.yml` |
| P5-C TTL fix | Echo message "4h" → "1h" (TTL was already 3600s) | `.github/workflows/agent-auth-delegation.yml` |
| S221 blocking-count | `check_pr_comments.py` count wired into retrigger body | `.github/workflows/copilot-agent-checkin.yml` |
| Dynamic Q1/Q2/Q3 | Python step reads PDA YAML, generates Q1–Q3 from top patterns | `.github/workflows/copilot-agent-checkin.yml` |
| CB-001 Typer API | Fixed E402 import ordering; removed dead `hasattr(_typer, "Typer")` guard | `src/codex_cli/app.py` |

## ✅ S299 Completed

| Item | Fix | Files |
|------|-----|-------|
| RFC-001 skill-agent binding | Full RFC written (problem stmt, priority scoring, graduation pipeline, orchestrator design) | `.codex/plans/RFC-001-skill-agent-binding.md` |
| RC-5 `build_comment_context()` | New public function + wired into initial POST of rescue comments | `scripts/ci/discussion_context_store.py`, `post_rescue_comment.py` |
| PR_LIFECYCLE v2.0.0 | §16.4 ✅ FIXED; §16.5 mermaid green; trigger map updated | `docs/ci/PR_LIFECYCLE.md` |
| comment #4183926920 replied | Root cause + S298 fix explained | PR comment |

## ✅ S298 Completed

| Item | Fix | Files |
|------|-----|-------|
| CodeQL 12784/12785 | `pre_session_context.py` implicit string concatenation fixed | `scripts/ci/pre_session_context.py` |
| CodeQL 12781 | `discussion_cleanup.py` unused `_GQL_ID_RE` removed | `scripts/ci/discussion_cleanup.py` |
| CodeQL 12782/12783 | `discussion_context_store.py` unused `_DISCUSSION_ACCOUNTABILITY`, `_CAT_QA` removed | `scripts/ci/discussion_context_store.py` |
| F541/F401 | 7 bare f-strings fixed; `urllib.parse` unused import removed | discussion scripts, `scan_failing_workflows.py` |
| escalate job | Standalone `gh pr comment` → `post_rescue_comment.py`; checkout from `refs/heads/main` (trusted) | `iterative-self-healing-ci.yml` |
| Pattern 8 | F401 now auto-fixable in CodeQL scan; `"CodeQL Alerts"` → `auto_fixable_patterns` | `auto_fix_common_issues.py` |
| PR_LIFECYCLE v1.9.0 | §7.2 cascade, §14.1 gaps, §14.5 P6-B/C tools, §16.1 map | `docs/ci/PR_LIFECYCLE.md` |
| Self-healing escalation RCA | comment #4183926920 explained (fired because escalate job pre-dated S294 upsert system); fixed by S298 | accountability report |

## ✅ S297 Completed (previous session)

| Item | Fix | Files |
|------|-----|-------|
| mcp_poster dedup | `_find_discussion_comment` → `last:100` backward pagination | `src/codex/github/mcp_poster.py` |
| RC-3 | `check_discussion_replies` — detect unread maintainer replies | `src/codex/github/mcp_poster.py` |
| RC-4 | `find_or_create_pr_discussion` — auto-create per-PR discussions | `src/codex/github/mcp_poster.py` |
| P6-B | `scripts/ci/pre_session_context.py` — hardened pre-session briefing | `scripts/ci/pre_session_context.py` |
| P6-C | `scripts/ci/discussion_context_store.py` — push-model context store | `scripts/ci/discussion_context_store.py` |
| Discussion cleanup | `discussion_cleanup.py` CLI + `discussion-cleanup.yml` workflow | `scripts/ci/discussion_cleanup.py` |

---

## 🔴 Priority 1 — Next Session Start Here

### Execute discussion cleanup manifest (BLOCKING — requires external trigger)
```bash
gh workflow run discussion-cleanup.yml \
  -f manifest_path=.codex/cleanup/discussion_cleanup_manifest.json \
  -f execute=true
```
526 duplicate comments in #3756/#3673 — manifest ready. Must be triggered by a human or external runner.

### RFC-001 Phase 1: Schema + Registry (S301)
- Add `skills` optional key to `.codex/schemas/AgentRegistrySchema.json`
- Add `skills:` entries to 5 pilot agents in `AGENT_REGISTRY.yaml`
- Skill wrappers: `pre_session_context`, `scan_failing_workflows`, `discussion_context`

### Wire pre_session_context.py into copilot-agent-checkin.yml S221 body
The pre_session_context.py §A/§B briefing should be appended to the retrigger body
so the receiving agent session has immediate context. Add a step that runs
`pre_session_context.py --brief` and pipes to `PRECESSION_BRIEFING` env var.

---

## 🟡 Priority 2 — After P1 Complete

### P2-C: Phase detection output in `workflow-execution-gate.yml`
Add `detect-phase` step outputting `pre-approval | wec-approved | agent-active | ready-to-review`.

### P5-E: Add `pre-commit-failure` pattern to `.codex/patterns/ci_failure_patterns.yaml`
Pattern: `"pre-commit.*failed|detect-secrets.*exit.*3|end-of-file-fixer.*fixed"`
PDA ID: `RP-PRECOMMIT-FAILURE`

### Wire `pre_session_context.py` into `copilot-agent-checkin.yml` body (§A+§B)
Add full §A workflows+ETAs + §B blocking comments to the check-in body, not just
the SCAN_TABLE. The retrigger body (S221 guard) already gets BLOCKING_COUNT (S300);
add §B full list as a collapsible `<details>` block.

---

## 🟢 Priority 3 — Enhancement

### P2-B: comment-gate cascade guard
Add `!endsWith(github.event.comment.user.login, '[bot]')` to `comment-review-gate.yml` `if:`.

### P3-C: Proactive monitor per-PR daily cap
State file `.codex/ci_monitor_state.json` — cap 5 posts per PR per calendar day.

---

## 🔵 Cognitive Brain Status

```
Operating Model: E (advisory) — D_CAPABLE gates pass, human activation pending
AGENT_REGISTRY: v1.9.0 (152 agents)
Pattern 8: ✅ F401 now auto-fixable in CodeQL scan
Pattern 1 + Pattern 8: dual coverage of unused imports
Session: S298 complete
Next: S299 — P1 priorities above
```

---

## Pre-Session Checklist (§14.5 PR_LIFECYCLE.md — MANDATORY)

```bash
# ALWAYS-FIRST — run before any code changes:
python scripts/ci/pre_session_context.py --repo Aries-Serpent/_codex_ --pr 3854

# Verify Pattern 8 CodeQL scan is clean:
python scripts/ci/auto_fix_common_issues.py --check-only --pattern 8

# Verify full F401 scan clean:
python -m ruff check . --select F401 --output-format=concise

# Verify actionlint clean:
/tmp/actionlint .github/workflows/*.yml 2>&1 | grep -v "^$" | head -5 || echo "✅ clean"
```
