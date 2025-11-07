# Pre-flight Checklist for Codex Operations

> **Purpose**: Address CODEX-005 (planning deficit). Reduces rework from 50% → 15%.  
> **Usage**: Copy, fill, commit before complex operations.  
> **Status**: Mandatory for patch applications; recommended for all operations.

## Pre-flight Checklist Template

**Copy this section and fill out for each operation:**

```text
## Operation: [DESCRIBE YOUR TASK IN ONE SENTENCE]

**Date (UTC)**: [YYYY-MM-DD HH:MM:SS]  
**Operator**: [YOUR NAME]  
**Branch**: [GIT BRANCH NAME]  
**PR Number**: [PR OR N/A]  

### Phase 1: Context Collection
- [ ] Read ALL source files that will be modified
- [ ] Identified file locations and line numbers
- [ ] Documented current state (size, key functions, interdependencies)
- [ ] Checked for existing tests, examples, templates
- [ ] Gathered git context: branch, commit hash, user

### Phase 2: Tool Inventory
- [ ] Listed all operations: Create, Read, Update, Delete, Validate
- [ ] Mapped each operation to tool: sed, cat, patch, python, grep, etc.
- [ ] Pre-validated tool availability: `command -v <tool>`
- [ ] Checked for tool conflicts (versions, dependencies)

### Phase 3: Strategy Definition
- [ ] Defined success criteria (what must be true when done)
- [ ] Outlined step-by-step execution plan (numbered steps)
- [ ] Identified rollback points (git commit hashes, file backups)
- [ ] Documented assumptions (paths, file names, values)

### Phase 4: Risk Assessment
**Identified Risks:**
| Risk | Probability | Mitigation |
|------|-------------|-----------|
| [Risk 1] | Low/Med/High | [Mitigation strategy] |
| [Risk 2] | Low/Med/High | [Mitigation strategy] |

### Phase 5: Execution Lock
- [ ] Committed checklist to session record
- [ ] Plan is locked: No exploratory commands mid-flight
- [ ] All commands verified against plan
- [ ] Documented any deviations with explanation

### Phase 6: Validation Plan
- [ ] Pre-execution validation: `[validation command]`
- [ ] Post-execution validation: `[validation command]`
- [ ] Rollback procedure: `[rollback steps]`
- [ ] Success confirmation: `[how to verify success]`

### Execution Summary

**Status**: [ ] Ready to Execute / [ ] Blocked / [ ] On Hold

**Next Action**: [What happens next]

**Estimated Duration**: [Time estimate]

**Owner Approval**: Signed: _____________ Date: _________
```
## Example: Applying a Patch

```text
## Operation: Apply security fix patch from PR #1234 to src/auth/handler.py

**Date (UTC)**: 2025-10-30 02:43:05  
**Operator**: mbaetiong  
**Branch**: 0D_base_  
**PR Number**: 1234  

### Phase 1: Context Collection
- [x] Read ALL source files: src/auth/handler.py, src/auth/utils.py, tests/test_auth.py
- [x] File locations: Line 45-67 (vulnerable function), Line 120+ (validation logic)
- [x] Current state: 450 lines, 3 test cases, imports from cryptography
- [x] Existing tests: 6 security test cases in tests/test_auth.py
- [x] Git context: Branch 0D_base_, commit c829fec7, user mbaetiong

### Phase 2: Tool Inventory
- [x] Operations: Validate patch → Apply patch → Run tests → Commit
- [x] Tools: git apply, bash script, pytest
- [x] Tool availability: git apply ✓, bash ✓, pytest ✓
- [x] No conflicts detected

### Phase 3: Strategy Definition
- [x] Success: All tests pass, security tests green, no linting errors
- [x] Steps: 1) Validate patch 2) Apply with --check 3) Run tests 4) Commit
- [x] Rollback: git reset --hard c829fec7
- [x] Assumptions: Patch from trusted source, no merge conflicts expected

### Phase 4: Risk Assessment
| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Merge conflict | Low | Pre-validated with git apply --check |
| Test failure | Low | 6 existing security tests cover scenario |
| Syntax error | Very Low | Patch validated before apply |

### Phase 5: Execution Lock
- [x] Checklist committed
- [x] Plan locked: ONLY following steps below
- [x] Commands verified against plan
- [x] No deviations expected

### Phase 6: Validation Plan
- [x] Pre-exec: bash scripts/validate_patch.sh PR-1234.patch
- [x] Post-exec: pytest tests/test_auth.py -v
- [x] Rollback: git reset --hard c829fec7; git clean -fd
- [x] Success: All 6 tests pass, no security warnings

### Execution Summary

**Status**: [x] Ready to Execute

**Next Action**: Apply patch, run tests, commit

**Estimated Duration**: 15 minutes

**Owner Approval**: Signed: mbaetiong Date: 2025-10-30
```
---

**Last Updated**: 2025-10-30  
**Status**: Reference template for CODEX-005 mitigation
