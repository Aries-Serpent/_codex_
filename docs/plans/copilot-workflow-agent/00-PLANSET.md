# Copilot Workflow Agent - Master Planset

> Generated: 2024-12-16 | Version: 1.0.0  
> Purpose: Master implementation roadmap with phases, milestones, and success criteria

## Executive Summary

Build a GitHub Copilot Workflow Agent that autonomously manages CI/CD lifecycle including:
- **Workflow Discovery**: Scan and index all workflow files
- **Workflow Triggering**: Start workflows via `workflow_dispatch`
- **Status Monitoring**: Poll run status and detect failures
- **Self-Healing**: Automatically remediate common failures
- **Result Delivery**: Report outcomes across sessions
- **Approval Gates**: Enforce policies for high-risk actions

## Phase Overview

| Phase | Name | Duration | Status |
|-------|------|----------|--------|
| 0 | Foundation & Planning | 1 week | ⏳ IN PROGRESS |
| 1 | Core Components | 2 weeks | 🔜 PENDING |
| 2 | Self-Healing Engine | 2 weeks | 🔜 PENDING |
| 3 | User Experience | 1 week | 🔜 PENDING |
| 4 | Production Hardening | 1 week | 🔜 PENDING |

---

## Phase 0: Foundation & Planning

### Objectives
- Document architecture and data models
- Create plan structure (planset, batchset, patchset)
- Set up checkpoint and continuation system
- Validate existing infrastructure

### Deliverables

| Deliverable | File | Status |
|-------------|------|--------|
| Plan directory structure | `docs/plans/copilot-workflow-agent/` | ✅ DONE |
| Master planset | `00-PLANSET.md` | ✅ DONE |
| Work batches | `01-BATCHSET.md` | ⏳ IN PROGRESS |
| Patch prompts | `02-PATCHSET.md` | ⏳ IN PROGRESS |
| Architecture doc | `03-ARCHITECTURE.md` | ⏳ IN PROGRESS |
| Checkpoint system | `08-CHECKPOINTS.md` | ⏳ IN PROGRESS |

### Acceptance Criteria
- [ ] All plan documents created
- [ ] Architecture validated against existing codebase
- [ ] Checkpoint IDs assigned to each phase
- [ ] Continuation prompts documented

### Checkpoint: `PHASE0-COMPLETE`

---

## Phase 1: Core Components

### Objectives
- Implement GitHub API client wrapper
- Create workflow inventory and parser
- Build session state management
- Implement workflow trigger API

### Components

#### 1.1 GitHub API Client (`src/services/github/client.py`)
```python
class GitHubClient:
    """Thin, testable wrapper around GitHub REST/GraphQL."""
    
    async def trigger_workflow(self, workflow_id: str, ref: str, inputs: dict) -> str:
        """Trigger workflow_dispatch and return run_id."""
        
    async def get_run_status(self, run_id: str) -> RunStatus:
        """Poll workflow run status."""
        
    async def get_job_logs(self, job_id: str) -> str:
        """Retrieve job logs for analysis."""
        
    async def download_artifact(self, artifact_id: str) -> bytes:
        """Download workflow artifact."""
```

#### 1.2 Workflow Inventory (`src/services/workflow/inventory.py`)
```python
class WorkflowInventory:
    """Discovers workflows, extracts triggers/inputs, builds dependency graph."""
    
    def scan_workflows(self, path: str = ".github/workflows") -> List[WorkflowMeta]:
        """Scan all workflow files and extract metadata."""
        
    def get_triggerable(self) -> List[WorkflowMeta]:
        """Return workflows with workflow_dispatch trigger."""
        
    def build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build workflow dependency graph."""
```

#### 1.3 Session State Store (`src/services/session/state.py`)
```python
class SessionState:
    """Persistent session + run state for cross-session resumption."""
    
    session_id: str
    created_at: datetime
    workflow_runs: List[WorkflowRun]
    pending_actions: List[Action]
    artifacts: Dict[str, ArtifactRef]
    checkpoints: List[Checkpoint]
```

### Deliverables

| Deliverable | File | Status |
|-------------|------|--------|
| GitHub API client | `src/services/github/client.py` | 🔜 PENDING |
| GitHub API types | `src/services/github/types.py` | 🔜 PENDING |
| Workflow inventory | `src/services/workflow/inventory.py` | 🔜 PENDING |
| Workflow parser | `src/services/workflow/parser.py` | 🔜 PENDING |
| Session state | `src/services/session/state.py` | 🔜 PENDING |
| State persistence | `src/services/session/storage.py` | 🔜 PENDING |

### Acceptance Criteria
- [ ] GitHub client can trigger workflows
- [ ] GitHub client can poll run status
- [ ] Workflow inventory scans all 45+ workflows
- [ ] Session state persists across sessions
- [ ] Unit tests pass with >80% coverage

