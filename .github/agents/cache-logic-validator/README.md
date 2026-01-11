# Cache Logic Validator Agent

> **Agent Type**: Test Automation
> **Version**: 1.0.0
> **Status**: 🟢 ACTIVE

## Purpose

Validate cache implementations using property-based testing with Hypothesis.

## Properties Tested

1. **Hit + Miss = Total Queries**
2. **Expired entries always count as miss**
3. **Concurrent access preserves counts**
4. **LRU ordering is maintained**

## Usage

```bash
python -m agents.cache_logic_validator validate src/codex/rag/cache.py
```

See `agent.yaml` for configuration.
