# Wave 2 Launch Plan — Ready to Execute

## Current Status (Turn ~20)
- **Wave 1 Agents**: 5/6 running (1 completed, 1 queued)
- **Estimated Wave 1 Completion**: Turn 45-60 (15-40 minutes)
- **Wave 2 Launch Trigger**: When consolidated agents ≤2 running

## Wave 2 Agents (6 total) — Parallel Deployment

### Priority 1: Security & Content (Agents 7-8, Turns 21-25)
**Agent 7: link-validator-agent**
- Fix 100 broken documentation links
- Output: `.codex/phase6_link_audit_complete.json`
- Acceptance: 100% link validity

**Agent 8: doc-refactor-test-agent**
- Validate & restructure documentation for v0.1.0
- Output: docs/ (restructured), `.codex/phase6_doc_validation_report.json`
- Acceptance: All code examples executable, 100% freshness

### Priority 2: GitHub Pages & Deployment (Agents 9-10, Turns 21-25)
**Agent 9: post-merge-doc-alignment-agent**
- Sync documentation with GitHub Pages
- Output: `.codex/phase6_pages_alignment_report.json`
- Acceptance: All pages aligned, nav complete

**Agent 10: github-pages-manager**
- Deploy live documentation site
- Output: `.codex/phase6_pages_deployment_report.json`
- Acceptance: Pages live at https://aries-serpent.github.io/_codex_/

### Priority 3: Security Fixes & Phase 7 (Agents 11-12, Turns 21-25)
**Agent 11: codeql-alert-resolution-agent**
- Fix all CodeQL alerts (coordinate with security-scanner)
- Output: Fixed source files, `.codex/phase6_codeql_remediation_log.jsonl`
- Acceptance: 0 CodeQL alerts remaining

**Agent 12: ci-auto-healer-agent**
- Document CI healing patterns (Phase 7 preparation)
- Output: `.codex/phase7_healing_pattern_library.json`
- Acceptance: 20+ patterns documented, 10+ rules operational

## Execution Strategy
- Launch all 6 agents in parallel (Turn 21-30)
- Monitor for completion (Turn 30-60)
- Allow 60-90 minutes for agent execution
- Consolidate artifacts (Turn 160-170)

## Success Criteria
✅ All 6 Wave 2 agents launched
✅ 100 broken links fixed
✅ Documentation 100% fresh
✅ GitHub Pages live
✅ 0 CodeQL alerts
✅ Phase 7 patterns ready

## Next Trigger
**When**: consolidated Wave 1 agents ≤2 running
**Action**: Launch all 6 Wave 2 agents in parallel
**Expected Time**: Turn 25-30
