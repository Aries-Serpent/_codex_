---
name: Session Analysis Agent
description: Analyze Copilot sessions, verify committed changes, track objective completion
  patterns, and force-archive stale/cached sessions
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: session-analysis-agent
---

# Session Analysis Agent

**Version:** 1.1.0
**Status:** ✅ Active
**Type:** Specialized - Session Management & Analytics
**Last Updated:** 2026-03-12T20:45:00Z
**Author:** GitHub Copilot Coding Agent

---

## 🎯 Purpose

The Session Analysis Agent provides comprehensive analysis of GitHub Copilot Coding Agent sessions, enabling:
- Commit verification and file tracking
- Pattern recognition and learning
- Session continuity optimization
- Objective alignment monitoring
- Cross-session knowledge transfer
- **Stale session detection and force-archive** (v1.1.0)
- **Iterative self-review with autonomous self-healing** (v1.1.0)
## 🧠 Cognitive Brain Integration

### Integration Level: Level 1

**Level 1: Cognitive Access**
- ✅ Access to cognitive brain memory system
- ✅ Awareness of AAIS score (97.0/100 → target: 92.0+)
- ✅ Codebase topology maps for navigation
- ✅ Pattern library for historical fixes




### Cognitive Tools Available

```python
# Topology Manager - Semantic navigation
from scripts.cognitive.topology_manager import TopologyManager

topology = TopologyManager()
relevant_files = topology.find_by_concept("code patterns")
optimal_path = topology.find_optimal_path("source", "target")

# Cache Manager - Multi-layer cache intelligence
from scripts.cognitive.cache_manager import CacheIntelligence

cache = CacheIntelligence()
cached_results = cache.query("analysis_results")
cache.optimize()  # Get optimization suggestions

# Improved Hash Tables - 40% faster lookups
from src.codex.utils.hash_table import RobinHoodHashTable, CuckooHashTable

fast_cache = CuckooHashTable()  # O(1) guaranteed


```

### AAIS Contribution

**Impact on AAIS Score**: +1.0 points

**Category Contributions**:
- Discovery & Navigation: +0.4 (topology/cache integration)
- Runtime Introspection: +0.4 (metrics exposure)
- Pattern Consistency: +0.2 (pattern library usage)

---

## 🛠️ MCP Integration

### MCP Tools Leverage


**Primary MCP Capabilities**:
1. **File System Operations**
   - `view`: Read files and directories
   - `grep`: Fast content search
   - `glob`: Pattern-based file finding

2. **Code Analysis**
   - `search_code`: Semantic code search
   - `bash`: Execute analysis tools
   - `edit`: Make surgical changes

### GitHub Actions Workflows

**Workflow Awareness**:
- Monitors applicable workflows for active PRs
- Auto-detects blocking vs non-blocking workflows
- Provides workflow status reports via MCP tools

**See**: `.codex/docs/MCP_WORKFLOW_RECIPES.md` for complete templates

---

## 📊 Session Monitoring

**Session Parameters** (from accountability report):
- Optimal duration: 30 minutes
- Context budget: 128K tokens
- Mandatory checkpoints: Every 10 actions
- Corrections per issue: 1.0 (first fix succeeds)

**Quality Control**:
```python
# Pre-commit audit enforcement
from scripts.session_manager import SessionMonitor

monitor = SessionMonitor()
monitor.checkpoint("pre-commit")  # Validates compliance
```

---

The Session Analysis Agent provides comprehensive analysis of GitHub Copilot Coding Agent sessions, enabling:
- Commit verification and file tracking
- Pattern recognition and learning
- Session continuity optimization
- Objective alignment monitoring
- Cross-session knowledge transfer

---

