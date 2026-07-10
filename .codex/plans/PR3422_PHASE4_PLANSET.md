# Phase 4 Planset — Cognitive Brain Full Production Wiring
# Aries-Serpent/_codex_ | Target PR: #3422 | Created: 2026-03-01
# Status: READY FOR EXECUTION
# ImprovementAreas: CI_SELF_HEALING, WORKFLOW_HEALTH, AGENT_CHAINING, DOCUMENTATION_HYGIENE

---

## 📋 Executive Summary

**Objective:** Complete the Phase 3 → Phase 4 transition by closing the remaining 5 open items
from PR #3421 and expanding the cognitive brain into full production capability.

**Input State (entering PR #3422):**
```
cli_api_server.py  — 537 lines; CORS ✅ SQLite ✅ OODA endpoints ✅
Frontend hooks     — still call mock-api-client (localhost:8000) for memory/quantum state
React dashboards   — MemoryManagementDashboard: real STM/LTM via use-memory-system ✅ (hook exists)
                   — The hook falls back to MockCodexAPIClient when :8000 unavailable
                   — Fix: point VITE_CODEX_API at :8765 (our FastAPI server)
CI failure rate    — ~30% unknown patterns remain; 7-day telemetry sample needed after merge
Agent fleet        — 59 registered; target 60+
```

**Deliverables:**
- [ ] **P4.1** — `use-memory-system.ts` / `use-quantum-state.ts` / `use-agent-orchestration.ts`
                  point to FastAPI `:8765` via `VITE_CLI_API_URL`; no mock fallback
- [ ] **P4.2** — FastAPI memory endpoints (`GET /api/memory/state`, `GET /api/memory/search`)
                  backed by `CODEX_DB_PATH` SQLite (same DB as CLI history)
- [ ] **P4.3** — Authentication header forwarding: API proxy auto-injects
                  `Authorization: Bearer <CODEX_MASTER_KEY>` for GitHub API calls
- [ ] **P4.4** — xterm.js WebSocket PTY integration — document and wire in React
- [ ] **P4.5** — CI telemetry 7-day report: identify unknown patterns, add 3+ to
                  `collect_telemetry.py` — drive CI failure rate toward <10%
- [ ] **P4.6** — 2 new agent definitions (reach 61 total): `memory-sync-agent.md` +
                  `telemetry-classifier-agent.md`
- [ ] **P4.7** — AGENT_REGISTRY.yaml v1.7.0 (126→128)
- [ ] **P4.8** — CHANGELOG, accountability report, session restore doc updated

---

## Architecture Diagram — Phase 4 Target State

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COGNITIVE BRAIN — PHASE 4 PRODUCTION                  │
│                                                                           │
│  React Frontend (cognitive_app/src/)                                      │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  App.tsx (8 tabs)                                                 │    │
│  │  ┌──────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │    │
│  │  │CliTerminal│ │AgentOrch.   │ │MemoryMgmt    │ │Metrics     │  │    │
│  │  │(xterm.js) │ │Panel        │ │Dashboard     │ │Dashboard   │  │    │
│  │  │/ws/cli ◄─┼─┼─────────────┼─┼──────────────┼─┼─────────── │  │    │
│  │  └──────────┘ └──────────────┘ └──────────────┘ └────────────┘  │    │
│  │       │              │                │               │           │    │
│  │  use-cli-ws    use-agent-orch   use-memory-sys  use-quantum-state │    │
│  │  (P4.4 PTY)    (P4.1 real API)  (P4.1 real API) (P4.1 real API) │    │
│  └────────────────────────┬─────────────────────────────────────────┘    │
│                            │ VITE_CLI_API_URL=http://localhost:8765       │
│  FastAPI Server (cli_api_server.py :8765)                                 │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  /ws/cli          PTY WebSocket (xterm.js P4.4)                    │  │
│  │  /api/request     HTTP proxy + auth-header forwarding (P4.3)       │  │
│  │  /api/cli/run     One-shot execution                                │  │
│  │  /api/cli/history SQLite-backed (CODEX_DB_PATH) ✅ PR #3421        │  │
│  │  /api/ooda/process  CognitiveAppMain.process() ✅ PR #3421         │  │
│  │  /api/ooda/metrics  K1 factor ✅ PR #3421                          │  │
│  │  /api/memory/state  STM/LTM counts ← P4.2 NEW                     │  │
│  │  /api/memory/search  Query memory DB ← P4.2 NEW                   │  │
│  └────────────────────────┬───────────────────────────────────────────┘  │
│                            │                                               │
│  SQLite (CODEX_DB_PATH ~/.codex/cli_history.db)                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  cli_history  (INSERT on run, SELECT on /history) ✅               │  │
│  │  stm_entries  (short-term: last 50 OODA executions) ← P4.2 NEW    │  │
│  │  ltm_entries  (long-term: consolidated patterns) ← P4.2 NEW       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Python Cognitive Layer                                                    │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  OODAOrchestrator.execute()  → stores to stm_entries ← P4.2       │  │
│  │  CognitiveAppMain.process()  → /api/ooda/process ✅                │  │
│  │  MemoryInterface (SQLiteMemory impl) ← P4.2 NEW concrete class    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  GitHub Actions / CI                                                       │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  ci-health-monitor.yml  ← CODEX_CI_FAILURE_RATE ✅                 │  │
│  │  collect_telemetry.py   ← +3 new patterns ← P4.5                  │  │
│  │  cognitive_brain_ci_feedback.yml  ← P-047 ✅                       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔵 P4.1 — Frontend Hook Rewiring (VITE_CLI_API_URL)

**Problem:** `use-memory-system.ts`, `use-quantum-state.ts`, `use-agent-orchestration.ts` all
hit `VITE_CODEX_API` (default `:8000`). Our FastAPI server is at `:8765`.

**Fix — 3 files, 1 env change each:**

### `cognitive_app/src/hooks/use-memory-system.ts`
```typescript
// BEFORE:
const API_URL = import.meta.env.VITE_CODEX_API || 'http://localhost:8000';

// AFTER (P4.1):
const API_URL = import.meta.env.VITE_CLI_API_URL
             ?? import.meta.env.VITE_CODEX_API
             ?? 'http://localhost:8765';
```

### `cognitive_app/src/lib/codex-api-client.ts`
Add `getMemoryState()` call delegation to `/api/memory/state` when base URL is `:8765`:
```typescript
async getMemoryState(): Promise<MemoryStateResponse> {
  // Try real backend first (P4.1)
  const resp = await fetch(`${this.baseUrl}/api/memory/state`);
  if (!resp.ok) throw new Error(`Memory state HTTP ${resp.status}`);
  return resp.json();
}
```

**Files to change:**
- `cognitive_app/src/hooks/use-memory-system.ts` — 1 line (VITE_CLI_API_URL)
- `cognitive_app/src/hooks/use-quantum-state.ts` — 1 line
- `cognitive_app/src/hooks/use-agent-orchestration.ts` — 1 line
- `cognitive_app/.env.example` — document VITE_CLI_API_URL (create if absent)

---

## 🟢 P4.2 — Memory Endpoints (SQLite STM/LTM)

**New endpoints in `cognitive_app/src/server/cli_api_server.py`:**

```python
# Add to _init_history_db():
conn.execute("""
    CREATE TABLE IF NOT EXISTS stm_entries (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        key       TEXT NOT NULL UNIQUE,
        value     TEXT NOT NULL,
        metadata  TEXT,
        timestamp TEXT NOT NULL,
        access_count INTEGER DEFAULT 0
    )
""")
conn.execute("""
    CREATE TABLE IF NOT EXISTS ltm_entries (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        key       TEXT NOT NULL UNIQUE,
        value     TEXT NOT NULL,
        metadata  TEXT,
        pattern_type TEXT,
        confidence REAL DEFAULT 1.0,
        timestamp TEXT NOT NULL
    )
""")

@app.get("/api/memory/state")
async def memory_state():
    """Return STM/LTM counts and cache metrics — drives MemoryManagementDashboard."""
    with _db_lock:
        stm_count = _db.execute("SELECT COUNT(*) FROM stm_entries").fetchone()[0]
        ltm_count = _db.execute("SELECT COUNT(*) FROM ltm_entries").fetchone()[0]
    return {
        "stm_count": stm_count,
        "ltm_count": ltm_count,
        "capacity": 1000,
        "cache_hit_rate": 0.0,       # updated by OODA loop writes
        "compression_rate": 0.0,     # ltm / (stm + ltm)
        "patterns": [],
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/api/memory/search")
async def memory_search(q: str = "", limit: int = 20):
    """Full-text search over STM + LTM — drives MemoryManagementDashboard search."""
    with _db_lock:
        rows = _db.execute(
            "SELECT key, value, metadata, 'stm' as tier FROM stm_entries "
            "WHERE key LIKE ? OR value LIKE ? "
            "UNION ALL "
            "SELECT key, value, metadata, 'ltm' as tier FROM ltm_entries "
            "WHERE key LIKE ? OR value LIKE ? "
            "LIMIT ?",
            (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", limit),
        ).fetchall()
    return {"items": [dict(r) for r in rows], "total": len(rows)}
```

**SQLiteMemory concrete class** (in `cli_api_server.py` or new `src/codex/cognitive/sqlite_memory.py`):
```python
class SQLiteMemory(MemoryInterface):
    """Concrete MemoryInterface backed by the same CODEX_DB_PATH SQLite database."""
    def store(self, key, value, metadata=None):
        with _db_lock:
            _db.execute(
                "INSERT OR REPLACE INTO stm_entries (key,value,metadata,timestamp) VALUES (?,?,?,?)",
                (key, json.dumps(value), json.dumps(metadata), datetime.utcnow().isoformat())
            )
            _db.commit()
        return True

    def retrieve(self, key):
        row = _db.execute("SELECT value FROM stm_entries WHERE key=?", (key,)).fetchone()
        return json.loads(row["value"]) if row else None

    def search(self, query, limit=10):
        q = next(iter(query.values()), "")
        rows = _db.execute(
            "SELECT key, value FROM stm_entries WHERE value LIKE ? LIMIT ?",
            (f"%{q}%", limit)
        ).fetchall()
        return [(r["key"], json.loads(r["value"])) for r in rows]

    def delete(self, key):
        with _db_lock:
            _db.execute("DELETE FROM stm_entries WHERE key=?", (key,))
            _db.commit()
        return True
```

Auto-initialize OODA orchestrator with `SQLiteMemory()` in `cli_api_server.py`:
```python
# In ooda_process() — replace stub with real SQLiteMemory:
if not app_instance._orchestrator and _BRAIN_BASE_AVAILABLE:
    from cognitive_app.src.server.cli_api_server import SQLiteMemory
    app_instance.initialize(_Planner(), SQLiteMemory())
```

---

## 🟡 P4.3 — Auth Header Forwarding (CODEX_MASTER_KEY → Bearer)

**Target:** API proxy at `/api/request` auto-injects GitHub auth header when target is `api.github.com`.

**Change in `cli_api_server.py` — `api_proxy()` function (~10 lines):**

```python
# After: headers = dict(req.headers or {})
# Add:
if "api.github.com" in url and "Authorization" not in headers:
    master_key = os.environ.get("CODEX_MASTER_KEY", "")
    backup_key = os.environ.get("CODEX_BACKUP_KEY", "")
    token = master_key or backup_key
    if token:
        headers["Authorization"] = f"Bearer {token}"
        log.debug("Auto-injected GitHub auth header (CODEX_MASTER_KEY)")
```

**Security note:** Tokens from env only; never logged; never returned in response headers.

---

## 🟣 P4.4 — xterm.js WebSocket PTY Integration

**Problem:** `CliTerminal.tsx` currently uses `<textarea>` or custom WebSocket handler.
True xterm.js integration gives real ANSI escape processing, cursor movement, colour.

**Implementation plan:**

### Step 1 — Install xterm.js in cognitive_app
```bash
cd cognitive_app && npm install xterm xterm-addon-fit xterm-addon-web-links
```

### Step 2 — New `cognitive_app/src/components/cli/XtermTerminal.tsx`
```typescript
import { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

const API_BASE = import.meta.env.VITE_CLI_API_URL ?? 'http://localhost:8765';
const WS_BASE  = API_BASE.replace(/^http/, 'ws');

export function XtermTerminal() {
  const containerRef = useRef<HTMLDivElement>(null);
  const termRef      = useRef<Terminal | null>(null);
  const wsRef        = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const term = new Terminal({ cursorBlink: true, theme: { background: '#0d0d0d' } });
    const fit  = new FitAddon();
    term.loadAddon(fit);
    term.open(containerRef.current);
    fit.fit();
    termRef.current = term;

    const ws = new WebSocket(`${WS_BASE}/ws/cli`);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'output') term.write(msg.data);
    };

    term.onData((data) => {
      ws.send(JSON.stringify({ type: 'input', data }));
    });

    const handleResize = () => {
      fit.fit();
      ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      ws.close();
      term.dispose();
    };
  }, []);

  return <div ref={containerRef} className="h-full w-full bg-[#0d0d0d] rounded-md" />;
}
```

### Step 3 — Replace existing CliTerminal with XtermTerminal in App.tsx CLI tab
```typescript
// cognitive_app/src/App.tsx — CLI tab
import { XtermTerminal } from '@/components/cli/XtermTerminal';
// Replace: <CliTerminal />
// With:    <XtermTerminal />
```

---

## 🔴 P4.5 — CI Telemetry: 3 New Pattern Classifiers

**Prerequisite:** PR #3421 merged to `main`; `ci-health-monitor.yml` has been running 7 days.

**Process:**
1. Download `telemetry_report.json` artifact from latest `ci-health-monitor` run
2. Sort `pattern_distribution` by count descending
3. Find top-3 entries still classified as `"unknown"`
4. Add classifier entries to `scripts/ci/collect_telemetry.py`

**Target classifiers to add (based on PR #3421 pre-flight patterns):**

```python
# In collect_telemetry.py — FAILURE_PATTERNS dict extension:
"DATETIME_001": {
    "keywords": ["offset-aware", "offset-naive", "cannot mix"],
    "category": "datetime",
    "batch_fixable": True,
},
"BUILD_001": {
    "keywords": ["license-expression", "pyproject.toml", "SPDX"],
    "category": "build",
    "batch_fixable": False,
},
"PKG_001": {
    "keywords": ["PEP 621", "setuptools", "dynamic"],
    "category": "packaging",
    "batch_fixable": False,
},
```

**Success metric:** `"unknown"` bucket drops from ~60% → <30% after 7-day sample.

---

## 🟤 P4.6 — 2 New Agent Definitions (reach 61 total)

### Agent: `memory-sync-agent.md`
**Purpose:** Syncs `SQLiteMemory` (STM/LTM) with cognitive brain pattern library
- Reads `/api/memory/state` to detect STM overflow
- Consolidates hot STM entries → LTM when STM > 80% capacity
- Tags patterns with ImprovementArea classification
- Prunes LTM entries older than 30 days with confidence < 0.3

### Agent: `telemetry-classifier-agent.md`
**Purpose:** Reads CI telemetry, identifies unknown patterns, proposes classifiers
- Triggers on `ci-health-alert` issues with pattern `"unknown_count > N"`
- Downloads artifact from `ci-health-monitor` run
- Analyzes unknown failure logs with string pattern matching
- Generates `collect_telemetry.py` patch adding new classifier entries
- Creates PR with classifier additions

---

## 📊 Phase 4 Success Metrics

| Metric | Entering P4 | Target P4 Exit |
|--------|-------------|----------------|
| CI failure rate | ~30% | **<10%** |
| "unknown" CI pattern | ~60% | **<20%** |
| Frontend hooks → real API | 0/3 | **3/3** |
| Memory endpoints live | 0/2 | **2/2** |
| Auth header forwarding | ❌ | **✅** |
| xterm.js PTY | ❌ | **✅** |
| Agent count | 59 | **61+** |
| AGENT_REGISTRY.yaml | v1.6.0 | **v1.7.0** |
| MemoryManagementDashboard real data | ❌ | **✅** |

---

## 🗓 Sprint Breakdown

### Sprint 6 — Memory Layer (P4.1 + P4.2)
**Effort:** ~2h | **Blocker:** None

```
Task 6.1: Add /api/memory/state + /api/memory/search to cli_api_server.py
Task 6.2: Add stm_entries + ltm_entries tables to _init_history_db()
Task 6.3: Implement SQLiteMemory concrete class
Task 6.4: Wire VITE_CLI_API_URL into 3 frontend hooks
Task 6.5: Update cognitive_app/.env.example
```

### Sprint 7 — Auth + xterm.js (P4.3 + P4.4)
**Effort:** ~1.5h | **Blocker:** npm install xterm

```
Task 7.1: Auth header forwarding in api_proxy()
Task 7.2: XtermTerminal.tsx component
Task 7.3: Wire XtermTerminal into App.tsx CLI tab
Task 7.4: cognitive_app/package.json: add xterm deps
```

### Sprint 8 — CI Telemetry (P4.5)
**Effort:** ~1h | **Blocker:** 7-day sample on main (post-merge)

```
Task 8.1: Retrieve telemetry artifact via GitHub MCP
Task 8.2: Identify top-3 unknown patterns
Task 8.3: Add classifiers to collect_telemetry.py
Task 8.4: Verify CODEX_CI_FAILURE_RATE drops after classifier deploy
```

### Sprint 9 — Agent Fleet (P4.6 + P4.7)
**Effort:** ~45min | **Blocker:** None

```
Task 9.1: memory-sync-agent.md
Task 9.2: telemetry-classifier-agent.md
Task 9.3: AGENT_REGISTRY.yaml v1.7.0 (126→128)
```

### Sprint 10 — Governance (P4.8)
**Effort:** ~20min | **Blocker:** None

```
Task 10.1: CHANGELOG.md [Unreleased] entry (WF-001 compliance)
Task 10.2: .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md W-061–W-068
Task 10.3: SESSION_RESTORE_PR3422.md chain prompt
Task 10.4: COGNITIVE_BRAIN_STATUS_PR3422.md (this doc, updated)
```

---

## 🔑 Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Single SQLite DB for CLI history + STM/LTM | Avoids file proliferation; consistent CODEX_DB_PATH path; single backup |
| `VITE_CLI_API_URL` instead of `VITE_CODEX_API` | Preserves backward compat with existing :8000 consumers; additive not breaking |
| Auth injection only for `api.github.com` hostname | Security principle of least surprise; never inject for arbitrary URLs |
| xterm.js over custom WebSocket parser | Industry standard; handles ANSI escapes, unicode, resize events correctly |
| `SQLiteMemory` in `cli_api_server.py` not new file | Keeps server self-contained; avoids new import chain during CI phase |
| Pattern classifiers added to existing `collect_telemetry.py` | Minimal change; no new script; single source of truth |

---

## ⚡ GROUNDED Enforcement Additions (Sprint 6–9)

### New Tier-1 gate (agent-auth-delegation.yml REQ-8):
> "Verify `/api/memory/state` returns `stm_count >= 0` before session start"

```yaml
# In agent-auth-delegation.yml — add after REQ-7:
- name: "🧠 REQ-8: Memory system health check"
  id: req8
  run: |
    HTTP=$(curl -sf http://localhost:8765/api/memory/state | python3 -c "
    import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('stm_count',0)>=0 else 1)
    " 2>/dev/null && echo "200" || echo "fail")
    if [ "$HTTP" != "200" ]; then
      echo "::warning::Memory system not responding — GROUNDED soft gate"
    fi
```

---

## 🧠 ImprovementArea Enum Alignment

| Sprint | ImprovementArea | Key Pattern ID |
|--------|----------------|----------------|
| S6 Memory layer | `ML_PATTERN_FEEDING` | P-048 |
| S7 Auth/xterm.js | `CI_SELF_HEALING` | P-047 |
| S8 Telemetry | `CI_SELF_HEALING` | P-047 |
| S9 Agent fleet | `AGENT_CHAINING` | P-049 |

```python
# cognitive_brain_ci_feedback.yml P-048 keywords:
"stm":          ("P-048", ImprovementArea.ML_PATTERN_FEEDING),
"ltm":          ("P-048", ImprovementArea.ML_PATTERN_FEEDING),
"memory":       ("P-048", ImprovementArea.ML_PATTERN_FEEDING),
"consolidat":   ("P-048", ImprovementArea.ML_PATTERN_FEEDING),
```

---

## 🔄 Self-Review Checklist (run before each commit)

```bash
# 1. YAML parse
python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"

# 2. Python AST
python3 -c "import ast; ast.parse(open('cognitive_app/src/server/cli_api_server.py').read())"

# 3. CHANGELOG updated
grep "Unreleased" CHANGELOG.md | head -1

# 4. Accountability report updated
grep "Last updated" docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md

# 5. No /tmp artifacts
ls /tmp/*.py /tmp/*.yml /tmp/*.json 2>/dev/null || echo "clean"

# 6. Git status — no unexpected files
git status --short | grep "^??" | grep -v ".pyc\|__pycache__\|node_modules" || echo "clean"

# 7. AGENT_REGISTRY version matches total
python3 -c "import yaml; d=yaml.safe_load(open('.github/agents/AGENT_REGISTRY.yaml')); print(f'v{d[\"version\"]} | {d[\"total_agents\"]} agents')"
```

---

## 📎 @copilot Continue Prompt (paste as first comment on PR #3422)

```
@copilot Read .codex/plans/PR3422_PHASE4_PLANSET.md for full context.

Phase 4 Cognitive Brain Production Wiring — sprint 6 start.

IMMEDIATE TASKS (in order):
1. P4.2: Add /api/memory/state + /api/memory/search endpoints to cli_api_server.py
2. P4.2: Add stm_entries + ltm_entries SQLite tables in _init_history_db()
3. P4.2: Implement SQLiteMemory(MemoryInterface) class in cli_api_server.py
4. P4.1: Update VITE_CLI_API_URL in use-memory-system.ts / use-quantum-state.ts / use-agent-orchestration.ts
5. P4.3: Auth header forwarding in api_proxy() for api.github.com URLs
6. P4.6: Create memory-sync-agent.md + telemetry-classifier-agent.md
7. P4.7: AGENT_REGISTRY.yaml v1.7.0 (126→128)
8. Governance: CHANGELOG.md + W-061+ in .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md

CRITICAL RULES:
- CHANGELOG.md MUST have [Unreleased] entry BEFORE first commit (WF-001 gate)
- NEVER use python3 -c multiline or << heredoc in GitHub Actions run: blocks
- SQLite writes MUST use _db_lock (threading.Lock)
- VITE_CLI_API_URL not VITE_CODEX_API (backward compat)
- sys.path modified once at module level only
- All 96 workflows must parse cleanly (run compliance check before commit)

Token status: CODEX_MASTER_KEY ✅ 100% | CODEX_BACKUP_KEY ✅ 100% (S117)
```

---

**Version:** 1.0.0
**Created:** 2026-03-01
**Author:** copilot-swe-agent (PR #3421 session)
**Next Review:** After PR #3422 Sprint 6 completion
**Status:** ✅ READY FOR EXECUTION
