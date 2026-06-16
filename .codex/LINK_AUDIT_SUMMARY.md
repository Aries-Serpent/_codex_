# 📋 Link Validation Audit Summary - CLEANED REPORT

**Scan Date:** 2026-06-16
**Repository:** Aries-Serpent/_codex_
**Scope:** docs/ (1,646 markdown files)

## ✅ Quick Stats

| Metric | Count | Note |
|--------|-------|------|
| Files scanned | 1,646 | ✅ |
| Valid internal links | 2,718 | ✅ |
| **Real broken links** | 2 | ⚠️ Requires action |
| False positives filtered | 62 | ℹ️ Not actionable |
| Same-file anchors broken | 95 | ⚠️ Minor issues |
| Cross-file anchors broken | 13 | ⚠️ Links to missing sections |
| External URLs | 2,699 | ℹ️ Manual review |
| **Overall success rate** | 96.1% | ✅ Healthy |

---

## 🔴 REAL BROKEN LINKS (Requires Action)

**Count: 2 critical issues**

### Missing or Incorrect File References

| Source File | Link | Issue | Line |
|-------------|------|-------|------|
| `docs/GITHUB_PAGES_MANAGER_IMPLEMENTATION.md` | `../guides/user-guide.md` | File not found: guides/user-guide.md | 233 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `.+?` | File not found: docs/plans/.+? | 2379 |


---

## 🟡 ANCHOR REFERENCE ISSUES

### Same-File Anchors (95 broken references)

These are links within a file that reference non-existent sections:

- **docs/AGENTIC_REPO_SYSTEM_GUIDE.md**: 3 broken anchors
  - `#5-manifest--discovery`
  - `#10-security--injection-hardening`
  - `#11-accountability--audit-trail`
- **docs/CODEBASE_MERMAID_MAPS.md**: 5 broken anchors
  - `#9-pda-loop--aftermath`
  - `#11-security--token-delegation`
  - `#16-phase-9--cognitive-brain-autonomous-ops`
  - ... and 2 more
- **docs/Copy_of_Repository Secrets and Variables Inventory.md**: 7 broken anchors
  - `#1-repository-variables-settingsvariablesactions`
  - `#3-environment-variables--secrets-aries_serpent_codex_`
  - `#8-immediate-post-setup-validation-ui`
  - ... and 4 more
- **docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md**: 16 broken anchors
  - `#2-how-to-set-variables--quick-links`
  - `#5-environment-secrets-aries_serpent_codex_`
  - `#6a--cognitive-brain`
  - ... and 13 more
- **docs/admin/HUMAN_ADMIN_REPO_VARIABLES_SETUP.md**: 1 broken anchors
  - `#1--batch-cli-method-recommended---5-minutes`
- **docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md**: 3 broken anchors
  - `#3-new-variables--cognitive-brain`
  - `#4-new-variables--copilot-cli`
  - `#5-new-variables--cicd-health`
- **docs/admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md**: 3 broken anchors
  - `#mcp-architecture-in-_codex_`
  - `#current-_codex_-mcp-implementation`
  - `#_codex_-specific-integration-examples`
- **docs/authentication/USER_GUIDE.md**: 5 broken anchors
  - `#enabling-multi-factor-authentication`
  - `#working-with-tokens`
  - `#session-management`
  - ... and 2 more
- **docs/ci/CI_RESCUE_PIPELINE.md**: 1 broken anchors
  - `#5-sequence-diagram--golden-path-2026-03-30`
- **docs/ci/PR_LIFECYCLE.md**: 12 broken anchors
  - `#7-rescue--self-healing-chain`
  - `#15-rag-module-tests--chronic-failure-pattern`
  - `#16-copilot-comment-budget--rate-limit-controls`
  - ... and 9 more

... and 16 more files with anchor issues


**Fix:** Ensure heading names match the referenced anchors. GitHub converts headings to anchors by:
- Converting to lowercase
- Replacing spaces with hyphens
- Removing special characters

Example: `## Configuration Settings` → `#configuration-settings`

### Cross-File Anchors (13 broken references)

These are links that reference sections in other files:

- **Source:** `docs/PR_TEMPLATE_COMPREHENSIVE.md` (line 710)
  **Link:** `./CONTRIBUTING.md#testing-requirements`
  **Target:** `docs/CONTRIBUTING.md` section `#testing-requirements`
- **Source:** `docs/ROADMAP.md` (line 53)
  **Link:** `ops/SAR_METHODOLOGY.md#10-gap-registry--roadmap`
  **Target:** `docs/ops/SAR_METHODOLOGY.md` section `#10-gap-registry--roadmap`
- **Source:** `docs/cognitive_brain/INDEX.md` (line 41)
  **Link:** `../evolution/EVOLUTION_TIMELINE.md#phase-9`
  **Target:** `docs/evolution/EVOLUTION_TIMELINE.md` section `#phase-9`
