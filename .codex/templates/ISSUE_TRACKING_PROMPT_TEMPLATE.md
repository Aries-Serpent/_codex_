# Issue Tracking Protocol - Reusable Prompt Template

**Purpose**: Maintain comprehensive tracking of ALL issues found during PR work, ensuring AI Agency Policy compliance (leave codebase better than found).

**Last Updated**: 2026-02-16  
**Template Version**: 1.0.0

---

## 📋 Instructions for AI Agents

When starting work on a PR or continuing previous work, use this template to:
1. **Document ALL issues found** (in-scope and out-of-scope)
2. **Track fix progress** with clear status indicators
3. **Maintain session continuity** across multiple interactions
4. **Provide transparent reporting** to human stakeholders

---

## 🎯 Session Initialization Checklist

Before making ANY code changes:

```markdown
- [ ] Read previous tracking log if exists: `.codex/PR_{PR_NUMBER}_FAILURE_TRACKING_LOG.md`
- [ ] Read root cause analysis if exists: `.codex/PR_{PR_NUMBER}_ROOT_CAUSE_ANALYSIS.md`
- [ ] Check for related tracking files: `.codex/CI_FAILURE_TRACKING_LOG.md`
- [ ] Review last commit message for context
- [ ] Identify ALL current failing checks/issues
- [ ] Create/update tracking document BEFORE first commit
```

---

## 📝 Tracking Document Structure

### File Naming Convention
```
.codex/PR_{PR_NUMBER}_FAILURE_TRACKING_LOG.md
```

### Required Sections

#### 1. Header (Always Update)
```markdown
# PR #{PR_NUMBER}: Continuous Failure Tracking Log

**Last Updated**: {ISO_TIMESTAMP}  
**PR**: #{PR_NUMBER}  
**Branch**: {branch_name}  
**Current Status**: {status_emoji} {brief_status}

---
```

#### 2. Attempt History (Append Only)
```markdown
## 🔄 Attempt History

### Attempt N: {Brief Description} ({commit_hash})
- **Date**: {ISO_DATE}
- **Change**: {what_was_changed}
- **Result**: {✅ SUCCESS / ❌ FAILED / ⏳ PENDING}
- **Root Cause**: {why_it_failed_or_succeeded}
- **Learning**: {key_insight}
```

#### 3. Current Failing Checks (Always Update)
```markdown
## 🎯 Current Failing Checks (Run: {workflow_run_id})

1. **Check Name**
   - Status: {❌ FAILED / ⏳ PENDING / ✅ PASSING}
   - Error: {concise_error_message}
   - Fix: {planned_or_applied_fix}
```

#### 4. Root Cause Summary (Update When Understanding Changes)
```markdown
## 📊 Root Cause Summary

**CONFIRMED ROOT CAUSE**: {one_sentence_summary}

### Why This Happens
{step_by_step_explanation}

### The Solution
{clear_actionable_steps}
```

#### 5. Implementation Plan (Update Progress)
```markdown
## 🔧 Implementation Plan

### Phase 1: {Phase_Name} {✅ COMPLETE / 🔄 IN_PROGRESS / ⏳ PENDING}
- [x] Task 1.1: {description}
- [ ] Task 1.2: {description}
```

#### 6. Additional Issues Found (AI Agency Policy)
```markdown
## 📝 Additional Issues Found & Fixed (AI Agency Policy)

### Issue N: {Issue_Category} {✅ FIXED / 🔄 IN_PROGRESS / ⏳ DEFERRED}
**Found**: {what_was_discovered}  
**Files**: {list_of_affected_files}  
**Impact**: {why_this_matters}  
**Fix**: {what_was_done}
```

#### 7. Comprehensive Fix Summary (Always Update)
```markdown
## 🎯 Comprehensive Fix Summary

| Category | Issues Found | Fixed | Remaining |
|----------|--------------|-------|-----------|
| {Category_1} | {N} | {M} ✅ | {N-M} |
| **TOTAL** | **{total}** | **{fixed}** | **{remaining}** |

**Progress**: {percentage}% complete ({fixed}/{total} issues resolved)
```

#### 8. Active Changes Tracker
```markdown
## 🔄 Active Changes in This Session

Session {N} - {ISO_TIMESTAMP}:
1. **{file_path}**: {change_description}
2. **{file_path}**: {change_description}

Commit: {commit_hash} - "{commit_message}"
```

#### 9. References & Next Actions
```markdown
## 🔗 References

- Root Cause Analysis: `.codex/PR_{PR_NUMBER}_ROOT_CAUSE_ANALYSIS.md`
- Related Workflows: `.github/workflows/{workflow_name}.yml`
- Previous Attempts: commits {hash_1}, {hash_2}

## 🎯 Next Actions

1. {immediate_next_step}
2. {following_step}
3. {validation_step}
```

