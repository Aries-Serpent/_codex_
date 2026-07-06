# Lane 3 Brief: Cognitive Brain Runtime Packaging

**Lane 3 Owner:** `cognitive-brain-cli-agent`  
**Duration:** Days 3-9 (Phase 1) + Days 10-14 (Phase 2)  
**Authority:** @mbaetiong D-tier approved  
**Phase 0 Decision Leverage:** Strategic Decision #4 (Cognitive engine export API)

---

## 🎯 Lane 3 Objective

Extract cognitive brain as a portable, locally-deployable runtime with stable APIs for OODA loop orchestration, session management, and pattern recognition—all operating in offline-safe mode by default.

---

## 📋 Deliverables

### Phase 1 (Days 3-9)

1. **Cognitive Engine Core Module** (`codex.cognitive_brain`)
   - Stable, public API for:
     - OODA loop execution (observe, orient, decide, act)
     - Session context management (preserve state across interruptions)
     - Short-term & long-term memory systems
     - Pattern recognition and decision logging
   - All offline-safe: No external API calls in core path
   - Import-time network safety: No network at `from codex.cognitive_brain import OODA`

2. **Portable API Specification**
   - Public classes:
     ```python
     from codex.cognitive_brain.ooda import OODA, OODAPhase, DecisionContext
     from codex.cognitive_brain.session import SessionContext, SessionManager
     from codex.cognitive_brain.memory import ShortTermMemory, LongTermMemory, MemoryConsolidation
     ```
   - Detailed docstrings with usage examples
   - Type hints throughout (Python 3.12 compatible)
   - No breaking changes post-release (semantic versioning)

3. **CLI Interface** (`codex-cognitive` entrypoint)
   - Commands:
     - `codex-cognitive run --config config.yaml` — Execute OODA loop
     - `codex-cognitive session list` — List sessions
     - `codex-cognitive session resume <session-id>` — Resume session
     - `codex-cognitive health` — Cognitive engine health check
   - All commands work offline (default: `CODEX_NETWORK_MODE=isolated`)

4. **Local Persistence Layer**
   - SQLite backend for session state, memory, decision logs
   - Default storage: `~/.codex/cognitive.db`
   - Configurable via environment: `CODEX_DB_PATH=/custom/path.db`
   - No remote state syncing (offline-only)
   - Connection pooling for concurrent access

### Phase 2 (Days 10-14)

5. **Network Isolation Hardening**
   - No external API calls in core cognitive module
   - Any network-dependent features (webhooks, external APIs) are behind explicit opt-in
   - Default config: `CODEX_NETWORK_MODE=isolated` (enforced)
   - PolicyViolationError raised for unapproved outbound requests (from Lane 4)

6. **API Documentation & Examples**
   - Docstrings for all public classes and methods
   - Usage example: Custom OODA loop in external application
   - Integration guide: Embedding cognitive engine in external projects
   - API reference: Complete method signatures and return types

---

## 🚀 Execution Roadmap

### Days 3-4: API Extraction & Stabilization

**Task 3.1: Public API Definition**
- Review current cognitive_brain modules:
  - `ooda.py`: OODA loop executor
  - `session.py`: Session context management
  - `memory.py`: STM/LTM consolidation
  - `patterns.py`: Pattern recognition
  - `decision_log.py`: Decision recording
- Mark classes/methods as public (export) vs internal (exclude)
- Output: API manifest (list of public symbols)

**Task 3.2: Documentation & Type Hints**
- Add docstrings to all public classes/methods (Google style)
- Add type hints to function signatures (Python 3.12)
- Include usage examples in docstrings
- Output: Annotated API definitions

**Task 3.3: Offline-Safety Audit**
- Scan cognitive_brain source for network calls
- Identify any `requests`, `httpx`, `urllib` usage
- Refactor to make import-time safe:
  - Move network calls to explicit functions with guards
  - Wrap in `@requires_network` decorator (from safety module)
  - Document which features require network (none in core)
- Output: Offline-safety verification report

### Days 5-6: CLI Development

**Task 3.4: CLI Architecture**
- Design CLI command structure:
  ```python
  # codex/cognitive_brain/cli.py
  @click.group()
  def main():
      """Cognitive brain runtime CLI"""
  
  @main.command()
  @click.option('--config', default='config.yaml')
  def run(config):
      """Execute OODA loop"""
  
  @main.command()
  def session():
      """Manage sessions"""
  
  @main.command()
  def health():
      """Health check"""
  ```
- Integrate with Typer or Click for CLI framework
- Output: CLI design specification

**Task 3.5: CLI Commands Implementation**
- Implement `codex-cognitive run`: Execute OODA loop from config file
- Implement `codex-cognitive session list`: List all sessions
- Implement `codex-cognitive session resume <session-id>`: Resume interrupted session
- Implement `codex-cognitive health`: Check engine health (memory usage, error rate, etc.)
- Each command: Test in isolation, verify works offline

### Days 7-8: Local Persistence

**Task 3.6: SQLite Setup**
- Database schema:
  ```sql
  CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    config JSONB,
    state JSONB
  );
  
  CREATE TABLE decisions (
    decision_id TEXT PRIMARY KEY,
    session_id TEXT,
    phase TEXT,  -- observe, orient, decide, act
    timestamp TIMESTAMP,
    context JSONB,
    result JSONB,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
  );
  
  CREATE TABLE memory (
    memory_id TEXT PRIMARY KEY,
    session_id TEXT,
    type TEXT,  -- stm or ltm
    entry JSONB,
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
  );
  ```
