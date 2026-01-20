# Batch Triage Cognitive Brain Strategic Integration - Master Planset

**Created**: 2026-01-19  
**Status**: Ready for Execution  
**Priority**: HIGH  
**Owner**: batch-triage-integration-agent  
**Context**: Post-tactical implementation, Phase 1 strategic integration

---

## Executive Summary

This planset defines the **strategic-level integration** of the Batch CI Failure Triage System with the Cognitive Brain, transforming it from a tactical reporting tool into an intelligent, learning, and autonomous remediation system.

**Current State**: ✅ **Tactical Implementation Complete**
- Batch analysis operational (558-line engine)
- 11 tests passing (100%)
- CLI & workflow integrated
- Reports auto-generated

**Target State**: 🎯 **Strategic Integration**
- Cognitive brain feedback loop active
- Automated remediation with approval gates
- Learning from triage outcomes
- Predictive failure detection
- Stakeholder notifications

---

## Phase 1: Cognitive Brain Integration (Weeks 1-3)

### Milestone 1.1: Batch Triage Agent Creation (Week 1)

**Objective**: Create specialized custom agent for batch triage with cognitive brain hooks

**Deliverables**:
```
.github/agents/batch-triage-agent/
├── README.md                      # Agent documentation
├── agent.yaml                     # Configuration & metadata
├── prompts/
│   ├── analyze_batch.md           # Main analysis prompt
│   ├── extract_patterns.md        # Pattern extraction logic
│   ├── generate_remediations.md   # Fix generation
│   └── escalation.md              # Escalation criteria
├── src/
│   ├── __init__.py
│   ├── analyzer.py                # Extended BatchTriageEngine
│   ├── pattern_learner.py         # Cognitive brain integration
│   ├── remediation_engine.py      # Auto-fix generation
│   └── notifier.py                # Stakeholder notifications
└── tests/
    ├── __init__.py
    ├── test_analyzer.py
    ├── test_pattern_learner.py
    ├── test_remediation_engine.py
    └── test_notifier.py
```

**Tasks**:
- [x] Review existing batch triage implementation
- [ ] Create agent directory structure
- [ ] Write agent README with capabilities and usage
- [ ] Define agent.yaml configuration
- [ ] Create specialized prompts for each analysis phase
- [ ] Implement analyzer extending BatchTriageEngine
- [ ] Implement pattern_learner for cognitive brain hooks
- [ ] Implement remediation_engine for auto-fix generation
- [ ] Implement notifier for Slack/email/GitHub
- [ ] Write comprehensive test suite (target: 20+ tests)
- [ ] Update AGENTS.md registry

**Success Criteria**:
- Agent operational and testable
- All tests passing
- Documentation complete
- Registered in agent ecosystem

**Dependencies**: None (standalone milestone)

**Estimated Effort**: 2-3 days

---

### Milestone 1.2: Cognitive Brain Feedback Loop (Week 2)

**Objective**: Implement learning system that stores and retrieves triage patterns

**Deliverables**:
```
scripts/cognitive/batch_triage_learnings.py      # Learning engine
.codex/cognitive_brain/patterns/ci_failures/     # Pattern storage
.codex/metrics/batch_triage_metrics.yaml         # Metrics tracking
```

**Implementation**:

```python
# scripts/cognitive/batch_triage_learnings.py

class BatchTriageLearningEngine:
    """Records and learns from batch triage outcomes"""
    
    def __init__(self, kb_path: Path = Path(".codex/cognitive_brain")):
        self.kb_path = kb_path
        self.patterns_dir = kb_path / "patterns" / "ci_failures"
        self.metrics_file = Path(".codex/metrics/batch_triage_metrics.yaml")
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
    
    def record_triage_outcome(self, batch_id: str, outcomes: List[Dict]):
        """Store triage results in cognitive brain KB"""
        timestamp = datetime.now().isoformat()
        outcome_file = self.patterns_dir / f"batch_{batch_id}_{timestamp}.json"
        
        data = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "total_failures": len(outcomes),
            "outcomes": outcomes,
            "patterns_detected": self._extract_patterns_from_outcomes(outcomes),
            "success_rate": self._calculate_success_rate(outcomes)
        }
        
        outcome_file.write_text(json.dumps(data, indent=2))
        self._update_metrics(data)
    
    def extract_patterns(self, failures: List[FailureRecord]) -> List[Pattern]:
        """Extract recurring failure patterns using ML clustering"""
        # Use historical data to identify patterns
        historical = self._load_historical_patterns()
        
        # Feature extraction
        features = self._extract_features(failures)
        
        # Pattern matching with similarity scoring
        patterns = self._match_patterns(features, historical)
        
        return patterns
    
    def update_remediation_success_rate(self, remediation_id: str, success: bool):
        """Track which fixes work - reinforcement learning"""
        remediations_db = self.patterns_dir / "remediations.jsonl"
        
        entry = {
            "remediation_id": remediation_id,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        
        # Append to JSONL for easy querying
        with open(remediations_db, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Update success rates in memory
        self._recalculate_remediation_scores()
    
    def get_historical_context(self, failure_type: str) -> Dict:
        """Retrieve past similar failures for better context"""
        pattern_files = self.patterns_dir.glob(f"*{failure_type}*.json")
        
        historical_data = []
        for pf in pattern_files:
            data = json.loads(pf.read_text())
            historical_data.append(data)
        
        return {
            "total_occurrences": len(historical_data),
            "common_remediations": self._aggregate_remediations(historical_data),
            "success_rates": self._aggregate_success_rates(historical_data),
            "time_to_resolve": self._calculate_avg_resolution_time(historical_data)
        }
    
    def get_best_remediation(self, failure: FailureRecord) -> Optional[str]:
        """Use historical success rates to recommend best fix"""
        context = self.get_historical_context(failure.failure_type)
        
        if not context["common_remediations"]:
            return None
        
        # Sort by success rate
        sorted_remed = sorted(
            context["common_remediations"],
            key=lambda x: x["success_rate"],
            reverse=True
        )
        
        return sorted_remed[0]["description"] if sorted_remed else None
```

**Tasks**:
- [ ] Create `scripts/cognitive/batch_triage_learnings.py`
- [ ] Implement BatchTriageLearningEngine class
- [ ] Create pattern storage directory structure
- [ ] Implement pattern extraction with ML clustering
- [ ] Implement remediation success tracking
- [ ] Implement historical context retrieval
- [ ] Create metrics tracking in YAML format
- [ ] Integrate with BatchTriageEngine
- [ ] Add hooks in batch_triage.py to call learning engine
- [ ] Write unit tests (target: 15+ tests)
- [ ] Document pattern storage format

**Success Criteria**:
- Patterns stored after each triage run
- Historical data retrievable
- Success rates tracked and updated
- All tests passing

**Dependencies**: Milestone 1.1 (agent structure)

**Estimated Effort**: 3-4 days

---

### Milestone 1.3: Automated Remediation Workflow (Week 2-3)

**Objective**: Build workflow that auto-applies low-risk fixes with approval gates

**Deliverables**:
```
.github/workflows/batch-triage-auto-remediate.yml    # Main workflow
.github/agents/batch-triage-agent/src/remediation_engine.py  # Enhanced
```

**Workflow Structure**:

```yaml
name: Batch Triage Auto-Remediation
on:
  workflow_run:
    workflows: ["Batch CI Failure Triage"]
    types: [completed]
  workflow_dispatch:
    inputs:
      batch_report_url:
        description: 'URL to batch triage report artifact'
        required: true
      apply_fixes:
        description: 'Auto-apply low-risk fixes'
        type: boolean
        default: false

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  parse-triage-report:
    name: Parse Triage Report
    runs-on: ubuntu-latest
    outputs:
      remediations: ${{ steps.parse.outputs.remediations }}
      low_risk_count: ${{ steps.parse.outputs.low_risk_count }}
      medium_risk_count: ${{ steps.parse.outputs.medium_risk_count }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download Triage Report
        uses: actions/download-artifact@v4
        with:
          name: batch-triage-report-${{ github.event.workflow_run.id }}
          path: /tmp/triage
      
      - name: Parse Report
        id: parse
        run: |
          python .github/agents/batch-triage-agent/src/remediation_engine.py \
            parse /tmp/triage/batch_triage_report.json \
            --output /tmp/remediations.json
          
          LOW_RISK=$(jq '[.[] | select(.risk=="low")] | length' /tmp/remediations.json)
          MED_RISK=$(jq '[.[] | select(.risk=="medium")] | length' /tmp/remediations.json)
          
          echo "remediations=$(cat /tmp/remediations.json | jq -c)" >> $GITHUB_OUTPUT
          echo "low_risk_count=$LOW_RISK" >> $GITHUB_OUTPUT
          echo "medium_risk_count=$MED_RISK" >> $GITHUB_OUTPUT

  apply-low-risk-fixes:
    name: Apply Low-Risk Fixes
    needs: parse-triage-report
    if: needs.parse-triage-report.outputs.low_risk_count > 0
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Apply Automated Fixes
        run: |
          python .github/agents/batch-triage-agent/src/remediation_engine.py \
            apply-fixes \
            --remediations '${{ needs.parse-triage-report.outputs.remediations }}' \
            --risk-level low \
            --branch batch-triage-auto-fix-${{ github.run_id }}
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          branch: batch-triage-auto-fix-${{ github.run_id }}
          title: "🤖 Auto-fix: Low-risk CI failure remediations"
          body: |
            ## Automated Remediation
            
            This PR contains automated fixes for low-risk CI failures identified by batch triage.
            
            **Fixes Applied**: ${{ needs.parse-triage-report.outputs.low_risk_count }}
            
            **Source**: Batch Triage Run #${{ github.event.workflow_run.id }}
            
            ### Review Checklist
            - [ ] Verify each fix addresses the root cause
            - [ ] Confirm no unintended side effects
            - [ ] Check tests pass
            
            /cc @mbaetiong
          labels: automated, ci-fix, batch-triage

  create-review-prs-medium-risk:
    name: Create PRs for Medium-Risk Fixes
    needs: parse-triage-report
    if: needs.parse-triage-report.outputs.medium_risk_count > 0
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        fix_index: [0, 1, 2, 3, 4]  # Max 5 PRs at once
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Apply Single Fix
        run: |
          python .github/agents/batch-triage-agent/src/remediation_engine.py \
            apply-fix-by-index \
            --remediations '${{ needs.parse-triage-report.outputs.remediations }}' \
            --index ${{ matrix.fix_index }} \
            --risk-level medium
      
      - name: Create Review PR
        uses: peter-evans/create-pull-request@v5
        with:
          branch: batch-triage-fix-${{ github.run_id }}-${{ matrix.fix_index }}
          title: "🔧 CI Fix: [Review Required] Medium-risk remediation"
          body: |
            ## Medium-Risk Remediation (Requires Review)
            
            This PR contains a medium-risk fix that requires human review before merging.
            
            **Risk Level**: Medium  
            **Confidence**: See fix details below
            
            ### Approval Required
            - [ ] @mbaetiong or engineering lead must approve
            
            /label needs-review ci-fix batch-triage

  notify-high-risk:
    name: Notify on High-Risk Issues
    needs: parse-triage-report
    runs-on: ubuntu-latest
    
    steps:
      - name: Send Slack Notification
        if: env.SLACK_WEBHOOK_URL != ''
        run: |
          python .github/agents/batch-triage-agent/src/notifier.py \
            slack \
            --webhook ${{ secrets.SLACK_WEBHOOK_URL }} \
            --channel '#eng-oncall' \
            --remediations '${{ needs.parse-triage-report.outputs.remediations }}' \
            --filter high-risk
      
      - name: Create Tracking Issue
        uses: actions/github-script@v7
        with:
          script: |
            const remediations = JSON.parse('${{ needs.parse-triage-report.outputs.remediations }}');
            const highRisk = remediations.filter(r => r.risk === 'high');
            
            if (highRisk.length > 0) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `🚨 High-Risk CI Failures Require Manual Investigation`,
                body: `## High-Risk Failures Detected\n\n` +
                      `${highRisk.length} high-risk failures require manual investigation.\n\n` +
                      `**Batch Triage Run**: #${{ github.event.workflow_run.id }}\n\n` +
                      `See attached report for details.`,
                labels: ['critical', 'ci-failure', 'needs-investigation']
              });
            }