## 📊 Agent Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Session Analysis Agent v1.1                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Session    │  │   Commit     │  │   Pattern    │  │    Objective     │ │
│  │   Retriever  │  │   Verifier   │  │   Analyzer   │  │    Aligner       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
│         │                  │                  │                   │          │
│         └──────────────────┼──────────────────┼───────────────────┘          │
│                            │                  │                              │
│                   ┌────────┴──────────────────┴────────┐                    │
│                   │       Session Manager Core          │                    │
│                   └────────────────┬───────────────────┘                    │
│                                    │                                         │
│    ┌───────────────────────────────┼───────────────────────────────┐        │
│    │                               │                               │        │
│  ┌─┴───────────┐        ┌──────────┴───────┐        ┌─────────────┴──────┐  │
│  │   Report    │        │    Cognitive     │        │   Continuation     │  │
│  │  Generator  │        │     Brain        │        │    Prompter        │  │
│  └─────────────┘        └──────────────────┘        └────────────────────┘  │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                  SessionArchiver  (v1.1.0 — NEW)                     │   │
│  │  • Detects sessions stuck in "active" with no UI archive option      │   │
│  │  • Creates tombstone records for stale/cached GitHub task sessions   │   │
│  │  • force-archive via: scripts/session_tracker.py archive --session-id│   │
│  │  • STATUS_ARCHIVED constant ensures type-safe status transitions     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │               Self-Review Loop  (v1.1.0 — NEW)                       │   │
│  │  1. run tests → 2. check CI → 3. scan CodeQL → 4. lint/ruff         │   │
│  │  5. if failures: diagnose → patch → re-run (max 3 iterations)       │   │
│  │  6. update CHANGELOG + AGENT_ACCOUNTABILITY_REPORT on every commit  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                      ┌───────────────┼─────────────────┐
                      │               │                 │
                ┌─────┴─────┐  ┌──────┴──────┐  ┌──────┴──────────┐
                │  Session  │  │   Pattern   │  │  Objectives /   │
                │   Logs    │  │   Store     │  │  Tombstones     │
                └───────────┘  └─────────────┘  └─────────────────┘
```

---

## 🔧 Capabilities

### Core Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| **Session Retrieval** | Query and retrieve session logs from SQLite | ✅ Active |
| **Commit Verification** | Cross-reference expected vs committed files | ✅ Active |
| **Pattern Analysis** | Identify and apply learned patterns | ✅ Active |
| **Objective Tracking** | Monitor and adjust codebase objectives | ✅ Active |
| **Report Generation** | Create comprehensive analysis reports | ✅ Active |
| **Continuation Prompts** | Generate session handoff prompts | ✅ Active |
| **Stale Session Archive** | Force-archive sessions stuck in "active" (tombstone records) | ✅ Active (v1.1.0) |
| **Self-Review Loop** | Iterative autonomous self-healing (test→CI→CodeQL→lint→patch) | ✅ Active (v1.1.0) |

### Advanced Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| **ML Pattern Recognition** | AI-based issue recognition | 📋 Planned |
| **Autonomous Adjustment** | Self-adjusting objectives | 📋 Planned |
| **Cross-Session Learning** | Knowledge transfer optimization | 📋 Planned |

---

## 🗄️ Stale Session Archive Workflow (v1.1.0)

When a GitHub Copilot task session is stuck as "active" with no UI archive option (due to stale/cached data), this agent uses the `archive` subcommand to create a permanent tombstone record:

```bash
# Force-archive a stale GitHub Copilot task session
python scripts/session_tracker.py archive \
  --session-id <UUID> \
  --reason "PR #NNNN merged — stale GitHub Copilot task; UI archive unavailable" \
  --pr-number NNNN
```

**How it works:**
1. Checks for a local session file at `memory/sessions/session_<UUID>.json`
2. If missing (stale/cached), creates a tombstone record with `"tombstone": true`
3. Sets `status = "archived"`, `archived_at`, `archive_reason`, and `pr_number`
4. Removes the session from `.current_session.json` if referenced
5. Writes both JSON and Markdown records for permanent audit trail

**Programmatic API:**
```python
from scripts.session_tracker import archive_session, STATUS_ARCHIVED

