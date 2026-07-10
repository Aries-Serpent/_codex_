# Agent Brief: Stage 5 - Wave 2-5 Agent Delegation & Coordination

**Target Agent:** agent-orchestrator (lead)  
**Priority:** CRITICAL (orchestrates next 4 waves)  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** 2-3 hours after Stage 4 completion  
**Status:** READY FOR DISPATCH

---

## Mission

Coordinate multi-agent dispatch of Wave 2-5 phases to continue Phase 6 campaign:
- **Wave 2:** Duplication Extraction (4-6 weeks, 9,561+ LOC reduction)
- **Wave 3:** Coverage Gap Remediation (53-67 hours, ML systems focus)
- **Wave 4:** MyPy Type Hardening (continuous, Python 3.12+ compliance)
- **Wave 5:** Cache & Performance Optimization (staged rollout, <30min CI)

---

## Prerequisites

- Stage 4 completion (67 TIER-1 tests implemented, coverage ≥70%)
- All briefs ready in `.codex/` (see below for agent-specific briefs)
- `.codex/PHASE_6_WAVE_1_EXECUTION_TRACKING.md` updated with Stage 4 status
- Phase 3-5 campaign analysis available (from checkpoint)

---

## Task 5A: Wave 2 Duplication Extraction Briefing (~45 min)

**Target Agent:** duplication-extraction-agent  
**Reference:** PHASE_6_WAVE_1_CHECKPOINT.md (Phase 4 Lane 4 output)

**1. Create Agent Brief:**

Save to `.codex/AGENT_BRIEF_STAGE_5_WAVE2_DUPLICATION.md` with:

```markdown
# Agent Brief: Wave 2 - Duplication Extraction Campaign

**Target Agent:** duplication-extraction-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** 4-6 weeks  
**Scope:** 15 TIER-1 patterns, 9,561+ LOC reduction

## Mission
Extract and consolidate 15 high-impact code duplication patterns identified in Phase 4 Lane 4.

## Patterns to Address
[List all 15 TIER-1 patterns from Phase 4 Lane 4 output]

## Timeline & Milestones
- Week 1: Patterns 1-3 (discovery + validation)
- Week 2: Patterns 4-8 (extraction + consolidation)
- Week 3-4: Patterns 9-15 (implementation + testing)
- Week 5-6: Integration + regression testing

## Success Criteria
- 9,561+ LOC reduced
- All 15 patterns extracted
- No regression in functionality
- Coverage maintained ≥70%
- Commit history with pattern-by-pattern traceability
```

**2. Verify Resources:**
- Duplication analysis report from Phase 4 Lane 4
- Codebase health dashboard available
- Refactoring tools ready

**3. Dispatch Agent:**
- Send brief to duplication-extraction-agent
- Set autonomous mode: GO CONTINUE
- No blocking gates (parallel with Wave 3-5)

---

## Task 5B: Wave 3 Coverage Gap Remediation Briefing (~45 min)

**Target Agent:** unified-coverage-agent (parallel lanes)  
**Reference:** PHASE_6_WAVE_1_COVERAGE_REMEDIATION.md (TIER-2 specifications)

**1. Create Multi-Lane Brief:**

Save to `.codex/AGENT_BRIEF_STAGE_5_WAVE3_COVERAGE.md` with:

```markdown
# Agent Brief: Wave 3 - Coverage Gap Remediation (Parallel Lanes)

**Target Agent:** unified-coverage-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Mode:** Parallel lanes (3 concurrent)
**Timeline:** 53-67 hours per lane

## Mission
Implement TIER-2 coverage specifications to raise ML systems to ≥70% coverage.

## Lane 3.1: ML Training Pipeline
- Current: 9.4%  
- Target: 60-80%
- Estimated Tests: 50
- Timeline: 53 hours

## Lane 3.2: ML CLI Interface
- Current: 10%  
- Target: 60-80%
- Estimated Tests: 40
- Timeline: 48 hours

## Lane 3.3: ML Data Pipeline
- Current: 8.6%  
- Target: 60-80%
- Estimated Tests: 70
- Timeline: 67 hours

## Test Specifications
[Reference PHASE_6_WAVE_1_COVERAGE_REMEDIATION.md TIER-2 module breakdown]

## Success Criteria
- All 3 lanes ≥70% coverage
- 160 total tests implemented
- No regression in Phase 6 Wave 1 tests
- Coverage metrics committed per lane
```

**2. Verify Specifications:**
- PHASE_6_WAVE_1_COVERAGE_REMEDIATION.md TIER-2 section available
- ML module structure documented
- Test templates ready