- Storage location: `~/.codex/cognitive.db` (configurable)
- Connection pooling: Allow multiple processes (optional)

**Task 3.7: Session Management**
- Create session: `SessionManager.create(session_id='...')`
- Load session: `SessionManager.load(session_id='...')`
- Save session: `session.save()` (auto-called after each OODA phase)
- Resume session: `SessionManager.resume(session_id='...')` (restore state)
- All operations: Offline-only, no network calls

### Day 9: Testing & Validation

**Task 3.8: Integration Testing**
- Test OODA loop execution with local config file
- Test session save/resume cycle
- Test CLI entrypoints: `codex-cognitive --version`, etc.
- Verify offline mode: No network calls with `CODEX_NETWORK_MODE=isolated`
- Output: Integration test report

---

## 🔗 Cross-Lane Dependencies

### Lane 3 ← Lane 1 (Cognitive Runtime ← Packaging)

**Dependency:** Lane 1 defines runtime profile, Lane 3 validates it matches
- Lane 1 specifies which modules go in runtime profile (cognitive_brain + utils)
- Lane 3 confirms extracted APIs fit within profile scope
- **Sync Point:** Day 6, Lane 3 reviews Lane 1 module list, confirms alignment

### Lane 3 ← Lane 2 (Cognitive Runtime ← Offline Bootstrap)

**Dependency:** Lane 2 identifies import-time network calls, Lane 3 fixes them
- Lane 2 audit flags any problematic imports in cognitive modules
- Lane 3 refactors to make import-safe
- **Sync Point:** Day 5, Lane 2 shares audit report with Lane 3

### Lane 3 → Lane 4 (Cognitive Runtime → Network Policy)

**Dependency:** Lane 3 identifies network-dependent features, Lane 4 enforces policy
- Lane 3 documents which features require network (e.g., webhooks)
- Lane 4 adds PolicyViolationError guards for network features
- **Sync Point:** Day 7, Lane 3 provides list of network-dependent features to Lane 4

### Lane 3 → Lane 5 (Cognitive Runtime → Documentation)

**Dependency:** Lane 5 documents cognitive engine APIs and CLI
- Lane 5 waits for finalized API spec from Lane 3 (by Day 9)
- Lane 5 writes integration guide + CLI examples (Phase 3)
- **Sync Point:** Lane 3 delivers API specification doc by Day 9

### Lane 3 → Lane 6 (Cognitive Runtime → Validation)

**Dependency:** Lane 6 validates cognitive engine in offline mode
- Lane 6 tests `codex-cognitive run` in isolated network (Phase 4)
- Lane 3 ensures all CLI commands work offline
- **Sync Point:** Lane 6 has finalized CLI by Phase 2 Day 14

---

## ✅ Acceptance Criteria

| Criterion | Validation | Owner |
|-----------|-----------|-------|
| OODA API exported & stable | All OODA classes/methods public, documented | cognitive-brain-cli-agent |
| Session API exported & stable | All SessionContext/SessionManager methods public, documented | cognitive-brain-cli-agent |
| Memory API exported & stable | All STM/LTM/consolidation methods public, documented | cognitive-brain-cli-agent |
| No import-time network calls | Audit confirms cognitive module safe to import offline | cognitive-brain-cli-agent |
| CLI entrypoints work | `codex-cognitive run`, `session`, `health` all functional | cognitive-brain-cli-agent |
| Local persistence operational | SQLite backend stores/retrieves sessions correctly | cognitive-brain-cli-agent |
| Offline mode enforced | CODEX_NETWORK_MODE=isolated blocks network attempts | cognitive-brain-cli-agent |
| Phase 1 gate (Day 9) | API extraction 80%+ complete, CLI functional | orchestrator-agent |
| Phase 2 gate (Day 14) | Offline isolation hardened, all tests passing | orchestrator-agent |

---

## 📌 Key Decisions from Phase 0

**Strategic Decision #4: Cognitive engine export API**
- ✅ APPROVED in INTELLIGENCE_CAMPAIGN_BASELINE.md
- Export: OODA, SessionContext, Memory systems (core logic)
- Exclude: Internal scaffolding, GitHub integrations, webhook ingress
- API stability: Semantic versioning, no breaking changes

---

## 🛠️ Tools & Commands

```bash
# Build cognitive engine wheel
python -m build --wheel

# Install
pip install dist/codex-core-0.1.0.whl

# Test CLI
codex-cognitive --version
codex-cognitive health
codex-cognitive run --config test-config.yaml

# Test API
python -c "from codex.cognitive_brain import OODA; print(OODA.__doc__)"

# Offline test (block network)
CODEX_NETWORK_MODE=isolated codex-cognitive health
```

---

## 📞 Escalation

**API Stability Issues?** Report to orchestrator-agent with:
- API issue description (breaking change risk, stability concern)
- Affected classes/methods
- Proposed resolution (refactor, mark as internal, document constraint)

**Example:**
> Issue: SessionContext.__init__ signature changed (added required parameter). Risk: Breaking change for external users. Resolution: Add backward-compatible default parameter, deprecation warning for old signature.