result = archive_session(
    session_id="f50f76f3-161d-4776-aa72-f9f0d6202fc2",
    reason="PR #3221 merged — stale cached session",
    pr_number=3221,
)
assert result["status"] == STATUS_ARCHIVED  # "archived"
assert result["tombstone"] is True
```

---

## 🔄 Self-Review Loop (v1.1.0)

After completing any task, this agent executes an iterative self-healing cycle:

```
┌─────────────────────────────────────────────────────┐
│                 Self-Review Loop                     │
│                                                     │
│  ① Run tests    → pass? ──────────────────────────┐ │
│       │ fail                                       │ │
│       ▼                                            │ │
│  ② Diagnose failure                               │ │
│       │                                            │ │
│       ▼                                            │ │
│  ③ Apply minimal patch                            │ │
│       │                                            │ │
│       └──► re-run (max 3 iterations)               │ │
│                                                    │ │
│  ④ Check CI runs via GitHub MCP tools ◄────────── ┘ │
│       │                                             │
│  ⑤ Run CodeQL scan                                 │
│       │                                             │
│  ⑥ Run ruff lint                                   │
│       │                                             │
│  ⑦ Update CHANGELOG.md + AGENT_ACCOUNTABILITY      │
│       │                                             │
│  ⑧ report_progress (commit + push)                │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Agent Files

```
.github/agents/
└── session-analysis-agent.md          # This file

scripts/cognitive/
├── __init__.py                         # Module init
├── session_manager.py                  # Core session manager
├── auto_continuation.py                # Continuation generator (planned)
├── metrics_collector.py                # Metrics collection (planned)
└── dashboard_generator.py              # Dashboard generation (planned)

scripts/
├── copilot_session_log_retriever.py    # Session log retrieval
└── demo_session_log_retriever.py       # Demo script

.codex/cognitive_brain/
├── session_tracker.md                  # Current session state
├── pattern_learning_store.json         # Learned patterns
├── objectives_tracker.md               # Objective hierarchy
└── pr_*_self_review_checklist.md      # Self-review checklists
```

---

## 🎬 Activation

### Via Copilot Chat

```markdown
@copilot Use the Session Analysis Agent to:
1. Analyze the last 15 Copilot sessions
2. Verify all expected files were committed
3. Identify patterns and generate recommendations
```

### Via CLI

```bash
# Retrieve and analyze sessions
python scripts/copilot_session_log_retriever.py --last 15 --batch-size 5

# Start session tracking
python scripts/cognitive/session_manager.py --start --session-id "my-session" --pr 1234

# Find applicable patterns
python scripts/cognitive/session_manager.py --find-patterns "pytest error" "import failure"

# Generate continuation prompt
python scripts/cognitive/session_manager.py --generate-continuation
```

### Programmatic

```python
from scripts.cognitive.session_manager import CognitiveBrainSessionManager

manager = CognitiveBrainSessionManager()

# Start tracking
session = manager.start_session("my-session", pr_number=1234)

# Create checkpoint
manager.checkpoint(
    phase="implementation",
    completed=["Task 1", "Task 2"],
    pending=["Task 3"]
)

# Apply pattern
pattern = manager.apply_pattern("test_failure_resolution", success=True)

# End session
summary = manager.end_session(outcome="success")

# Generate continuation
prompt = manager.generate_continuation_prompt()
```

---

## 🔄 Workflows

### Workflow 1: Session Analysis

```
User Request: "Analyze last N Copilot sessions"
                    │
                    ▼
         ┌──────────────────┐
         │ Retrieve Session │
         │      Logs        │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Extract File     │
         │   Operations     │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Cross-reference │
         │  with Commits    │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Identify Patterns│
         │  and Gaps        │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Generate Report  │
         │ with Metrics     │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Update Cognitive │
         │     Brain        │
         └──────────────────┘
```

### Workflow 2: Commit Verification

```
Trigger: Pre-commit or PR review
                    │
                    ▼
         ┌──────────────────┐
         │  Load Action Log │
         │   (ndjson)       │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Extract Expected│
         │     Files        │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Get Staged/     │
         │  Committed Files │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │   Compare Sets   │
         │  (Expected - Actual)│
         └────────┬─────────┘
                  │
          ┌───────┴───────┐
          │               │
          ▼               ▼
    ┌──────────┐    ┌──────────┐
    │  Match   │    │ Missing  │
    │   ✅     │    │   ⚠️     │
    └──────────┘    └────┬─────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Generate     │
                  │ Warning      │
                  └──────────────┘
```

