# Custom Agent Documentation Suite — Index

> **Generated:** 2026-06-26  
> **Purpose:** Central hub for custom agent methodology, patterns, and best practices  

---

## 📚 Documentation Guide

This documentation suite provides comprehensive methodology for effective multi-agent orchestration and full agentic autonomy within the Aries-Serpent/_codex_ repository.

### Core Documents

#### 1. **[Custom Agent Selection Framework](./CUSTOM_AGENT_SELECTION_FRAMEWORK.md)**

**When to use:** Choosing the right agent(s) for your task

**Key sections:**
- Domain-to-agent mapping (5 domains: CI/CD, Testing, Docs, Security, Config)
- Selection criteria matrix
- Agent selection algorithm (5-step decision process)
- Capability tags reference
- Anti-patterns & common pitfalls
- Quick reference decision tree

**Example:** "I need to fix failing tests" → See Testing domain → Select `autonomous-test-healer-agent`

---

#### 2. **[Multi-Agent Interaction Protocol](./CUSTOM_AGENT_INTERACTION_PROTOCOL.md)**

**When to use:** Understanding how agents communicate and hand off work

**Key sections:**
- Agent lifecycle states (IDLE → RECEIVING → VALIDATING → EXECUTING → VERIFYING → RETURNING → IDLE)
- Communication channels (task delegation, result return, status updates)
- Handoff protocols (sequential, parallel, cascading)
- Result verification checklist
- Error handling & escalation paths
- State machine diagrams

**Example:** "How do I pass results from Agent A to Agent B?" → See Handoff Protocol section

---

#### 3. **[Agent Workflow Coordination Diagrams](./CUSTOM_AGENT_COORDINATION_WORKFLOWS.md)**

**When to use:** Visualizing how agents work together

**Key diagrams (8 total):**
- Overall system architecture
- Agent selection decision tree
- CI/CD failure resolution cascade
- Testing & coverage audit workflow
- Documentation audit workflow
- Security scanning & remediation flow
- Multi-lane parallel execution model
- Session lifecycle & agentic autonomy loop
- Full agentic autonomy pattern

**Example:** "Show me the multi-agent flow for a security audit" → See Security Scanning diagram

---

#### 4. **[Custom Agent Repeatable Processes](./CUSTOM_AGENT_REPEATABLE_PROCESSES.md)**

**When to use:** Running a session with full autonomy

**Key sections:**
- Session initialization (pre-execution setup)
- Three-phase execution model (Initial Sweep → Specialist Deep-Dives → Final Polish)
- Multi-lane execution & lifecycle management
- Lane management procedures (start, monitor, complete)
- Result aggregation & conflict resolution
- Error detection, classification, & recovery
- Session closure checklist
- Pre-session, per-phase, and post-session checklists

**Example:** "How do I run a full-autonomy session?" → See Full-Autonomy Workflow section

---

## 🎯 Quick Start by Use Case

### "I need to fix a single issue"
→ **Selection Framework**: Use decision tree to pick 1 agent  
→ **Interaction Protocol**: Understand delegation → result return  
→ **Repeatable Processes**: Use single-lane section  

### "I have multiple issues to fix"
→ **Selection Framework**: Map all issues to agents  
→ **Coordination Workflows**: Review multi-lane execution diagram  
→ **Repeatable Processes**: Follow three-phase model  

### "I want to understand full agentic autonomy"
→ **Coordination Workflows**: Study agentic autonomy loop diagram  
→ **Repeatable Processes**: Read full-autonomy workflow section  
→ **Interaction Protocol**: Review agent lifecycle states  

### "I'm implementing a new custom agent"
→ **Selection Framework**: Define agent's domain & capabilities  
→ **Interaction Protocol**: Follow communication protocol  
→ **Coordination Workflows**: Determine handoff patterns  

---

## 🔗 Cross-References

### Within This Suite

All four documents are cross-linked:

```
SELECTION_FRAMEWORK.md
  ├→ references Selection Algorithm → Interaction Protocol
  ├→ references Capability Tags → Agent Registry
  └→ references Decision Tree → Coordination Workflows

INTERACTION_PROTOCOL.md
  ├→ references Agent States → Session Lifecycle (Workflows)
  ├→ references Handoff Patterns → Repeatable Processes
  └→ references Communication Channels → examples in Processes

COORDINATION_WORKFLOWS.md
  ├→ references Decision Tree → Selection Framework
  ├→ references Multi-Lane Model → Lane Management (Processes)
  └→ references Agent Lifecycle → Interaction Protocol

REPEATABLE_PROCESSES.md
  ├→ references Phase Model → Coordination Workflows
  ├→ references Lane Lifecycle → Interaction Protocol
  └→ references Agent Selection → Selection Framework
```

### External References

- **Agent Registry:** `.github/agents/AGENT_REGISTRY.yaml` — Authoritative agent definitions
- **Operational Guidelines:** `./OPERATIONAL_GUIDELINES.md` — Agent operational constraints
- **Accountability:** `../../.codex/AGENT_ACCOUNTABILITY_REPORT.md` — Session tracking

---

## 📊 Key Concepts

### Agent Domain Classification

| Domain | Primary Agent | Specialists | Use When |
|--------|---------------|-------------|----------|
| **CI/CD** | ci-auto-healer-agent | 4 available | Workflow failures, test failures, build issues |
| **Testing** | unified-coverage-agent | 8 available | Test failures, coverage gaps, flaky tests |
| **Documentation** | unified-doc-agent | 5 available | Doc structure, links, freshness, terminology |
| **Security** | unified-security-scanner | 7 available | CodeQL, GHAS, deps, secrets |
| **Configuration** | config-validator | 5 available | Config validation, migration, PyTorch |

