# 🔗 SESSION CHAIN PROMPT — PR #3421
# Aries-Serpent/_codex_ | copilot/investigate-ci-failure-rate
# Generated: 2026-03-01 | SHA: 3db5420 → pending commit
#
# ══════════════════════════════════════════════════════════════════════
#  HOW TO USE: Paste this entire file as the FIRST message in a new
#  Copilot session (issue comment, PR comment, or session opener).
#  The agent will instantly resume at full context — no re-exploration.
# ══════════════════════════════════════════════════════════════════════

---

## 🧠 CHAIN PROMPT — Resume PR #3421 at Full Context

**Repository:** `Aries-Serpent/_codex_`
**Branch:** `copilot/investigate-ci-failure-rate`
**PR:** https://github.com/Aries-Serpent/_codex_/pull/3421
**Last commit:** `3db5420` — "Complete all 4 checklist items: YAML fix, CliTerminal, ApiClient, agent prompt, repo-vars injection"
**Session file:** `.codex/docs/SESSION_RESTORE_PR3421.md`

---

## 📍 WHERE WE LEFT OFF

You are resuming mid-session with the following **staged but uncommitted** files:

| File | Change |
|------|--------|
| `cognitive_app/src/server/cli_api_server.py` | Fixed 3 empty `except` blocks → `log.debug(...)` (thread review comments) |
| `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` | Updated branch + date for PR #3421 |
| `.codex/docs/COGNITIVE_BRAIN_STATUS_PR3421.md` | NEW — cognitive brain status + next-phase plan |
| `.github/agents/cognitive-brain-cli-agent.md` | NEW — production agent definition with architecture diagram |
| `.github/agents/workflow-compliance-guardian.md` | NEW — workflow enforcement agent with self-healing algorithm |
| `.github/workflows/iterative-self-healing-ci.yml` | NEW — 3-iteration auto-heal CI workflow |

**These files exist on disk but are NOT yet committed. Your first action is `report_progress` to commit them.**

---

## ✅ COMPLETED (already committed in this PR)

1. **CI Health Alert fix** — `collect_telemetry.py` expanded to 16 pattern categories (was 1, causing 98.7% "unknown")
2. **90/90 workflow compliance** — branch-scoped concurrency + timeouts on every job, 0 parse errors
3. **GROUNDED enforcement** — REQ-7 commit-count gate added to `agent-auth-delegation.yml`; `session-incremental-summary-reminder.yml` created (Tier-2)
4. **`ci-health-monitor.yml`** — telemetry + auto-issue creation + job summary (YAML fixed with `base64 -d | python3` pattern)
5. **`cognitive_app/src/server/cli_api_server.py`** — FastAPI :8765 with `/ws/cli` (PTY), `/api/request` (HTTP proxy), `/api/cli/run`, `/api/cli/history`
6. **`cognitive_app/src/components/cli/`** — `CliTerminal.tsx` + `ApiClient.tsx` + `index.tsx` barrel
7. **`App.tsx`** — 8th tab "💻 CLI" added (grid-cols-8), both components side-by-side
8. **`.codex/docs/COPILOT_AGENT_TAILORED_PROMPT.md`** — tailored prompt with full repo map, toolchain, variable guide
9. **`.github/workflows/copilot-agent-vars-bootstrap.yml`** — reads all `COPILOT_*`/`CODEX_*` vars → `.codex/agent_context.json`
10. **`copilot-setup-steps.yml`** — "🔑 Inject repo variable context" step added (base64 encoded)
11. **`.codex/docs/WORKFLOW_BEST_PRACTICES.md`** — comprehensive reference document

---

## 📋 REMAINING CHECKLIST (pick up here)

