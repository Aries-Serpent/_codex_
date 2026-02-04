# Template Variables Reference Guide

---

## 📚 Complete Variable Dictionary

This document provides a comprehensive reference for all variables used in Agent Hand-off Protocol templates.

---

## 🔤 Common Variables (All Templates)

| Variable | Type | Description | Example | Required |
|----------|------|-------------|---------|----------|
| `{phase_name}` | String | Full phase identifier | "Pre-commit 3-4: Tokenization Coverage Analysis" | Yes |
| `{phase_tag}` | String | Hashtag-safe phase identifier | "precommit-3-4" | Yes |
| `{timestamp}` | ISO 8601 | Current timestamp | "2026-02-04T14:30:00Z" | Yes |
| `{handoff_id}` | String | Unique hand-off identifier | "HO-001", "HO-002" | Yes |
| `{plan_file}` | Path | Relative path to plan file | "`.codex/plans/pr_3145/01_*.md`" | Yes |
| `{plan_name}` | String | Display name of plan | "Tokenization Coverage Analysis" | Yes |
| `{plan_link}` | URL | Link to plan file | Relative or full URL | Yes |
| `{status}` | String | Current status | "Complete", "In Progress", "Pending" | Yes |

---

## 📤 Copilot → Codex Variables

### Phase Information

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{completion_timestamp}` | ISO 8601 | When phase completed | "2026-02-04T14:30:00Z" |
| `{deliverables_list}` | Markdown | List of deliverables with links | "- [file1.md](link)\n- [file2.json](link)" |
| `{link_N}` | URL | Link to specific deliverable | "https://github.com/..." or ".codex/..." |

### Metrics

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{metrics_table}` | Markdown | Table of metrics | See template for structure |
| `{metric_name}` | String | Name of metric | "Coverage", "Files Analyzed" |
| `{metric_value}` | Any | Value of metric | "45.2%", "7/7", "12" |
| `{metric_target}` | Any | Target value | "70%", "7", "10+" |
| `{metric_status}` | Emoji + Text | Status indicator | "✅ Complete", "🟡 Below Target" |

### Review Request

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{primary_review_focus}` | Text | Main area for review | "Coverage gap analysis and test prioritization" |
| `{validation_item_N}` | String | Checklist item | "Verify all 7 modules analyzed" |
| `{question_N}` | String | Question for reviewer | "Is the test prioritization appropriate?" |

### Next Actions

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{next_action_description}` | Text | What should happen next | "Review coverage gaps and approve strategy" |
| `{expectation_N}` | String | Expected deliverable | "Validation report with approval/changes" |

### References

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{artifact_dir}` | Path | Artifacts directory | "`.codex/plans/pr_3145/`" |
| `{artifact_dir_link}` | URL | Link to directory | GitHub directory URL |
| `{log_file}` | Filename | Log file name | "`coverage_analysis.log`" |
| `{log_link}` | URL | Link to log file | Relative or full URL |
| `{brain_doc}` | Filename | Cognitive brain doc name | "`pr_3145_planset_registration.md`" |
| `{brain_link}` | URL | Link to brain doc | Relative or full URL |

---

## 📥 Codex → Copilot Variables

### Review Results

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{review_type}` | String | Type of review | "Coverage Analysis Validation", "Test Quality Review" |
| `{review_timestamp}` | ISO 8601 | When review completed | "2026-02-04T15:00:00Z" |
| `{overall_status}` | String with Emoji | Overall assessment | "✅ Passed", "⚠️ Passed with Recommendations" |
| `{validation_summary}` | Text | Brief summary | 2-3 sentence overview |

### Findings

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{strengths_list}` | Markdown | List of strengths | "- Strength 1\n- Strength 2" |
| `{improvements_list}` | Markdown | List of improvements | "- Improvement 1\n- Improvement 2" |
| `{issues_list}` | Markdown | List of issues | "- Issue 1\n- Issue 2" or "None identified ✅" |
| `{recommendations_section}` | Markdown | Detailed recommendations | Structured recommendations with priorities |

### Decision

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{decision_status}` | String with Emoji | Approval decision | "✅ APPROVE", "❌ REQUEST CHANGES" |
| `{decision_tag}` | String | Hashtag for decision | "approved", "changes-requested" |
| `{decision_explanation}` | Text | Reasoning for decision | Explanation paragraph |
| `{condition_N}` | String | Approval condition | "Address edge case testing" |

### Next Phase

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{next_phase_name}` | String | Name of next phase | "Pre-commit 5-8: Comprehensive Test Implementation" |
| `{next_plan_file}` | Path | Path to next plan | "`.codex/plans/pr_3145/02_*.md`" |
| `{instructions_for_copilot}` | Markdown | Detailed instructions | Multi-paragraph instructions |

### References

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{review_report_name}` | String | Display name of report | "Pre-commit 3-4 Review Report" |
| `{review_report_link}` | URL | Link to review report | Relative or full URL |
| `{checklist_name}` | String | Validation checklist name | "Coverage Analysis Validation Checklist" |
| `{checklist_link}` | URL | Link to checklist | Relative or full URL |
| `{next_plan_name}` | String | Display name of next plan | "Comprehensive Test Implementation" |
| `{next_plan_link}` | URL | Link to next plan | Relative or full URL |

