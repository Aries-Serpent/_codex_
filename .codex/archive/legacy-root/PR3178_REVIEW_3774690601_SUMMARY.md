# PR #3178 Review 3774690601 - Issues to Address

## Review from copilot-pull-request-reviewer[bot]
**Submitted:** 2026-02-09T18:21:31Z
**Commit:** 51f4cb5fdb26b2aed0f4376da795111d5f9477b5

## Issues to Fix

### 1. Unused Imports (CodeQL & Code Quality Alerts)
- **tests/cli/conftest.py:58** - Unused import 'torch'
  - Fix: Replace with `importlib.import_module("torch")`
- **tests/rag/test_device_placement.py:6** - Unused import 'Mock'
  - Fix: Remove the import
- **tests/retrieval/test_factory.py:5** - Unused import 'patch'
  - Fix: Remove 'patch' from import list
- **scripts/audit_file_handles.py:23** - Unused import 'Tuple'
  - Fix: Remove 'Tuple' from typing import

### 2. Empty Except Blocks
- **tests/test_msp_infer_api.py:189** - Empty except with no comment
  - Fix: Add explanatory comment about ignoring cleanup errors
- **scripts/lint/check_device_placement.py:113** - Empty except and BaseException handling
  - Fix: Replace bare except with specific exceptions (OSError, IOError, UnicodeDecodeError)
  - Add comment explaining behavior

### 3. Unused Variables
- **tests/tokenization/conftest.py** - Variable 'original_spm' not used (RESOLVED in review)
- **src/quantum/orchestrator.py** - Variable 'task_map' not used (RESOLVED in review)

### 4. Logic Issues
- **tests/rag/test_device_placement.py:146** - Non-callable called (SimpleModel)
  - Need to investigate if this is a test issue
- **src/codex/ast/graph.py** - Topological sort edge direction issue
  - DependencyGraph.add_node() adds edges as node→dependency but returns reversed order
  - May cause dependents to appear before dependencies

### 5. Platform Compatibility
- **tests/coverage_push/test_edge_cases.py** - Hard-coded forward-slash in path assertion
  - Fix: Use `rel_path.as_posix()` or compare path parts for Windows compatibility

### 6. Workflow Issues
- **.github/workflows/docker-build-tests.yml.template:36** - Empty target matrix entries
  - Fix: Filter matrix to exclude empty targets

### 7. Error Handling
- **scripts/lint/check_device_placement.py:118, 145** - check_file() swallows errors
  - Fix: Propagate errors to main() for proper exit code 2

### 8. Performance
- **scripts/lint/check_device_placement.py:115** - File read on every .to() call
  - Fix: Load file once or memoize line numbers

### 9. Breaking Changes
- **services/crawler/__init__.py:26** - Removed exported symbols
  - Need to check if this breaks external code
  - Consider re-exporting old names as deprecated aliases

## Priority Order
1. **High Priority** - Unused imports (auto-fixable)
2. **High Priority** - Empty except blocks (security)
3. **Medium Priority** - Unused variables (already resolved)
4. **Medium Priority** - Logic issues (topological sort, SimpleModel)
5. **Low Priority** - Platform compatibility
6. **Low Priority** - Performance optimization
