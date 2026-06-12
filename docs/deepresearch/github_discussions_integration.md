# DeepResearch: GitHub Discussions — Codebase Integration, Hardening, and CLI Design

> **Generated:** 2026-03-25 | **Author:** Copilot Coding Agent (S192) | **PR:** #3741
> **Roles:** [Primary: Research Integrator], [Secondary: CI Engineer] ⚡ Energy: 9
> **Target:** `https://github.com/Aries-Serpent/_codex_/discussions`
> **Index:** `docs/deepresearch/INDEX.md`

---

## 1. Executive Summary

The `_codex_` repository already has a functioning GitHub Discussions integration
built around `src/codex/github/mcp_poster.py` and the
`.github/workflows/post-accountability-to-discussion.yml` workflow.  As of S192
this infrastructure has been **hardened** with five new methods and four new CLI
subcommands that close the remaining gaps:

| Gap (pre-S192) | Fix (S192) |
|---|---|
| No way to add a comment to an *existing* discussion | `add_discussion_comment()` + `add-discussion-comment` CLI |
| Duplicate status comments accumulate on every push | `upsert_discussion_comment()` + `upsert-discussion-comment` CLI |
| No standardised CI pattern summary poster | `post_ci_pattern_summary()` + `post-ci-pattern-summary` CLI |
| No tokenized continuation chain poster | `post_continuation_chain()` + `post-continuation` CLI | <!-- pragma: allowlist secret -->
| No scheduled/push-triggered discussion status workflow | `.github/workflows/post-ci-status-to-discussion.yml` |
| No self-contained chain generator that reads live state | `scripts/cognitive/continuation_chain.py` |

---

## 2. Existing Infrastructure Audit

### 2.1 Python API — `src/codex/github/mcp_poster.py`

| Method | Status | Purpose |
|---|---|---|
| `create_discussion()` | ✅ Pre-existing | Create a new Discussion (GraphQL `createDiscussion`) |
| `post_session_summary_discussion()` | ✅ Pre-existing | Wrapper: S-number summary → "session-summaries" category |
| `add_discussion_comment()` | ✅ **New S192** | Add a comment to an existing Discussion |
| `upsert_discussion_comment()` | ✅ **New S192** | Idempotent add-or-update by HTML marker |
| `post_ci_pattern_summary()` | ✅ **New S192** | Upsert CI pattern knowledge-graph summary |
| `post_continuation_chain()` | ✅ **New S192** | Always-new comment: tokenized chain prompt | <!-- pragma: allowlist secret -->
| `_resolve_discussion_node_id()` | ✅ **New S192** | GraphQL: discussion number → node ID |
| `_find_discussion_comment()` | ✅ **New S192** | GraphQL: search 50 most recent comments for marker |
| `_update_discussion_comment()` | ✅ **New S192** | GraphQL `updateDiscussionComment` |
| `_resolve_discussion_ids()` | ✅ Pre-existing | repo + category → node IDs for `createDiscussion` |
| `retrieve_cb_patterns()` | ✅ Pre-existing | Query CB SQLite → markdown table for context injection |

### 2.2 Workflows

| Workflow | File | Status | Purpose |
|---|---|---|---|
| Post Accountability to Discussion | `post-accountability-to-discussion.yml` | ✅ Pre-existing | Upserts the latest accountability session entry into authoritative discussion #3673 with a branch/PR/session/turn key |
| Post CI Status to Discussions | `post-ci-status-to-discussion.yml` | ✅ **New S192** | Posts continuation chain + CI pattern summary on push to `0D_base_`/`copilot/**` |

### 2.3 Discussion Threads in Use

| # | Title | Purpose | Upsert Key |
|---|---|---|---|
| 3673 | Accountability Report | Authoritative historical notes sourced from `AGENT_ACCOUNTABILITY_REPORT.md` | `<!-- codex-accountability-turn:v1 branch=… pr=… session=… turn=… -->` |
| _auto_ | CI Pattern Summary | High-recurrence + cross-PR tables | `<!-- ci-pattern-summary:{session_id} -->` |
| _auto_ | Continuation Chain | Tokenized chain prompts for next-session pickup | Always new comment | <!-- pragma: allowlist secret -->