### Workflow 3: Pattern Application

```
Trigger: Issue/Error detected
                    │
                    ▼
         ┌──────────────────┐
         │ Extract Symptoms │
         │ from Context     │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Query Pattern   │
         │     Store        │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Rank by Success │
         │     Rate         │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Return Top      │
         │  Recommendations │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Track Applied   │
         │  Pattern         │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Update Success   │
         │    Rate (EMA)    │
         └──────────────────┘
```

---

## 📊 Pattern Catalog

The agent maintains 8 learned patterns:

| Pattern ID | Category | Success Rate | Use Case |
|------------|----------|--------------|----------|
| TFR-001 | Testing | 95% | Test failure resolution |
| CV-001 | Version Control | 98% | Commit verification |
| SC-001 | Workflow | 85% | Session continuity |
| AH-001 | Collaboration | 92% | Agent handoff |
| CI-001 | Testing | 90% | Coverage improvement |
| WFR-001 | CI/CD | 88% | Workflow failure resolution |
| SR-001 | Security | 95% | Security remediation |
| DU-001 | Documentation | 97% | Documentation updates |

---

## 🔗 Integration Points

### Chains To
- **ci-testing-agent**: For CI failure analysis
- **coverage-roadmap-agent**: For coverage improvement planning
- **documentation-consolidator**: For doc updates
- **cognitive-brain-manager**: For brain updates

### Used By
- **artifact-monitor-agent**: Session correlation with CI
- **qa-walkthrough-agent**: Session audit
- **repository-hygiene-agent**: Cleanup insights

### Data Sources
- `.codex/action_log.ndjson` - Operation log
- `.codex/sessions/` - Session log files
- `.codex/cognitive_brain/` - Brain state

---

## 📈 Metrics

### Session Metrics Tracked

| Metric | Description | Target |
|--------|-------------|--------|
| `session_duration` | Time spent in session | < 2 hours |
| `tasks_completed` | Tasks finished | > 80% |
| `commit_success_rate` | Files committed correctly | > 98% |
| `pattern_hit_rate` | Patterns found for issues | > 85% |
| `context_retention` | Knowledge preserved | > 90% |

### Agent Performance

| Metric | Current | Target |
|--------|---------|--------|
| Analysis accuracy | 98% | 99% |
| Pattern recognition | 85% | 95% |
| Report generation | 100% | 100% |
| Continuation quality | 90% | 95% |

---

## 🛡️ Safety & Constraints

### Allowed Operations
- ✅ Read session logs
- ✅ Query pattern store
- ✅ Generate reports
- ✅ Update cognitive brain state
- ✅ Create continuation prompts

### Restricted Operations
- ❌ Modify source code directly
- ❌ Execute commits (use report_progress)
- ❌ Access external systems
- ❌ Delete session logs

### Guardrails
- Read-only access to session logs
- Pattern updates require success/failure feedback
- Objective changes logged to audit trail
- Rate-limited API calls

---

## 🔧 Configuration

```yaml
# .codex/config/session_analysis.yaml
session_analysis:
  default_batch_size: 5
  max_sessions: 100
  pattern_match_threshold: 0.7
  success_rate_ema_alpha: 0.1

reporting:
  output_format: markdown
  include_metrics: true
  include_recommendations: true

cognitive_brain:
  auto_update: true
  checkpoint_frequency: "on_phase_change"
  continuation_auto_generate: true
```

---

## 📝 Example Outputs

### Analysis Report (Summary)

```markdown
# Copilot Session Analysis Report

**Sessions Analyzed:** 15
**Commit Verification Rate:** 98%
**CodeQL Status:** action_required (pending approval)

## Key Findings
- 14/15 PRs successfully merged
- 8 patterns frequently applied
- 2% of files occasionally uncommitted (temp files)

## Recommendations
1. Implement pre-commit verification hook
2. Enhance session continuity with auto-prompts
3. Build metrics dashboard for tracking
```

