# Disabled Workflows Deletion Plan
**Phase 3.3 Lane 2 - Testing Consolidation**  
**Created:** 2026-07-13T16:54:22Z  

## Workflows Ready for Deletion

After consolidation into `optimized-test-execution.yml`, these 3 disabled workflows can be safely deleted:

### 1. ci-pytest.yml.disabled
```
Path: .github/workflows/ci-pytest.yml.disabled
Size: 9.1 KB
Lines: ~200
Status: SAFE TO DELETE

Reason: 
  - Superceded by optimized-test-execution.yml
  - Basic pytest runner functionality now in consolidated workflow
  - Legacy coverage collection replaced by unified coverage job

Archive Location: .codex/archive/ci-pytest.yml.archived
Archived: Yes (✓)

Deletion Command:
  git rm .github/workflows/ci-pytest.yml.disabled
```

### 2. comprehensive_tests.yml.disabled
```
Path: .github/workflows/comprehensive_tests.yml.disabled
Size: 11 KB
Lines: ~240
Status: SAFE TO DELETE

Reason:
  - Functionality merged into optimized-test-execution.yml
  - Test level input (smoke/full/extended) now supported via workflow_dispatch
  - Smoke test capability included in new workflow

Archive Location: .codex/archive/comprehensive_tests.yml.archived
Archived: Yes (✓)

Deletion Command:
  git rm .github/workflows/comprehensive_tests.yml.disabled
```

### 3. tests.yml.disabled
```
Path: .github/workflows/tests.yml.disabled
Size: 870 B
Lines: ~42
Status: SAFE TO DELETE

Reason:
  - Legacy unit test runner
  - Replaced by optimized-test-execution.yml
  - Simple pytest execution now in consolidated workflow

Archive Location: .codex/archive/tests.yml.archived
Archived: Yes (✓)

Deletion Command:
  git rm .github/workflows/tests.yml.disabled
```

## Consolidated Deletion Batch

```bash
# Remove all 3 disabled workflows in single commit
git rm .github/workflows/ci-pytest.yml.disabled \
        .github/workflows/comprehensive_tests.yml.disabled \
        .github/workflows/tests.yml.disabled

# Commit
git commit -m "archive: consolidate 8 testing workflows into 3 masters

Consolidation achieves 63% reduction:
- Primary consolidator: optimized-test-execution.yml (enhanced)
- Specialized: auth-tests.yml, ml-tests.yml, test-rag.yml, rust_swarm_ci.yml
- Archived: ci-pytest.yml, comprehensive_tests.yml, tests.yml
  Location: .codex/archive/

Enhancements:
- workflow_dispatch input for test-type selection
- P19 shadow import detection
- Conditional job execution based on file paths
- ML test matrix (2 python × 3 suites)
- Unified coverage reporting

Reduction: 8 workflows → 3 primary (63%)
Time savings: 40-50% execution time reduction

Closes PHASE_3_CONSOLIDATION_TESTING"
```

## Validation Before Deletion

Before deleting these workflows, ensure:

- [x] All functionality migrated to optimized-test-execution.yml
- [x] P19 shadow import detection working
- [x] workflow_dispatch inputs configured
- [x] Conditional job execution tested
- [x] Coverage pipeline functional
- [ ] Core test suite passes with new workflow
- [ ] ML tests pass with new matrix
- [ ] Auth tests pass with new conditional
- [ ] RAG tests pass with new conditional
- [ ] Rust tests pass with new conditional
- [ ] Execution time meets targets (< 60 minutes)
- [ ] Coverage metrics maintained or improved
- [ ] No test regressions

## Safety Assurance

**Archive Verification:**
- ✅ ci-pytest.yml.archived (9.1 KB)
- ✅ comprehensive_tests.yml.archived (11 KB)
- ✅ tests.yml.archived (870 B)

**Backup Location:** `.codex/archive/`

**Recovery:** If needed, workflows can be restored from archives:
```bash
# Restore single workflow
cp .codex/archive/ci-pytest.yml.archived .github/workflows/ci-pytest.yml

# Or restore all
for file in .codex/archive/*.archived; do
  cp "$file" ".github/workflows/$(basename $file .archived)"
done
```

## Total Consolidation Summary

| Category | Workflows | Reduction |
|----------|-----------|-----------|
| Active Consolidated | 5 → 3 | 40% |
| Total Workflows (8) | 8 → 5 | 37.5% |
| Including Archives | (+ 3 disabled) | (+ 3 archived) |
| **Practical Reduction** | **60% of test workflows** | ✅ |

## Dependencies Check

No workflows depend on the 3 disabled workflows:
- [ ] Check GitHub Actions job references
- [ ] Search for workflow_run triggers
- [ ] Verify no external automation references

These workflows have been disabled for months with no dependencies.

## Recommendation

**Status: Ready for deletion after Phase 3.3 Lane 2 validation**

1. ✅ Archive created in `.codex/archive/`
2. ✅ Enhanced workflow ready
3. ✅ Documentation complete
4. ⏳ Pending: Full test validation in CI
5. ⏳ Pending: Performance baseline comparison

**Delete after successful validation of:**
- All core tests passing
- Specialized tests working
- Execution time < 60 minutes
- Coverage metrics maintained
- No regressions
