# 📦 ARCHIVED AGENTS REFERENCE

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:50:53.895640  
**Purpose:** Document why agents were archived and migration paths

---

## Overview

14 agents have been archived for strategic reasons. This document provides migration guidance for users who encounter these agents.

### Quick Migration Table

| Archived Agent | Reason | Replacement | Migration Path |
|---|---|---|---|
| coverage-gapfill-agent | Consolidated | unified-coverage-agent | Use `@copilot use unified-coverage-agent` |
| test-coverage-agent | Consolidated | unified-coverage-agent | Use unified-coverage-agent |
| coverage-maintenance-agent | Consolidated | unified-coverage-agent | Use unified-coverage-agent |
| coverage-roadmap-agent | Consolidated | unified-coverage-agent | Use unified-coverage-agent |
| test-coverage-monitor | Consolidated | unified-coverage-agent | Use unified-coverage-agent |
| documentation-quality-agent | Consolidated | unified-doc-agent | Use unified-doc-agent |
| doc-refactor-test-agent | Consolidated | unified-doc-agent | Use unified-doc-agent |
| workflow-health-monitor.deprecated | Replaced | workflow-health-monitor | Use workflow-health-monitor (v2) |
| test-coverage-agent-old | Obsolete | unified-coverage-agent | Use unified-coverage-agent |
| repo-sync-v1 | Replaced | repository-organization-agent | Use repository-organization-agent |
| ci-legacy-fixer | Deprecated | ci-failure-resolution-agent | Use ci-failure-resolution-agent |
| auth-legacy-validator | Obsolete | security-audit-agent | Use unified-security-scanner |
| doc-link-checker-old | Consolidated | link-validator-agent (→ unified-doc-agent) | Use unified-doc-agent |
| performance-profiler-v1 | Replaced | performance-monitor-agent | Use performance-monitor-agent |

---

## Detailed Migration Guides

### Coverage Agents → unified-coverage-agent

**5 Coverage Agents Consolidated:**
1. coverage-gapfill-agent
2. coverage-maintenance-agent
3. coverage-roadmap-agent
4. test-coverage-agent
5. test-coverage-monitor

**Why Consolidated:**
- Redundant functionality (5 agents doing overlapping tasks)
- Fragmented user experience (unclear which to use)
- Difficult to maintain consistent coverage strategy
- Complicated dependency tracking

**Migration:**
```bash
# OLD:
@copilot use coverage-gapfill-agent
Task: "Fill coverage gaps in src/auth/"

# NEW:
@copilot use unified-coverage-agent
Task: "Fill coverage gaps in src/auth/ (gap-fill mode)"
```

**Backward Compatibility:**
- `unified-coverage-agent` auto-detects mode (gap-fill, maintenance, roadmap, monitor)
- Configuration files still supported
- Existing coverage baselines preserved

**Timeline:**
- June 2026: Agents archived
- July 2026: Full deprecation
- August 2026: Removal from registry

---

### Documentation Agents → unified-doc-agent

**5 Documentation Agents Consolidated:**
1. documentation-quality-agent
2. doc-refactor-test-agent
3. terminology-consistency-agent
4. link-validator-agent
5. doc-freshness-checker

**Why Consolidated:**
- Complementary functions better served together
- Improved documentation workflow
- Single entry point for all doc work
- Better consistency enforcement

**Migration:**
```bash
# OLD:
@copilot use documentation-quality-agent
Task: "Improve documentation quality"

# NEW:
@copilot use unified-doc-agent
Task: "Improve documentation quality (quality mode)"
```

---

### workflow-health-monitor.deprecated → workflow-health-monitor

**Reason for Deprecation:**
- Version 1 used naive metric collection
- Version 2 uses Bayesian probabilistic analysis
- Better accuracy and false-positive reduction
- Integrated with PDA loop

**Migration:**
```bash
# OLD (v1):
@copilot use workflow-health-monitor.deprecated

# NEW (v2):
@copilot use workflow-health-monitor
```

**Key Improvements:**
- 40% fewer false positives
- Real-time anomaly detection
- Historical trend analysis
- Predictive failure warnings

---

## Deprecation Process & Timeline