---

## 🤖 Automated Prompts for Each Session

### Session Start Prompt
```
@copilot I'm continuing work on PR #{PR_NUMBER}. Before proceeding:

1. Read `.codex/PR_{PR_NUMBER}_FAILURE_TRACKING_LOG.md` 
2. Show me:
   - Current progress percentage
   - What was attempted last session
   - What failed and why
   - What should be attempted next
3. List all current failing checks
4. Provide recommended next steps

Then wait for my confirmation before making changes.
```

### Session End Prompt
```
@copilot Update tracking documents with this session's progress:

1. Update `.codex/PR_{PR_NUMBER}_FAILURE_TRACKING_LOG.md`:
   - Add new attempt to history
   - Update fix summary table
   - Document active changes
   - Update next actions

2. Verify:
   - All issues documented
   - All files tracked
   - Progress percentage updated
   - Commit included in tracking

3. Provide session summary:
   - What was fixed
   - What remains
   - Recommended next steps
```

### Status Check Prompt
```
@copilot Generate current status report from `.codex/PR_{PR_NUMBER}_FAILURE_TRACKING_LOG.md`:

1. Progress dashboard (visual)
2. Issues breakdown by category
3. Recent changes timeline
4. Blocking issues vs nice-to-have
5. Estimated completion percentage
```

---

## 📊 Status Indicators Reference

### Issue Status
- ✅ **FIXED**: Implemented and verified
- 🔄 **IN_PROGRESS**: Currently being worked on
- ⏳ **PENDING**: Identified but not started
- 🔍 **INVESTIGATING**: Root cause analysis in progress
- ⚠️ **BLOCKED**: Waiting on external dependency
- 📌 **DEFERRED**: Intentionally postponed with reason

### Phase Status
- ✅ **COMPLETE**: All tasks done and verified
- 🔄 **IN_PROGRESS**: Some tasks complete, some ongoing
- ⏳ **PENDING**: Not started
- ⚠️ **BLOCKED**: Cannot proceed due to blocker

### Check Status
- ✅ **PASSING**: Check succeeds
- ❌ **FAILED**: Check fails
- ⏳ **PENDING**: Check not yet run
- ⏭️ **SKIPPED**: Check skipped (intentional)

---

## 🎨 Visual Progress Indicators

### Progress Bar (Copy-Paste Ready)
```
0%   [                    ] 0/20
25%  [█████               ] 5/20
50%  [██████████          ] 10/20
75%  [███████████████     ] 15/20
100% [████████████████████] 20/20
```

### Category Breakdown
```
┌─────────────────────────────────────┐
│ Issue Category Breakdown            │
├─────────────────────────────────────┤
│ 🟢 Workflows:    13/13 (100%) ✅    │
│ 🟢 Test Mocks:    2/2  (100%) ✅    │
│ 🟢 CI Scripts:    1/1  (100%) ✅    │
│ 🟡 Test Patterns: 0/4   (0%)  🔄    │
│ 🟡 Config:        0/1   (0%)  🔄    │
├─────────────────────────────────────┤
│ 📊 Total:        16/21 (76%)        │
└─────────────────────────────────────┘
```

---

## 🔄 Integration with AI Agency Policy

### Required Actions Per Policy

1. **Document ALL Issues**
   - In-scope issues
   - Out-of-scope issues discovered
   - Pre-existing issues found
   - New issues introduced

2. **Track Fix Status**
   - What was attempted
   - What worked
   - What failed
   - Why it failed

3. **Maintain Continuity**
   - Link to previous attempts
   - Reference related documents
   - Track pattern history
   - Document learnings

4. **Transparent Reporting**
   - Clear progress metrics
   - Honest status updates
   - Blockers identified
   - Help requests explicit

---

## 📖 Example Usage

### Example 1: Starting Fresh PR Work

