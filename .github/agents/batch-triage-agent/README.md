# Batch Triage Agent

**Purpose**: Intelligent batch CI failure triage with cognitive brain integration for learning and automated remediation  
**Status**: active  
**Maturity**: beta  
**Version**: 1.0.0

## Capabilities

- **Batch Failure Analysis**: Analyze multiple CI failures simultaneously with intelligent grouping
- **Pattern Recognition**: Learn from historical failures using cognitive brain patterns
- **Automated Remediation**: Generate and apply fixes with risk-based approval gates
- **Stakeholder Notifications**: Alert teams via Slack, email, or GitHub issues
- **Metrics Tracking**: Monitor triage effectiveness and remediation success rates
- **Cognitive Learning**: Store outcomes in knowledge base for continuous improvement

## Usage

### As GitHub Copilot Agent
```
@copilot use batch-triage-agent to analyze recent CI failures and suggest fixes
@copilot use batch-triage-agent to triage issues #2905-2915 with remediation suggestions
```

### As Standalone Tool
```bash
# Analyze batch from CSV
python .github/agents/batch-triage-agent/src/analyzer.py --from-file scripts/ci/links_extraction.csv

# Analyze specific issues
python .github/agents/batch-triage-agent/src/analyzer.py --issues 2905,2906,2907

# Generate remediation plan
python .github/agents/batch-triage-agent/src/remediation_engine.py --batch-id batch_001
```

### Via GitHub Actions
```yaml
- name: Run Batch Triage
  uses: ./.github/workflows/batch-ci-triage.yml
  with:
    issue_numbers: "2905,2906,2907"
```

## Architecture

```
Batch Triage Agent
├── analyzer.py          # Extends BatchTriageEngine
├── pattern_learner.py   # Cognitive brain integration
├── remediation_engine.py # Auto-fix generation
└── notifier.py          # Stakeholder alerts
```

### Integration with Cognitive Brain

**PDA Loop Integration**:
- **Perception**: Extract patterns from failure data
- **Decision**: Select optimal remediation based on historical success
- **Action**: Apply fixes or escalate to humans
- **Aftermath**: Record outcomes for learning

**Knowledge Base Storage**:
- Patterns: `.codex/cognitive_brain/patterns/ci_failures/`
- Metrics: `.codex/metrics/batch_triage_metrics.yaml`
- Outcomes: `.codex/cognitive_brain/patterns/ci_failures/outcomes/`

## Configuration

See `agent.yaml` for configuration options:
- Risk thresholds (low/medium/high)
- Notification channels
- Learning parameters
- Success criteria

## Integration Points

- **BatchTriageEngine**: Core triage logic from `scripts/ci/batch_triage.py`
- **Self-Healing System**: Pattern detection from `agents/self_healing.py`
- **Cognitive Brain**: Learning and storage via PDA loop
- **GitHub Actions**: Automated workflow execution
- **Owner Approval Guard**: Gating for automated changes

## Examples

### Example 1: Batch Analysis
```python
from batch_triage_agent.src.analyzer import BatchTriageAnalyzer

analyzer = BatchTriageAnalyzer()
results = analyzer.analyze_batch(issue_numbers=[2905, 2906, 2907])
print(f"Found {len(results.groups)} failure groups")
```

### Example 2: Pattern Learning
```python
from batch_triage_agent.src.pattern_learner import PatternLearner

learner = PatternLearner()
learner.record_outcome(batch_id="batch_001", success=True)
patterns = learner.get_historical_patterns("test_failure")
```

### Example 3: Auto-Remediation
```python
from batch_triage_agent.src.remediation_engine import RemediationEngine

engine = RemediationEngine()
fixes = engine.generate_fixes(failures)
low_risk = [f for f in fixes if f.risk == "low"]
engine.apply_fixes(low_risk, create_pr=True)
```

## Testing

```bash
# Run all tests
pytest .github/agents/batch-triage-agent/tests/ -v

# Run specific test module
pytest .github/agents/batch-triage-agent/tests/test_pattern_learner.py -v

# With coverage
pytest .github/agents/batch-triage-agent/tests/ --cov=.github/agents/batch-triage-agent/src
```

## Key Performance Indicators

- **Triage Time**: < 5 minutes per batch
- **Pattern Detection Accuracy**: > 80%
- **Remediation Success Rate**: > 70%
- **Auto-Resolution Rate**: > 50% for low-risk issues
- **Stakeholder Satisfaction**: > 4.0/5.0

## Changelog

### Version 1.0.0 (2026-01-19)
- Initial release
- Batch analysis with 4 grouping strategies
- Cognitive brain integration
- Automated remediation workflow
- Metrics tracking and dashboard
- 20+ comprehensive tests

## Maintainer

Batch Triage Integration Agent (automated) / Community Maintained

## Related Documentation

- **Planset**: `.codex/plans/BATCH_TRIAGE_COGNITIVE_BRAIN_INTEGRATION_PLANSET.md`
- **Self-Review**: `.codex/SELF_REVIEW_BATCH_TRIAGE_INTEGRATION.md`
- **User Guide**: `scripts/ci/README_BATCH_TRIAGE.md`
- **Continuation Prompt**: `.codex/CONTINUATION_PROMPT_BATCH_TRIAGE_PHASE2.md`
