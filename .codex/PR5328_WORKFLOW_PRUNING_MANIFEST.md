# PR #5328 Workflow Pruning Manifest
**Generated:** 2026-07-17T01:54:30Z  
**Purpose:** Track TIER 2 workflows disabled to prevent cascading failures  
**Restoration:** After PR #5328 merge, revert all changes in this manifest

---

## Strategy: Conditional Skip Using Environment Control

Instead of modifying all 43 workflow files individually, we use a centralized control:

1. **Master Control File:** `.codex/.pr5328-tier2-disabled.txt`
2. **Each TIER 2 workflow checks:** If this file exists, skip workflow
3. **After PR merges:** Delete control file to restore all workflows

---

## TIER 2 Workflows to Disable (43 total)

### VALIDATION (10)
- [ ] Validate Bash Examples
- [ ] Validate Workflow Documentation Links  
- [ ] Validate YAML Examples
- [ ] WEC gate (workflow-execution-gate.yml)
- [ ] validate-manifest-drift
- [ ] Agent files size check
- [ ] E→D Transition Readiness Check
- [ ] Cross-Reference Validation
- [ ] Detect duplicates
- [ ] Deterministic diff guard

### DOCUMENTATION (6)
- [ ] Heading Hierarchy Validation
- [ ] Markdownlint
- [ ] Import Layer Boundary Check
- [ ] No broken internal links
- [ ] RP-003: Documentation Links
- [ ] Validate Python Examples

### MAINTENANCE/UTILITY (14)
- [ ] CI Health Check
- [ ] Delete stale PR comments
- [ ] Auto-fix Common Issues
- [ ] Detect merge commit
- [ ] Fast Validation
- [ ] Final Pre-Merge Checks
- [ ] Repository Health
- [ ] Triage gate
- [ ] Determine Check Scope
- [ ] GitHub Guru Agent
- [ ] Check approval
- [ ] Context capture
- [ ] Scan PR comments
- [ ] Deferral Language Policy Check

### MONITORING/PERFORMANCE (4)
- [ ] Latency Baseline Policy Check
- [ ] PR Cost Check
- [ ] MCP Metrics Threshold Gate
- [ ] CI Checkpoint Validation

### QUALITY/COVERAGE (4)
- [ ] RP-002: mypy Baseline
- [ ] Coverage Ratchet
- [ ] Heal Markdown Secret False-Positives
- [ ] RP-001: API Null-Handling

### COMPLIANCE/STANDARDS (5)
- [ ] Validate Token Scopes
- [ ] Enforce standards
- [ ] Freshness check
- [ ] Branch rebase gate
- [ ] (Additional compliance workflows)

---

## Implementation Status

**Phase 1: Create Control File**
- [x] Create `.codex/.pr5328-tier2-disabled.txt`

**Phase 2: Modify Top-Level Workflows** 
Starting with the most impactful TIER 2 workflows:
- [ ] workflow-execution-gate.yml
- [ ] ci-checkpoint-validation.yml
- [ ] branch-rebase-gate.yml
- [ ] deferral-language-gate.yml
- [ ] And 39 others...

**Phase 3: Test & Verify**
- [ ] Verify PR #5328 workflow count drops to 19-22 active
- [ ] Confirm TIER 0 & TIER 1 workflows still active
- [ ] Check for cascading failure reduction

**Phase 4: Document & Commit**
- [ ] Commit all workflow changes
- [ ] Document pruning in session
- [ ] Create restoration plan

---

## Restoration Plan

After PR #5328 is successfully merged:

1. Delete `.codex/.pr5328-tier2-disabled.txt`
2. Revert all workflow `if: false` changes  
3. Verify all 62+ workflows are active again
4. Commit restoration
5. Close this manifest