### Deprecation Status Legend
- 🟢 **Active:** Fully supported
- 🟡 **Deprecated:** Use replacement agent
- 🔴 **Archived:** No longer available

### Current Deprecation Timeline

**Phase 1 (Now - June 2026):** All 14 agents marked as archived
- Users directed to replacements
- Old agents still callable (with deprecation warning)
- Documentation updated

**Phase 2 (July 2026):** Soft removal
- Archived agents return error directing to replacement
- No automatic migration (user must update scripts)
- API returns 410 Gone for archived agents

**Phase 3 (August 2026):** Hard removal
- Archived agents completely removed from registry
- Historical data preserved in archive
- No way to call archived agents

---

## Backward Compatibility Notes

### Configuration File Migration

**Old format (coverage-gapfill-agent):**
```yaml
agent: coverage-gapfill-agent
config:
  target_coverage: 0.85
  modules: [src/auth, src/api]
```

**New format (unified-coverage-agent):**
```yaml
agent: unified-coverage-agent
mode: gap-fill
config:
  target_coverage: 0.85
  modules: [src/auth, src/api]
```

### API Compatibility
- Old agent IDs still recognized in API calls
- Transparent routing to replacement agents
- Response format may differ (documented in migration guide)

---

## Archive Metadata

### Archived Agents (14 total)

| Agent ID | Name | Archived | Reason |
|----------|------|----------|--------|
| coverage-gapfill-agent | Coverage Gap Filler | 2026-06-20 | Consolidated |
| coverage-maintenance-agent | Coverage Maintenance | 2026-06-20 | Consolidated |
| coverage-roadmap-agent | Coverage Roadmap | 2026-06-20 | Consolidated |
| test-coverage-agent | Test Coverage (v1) | 2026-06-20 | Consolidated |
| test-coverage-monitor | Test Coverage Monitor | 2026-06-20 | Consolidated |
| documentation-quality-agent | Doc Quality (v1) | 2026-06-20 | Consolidated |
| doc-refactor-test-agent | Doc Refactor Test | 2026-06-20 | Consolidated |
| workflow-health-monitor.deprecated | Workflow Monitor (v1) | 2026-06-20 | Replaced |
| test-coverage-agent-old | Test Coverage (legacy) | 2026-06-20 | Obsolete |
| repo-sync-v1 | Repo Sync (v1) | 2026-06-20 | Replaced |
| ci-legacy-fixer | CI Fixer (legacy) | 2026-06-20 | Deprecated |
| auth-legacy-validator | Auth Validator (legacy) | 2026-06-20 | Obsolete |
| doc-link-checker-old | Link Checker (old) | 2026-06-20 | Consolidated |
| performance-profiler-v1 | Performance Profiler (v1) | 2026-06-20 | Replaced |

---

## How to Update Your Code

### Step 1: Find archived agents in your code
```bash
grep -r "coverage-gapfill-agent\|test-coverage-agent\|documentation-quality-agent" *.py *.md *.yaml
```

### Step 2: Replace with consolidated agents
```bash
sed -i 's/coverage-gapfill-agent/unified-coverage-agent/g' *
sed -i 's/documentation-quality-agent/unified-doc-agent/g' *
sed -i 's/workflow-health-monitor.deprecated/workflow-health-monitor/g' *
```

### Step 3: Update mode specification
Add `mode:` parameter if required by new agent

### Step 4: Test replacement agents
```bash
@copilot test unified-coverage-agent
@copilot test unified-doc-agent
```

---

## FAQ

**Q: Can I still use archived agents?**
A: Only until August 2026. Migrate now to avoid disruption.

**Q: Will my existing configs work?**
A: Partially. You may need to add `mode:` parameter for some agents.

**Q: What if I have custom scripts using archived agents?**
A: Update them now. Automated deprecation warnings will appear in July.

**Q: How do I migrate complex workflows?**
A: See specific migration guides above for each agent family.

---

## Metadata

- **Generated:** 2026-06-20T06:50:53.895649
- **Archive Date:** 2026-06-20
- **Deprecation Deadline:** 2026-08-20
- **Maintainer:** @mbaetiong

