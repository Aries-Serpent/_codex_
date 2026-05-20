# PR #4511 — What's Next

## 🔄 Code-Quality Fix Batch: Test Helper Scoping + Workflow Merge Improvements

**Updated: 2026-05-20T00:45Z — S2 review remediations applied**

| Objective | Status |
|-----------|--------|
| Apply 3 AI findings to `tests/services/audio/test_transcription_workflow.py` | ✅ Complete |
| Apply 4 AI findings to `tools/workflow_merge.py` | ✅ Complete |
| Address code-review: list comprehension in `compile_replacements` | ✅ Complete |
| Fix `compile_replacements` conditional word-boundary look-arounds | ✅ S2 — resolves dot-token regression |
| Fix `count_references` — pass `allow_failure=True` to `rg` (exits 1 on no match) | ✅ S2 — resolves `CalledProcessError` on empty result |
| Audit `allow_failure` call sites | ✅ Complete — 0 external callers; `rg` call now explicitly opts in |
| Add unit tests: `compile_replacements`, `replace_in_file`, `update_references` | ✅ 16 tests — all passing |
| Fix test docstring: remove stale bullet; add actual `update_references` test | ✅ S2 |
| Validate with ruff + pytest | ✅ Passing; 3 line-length violations also fixed |
| Create verification report | ✅ `docs/roadmap/PR4511_verification_report.md` |
| Remediate 6 inline code-review comments | ✅ S2 complete |
| Deduplicate living docs (whats_next, session_diagram) | ✅ S2 |
| Fix follow-up prompt (stale PR #4510 refs, metadata) | ✅ S2 |
| Update CHANGELOG + AGENT_ACCOUNTABILITY_REPORT | ✅ S2 |
| Run `sync_tracked_files --fix` (Pattern 22 drift) | ✅ S2 |

### Changes Applied — S1 (initial)

#### `tests/services/audio/test_transcription_workflow.py`
1. **kwargs naming**: `**_kwargs` → `**kwargs` in `stub_process_file_method`.
2. **`_FakePyannoteSegment` scope**: Moved into the single consuming test function.
3. **`_FakeSegment` / `_FakeWhisperModel` scope**: Promoted to module scope for reuse.

#### `tools/workflow_merge.py`
4. **Error logging agent name**: `ChatGPT-5` → `ChatGPT @codex`.
5. **`allow_failure` default**: `True` → `False` (fail-fast).
6. **Compile regex once**: `compile_replacements()` helper; `replace_in_file()` accepts compiled list; `update_references()` compiles once.
7. **Grammar fix**: `"ALL GitHub Action."` → `"ALL GitHub Actions workflows."`.

#### `tests/tools/test_workflow_merge_replacements.py` (new)
- 14 tests covering `compile_replacements` and `replace_in_file`.

### Changes Applied — S2 (review remediations, 2026-05-20T00:45Z)

#### `tools/workflow_merge.py`
- `compile_replacements`: conditional look-arounds — `(?<!\w)` / `(?!\w)` applied only when
  key starts/ends with a word character; dot-terminated tokens (e.g. `workflow.`) now match correctly.
- `count_references`: `_run(["rg", ...], allow_failure=True)` — `rg` exits 1 on no matches; no
  longer raises `CalledProcessError`.
- Three line-length violations fixed (lines 58, 78, 381).

#### `tests/tools/test_workflow_merge_replacements.py`
- Module docstring updated to accurately describe all covered functions.
- `test_pattern_matches_whole_word_only` updated (removed incorrect `foo.bar` assertion).
- Added `test_dot_terminated_key_matches_followed_by_word_char` for attribute-access token fix.
- Added `TestUpdateReferences` (2 tests): verifies changed/scanned counts using monkeypatched REPO.

#### `.github/copilot-prompts/active/PR-4511-followup.md`
- Header metadata updated (Date → 2026-05-20, Commit → latest, Files Modified → actual list).
- All stale PR #4510 references replaced with PR #4511.

### Workflow Status (as of 2026-05-20T00:45Z)
- CI fan-out running after maintainer approval.
- All required checks anticipated green after S2 push.

### Next Immediate Actions
1. Wait for CI fan-out to complete.
2. Merge PR #4511 once all required checks are green.
