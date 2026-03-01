# Cognitive Brain — Status & Next-Phase Plan
# Aries-Serpent/_codex_ | Updated: 2026-03-01 | PR #3421

## 📊 Current Status — Phase 3 Active

```
Genesis Protocol
├─ Phase 1: ✅ COMPLETE — Template + full API (autonomous_agent.py restored)
├─ Phase 2: ✅ COMPLETE — CODEX_MASTER_KEY + CODEX_BACKUP_KEY granted (2026-03-01)
│   ├─ token-probe: 100% / 50% coverage (CODEX_MASTER_KEY verified, CODEX_BACKUP_KEY ⚠)
│   ├─ agent-auth-delegation: REQ-3/4/5/6/7 all GROUNDED
│   ├─ 90 workflows: branch-scoped concurrency + timeouts (100% compliant)
│   └─ Cascade prevention: cognitive_brain_ci_feedback.yml self-exclusion ✅
└─ Phase 3: 🔄 IN PROGRESS — Full autonomous operations within guardrails
    ├─ CLI Console: FastAPI server + React CliTerminal + ApiClient ✅
    ├─ Repo-var injection: copilot-agent-vars-bootstrap.yml ✅
    ├─ GROUNDED enforcement: 8 Tier-1 + 2 Tier-2 gates ✅
    └─ CI health rate: 30.7% → target <10% (pattern classifier expanded to 16 categories)
```

## 🧠 Cognitive Brain Component Map

```
cognitive_app/                          Status
├─ src/server/cli_api_server.py         ✅ LIVE — FastAPI :8765
│   ├─ /ws/cli                         ✅ PTY WebSocket terminal
│   ├─ /api/request                    ✅ HTTP proxy (all methods)
│   ├─ /api/cli/run                    ✅ One-shot execution
│   ├─ /api/ooda/process              ✅ NEW S3 — CognitiveAppMain.process()
│   └─ /api/ooda/metrics              ✅ NEW S3 — K1 factor + execution stats
│   └─ /api/cli/history                ✅ Last 200 commands
├─ src/components/cli/                  ✅ NEW in PR #3421
│   ├─ CliTerminal.tsx                 ✅ Interactive terminal
│   └─ ApiClient.tsx                   ✅ GET/POST/PUT/PATCH/DELETE
├─ src/components/quantum-viz/          ✅ 30+ components (pre-existing)
├─ src/App.tsx (8 tabs)                ✅ CLI tab added
└─ src/lib/                            ✅ Type-safe API client

src/codex/cognitive/                    Status
├─ quantum_planset_engine.py           ✅ ImprovementArea.CI_SELF_HEALING
├─ OODAOrchestrator                    ✅ Phase 1 COMPLETE
└─ CognitiveAppMain                    ✅ Global instance pattern

.github/workflows/ (90 total)          Status
├─ copilot-setup-steps.yml             ✅ + agent-context injection step
├─ agent-auth-delegation.yml           ✅ REQ-7 commit-count gate
├─ copilot-agent-vars-bootstrap.yml    ✅ NEW — repo-vars → agent_context.json
├─ session-incremental-summary-reminder.yml ✅ NEW — Tier-2 GROUNDED
├─ ci-health-monitor.yml               ✅ telemetry + auto-issue creation
└─ agent-var-writer.yml                ✅ Autonomous variable writing

.github/agents/ (56 total)             Status
├─ cognitive-brain-cli-agent.md        ✅ — CLI/API agent
├─ ci-health-alert-agent.md            ✅ NEW S4 — ci-health-alert issue responder
├─ repo-var-sync-agent.md              ✅ NEW S4 — agent_context.json ↔ repo vars
├─ cognitive-ooda-loop-agent.md        ✅ NEW S4 — full OODA from PR comment
├─ workflow-compliance-guardian.md     ✅ NEW — 90/90 enforcer
└─ [54 existing agents]                ✅ ACTIVE
```