### Timing

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{response_time}` | Duration | Time to respond | "30 minutes", "2 hours" |

---

## 📊 Tracking Template Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{link_text}` | String | Display text for link | "Comment #123" |
| `{comment_url}` | URL | Full URL to PR comment | "https://github.com/.../pull/3145#issuecomment-123" |
| `{response_time}` | Duration | Time to respond | "30 min", "2 hours", "-" (for initial) |
| `{total_handoffs}` | Integer | Total count | "15" |
| `{completed_count}` | Integer | Completed count | "2" |
| `{in_progress_count}` | Integer | In progress count | "1" |
| `{pending_count}` | Integer | Pending count | "12" |
| `{failed_count}` | Integer | Failed count | "0" |
| `{success_rate}` | Float | Success percentage | "100.0" |
| `{avg_response_time}` | Duration | Average time | "30 minutes" |
| `{pc3_4_complete}` | Integer | Phase-specific count | "2" |
| `{pc3_4_rate}` | Float | Phase-specific rate | "100.0" |

---

## 🎨 Variable Formatting Guidelines

### Timestamps
- **Format**: ISO 8601 with timezone
- **Example**: `2026-02-04T14:30:00Z`
- **Never use**: Relative times like "2 hours ago"

### Paths
- **Format**: Relative from repository root
- **Example**: `.codex/plans/pr_3145/file.md`
- **Backticks**: Always wrap in backticks for display

### URLs
- **Format**: Full HTTPS URL or relative path
- **Example**: `https://github.com/Aries-Serpent/_codex_/pull/3145#issuecomment-123`
- **Markdown**: Use `[text](url)` format

### Status Indicators
- **Format**: Emoji + Text
- **Examples**:
  - `✅ Complete`
  - `🟡 Below Target`
  - `❌ Failed`
  - `🔄 In Progress`
  - `⏳ Pending`

### Lists
- **Format**: Markdown unordered list
- **Example**:
  ```markdown
  - Item 1
  - Item 2
  - Item 3
  ```

### Tables
- **Format**: Markdown table with headers
- **Example**:
  ```markdown
  | Header 1 | Header 2 |
  |----------|----------|
  | Value 1  | Value 2  |
  ```

---

## 🔧 Variable Substitution Examples

### Simple Substitution

**Template**:
```markdown
**Phase**: {phase_name}
**Status**: {status}
```

**After Substitution**:
```markdown
**Phase**: Pre-commit 3-4: Tokenization Coverage Analysis
**Status**: Complete
```

### List Substitution

**Template**:
```markdown
### Deliverables
{deliverables_list}
```

**After Substitution**:
```markdown
### Deliverables
- Coverage baseline: [tokenization_coverage_baseline.md](.codex/plans/pr_3145/tokenization_coverage_baseline.md)
- Gap analysis: [coverage_tokenization.json](coverage_tokenization.json)
- Test mapping: [test_case_mapping.md](.codex/plans/pr_3145/test_case_mapping.md)
```

### Table Substitution

**Template**:
```markdown
### Metrics
{metrics_table}
```

**After Substitution**:
```markdown
### Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Coverage | 45.2% | 70% | 🟡 Below Target |
| Files | 7/7 | 7 | ✅ Complete |
```

---

## 🛠️ Script Integration

### Generate Comment with Variables

```bash
python scripts/handoff/generate_handoff_comment.py \
  --template copilot_to_codex \
  --variable "phase_name=Pre-commit 3-4" \
  --variable "status=Complete" \
  --variable "completion_timestamp=2026-02-04T14:30:00Z" \
  --deliverables "baseline.md,coverage.json,mapping.md" \
  --metrics "coverage=45.2,files=7,tests=12" \
  --output comment.md
```

### Validate Variable Completeness

```bash
python scripts/handoff/generate_handoff_comment.py \
  --template copilot_to_codex \
  --validate-only \
  --show-missing-variables
```

---

## ✅ Variable Validation Rules

### Required Variables
- Must be provided for comment generation
- Script will fail if missing
- Marked "Yes" in variable tables above

### Optional Variables
- Can be omitted
- Default values may be used
- Marked "No" in variable tables above

### Type Checking
- **String**: Any text
- **Integer**: Whole numbers only
- **Float**: Decimal numbers
- **ISO 8601**: Timestamp format validation
- **URL**: Valid URL format
- **Path**: Valid file path format
- **Markdown**: Valid Markdown syntax
- **Duration**: Valid duration format (e.g., "30 min", "2 hours")

---

## 📝 Best Practices

1. **Always use ISO 8601** for timestamps
2. **Always wrap paths** in backticks
3. **Use markdown links** for all URLs
4. **Include emoji indicators** in status fields
5. **Be specific** in descriptions
6. **Validate before posting** comment
7. **Keep lists concise** (3-5 items ideal)
8. **Use tables** for structured data
9. **Reference actual files** not placeholders
10. **Update tracking** immediately after hand-off

---

**Guide Version**: 1.0.0
**Last Updated**: 2026-02-04T14:15:00Z
**Maintainer**: AI Agent Team
