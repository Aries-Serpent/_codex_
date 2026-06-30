# Phase 9.1 ⟷ Phase 9.2 Infrastructure Bridge Plan

**Created**: 2026-06-30T16:38:33Z  
**Context**: How Phase 9.1 agents lay groundwork for Phase 9.2 machine-readable documentation infrastructure

---

## 🌉 Integration Architecture

Phase 9.1 (Agents 2-5) and Phase 9.2 (Machine-Readable Docs Infrastructure) are deeply connected:

```
Phase 9.1: Agent Implementation              Phase 9.2: Infrastructure Implementation
────────────────────────────────             ─────────────────────────────────────
Agent 2: test-coverage-enforcer      ──→     JSONL Schema Coverage Validation
Agent 3: dependency-conflict-resolver ──→    docs_agent Tooling Dependencies
Agent 4: security-vulnerability-patcher ──→  MCP Tool Contract Security
Agent 5: service-integration-tester   ──→    MCP Tool Mock HTTP Implementation
```

---

## 📋 Test Coverage Integration (Agent 2 → Phase 9.2 Part 1)

### What Agent 2 Tests
- Coverage threshold enforcement
- Test gap identification & generation
- CI/CD merge gate integration
- Coverage report generation

### What Phase 9.2 Needs Tested
- 8 JSONL record types (Document, Section, Block, Action, Decision, Requirement, Reference, Relationship)
- Schema validation against 8 JSON Schemas
- JSONL line-delimitedness & record completeness
- JSONL record interoperability

### Integration Test Creation (Agent 2)
**File**: `tests/docs_agent/test_schemas.py` (15+ tests)

```python
# Example test pattern from Agent 2 approach
def test_jsonl_schema_document_record():
    """Validate JSONL document record against schema"""
    # Will be used by Phase 9.2 infrastructure

def test_jsonl_record_integrity():
    """Validate record completeness and relationships"""
    # Will validate all 8 record types

def test_schema_version_compatibility():
    """Validate schema evolution patterns"""
    # Prepare for schema versioning in Phase 9.2
```

**Impact**: Phase 9.2 can immediately run Agent 2's schema coverage tests before implementing full infrastructure.

---

## 📦 Dependency Resolution Integration (Agent 3 → Phase 9.2 Part 4)

### What Agent 3 Tests
- Python package version conflicts
- Multi-constraint resolution
- Dependency graph analysis

### What Phase 9.2 Needs Tested
- `tools/docs_agent/` module dependencies (Pydantic, SQLAlchemy, FastAPI for MCP, click, etc.)
- JSONL schema dependencies (dataclass validators, enum types)
- SQLite backend dependencies (sqlite3, FTS)
- MCP server dependencies (starlette, httpx, msgspec)

### Dependency Matrix Creation (Agent 3)
**File**: `tests/deps_agent/test_docs_agent_compatibility.py` (20+ tests)

```python
# Example dependency matrix from Agent 3
DOCS_AGENT_DEPS = {
    "pydantic": ">=2.0",        # For schema validation
    "sqlalchemy": ">=2.0",      # For SQLite ORM
    "click": ">=8.0",           # For CLI
    "fastapi": ">=0.100",       # For MCP server optional
}

def test_docs_agent_dep_resolution():
    """Validate deps can be resolved together"""
    # Phase 9.2 infrastructure can use this matrix

def test_schema_pydantic_compatibility():
    """Validate schemas work with installed Pydantic version"""
    # Critical for JSONL record validation
```

**Impact**: Phase 9.2 starts with validated dependency matrix from Agent 3.

---

## 🔒 Security Integration (Agent 4 → Phase 9.2 Part 6)

### What Agent 4 Tests
- CVE detection & patch selection
- Secret/credential handling
- Security policy enforcement

### What Phase 9.2 Needs Tested
- MCP tool contract security (12 tools):
  - `search_docs`: Input sanitization (SQL injection prevention for FTS)
  - `get_task_brief`: Secret sanitization (no API keys in briefing)
  - `impact_analysis`: Scope validation (no elevation of privilege)
  - All tools: Input validation, output encoding
  
- Secret management in generated MCP configs
- Policy enforcement in governance workflow

### Security Test Creation (Agent 4)
**File**: `tests/mcp_tools/test_security.py` (20+ tests)