- **Source:** `docs/cognitive_brain/INDEX.md` (line 42)
  **Link:** `../evolution/PLANSET_REGISTRY.md#phase-9`
  **Target:** `docs/evolution/PLANSET_REGISTRY.md` section `#phase-9`
- **Source:** `docs/index.md` (line 99)
  **Link:** `../CONTRIBUTING.md#using-operational-templates`
  **Target:** `CONTRIBUTING.md` section `#using-operational-templates`
- **Source:** `docs/reporting/copilot_agent_session_standard_operation.md` (line 120)
  **Link:** `workflow_portfolio_7d_analysis.md#-branch-update-conflict-dashboard`
  **Target:** `docs/reporting/workflow_portfolio_7d_analysis.md` section `#-branch-update-conflict-dashboard`
- **Source:** `docs/status_updates/survey-0D_base_-and-1926-2025-10-30.md` (line 2212)
  **Link:** `./guides/reasoning_overview.md#evaluation-readiness`
  **Target:** `docs/status_updates/guides/reasoning_overview.md` section `#evaluation-readiness`
- **Source:** `docs/system/CODEBASE_DASHBOARD.md` (line 47)
  **Link:** `../SECRETS_AND_ENVIRONMENT_VARIABLES.md#🗺️-workflow--agent-variable-usage-map`
  **Target:** `docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md` section `#🗺️-workflow--agent-variable-usage-map`
- **Source:** `docs/tech_debt/research_queue/questions_for_research.md` (line 679)
  **Link:** `../../../src/codex_init.py#L15`
  **Target:** `src/codex_init.py` section `#L15`
- **Source:** `docs/tech_debt/research_queue/questions_for_research.md` (line 716)
  **Link:** `../../../tools/validate.py#L25`
  **Target:** `tools/validate.py` section `#L25`
- **Source:** `docs/tech_debt/research_queue/questions_for_research.md` (line 763)
  **Link:** `../../../src/codex_ml/training/unified_training.py#L42`
  **Target:** `src/codex_ml/training/unified_training.py` section `#L42`
- **Source:** `docs/tech_debt/research_queue/questions_for_research.md` (line 784)
  **Link:** `../../../src/codex_ml/training/unified_training.py#L43`
  **Target:** `src/codex_ml/training/unified_training.py` section `#L43`
- **Source:** `docs/validation/Windows_Filename_Remediation.md` (line 158)
  **Link:** `../../AGENTS.md#-cross-platform-filename-requirements`
  **Target:** `AGENTS.md` section `#-cross-platform-filename-requirements`


**Fix:** Either add the missing section to the target file or update the link.

---

## ℹ️ FALSE POSITIVES FILTERED OUT

**Count: 62**

The following items were detected as links but are actually:
- Regex patterns in code examples
- Type annotations
- Code snippets
- Placeholder text

These do not require any action.

Examples of filtered false positives:
- `[^"\']+` in docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md
- `[^"\']+` in docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md
- `[^"\']+` in docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md
- `mailto:support@example.com` in docs/GITHUB_SPARK_INTEGRATION_GUIDE.md
- `[^"\']+` in docs/quality/BROKEN_LINKS_REPORT.md
- ... and 57 more


---

## 🌐 EXTERNAL LINKS (2,699 found)

**Action:** These should be verified periodically but don't block documentation.

Consider using:
- `markdown-link-checker` npm package
- GitHub Actions: `gaurav-nelson/github-action-markdown-link-check`
- Manual spot checks with `curl -I <url>`

---

## ✨ RECOMMENDATIONS

### High Priority
1. Fix 2 real broken file references
2. These prevent proper navigation and hurt documentation quality

### Medium Priority
1. Fix 95 same-file anchor references
2. Update 13 cross-file anchor links
3. These improve navigation within and between documents

### Low Priority
1. Set up automated link checking in CI/CD
2. Validate external links periodically
3. Document link conventions for contributors

---

## 📊 Files Most Affected

Top files with anchor issues:
- `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md`: 16 anchor issues
- `docs/ci/PR_LIFECYCLE.md`: 12 anchor issues
- `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md`: 10 anchor issues
- `docs/ops/SAR_METHODOLOGY.md`: 9 anchor issues
- `docs/Copy_of_Repository Secrets and Variables Inventory.md`: 7 anchor issues


---

## 🔧 How to Run This Audit

```bash
# Run the validator
python3 .codex/link_validator.py

# View results
cat .codex/LINK_VALIDATION_REPORT.md  # Full markdown report
cat .codex/link_audit_detailed.json   # Raw JSON data
```

---

**Generated:** 2026-06-16T13:28:39Z
**Status:** ✅ Complete
**Next Step:** Review and fix broken links per priority