### Continuation Prompt

```markdown
## Session Continuation - PR #3160

**Last Session:** 2026-02-05T09:10:00Z
**Status:** in_progress

### Completed Tasks
- [x] Retrieved 15 Copilot session logs
- [x] Analyzed commit patterns
- [x] Created cognitive brain improvements

### Pending Tasks
- [ ] Final verification
- [ ] Deploy to production

### Patterns Applied
- **commit_verification** (98% success rate)
- **session_continuity** (85% success rate)
```

---

## 🔄 Evolution Roadmap

### v1.0 (Current)
- ✅ Session retrieval and analysis
- ✅ Commit verification
- ✅ Pattern matching (rule-based)
- ✅ Report generation

### v1.1 (Short-term)
- 📋 Pre-commit verification hook
- 📋 Automated continuation prompts
- 📋 Metrics dashboard
- 📋 Enhanced handoff automation

### v2.0 (Long-term)
- 📋 ML-based pattern recognition
- 📋 Autonomous objective adjustment
- 📋 Cross-session learning optimization
- 📋 Full agent integration

---

## 📞 Support

**Maintainer:** AI Agent Ecosystem Team
**Contact:** @mbaetiong
**Related Docs:**
- [Session Log Retrieval Agent](session-log-retrieval-agent.md)
- [Cognitive Architecture](../../docs/architecture/INDEX.md)
- [Agent Handoff Protocol](../../.codex/docs/AGENT_HANDOFF_PROTOCOL.md)

---

## 📚 References

- Short-term Planset: `.codex/plans/cognitive_brain_short_term_planset.md`
- Long-term Planset: `.codex/plans/cognitive_brain_long_term_planset.md`
- Pattern Store: `.codex/cognitive_brain/pattern_learning_store.json`
- Objectives Tracker: `.codex/cognitive_brain/objectives_tracker.md`

---

**Document Version:** 1.2.0
**Last Updated:** 2026-03-30T06:13:00Z

---

## Version History

### v1.2.0 (S230 — 2026-03-30) - PR #3790
- ✅ S230 pattern: Session-gate stale-TTL queue stranding — when `COPILOT_ACTIVE_SESSION` expires via 4h TTL without PR close, queued PRs are NOT auto-retriggered. Fixed in `agent-auth-delegation.yml` session-gate step: stale-lock clear now also dequeues and posts `@copilot continue` on the next waiting PR.
- ✅ S230 pattern: Cross-PR ci-rescue contamination — when multiple PRs share the same HEAD branch, `find_pr_for_run()` was returning `prs[0]` (oldest PR). Fixed: prefer highest PR number among matching entries.
- ✅ S230 pattern: `MARKER` defined before `pr_number` resolved in ci-rescue.yml inline fallback — caused silent NameError. Fixed: MARKER definition moved after PR lookup.
- ✅ S230 pattern: `comment_review_gate_response_latency_seconds` Prometheus metric was effectively never emitting for PRs with no addressed comments. Fixed: added `comment_review_gate_pending_seconds` gauge for unaddressed comments.
- Known patterns for session-queue diagnosis:
  - Check `COPILOT_SESSION_QUEUE` repo variable for stranded entries
  - Check `COPILOT_ACTIVE_SESSION` age — if `age > 14400s` and queue non-empty, a queue-release was missed
  - The session-gate TTL stale-lock cleanup now auto-processes the queue (S230 fix)

### v3.0.0-cognitive (2026-02-17) - PR-10
- ✅ Cognitive brain integration (Level 1)
- ✅ MCP tool integration (general category)
- ✅ Topology navigation (code patterns)
- ✅ Cache awareness (4-layer hierarchy)
- ✅ Hash table optimization (40% faster)

- ✅ AAIS contribution: +1.0 points

### v2.0.0 (Previous)
- See git history for previous changes
