# 🎯 PR Follow-Up Tasks - #4510

**PR**: #4510  
**Title**: [WIP] Update speaker name timeout documentation or configuration  
**Branch**: `copilot/update-speaker-name-timeout`  
**Author**: @Copilot  
**Date**: 2026-05-19  
**Commit**: `e798347`  
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work
- [`e798347`] fix prompt references and pyannote test helper scope
- [`6dc7742`] test: rename shared audio workflow helper
- [`3c3333f`] fix audio timeout follow-up and refresh living docs
- [`f0185d1`] fix audio transcription timeout config and workflow tests
- [`03b3326`] chore: start audio transcription follow-up fixes

### Files Modified
- `apps/dev/audio_transcriber_ui.py`
- `tests/services/audio/test_transcription_workflow.py`
- `docs/roadmap/review_codebase_next_changes_whats_next.md`
- `docs/roadmap/review_codebase_next_changes_session_diagram.mmd`
- `CHANGELOG.md`
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- `.github/copilot-prompts/active/PR-4510-followup.md`

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Monitor the latest approved workflow fan-out on the current PR head and capture any actionable failed jobs with logs.
- [ ] Re-check `PR Auto-Fix Check`, validation, and security workflows after the latest push.
- [ ] Keep `whats_next`, `session_diagram`, `CHANGELOG.md`, and `AGENT_ACCOUNTABILITY_REPORT.md` aligned with any new workflow findings.
- [ ] Preserve the final 5 minutes of the session for concise wrap-up and handoff.

### Additional Session Requirements
- [ ] Re-run focused validation if any additional code or test edits are made.
- [ ] Keep the PR follow-up prompt in sync with the actual branch head and PR state.

### Current workflow monitor snapshot
- Current reviewed head during this session: `f0185d1e` / later continuation commits on PR #4510.
- Approved workflow fan-out observed in progress: `Validation Pipeline`, `CodeQL Advanced`, `QA Walkthrough Agent`, `Semgrep SAST (SARIF Upload)`, `PR Auto-Fix Check`, `Audit & QA Suite (Unified)`, `Coverage with Timeout Guards`, `Resilient Dependency Submission`, `Secrets Baseline Enforcer`, `Workflow Documentation Link Validation`, and dependency submission workflows.
- Control workflows observed as `action_required`: `Agent Token Delegation`, `Workflow Execution Gate`, `PR Cost Check`, `Generate PR Follow-Up Prompt`.
- Startup-level fail-like runs observed with zero jobs via MCP: `Rust-Python Hybrid Swarm CI/CD`, `Progressive Validation Suite`, `Data Quality & Determinism Suite`.

---

## ✅ VALIDATION SNAPSHOT

```bash
python -m ruff check apps/dev/audio_transcriber_ui.py tests/services/audio/test_transcription_workflow.py
python -m pytest -q tests/services/audio/test_transcription_workflow.py
python -m pytest -q tests/services/audio
```

Manual verification completed in-session:
- `_gui_input_func()` was exercised with a stubbed root and `speaker_name_timeout_seconds=0.01`, confirming the timeout fallback returns `""`.

---

## 🔍 MANDATORY SELF-REVIEW PROTOCOL

**CRITICAL**: Perform 5 comprehensive self-review passes before concluding.

### Pass 1: Code Quality & Correctness
- [ ] All syntax errors resolved
- [ ] No linting warnings introduced
- [ ] Error handling remains correct
- [ ] Edge cases covered

### Pass 2: Testing & Validation
- [ ] Focused tests passing locally
- [ ] Relevant workflow checks reviewed
- [ ] No regressions introduced

### Pass 3: Documentation & Communication
- [ ] Living docs updated
- [ ] Accountability updated
- [ ] CHANGELOG updated
- [ ] Follow-up prompt updated

### Pass 4: Security & Safety
- [ ] No secrets introduced
- [ ] No unsafe new code paths introduced
- [ ] Validation feedback reviewed

### Pass 5: Integration & Dependencies
- [ ] PR remains internally consistent
- [ ] Workflow monitor status recorded accurately
- [ ] Backward compatibility maintained

**Failure Protocol**: If any checkpoint fails, fix it in the current session and re-run validation.

---

## 🤖 COPILOT AGENT INSTRUCTIONS

**When you see `@copilot continue` in PR #4510:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4510-followup.md`
2. Monitor the latest workflow state on the PR head
3. Fix any actionable review or CI findings found on that head
4. Update living docs and accountability artifacts with the new status
5. Preserve the final 5 minutes for wrap-up

---

**Generated**: 2026-05-19  
**Template Version**: 2.0.0  
**Last Updated**: 2026-05-19 22:40:00
