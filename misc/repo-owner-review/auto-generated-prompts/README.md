# Auto-Generated Follow-Up Prompts

## Purpose
This directory contains auto-generated follow-up prompt files that were previously located in `.github/copilot-prompts/active/`. These files were moved here as part of repository cleanup based on code review feedback.

## Why These Files Were Moved

**Date Moved**: 2025-12-29  
**Original Location**: `.github/copilot-prompts/active/`  
**Moved By**: Copilot Agent (PR #2639)  
**Reason**: Code review identified these as "auto-generated bloat"

### Review Feedback

**Review Location**: [PR #2639 Review Thread](https://github.com/Aries-Serpent/_codex_/pull/2639#pullrequestreview-3616439065)
The code reviewer noted that these 21 files:
1. Were nearly-identical auto-generated templates with minimal customization
2. Each file said "No files modified" in the Files Modified section
3. Had placeholder tasks like "Complete implementation" and "Add validation commands"
4. Contained the exact same 5-pass self-review protocol
5. Had generic instructions without specific, actionable content
6. Added significant repository bloat (over 2,400 lines of mostly duplicated content) without clear value

### Recommendations from Review
- Only generate these files when there's actual follow-up work needed
- Store templates separately and generate them on-demand
- Add more specific, actionable content for each PR
- Use a more lightweight tracking mechanism (like GitHub Issues or a single tracking file)

## Files in This Directory

The following 21 follow-up prompt files were restored from commit `2e0369c~1` and moved here:

1. **PR-2635-followup.md** - Shows evidence of active use:
   - Status changed to "✅ IMPLEMENTATION COMPLETE - Awaiting CI Validation"
   - Multiple checked completion items (Priority 1 tasks marked with ✅)
   - Contains specific completed work with commit SHAs
   - may be valuable as example of properly utilized follow-up prompt
2. PR-2636-followup.md
3. PR-2637-followup.md
4. PR-2638-followup.md
5. PR-2641-followup.md
6. PR-2642-followup.md
7. PR-2643-followup.md
8. PR-2644-followup.md
9. PR-2645-followup.md
10. PR-2646-followup.md
11. PR-2647-followup.md
12. PR-2648-followup.md
13. PR-2649-followup.md
14. PR-2650-followup.md
15. PR-2651-followup.md
16. PR-2652-followup.md
17. PR-2653-followup.md
18. PR-2654-followup.md
19. PR-2655-followup.md
20. PR-2656-followup.md
21. **PR-9999-followup.md** - Template instantiation with placeholder PR number (test/development file)
   - Contains real commit data (5e2b236, dd00da3) from branch `copilot/fix-import-order-issue`
   - Used 9999 as placeholder PR number, suggesting test instantiation
   - Not a core template (actual template is in `.github/copilot-prompts/templates/pr-continuation.md`)

### Note on PR-2635
This file shows clear signs of active use during development, unlike the other generic auto-generated files. It contains:
- Modified status line indicating implementation completion
- Four checked Priority 1 tasks with completion indicators (✅)
- Specific commit history with meaningful work descriptions
- "No files modified" section suggesting it was tracking work-in-progress

This file may serve as a useful example of how the follow-up prompt system should work when properly utilized, compared to the mostly-empty template instantiations.

## Can This Content Be Repurposed?

**Possibly, but needs significant rework:**

- The 5-pass self-review protocol template could be extracted into a single reusable template
- The validation command patterns could be documented in a developer guide
- The follow-up task structure could inform a GitHub Issue template
- The self-review criteria could be integrated into CI/CD checks

## Replacement/Improvement Strategy

Instead of auto-generating individual files for each PR, consider:

1. **GitHub Issues**: Use issue templates for follow-up work with proper task tracking
2. **Single Template File**: Store one canonical template and reference it in documentation
3. **CI/CD Integration**: Automate validation checks directly in workflows
4. **Wiki/Documentation**: Move generic guidance to repository documentation
5. **On-Demand Generation**: Only create follow-up files when specific action items are identified

## Repository Owner Action Required

The repository owner should review these files and decide:
- [ ] Can these be permanently deleted?
- [ ] Should any content be extracted into templates/documentation?
- [ ] Should the auto-generation process be modified or disabled?
- [ ] Are there other similar auto-generated files that need review?

## Related Documentation
- Original commit removing files: `2e0369c`
- Commit before deletion: `2e0369c~1`
- PR that removed files: #2639
- Code review thread: https://github.com/Aries-Serpent/_codex_/pull/2639#pullrequestreview-3616439065