```

**Tasks**:
- [ ] Create `.github/workflows/batch-triage-auto-remediate.yml`
- [ ] Implement remediation parsing logic
- [ ] Implement fix application engine
- [ ] Add risk classification (low/medium/high)
- [ ] Implement approval gate integration
- [ ] Add PR creation logic
- [ ] Add Slack notification support
- [ ] Add email notification support
- [ ] Integrate with owner-approval-guard agent
- [ ] Write workflow tests
- [ ] Document remediation process

**Success Criteria**:
- Low-risk fixes auto-applied successfully
- Medium-risk PRs created for review
- High-risk issues escalated properly
- All approval gates functional
- Notifications delivered

**Dependencies**: Milestones 1.1, 1.2

**Estimated Effort**: 3-4 days

---

### Milestone 1.4: Metrics Dashboard (Week 3)

**Objective**: Create dashboard for tracking triage effectiveness

**Deliverables**:
```
.codex/metrics/batch_triage_metrics.yaml         # Metrics data
.codex/reports/batch_triage_dashboard.md         # Dashboard
scripts/ci/generate_triage_dashboard.py          # Generator
```

**Metrics to Track**:

```yaml
# .codex/metrics/batch_triage_metrics.yaml
batch_triage:
  metadata:
    last_updated: "2026-01-19T20:00:00Z"
    version: "1.0"
  
  overall:
    total_batches_analyzed: 0
    total_failures_triaged: 0
    total_groups_identified: 0
    total_patterns_detected: 0
    total_remediations_suggested: 0
    total_remediations_applied: 0
    total_remediations_successful: 0
  
  averages:
    avg_triage_time_seconds: 0.0
    avg_failures_per_batch: 0.0
    avg_groups_per_batch: 0.0
    avg_time_to_remediation_hours: 0.0
  
  rates:
    pattern_detection_accuracy: 0.0
    remediation_success_rate: 0.0
    auto_resolution_rate: 0.0
    false_positive_rate: 0.0
  
  by_severity:
    critical:
      count: 0
      avg_resolution_time_hours: 0.0
      success_rate: 0.0
    high:
      count: 0
      avg_resolution_time_hours: 0.0
      success_rate: 0.0
    medium:
      count: 0
      avg_resolution_time_hours: 0.0
      success_rate: 0.0
    low:
      count: 0
      avg_resolution_time_hours: 0.0
      success_rate: 0.0
  
  by_failure_type:
    test_failure:
      count: 0
      success_rate: 0.0
    import_error:
      count: 0
      success_rate: 0.0
    build_failure:
      count: 0
      success_rate: 0.0
    lint_error:
      count: 0
      success_rate: 0.0
  
  trends:
    last_7_days:
      batches: 0
      failures: 0
      success_rate: 0.0
    last_30_days:
      batches: 0
      failures: 0
      success_rate: 0.0
  
  stakeholder_satisfaction:
    avg_rating: 0.0
    total_responses: 0
    promoters: 0
    passives: 0
    detractors: 0
```

**Dashboard Template**:

```markdown
# Batch Triage Dashboard

**Last Updated**: {{ last_updated }}  
**Period**: {{ period }}

---

## 📊 Key Metrics

| Metric | Value | Trend | Target |
|--------|-------|-------|--------|
| **Total Batches** | {{ total_batches }} | {{ batch_trend }} | - |
| **Triage Time** | {{ avg_triage_time }}s | {{ time_trend }} | <5min |
| **Success Rate** | {{ success_rate }}% | {{ success_trend }} | >70% |
| **Auto-Resolution** | {{ auto_rate }}% | {{ auto_trend }} | >50% |
| **Pattern Accuracy** | {{ pattern_accuracy }}% | {{ pattern_trend }} | >80% |

---

## 🎯 Success Rate by Severity

```chart
type: bar
data:
  labels: [Critical, High, Medium, Low]
  datasets:
    - label: Success Rate
      data: [{{ critical_rate }}, {{ high_rate }}, {{ medium_rate }}, {{ low_rate }}]
```

