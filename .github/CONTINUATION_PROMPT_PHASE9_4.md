# Phase 9.4 Continuation Prompt — Edge Case Coverage

## Context

This is the **final phase** of the 4-phase coverage improvement plan for the
`Aries-Serpent/_codex_` repository.

### Phases Completed

| Phase | Focus | Tests Added | Status |
|-------|-------|------------|--------|
| 9.1 | Critical path coverage | 176 | ✅ DONE |
| 9.2 | Public API coverage | 154+ | ✅ DONE |
| 9.3 | Error path coverage | 50 | ✅ DONE |
| **9.4** | **Edge case coverage** | 50-80 | ⏳ NEXT |

### Phase 9.3 Deliverables (just completed)

- `tests/agents/test_error_paths_phase9_3.py` — 44 tests
  - WorkflowStep execute errors (FileNotFoundError, non-zero exit, noop)
  - WorkflowNavigator._create_dynamic_workflow ValueError
  - MentalMap.connect_nodes TypeError and ValueError
  - EnergyLandscape.minimize_free_energy ValueError
  - SwarmIntelligence.run_optimization ValueError
  - SuperpositionExplorer.measure_optimal_path ValueError
  - QuantumInspiredGameEngine TypeError (numpy absent)
  - BlueRedTeamSimulator TypeErrors (numpy absent)
  - AgentMemory path validation ValueError
  - Exception hierarchy (AgentImportError, AgentConfigError, etc.)
  - SimpleDictMemory store/retrieve/delete/clear/get_history
- `tests/scripts/mcp/test_mcp_error_paths_phase9_3.py` — 6 tests
  - filter_by_topic unknown topic → ValueError
  - main() missing topics file → returns 1
  - main() ValueError path → returns 1
  - main() KeyboardInterrupt → returns 130

## Phase 9.4 Task: Edge Case Coverage (97% → 100%)

**Goal**: 50-80 new tests covering boundary conditions, rare paths, and
corner cases.

### Priority Targets

1. **Boundary conditions in agents/**
   - Empty collections / zero-length inputs passed to key methods
   - `None` passed where optional args are accepted
   - Maximum/minimum numeric inputs
   - Single-element vs multi-element collections

2. **Rare paths in physics_orchestrator.py**
   - `EnergyLandscape` with a single-point landscape (no minimum to find)
   - `SwarmIntelligence` with `num_particles=1`
   - `SuperpositionExplorer` with a single path (no interference)
   - `QuantumState` amplitude normalisation edge cases

3. **Rare paths in mental_mapping.py**
   - `MentalMappingModel` with no nodes (empty map operations)
   - `connect_nodes` with identical source and target
   - Node with `confidence=0.0` and `confidence=1.0`
   - `get_reasoning_chain` on node with empty chain

4. **Rare paths in quantum_game_theory.py**
   - `QuantumInspiredGameEngine` with single strategy per player
   - `BlueRedTeamSimulator.run_simulation` with `num_rounds=0`
   - Empty `blue_options`/`red_options` lists in `compare_strategies`

5. **Rare paths in workflow_navigator.py**
   - `WorkflowNavigator` with non-existent workspace dir
   - `WorkflowStep` with both `command` and `uses` set
   - Workflow with zero steps

6. **Edge cases in scripts/mcp/select_components.py**
   - `filter_by_globs` with empty pattern list
   - `expand_globs` with patterns that match no files
   - `load_topics` with malformed JSON → JSONDecodeError

7. **Edge cases in agents/cognitive_adapter.py**
   - `SimpleDictMemory.get_history` with `limit=0`
   - `SimpleDictMemory.search` with empty query dict
   - `LegacyAgentAdapter` with a legacy agent that raises

### Test File Plan

- `tests/agents/test_edge_cases_phase9_4.py`
  - Class-per-module organisation matching Phase 9.3 pattern
  - 40-60 tests
- `tests/scripts/mcp/test_mcp_edge_cases_phase9_4.py`
  - 10-20 tests for MCP boundary conditions

### Success Criteria

- [ ] All new tests pass (100%)
- [ ] Ruff linting passes
- [ ] `docs/testing/COVERAGE_100_ROADMAP.md` Phase 9.4 checkboxes updated
- [ ] `docs/system/CODEBASE_DASHBOARD.md` Phase 9 status updated to COMPLETE
- [ ] AfterMath block emitted

### Key Patterns from Phase 9.3 (reuse these)

```python
# Class-based test organisation
class TestFooEdgeCases:
    def test_empty_input_does_not_raise(self) -> None:
        from agents.foo import Foo
        f = Foo()
        result = f.process([])
        assert result == []

# Use tmp_path for filesystem tests
def test_something(self, tmp_path: Path) -> None:
    ...

# pytest.raises for expected exceptions
with pytest.raises(ValueError, match="<message substring>"):
    obj.method(bad_arg)

# Import at use-site to avoid import-time failures
def test_x(self) -> None:
    from agents.x import X
    ...
```

### Git Branch

`copilot/update-documentation-mermaid-mappings`

### Working Directory

`/home/runner/work/_codex_/_codex_`