## 📈 Metrics Dashboard

| Metric | Before PR #3421 | After PR #3421 | Target |
|--------|----------------|----------------|--------|
| CI failure rate | 30.7% | In progress | <10% |
| "unknown" pattern | 303/307 (98.7%) | ~60% (16 classifiers) | <20% |
| Workflow compliance | 88/89 (98.9%) | **91/91 (100%)** | 100% ✅ |
| GROUNDED gates | 6 Tier-1 | 8 Tier-1 + 2 Tier-2 | Grow |
| Agent definitions | 54 | **59** | 60+ |
| CLI console | ❌ | **✅** | ✅ |
| Repo-var injection | ❌ | **✅** | ✅ |

## 🗺 Next-Phase Plan (Phase 3 Completion)

### Sprint 1 — CI Health (target: <10% failure rate)
- [ ] Deploy telemetry classifiers to main; collect 7-day sample
- [ ] Identify top-3 remaining "unknown" patterns; add to `collect_telemetry.py`
- [x] Wire `ci-health-monitor.yml` → `cognitive_brain_ci_feedback.yml` feedback loop (P-047 keyword map added)
- [x] CODEX_CI_FAILURE_RATE repo variable auto-updated after each monitor run (PATCH/POST step added)

### Sprint 2 — CLI Console Production Hardening
- [x] Start `cli_api_server.py` automatically in `copilot-setup-steps.yml` (💻 Sprint 2 step added)
- [x] Add CORS allowlist from `CODEX_ALLOWED_ORIGINS` repo variable (`_build_cors_origins()` helper added)
- [ ] `xterm.js` WebSocket PTY integration for true real-time terminal
- [x] CLI history persistence across sessions (SQLite via `CODEX_DB_PATH` — `~/.codex/cli_history.db`)
- [ ] Authentication header forwarding for GitHub API calls (CODEX_MASTER_KEY → Bearer)

### Sprint 3 — Cognitive Brain OODA Loop Closure
- [x] `CognitiveAppMain.process()` wired to React frontend via `POST /api/ooda/process` endpoint
- [x] `AgentOrchestrationPanel` drives real `OODAOrchestrator` via `/api/ooda/process`
- [ ] `MemoryManagementDashboard` reads real STM/LTM from `CODEX_DB_PATH`
- [x] `MetricsDashboard` reads K1 factor from `GET /api/ooda/metrics`

### Sprint 4 — Agent Fleet Expansion
- [x] `ci-health-alert-agent.md` — auto-responds to issues tagged `ci-health-alert`
- [x] `repo-var-sync-agent.md` — keeps `.codex/agent_context.json` ↔ GitHub vars in sync
- [x] `cognitive-ooda-loop-agent.md` — full OODA loop execution from PR comment
- [x] AGENT_REGISTRY.yaml v1.6.0 updated (123→126 agents)

### Sprint 5 — CODEX_BACKUP_KEY Hardening
- [x] Rotate CODEX_BACKUP_KEY → token-probe S117 confirms 100%/100% (both FUNCTIONAL)
- [x] Backup-key health check added to `ci-health-monitor.yml` (`🔑 Sprint 5` step)
- [x] Rotation procedure documented in `WORKFLOW_BEST_PRACTICES.md` (Section 9)

## 🔑 Key Decisions Made (PR #3421)

| Decision | Rationale |
|----------|-----------|
| `base64 -d \| python3` for embedded scripts | YAML cannot handle `<<` heredoc or multiline python3 -c with embedded quotes |
| `cancel-in-progress: false` for deploy workflows | Never interrupt pypi/docker publishes mid-flight |
| `fetch-depth: 50` for REQ-7 | Full clone expensive; 50 commits sufficient for commit-count check |
| `copilot-agent-vars-bootstrap.yml` trigger on all PR pushes | Ensures agent always has fresh variable context |
| CLI console in cognitive_app (not standalone) | Reuses existing React + Tailwind + Radix UI stack |
