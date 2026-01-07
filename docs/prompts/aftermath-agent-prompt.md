# [Prompt]: AfterMath Action Workflow — Copilot Agent Emission Standard
> **Version**: 1.0.0  
> **Last Updated**: 2025-12-30  
> **Purpose**: Structured session logging for AI-driven lessons learned

## Objective

Instruct GitHub Copilot Agent to emit structured session annotations that the AfterMath Action Workflow can parse to produce durable "lessons learned" artifacts from Copilot Coding Agent logs. This enables AI Agents to review, ingest, and learn from actual self-experience.

## Context

**Problem**: Copilot sessions contain valuable learnings but logs are ephemeral and unstructured.

**Solution**: Emit standardized YAML-fenced "aftermath" blocks to:
- `$GITHUB_STEP_SUMMARY` (workflow job summaries)
- Final PR comments (when working on PRs)

**Benefits**:
- Durable lessons learned artifacts
- AI agents can ingest and learn from experience
- Checkpoint-based resume capability
- Automated metrics tracking
- Enhanced prompt creation

## Agent Tasks

At the end of every active session (PR or workflow), write a structured "aftermath" block containing:

1. **Session Metadata**: IDs, timestamps, context
2. **Lessons Learned**: Title, context, root cause, fix, evidence
3. **Decisions Made**: What, why, alternatives, tradeoffs
4. **Metrics**: Token usage, commits, files, duration
5. **Quality**: Tests, coverage, review status
6. **Blockers**: Issues encountered and resolutions
7. **Next Steps**: Continuation tasks and status
8. **Future Research**: Research topics identified during session

## Required Annotation Schema

Emit exactly one fenced block labeled `aftermath` with the following YAML structure:

```aftermath
meta:
  # Identifiers
  session_id: "S-PR2671-Previous Cycle-12-30-1"
  pr: 2671
  branch: "copilot/sub-pr-2668-again"
  run_id: 59168839007

  # Timestamps (ISO 8601, UTC)
  started_at: "2025-12-30T08:00:00Z"
  finished_at: "2025-12-30T08:18:00Z"

  # Context (free text or short bullets)
  context: "Resolve PR review items; implement AfterMath logging; advance Phase 9"

lessons:
  - title: "Code quality maintenance scripts"
    context: "PR review identified unused imports and empty except blocks"
    root_cause: "Initial rapid development without linting validation"
    fix: "Removed unused imports (json, subprocess, Set); added explanatory comments"
    evidence:
      - type: "commit"
        sha: "b62e012"
      - type: "pr_review"
        ref: "3619599169"
    outcome: "All 4 code quality findings resolved"
    
  - title: "Systematic documentation alignment"
    context: "Session required documentation verification across all components"
    root_cause: "Rapid multi-phase delivery without systematic validation"
    fix: "Created automated diagram update system; verified all READMEs current"
    evidence:
      - type: "commit"
        sha: "ff3c5e9"
      - type: "file"
        path: "scripts/maintenance/update_diagrams.py"
    outcome: "Documentation alignment system operational"

decisions:
  - what: "Implement AfterMath logging system"
    why: "Enable AI agents to learn from session experience and resume from checkpoints"
    alternatives: ["Manual session summaries", "External logging service"]
    chosen: "Structured YAML blocks in GitHub outputs"
    tradeoffs: "Requires agent discipline to emit blocks consistently"
    outcome: "System designed and implemented"

metrics:
  tokens_used: 107199
  tokens_available: 892801
  commits: 24
  files_changed: 45
  documentation_kb: 212
  session_duration_minutes: 180
  
quality:
  tests_passing: true
  test_count: "1500+"
  coverage_percent: 72
  self_review_passes: 5
  self_review_concerns: 0
  security_scan_findings: 4
  security_scan_resolved: 4

blockers:
  - issue: "Unused imports in maintenance scripts"
    impact: "Code quality warnings"
    resolution: "Removed unused imports; validated with py_compile"
    status: "resolved"
    
  - issue: "Empty except block without comment"
    impact: "CodeQL findings"
    resolution: "Added explanatory comment for best-effort suggestion logic"
    status: "resolved"

next_steps:
  - task: "Implement AfterMath logging in all future sessions"
    priority: "high"
    status: "complete"
    
  - task: "Phase 9.1: Critical path coverage testing"
    priority: "high"
    status: "pending"
    estimated_effort: "150-200 tests, 2-3 sessions"
    
  - task: "Fix 321 broken documentation links"
    priority: "medium"
    status: "pending"
    estimated_effort: "1-2 sessions"
    
  - task: "Agent normalization improvements (81% → 95%)"
    priority: "medium"
    status: "pending"
    estimated_effort: "1 session"

future_research:
  - topic: "ML-powered pattern detection in lessons learned"
    rationale: "Automatically identify recurring patterns across sessions for proactive optimization"
    potential_approach: "Train classifier on lesson root_cause → fix pairs; suggest preemptive solutions"
    estimated_complexity: "medium"
    dependencies: ["Sufficient lessons corpus (50+ sessions)", "ML infrastructure"]
    expected_impact: "Reduce recurring issues by 30-40%"
    
  - topic: "Automated test generation from coverage gaps"
    rationale: "AI generates tests for uncovered code paths based on code analysis"
    potential_approach: "AST analysis + GPT-4 to generate pytest fixtures and test cases"
    estimated_complexity: "high"
    dependencies: ["Coverage data", "Code understanding model", "Test execution sandbox"]
    expected_impact: "Accelerate coverage improvement 2-3x"
    
  - topic: "Session checkpoint resume with context injection"
    rationale: "Resume interrupted sessions with full context from checkpoint data"
    potential_approach: "Load checkpoint YAML, inject into system prompt with phase status"
    estimated_complexity: "low"
    dependencies: ["Checkpoint storage", "Prompt engineering"]
    expected_impact: "Enable seamless multi-session workflows"
    
  - topic: "Cognitive brain predictive analytics"
    rationale: "Predict blockers and estimate effort based on historical patterns"
    potential_approach: "Time series analysis on metrics + blocker history"
    estimated_complexity: "medium"
    dependencies: ["Historical aftermath data", "Analytics framework"]
    expected_impact: "Improve planning accuracy 20-30%"

status: "complete"
phases_complete: ["6", "7", "8"]
phases_active: ["9"]
overall_health: "excellent"
```