```python
def test_search_docs_fts_injection_protection():
    """Validate FTS query escaping prevents injection"""
    # Phase 9.2 MCP search_docs tool will use this pattern

def test_task_brief_no_secrets_in_response():
    """Validate no secrets in get_task_brief output"""
    # Phase 9.2 must pass this security check

def test_mcp_config_secret_exclusion():
    """Validate no secrets in generated Copilot MCP config"""
    # Critical for production deployment
```

**Impact**: Phase 9.2's MCP tools must pass Agent 4's security test suite.

---

## 🌐 MCP Tool Contract Integration (Agent 5 → Phase 9.2 Part 6)

### What Agent 5 Tests
- Service integration testing
- HTTP mock client generation
- End-to-end workflow validation
- API contract compliance

### What Phase 9.2 Needs Tested
- 12 Copilot MCP tools for docs infrastructure:
  1. `get_agent_context` → Project state summary
  2. `search_docs` → FTS search across JSONL
  3. `get_document` → Retrieve document with sections/blocks
  4. `get_related_context` → Find related entities
  5. `get_task_brief` → Classify objective & recommend workflow
  6. `impact_analysis` → Identify affected records
  7. `list_actions` → Query action registry
  8. `validate_docs` → Validate infrastructure
  9. `rebuild_indexes` → Regenerate SQLite/FTS
  10. `update_action_status` → Update task status
  11. `classify_candidate_file` → Classify knowledge-bearing file
  12. `ingest_candidate_file` → Convert to JSONL

### MCP Tool Integration Tests (Agent 5)
**File**: `tests/integration/test_copilot_mcp_tools.py` (25+ tests)

```python
class TestCopilotMCPTools:
    """Mock HTTP clients for all 12 Copilot MCP tools"""
    
    def test_get_agent_context_contract(self):
        """Validate get_agent_context response schema"""
        # Direct reuse in Phase 9.2 MCP server implementation
    
    def test_search_docs_full_workflow(self):
        """Validate search_docs → results → follow-up queries"""
        # Tests the complete search workflow
    
    def test_get_task_brief_with_related_context(self):
        """Validate task_brief includes all required context"""
        # Tests critical Copilot agent workflow
    
    def test_impact_analysis_cascade(self):
        """Validate impact_analysis detects all affected records"""
        # Tests relationship graph traversal
```

**Service Mock Clients** (generated by Agent 5):
```python
# Mock HTTP endpoint generators
class SearchDocsServiceMock:
    """Mock search_docs endpoint"""
    async def search(self, query: str, limit: int = 10) -> dict:
        return {"results": [...]}

class TaskBriefServiceMock:
    """Mock get_task_brief endpoint"""
    async def classify(self, objective: str) -> dict:
        return {"intent": "...", "related_docs": [...]}

# Phase 9.2 can wrap real implementations around these mocks
```

**Impact**: Phase 9.2's MCP server implementation can directly wrap Agent 5's mock clients into production implementations.

---

## 📊 Cognitive Brain Knowledge Transfer

### After Agent 2 (test-coverage-enforcer)
**Patterns Captured**:
- JSONL schema validation patterns
- Coverage enforcement algorithms
- Test gap identification heuristics

### After Agent 3 (dependency-conflict-resolver)
**Patterns Captured**:
- Dependency matrix generation
- Version compatibility checking
- Conflict resolution algorithms
- Schema evolution tracking

### After Agent 4 (security-vulnerability-patcher)
**Patterns Captured**:
- MCP tool security validation patterns
- Secret detection & sanitization
- Input validation patterns (FTS, SQL escaping)
- Security policy enforcement

### After Agent 5 (service-integration-tester)
**Patterns Captured**:
- MCP tool mock implementation patterns
- HTTP client contract validation
- End-to-end workflow testing
- Service integration patterns

**Phase 9.2 Usage**: All patterns automatically available through cognitive brain injection for Phase 9.2 agent implementations (Agents A-I).

---

## 🔄 File Structure Prepared by Phase 9.1

By end of Phase 9.1, these files will exist with patterns Agent 5 establishes:

```
tests/
├─ docs_agent/
│  ├─ test_schemas.py              ← Agent 2 creates (JSONL schemas)
│  └─ test_schema_evolution.py      ← Agent 2 extends
├─ mcp_tools/
│  ├─ test_security.py             ← Agent 4 creates (MCP tool security)
│  └─ test_input_validation.py      ← Agent 4 extends
└─ integration/
   ├─ test_copilot_mcp_tools.py     ← Agent 5 creates (MCP tool contracts)
   ├─ mock_services/                ← Agent 5 generates
   │  ├─ search_docs_service.py
   │  ├─ task_brief_service.py
   │  └─ ... (12 total mock services)
   └─ test_mcp_workflows.py         ← Agent 5 extends
```

**Phase 9.2 Usage**: These files provide direct test templates and mock services for building real Phase 9.2 infrastructure.

---

## 📋 Phase 9.2 Agent Assignments (Preview)

With patterns established by Agents 2-5, Phase 9.2 will distribute work:

| Agent | Task | Depends On |
|-------|------|-----------|
| Agent A (Inventory) | Audit repo, classify candidates, generate reports | Agent 2's test coverage patterns |
| Agent B (Schema) | Design JSONL models, create JSON Schemas | Agent 2's schema coverage tests |
| Agent C (Converter) | Convert Markdown → JSONL, extract structure | Agent 2's coverage + Agent 3's dependency mapping |
| Agent D (Relationships) | Build entity graph, validate relationships | Agent 3's graph analysis patterns |
| Agent E (Validation) | Validate JSONL, detect issues, fix errors | Agent 4's security + Agent 2's coverage |
| Agent F (Query Infrastructure) | Build SQLite, FTS, query layer | Agent 5's service integration patterns |
| Agent G (GitHub Actions) | Create governance workflow, enforce policy | Agent 4's security + Agent 2's validation |
| Agent H (Copilot Tooling) | Implement 12 MCP tools using Agent 5's mocks | Agent 5's mock services directly wrapped |
| Agent I (Cleanup) | Quarantine candidates, generate reports | All previous agents' validation patterns |

---

## 🎯 Success Criteria Bridge

### Phase 9.1 Success
- ✅ 103+ tests passing (Agents 2-5)
- ✅ 90%+ coverage (per agent)
- ✅ 140KB+ documentation (Agents 2-5)
- ✅ 67% average component reuse
- ✅ A+ quality score all agents
- ✅ Patterns captured in cognitive brain

### Phase 9.2 Readiness
- ✅ Test templates available (from Agents 2-5 test suites)
- ✅ Dependency matrix validated (from Agent 3)
- ✅ Security patterns proven (from Agent 4)
- ✅ MCP tool mocks ready (from Agent 5)
- ✅ Cognitive brain patterns loaded (from all agents)
- ✅ Agents A-I can start parallel implementation with templates

---

## 🚀 Handoff Plan

### At End of Phase 9.1
Generate deliverable:
**File**: `.codex/PHASE_9_1_TO_9_2_HANDOFF_SUMMARY.md`

Must include:
1. All test file locations (Agents 2-5 test suites)
2. All reusable patterns (from cognitive brain)
3. All mock service implementations (from Agent 5)
4. Dependency matrix (from Agent 3)
5. Security patterns (from Agent 4)
6. Schema coverage tests (from Agent 2)
7. Exact commands for Phase 9.2 Agents A-I to start work
8. Validation checklist for Phase 9.2 preconditions

### Phase 9.2 Kickoff
Agents A-I will:
1. Load Phase 9.1 patterns from cognitive brain
2. Run Phase 9.1 test suites to validate setup
3. Use mock services from Agent 5 as starting templates
4. Run dependency resolution from Agent 3
5. Execute security validation from Agent 4
6. Cover new infrastructure code using Agent 2's patterns
7. Begin parallel Phase 9.2 infrastructure implementation

---

## 📞 Authority & Approval

**Phase 9.1 Authority**: @mbaetiong D-tier (confirmed 2026-06-27)
**Phase 9.2 Authority**: Same @mbaetiong D-tier extends to Phase 9.2 per approval scope

**No renegotiation needed** — Approval already granted for "all plan phase steps planned and unplanned."

---

## 📄 Document Status

**Version**: 1.0  
**Created**: 2026-06-30T16:38:33Z  
**Status**: ✅ BRIDGE PLAN COMPLETE

**Next Step**: Execute Phase 9.1 (Agents 2-5) immediately with full infrastructure integration awareness.

---

*Phase 9.1 ⟷ Phase 9.2 Infrastructure Bridge*  
*Establishes foundation for comprehensive machine-readable documentation system*
