# Archive Policy Consolidation — PR Execution Plan

> Source: Codex automation status update (2024-10-24)
> Scope: Publish and merge the already-prepared archive policy consolidation commit (`cfba4786`).

## Current State Snapshot

| Dimension | Status | Notes |
| --- | --- | --- |
| Execution | ✅ Complete | Commit `cfba4786` is present on the `work` branch.
| Pre-commit validation | ✅ Passed | Local hooks finished successfully; no outstanding lint/test actions.
| Evidence trail | ✅ Recorded | `.codex/evidence/archive_ops.jsonl` contains the consolidation record (line 30).
| Backward compatibility | ✅ Maintained | Stub left at the historical policy location; branch protection checklist already references the new path.
| Branch status | 🔄 Ready for PR | Branch is clean, rebased, and conventional-commit compliant.
| PR creation | 🔲 Pending | Awaiting formal pull request submission.

## Phase Breakdown

### Phase 1 — Create Pull Request (≈ 5 min)

1. Open a PR from `work` → `main` with title `docs(archive): consolidate archive policy guidance`.
2. Use the prepared description:
   ```bash
   gh pr create \
     --title "docs(archive): consolidate archive policy guidance" \
     --body "$(cat <<'EOB'
   ## Summary

   Consolidates archive/deprecation policy from multiple variants into a single canonical document located at `docs/arch/_archive-policy/canonical-archiving-policy.md`.

   - Moved: `docs/policies/archive-policy.md` → `docs/arch/_archive-policy/canonical-archiving-policy.md`
   - Retained: Deprecated variants (v2–v4) in `_deprecated/` folder for traceability
   - Created: Index document with navigation, related artifacts, validation checklist
   - Updated: `docs/policies/branch-protection-checklist.md` (policy path reference)
   - Appended: `.codex/evidence/archive_ops.jsonl` with consolidation record
   - Stub: Old location preserved for backward compatibility

   ## References

   - Related ADR: docs/arch/adr-Previous Cycle-10-17-root-docs-cleanup.md
   - Evidence: Commit cfba4786 + .codex/evidence/archive_ops.jsonl (line 30)

   ## Validation

   - ✅ Pre-commit hooks: all passed
   - ✅ Conventional Commits: compliant (`docs(archive):...`)
   - ✅ No breaking changes
   - ✅ Backward compatible (stub + index)

   Closes: #TBD (if applicable)
   EOB
   )" \
     --head work \
     --base main
   ```
3. Apply labels such as `documentation`, `archive`, and `governance` if your workflow uses them.

### Phase 2 — CI & Code Review (≈ 5–30 min)

| Check | Expected Result | Contingency |
| --- | --- | --- |
| Link checker | ✅ Pass | Fix any outdated references under `docs/` and amend the commit. |
| Markdown lint | ✅ Pass | Re-run pre-commit and adjust formatting if necessary. |
| Pre-commit (server) | ✅ Pass | Should mirror local results; investigate environmental differences if it fails. |
| CODEOWNERS review | ⏳ Pending | Manually request reviewers if auto-assignment does not trigger. |
| Security scans | ✅ Pass | Docs-only change; issues are unlikely. |

### Phase 3 — Merge & Cleanup (≈ 2–5 min)

1. Merge once approvals and checks complete (squash or rebase preferred for single-commit PRs).
2. Delete the `work` branch after merge to keep branch list tidy.
3. Confirm the merge by verifying `git log --oneline -1 main` shows commit `cfba4786`.

### Phase 4 — Post-Merge Validation (≈ 5–10 min)

1. Pull latest `main` and run the targeted test suite if desired:
   ```bash
   git checkout main
   git pull origin main
   pytest -q
   ```
2. Validate archive operations:
   - Ensure `.codex/evidence/archive_ops.jsonl` logs subsequent entries as expected.
   - Spot-check a tombstone workflow against the canonical policy.
3. Verify no stale references remain to `docs/policies/archive-policy.md` beyond the stub by running:
   ```bash
   rg "docs/policies/archive-policy" --type md
   ```

### Phase 5 — Optional Enhancements (≈ 15–30 min)

- Update `../CHANGELOG.md` under the “Documentation” section to highlight the consolidation.
- Add or link a tombstone template in `docs/arch/_archive-policy/templates/` if none exists.
- Document archive tooling paths (planner, vacuum scripts) within `index.md` for discoverability.
- Consider drafting an ADR summarizing the consolidation if governance requires it.

## Decision Paths

| Option | When to Choose | Actions |
| --- | --- | --- |
| **A. Quick Path** | Low-risk, docs-only change | Phase 1 → Phase 3. |
| **B. Comprehensive Path** | Desire extra documentation polish | Phase 1 → Phase 5 (selected items). |
| **C. Extended Validation** | Need exhaustive assurance | Phase 1 → Phase 5 with full test suites and tooling checks. |

## Next Action

- Confirm which option (A/B/C) you intend to follow.
- Execute Phase 1 immediately to open the pull request.
- Monitor CI and reviews per the selected path.

Maintain this document alongside the canonical policy so future maintainers can reuse or adapt the PR workflow.