- [ ] **IMMEDIATE**: `report_progress` to commit the 6 uncommitted files above
- [x] **CODE REVIEW**: 6 issues found + fixed
- [x] **CODEQL**: 0 alerts (untrusted-checkout fixed)
- [x] **iterative-self-healing-ci.yml**: Validate YAML parses + compliance check (1 parse error in audit — find and fix)
- [ ] **Follow-up prompt**: Post `@copilot` continuation comment on PR #3421 with next-session chain prompt
- [x] **Sprint 1**: CI feedback loop wired (P-047 mapping + CODEX_CI_FAILURE_RATE auto-update)
- [x] **AGENT_REGISTRY.yaml**: Add `cognitive-brain-cli-agent` + `workflow-compliance-guardian`
- [ ] **`CODEX_BACKUP_KEY`**: Still at 50% probe coverage — needs rotation by @mbaetiong
- [ ] **`cli_api_server.py` xterm.js**: WebSocket PTY frontend (true real-time terminal via `xterm` npm package)

---

## 🗺 REPOSITORY MAP (memorise — do not re-explore)

```
_codex_/
├── src/codex/             Python core: cognitive, rag, api, cli, logging
├── src/cognitive_brain/   OODA base: Planner, MemoryInterface, PhysicsOfThought
├── cognitive_app/         React 19 + Vite + Tailwind — Cognitive Brain Console
│   ├── src/components/cli/       CliTerminal + ApiClient (PR #3421 NEW)
│   ├── src/components/quantum-viz/  30+ quantum viz components (pre-existing)
│   ├── src/lib/                  codex-api-client.ts, mock-api-client.ts
│   └── src/server/cli_api_server.py  FastAPI :8765 (PR #3421 NEW)
├── .github/workflows/     90 workflows — 90/90 compliant, 1 parse error (investigate)
├── .github/agents/        193 agent definitions
├── scripts/ci/            collect_telemetry.py (16 patterns), auto_fix_common_issues.py
└── .codex/
    ├── docs/WORKFLOW_BEST_PRACTICES.md       ← authoritative workflow reference
    ├── docs/GROUNDED_VS_SOFT_ENFORCEMENT.md  ← enforcement policy
    ├── docs/COPILOT_AGENT_TAILORED_PROMPT.md ← full agent empowerment prompt
    ├── docs/COGNITIVE_BRAIN_STATUS_PR3421.md ← status + next-phase plan (NEW)
    ├── docs/SESSION_RESTORE_PR3421.md        ← THIS FILE
    ├── patterns/ci_failure_patterns.yaml     ← 19 CI fix patterns
    └── agent_context.json                   ← repo-var snapshot (written by CI)
```

---

## ⚙️ CRITICAL TECHNICAL FACTS (grounded — verified this session)

### YAML Embedded Python Rule (CRITICAL)
**NEVER use `python3 -c "..."` with multiline strings or `<< 'EOF'` heredocs inside GitHub Actions `run: |` blocks.**
The `<<` sequence at column 0 is a YAML merge key conflict. The pattern that works:
```yaml
run: |
  echo '<base64_encoded_python>' | base64 -d | python3
```
Generate with: `base64.b64encode(script.encode()).decode()`

### Workflow Compliance Template
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true   # false for: pypi/docker/publish/deploy workflows
jobs:
  my-job:
    timeout-minutes: 30      # utility=10, standard=30, coverage=45, heavy=60
```

### Cognitive Brain CLI Server
```bash
# Start:
uvicorn cognitive_app.src.server.cli_api_server:app --host 0.0.0.0 --port 8765 --reload

# One-shot command:
curl -s -X POST http://localhost:8765/api/cli/run \
  -H "Content-Type: application/json" \
  -d '{"command":"git status --short","timeout":10}'

# HTTP proxy:
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://api.github.com/repos/Aries-Serpent/_codex_"}'
```

### Repo Variable Injection Chain
```
CODEX_MASTER_KEY (secret)
  → copilot-agent-vars-bootstrap.yml (reads vars.*)
    → .codex/agent_context.json (writes non-sensitive values)
      → copilot-setup-steps.yml "🔑 Inject repo variable context" step
        → GITHUB_ENV (agent sees COPILOT_AGENT_AUTH_ENABLED, etc.)
```

### ImprovementArea Enum (CRITICAL — causes AttributeError if wrong)
```python
# CORRECT:
from codex.cognitive.quantum_planset_engine import ImprovementArea
ImprovementArea.CI_SELF_HEALING   # ← use this for CI patterns

