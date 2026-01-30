# Path to 100% Coverage Plan - semgrep URL regex validation

**Scope:** Replace URL substring checks in semgrep suppression tests with regex-based detection and verify coverage for related security checks.

## Phase 1: Semgrep suppression test hardening

### Pre-commit 1-2: Update URL detection

**Goal:** Replace substring checks with regex-based URL literal detection to satisfy security guidance and prevent bypasses.

**Tasks:**
- [ ] Replace `"http" in line` checks with regex `\bhttps?://` in `tests/test_semgrep_suppressions.py`.
- [ ] Add reusable compiled regex for URL literal detection.
- [ ] Confirm no remaining substring checks in semgrep suppression tests.

**Success Criteria:**
- [ ] Semgrep suppression tests use regex-based URL detection exclusively.
- [ ] No `url-substring-check` findings for the updated test module.

**Files to Modify:**
- `tests/test_semgrep_suppressions.py`

### Review, Verify, Commit
- [ ] Run targeted pytest for semgrep suppression tests.
- [ ] Run RAG end-to-end test module (integration coverage spot-check).
- [ ] Update audit logs and results.

## Phase 2: Coverage confirmation

### Pre-commit 3-4: Validation & documentation

**Goal:** Document validation output and ensure coverage expectations remain satisfied.

**Tasks:**
- [ ] Record validation results in `.codex/results.md`.
- [ ] Append entry in `.codex/change_log.md` with changes and validation.
- [ ] Append action log entries for all updated artifacts.

**Success Criteria:**
- [ ] Tests run and results captured in audit logs.
- [ ] Coverage plan reflects completion status and next steps.

---

## Fix Strategy Notes
- Use regex detection for URL literals instead of substring checks to align with semgrep guidance.
- Keep suppression discovery logic unchanged, only update URL detection utilities and assertions.
- Maintain existing file-scoped suppressions to avoid broadening suppression scope.
- Leverage `mappings/shared_mappings.json` for any related refactor tooling updates to stay aligned with tokenization mapping conventions.
