# Rate-Limit Recovery Runbook

**Applies to:** Copilot Cloud Agent sessions on `Aries-Serpent/_codex_`
**Pattern:** `RATE_LIMIT_001` (added S923, 2026-05-11)
**Scripts:** `scripts/ci/rate_limit_handler.py`, `scripts/ci/push_conflict_resolver.py`

---

## 🔍 Symptoms

| Signal | Meaning |
|--------|---------|
| `CAPIError: 429 Sorry, you've exceeded your weekly rate limit` | Weekly token budget exhausted |
| `Rate limit exceeded after 5 retries` | Agent made 5 exponential-backoff attempts, all 429 |
| `Changes were pushed to Copilot's branch while it was working` | Concurrent bot commits diverged the branch |
| `COPILOT_AGENT_PREVIOUS_SESSION_IDS` has 3+ entries | Multiple retry sessions, each hitting 429 |
| `fix(ci): universal baseline sweep [skip ci]` commits in git log | Bot pushed during agent session |

### Real-world cascade (PR #4389, 2026-05-10)

```
Run #3476  23:53Z  → 429 (session 1)
Run #3477  00:41Z  → 429 (session 2, immediate retry)
Run #3478  00:54Z  → 429
Run #3479  01:09Z  → 429
Runs 3480–3483     → 429 (cascade: ~15 min each)
            [~15h gap — rate limit resets]
Run #3486  17:13Z  → push conflict (bot commits during session)
Run #3489  17:47Z  → push conflict (bot commits during session)
```

**Root cause:** Each 429 session-termination triggers CI automation which
immediately re-queues the Copilot agent. The agent re-fires into the same
429, creating a loop until the weekly budget exhausts completely.

---

## 🛠️ Recovery Procedure

### Step 1 — After rate-limit reset, resolve push conflicts first

```bash
# Check how far behind the branch is (bot commits during interrupted sessions)
git fetch origin
git log --oneline HEAD..origin/$(git branch --show-current) | head -10

# Auto-resolve known bot-commit conflicts
python3 scripts/ci/push_conflict_resolver.py
```

The resolver handles these automatically:

| File | Policy | Reason |
|------|--------|--------|
| `CODEX_MANIFEST.json` | `--theirs` (remote) | Auto-generated; latest is authoritative |
| `.codex/agent_context.json` | `--theirs` (remote) | Auto-generated |
| `.secrets.baseline` | `--ours` (branch) | P-045: always keep branch version |
| All other files | ❌ Unresolvable | Requires manual intervention |

### Step 2 — Load the checkpoint to understand session state

```bash
python3 scripts/ci/rate_limit_handler.py --check
```

Output shows:
- **completed**: tasks fully committed before interruption
- **in_progress**: task that was mid-flight (verify git log — may be partial)
- **pending**: tasks that never started (carry forward)

### Step 3 — Mark checkpoint resolved, then continue

```bash
# Mark the checkpoint so Pattern 33 stops reporting it
python3 scripts/ci/rate_limit_handler.py --resolve --session S924

# Continue with the pending tasks from the checkpoint
```

---

## 🤖 Saving a Checkpoint (during/after a 429 failure)

When a session is interrupted by a 429 error, call the handler to preserve state:

```bash
python3 scripts/ci/rate_limit_handler.py \
  --pr-number 4389 \
  --error-json '{"code":"user_weekly_rate_limited","text":"reset in 6 hours 5 minutes","ghRequestId":"CC44:7229D:..."}' \
  --completed "Fix CodeQL #13447,Resolve merge conflict" \
  --in-progress "Fix CodeQL #13429" \
  --pending "Update CHANGELOG,Run parallel_validation" \
  --session S923
```

This:
1. Writes `.codex/rate_limit_checkpoint.json`
2. Posts a structured comment to the PR with task state + retry time
3. Documents the push-conflict risk for the next session

### Stdin mode (pipe raw error JSON)

```bash
echo "$COPILOT_ERROR_JSON" | python3 scripts/ci/rate_limit_handler.py \
  --pr-number 4389 \
  --stdin-error \
  --completed "..." \
  --pending "..."
```

---

## 🚦 Pattern 33 — CI Detection

`scripts/ci/auto_fix_common_issues.py` Pattern 33 (`Rate Limit Checkpoint`)
automatically surfaces an unresolved checkpoint at every CI scan:

```
⚠  Pattern 33 (Rate Limit Checkpoint): Unresolved rate-limit checkpoint from
   session S923 (PR #4389). Retry after: 2026-05-10T10:45Z. Pending: [Fix C, Fix D].
      → Load checkpoint:  python3 scripts/ci/rate_limit_handler.py --check
      → Resolve conflict: python3 scripts/ci/push_conflict_resolver.py
      → Mark resolved:    python3 scripts/ci/rate_limit_handler.py --resolve
```

This is **informational only** — it never blocks CI or causes a non-zero exit.

---

## 🔒 Preventing the Cascade

The cascade (8 sessions, all 429) happens because CI automation re-queues
the agent immediately after each failure. Mitigations:

1. **Checkpoint comment** — the PR comment posted by `rate_limit_handler.py`
   gives the agent a structured recovery prompt with the reset time, preventing
   blind retries.

2. **`push_conflict_resolver.py` in pre-push** — running the resolver before
   any `git push` prevents "Changes were pushed while working" failures that
   pile on top of rate-limits.

3. **Session spacing** — the recovery instruction includes the reset time, so
   `@copilot` re-invocations can be timed appropriately.

---

## 📁 Related Files

| File | Purpose |
|------|---------|
| `scripts/ci/rate_limit_handler.py` | Core checkpoint + PR comment handler |
| `scripts/ci/push_conflict_resolver.py` | Auto-rebase for bot-commit conflicts |
| `scripts/ci/auto_fix_common_issues.py` Pattern 33 | CI detection |
| `.codex/rate_limit_checkpoint.json` | Live checkpoint (gitignored in user envs) |
| `tests/ci/test_rate_limit_handler.py` | 18 unit tests |

---

## 🔗 References

- [GitHub Copilot Rate Limits](https://docs.github.com/copilot/concepts/rate-limits)
- [P-045: .secrets.baseline conflict policy](../../.codex/CODEBASE_AGENCY_POLICY.md)
- [PR #4389 session diagram](../../docs/sessions/PR4389_session_diagram.md)
- [CI Failure Triage Issue #4388](https://github.com/Aries-Serpent/_codex_/issues/4388)
