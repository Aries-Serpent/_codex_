@copilot Continue Phase 8.7 Universal Intelligence implementation with the following PR slices:

## PR1: Universal Task Interface (UTI) Enhancement
1. Add environment adapters for common task types (gridworld, bandit, classification)
2. Implement task complexity estimation
3. Add schema validation with JSON Schema
4. Create 10+ additional tests for edge cases

## PR2: Meta-Policy Router (MPR) Enhancement
1. Implement full MAML algorithm integration
2. Add Reptile algorithm support
3. Implement dynamic hyperparameter tuning
4. Add strategy performance tracking
5. Create benchmark suite for algorithm comparison

## PR3: Abstraction Engine Enhancement
1. Implement hierarchical concept extraction
2. Add relation type detection (causal, temporal, spatial)
3. Implement analogy quality scoring
4. Create golden snapshot tests for concept graphs

## PR4: Grounding Layer Enhancement
1. Add GitHub API adapter (mocked for tests)
2. Implement action validation pipeline
3. Add execution trace replay
4. Create feasibility score thresholds

## PR5: Universal Pattern Store Enhancement
1. Implement similarity-based retrieval with embeddings
2. Add pattern versioning and deprecation
3. Implement cross-domain pattern matching
4. Add storage efficiency metrics

## PR6: Safety & Negative Transfer
1. Implement domain isolation mechanism
2. Add rollback trigger with baseline restore
3. Implement forgetting detection
4. Create safety constraint enforcement tests

## PR7: EXP-10 Validation
1. Create EXP-10 benchmark harness
2. Implement k₁ ≤ 0.28 validation
3. Add zero-shot and few-shot transfer tests
4. Generate metrics artifacts (JSONL)

## Validation Commands
```bash
python3 -m py_compile .github/agents/core/universal_intelligence.py
bandit -r .github/agents/core/ -ll
pytest .github/agents/core/tests/test_universal_intelligence.py -v
```

## Success Criteria
- [ ] All 7 PR slices implemented
- [ ] 50+ tests passing for Phase 8.7
- [ ] k₁ validation framework complete
- [ ] Metrics artifacts generated
- [ ] No medium/high security alerts

## References
- PHASE_8_7_IMPLEMENTATION_PLAN.md
- QUANTUM_VARIABLE_INTELLIGENCE.md
- COGNITIVE_BRAIN_STATUS_V5.md
