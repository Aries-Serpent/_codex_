# ADR-001: Hydra Configuration Consolidation

**Date:** 2026-01-09  
**Status:** Accepted  
**Deciders:** mbaetiong, GitHub Copilot

## Context
Configuration fragmented across `conf/`, `configs/`, and hardcoded Python dictionaries causing drift and maintenance issues.

## Decision
Consolidate all configuration into Hydra-managed YAML structure in `conf/` directory with dual-path fallback for backward compatibility.

## Rationale
1. **Single Source of Truth:** Eliminates configuration drift
2. **Type Safety:** Hydra provides runtime validation
3. **Composability:** Easy configuration overrides and composition
4. **Backward Compatible:** Dual-path fallback prevents breaking changes

## Consequences

### Positive
- ✅ Reduced maintenance burden
- ✅ Better testability
- ✅ Easier configuration debugging
- ✅ 6-month migration grace period

### Negative
- ⚠️ Learning curve for Hydra
- ⚠️ Initial migration effort (32 files)

### Neutral
- 📊 Performance: <100ms config loading (acceptable)

## Alternatives Considered
1. **Pydantic-only:** Less ecosystem support
2. **Dynaconf:** Less composition features
3. **Status quo:** Technical debt accumulation

## Implementation
See: PS-01 planset, `src/codex/utils/config_loader.py`

**Last Updated:** 2026-01-09