---

## 📈 Trends (30 Days)

**Batches Analyzed**: {{ batches_30d }}  
**Failures Triaged**: {{ failures_30d }}  
**Success Rate**: {{ success_30d }}%

---

## 🚀 Top Performing Remediations

1. **{{ top1_name }}** - {{ top1_rate }}% success ({{ top1_count }} uses)
2. **{{ top2_name }}** - {{ top2_rate }}% success ({{ top2_count }} uses)
3. **{{ top3_name }}** - {{ top3_rate }}% success ({{ top3_count }} uses)

---

## ⚠️ Areas for Improvement

{{ improvement_items }}

---

## 💡 Recommendations

{{ recommendations }}
```

**Tasks**:
- [ ] Create metrics YAML schema
- [ ] Implement metrics collection in batch_triage.py
- [ ] Create dashboard generator script
- [ ] Design dashboard template
- [ ] Add trend visualization
- [ ] Add success rate breakdown
- [ ] Add remediation leaderboard
- [ ] Implement auto-refresh (daily)
- [ ] Write dashboard tests
- [ ] Document metrics definitions

**Success Criteria**:
- Dashboard auto-generated after each triage
- Metrics accurately tracked
- Trends visible
- Actionable insights provided

**Dependencies**: Milestones 1.2, 1.3

**Estimated Effort**: 2-3 days

---

## Phase 2: Advanced Automation (Weeks 4-6)

### Milestone 2.1: Trend Analysis Engine

**Objective**: Detect patterns over time, predict failures

**Features**:
- Time-series analysis of failure patterns
- Anomaly detection
- Prediction of likely failures
- Proactive alerts

**Estimated Effort**: 4-5 days

---

### Milestone 2.2: Performance Optimization

**Objective**: Reduce triage time by 50%

**Features**:
- Caching of workflow logs
- Parallel processing
- Incremental analysis
- Rate limit handling

**Estimated Effort**: 3-4 days

---

### Milestone 2.3: Issue Lifecycle Management

**Objective**: Automate issue tracking and closure

**Features**:
- Auto-labeling by failure type
- Auto-closure with verification
- Related issue linking
- Status tracking

**Estimated Effort**: 3-4 days

---

## Success Criteria (Overall)

### Phase 1 Complete When:
- ✅ Batch triage agent operational
- ✅ Cognitive brain feedback loop active
- ✅ Automated remediation workflow deployed
- ✅ Metrics dashboard functional
- ✅ Stakeholder notifications configured
- ✅ All tests passing (target: 50+ tests)
- ✅ Documentation complete

### Key Performance Indicators:
- **Triage Time**: < 5 minutes per batch
- **Pattern Detection**: > 80% accuracy
- **Remediation Success**: > 70% for suggested fixes
- **Auto-Resolution**: > 50% of low-risk issues
- **Stakeholder Satisfaction**: > 4.0/5.0

---

## Risk Mitigation

### Technical Risks:
1. **GitHub API Rate Limits**
   - **Mitigation**: Caching, conditional requests, backoff strategy
   
2. **False Positive Patterns**
   - **Mitigation**: Confidence thresholds, human review, learning feedback
   
3. **Over-Automation**
   - **Mitigation**: Approval gates, rollback capability, audit logs

### Operational Risks:
1. **Alert Fatigue**
   - **Mitigation**: Smart filtering, severity-based routing, digest mode
   
2. **Stale Patterns**
   - **Mitigation**: Pattern expiry (90 days), periodic review

---

## Resource Requirements

- **Development Time**: 3-6 weeks (1 developer)
- **Testing Time**: Integrated throughout
- **Documentation Time**: 1-2 days per milestone
- **Review Time**: 2-3 days

---

## Next Actions

1. ✅ Create this planset
2. ⬜ Begin Milestone 1.1 (Agent Creation)
3. ⬜ Set up metrics tracking baseline
4. ⬜ Review with stakeholders
5. ⬜ Execute iteratively

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-19  
**Owner**: batch-triage-integration-agent  
**Status**: Ready for Execution