### Checkpoint: `PHASE1-COMPLETE`

---

## Phase 2: Self-Healing Engine

### Objectives
- Integrate with existing self-healing workflows
- Build failure detection and classification
- Implement auto-remediation strategies
- Generate fix patches

### Components

#### 2.1 Failure Detector (`src/services/healing/detector.py`)
```python
class FailureDetector:
    """Analyzes job logs to detect and classify failures."""
    
    def analyze_logs(self, logs: str) -> FailureAnalysis:
        """Parse logs and identify failure patterns."""
        
    def classify_failure(self, analysis: FailureAnalysis) -> FailureType:
        """Classify failure into known categories."""
```

#### 2.2 Auto-Remediator (`src/services/healing/remediator.py`)
```python
class AutoRemediator:
    """Applies automatic fixes for known failure types."""
    
    def can_remediate(self, failure: FailureType) -> bool:
        """Check if failure can be auto-remediated."""
        
    def generate_fix(self, failure: FailureAnalysis) -> Optional[Patch]:
        """Generate fix patch for failure."""
        
    def apply_fix(self, patch: Patch) -> ApplyResult:
        """Apply fix and return result."""
```

### Failure Categories

| Category | Auto-Remediation | Example |
|----------|-----------------|---------|
| Dependency Missing | ✅ Yes | Add missing pip package |
| Timeout | ✅ Yes | Increase timeout value |
| YAML Syntax | ✅ Yes | Fix YAML formatting |
| Test Flaky | ⚠️ Partial | Add retry or skip |
| API Deprecated | ✅ Yes | Upgrade action version |
| Permission | ❌ No | Requires manual review |

### Acceptance Criteria
- [ ] Detector identifies 90%+ of common failures
- [ ] Auto-remediation success rate >70%
- [ ] Patches validated before application
- [ ] Audit trail for all remediations

### Checkpoint: `PHASE2-COMPLETE`

---

## Phase 3: User Experience

### Objectives
- Build web UI integration points
- Implement approval workflows
- Create result delivery system
- Add natural language interface

### Components

#### 3.1 Agent Surface (`src/services/agent/surface.py`)
```python
class AgentSurface:
    """Web-UI integration for Copilot agent."""
    
    def show_workflow_preview(self, workflow: WorkflowMeta) -> Preview:
        """Show workflow preview before triggering."""
        
    def request_approval(self, action: Action) -> ApprovalRequest:
        """Request user approval for high-risk action."""
        
    def display_results(self, run: WorkflowRun) -> ResultDisplay:
        """Display workflow results to user."""
```

#### 3.2 Approval Engine (`src/services/agent/approval.py`)
```python
class ApprovalEngine:
    """Enforces policies for high-risk actions."""
    
    def requires_approval(self, action: Action) -> bool:
        """Check if action requires user approval."""
        
    def create_approval_request(self, action: Action) -> ApprovalRequest:
        """Create approval request with context."""
```

### Acceptance Criteria
- [ ] Web UI shows workflow previews
- [ ] Approval requests work end-to-end
- [ ] Results delivered to correct session
- [ ] Natural language triggers work

### Checkpoint: `PHASE3-COMPLETE`

---

## Phase 4: Production Hardening

### Objectives
- Add comprehensive telemetry
- Implement rate limiting and quotas
- Add security guardrails
- Performance optimization

### Deliverables

| Area | Deliverable | Status |
|------|-------------|--------|
| Telemetry | OTEL integration | 🔜 PENDING |
| Rate Limiting | Token bucket limiter | 🔜 PENDING |
| Security | Scoped token usage | 🔜 PENDING |
| Performance | Caching layer | 🔜 PENDING |

### Acceptance Criteria
- [ ] All operations traced
- [ ] Rate limits enforced
- [ ] No secret exposure
- [ ] P95 latency <2s

### Checkpoint: `PHASE4-COMPLETE`

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow Discovery | 100% | All workflows indexed |
| Trigger Success Rate | >99% | Successful triggers / attempts |
| Failure Detection | >90% | Detected / actual failures |
| Auto-Remediation | >70% | Successful fixes / attempts |
| User Satisfaction | >4.5/5 | User feedback scores |
| P95 Latency | <2s | End-to-end response time |

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GitHub API rate limits | High | Medium | Implement backoff, caching |
| Token scope creep | High | Low | Least privilege, audit |
| Self-healing loops | Medium | Medium | Circuit breakers, max attempts |
| Session state corruption | High | Low | Checksums, backup, recovery |

---

## Next Steps

1. Complete Phase 0 documentation
2. Begin Phase 1 implementation with GitHub client
3. Set up CI for agent components
4. Create integration test suite

**To continue from this plan:**
```
@copilot Execute Phase 1 Batch 1 from docs/plans/copilot-workflow-agent/01-BATCHSET.md
```
