# PHASE 5 LANE 5.2B: MyPy Type Checker Health Report

**Generated:** 2026-06-27T03:35:50Z
**Mode:** Strict Type Checking

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Type Errors | 3723 |
| Unique Files Affected | 729 |
| Current Baseline | 1070 |
| Status | ⚠️ BASELINE EXCEEDED |

## Error Distribution by Severity

| Severity | Count |
|----------|-------|
| HIGH | 1381 |
| MEDIUM | 1935 |
| LOW | 199 |

## Top Error Codes (Priority Order)

| Code | Count | Category | Auto-Fixable |
|------|-------|----------|--------------|
| `[no-untyped-def]` | 1249 | MYPY-MISSING-RETURN-TYPE | ✅ |
| `[type-arg]` | 571 | MYPY-MISSING-TYPE-ARGS | ✅ |
| `[no-any-return]` | 406 | MYPY-ANY-RETURN | ❌ |
| `[no-untyped-call]` | 352 | MYPY-UNTYPED-CALL | ❌ |
| `[assignment]` | 297 | MYPY-INCOMPATIBLE-ASSIGNMENT | ❌ |
| `[untyped-decorator]` | 199 | MYPY-UNTYPED-DECORATOR | ❌ |
| `[misc]` | 149 | MYPY-MISC | ❌ |
| `[attr-defined]` | 132 | MYPY-ATTR-UNDEFINED | ❌ |
| `[arg-type]` | 114 | MYPY-ARG-TYPE | ✅ |
| `[union-attr]` | 46 | MYPY-UNION-ATTR | ✅ |
| `[no-redef]` | 35 | UNKNOWN | ❌ |
| `[index]` | 33 | UNKNOWN | ❌ |
| `[call-arg]` | 30 | UNKNOWN | ❌ |
| `[return-value]` | 26 | UNKNOWN | ❌ |
| `[operator]` | 14 | UNKNOWN | ❌ |

## Auto-Fixable Error Patterns

### MYPY-MISSING-RETURN-TYPE
- **Count:** 1249
- **Description:** Function missing return type annotation
- **Fix Method:** Add -> None or proper return type annotation
- **Severity:** HIGH

### MYPY-MISSING-TYPE-ARGS
- **Count:** 571
- **Description:** Missing type arguments for generic type
- **Fix Method:** Add type parameters (e.g., dict[str, Any])
- **Severity:** MEDIUM

### MYPY-ARG-TYPE
- **Count:** 114
- **Description:** Incompatible argument type
- **Fix Method:** Fix argument type or add type: ignore[arg-type]
- **Severity:** MEDIUM

### MYPY-UNION-ATTR
- **Count:** 46
- **Description:** Union type attribute access without narrowing
- **Fix Method:** Narrow union type or add isinstance guard
- **Severity:** MEDIUM

**Total Auto-Fixable Errors:** 1980

## Top Files Requiring Remediation

| File | Error Count | Primary Issues |
|------|-------------|-----------------|
| `src/codex_ml/train_loop.py` | 54 | `[no-untyped-def]` |
| `src/codex_ml/plugins/registries.py` | 50 | `[no-untyped-def]` |
| `src/training/engine_hf_trainer.py` | 50 | `[no-untyped-call]` |
| `src/codex_ml/__init__.py` | 43 | `[misc]` |
| `transformers/__init__.py` | 40 | `[no-untyped-def]` |
| `src/codex/training.py` | 38 | `[no-untyped-def]` |
| `src/context_management/observability.py` | 32 | `[type-arg]` |
| `src/tests/test_concurrency_protection.py` | 31 | `[no-untyped-def]` |
| `src/zendesk/api_client.py` | 29 | `[no-any-return]` |
| `src/codex_ml/training/legacy_api.py` | 28 | `[no-untyped-def]` |
| `src/codex_ml/serving/inference_server.py` | 28 | `[assignment]` |
| `agents/physics_orchestrator.py` | 27 | `[no-untyped-def]` |
| `src/tests/test_session_embeddings_phase4.py` | 26 | `[no-untyped-def]` |
| `src/codex_ml/ast/tests/test_node.py` | 25 | `[no-untyped-def]` |
| `src/codex_ml/ast/tests/test_graph.py` | 23 | `[no-untyped-def]` |
| `src/codex_ml/cli/main.py` | 23 | `[untyped-decorator]` |
| `src/codex_ml/ast/tests/test_analyzers.py` | 22 | `[no-untyped-def]` |
| `src/codex_ml/evaluation/loop.py` | 22 | `[type-arg]` |
| `src/codex/brain/ooda_orchestrator.py` | 22 | `[arg-type]` |
| `src/codex/github/mcp_poster.py` | 21 | `[no-any-return]` |
| `src/codex/archive/backend.py` | 21 | `[call-arg]` |
| `src/codex/rag/embeddings.py` | 20 | `[no-untyped-def]` |
| `src/codex_ml/serving/optimizations.py` | 20 | `[no-untyped-def]` |
| `src/codex_ml/tokenization/hf_tokenizer.py` | 19 | `[attr-defined]` |
| `src/codex/cli/main.py` | 19 | `[no-untyped-def]` |

## Remediation Strategy

### Phase 1: High-Priority Auto-Fixes
1. **Missing Return Type Annotations** ([no-untyped-def]: 1249 errors)
   - Add `-> None` to functions with no return statement
   - Add proper return type to functions returning values
   - Estimate: 800+ errors fixable in this pass

2. **Missing Type Arguments** ([type-arg]: 571 errors)
   - Convert bare `dict` to `dict[str, Any]`
   - Convert bare `tuple` to `tuple[Any, ...]`
   - Estimate: 300+ errors fixable in this pass

3. **Argument Type Mismatches** ([arg-type]: 114 errors)
   - Add type: ignore[arg-type] for externally-typed functions
   - Estimate: 60+ errors fixable in this pass

### Phase 2: Manual Review & Complex Fixes
1. **Untyped Calls** ([no-untyped-call]: 352 errors)
   - Requires annotating upstream functions
2. **Any Returns** ([no-any-return]: 406 errors)
   - Requires narrowing return types
3. **Attribute Errors** ([attr-defined]: 132 errors)
   - Requires structural fixes

## Action Items for Next Sessions

- [ ] Apply no-untyped-def auto-fixes (should reduce errors ~500+)
- [ ] Apply type-arg auto-fixes (should reduce errors ~300+)
- [ ] Review and fix assignment errors (requires type narrowing)
- [ ] Implement union-attr guards for optional attributes
- [ ] Update .mypy_baseline once fixes are applied

## Technical Debt by Module

| Module | Errors | Complexity |
|--------|--------|------------|
| codex_ml | 300+ | HIGH - Type annotations needed across training pipeline |
| cognitive_brain | 150+ | HIGH - Complex async/union types |
| codex | 120+ | MEDIUM - Core library type improvements |
| training | 100+ | MEDIUM - ML framework integration types |
| tests | 100+ | LOW - Test-specific typing (can defer) |

## Next Steps

1. **Session S286**: Apply auto-fixable patterns (no-untyped-def, type-arg)
2. **Session S287**: Review and fix assignment + union-attr errors
3. **Session S288**: Complete remaining manual fixes and update baseline
4. **Goal**: Reduce errors from 3723 → ~1070 baseline (70% reduction)