---

## 3. CLI Design for Copilot Coding Agents

### 3.1 Existing CLI (`python -m codex.github.mcp_poster`)

```
post-comment               Post a PR comment
set-variable               Create/update a repo variable
create-discussion          Create a new GitHub Discussion
create-branch              Create a branch ref
create-pr                  Open a pull request
merge-branch               Server-side merge
retrieve-patterns          Print recent CB patterns as Markdown
commit-files               Push file changes via Git Data API
add-discussion-comment     [NEW] Add comment to existing Discussion
upsert-discussion-comment  [NEW] Add-or-update by marker
post-ci-pattern-summary    [NEW] Upsert CI pattern summary to Discussion
post-continuation          [NEW] Post tokenized continuation chain  # pragma: allowlist secret
```

### 3.2 New Script CLI (`python scripts/cognitive/continuation_chain.py`)

```
--db PATH                  SQLite pattern DB path
--manifest PATH            CODEX_MANIFEST.json path
--session-id STR           Session ID (overrides env vars)
--sha STR                  Git SHA (overrides env vars)
--output PATH              Write to file instead of stdout
--post-to-discussion       Post to GitHub Discussions
--repo OWNER/REPO          GitHub repo (default: Aries-Serpent/_codex_)
--discussion-number INT    Target discussion number (default: 3673)
--upsert                   Upsert by session marker (prevents duplicate comments)
```

### 3.3 Recommended CLI Design Patterns for Copilot Agents

The following CLIs should be considered for future phases based on the
systematic gaps identified in this research:

#### CLI 1: `discussion-sync` — Sync cognitive brain state to Discussion

```bash
python -m codex.github.mcp_poster upsert-discussion-comment \
  --repo Aries-Serpent/_codex_ \
  --number 3673 \
  --body-file /tmp/brain_status.md \
  --marker "<!-- brain-status:$(git rev-parse --short HEAD) -->"
```

**Purpose:** Idempotent sync of any markdown document to a Discussion comment.
One command, no duplicates.  Marker encodes the commit SHA so each unique
commit gets exactly one comment; re-runs on the same commit update the
existing comment.

#### CLI 2: `discussion-broadcast` — Post to multiple Discussions at once

```bash
python scripts/cognitive/continuation_chain.py \
  --post-to-discussion \
  --discussion-number 3673 \
  --upsert
```

**Purpose:** A single `continuation_chain.py` invocation reads all live state
and posts a self-contained prompt.  Any Copilot Agent picking up this Discussion
thread can resume context without accessing any other file.

#### CLI 3: `post-continuation` — Tokenized chain for Agent pickup

```bash
python -m codex.github.mcp_poster post-continuation \
  --repo Aries-Serpent/_codex_ \
  --number 3673 \
  --body-file /tmp/chain.md
```

**Purpose:** Posts a continuation chain that begins with `@copilot continue
<task_url>` — any Copilot Agent browsing Discussion #3673 immediately gets
the structured handoff prompt.

#### CLI 4: `post-ci-pattern-summary` — Push pattern knowledge graph to Discussion

```bash
python -m codex.github.mcp_poster post-ci-pattern-summary \
  --repo Aries-Serpent/_codex_ \
  --number 3673 \
  --body-file /tmp/patterns.md \
  --session-id "run-$GITHUB_RUN_ID"
```

**Purpose:** CI-triggered, idempotent.  Each workflow run upserts the CI
pattern table, keeping discussion #3673 always showing the latest state.

#### CLI 5 (Future): `discussion-search` — Search Discussion for patterns

```python
# Proposed API (Phase 8 P3):
poster.find_discussion_comments_by_marker(
    repo="Aries-Serpent/_codex_",
    discussion_number=3673,
    marker="<!-- codex-continuation-chain:",
    max_results=10,
)
```

**Purpose:** Allows an agent to **scan** all previous continuation chains in
a Discussion thread to reconstruct project history.

