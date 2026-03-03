# 🧠 PR #3422 — Phase 4 Completion Chain Prompt

**PR**: [#3422](https://github.com/Aries-Serpent/_codex_/pull/3422)  
**Branch**: `copilot/add-sqlite-memory-integration`  
**Status**: Phase 4 COMPLETE — Phase 5 ready  
**Generated**: 2026-03-01 (Phase 4 session close)  
**Last commit**: Phase 4 full agency execution (bandit fix + status docs + agent v2.0 upgrades)

---

## 📋 Context Restoration

Read these files in order to restore full context:

```bash
cat .codex/plans/PR3422_PHASE4_PLANSET.md           # Phase 4 plan
cat docs/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR3422.md  # completion summary
cat .github/agents/AGENT_REGISTRY.yaml | head -5    # registry state (v1.7.0 / 128 agents)
cat CHANGELOG.md | head -50                          # [Unreleased] PR #3422 entries
```

---

## ✅ Phase 4 Completed (PR #3422)

| Sprint | Item | File | Done |
|--------|------|------|------|
| S6 | `stm_entries` + `ltm_entries` SQLite tables | `cli_api_server.py` | ✅ |
| S6 | `SQLiteMemory` class + OODA auto-init | `cli_api_server.py` | ✅ |
| S6 | `GET /api/memory/state` + `GET /api/memory/search` | `cli_api_server.py` | ✅ |
| S6 | `VITE_CLI_API_URL` in 3 hooks + `.env.example` | hooks + env | ✅ |
| S7 | Auth header forwarding (`CODEX_MASTER_KEY → Bearer`) | `cli_api_server.py` | ✅ |
| S7 | `XtermTerminal.tsx` + `App.tsx` wiring | React CLI tab | ✅ |
| S8 | 3 new telemetry classifiers | `collect_telemetry.py` | ✅ |
| S9 | `memory-sync-agent.md` v2.0 (diagram + impl) | `.github/agents/` | ✅ |
| S9 | `telemetry-classifier-agent.md` v2.0 (diagram + impl) | `.github/agents/` | ✅ |
| S9 | `cognitive-ooda-loop-agent.md` v2.0 (Phase 4 wiring) | `.github/agents/` | ✅ |
| S9 | `AGENT_REGISTRY.yaml` v1.7.0 (126→128) | registry | ✅ |
| S10 | REQ-8 GROUNDED gate (base64-encoded, decoded comment) | `agent-auth-delegation.yml` | ✅ |
| S10 | `COGNITIVE_BRAIN_STATUS_PR3422.md` | `docs/cognitive_brain/status/` | ✅ |
| S10 | `COGNITIVE_BRAIN_STATUS_V2.md` Phase 40 entry | `cognitive_app/` | ✅ |
| Sec | Bandit B603 `# nosec` with justification | `cli_api_server.py` | ✅ |
| Qual | `datetime.now(timezone.utc)` in new code | `cli_api_server.py` | ✅ |
| Qual | `MEMORY_CAPACITY` configurable constant | `cli_api_server.py` | ✅ |
| Qual | `console.warn` in XtermTerminal.tsx catch | `XtermTerminal.tsx` | ✅ |
| Gov | `CHANGELOG.md` `[Unreleased]` entry | `CHANGELOG.md` | ✅ |
| Gov | W-061–W-069 in `AGENT_ACCOUNTABILITY_REPORT.md` | accountability report | ✅ |

---

## 🚀 Phase 5 — Immediate Tasks (Next Session)

**CRITICAL RULES (from stored memory):**
- YAML embedded Python: `echo '<b64>' | base64 -d | python3` ONLY — never multiline `python3 -c`
- SQLite writes: always use `_db_lock` (threading.Lock)
- CHANGELOG.md MUST have `[Unreleased]` BEFORE first commit
- AGENT_ACCOUNTABILITY_REPORT.md MUST be touched in every commit
- All 96 workflows must YAML-parse before commit

### Sprint 11 — Memory Consolidation REST API
```
Task 11.1: Add POST /api/memory/consolidate to cli_api_server.py
  - Triggers SQLiteMemory.consolidate(): moves hot stm_entries → ltm_entries
  - Accepts: { "dry_run": bool, "threshold": float }
  - Returns: { "consolidated": N, "pruned": N, "stm_count_after": N }

Task 11.2: Increment access_count on SQLiteMemory.retrieve()
  - UPDATE stm_entries SET access_count = access_count + 1 WHERE key = ?
  - Enables Memory Sync Agent hotness detection

Task 11.3: Add GET /api/memory/ltm endpoint
  - Returns paginated LTM entries with confidence + pattern_type
  - Drives future LTM browser panel in MemoryManagementDashboard
```

### Sprint 12 — CI Self-Healing Verification
```
Task 12.1: After PR #3422 merges → wait 7 days for telemetry cycle
Task 12.2: Check CODEX_CI_FAILURE_RATE repo variable (target: <10%)
Task 12.3: If unknown bucket still > 20%: run Telemetry Classifier Agent
Task 12.4: Add ci-health-alert issue auto-opener to ci-health-monitor.yml
  (triggers when unknown_count > 10 in pattern_distribution)
```

### Sprint 13 — Auth Security Hardening
```
Task 13.1: Add CODEX_ALLOWED_GITHUB_ORGS env guard in api_proxy()
  - Only inject auth token when URL org matches allowlist
  - Default: ["Aries-Serpent"]

Task 13.2: Rate-limit /api/request — 10 req/s per origin (use SlowAPI or asyncio.Semaphore)

Task 13.3: Add POST /api/memory/store endpoint
  - External STM writes via REST (needed for agent-to-agent memory sharing)
  - Body: { "key": str, "value": any, "metadata": any }
```

### Sprint 14 — Agent Fleet (reach 130)
```
Task 14.1: .github/agents/self-healing-monitor-agent.md
  - Orchestrates: Memory Sync → Telemetry Classifier → OODA loop
  - Activation: CODEX_CI_FAILURE_RATE transitions to "critical"

Task 14.2: .github/agents/api-proxy-audit-agent.md
  - Logs all /api/request calls to LTM with url, method, status, duration
  - Detects anomalous patterns (same URL hit > 100x/hour)

Task 14.3: AGENT_REGISTRY.yaml v1.8.0 (128→130)
```

### Sprint 15 — Phase 5 Governance
```
Task 15.1: CHANGELOG.md [Unreleased] — PR #3423 entry
Task 15.2: AGENT_ACCOUNTABILITY_REPORT.md W-070+
Task 15.3: SESSION_RESTORE_PR3423.md chain prompt
Task 15.4: COGNITIVE_BRAIN_STATUS_V2.md Phase 41 entry
```

---

## 🔑 Critical Technical State

| Item | Current Value |
|------|--------------|
| FastAPI server | `:8765` (VITE_CLI_API_URL) |
| SQLite DB path | `CODEX_DB_PATH` → `~/.codex/cli_history.db` |
| Memory capacity | `CODEX_MEMORY_CAPACITY` → 1000 (default) |
| Auth token env | `CODEX_MASTER_KEY` (primary) → `CODEX_BACKUP_KEY` (fallback) |
| Auth scope | `api.github.com` only |
| Agent registry | v1.7.0 / 128 agents |
| CI failure rate | ~30% → target <10% after Sprint 12 |
| Unknown patterns | ~60% → <20% with 3 new classifiers |
| AAIS score | 98.0/100 |

---

## 🛡 Self-Review Protocol (5 passes before each commit)

```bash
# Pass 1: Python AST
python3 -c "import ast; ast.parse(open('cognitive_app/src/server/cli_api_server.py').read()); print('AST OK')"

# Pass 2: YAML parse
python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]; print('YAML OK')"

# Pass 3: CHANGELOG + accountability
grep 'Unreleased' CHANGELOG.md | head -1
grep 'Last updated' docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md | head -1

# Pass 4: Clean tmp
ls /tmp/*.py /tmp/*.yml /tmp/*.json 2>/dev/null || echo 'clean'

# Pass 5: Registry version
python3 -c "import yaml; d=yaml.safe_load(open('.github/agents/AGENT_REGISTRY.yaml')); print(f'v{d[\"version\"]} | {d[\"total_agents\"]} agents')"
```

---

## 📎 Follow-Up @copilot Comment Template

```
@copilot Read .github/copilot-prompts/active/PR-3422-followup.md for Phase 5 context.

Phase 5 — Sprint 11-15 start.

IMMEDIATE TASKS (in order):
1. Sprint 11: POST /api/memory/consolidate + access_count increment + GET /api/memory/ltm
2. Sprint 12: After merge, verify CODEX_CI_FAILURE_RATE < 10%; auto-opener for ci-health-alert
3. Sprint 13: CODEX_ALLOWED_GITHUB_ORGS guard + rate-limit /api/request
4. Sprint 14: self-healing-monitor-agent.md + api-proxy-audit-agent.md; AGENT_REGISTRY v1.8.0
5. Sprint 15: Governance — CHANGELOG + W-070+ + SESSION_RESTORE_PR3423.md

CRITICAL RULES:
- CHANGELOG.md [Unreleased] entry BEFORE first commit
- NEVER python3 -c multiline in GitHub Actions run: blocks (use base64)
- SQLite writes MUST use _db_lock
- AGENT_ACCOUNTABILITY_REPORT.md touched every commit
- 5-pass self-review before session close

Token status: CODEX_MASTER_KEY ✅ | CODEX_BACKUP_KEY ✅
```

---

**Version:** 1.0.0 Phase 5 ready  
**Created:** 2026-03-01 (Phase 4 session close)  
**Author:** copilot-swe-agent (PR #3422)  
**Next:** PR #3423 Sprint 11–15
