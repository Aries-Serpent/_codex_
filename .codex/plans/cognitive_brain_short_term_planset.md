# Cognitive Brain Improvement Planset - Short-term (Next 5 Sessions)

> **Generated:** 2026-02-05T09:30:00Z  
> **Planset ID:** CB-ST-2026-02-05  
> **Status:** 📋 PLANNED  
> **Timeline:** 5 Copilot sessions  
> **Owner:** GitHub Copilot Coding Agent

---

## 🎯 Planset Overview

This planset defines the implementation strategy for 4 short-term cognitive brain improvements to be executed over the next 5 Copilot coding agent sessions.

### Success Criteria
- [ ] All 4 initiatives implemented and tested
- [ ] Integration with existing cognitive brain infrastructure
- [ ] Documentation updated for each feature
- [ ] Metrics showing measurable improvement

---

## 📋 Plan 1: Pre-commit Verification Hook

### Objective
Implement automated verification that all expected files from session logs are staged before commit.

### Session: 1 of 5
**Estimated Duration:** 1 session  
**Priority:** P1 - High  
**Dependencies:** `action_log.ndjson`, `report_progress` tool

### Implementation Steps

```yaml
phase_1_analysis:
  - Review current action_log.ndjson structure
  - Identify file operation patterns (create, edit, delete)
  - Design verification algorithm

phase_2_implementation:
  - Create scripts/hooks/pre_commit_verify.py
  - Implement action_log parser
  - Implement staged files comparison
  - Add warning/error reporting

phase_3_integration:
  - Add to .pre-commit-config.yaml
  - Test with sample commits
  - Document usage

phase_4_validation:
  - Run on test scenarios
  - Verify edge cases (temp files, .gitignore)
  - Update cognitive brain with results
```

### Deliverables
| Deliverable | Path | Status |
|-------------|------|--------|
| Verification script | `scripts/hooks/pre_commit_verify.py` | 📋 Planned |
| Pre-commit config update | `.pre-commit-config.yaml` | 📋 Planned |
| Test file | `tests/test_pre_commit_verify.py` | 📋 Planned |
| Documentation | `docs/PRE_COMMIT_VERIFICATION.md` | 📋 Planned |

### Acceptance Criteria
- [ ] Hook detects uncommitted expected files
- [ ] Correctly ignores /tmp and .gitignore patterns
- [ ] Clear error messages with file paths
- [ ] No false positives on test runs
- [ ] Integrated with existing pre-commit workflow

---

## 📋 Plan 2: Automated Continuation Prompt Generator

### Objective
Automatically generate structured continuation prompts at session end for seamless handoff.

### Session: 2 of 5
**Estimated Duration:** 1 session  
**Priority:** P1 - High  
**Dependencies:** `session_manager.py`, cognitive brain infrastructure

### Implementation Steps

```yaml
phase_1_enhancement:
  - Extend session_manager.py with auto-generation
  - Add file operation tracking
  - Implement context extraction from checkpoints

phase_2_template_system:
  - Create continuation prompt templates
  - Support multiple output formats (markdown, JSON)
  - Include structured context sections

phase_3_integration:
  - Hook into report_progress workflow
  - Auto-save to .codex/prompts/continuation/
  - Generate PR comment format

phase_4_validation:
  - Test with sample sessions
  - Validate context completeness
  - Measure handoff effectiveness
```

### Deliverables
| Deliverable | Path | Status |
|-------------|------|--------|
| Enhanced session_manager | `scripts/cognitive/session_manager.py` | ✅ Partial |
| Prompt templates | `.codex/templates/continuation/` | 📋 Planned |
| Auto-generator | `scripts/cognitive/auto_continuation.py` | 📋 Planned |
| Output directory | `.codex/prompts/continuation/` | 📋 Planned |

### Acceptance Criteria
- [ ] Automatic prompt generation on session end
- [ ] Complete context transfer (completed, pending, blockers)
- [ ] Pattern recommendations included
- [ ] Objective alignment status included
- [ ] Ready-to-use PR comment format

---

## 📋 Plan 3: Session Metrics Dashboard

### Objective
Build a metrics dashboard to track session effectiveness, patterns, and objectives.

### Session: 3-4 of 5
**Estimated Duration:** 2 sessions  
**Priority:** P2 - Medium  
**Dependencies:** Pattern store, objectives tracker, session data

### Implementation Steps

