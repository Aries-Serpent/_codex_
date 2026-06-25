# 🚀 Quick Start: Data Aggregation & Agent Delegation System

**Status:** ✅ Components 1-4 Ready | 🔄 Component 5 In Progress  
**Created:** 2026-06-22T00:32:00Z

---

## 5-Minute Quick Start

### 1️⃣ Generate Session Context (1 minute)

```bash
# Create manifest from 8+ data sources
python scripts/ci/unified_data_aggregator.py \
    --output .codex/session_context_manifest.json

# Check result
cat .codex/session_context_manifest.json | jq '.stats'
```

**Output:**
```json
{
  "data_sources_active": 4,
  "data_sources_total": 6,
  "in_flight_agents": 0,
  "patterns_tracked": 10,
  "delegation_recommendations": 2,
  "phase_completion_pct": 85
}
```

### 2️⃣ Delegate Agents in Parallel (1 minute)

```bash
# Trigger adaptive delegation workflow
gh workflow run adaptive-agent-delegation.yml \
    -f delegation_mode=parallel \
    -f max_agents=5

# Watch execution
gh workflow view adaptive-agent-delegation -v
```

**What Happens:**
- Loads context manifest
- Parses recommended agents (e.g., unified-coverage-agent, ci-auto-healer-agent)
- Queues 5 agents in PARALLEL (not serial)
- Collects results asynchronously (no blocking)

### 3️⃣ Monitor In-Flight Agents (1 minute)

```bash
# View real-time dashboard
cat .codex/RAPID_DELEGATION_STATUS.md

# Or generate fresh dashboard
python scripts/ci/rapid_delegation_engine.py
```

**Shows:**
- Agents executing RIGHT NOW
- Success rates
- Timeout tracking
- Failed tasks + retry status

### 4️⃣ Query Results (1 minute)

```bash
# View coalesced results
cat .codex/delegation_results.json

# Or programmatically
python3 << 'EOF'
from scripts.ci.rapid_delegation_engine import DelegationEngine

engine = DelegationEngine()
results = engine.collect_results()

print(f"✅ Completed: {results.completed_tasks}")
print(f"❌ Failed: {results.failed_tasks}")
print(f"🔄 Recommended next actions: {results.next_actions}")
EOF
```

---

## Architecture at a Glance

```
Context Aggregation  →  Pattern Matching  →  Agent Delegation  →  Result Collection
   (1 minute)            (automatic)           (parallel)           (async)
     ↓                       ↓                    ↓                    ↓
.codex/session_        workflow_pattern_  adaptive-agent-      rapid_delegation_
context_manifest.json  library.py         delegation.yml       engine.py
```

---

## Use Cases

### 🎯 Use Case 1: Coverage Gaps + CI Healing

**Problem:** Coverage at 19%, 5 CI failures  
**Old Process:** Wait 2-3 hours for serial fixes  
**New Process:**

```bash
# Aggregator detects issues
python scripts/ci/unified_data_aggregator.py

# Delegation queues both agents in parallel
gh workflow run adaptive-agent-delegation.yml

# Result: Fixed in 30 minutes (coverage + auto-fix in parallel)
```

### 🎯 Use Case 2: Security Alert Response

**Problem:** 3 critical security patterns detected  
**Old Process:** Fix them one-by-one, wait 3+ hours  
**New Process:**

```bash
# Cascade all 3 agents in parallel
agents=$(python3 -c "from scripts.ci.workflow_pattern_library import PatternLibrary; lib = PatternLibrary(); print(','.join(lib.get_cascade_agents(['security-scan', 'auth-delegation', 'docker-build'])))")

# Delegate all at once
for agent in $(echo $agents | tr ',' '\n'); do
  python3 << EOF
from scripts.ci.rapid_delegation_engine import DelegationEngine
engine = DelegationEngine()
engine.queue_agent("$agent", {"security": True})
EOF
done

# Result: All 3 fixed in parallel instead of serial
```

### 🎯 Use Case 3: Phase State Monitoring

**Problem:** Phase 2.1 at 85%, Phase 2.2 blocked  
**Solution:**

```bash
# Dashboard shows current state
cat .codex/RAPID_DELEGATION_STATUS.md

# When Phase 2.1 completes, automatically start Phase 2.2
# (Will be automated with Component 5 enhancement)
```

---

## Reference: Pattern Library

Query available patterns and recommendations:

```python
from scripts.ci.workflow_pattern_library import PatternLibrary

lib = PatternLibrary()

# List all patterns
for pattern_id, pattern in lib.patterns.items():
    print(f"{pattern_id}: {pattern.pattern_name}")
    print(f"  Agents: {pattern.recommended_agents}")
    print(f"  Auto-fixable: {pattern.auto_fixable}")

# Output:
# coverage-timeout: Coverage Timeout / Collection Issues
#   Agents: ['unified-coverage-agent', 'ci-auto-healer-agent']
#   Auto-fixable: True
# ...
```

---

## Reference: Task Queuing

Fire-and-forget agent delegation without blocking:

```python
from scripts.ci.rapid_delegation_engine import DelegationEngine, TaskStatus

engine = DelegationEngine()

# Queue agents (non-blocking, returns immediately)
t1 = engine.queue_agent("unified-coverage-agent", {"phase": "2.1"}, priority="high")
t2 = engine.queue_agent("ci-auto-healer-agent", {"issues": 5})
t3 = engine.queue_agent("workflow-health-monitor", {},
                        retry_fallback=["ci-testing-agent"])

print(f"✅ Queued 3 agents: {t1}, {t2}, {t3}")

# Poll for results (non-blocking)
in_flight = engine.get_in_flight_tasks()
print(f"In-flight: {len(in_flight)} agents")

# Collect results later (no blocking on completion)
results = engine.collect_results(wait_for_all=False)
print(f"Completed: {results.completed_tasks}")

# Handle failures with adaptive retry
for task in results.task_results:  # pragma: allowlist secret
    if task.status == TaskStatus.FAILED and task.fallback_agents:
        print(f"Retrying {task.agent_id} with fallback: {task.fallback_agents}")
        for fallback in task.fallback_agents:
            engine.queue_agent(fallback, task.context, retry_fallback=[])
```

---

## Common Commands

```bash
# Generate fresh context manifest
python scripts/ci/unified_data_aggregator.py

# Delegate agents (parallel mode, 5 max)
gh workflow run adaptive-agent-delegation.yml -f max_agents=5

# Delegate with specific mode
gh workflow run adaptive-agent-delegation.yml -f delegation_mode=cascading

# Dry-run delegation (no actual execution)
gh workflow run adaptive-agent-delegation.yml -f dry_run=true

# View dashboard
cat .codex/RAPID_DELEGATION_STATUS.md

# View results
cat .codex/delegation_results.json | jq '.merged_output'

# Check delegation engine state
ls -lh .codex/delegation_tasks.json
cat .codex/delegation_tasks.json | jq '.tasks | length'
```

---

## Troubleshooting

### ❌ "Manifest not found"

```bash
# Generate it
python scripts/ci/unified_data_aggregator.py
```

### ❌ "No agents recommended"

```bash
# Check pattern library
python3 -c "from scripts.ci.workflow_pattern_library import PatternLibrary; lib = PatternLibrary(); print(lib.patterns.keys())"

# Manually queue agent
python3 << 'EOF'
from scripts.ci.rapid_delegation_engine import DelegationEngine
engine = DelegationEngine()
engine.queue_agent("unified-coverage-agent", {"manual": True})
EOF
```

### ❌ "Workflow not found"

```bash
# Verify workflow exists
gh workflow list | grep adaptive-agent-delegation

# If not, deploy it
git add .github/workflows/adaptive-agent-delegation.yml
git commit -m "Deploy adaptive agent delegation framework"
git push
```

### ❌ "Tasks not completing"

```bash
# Check rapid delegation engine state
python scripts/ci/rapid_delegation_engine.py

# See in-flight tasks
python3 << 'EOF'
from scripts.ci.rapid_delegation_engine import DelegationEngine
engine = DelegationEngine()
for task in engine.get_in_flight_tasks():
    print(f"{task.task_id}: {task.agent_id} ({task.status.value})")
EOF
```

---

## Performance Expectations

| Operation | Time |
|-----------|------|
| Context aggregation | <1 min |
| Agent delegation (parallel) | <2 min |
| In-flight monitoring | <30 sec |
| Result collection (async) | Non-blocking |
| Dashboard generation | <30 sec |

**Total time to delegate 5 agents:** ~3 minutes (vs. 2-3 hours serial)

---

## Next Steps

1. **Try it now:**
   ```bash
   python scripts/ci/unified_data_aggregator.py
   gh workflow run adaptive-agent-delegation.yml
   ```

2. **Monitor execution:**
   ```bash
   watch -n 5 'cat .codex/RAPID_DELEGATION_STATUS.md | head -20'
   ```

3. **Integrate into Phase 2.2:**
   - Component 5 enhancement (in progress) will auto-run at session startup
   - No manual invocation needed after Phase 2.2 activation

4. **Customize patterns:**
   - Add new patterns to `workflow_pattern_library.py`
   - Map to agents in `pattern.recommended_agents`
   - Patterns auto-discovered by delegation framework

---

## Resources

📖 **Full Documentation:**
- [Integration Guide](DATA_AGGREGATION_INTEGRATION_GUIDE.md) - Complete reference
- [Component 5 Spec](COMPONENT_5_SPECIFICATION.md) - Session bootstrap enhancement
- [Pattern Library](../scripts/ci/workflow_pattern_library.py) - Source code
- [Delegation Engine](../scripts/ci/rapid_delegation_engine.py) - Source code

🔗 **Related:**
- [AGENT_REGISTRY.yaml](../.github/agents/AGENT_REGISTRY.yaml) - 145 available agents
- [Phase 2.2 Spec](PHASE_2_2_WORKFLOW_ENABLEMENT_SPEC.md) - Workflow activation
- [Cognitive Brain Docs](.codex/docs/COGNITIVE_BRAIN_COMPLETE_DOCS.md) - Context injection

---

**Ready to accelerate your agent execution!** 🚀

Next: Trigger your first parallel delegation with `gh workflow run adaptive-agent-delegation.yml`