## Fallback Inline Tags

If fenced blocks are not feasible, emit fallback inline tags:

```
<!--AFTERMATH:SESSION_ID=S-PR2671-Previous Cycle-12-30-1-->
<!--AFTERMATH:LESSONS_COUNT=2-->
<!--AFTERMATH:LESSON_1="Code quality: Removed unused imports (b62e012)"-->
<!--AFTERMATH:LESSON_2="Documentation: Created diagram update system (ff3c5e9)"-->
<!--AFTERMATH:DECISIONS_COUNT=1-->
<!--AFTERMATH:DECISION_1="AfterMath logging system implemented"-->
<!--AFTERMATH:METRICS:TOKENS=107199/1000000-->
<!--AFTERMATH:METRICS:COMMITS=24-->
<!--AFTERMATH:QUALITY:TESTS_PASSING=true-->
<!--AFTERMATH:QUALITY:COVERAGE=72%-->
<!--AFTERMATH:FUTURE_RESEARCH_COUNT=4-->
<!--AFTERMATH:FUTURE_RESEARCH_1="ML-powered pattern detection (medium complexity)"-->
<!--AFTERMATH:FUTURE_RESEARCH_2="Automated test generation (high complexity)"-->
<!--AFTERMATH:FUTURE_RESEARCH_3="Session checkpoint resume (low complexity)"-->
<!--AFTERMATH:FUTURE_RESEARCH_4="Cognitive brain predictive analytics (medium complexity)"-->
<!--AFTERMATH:STATUS=complete-->
<!--AFTERMATH:END-->
```

## Validation

The AfterMath Action Workflow will:
1. Parse `$GITHUB_STEP_SUMMARY` and PR comments
2. Extract `aftermath` blocks or inline tags
3. Validate schema completeness
4. Generate durable artifacts:
   - `lessons_learned.md` (cumulative)
   - `session_metrics.json` (time series)
   - `checkpoint_state.yaml` (resume data)
5. Update cognitive brain with findings

## Integration Requirements

### For GitHub Copilot Agent Sessions

1. **Start of Session**: Load previous checkpoints if available
2. **During Session**: Track decisions, lessons, metrics
3. **End of Session**: Emit aftermath block to:
   - `$GITHUB_STEP_SUMMARY` (workflows)
   - Final PR comment (PRs)
4. **Continuation**: Reference previous session_id for continuity

### For Repository Maintainers

1. Enable AfterMath Action Workflow in `.github/workflows/aftermath.yml`
2. Configure artifact storage location
3. Integrate with cognitive brain updates
4. Set retention policy for checkpoint data

## Usage Example

```yaml
# .github/workflows/aftermath.yml
name: AfterMath Lessons Learned

on:
  pull_request:
    types: [closed]
  workflow_run:
    workflows: ["*"]
    types: [completed]

jobs:
  capture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Parse AfterMath Blocks
        run: |
          python scripts/aftermath/parse_session.py \
            --source=$GITHUB_STEP_SUMMARY \
            --output=.codex/lessons_learned/
      - name: Update Cognitive Brain
        run: |
          python scripts/aftermath/update_cognitive_brain.py \
            --lessons=.codex/lessons_learned/ \
            --dashboard=docs/system/CODEBASE_DASHBOARD.md
      - uses: actions/upload-artifact@v4
        with:
          name: aftermath-artifacts
          path: .codex/lessons_learned/
```

## Success Criteria

- ✅ Aftermath blocks emitted in every session
- ✅ Lessons learned cumulative file updated
- ✅ Metrics tracking operational
- ✅ Checkpoint resume tested and working
- ✅ Cognitive brain integration complete
- ✅ All future Copilot sessions adopt standard

## Best Practices

1. **Be Specific**: Include commit SHAs, file paths, line numbers
2. **Include Evidence**: Links to PRs, issues, logs, runs
3. **Quantify Impact**: Time saved, bugs prevented, coverage gained
4. **Track Decisions**: Why choices were made, alternatives considered
5. **Update Metrics**: Token usage, session duration, work completed
6. **Document Blockers**: What stopped progress, how resolved
7. **Plan Next Steps**: Clear priorities and estimates

## Maintenance

- **Version**: Update when schema changes
- **Testing**: Validate parser on sample blocks monthly
- **Review**: Audit lessons learned quarterly for patterns
- **Refinement**: Adjust schema based on usage feedback

## References

- AfterMath Parser: `scripts/aftermath/parse_session.py`
- Cognitive Brain Update: `scripts/aftermath/update_cognitive_brain.py`
- Lessons Archive: `.codex/lessons_learned/`
- Checkpoint Storage: `.codex/checkpoints/`
- Dashboard Integration: `docs/system/CODEBASE_DASHBOARD.md`

---

**Note**: This is a living standard. As AI agents evolve, the schema and tooling will adapt. Feedback from usage will drive continuous improvement of the AfterMath system.