```yaml
phase_1_data_collection:
  - Define metrics schema
  - Implement data collectors for:
    - Session duration
    - Tasks completed/pending
    - Patterns applied
    - Files created/modified
    - Commit success rate

phase_2_aggregation:
  - Create metrics aggregation engine
  - Implement time-series analysis
  - Add trend detection

phase_3_visualization:
  - Create markdown-based dashboard
  - Add ASCII charts for terminal
  - Generate weekly/monthly reports

phase_4_integration:
  - Auto-update on session end
  - Add to cognitive brain status
  - Create alerting for anomalies
```

### Deliverables
| Deliverable | Path | Status |
|-------------|------|--------|
| Metrics schema | `.codex/schemas/session_metrics.json` | 📋 Planned |
| Collector script | `scripts/cognitive/metrics_collector.py` | 📋 Planned |
| Dashboard generator | `scripts/cognitive/dashboard_generator.py` | 📋 Planned |
| Dashboard output | `.codex/cognitive_brain/dashboard.md` | 📋 Planned |
| Report template | `.codex/templates/weekly_report.md` | 📋 Planned |

### Metrics to Track
```yaml
session_metrics:
  - duration_minutes
  - tasks_completed
  - tasks_pending
  - patterns_applied
  - patterns_success_rate
  - files_created
  - files_modified
  - commit_success_rate
  - objective_alignment_score

aggregate_metrics:
  - avg_session_duration
  - completion_rate_trend
  - pattern_effectiveness
  - objective_progress
```

### Acceptance Criteria
- [ ] Real-time metrics collection
- [ ] Weekly trend analysis
- [ ] Visual dashboard in markdown
- [ ] Alerting for degradation
- [ ] Exportable reports

---

## 📋 Plan 4: Enhanced Agent Handoff Automation

### Objective
Automate agent-to-agent handoff with structured templates and tracking.

### Session: 5 of 5
**Estimated Duration:** 1 session  
**Priority:** P2 - Medium  
**Dependencies:** Agent handoff protocol, session manager

### Implementation Steps

```yaml
phase_1_automation:
  - Create handoff comment generator
  - Implement template selection logic
  - Add context packaging

phase_2_tracking:
  - Enhance handoff_tracking.json
  - Add handoff metrics
  - Implement success/failure tracking

phase_3_validation:
  - Add handoff verification checks
  - Implement retry logic
  - Create fallback templates

phase_4_integration:
  - Connect to session manager
  - Auto-trigger on phase completion
  - Update cognitive brain
```

### Deliverables
| Deliverable | Path | Status |
|-------------|------|--------|
| Handoff automator | `scripts/handoff/auto_handoff.py` | 📋 Planned |
| Enhanced tracking | `.codex/handoff_tracking.json` | ✅ Exists |
| Validation script | `scripts/handoff/validate_handoff.py` | 📋 Planned |
| Templates | `.codex/templates/handoff/` | ✅ Exists |

### Acceptance Criteria
- [ ] Automatic handoff comment generation
- [ ] Complete context transfer validated
- [ ] Handoff success rate tracked
- [ ] Retry logic for failed handoffs
- [ ] Integration with PR comment system

---

## 📊 Execution Timeline

```
Session 1: Pre-commit verification hook
  ├── Analysis: 15%
  ├── Implementation: 50%
  ├── Integration: 25%
  └── Validation: 10%

Session 2: Continuation prompt generator
  ├── Enhancement: 30%
  ├── Templates: 30%
  ├── Integration: 25%
  └── Validation: 15%

Session 3-4: Metrics dashboard
  ├── Data collection: 25%
  ├── Aggregation: 25%
  ├── Visualization: 30%
  └── Integration: 20%

Session 5: Agent handoff automation
  ├── Automation: 30%
  ├── Tracking: 25%
  ├── Validation: 25%
  └── Integration: 20%
```

---

## 🔗 Dependencies & Prerequisites

### Required Infrastructure
- [x] Cognitive brain directory structure
- [x] Session manager script
- [x] Pattern learning store
- [x] Objectives tracker
- [ ] Metrics schema definition
- [ ] Template system

### External Dependencies
- [x] pre-commit framework
- [x] Python 3.11+
- [x] SQLite for session logs
- [ ] ASCII chart library (optional)

---

## 📈 Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Commit verification rate | 98% | 100% | Files committed / Files expected |
| Context loss between sessions | ~20% | <5% | Survey / analysis |
| Handoff success rate | 85% | 95% | Successful handoffs / Total |
| Session effectiveness | N/A | Baseline | Tasks completed / Session |

---

## 🔄 Iteration Protocol

1. **Pre-session:** Load planset, identify current phase
2. **Execution:** Follow implementation steps
3. **Checkpoint:** Update progress, log patterns
4. **Post-session:** Update planset status, generate continuation

---

**Last Updated:** 2026-02-05T09:30:00Z  
**Next Review:** After Session 1 completion
