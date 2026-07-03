# SESSION 2 SUPPORT TRACK - WORKFLOW MONITORING SETUP

## Authority & Execution Context
- **Authority**: @mbaetiong D-tier autonomous (GO CONTINUE)
- **Branch**: copilot/multi-agent-campaign-plan
- **Timeline**: 60-90 minutes parallel with Phases 2-3
- **Session**: Session 2 Support Track

## Baseline Assessment

### Workflow Inventory
- **Total Workflows**: 213
- **Workflows with path references**: 174 (82%)
- **Total path references to track**: 832

### Reference Categories by Volume
```
Scripts:    578 references (69.5%) - PRIMARY UPDATE TARGET
Docs:       125 references (15.0%) - SECONDARY TARGET
Sources:     75 references (9.0%)  - MONITOR
Tests:       46 references (5.5%)  - MONITOR
Artifacts:    8 references (1.0%)  - VALIDATE
```

### High Priority Workflows (First Update Batch)
1. **iterative-self-healing-ci.yml** - 38 refs - Critical CI logic
2. **auth-tests.yml** - 23 refs - Auth test execution
3. **autonomy-phase-ci-matrix.yml** - 22 refs - Phase matrix tests
4. **copilot-setup-steps.yml** - 22 refs - Setup validation
5. **agent-auth-delegation.yml** - 21 refs - Agent auth tests

### YAML Validation Status
✅ All 213 workflows are valid YAML (baseline established)

## Monitoring Strategy

### Phase 2 Detection (File Renames)
When Phase 2 commits are detected:
1. Extract renamed paths from git diff
2. Cross-reference against all 174 workflows
3. Identify affected workflows
4. Update references atomically
5. Validate YAML syntax
6. Create commit with phase marker

### Phase 3 Detection (Additional Renames)
When Phase 3 commits are detected:
1. Repeat Phase 2 process
2. Track cumulative changes
3. Validate no path conflicts
4. Generate consolidated change report

## Execution Checklist

### Before Phase 2 Starts ✅
- [x] Scan all 213 workflows
- [x] Identify 174 workflows with path references
- [x] Establish YAML validity baseline
- [x] Create SQL tracking database
- [x] Initialize update system
- [x] Set up monitoring infrastructure

### During Phase 2 (Reactive)
- [ ] Monitor git commits for Phase 8.3.2 markers
- [ ] Detect renamed paths automatically
- [ ] Update affected workflows
- [ ] Validate YAML syntax
- [ ] Generate atomic commit (Phase 2 batch)

### During Phase 3 (Reactive)
- [ ] Monitor git commits for Phase 8.3.3 markers
- [ ] Detect renamed paths automatically
- [ ] Update affected workflows
- [ ] Validate YAML syntax
- [ ] Generate atomic commit (Phase 3 batch)

### After Both Phases Complete ✅
- [ ] Run comprehensive validation
- [ ] Check for orphaned old paths (grep should return 0)
- [ ] Verify all artifact paths
- [ ] Generate final report
- [ ] Create accountability summary

## Key Reference Files

- **Workflow directory**: `.github/workflows/` (213 files)
- **Build scripts**: `scripts/` (35+ scripts with CI references)
- **Tracking database**: Session SQLite (workflow_updates, phase_commits, validation_results)
- **Report output**: `.codex/SESSION_2_SUPPORT_WORKFLOW_UPDATES_REPORT.md`

## Success Criteria

1. **Detection**: 100% of Phase 2-3 renames detected within 5 minutes
2. **Updates**: 100% of affected workflows updated atomically
3. **Validation**: 100% YAML validity maintained
4. **Paths**: 0 references to old paths remain (except comments)
5. **Commits**: 2 atomic commits (Phase 2, Phase 3) with proper messages
6. **Report**: Complete traceability of all changes

## Atomic Commit Templates

### Phase 2 Batch Commit
```
ci: update workflow paths for Phase 8.3.2 file renames

Updated 174 workflows with new paths from Phase 8.3.2 renames.
- Scripts: XX references updated
- Docs: YY references updated
- Sources: ZZ references updated
- Total: WWW changes across VVV workflows

All YAML syntax validated. No path collisions detected.

Tracking: See .codex/SESSION_2_SUPPORT_WORKFLOW_UPDATES_REPORT.md
```

### Phase 3 Batch Commit
```
ci: update workflow paths for Phase 8.3.3 file renames

Updated affected workflows with new paths from Phase 8.3.3 renames.
- Scripts: XX references updated
- Docs: YY references updated
- Total: WWW additional changes across VVV workflows

All YAML syntax validated. Cumulative changes validated for conflicts.

Tracking: See .codex/SESSION_2_SUPPORT_WORKFLOW_UPDATES_REPORT.md
```

## Escalation Path

If any issue is detected:
1. **YAML errors**: Fix immediately, revalidate, update SQL tracking
2. **Path conflicts**: Flag in report, escalate to Phase manager
3. **Missing commits**: Wait up to 5 minutes, then scan manually
4. **Tool failures**: Use fallback grep-based updates

## Parallel Execution Notes

- This track runs CONCURRENTLY with Phases 2-3
- NO blocking - Phase 2-3 can commit freely
- Updates happen reactively as commits appear
- All changes are ADDITIVE to workflow files only
- No breaking changes to existing workflows

## Monitoring Command (for manual checks)

```bash
# Check for Phase 2 commits
git log --oneline --all --grep="Phase 8.3.2\|Phase-8.3.2" | head -5

# Check for Phase 3 commits
git log --oneline --all --grep="Phase 8.3.3\|Phase-8.3.3" | head -5

# Validate all workflows
for file in .github/workflows/*.yml; do
  python3 -c "import yaml; yaml.safe_load(open('$file'))" && echo "✓ $file" || echo "✗ $file"
done

# Check for orphaned old paths
grep -r "OLD_PATH_PATTERN" .github/workflows/
```

## Status Dashboard

```
┌─────────────────────────────────────────┐
│  SESSION 2 SUPPORT TRACK STATUS         │
├─────────────────────────────────────────┤
│ Phase 2 Status:        [MONITORING]     │
│ Phase 3 Status:        [MONITORING]     │
│ Workflows Updated:     0/174            │
│ YAML Validity:         100% (213/213)   │
│ Orphaned Paths:        0                │
│ Last Scan:             2024-01-XX 00:00 │
└─────────────────────────────────────────┘
```

## Contact & Authority

**Agent**: Workflow CI Fixer Agent (Session 2 Support Track)
**Authority**: @mbaetiong D-tier autonomous
**Escalation**: Create [SESSION-2-ESCALATION] issue if blocking found

---

**Document Status**: 🟢 Ready for Parallel Execution  
**Last Updated**: 2024-01-23T00:00:00Z  
**Next Phase**: Await Phase 2 commits
