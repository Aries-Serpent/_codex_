# Custom Agent Repeatable Processes

> **Document:** Repeatable Processes for Full Agentic Autonomy  
> **Version:** 1.0.0  
> **Generated:** 2026-06-26  
> **Purpose:** Step-by-step procedures for achieving full session time utilization through parallel agent delegation and multi-lane execution  

---

## Table of Contents

1. [Session Initialization](#session-initialization)
2. [Full-Autonomy Workflow](#full-autonomy-workflow)
3. [Multi-Lane Execution](#multi-lane-execution)
4. [Lane Management](#lane-management)
5. [Result Aggregation](#result-aggregation)
6. [Error Recovery](#error-recovery)
7. [Session Closure](#session-closure)
8. [Checklists & Templates](#checklists--templates)

---

## Session Initialization

### Pre-Execution Setup

**Objective:** Establish context, identify tasks, and prepare for autonomous execution.

**Steps:**

```
1. LOAD SESSION CONTEXT
   □ Fetch current branch and commit SHA
   □ Load task backlog from PR/issue
   □ Check prior session state (.codex/AGENT_ACCOUNTABILITY_REPORT.md)
   □ Verify repository state (no uncommitted changes)
   
2. IDENTIFY AVAILABLE LANES
   □ Count CI/CD capacity available
   □ Assess concurrent task limit (typically 4-6 agents)
   □ Verify no blocking dependencies
   □ Check session time budget (estimate: 30-120 min)
   
3. CLASSIFY TASKS BY DOMAIN
   □ Scan backlog for CI/CD issues
   □ Scan backlog for testing issues
   □ Scan backlog for documentation issues
   □ Scan backlog for security issues
   □ Scan backlog for configuration issues
   
   Result: Domain-labeled task list, prioritized
   
4. BUILD EXECUTION PLAN
   □ Group tasks by parallelizability
   □ Assign agents to each task
   □ Define success criteria for each task
   □ Estimate duration per task
   
   Result: Structured plan with phases and lane assignments
   
5. VALIDATE PLAN
   □ Confirm all agent selections match capabilities
   □ Verify no circular dependencies
   □ Check for resource conflicts
   □ Confirm time allocation realistic
   
   Output: Execution plan approved, ready for dispatch
```

### Context Load Template

```json
{
  "session": {
    "session_id": "uuid",
    "branch": "copilot/feature-name",
    "start_time": "2026-06-26T18:30:00Z",
    "time_budget_minutes": 90,
    "max_parallel_agents": 4
  },
  "backlog": {
    "total_tasks": 12,
    "ci_cd_issues": 4,
    "testing_issues": 3,
    "documentation_issues": 2,
    "security_issues": 2,
    "configuration_issues": 1
  },
  "prior_state": {
    "last_session_id": "prior-uuid",
    "last_session_commits": 5,
    "resolved_items": ["task-1", "task-2"],
    "open_items": ["task-3", "task-4"]
  },
  "available_agents": [
    "ci-testing-agent",
    "autonomous-test-healer-agent",
    "unified-coverage-agent",
    "unified-doc-agent",
    "codeql-alert-resolution-agent"
  ]
}
```

---

## Full-Autonomy Workflow

### Phase-Based Execution

**Objective:** Execute all available work within session time using parallelization.

**Three-Phase Model:**

#### Phase 1: Initial Sweep (Broad Coverage)

Deploy multiple agents across domains in parallel.

```
1. ASSIGN LANES
   Lane 1: ci-auto-healer-agent (CI/CD patterns)
   Lane 2: autonomous-test-healer-agent (Fix failing tests)
   Lane 3: unified-coverage-agent (Coverage gaps)
   Lane 4: unified-doc-agent (Doc structure issues)
   
2. DISPATCH ALL AGENTS
   - Send task context to each agent
   - Confirm receipt and parsing
   - Monitor execution
   
3. AWAIT COMPLETION
   - Monitor progress asynchronously
   - Timeout: phase_duration or first_completion + buffer
   
4. AGGREGATE RESULTS
   - Collect output from all 4 agents
   - Verify consistency
   - Identify any failures
   
   Expected outcome: 60-70% of backlog resolved
```

#### Phase 2: Specialist Deep-Dives (Remaining Work)

Address remaining issues with more specialized agents.

```
1. ASSESS PHASE 1 RESULTS
   □ Which items still failing?
   □ Which domains need more work?
   □ What prerequisites unblock new tasks?
   
2. REASSIGN LANES
   Lane 1: fragile-test-guardian (Flaky test stabilization)
   Lane 2: test-enhancement-agent (Edge case addition)
   Lane 3: link-validator-agent (Doc link health)
   Lane 4: codeql-alert-resolution-agent (Security audit)
   
3. DISPATCH PHASE 2 AGENTS
   - Different specialists targeting different issues
   - May reuse agents from Phase 1 if available
   
4. COLLECT PHASE 2 RESULTS
   
   Expected outcome: 90-95% of backlog resolved
```

#### Phase 3: Final Polish (Remaining Buffer)

Clean up any stragglers and optimization.

```
1. IDENTIFY REMAINING ITEMS
   □ What's left in the backlog?
   □ What requires manual intervention?
   □ What optimization can be done quickly?
   
2. FINAL AGENT ASSIGNMENTS
   Lane 1: Active specialists for quick wins
   Lane 2-3: Idle (if no remaining work)
   
3. EXECUTE FINAL ITEMS
   
   Expected outcome: 95-99% resolution
   
4. PREPARE FOR CLOSURE
   - Archive final artifacts
   - Generate summary report
```

### Execution Checkpoint Template

```yaml
Phase: 1
Status: EXECUTING
StartTime: 2026-06-26T18:30:00Z
ElapsedMinutes: 15
RemainingMinutes: 75

Lanes:
  Lane1:
    Agent: ci-auto-healer-agent
    Status: EXECUTING
    Progress: 45%
    ItemsProcessed: 3/7
    EstimatedCompletion: 2026-06-26T18:35:00Z
    
  Lane2:
    Agent: autonomous-test-healer-agent
    Status: EXECUTING
    Progress: 60%
    ItemsProcessed: 4/7
    EstimatedCompletion: 2026-06-26T18:33:00Z
    
  Lane3:
    Agent: unified-coverage-agent
    Status: QUEUED
    
  Lane4:
    Agent: unified-doc-agent
    Status: IDLE

AggregatedMetrics:
  TotalTasksStarted: 7
  TasksCompleted: 0
  TasksFailed: 0
  ActiveLanes: 2
  IdleLanes: 2
```

---

## Multi-Lane Execution

### Lane Lifecycle

**Definition:** A "lane" is an independent execution context for one agent performing one category of work.

```
Lane State Transitions
┌──────┐
│ IDLE │ (ready for work)
└───┬──┘
    │ task assigned
    ▼
┌──────────┐
│ QUEUED   │ (waiting to start)
└───┬──────┘
    │ execution starts
    ▼
┌──────────┐
│EXECUTING │ (active work)
└───┬──────┘
    │ work complete or error
    ├─ success → ┌─────────┐
    │            │COMPLETED│
    │            └──┬──────┘
    │               │ results returned
    │               ▼
    │            ┌──────┐
    │            │ IDLE │ (ready for next)
    │            └──────┘
    │
    └─ failure → ┌─────────┐
                 │ FAILED  │
                 └──┬──────┘
                    │ escalation/retry
                    ▼
                 ┌──────────┐
                 │ESCALATED │
                 └──────────┘
```

### Lane Optimization Rules

**Rule 1: Maximize Lane Utilization**

```
Objective: Minimize idle lanes during session time

Strategy:
├─ Phase 1: Deploy all 4 lanes with tasks from backlog
├─ Phase 2: Reuse lanes for new tasks as previous complete
├─ Phase 3: Consolidate remaining tasks to 1-2 lanes
└─ Monitor: Idle time < 10% of session time
```

**Rule 2: Respect Task Dependencies**

```
Constraint: Only dispatch independent tasks to parallel lanes

Examples:

✅ GOOD PARALLELISM:
   Lane 1: Fix failing tests (independent)
   Lane 2: Check doc links (independent)
   Lane 3: Validate config (independent)
   Result: All can run simultaneously
   
❌ BAD PARALLELISM:
   Lane 1: config-migration-assistant (generates config)
   Lane 2: config-validator (needs config from Lane 1)
   Problem: Lane 2 blocked until Lane 1 complete
   Solution: Make sequential, not parallel
```

**Rule 3: Monitor Memory & Resource Usage**

```
Limit concurrent agents by resource availability:

CPU-bound tasks: Limit to 2 concurrent
  Example: mutation-testing-agent, meta-tensor-validator

I/O-bound tasks: Can run 4+ concurrent
  Example: link-validator-agent, doc-freshness-checker

Mixed: Interleave—run 1 CPU + 2 I/O at once
  Example: ci-testing-agent (CPU) + link-validator (I/O)
```

---

## Lane Management

### Starting a Lane

```
Procedure: Start-Lane

Input:
  - lane_id: 1-4
  - agent_id: e.g., "ci-auto-healer-agent"
  - task_context: detailed task specification

Steps:

1. VALIDATE AGENT AVAILABILITY
   □ Is agent currently IDLE?
   □ Does agent have required capabilities?
   □ Are prerequisites met?
   
2. PREPARE TASK CONTEXT
   □ Package task with all needed info
   □ Include success criteria
   □ Set timeout
   □ Include backoff strategy
   
3. DISPATCH AGENT
   □ Send delegation signal to agent
   □ Confirm receipt
   □ Mark lane as QUEUED
   □ Record dispatch timestamp
   
4. MONITOR EXECUTION
   □ Poll for progress updates
   □ Log interim metrics
   □ Check for errors
```

### Monitoring Active Lanes

```
Procedure: Monitor-Lanes

Interval: Every 30 seconds during execution

Steps:

1. POLL ALL ACTIVE LANES
   For each lane (1-4):
     □ Query agent status
     □ Get progress percentage
     □ Check for errors
     □ Estimate time to completion
     
2. AGGREGATE STATUS
   □ Total lanes: 4
   □ Active lanes: N
   □ Idle lanes: 4-N
   □ Failed lanes: M
   
3. DETECT ISSUES
   □ Timeout? (Phase time expired)
     → Escalate to human / trigger failsafe
   □ Error state?
     → Log and attempt retry (with backoff)
   □ Hung agent?
     → Signal timeout, move to next task
     
4. ADJUST IF NEEDED
   □ Any idle lanes available?
     → Assign next task from backlog
   □ Any completed lanes?
     → Prepare them for Phase N+1
```

### Completing a Lane

```
Procedure: Complete-Lane

Input:
  - lane_id: 1-4
  - agent_id: which agent
  - results: agent's output

Steps:

1. VERIFY RESULTS
   □ All success criteria met?
   □ Results well-formed (JSON parseable)?
   □ Artifacts properly stored?
   □ Commit SHAs recorded?
   
2. INTEGRATE RESULTS
   □ Merge into consolidated result set
   □ Check for conflicts with other lanes
   □ Update success metrics
   
3. ARCHIVE & LOG
   □ Store results in .codex/results/
   □ Record completion timestamp
   □ Log metrics (time taken, items processed)
   
4. MARK LANE READY
   □ Set lane state to IDLE
   □ Clear task context
   □ Make available for next assignment
```

---

## Result Aggregation

### Merging Results from Multiple Lanes

```
Procedure: Merge-Lane-Results

Input:
  - results_lane_1: output from agent 1
  - results_lane_2: output from agent 2
  - results_lane_N: output from agent N

Steps:

1. EXTRACT INDIVIDUAL RESULTS
   For each lane result:
     □ Parse JSON/structured format
     □ Validate schema
     □ Extract key metrics
     
2. CHECK FOR CONFLICTS
   □ Did any two lanes touch same file?
     → Inspect for conflicts
     → Log warning if conflict
   □ Did any two lanes make contradictory changes?
     → Flag for manual review
     
3. MERGE COHERENTLY
   ├─ Metrics: Sum/aggregate
   │  Example: tests_fixed_lane1=5, tests_fixed_lane2=3
   │          → total_tests_fixed = 8
   │
   ├─ Changes: Combine file lists
   │  Example: lane1 changed [a.py, b.py]
   │          lane2 changed [c.py, d.py]
   │          → combined [a.py, b.py, c.py, d.py]
   │
   └─ Commits: Collect all commit SHAs
      Example: lane1 commits [sha1, sha2]
               lane2 commits [sha3]
               → combined [sha1, sha2, sha3]
               
4. GENERATE MERGED REPORT
   {
     "status": "success",
     "metrics": {
       "tests_fixed": 8,
       "coverage_gain": 0.12,
       "files_modified": 4,
       "docs_updated": 3
     },
     "commits": ["sha1", "sha2", "sha3"],
     "per_lane_results": [
       { "lane": 1, "agent": "...", "summary": "..." },
       { "lane": 2, "agent": "...", "summary": "..." }
     ]
   }
```

### Conflict Resolution

```
Conflict Scenarios & Resolution

1. TWO LANES MODIFIED SAME FILE

   Scenario: Lane 1 (ci-auto-healer) modifies tests/test_x.py
             Lane 2 (autonomous-test-healer) modifies tests/test_x.py
             
   Detection:
     □ File appears in both lane results
     
   Resolution:
     Step 1: Fetch both versions
     Step 2: Use git merge to combine
     Step 3: Manual review if merge conflicts
     Step 4: Accept resolved version
     
2. CONTRADICTORY CHANGES

   Scenario: Lane 1 sets config value A=true
             Lane 2 sets config value A=false
             
   Detection:
     □ Conflicting assignments in same key
     
   Resolution:
     Step 1: Flag as HIGH PRIORITY
     Step 2: Examine each agent's rationale
     Step 3: Determine correct value based on context
     Step 4: Select winner, document rationale
     Step 5: Log decision for future reference
     
3. DEPENDENCY VIOLATION

   Scenario: Lane 1 (config-migration) output should feed to Lane 2 (config-validator)
             But Lane 2 executed in parallel, used old config
             
   Resolution:
     Step 1: Detect ordering issue
     Step 2: Re-run Lane 2 with Lane 1 output
     Step 3: Update final results with corrected Lane 2 output
```

---

## Error Recovery

### Error Detection & Classification

```
Error Type → Recovery Strategy

1. AGENT TIMEOUT (execution takes > estimated)
   Symptom: Lane still EXECUTING after 30min
   Action: Signal agent to complete & return interim results
   Strategy: Partial success is acceptable, move to next task
   
2. CAPABILITY MISMATCH (agent can't do task)
   Symptom: Agent returns "not capable" status
   Action: Reselect agent, try different agent
   Strategy: Fall back to more generalist agent or escalate
   
3. PREREQUISITE MISSING (dependencies not met)
   Symptom: Agent can't proceed without input
   Action: Fulfill prerequisite first, retry agent
   Strategy: Reorder tasks or request human intervention
   
4. PARTIAL FAILURE (agent completes some work, fails on rest)
   Symptom: Agent returns mixed success/failure
   Action: Accept completed work, handle failures
   Strategy: Log failures, attempt retry, escalate if critical
   
5. RESOURCE EXHAUSTED (out of memory, disk space, etc.)
   Symptom: Agent reports resource error
   Action: Free resources (delete artifacts, etc.)
   Strategy: Retry agent or move to next task
   
6. EXECUTION HANG (agent not responding)
   Symptom: No progress updates for 5+ minutes
   Action: Force timeout, move to next task
   Strategy: Log hang, investigate later
```

### Retry Strategy

```
Procedure: Retry-With-Backoff

For retriable errors:

Attempt 1: Retry immediately
  Delay: 0 seconds
  
Attempt 2: Wait then retry
  Delay: 30 seconds
  
Attempt 3: Wait longer then retry
  Delay: 90 seconds
  
Attempt 4: Wait much longer then retry
  Delay: 300 seconds (5 min)
  
Attempt 5+: Give up
  Action: Escalate to human or next lane
  
Max retries: 4
Total retry time: ~425 seconds (~7 minutes)

Abort early if:
  - Error is non-retriable (capability mismatch)
  - Time budget insufficient for retries
  - Human escalation triggered
```

---

## Session Closure

### End-of-Session Checklist

```
1. STOP ACCEPTING NEW WORK
   □ Set session time budget to ZERO
   □ No new agent delegations
   □ Complete in-flight agents (wait for results)
   
2. WAIT FOR IN-FLIGHT COMPLETIONS
   □ Poll all active lanes
   □ Set timeout: 5 minutes max
   □ Force timeout if exceeded
   
3. COLLECT FINAL RESULTS
   □ Gather outputs from all agents
   □ Perform final merge
   □ Resolve any last conflicts
   
4. GENERATE SESSION REPORT
   □ Total tasks completed
   □ Total commits
   □ Metrics summary (tests fixed, coverage gain, etc.)
   □ Failures/escalations
   □ Time spent
   □ Efficiency score
   
5. UPDATE DOCUMENTATION
   □ Commit changes to AGENT_ACCOUNTABILITY_REPORT.md
   □ Update CHANGELOG.md with summary
   □ Archive session context
   
6. FINALIZE BRANCH
   □ All commits pushed
   □ PR updated with results
   □ Ready for merge gate
```

### Session Report Template

```yaml
Session:
  ID: uuid
  Branch: copilot/feature-name
  StartTime: 2026-06-26T18:30:00Z
  EndTime: 2026-06-26T19:45:00Z
  DurationMinutes: 75

Execution:
  Phase1Items: 7/10 (70%)
  Phase2Items: 2/10 (20%)
  Phase3Items: 1/10 (10%)
  TotalCompleted: 10/10 (100%)
  
Metrics:
  CommitsGenerated: 12
  FilesModified: 45
  LinesChanged: 1200
  TestsFixed: 8
  CoverageGain: 0.12
  
ParallelExecution:
  LanedTasks: 4
  SequentialTasks: 6
  ParallelEfficiency: 1.8x (vs sequential)
  
Agents:
  - ci-auto-healer-agent: 2 tasks, 100% success
  - autonomous-test-healer-agent: 2 tasks, 100% success
  - unified-coverage-agent: 2 tasks, 100% success
  - unified-doc-agent: 1 task, 100% success
  - link-validator-agent: 1 task, 100% success
  - codeql-alert-resolution-agent: 2 tasks, 100% success
  
Failures:
  - None
  
Escalations:
  - None
  
Outcome: SUCCESS
Status: Ready for merge
```

---

## Checklists & Templates

### Pre-Session Checklist

```markdown
## Pre-Session Validation (5 min)

- [ ] Branch checked out correctly
- [ ] No uncommitted changes
- [ ] Prior session state reviewed
- [ ] Session time budget set (90-120 min)
- [ ] Backlog tasks identified (8-15 items)
- [ ] Domain classification complete
- [ ] Execution plan drafted
- [ ] Agent assignments confirmed
- [ ] Dependencies resolved
- [ ] Success criteria defined
- [ ] Time estimate realistic

**Status:** ☐ READY TO EXECUTE
```

### Per-Phase Checklist

```markdown
## Phase 1 Execution (30-40 min)

### Pre-Dispatch
- [ ] 4 agents selected
- [ ] Task contexts prepared
- [ ] Success criteria defined
- [ ] Timeouts set (1800 sec)

### Dispatch
- [ ] Agent 1 delegated (Lane 1)
- [ ] Agent 2 delegated (Lane 2)
- [ ] Agent 3 delegated (Lane 3)
- [ ] Agent 4 delegated (Lane 4)

### Monitoring (every 30 sec)
- [ ] Check Lane 1 progress
- [ ] Check Lane 2 progress
- [ ] Check Lane 3 progress
- [ ] Check Lane 4 progress
- [ ] Log interim metrics

### Completion
- [ ] Lane 1 results collected
- [ ] Lane 2 results collected
- [ ] Lane 3 results collected
- [ ] Lane 4 results collected
- [ ] Merge conflicts resolved
- [ ] Results validated

**Phase 1 Outcome:** ___ items completed
```

### Post-Session Checklist

```markdown
## Post-Session Finalization (10 min)

- [ ] All agent executions complete
- [ ] Final results merged
- [ ] Artifacts archived in .codex/
- [ ] Session report generated
- [ ] AGENT_ACCOUNTABILITY_REPORT.md updated
- [ ] CHANGELOG.md updated
- [ ] All commits pushed to branch
- [ ] PR body updated with summary
- [ ] PR marked ready for review

**Session Status:** ☐ COMPLETE & READY FOR MERGE
```

---

## See Also

- [Custom Agent Selection Framework](./CUSTOM_AGENT_SELECTION_FRAMEWORK.md)
- [Multi-Agent Interaction Protocol](./CUSTOM_AGENT_INTERACTION_PROTOCOL.md)
- [Agent Workflow Coordination](./CUSTOM_AGENT_COORDINATION_WORKFLOWS.md)
- [AGENT_REGISTRY.yaml](../.github/agents/AGENT_REGISTRY.yaml)
- [Operational Guidelines](./OPERATIONAL_GUIDELINES.md)
