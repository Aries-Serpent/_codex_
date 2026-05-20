# PR #4511 — What's Next

## 🔄 Code-Quality Fix Batch: Test Helper Scoping + Workflow Merge Improvements (2026-05-20T00:01Z)

| Objective | Status |
|-----------|--------|
| Apply 3 AI findings to `tests/services/audio/test_transcription_workflow.py` | ✅ Complete |
| Apply 4 AI findings to `tools/workflow_merge.py` | ✅ Complete |
| Validate with ruff + pytest | ✅ Passing |
| Update living docs, CHANGELOG, accountability | ✅ Complete |
| Wrap-up + follow-up prompt | ✅ Active |

### Changes Applied

#### `tests/services/audio/test_transcription_workflow.py`
1. **Finding 1 — kwargs naming**: Renamed `**_kwargs` → `**kwargs` in `stub_process_file_method` for Python convention consistency.
2. **Finding 2 — `_FakePyannoteSegment` scope**: Moved from module level into the single test that uses it (`test_process_file_with_pyannote_backend_uses_pyannote_path`) to reduce module-level clutter.
3. **Finding 3 — `_FakeSegment` / `_FakeWhisperModel` scope**: Extracted from nested-inside-test to module scope so multiple tests can reuse them without duplication.

#### `tools/workflow_merge.py`
4. **Finding 1 — Error logging agent name**: Corrected `ChatGPT-5` → `ChatGPT @codex` in `log_error()` for consistency with the pattern used across the codebase.
5. **Finding 2 — `allow_failure` default**: Changed `allow_failure: bool = True` → `False` in `_run()` to enforce fail-fast behaviour by default.
6. **Finding 3 — Compile regex once**: Extracted `compile_replacements()` helper that pre-compiles all patterns; `replace_in_file()` now accepts `list[tuple[re.Pattern, str]]` instead of recompiling on every call; `update_references()` calls `compile_replacements()` once before the traversal loop.
7. **Finding 4 — Grammar fix**: Corrected `"ALL GitHub Action."` → `"ALL GitHub Actions workflows."` in the compliance `log_change` call.

### Validation
- `python -m ruff check tests/services/audio/test_transcription_workflow.py tools/workflow_merge.py` ✅
- `python -m pytest tests/services/audio/test_transcription_workflow.py -q` → 8 passed ✅
- `ast.parse("tools/workflow_merge.py")` ✅

### Next Immediate Actions
1. Merge PR #4511 once CI is green.
2. No follow-up work anticipated; all 7 findings fully resolved.
