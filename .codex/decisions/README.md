# Decision History

This directory stores AI Agent decision history for auditability and learning.

## Decision Format

Each decision is stored as JSON:
```json
{
  "id": "decision_id",
  "timestamp": "ISO8601 timestamp",
  "context": "What was being worked on",
  "decision": "What was decided",
  "rationale": "Why this decision was made",
  "alternatives_considered": ["alt1", "alt2"],
  "outcome": "What happened",
  "learned": "What was learned"
}
```

## Usage

Decisions are automatically recorded during:
- Autonomous authorization checks
- Task orchestration
- Pattern application
- Problem solving

## Query Decisions

```bash
# Find decisions related to security
grep -r "security" .codex/decisions/

# Find recent decisions
find .codex/decisions/ -name "*.json" -mtime -7
```

## Learning from Decisions

The cognitive brain uses decision history to:
- Avoid repeating mistakes
- Apply successful strategies
- Build confidence in patterns
- Improve future decisions
