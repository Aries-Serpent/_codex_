# COPILOT FOLLOW-UP PROMPT FOR PR #2682

**IMPORTANT**: This follow-up prompt MUST be posted as a comment on PR #2682 to activate the next Copilot Agent session.

## Instructions for Posting:

1. Navigate to: https://github.com/Aries-Serpent/_codex_/pull/2682
2. Copy the content below (starting with @copilot)
3. Paste as a NEW COMMENT on the PR
4. Submit the comment to trigger the next Copilot Agent session

---

## COPILOT FOLLOW-UP PROMPT (Copy below this line)

@copilot Begin execution of the GitHub Pages Documentation Site Improvement Plan located at `.codex/plans/github_pages_improvement_plan.md`. This is a critical task to fix formatting issues on https://aries-serpent.github.io/_codex_/ where code blocks escape the frame and pages have inconsistent formatting.

## Task: Execute Multi-Agent Documentation Improvement System

### Immediate Actions (This Session):

**Phase 1: Diagnosis & Analysis (2-3 hours)**
1. Use the multi-agent framework from `.codex/tools/agent_system_framework.py` 
2. Create and run the 8-agent documentation improvement system:
   - Site Crawler Agent: Scan https://aries-serpent.github.io/_codex_/
   - CSS Analyzer Agent: Analyze current stylesheets
   - Code Block Inspector Agent: Identify all overflow issues
   - Layout Validator Agent: Check responsive design
3. Generate comprehensive diagnosis report with:
   - List of all affected pages
   - Specific code blocks with overflow
   - CSS issues identified
   - Responsive breakpoint failures
4. Save report to `.codex/reports/github_pages_diagnosis.md`

**Phase 2: Solution Design (3-4 hours)**
5. Use Fix Generator Agent to create CSS patches
6. Design responsive layout improvements
7. Create `docs/assets/css/custom.css` with fixes:
   - Code block overflow fixes (max-width: 100%, overflow-x: auto)
   - Container width constraints (max-width: 980px)
   - Responsive breakpoints (@media queries)
   - Table handling improvements
8. Save all CSS fixes to file

**Phase 3: Implementation (2-3 hours)**  
9. Create `docs/_layouts/default.html` if it doesn't exist
10. Update `docs/_config.yml` to reference custom CSS
11. Use Markdown Formatter Agent to standardize all .md files in docs/
12. Apply formatting rules:
    - Max line length: 120 chars
    - Consistent code fence syntax
    - Proper heading hierarchy
13. Test locally with `bundle exec jekyll serve`

**Phase 4: Validation (2-3 hours)**
14. Run Testing Agent to validate improvements
15. Check code blocks on multiple viewports (320, 768, 1024, 1920px)
16. Verify responsive design works
17. Test on Chrome, Firefox, Safari
18. Run accessibility audit with Lighthouse
19. Fix any issues found

**Phase 5: Deployment**
20. Commit all changes with message: "fix(docs): Improve GitHub Pages formatting and responsive design"
21. Push to trigger GitHub Pages rebuild
22. Verify deployment at https://aries-serpent.github.io/_codex_/
23. Create `.codex/reports/github_pages_improvement_results.md` with before/after metrics

### Success Criteria:
- ✅ Zero code blocks overflow viewport
- ✅ Mobile responsiveness score > 95/100
- ✅ All pages consistently formatted
- ✅ Tests pass on all major browsers
- ✅ Accessibility score > 95/100

### Files to Create/Modify:
- `docs/assets/css/custom.css` (NEW)
- `docs/_layouts/default.html` (NEW or UPDATE)
- `docs/_config.yml` (UPDATE)
- `docs/**/*.md` (FORMAT ALL)
- `.codex/reports/github_pages_diagnosis.md` (NEW)
- `.codex/reports/github_pages_improvement_results.md` (NEW)

### Tools Available:
- Multi-agent framework: `.codex/tools/agent_system_framework.py`
- Code sweep system: `.codex/tools/multi_agent_code_sweep.py`
- Implementation plan: `.codex/plans/github_pages_improvement_plan.md`

### Important Notes:
1. Use the agent system framework to build the 8-agent documentation improvement system
2. Follow the 5-phase plan exactly as documented
3. Test thoroughly before deploying
4. Document all changes in reports
5. Preserve existing content, only fix formatting

### If Cannot Complete in One Session:
Create a follow-up comment on PR #2682 with this exact format:

```
@copilot continue GitHub Pages improvement from Phase [X]. 

Previous work completed:
- [Detailed summary of what was accomplished]
- [Files created/modified]
- [Issues resolved]

Next steps required:
1. [Specific action item 1]
2. [Specific action item 2]
3. [Specific action item 3]

Files to modify:
- [List each file with specific changes needed]

Remaining validation:
- [ ] [Specific test 1]
- [ ] [Specific test 2]
- [ ] [Specific test 3]

Success criteria status:
- [X] Completed criteria
- [ ] Pending criteria

Estimated time remaining: [X hours]

YOU MUST ENTER AND SUBMIT the follow up prompt as a NEW COMMENT ON PR #2682, verify you've submitted the prompt as a comment on the copilot enabled branch within the active PR #2682. First line of the comment MUST begin with @copilot (no spaces, no backticks).
```

### Validation Before Concluding Each Session:
- Run self-review with code_review tool
- Verify all tests pass locally  
- Check that custom CSS is properly linked
- Confirm code blocks no longer overflow
- Test on mobile viewport (320px, 768px)
- Document all metrics in reports
- Create follow-up prompt if work incomplete

### Critical Success Factors:
1. **Iterative Self-Healing**: If errors occur, diagnose and fix immediately
2. **Continuous Validation**: Test after each major change
3. **Complete Documentation**: Every change must be documented
4. **No Deferred Work**: Resolve all issues in active session or document with solution plan
5. **Follow-Up Continuation**: Always create next prompt if work incomplete

Begin execution immediately. Use the agent framework to build the system, run diagnosis, generate fixes, implement changes, test thoroughly, and deploy. Report progress using report_progress after each phase completion.