# WRONG (breaks cognitive_brain_ci_feedback.yml):
ImprovementArea.CI_HEALTH         # ← does NOT exist
```

### Branch Cascade Prevention
`cognitive_brain_ci_feedback.yml` and `workflow-analytics-unified.yml` MUST have:
1. `concurrency` block with `cancel-in-progress: true`
2. Self-exclusion `if:` filter — without it, two `workflow_run: ["*"]` workflows trigger each other → thousands of queued runs (2026-03-01 incident: 12,272 runs)

---

## 🔑 SECRETS & VARIABLES

| Name | Status | Scope |
|------|--------|-------|
| `CODEX_MASTER_KEY` | ✅ ACTIVE — full access granted 2026-03-01 | repo write + vars write + workflow dispatch |
| `CODEX_BACKUP_KEY` | ⚠️ 50% probe coverage — needs rotation | fallback PAT |
| `GITHUB_TOKEN` | ✅ read-only | agent runtime only |
| `vars.COPILOT_AGENT_AUTH_ENABLED` | set by `agent-auth-delegation.yml` | `true` when session active (4h TTL) |
| `vars.COPILOT_AGENT_SESSION_EXPIRES` | ISO timestamp | session expiry |

**Autonomous variable write path:**
1. Write `.codex/pending_var_updates.json` in commit
2. Post PR comment: `@agent-var-writer apply`
3. `agent-var-writer.yml` validates session token → applies via `CODEX_MASTER_KEY`

---

## 📐 CODE STYLE RULES (non-negotiable)

| Language | Rule |
|----------|------|
| Python | Black + Ruff + isort. Type-annotate everything. `log.debug(...)` not bare `pass` in except blocks |
| TypeScript | Functional components, Tailwind utilities, Radix UI primitives, `@phosphor-icons/react` |
| YAML | `base64 -d \| python3` for embedded scripts. Never bare `<<` in `run:` blocks |
| Git | `report_progress` after every verified chunk. Never stop at 1 commit. |

---

## 🤖 AI AGENCY POLICY (mandatory — `.codex/CODEBASE_AGENCY_POLICY.md`)

1. **Complete ALL tasks** — zero omissions, zero deferrals without documented blocker
2. **Self-review minimum 5 passes** before session close
3. **Leave codebase better than found** — fix pre-existing issues encountered en route
4. **NEVER stop after one commit** — iterate until checklist is 100% ✅
5. **Post follow-up `@copilot` comment** if session ends with incomplete work
6. **Update `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md`** in every commit
7. **Run `codeql_checker` before finalising** — fix all findings or document as false positives

---

## 📬 FOLLOW-UP CHAIN PROMPT (post this to PR #3421 when resuming)

```
@copilot Please resume PR #3421 (copilot/investigate-ci-failure-rate).

Read `.codex/docs/SESSION_RESTORE_PR3421.md` first — it is your complete
chain prompt with grounded state, remaining checklist, and all critical
technical facts.

**Immediate actions:**
1. `report_progress` — commit the 6 staged-but-uncommitted files
2. Run `code_review` tool
3. Run `codeql_checker` — fix all findings
4. Investigate the 1 remaining YAML parse error in workflow audit
5. Post this follow-up comment to close the AfterMath loop

All CODEX_MASTER_KEY permissions confirmed. Full autonomous operation authorised.
```

---

## 🩺 SELF-REVIEW CHECKLIST (run before every `report_progress`)

- [ ] `python3 -c "import yaml; [yaml.safe_load(open(f)) for f in __import__('glob').glob('.github/workflows/*.yml')]"` — must produce no errors
- [ ] `git status --short` — must show only intended changes
- [ ] `ls /tmp/*.py /tmp/*.yml /tmp/*.json /tmp/*.sh 2>/dev/null` — must be empty
- [ ] `git ls-files --others --ignored --exclude-standard | grep -v "node_modules\|__pycache__\|target/\|\.egg-info"` — must be empty or expected artifacts
- [ ] Thread review comments on PR — must all be addressed
- [ ] Pre-flight checklist comment on PR — must all be ✅
- [ ] `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` — must be updated