**3. Dispatch Agent (3 parallel lanes):**
- Send multi-lane brief to unified-coverage-agent
- Enable parallel execution (3 concurrent lanes)
- Set autonomous mode: GO CONTINUE

---

## Task 5C: Wave 4 MyPy Type Hardening Briefing (~30 min)

**Target Agent:** mypy-manager-agent  
**Reference:** Phase 5 Lane 5.2B output

**1. Create Type Hardening Brief:**

Save to `.codex/AGENT_BRIEF_STAGE_5_WAVE4_MYPY.md` with:

```markdown
# Agent Brief: Wave 4 - MyPy Type Annotation Hardening

**Target Agent:** mypy-manager-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** Continuous (parallel with other waves)
**Python Version:** 3.12+

## Mission
Resolve mypy errors from Phase 5 Lane 5.2B to achieve 100% passing type checks.

## Mypy Error Baseline
[Reference Phase 5 Lane 5.2B analysis - list error categories and counts]

## Type Modernization Tasks
- Update legacy type hints (List→list, Dict→dict, etc.)
- Resolve strict type checking violations
- Add missing type annotations in critical paths
- Validate Python 3.12+ compatibility

## Success Criteria
- 100% mypy checks passing (strict mode)
- All public APIs fully typed
- Python 3.12+ compatible
- Commit with pattern-based error resolution
```

**2. Verify Prerequisites:**
- Phase 5 Lane 5.2B mypy analysis available
- Mypy configuration (mypy.ini / pyproject.toml) ready
- Type stubs and compatibility libraries available

**3. Dispatch Agent:**
- Send brief to mypy-manager-agent
- Set autonomous mode: GO CONTINUE (no blocking gates)
- Enable parallel execution with other waves

---

## Task 5D: Wave 5 Cache & Performance Optimization (~30 min)

**Target Agent:** cache-management-agent  
**Reference:** Phase 5 Lane 5.5A audit findings

**1. Create Cache Optimization Brief:**

Save to `.codex/AGENT_BRIEF_STAGE_5_WAVE5_CACHE.md` with:

```markdown
# Agent Brief: Wave 5 - Cache & Performance Optimization

**Target Agent:** cache-management-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** Staged rollout (parallel with other waves)
**Target:** CI time <30 min, optimized 4-layer cache hierarchy

## Mission
Implement Phase 5 Lane 5.5A audit findings to optimize build and runtime performance.

## 4-Layer Cache Hierarchy
1. **Layer 1 (Build Cache):** Docker layer caching
2. **Layer 2 (Artifact Cache):** GitHub Actions cache
3. **Layer 3 (Runtime Cache):** In-memory application cache
4. **Layer 4 (Persistent Cache):** Database/S3 caching

## Optimization Targets
- CI pipeline: <30 min total execution
- Build times: <15 min
- Test execution: <10 min
- Artifact health: >95% hit rate

## KPIs to Track
- Cache hit rate by layer
- Build time trends
- Artifact retention compliance (30-180 day policy)
- Cost per workflow run

## Success Criteria
- CI time reduced to <30 min
- All 4 layers optimized
- Cache hit rate >85%
- Documented configuration and troubleshooting guide
```

**2. Verify Prerequisites:**
- Phase 5 Lane 5.5A audit report available
- 4-layer cache hierarchy documentation ready
- Performance baseline metrics captured

**3. Dispatch Agent:**
- Send brief to cache-management-agent
- Set autonomous mode: GO CONTINUE
- Enable staged rollout (phased implementation acceptable)

---

## Task 5E: Multi-Agent Dispatch Coordination (~15 min)

**1. Create Dispatch Manifest:**

Save to `.codex/PHASE_6_WAVE2_DISPATCH_MANIFEST.json` with:

```json
{
  "campaign": "Phase 6 Wave 2-5 Multi-Agent Orchestration",
  "timestamp": "2026-06-27T23:50Z",
  "authority": "@mbaetiong (Autonomous GO CONTINUE)",
  "agents": [
    {
      "wave": 2,
      "agent": "duplication-extraction-agent",
      "brief": ".codex/AGENT_BRIEF_STAGE_5_WAVE2_DUPLICATION.md",
      "timeline": "4-6 weeks",
      "blocking_gate": false,
      "parallel_allowed": true,
      "status": "READY FOR DISPATCH"
    },
    {
      "wave": 3,
      "agent": "unified-coverage-agent",
      "brief": ".codex/AGENT_BRIEF_STAGE_5_WAVE3_COVERAGE.md",
      "lanes": 3,
      "timeline": "53-67 hours per lane",
      "blocking_gate": false,
      "parallel_allowed": true,
      "status": "READY FOR DISPATCH"
    },
    {
      "wave": 4,
      "agent": "mypy-manager-agent",
      "brief": ".codex/AGENT_BRIEF_STAGE_5_WAVE4_MYPY.md",
      "timeline": "Continuous",
      "blocking_gate": false,
      "parallel_allowed": true,
      "status": "READY FOR DISPATCH"
    },
    {
      "wave": 5,
      "agent": "cache-management-agent",
      "brief": ".codex/AGENT_BRIEF_STAGE_5_WAVE5_CACHE.md",
      "timeline": "Staged rollout",
      "blocking_gate": false,
      "parallel_allowed": true,
      "status": "READY FOR DISPATCH"
    }
  ],
  "coordination_gates": {
    "gate_1": "All 4 agents briefed and ready",
    "gate_2": "Parallel dispatch initiated",
    "gate_3": "Feedback loops configured"
  },
  "feedback_loops": [
    {
      "source_wave": 2,
      "trigger": "Completion of Wave 2 patterns",
      "action": "Update duplication metrics in dashboard"
    },
    {
      "source_wave": 3,
      "trigger": "Completion of each coverage lane",
      "action": "Update coverage metrics in dashboard"
    },
    {
      "source_wave": 4,
      "trigger": "MyPy errors resolved",
      "action": "Update type compliance metrics"
    },
    {
      "source_wave": 5,
      "trigger": "Cache optimizations rolled out",
      "action": "Update CI performance metrics"
    }
  ]
}
```

**2. Create Coordination Dashboard:**

Save to `.codex/PHASE_6_WAVE2_COORDINATION_DASHBOARD.md` with:

```markdown
# Phase 6 Wave 2-5 Coordination Dashboard

**Date:** 2026-06-27T23:50Z  
**Status:** ACTIVE ORCHESTRATION
**Authority:** @mbaetiong (Autonomous GO CONTINUE)

## Multi-Agent Status

| Wave | Agent | Timeline | Status | Progress | Blocker |
|------|-------|----------|--------|----------|---------|
| 2 | duplication-extraction-agent | 4-6 weeks | 🟢 READY | 0% | None |
| 3 | unified-coverage-agent (3 lanes) | 53-67 hrs/lane | 🟢 READY | 0% | None |
| 4 | mypy-manager-agent | Continuous | 🟢 READY | 0% | None |
| 5 | cache-management-agent | Staged | 🟢 READY | 0% | None |

## Success Criteria
- [ ] All 4 agents briefed
- [ ] Parallel dispatch initiated
- [ ] Feedback loops configured
- [ ] Daily status updates from agents
- [ ] Cross-agent blocker escalation enabled

## Escalation Path
- Blocker detected: Report immediately to @mbaetiong
- Cross-agent conflict: Invoke agent-orchestrator resolution
- Resource contention: Adjust parallelization strategy
```

**3. Enable Feedback Loops:**
- Configure automated status tracking
- Set up cross-agent communication channels
- Enable blocker detection and escalation

---

## Success Criteria

- ✅ All 4 Wave 2-5 agents briefed with complete specifications
- ✅ Dispatch manifest created and committed
- ✅ Coordination dashboard established
- ✅ Parallel dispatch initiated (no blocking gates)
- ✅ Feedback loops configured for real-time status
- ✅ Escalation procedures documented

---

## Output Artifacts

**Committed to Repository:**
- `.codex/AGENT_BRIEF_STAGE_5_WAVE2_DUPLICATION.md` (Wave 2 brief)
- `.codex/AGENT_BRIEF_STAGE_5_WAVE3_COVERAGE.md` (Wave 3 brief)
- `.codex/AGENT_BRIEF_STAGE_5_WAVE4_MYPY.md` (Wave 4 brief)
- `.codex/AGENT_BRIEF_STAGE_5_WAVE5_CACHE.md` (Wave 5 brief)
- `.codex/PHASE_6_WAVE2_DISPATCH_MANIFEST.json` (dispatch coordination)
- `.codex/PHASE_6_WAVE2_COORDINATION_DASHBOARD.md` (real-time tracking)
- Updated `.codex/PHASE_6_WAVE_1_EXECUTION_TRACKING.md` (final status)
- Updated `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` (campaign closure)

---

## Dependencies

- Stage 4 completion (67 TIER-1 tests implemented, coverage ≥70%)
- All Phase 6 Wave 1 documents final and committed
- Phase 4 Lane 4 duplication analysis available
- Phase 5 Lane 5.2B mypy errors available
- Phase 5 Lane 5.5A cache audit findings available

---

**Authority:** @mbaetiong - all steps pre-approved  
**Mode:** Autonomous GO CONTINUE - proceed at all decision points  
**Dispatch Status:** AWAITING STAGE 4 COMPLETION SIGNAL