#### CLI 6 (Future): `discussion-digest` — Build a digest of all session chains

```bash
python scripts/cognitive/discussion_digest.py \
  --repo Aries-Serpent/_codex_ \
  --discussion-number 3673 \
  --marker "<!-- codex-continuation-chain:" \
  --last-n 5 \
  --output /tmp/digest.md
```

**Purpose:** Scan the last N continuation-chain comments in a Discussion,
extract the `TOKEN:NEXT_STEPS` sections, and build a digest prompt for
onboarding a new agent session with accumulated context.

---

## 4. Hardened Posting Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │         GitHub Actions Workflow              │
                    │  post-ci-status-to-discussion.yml           │
                    │  (triggers on push to 0D_base_/copilot/**)  │
                    └───────────────┬─────────────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────────────┐
                    │   continuation_chain.py                      │
                    │   Reads:                                     │
                    │   • CODEX_MANIFEST.json (ci_patterns)        │
                    │   • pattern_recorder.py (high_rec, cross_pr) │
                    │   • COGNITIVE_BRAIN_STATUS_*.md              │
                    │   Outputs: tokenized Markdown chain          │  # pragma: allowlist secret
                    └───────────────┬─────────────────────────────┘
                                    │
               ┌────────────────────▼────────────────────────────┐
               │             mcp_poster.py                        │
               │                                                  │
               │  post_continuation_chain()  ──────────────────► │
               │  post_ci_pattern_summary()  ──────────────────► │──► Discussion #3673
               │  upsert_discussion_comment()  ────────────────► │
               │  add_discussion_comment()  ────────────────────► │
               └────────────────────┬────────────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────────────┐
                    │        GitHub GraphQL API                    │
                    │  addDiscussionComment mutation               │
                    │  updateDiscussionComment mutation            │
                    │  discussion(number: N) { comments }         │
                    └─────────────────────────────────────────────┘
```

---

## 5. Copilot Agent + Copilot Assistant Integration

### 5.1 How Copilot Coding Agents Use Discussions

| Use Case | Mechanism | CLI |
|---|---|---|
| Post follow-up prompt after session | `post_continuation_chain()` | `post-continuation` |
| Update status without spamming thread | `upsert_discussion_comment()` | `upsert-discussion-comment` |
| Report CI pattern state | `post_ci_pattern_summary()` | `post-ci-pattern-summary` |
| Resume from prior session context | Read last chain comment from Discussion | `discussion-digest` (planned) |
| Post session accountability | `post-accountability-to-discussion.yml` | Automatic upsert on `AGENT_ACCOUNTABILITY_REPORT.md` push; exactly one authoritative comment per branch/PR/session/turn |

### 5.2 Tokenized Continuation Chain Format

The `continuation_chain.py` output uses HTML comment token markers that are
invisible in rendered Markdown but machine-parseable:

```markdown
<!-- TOKEN:META -->
────────────────────────────────────────────────────────────
**Session:** `run-23519039857`
**SHA:** `ffaa534`
**Generated:** `2026-03-25T01:30:00Z`
────────────────────────────────────────────────────────────

<!-- TOKEN:PHASE -->
...current phase completion state...

<!-- TOKEN:PATTERNS -->
...high-recurrence + cross-PR pattern tables...

<!-- TOKEN:NEXT_STEPS -->
...Phase 8 roadmap checklist...
```

Any Copilot Agent or Copilot Assistant can:
1. Find the most recent comment containing `<!-- TOKEN:META -->` in Discussion #3673
2. Parse the token sections to instantly reconstruct session context
3. Execute the `@copilot continue` CTA in `TOKEN:NEXT_STEPS`

### 5.3 Search and Scan Capabilities

**Current (S192):**
- `_find_discussion_comment()` — scans up to 50 comments for a marker string
- `retrieve_cb_patterns()` — queries CB SQLite memory for recent patterns

**Planned (Phase 8):**
- `discussion_digest.py` — scan N most recent chain comments → build aggregate context
- Pattern-aware RAG index over Discussion thread history
- `cross_pr_correlation()` → auto-create GitHub Issue when ≥3 PRs affected

---

## 6. Deduplication Strategy

The biggest risk with automated Discussion posting is **thread spam** — every
CI run posting a new comment makes threads unreadable.

**Solution: Marker-based upsert**

```python
marker = f"<!-- ci-pattern-summary:{session_id} -->"
full_body = f"{marker}\n{summary_md}"
poster.upsert_discussion_comment(repo, number, full_body, marker)
```

- The marker is an invisible HTML comment in the first line
- `_find_discussion_comment()` scans the thread for the marker
- If found: `updateDiscussionComment` (GraphQL mutation) — no new comment
- If not found: `addDiscussionComment` — new comment only

**Best practice: session-scoped markers**
- Same session re-running: `<!-- ci-pattern-summary:run-12345 -->` → upsert
- New session: `<!-- ci-pattern-summary:run-12346 -->` → new comment

---

## 7. Security and Token Requirements

| Operation | Required Permission | Token Priority | <!-- pragma: allowlist secret -->
|---|---|---|
| Read discussions | `discussions: read` | `GITHUB_TOKEN` | <!-- pragma: allowlist secret -->
| Add/update discussion comment | `discussions: write` | `CODEX_MASTER_KEY` → `CODEX_BACKUP_KEY` |
| Create new discussion | `discussions: write` | `CODEX_MASTER_KEY` |
| Search comments (GraphQL) | `discussions: read` | `GITHUB_TOKEN` | <!-- pragma: allowlist secret -->

All write operations require `discussions: write` permission in the workflow
`permissions:` block AND on the token itself.  `GITHUB_TOKEN` from Actions
has `discussions: write` in the default permissions if the repo has Discussions
enabled.

**Validation check (from `admin_setup_verification.yml`):**

```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://api.github.com/repos/${{ github.repository }}/discussions")
if [ "$STATUS" = "200" ]; then echo "Discussions enabled"; fi
```

---

## 8. Relevant Repo Files

| File | Role |
|---|---|
| `src/codex/github/mcp_poster.py` | Core Discussion API client (GraphQL + REST) |
| `scripts/cognitive/continuation_chain.py` | **New S192** — tokenized chain builder | <!-- pragma: allowlist secret -->
| `.github/workflows/post-accountability-to-discussion.yml` | Posts accountability entries to #3673 |
| `.github/workflows/post-ci-status-to-discussion.yml` | **New S192** — push-triggered CI status posts |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | Accountability report source |
| `CODEX_MANIFEST.json` (`ci_patterns`) | Knowledge graph exported to Discussions |
| `scripts/ci/pattern_recorder.py` | Pattern DB queried by continuation_chain.py |
| `.codex/docs/COGNITIVE_BRAIN_STATUS_*.md` | Phase status read by continuation_chain.py |
| `tests/github/test_mcp_poster.py` | Tests for `create_discussion`, `post_session_summary_discussion` |
| `.github/agents/ci-pattern-guardian.md` | Agent spec referencing CI pattern → Discussion pipeline |

---

## 9. Recommended Next Actions

| Priority | Action | File |
|---|---|---|
| P1 | Add tests for `add_discussion_comment`, `upsert_discussion_comment`, `post_ci_pattern_summary` | `tests/github/test_mcp_poster.py` |
| P1 | Verify `post-ci-status-to-discussion.yml` triggers successfully on next `0D_base_` push | CI |
| P2 | Build `scripts/cognitive/discussion_digest.py` — scan last N chain comments → aggregate context | New script |
| P2 | Add `discussion-search` CLI: find comments by marker across a thread | `mcp_poster.py` |
| P3 | RAG-index Discussion thread history for semantic search by Copilot Agents | `src/codex/api/rag_api.py` |
| P3 | `cross_pr_correlation()` → auto-create GitHub Issue (Phase 8 P3) | `pattern_recorder.py` |

---

*Generated by Copilot Coding Agent S192 | Session-linked to PR #3741 | Phase 8 deepresearch deliverable*