### Multi-Lane Execution Model

```
Lane = Independent execution context for one agent

Lanes:
  Lane 1: ci-auto-healer-agent (fixing CI)
  Lane 2: autonomous-test-healer-agent (fixing tests)
  Lane 3: unified-coverage-agent (coverage gaps)
  Lane 4: unified-doc-agent (doc structure)

All lanes execute in parallel:
  Total time ≈ max(lane1_time, lane2_time, lane3_time, lane4_time)
  vs. sequential ≈ lane1_time + lane2_time + lane3_time + lane4_time
  
Efficiency gain: 2-4x faster with careful parallelization
```

### Agent Lifecycle

```
State transitions:
  IDLE → RECEIVING → VALIDATING → EXECUTING → VERIFYING → RETURNING → IDLE
  
Key gates:
  VALIDATING: Prerequisite check (if fails → ESCALATING)
  EXECUTING: Work in progress (if blocker → ESCALATING)
  VERIFYING: Self-check results (if invalid → retry EXECUTING)
```

---

## 🚀 Common Workflows

### Workflow 1: Simple Fix

```
1. Select agent using Selection Framework
2. Delegate task using Interaction Protocol
3. Await results
4. Verify results
5. Return to primary
```

### Workflow 2: Multi-Domain Audit

```
1. Classify all issues by domain
2. Select agents per domain (multi-agent setup)
3. Delegate to all agents (parallel lanes)
4. Monitor all lanes
5. Merge results from all lanes
6. Resolve conflicts
7. Return consolidated results
```

### Workflow 3: Full-Autonomy Session

```
1. Session Initialization (prep backlog)
2. Phase 1: Initial Sweep (4 agents parallel)
3. Phase 2: Specialist Deep-Dives (4 new agents parallel)
4. Phase 3: Final Polish (remaining work)
5. Session Closure (archive & report)
```

---

## 📋 Checklists

### Pre-Session Checklist

- [ ] Branch checked out correctly
- [ ] No uncommitted changes
- [ ] Backlog tasks identified
- [ ] Domain classification complete
- [ ] Execution plan drafted
- [ ] Agent assignments confirmed
- [ ] Dependencies resolved

**See:** Repeatable Processes → Session Initialization

---

### Per-Phase Checklist

- [ ] Agents selected and validated
- [ ] Task contexts prepared
- [ ] Success criteria defined
- [ ] Timeouts set
- [ ] All agents dispatched
- [ ] Lanes monitored during execution
- [ ] Results collected and merged
- [ ] Conflicts resolved

**See:** Repeatable Processes → Multi-Lane Execution

---

### Post-Session Checklist

- [ ] All agent executions complete
- [ ] Final results merged
- [ ] Session report generated
- [ ] Documentation updated
- [ ] All commits pushed
- [ ] PR ready for review

**See:** Repeatable Processes → Session Closure

---

## 🔍 Error Resolution Quick Reference

| Error | Symptom | Resolution |
|-------|---------|-----------|
| **Capability Mismatch** | Agent returns "not capable" | Reselect agent per Selection Framework |
| **Timeout** | Agent doesn't complete in time | Escalate or move to next task |
| **Partial Failure** | Agent completes some work, fails on rest | Accept completed work, escalate failures |
| **Prerequisite Missing** | Agent can't proceed | Fulfill prerequisite, retry |
| **Conflict** | Two lanes modified same file | Merge using git, manually review if needed |

**See:** Repeatable Processes → Error Recovery

---

## 📈 Metrics & Optimization

### Lane Utilization

```
Goal: Minimize idle lanes

Good: 4 lanes, all executing = 100% utilization
Bad:  4 lanes, 2 idle = 50% utilization
```

### Time Efficiency

```
Sequential execution: T = t1 + t2 + t3 + t4
Parallel execution:   T = max(t1, t2, t3, t4)
Efficiency gain:      2-4x faster with good lane balancing
```

### Success Rate

```
Goal: 95%+ task completion in single session

Typical: 90-100% with proper agent selection
With retries: 95%+ achievable
```

---

## 🎓 Learning Path

1. **Beginner:** Start with Selection Framework decision tree
2. **Intermediate:** Read Interaction Protocol for understanding handoffs
3. **Advanced:** Study Coordination Workflows for multi-agent patterns
4. **Expert:** Implement Repeatable Processes for full-autonomy sessions

---

## 📞 Support & References

### When Something Breaks

1. Classify error using Repeatable Processes → Error Classification
2. Apply recovery strategy
3. If unresolved, escalate to human

### Agent Information

- Full agent list: `.github/agents/AGENT_REGISTRY.yaml`
- Agent capabilities: Each agent's `capability_tags` in registry
- Agent autonomy model: See Operational Guidelines

### Documentation Structure

```
docs/
├── agent/
│   ├── CUSTOM_AGENT_SELECTION_FRAMEWORK.md (⬅ YOU ARE HERE)
│   ├── CUSTOM_AGENT_INTERACTION_PROTOCOL.md
│   ├── CUSTOM_AGENT_COORDINATION_WORKFLOWS.md
│   ├── CUSTOM_AGENT_REPEATABLE_PROCESSES.md
│   ├── INDEX.md (this file)
│   └── [other agent documentation]
```

---

## 📝 Document Maintenance

**Last Updated:** 2026-06-26  
**Version:** 1.0.0  
**Maintainer:** @mbaetiong  

### How to Update This Suite

1. If adding new agent → Update Selection Framework & Agent Registry
2. If changing communication → Update Interaction Protocol
3. If new workflow pattern → Add diagram to Coordination Workflows
4. If new procedure → Add checklist to Repeatable Processes

---

**🚀 Ready to get started?** Pick a use case above and follow the recommended documents!
