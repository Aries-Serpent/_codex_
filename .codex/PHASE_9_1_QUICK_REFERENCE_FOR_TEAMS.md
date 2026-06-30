# Phase 9.1 Quick Reference — For Phase 9.2 & 9.3 Teams

**Version**: 1.0.0  
**Date**: 2026-06-30  
**Audience**: Phase 9.2 & 9.3 agent teams  
**Authority**: orchestrator-agent (D-tier)

---

## 🎯 Overview

Phase 9.1 has established a **D_CAPABLE decision framework** that provides:
- Immutable decision logging
- Confidence-based escalation
- Human approval workflows
- Complete audit trail

This guide shows how to **integrate Phase 9.1 into your Phase 9.2/9.3 operations**.

---

## 📦 Phase 9.1 Deliverables

| Component | Location | Type | Status |
|-----------|----------|------|--------|
| Decision Logger | `scripts/ci/phase_9_1_decision_logger.py` | Python CLI | ✅ Operational |
| Confidence Scorer | `scripts/ci/phase_9_1_confidence_scorer.py` | Python CLI | ✅ Operational |
| Test Suite | `tests/unit/test_phase_9_1_decisions.py` | Pytest | ✅ 100/100 passing |
| Framework Spec | `.codex/archive/phases/PHASE_9_1_DECISION_FRAMEWORK.md` | Reference | ✅ Complete |
| Operational Status | `.codex/PHASE_9_1_OPERATIONAL_STATUS_*.md` | Dashboard | ✅ Live |

---

## 🚀 Quick Start (5 minutes)

### 1. Log Your First Decision

```bash
cd /home/runner/work/_codex_/_codex_

# Log a decision
python scripts/ci/phase_9_1_decision_logger.py execute \
  --agent "ci-auto-healer-agent" \
  --decision-type "B" \
  --confidence 85 \
  --context '{"error": "timeout"}' \
  --output '{"action": "increase_timeout"}'
```

### 2. Query Your Decisions

```bash
# Get all decisions for your agent in the last 24 hours
python scripts/ci/phase_9_1_decision_logger.py query \
  --agent "ci-auto-healer-agent" \
  --since "2026-06-30T00:00:00Z"

# Get only high-confidence decisions
python scripts/ci/phase_9_1_decision_logger.py query \
  --agent "ci-auto-healer-agent" \
  --confidence-min 80

# Get only escalated decisions
python scripts/ci/phase_9_1_decision_logger.py query \
  --agent "ci-auto-healer-agent" \
  --escalated
```

### 3. Check Agent Accuracy

```bash
# Get accuracy metrics for your agent
python scripts/ci/phase_9_1_decision_logger.py accuracy \
  --agent "ci-auto-healer-agent"
```

### 4. Export Your Audit Trail

```bash
# Export all decisions to JSON
python scripts/ci/phase_9_1_decision_logger.py export \
  --agent "ci-auto-healer-agent" \
  --format json \
  --output audit_trail.json
```

---

## 📊 Decision Types & Thresholds

### Type A: Low-Risk, Read-Only
**Examples**: Pattern analysis, static validation, audits
- **Execute if**: Confidence ≥ 80%
- **Escalate if**: Confidence < 65%

### Type B: Medium-Risk, Structured Modifications
**Examples**: Workflow updates, test changes, configuration
- **Execute if**: Confidence ≥ 75%
- **Escalate if**: Confidence < 60-65%

### Type C: High-Risk, Code Modifications
**Examples**: Test logic changes, CI modifications
- **Execute if**: Confidence ≥ 75% (conditional)
- **Escalate if**: Confidence < 60% (CRITICAL)

### Type D: System-Critical
**Examples**: Security changes, deployments
- **Always human pre-approved**

---

## 🧮 Confidence Scoring Formula

```
Confidence = (H × 0.40) + (T × 0.30) + (C × 0.20) + (M × 0.10)

Where:
  H = Historical accuracy baseline (0-100)
  T = Context complexity (0-100, inverse: lower=better)
  C = Test coverage percentage (0-100)
  M = Manual override signals (0-100, default 50)
```

### Calculate Your Confidence Score

```bash
python scripts/ci/phase_9_1_confidence_scorer.py score \
  --agent "ci-auto-healer-agent" \
  --decision-type "B" \
  --historical-accuracy 85 \
  --context-complexity 40 \
  --test-coverage 92
```

---

## 🔗 Integration with Your Agent

### Option 1: Use CLI (Recommended for simple integration)

```bash
#!/bin/bash
# your_agent_workflow.sh

# Your agent decision logic
python your_agent.py > decision_output.json

# Log the decision
python scripts/ci/phase_9_1_decision_logger.py execute \
  --agent "your-agent-name" \
  --decision-type "B" \
  --confidence $(jq '.confidence' decision_output.json) \
  --context "$(jq '.context' decision_output.json)" \
  --output "$(jq '.output' decision_output.json)"
```

### Option 2: Direct Python Integration (For complex logic)

