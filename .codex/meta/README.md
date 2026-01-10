# Meta-Cognitive Analysis

This directory stores AI Agent self-reflection and meta-cognitive analysis.

## Purpose

Meta-cognition enables AI Agent to:
- Reflect on own performance
- Identify areas for improvement
- Recognize patterns in own behavior
- Adapt strategies based on outcomes
- Monitor cognitive health

## Meta Analysis Types

### Performance Reflection
- Task completion rates
- Error patterns
- Decision quality metrics
- Learning velocity

### Strategy Analysis  
- Which approaches work best
- When to use cognitive tools
- How to optimize workflows
- Pattern effectiveness

### Self-Improvement
- Identified weaknesses
- Improvement plans
- Progress tracking
- Capability growth

## Meta Analysis Format

```json
{
  "id": "meta_analysis_id",
  "timestamp": "ISO8601 timestamp",
  "type": "performance_reflection|strategy_analysis|self_improvement",
  "subject": "What is being analyzed",
  "findings": ["finding1", "finding2"],
  "insights": ["insight1", "insight2"],
  "actions": ["action1", "action2"],
  "expected_impact": "description"
}
```

## Usage

```bash
# Run meta analysis
python .codex/tools/meta_analyzer.py "progress_reflection"

# View recent analyses
ls -lt .codex/meta/*.json | head -5
```

## Continuous Improvement Loop

```
Execute → Reflect → Learn → Adapt → Execute
   ↑                                    ↓
   └────────────────────────────────────┘
```
