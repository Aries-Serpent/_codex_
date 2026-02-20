# Copilot → Codex Hand-off Comment Template

---

## 📤 HAND-OFF: Copilot → Codex

@codex {phase_name} Complete - Review Requested

### 📊 Phase Summary

**Phase**: {phase_name}
**Plan**: {plan_file}
**Status**: ✅ {status}
**Completed**: {completion_timestamp}

---

### 📦 Deliverables

{deliverables_list}

**Example**:
- Coverage baseline report: [tokenization_coverage_baseline.md]({link_1})
- Gap analysis: [coverage_tokenization.json]({link_2})
- Test case mapping: [test_case_mapping.md]({link_3})

---

### 📈 Metrics

{metrics_table}

**Example**:
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Coverage | 45.2% | 70% | 🟡 Below Target |
| Files Analyzed | 7/7 | 7 | ✅ Complete |
| Tests Mapped | 12 | 10+ | ✅ Exceeds Minimum |
| Iterations | 4/4 | 4 | ✅ Complete |

---

### 🔍 Review Request

**Primary Focus**:
{primary_review_focus}

**Validation Checklist**:
- [ ] {validation_item_1}
- [ ] {validation_item_2}
- [ ] {validation_item_3}

**Questions for Review**:
1. {question_1}
2. {question_2}

---

### ➡️ Next Action

{next_action_description}

**Expected from Codex**:
1. {expectation_1}
2. {expectation_2}
3. {expectation_3}

---

### 📚 References

**Plan Document**: [{plan_name}]({plan_link})
**Artifacts Directory**: [{artifact_dir}]({artifact_dir_link})
**Execution Logs**: [{log_file}]({log_link})
**Cognitive Brain**: [{brain_doc}]({brain_link})

---

### 🏷️ Tags

`#{phase_tag}` `#handoff` `#review-requested` `#copilot-to-codex`

---

**Hand-off ID**: {handoff_id}
**Triggered**: {timestamp}
**Next Agent**: @codex

---

## 📝 Template Variables

Replace the following placeholders when generating a comment:

| Variable | Description | Example |
|----------|-------------|---------|
| `{phase_name}` | Pre-commit phase identifier | "Pre-commit 3-4: Tokenization Coverage Analysis" |
| `{plan_file}` | Path to plan file | "`.codex/plans/pr_3145/01_tokenization_coverage_analysis.md`" |
| `{status}` | Completion status | "Complete" / "Complete with notes" |
| `{completion_timestamp}` | ISO 8601 timestamp | "2026-02-04T14:30:00Z" |
| `{deliverables_list}` | Markdown list of deliverables | See example above |
| `{link_N}` | URL to deliverable | "https://github.com/..." or relative path |
| `{metrics_table}` | Markdown table of metrics | See example above |
| `{primary_review_focus}` | Main area for Codex to review | "Coverage gap analysis and test prioritization" |
| `{validation_item_N}` | Specific validation checklist items | "Verify all 7 modules analyzed" |
| `{question_N}` | Questions for Codex | "Is the test prioritization appropriate?" |
| `{next_action_description}` | What should happen next | "Review coverage gaps and approve test implementation strategy" |
| `{expectation_N}` | Expected deliverables from Codex | "Validation report with approval/changes" |
| `{plan_name}` | Display name of plan | "Tokenization Coverage Analysis" |
| `{plan_link}` | Link to plan file | Relative or full URL |
| `{artifact_dir}` | Artifacts directory name | "`.codex/plans/pr_3145/`" |
| `{artifact_dir_link}` | Link to artifacts directory | URL to directory view |
| `{log_file}` | Log file name | "`coverage_analysis.log`" |
| `{log_link}` | Link to log file | Relative or full URL |
| `{brain_doc}` | Cognitive brain document name | "`pr_3145_planset_registration.md`" |
| `{brain_link}` | Link to cognitive brain doc | Relative or full URL |
| `{phase_tag}` | Hashtag for phase | "precommit-3-4" |
| `{handoff_id}` | Unique hand-off identifier | "HO-001" / "HO-002" |
| `{timestamp}` | Current ISO 8601 timestamp | "2026-02-04T14:30:00Z" |

---

## 💡 Usage Example

```markdown
@codex Pre-commit 3-4 Complete - Review Requested

### 📊 Phase Summary

**Phase**: Pre-commit 3-4: Tokenization Coverage Analysis
**Plan**: `.codex/plans/pr_3145/01_tokenization_coverage_analysis.md`
**Status**: ✅ Complete
**Completed**: 2026-02-04T14:30:00Z

---

### 📦 Deliverables


---

### 📈 Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Overall Coverage | 45.2% | 70% | 🟡 Below Target |
| Files Analyzed | 7/7 | 7 | ✅ Complete |
| Tests Mapped | 12 | 10+ | ✅ Exceeds Minimum |
| Gap to Target | 24.8% | 0% | 🟡 Action Needed |

---

### 🔍 Review Request

**Primary Focus**:
Review coverage gap analysis and validate test prioritization strategy. Ensure the 12 mapped tests will achieve 70%+ coverage target.

**Validation Checklist**:
- [ ] All 7 tokenization modules analyzed
- [ ] Coverage gaps correctly identified
- [ ] Test case mapping addresses high-impact gaps first
- [ ] Test priorities align with coverage targets

**Questions for Review**:
1. Is the prioritization of loader.py and api.py appropriate given their low coverage?
2. Should we add additional integration tests beyond the 12 mapped?

---

### ➡️ Next Action

Review coverage gaps and approve test implementation strategy for Pre-commit 5-8.

**Expected from Codex**:
1. Validation report confirming coverage analysis accuracy
2. Approval or requested changes for test strategy
3. Hand-off to @copilot for Plan 2 execution (if approved)

---

### 📚 References


---

### 🏷️ Tags

`#precommit-3-4` `#handoff` `#review-requested` `#copilot-to-codex`

---

**Hand-off ID**: HO-002
**Triggered**: 2026-02-04T14:30:00Z
**Next Agent**: @codex
```

---

## 🔧 Generation Script

Use `scripts/handoff/generate_handoff_comment.py` to automatically populate this template:

```bash
python scripts/handoff/generate_handoff_comment.py \
  --template copilot_to_codex \
  --phase "Pre-commit 3-4" \
  --plan ".codex/plans/pr_3145/01_tokenization_coverage_analysis.md" \
  --deliverables "baseline.md,coverage.json,mapping.md" \
  --metrics "coverage=45.2,files=7,tests=12" \
  --output comment.md
```

---

**Template Version**: 1.0.0
**Last Updated**: 2026-02-04T14:15:00Z
**Template Type**: Copilot → Codex Hand-off