```python
from scripts.ci.phase_9_1_decision_logger import DecisionLogger
from scripts.ci.phase_9_1_confidence_scorer import ConfidenceScorer

# Initialize loggers
logger = DecisionLogger()
scorer = ConfidenceScorer()

# Your decision logic
context = {"error": "test_timeout", "attempt": 1}
historical_accuracy = 85
test_coverage = 92

# Calculate confidence
confidence = scorer.score(
    agent_id="your-agent-name",
    decision_type="B",
    historical_accuracy=historical_accuracy,
    context_complexity=40,
    test_coverage=test_coverage
)

# Check if should escalate
threshold = scorer.get_threshold("your-agent-name", "B")
if confidence < threshold:
    # Escalate to human
    decision_id = logger.execute(
        agent_id="your-agent-name",
        decision_type="B",
        confidence_score=confidence,
        context=context,
        output={"action": "escalate_to_human"},
        escalation_reason=f"Confidence {confidence}% below threshold {threshold}%"
    )
else:
    # Execute decision
    decision_id = logger.execute(
        agent_id="your-agent-name",
        decision_type="B",
        confidence_score=confidence,
        context=context,
        output={"action": "fix_timeout", "new_value": 30}
    )
```

---

## ✅ Authorized Agents

Your agent **must be one of the 9 authorized agents** to use Phase 9.1 logging:

1. **ci-auto-healer-agent** — 85% baseline, <3% FP
2. **autonomous-test-healer-agent** — 88% baseline, <2% FP
3. **test-alignment-fixer** — 82% baseline, <1% FP
4. **code-analysis-agent** — 80% baseline, <2% FP
5. **unified-coverage-agent** — 81% baseline, <1% FP
6. **doc-freshness-checker** — 84% baseline, <2% FP
7. **link-validator-agent** — 89% baseline, <1% FP
8. **dependency-conflict-agent** — 83% baseline, <2% FP
9. **test-failure-analyzer-agent** — 82% baseline, <2% FP

**Not authorized?** → Contact @mbaetiong for authorization

---

## 📈 Monitoring Your Decisions

### View All Your Decisions

```bash
python scripts/ci/phase_9_1_decision_logger.py query \
  --agent "your-agent-name" \
  --since "2026-06-30T00:00:00Z" \
  --limit 100
```

### Track Accuracy Over Time

```bash
python scripts/ci/phase_9_1_decision_logger.py accuracy \
  --agent "your-agent-name"
```

**Output**:
```
Agent: your-agent-name
Total Decisions: 42
Successful: 40 (95.2%)
Escalated: 2 (4.8%)
False Positives: 0 (0%)
Average Confidence: 84.3%
```

### Find Low-Confidence Decisions

```bash
python scripts/ci/phase_9_1_decision_logger.py query \
  --agent "your-agent-name" \
  --confidence-max 70
```

---

## 🆘 Troubleshooting

### "Agent not authorized" Error

```
Error: your-agent-name is not in authorized agent list
```

**Solution**: Your agent must be one of the 9 authorized agents. Contact @mbaetiong for authorization.

### "Decision Logger not found" Error

```
Error: Cannot locate phase_9_1_decision_logger.py
```

**Solution**: Ensure you're running from the repo root:
```bash
cd /home/runner/work/_codex_/_codex_
```

### High Escalation Rate

If >10% of your decisions are being escalated:

1. Check your historical accuracy baseline
2. Reduce context complexity (simplify decision logic)
3. Increase test coverage for your scenarios
4. Review escalated decisions for patterns

```bash
python scripts/ci/phase_9_1_decision_logger.py query \
  --agent "your-agent-name" \
  --escalated \
  --limit 20
```

---

## 📚 Further Reading

- **Full Framework**: `.codex/archive/phases/PHASE_9_1_DECISION_FRAMEWORK.md`
- **Agent Authorization**: `.codex/archive/phases/PHASE_9_1_AGENT_AUTHORIZATION_SUMMARY.md`
- **Execution Summary**: `.codex/archive/phases/PHASE_9_1_EXECUTION_SUMMARY.md`
- **Operational Status**: `.codex/PHASE_9_1_OPERATIONAL_STATUS_*.md`
- **Test Suite**: `tests/unit/test_phase_9_1_decisions.py` (100+ examples)

---

## 🔔 Phase 9.2/9.3 Integration Points

### For Phase 9.2 Teams (Self-Healing)
- Use Phase 9.1 decision logger for all automated fixes
- Log confidence scores before auto-fixing
- Leverage escalation mechanism for suspicious patterns

### For Phase 9.3 Teams (Routing)
- Query Phase 9.1 decision history for pattern analysis
- Use agent accuracy metrics for routing decisions
- Implement semantic search over decision audit trail

---

## ⏱️ Performance Characteristics

| Operation | Time | Scale |
|-----------|------|-------|
| Log Decision | <50ms | Per decision |
| Query | <1s | Typical (100 results) |
| Accuracy Calc | <100ms | Per agent |
| Export 1000 decisions | <5s | JSON format |

---

## 📞 Support

**Questions?** 
- Check test suite: `tests/unit/test_phase_9_1_decisions.py`
- Run help: `python scripts/ci/phase_9_1_decision_logger.py --help`
- Contact: orchestrator-agent or @mbaetiong

**Issues?**
- Open GitHub issue with decision ID
- Include relevant decision log excerpt
- Tag with `phase-9-1`

---

**Generated**: 2026-06-30T19:01:23Z  
**Status**: ✅ Ready for Phase 9.2/9.3 integration  
**Authority**: orchestrator-agent (D-tier autonomous)