```markdown
# PR #3248: Continuous Failure Tracking Log

**Last Updated**: 2026-02-16T12:00:00Z  
**PR**: #3248  
**Branch**: copilot/sub-pr-3248  
**Current Status**: 🔄 IN PROGRESS - Initial investigation

---

## 🔄 Attempt History

### Attempt 1: Initial Analysis
- **Date**: 2026-02-16
- **Change**: Reviewed failing checks, created tracking document
- **Result**: ⏳ PENDING - Investigation complete
- **Root Cause**: TBD - gathering evidence
- **Learning**: Need to check previous PR history for patterns

---

## 🎯 Current Failing Checks (Run: 22062286142)

1. **Pre-Flight CI Validation**
   - Status: ❌ FAILED
   - Error: "21 workflow(s) with missing explicit plugin flags"
   - Fix: ⏳ Planned - Review plugin configuration approach

2. **Resilient Validation Suite (integration)**
   - Status: ❌ FAILED
   - Error: "unrecognized arguments: --timeout=300 -n 2"
   - Fix: ⏳ Planned - Investigate xdist worker plugin loading

---

## 🔧 Implementation Plan

### Phase 1: Investigation ✅ COMPLETE
- [x] Review all failing checks
- [x] Read previous PR history
- [x] Check for root cause analysis docs
- [x] Create tracking document

### Phase 2: Root Cause Analysis 🔄 IN PROGRESS
- [x] Identify plugin loading pattern
- [ ] Test locally
- [ ] Document findings

### Phase 3: Implementation ⏳ PENDING
- [ ] Fix workflows
- [ ] Update scripts
- [ ] Test fixes

---

## 🎯 Next Actions

1. Read `.codex/PR_3248_ROOT_CAUSE_ANALYSIS.md` if exists
2. Test plugin loading locally
3. Create fix plan based on evidence
```

### Example 2: Continuing Work

```markdown
## 🔄 Attempt History

### Attempt 5: Comprehensive Fix Implementation
- **Date**: 2026-02-16T14:30:00Z
- **Change**: Fixed 13 workflows, updated pre-flight check, fixed test mocks
- **Result**: 🔄 IN PROGRESS - Partial success
- **Root Cause**: Workflows using wrong plugin loading approach
- **Learning**: Must update ALL related files, not just failing ones

---

## 🎯 Comprehensive Fix Summary

| Category | Issues Found | Fixed | Remaining |
|----------|--------------|-------|-----------|
| Workflow Plugin Config | 13 | 13 ✅ | 0 |
| Test Mocks | 2 | 2 ✅ | 0 |
| CI Scripts | 1 | 1 ✅ | 0 |
| Test Patterns | 4 | 0 | 4 🔄 |
| Config Overlap | 1 | 0 | 1 🔄 |
| **TOTAL** | **21** | **16** | **5** |

**Progress**: 76% complete (16/21 issues resolved)

---

## 🔄 Active Changes in This Session

Session 5 - 2026-02-16T14:30:00Z:
1. **.github/workflows/*.yml**: 13 workflows updated with plugin pinning
2. **scripts/ci/pre_flight_check.py**: Updated validation logic
3. **tests/*.py**: 2 test files fixed (DummyOptimizer)
4. **.codex/PR_3248_FAILURE_TRACKING_LOG.md**: Comprehensive tracking added

Commit: 29dcd616 - "fix(ci): comprehensive workflow plugin configuration"
```

---

## 🚀 Best Practices

### DO ✅
- Update tracking document BEFORE first commit in session
- Document ALL issues found (even out of scope)
- Use consistent status indicators
- Link to related documents
- Include commit hashes for traceability
- Update progress percentages after each change
- Document learnings from failed attempts
- Use clear, specific language

### DON'T ❌
- Skip documenting "obvious" issues
- Leave status ambiguous
- Forget to update timestamps
- Omit root cause when known
- Skip session summary
- Lose track of attempted solutions
- Assume next agent will figure it out

---

## 🔍 Troubleshooting

### "I lost track of what was done"
→ Read Active Changes section, check commit history

### "Same issue keeps failing"
→ Read Attempt History, look for patterns in what was tried

### "Not sure what to do next"
→ Check Next Actions section, review Implementation Plan

### "Can't find related documents"
→ Check References section for paths

### "Progress seems wrong"
→ Recount issues in Fix Summary table, update percentage

---

## 📞 Support & Escalation

If tracking document becomes:
- Too large (>1000 lines): Create archive, start fresh with summary
- Conflicting: Human review needed
- Unclear: Ask for clarification, don't guess

Escalate to human when:
- More than 5 failed attempts on same issue
- Blocking issues prevent all progress
- Root cause unknown after thorough investigation
- Resources/permissions needed

---

## 📚 Related Templates

- **Root Cause Analysis**: `.codex/templates/ROOT_CAUSE_ANALYSIS_TEMPLATE.md`
- **Session Summary**: `.codex/templates/SESSION_SUMMARY_TEMPLATE.md`
- **CI Failure Report**: `.codex/templates/CI_FAILURE_REPORT_TEMPLATE.md`

---

**Template Maintained By**: AI Agents & Human Maintainers  
**Feedback**: Create issue with label `tracking-template`  
**Version History**: See `.codex/templates/CHANGELOG.md`
