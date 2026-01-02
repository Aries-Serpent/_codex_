# Phase 7 Code Review & Security Fixes

## Code Review Comments (30 issues)

### Unused Imports (17)
- [ ] src/cognitive_brain/quantum/ab_testing.py:12 - datetime
- [ ] src/cognitive_brain/quantum/adaptive_scoring.py:19 - field
- [ ] src/cognitive_brain/quantum/adaptive_scoring.py:20 - Optional
- [ ] src/cognitive_brain/quantum/adaptive_scoring.py:21 - math
- [ ] src/cognitive_brain/quantum/base.py:8 - Optional, List
- [ ] src/cognitive_brain/quantum/coherence_monitor.py:8 - time
- [ ] src/cognitive_brain/quantum/coherence_monitor.py:15-18 - QuantumFeature, CoherenceDegradationError
- [ ] src/cognitive_brain/integrations/compliance_integration.py:16 - Optional, Dict, Any, Callable
- [ ] src/cognitive_brain/integrations/entangled_assessor.py:13 - Tuple
- [ ] src/cognitive_brain/integrations/entangled_assessor.py:16 - EntangledPair
- [ ] src/cognitive_brain/experiments/exp1_validation.py:22 - asdict
- [ ] src/cognitive_brain/experiments/exp1_validation.py:26 - ExperimentConfig
- [ ] src/cognitive_brain/experiments/exp2_validation.py:22 - SuperpositionEngine
- [ ] src/cognitive_brain/quantum/superposition.py:17 - QuantumFeature, QuantumState
- [ ] src/cognitive_brain/quantum/uncertainty.py:21 - hashlib
- [ ] tests/* (multiple test files) - various unused imports

### Unused Variables (5)
- [ ] src/cognitive_brain/experiments/exp1_validation.py:144 - framework
- [ ] tests/cognitive_brain/quantum/test_ab_testing.py:373 - variant
- [ ] tests/cognitive_brain/integrations/test_entangled_assessor.py:98 - pair_id_1
- [ ] tests/cognitive_brain/integrations/test_entangled_assessor.py:101 - first_id
- [ ] tests/cognitive_brain/quantum/test_uncertainty.py:169 - min_uncertainty

### Duplicate Imports (1)
- [ ] tests/cognitive_brain/quantum/test_uncertainty.py:354 - sqlite3 (already imported line 9)

## Security Scan Issues (35)

### Critical (1)
- [ ] Gitleaks License - Document requirement (not fixable in code)

### High Priority (3)
- [ ] src/cognitive_brain/experiments/exp1_validation.py:259 - Insecure temp file
- [ ] src/cognitive_brain/quantum/uncertainty.py:180 - Use math.hypot()
- [ ] GitHub Actions - Document pinning requirement

### Medium Priority (33)
- [ ] Replace `random` with `secrets` in all experiment files (33 instances)

## Execution Plan

1. Fix all unused imports
2. Fix all unused variables
3. Fix duplicate imports
4. Fix insecure temp file usage
5. Fix Pythagorean calculation
6. Add comments for random vs secrets usage (won't change as these are test data generators)
7. Run tests to validate
8. Commit with references to all review comments
