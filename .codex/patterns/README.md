# Learned Patterns

This directory stores patterns automatically learned from the codebase by the Pattern Learner tool.

## Pattern Categories

- **naming/** - Naming conventions
- **architectural/** - Architectural patterns  
- **coding_style/** - Coding style patterns
- **error_handling/** - Error handling patterns
- **testing/** - Testing patterns
- **security/** - Security patterns

## Pattern Format

Each pattern is stored as JSON:
```json
{
  "id": "pattern_id",
  "name": "Pattern Name",
  "category": "category",
  "description": "Description of pattern",
  "examples": [],
  "frequency": 10,
  "confidence": 0.9,
  "learned_at": "ISO8601 timestamp",
  "last_seen": "ISO8601 timestamp"
}
```

## Usage

Patterns are automatically learned by:
```bash
python .codex/tools/pattern_learner.py
```

And can be queried by other cognitive brain tools.
