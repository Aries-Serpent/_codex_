# Documentation Index

**Last Updated**: 2024-12-11  
**Total Files**: 693+ markdown files  
**Purpose**: Comprehensive index of all documentation in the repository

---

## Quick Navigation

- [Active Documentation](#active-documentation)
- [Archived Documentation](#archived-documentation)
- [Technical Documentation](#technical-documentation)
- [Guides and Tutorials](#guides-and-tutorials)
- [Status Reports](#status-reports)
- [Architecture and Design](#architecture-and-design)

---

## Active Documentation

### Core Documentation

| Document | Purpose | Last Updated | Status |
|----------|---------|--------------|--------|
| [README.md](../README.md) | Project overview | Current | ✅ Active |
| [AGENTS.md](../AGENTS.md) | Agent operations playbook | 2024-12-10 | ✅ Active |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines | Current | ✅ Active |
| [SECURITY.md](../SECURITY.md) | Security policy | Current | ✅ Active |
| [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Community standards | Current | ✅ Active |
| [GOVERNANCE.md](../GOVERNANCE.md) | Governance model | Current | ✅ Active |

### Recent Additions (2024-12-11)

| Document | Size | Purpose |
|----------|------|---------|
| [COMPREHENSIVE_GAP_ANALYSIS.md](archive/COMPREHENSIVE_GAP_ANALYSIS.md) | 15.3KB | Gap analysis with priority matrix |
| [PR_FINAL_SUMMARY.md](archive/pr_reports/PR_FINAL_SUMMARY.md) | 10.6KB | PR summary with metrics |
| [CONTRIBUTOR_ONBOARDING.md](./CONTRIBUTOR_ONBOARDING.md) | 12.3KB | Onboarding guide |
| [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) | 32KB | Comprehensive architecture reference |

### Agent Infrastructure (64KB+)

| Document | Size | Category |
|----------|------|----------|
| [agents/prompts/debugging/test-failure-debugging.md](../agents/prompts/debugging/test-failure-debugging.md) | 4.8KB | Debugging |
| [agents/prompts/debugging/resolve-merge-conflicts.md](../agents/prompts/debugging/resolve-merge-conflicts.md) | 6.3KB | Debugging |
| [agents/prompts/debugging/performance-optimization.md](../agents/prompts/debugging/performance-optimization.md) | 7.0KB | Debugging |
| [agents/prompts/debugging/security-remediation.md](../agents/prompts/debugging/security-remediation.md) | 8.6KB | Debugging |
| [agents/prompts/audit/run-full-audit.md](../agents/prompts/audit/run-full-audit.md) | - | Audit |
| [agents/prompts/audit/check-regressions.md](../agents/prompts/audit/check-regressions.md) | - | Audit |
| [agents/prompts/deployment/pre-release-deployment.md](../agents/prompts/deployment/pre-release-deployment.md) | - | Deployment |
| [agents/prompts/documentation/generate-wiki.md](../agents/prompts/documentation/generate-wiki.md) | - | Documentation |
| [agents/prompts/organization/repository-cleanup.md](../agents/prompts/organization/repository-cleanup.md) | - | Organization |
| [agents/prompts/self-healing/feedback-loop.md](../agents/prompts/self-healing/feedback-loop.md) | - | Self-Healing |

---

## Archived Documentation

### Historical Documents (archive/historical_docs_20251210/)

**Status**: Archived as of 2024-12-10  
**Reason**: Information preserved in more recent documents or no longer relevant  
**Count**: 50+ documents

| Category | Count | Examples |
|----------|-------|----------|
| Status Updates | 15+ | STATUS_UPDATE_AUDIT_REPORT.md, WORK_SUMMARY.md |
| Implementation Reports | 10+ | IMPLEMENTATION_COMPLETE.md, MSP_IMPLEMENTATION_SUMMARY.md |
| Phase Completions | 8+ | PHASE_6_INTEGRATION_COMPLETE.md, PHASE_C_SUMMARY.md |
| Gap Analyses | 5+ | GAP_REMEDIATION_STATUS.md, MLOPS_GAP_ANALYSIS_AND_ROADMAP.md |
| Achievement Reports | 5+ | ACHIEVEMENT_99_PERCENT.md, FINAL_STATUS_100_PERCENT.md |

**Full Index**: See [workbench/INDEX.md](../workbench/INDEX.md)

### Removed Documents (archive/removed/)

**Status**: Removed from active use  
**Count**: 10+ documents  
**Examples**:
- Codex_Questions.md
- STATUS_UPDATE (various dates)
- CODEBASE_AUDIT (historical versions)

---

## Technical Documentation

### Architecture

| Document | Purpose | Diagrams |
|----------|---------|----------|
| [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) | Comprehensive architecture reference | Yes (Mermaid) |
| [agents/prompts/ARCHITECTURE.md](../agents/prompts/ARCHITECTURE.md) | System architecture diagrams | Yes (Mermaid) |
| [agents/ORCHESTRATION.md](../agents/ORCHESTRATION.md) | Physics-inspired orchestration | Yes |

### API Documentation

| Document | Purpose |
|----------|---------|
| [agents/prompts/API_MODEL.md](../agents/prompts/API_MODEL.md) | API model documentation |
| [agents/codex_client/README.md](../agents/codex_client/README.md) | Codex client API |

### Configuration

| Document | Purpose |
|----------|---------|
| [.codex/README.md](../.codex/README.md) | Codex environment setup |
| [training/config.py](../training/config.py) | Training configuration (code) |
| [pyproject.toml](../pyproject.toml) | Project configuration |

---

## Guides and Tutorials

### User Guides

| Guide | Audience | Updated |
|-------|----------|---------|
| [CONTRIBUTOR_ONBOARDING.md](./CONTRIBUTOR_ONBOARDING.md) | New contributors | 2024-12-11 |
| [MCP_DEVELOPER_GUIDE.md](mcp/MCP_DEVELOPER_GUIDE.md) | MCP developers | Current |
| [USAGE_GUIDE.md](../USAGE_GUIDE.md) | End users | Current |

### Agent Guides

| Guide | Purpose | Updated |
|-------|---------|---------|
| [AGENTS.md](../AGENTS.md) | Comprehensive agent guide | 2024-12-10 |
| [agents/TOKENIZED_WORKFLOWS.md](../agents/TOKENIZED_WORKFLOWS.md) | Workflow tokens | Current |
| [agents/prompts/README.md](../agents/prompts/README.md) | Prompts library | 2024-12-11 |

### Integration Guides

| Guide | Focus |
|-------|-------|
| [HAR_INTEGRATION_PLAN.md](./HAR_INTEGRATION_PLAN.md) | HAR file integration |
| [COPILOT_PROMPT_100_PERCENT.md](../COPILOT_PROMPT_100_PERCENT.md) | Copilot integration |
| [MCP_100_PERCENT_ROADMAP.md](../MCP_100_PERCENT_ROADMAP.md) | MCP integration roadmap |

---

## Status Reports

### Active Reports

| Report | Purpose | Date |
|--------|---------|------|
| [COMPREHENSIVE_GAP_ANALYSIS.md](archive/COMPREHENSIVE_GAP_ANALYSIS.md) | Current gaps and priorities | 2024-12-11 |
| [PR_FINAL_SUMMARY.md](archive/pr_reports/PR_FINAL_SUMMARY.md) | Latest PR summary | 2024-12-11 |
| [codex_gap_registry.yaml](../codex_gap_registry.yaml) | Gap tracking (YAML) | 2024-12-11 |

### Audit Reports

| Report | Focus | Location |
|--------|-------|----------|
| Audit Artifacts | Capability tracking | [audit_artifacts/](../audit_artifacts/) |
| Reports | Generated reports | [reports/](../reports/) |
| Stub Analysis | Code stubs | [reports/stub_analysis.md](../reports/stub_analysis.md) |

---

## Architecture and Design

### Design Documents

| Document | Focus | Diagrams |
|----------|-------|----------|
| [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) | System architecture | Yes |
| [LEVEL_4_MLOPS_ASSESSMENT.md](../LEVEL_4_MLOPS_ASSESSMENT.md) | MLOps maturity | No |
| [T1_SOLUTION.md](../T1_SOLUTION.md) | T1 solution design | No |

### Implementation Plans

| Plan | Status | Location |
|------|--------|----------|
| HAR Integration | Planned | [HAR_INTEGRATION_PLAN.md](./HAR_INTEGRATION_PLAN.md) |
| MCP Roadmap | Complete | [MCP_100_PERCENT_ROADMAP.md](../MCP_100_PERCENT_ROADMAP.md) |
| Gap Remediation | Complete | [COMPREHENSIVE_GAP_ANALYSIS.md](archive/COMPREHENSIVE_GAP_ANALYSIS.md) |

---

## Documentation by Topic

### MLOps and Training

- `LEVEL_4_MLOPS_ASSESSMENT.md` - MLOps maturity assessment
- `training/` - Training documentation
- `audit_artifacts/` - Audit results
- `MATURITY_REMAINING_WORK.md` - Maturity improvements

### Testing and Quality

- `tests/` - Test documentation
- `reports/stub_analysis.md` - Stub analysis
- `.codex/` - Quality checks
- `COMPREHENSIVE_GAP_ANALYSIS.md` - Gap analysis

### Security and Compliance

- `SECURITY.md` - Security policy
- `security_allowlist.json` - Approved exceptions
- `agents/prompts/debugging/security-remediation.md` - Security guide
- `.bandit.yaml` - Bandit configuration

### Deployment and Operations

- `deploy/` - Deployment manifests
- `Dockerfile*` - Container images
- `docker-compose.yml` - Local orchestration
- `.github/workflows/` - CI/CD (gated)

### AI Agent Integration

- `agents/` - Agent infrastructure
- `agents/prompts/` - Prompt library
- `AGENTS.md` - Agent operations
- `agents/TOKENIZED_WORKFLOWS.md` - Workflow tokens

---

## Documentation Statistics

### By Category

| Category | Count | Percentage |
|----------|-------|------------|
| Active Documentation | ~100 | 14% |
| Archived Documentation | ~50 | 7% |
| Agent Prompts | ~10 | 1% |
| Test Documentation | ~500 | 72% |
| Other | ~33 | 5% |

### By Status

| Status | Count | Notes |
|--------|-------|-------|
| ✅ Active | ~600 | Current and maintained |
| 📦 Archived | ~50 | Preserved for reference |
| ❌ Removed | ~10 | Obsolete, in archive/removed/ |
| 🆕 Recent (< 1 week) | ~10 | Added in recent PRs |

### By Size

| Size Range | Count | Examples |
|------------|-------|----------|
| < 1KB | ~300 | Small test docs, stubs |
| 1-10KB | ~300 | Standard documentation |
| 10-50KB | ~80 | Comprehensive guides |
| > 50KB | ~13 | Major reference documents |

---

## Finding Documentation

### By Task

**I want to...**

- **Contribute code**: Start with [CONTRIBUTOR_ONBOARDING.md](./CONTRIBUTOR_ONBOARDING.md)
- **Use AI Agents**: See [AGENTS.md](../AGENTS.md) and [agents/prompts/](../agents/prompts/)
- **Understand architecture**: Read [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md)
- **Debug issues**: Check [agents/prompts/debugging/](../agents/prompts/debugging/)
- **Deploy the system**: See [deploy/](../deploy/) and [Dockerfile*](../Dockerfile)
- **Run tests**: See [tests/](../tests/) and [CONTRIBUTOR_ONBOARDING.md](./CONTRIBUTOR_ONBOARDING.md)
- **Understand MLOps**: Read [LEVEL_4_MLOPS_ASSESSMENT.md](../LEVEL_4_MLOPS_ASSESSMENT.md)
- **Report security issues**: Follow [SECURITY.md](../SECURITY.md)

### By Audience

**I am a...**

- **New Contributor**: [CONTRIBUTOR_ONBOARDING.md](./CONTRIBUTOR_ONBOARDING.md), [CONTRIBUTING.md](../CONTRIBUTING.md)
- **AI Agent**: [AGENTS.md](../AGENTS.md), [agents/prompts/](../agents/prompts/), [agents/TOKENIZED_WORKFLOWS.md](../agents/TOKENIZED_WORKFLOWS.md)
- **Developer-Architect**: [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md), [COMPREHENSIVE_GAP_ANALYSIS.md](archive/COMPREHENSIVE_GAP_ANALYSIS.md)
- **DevOps Engineer**: [deploy/](../deploy/), [.github/workflows/](../.github/workflows/), [docker-compose.yml](../docker-compose.yml)
- **Security Researcher**: [SECURITY.md](../SECURITY.md), [agents/prompts/debugging/security-remediation.md](../agents/prompts/debugging/security-remediation.md)
- **ML Engineer**: [training/](../training/), [LEVEL_4_MLOPS_ASSESSMENT.md](../LEVEL_4_MLOPS_ASSESSMENT.md)

---

## Maintenance Guidelines

### For Contributors

**Adding New Documentation**:
1. Create file in appropriate directory
2. Add entry to this index
3. Follow naming conventions (lowercase-with-hyphens or UPPERCASE_WITH_UNDERSCORES)
4. Include metadata (date, author, purpose)
5. Link from related documents

**Updating Documentation**:
1. Update the document
2. Update "Last Updated" metadata
3. Update this index if location/status changes
4. Notify relevant stakeholders

**Archiving Documentation**:
1. Move to appropriate archive/ subdirectory
2. Update this index with archived status
3. Add redirect in original location if applicable
4. Update dependent documents

### For AI Agents

**Finding Documentation**:
```python
from pathlib import Path

# List all markdown files
docs = list(Path('.').rglob('*.md'))

# Filter by category
active_docs = [d for d in docs if 'archive' not in str(d)]
archived_docs = [d for d in docs if 'archive' in str(d)]

# Search by topic
def find_docs(topic):
    return [d for d in docs if topic.lower() in d.name.lower()]
```

**Using Index Programmatically**:
- Parse this markdown file
- Extract links and metadata
- Build documentation graph
- Identify gaps or inconsistencies

---

## Related Resources

### External Links

- **Repository**: https://github.com/Aries-Serpent/_codex_
- **Issues**: https://github.com/Aries-Serpent/_codex_/issues
- **Pull Requests**: https://github.com/Aries-Serpent/_codex_/pulls
- **Wiki**: (Generate via agents/prompts/documentation/generate-wiki.md)

### Internal Tools

- **Workflow Navigator**: `agents/workflow_navigator.py`
- **Audit Runner**: `scripts/space_traversal/audit_runner.py`
- **Documentation Generator**: `agents/prompts/documentation/`

---

## Changelog

| Date | Change | Impact |
|------|--------|--------|
| 2024-12-11 | Created comprehensive index | Initial version |
| 2024-12-11 | Added architecture blueprint | 32KB new doc |
| 2024-12-11 | Added debugging guides | 26KB new docs |
| 2024-12-11 | Added contributor onboarding | 12KB new doc |
| 2024-12-10 | Archived historical documents | 50+ files moved |

---

**Index Version**: 1.0.0  
**Maintainer**: Repository owners  
**Last Full Audit**: 2024-12-11  
**Next Review**: 2026-01-11 (quarterly)
