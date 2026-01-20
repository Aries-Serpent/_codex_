# AGENTS.md - AI Agent Documentation

> **Status:** ✅ UP-TO-DATE (2026-01-16 - IP-005 Security Updates Complete)  
> **Repository:** Aries-Serpent/_codex_ (ID: 1040037790)  
> **Genesis Status:** Phase 1 Complete - Pre-Token Setup
> **Workflows:** 49 active (100% parity, 19 consolidated)
> **Security:** ✅ 26 vulnerabilities fixed (IP-005 Complete)
> 
> **📚 Full Documentation:** For complete operational details including audit pipelines, Python ingestion,  
> security utilities, and troubleshooting procedures, see [.codex/docs/AGENTS.md.original.cf4e8c9.md](.codex/docs/AGENTS.md.original.cf4e8c9.md)

---

## 🎯 Quick Start

**New AI Agent?** Read this first (5 min orientation):

0. **🚨 CRITICAL: Read [AI Codebase Agency Policy](.codex/CODEBASE_AGENCY_POLICY.md)** - MANDATORY
1. **Repository Status:** Pre-Genesis (Template Mode - SAFE_MODE active)
2. **Your Role:** Advisory only - No autonomous actions yet
3. **Key Constraints:** See [.codex/guardrails.md](.codex/guardrails.md)
4. **Operational Guide:** See [docs/agent/OPERATIONAL_GUIDELINES.md](docs/agent/OPERATIONAL_GUIDELINES.md)

### ⚠️ AI Codebase Agency Policy (MANDATORY)

**ALL AI agents MUST address ALL issues discovered in the codebase, regardless of whether they are pre-existing or introduced by current work.**

**Prohibited Statements:**
- ❌ "This is not related to my PR"
- ❌ "These are pre-existing issues"
- ❌ "My PR only adds files to X"

**Required Actions:**
- ✅ Fix ALL CI/CD failures
- ✅ Fix ALL broken documentation links
- ✅ Fix ALL linting/type errors
- ✅ Leave codebase better than found

**Full Policy:** [.codex/CODEBASE_AGENCY_POLICY.md](.codex/CODEBASE_AGENCY_POLICY.md)

---

## 📊 Current Repository State

```
Repository: Aries-Serpent/_codex_
Repository ID: 1040037790
Language: Python (78.3%), Markdown (18%), Shell (2.5%)
Tests: 1500+ | Coverage: 72% | Security: 0 vulnerabilities (48 fixed)

Genesis Protocol Status:
├─ Phase 1: ✅ COMPLETE (Full implementation with API preserved)
├─ Phase 2: 🔄 READY (Awaiting human admin activation)
└─ Phase 3: ⏳ FUTURE (Full autonomous operations)

Agent Implementation: FULL API MODE
├─ autonomous_actions_enabled: false (safety guard active)
├─ scripts/autonomous_agent.py: Full implementation with complete API
├─ Test Suite: 23/23 tests passing ✅
└─ Workflows: Enabled (if: true - Genesis activated)
```

**Note on autonomous_agent.py:**
The autonomous agent implementation has been restored to its full version (pre-Genesis)
to maintain API compatibility with the test suite. All classes (AutonomousAgent,
CodeHealthSensor, ActionProposer) and enums (HealthStatus, ActionType, DecisionLevel)
are available for testing and development purposes.

---

## 🤖 Agent Profile

| Attribute | Value |
|-----------|-------|
| Agent Name | ai_org_repo_admin |
| Version | 0.0.0-template |
| Authority Level | Pre-Genesis (Advisory Only) |
| Operational Mode | SAFE_MODE enabled |

---

## 📚 Essential Documentation

### Must-Read Documents

1. **[.codex/guardrails.md](.codex/guardrails.md)** - Operational constraints (5 min)
2. **[.github/TEMPORARY_FILES_POLICY.md](.github/TEMPORARY_FILES_POLICY.md)** - 🚨 CRITICAL: Never use /tmp/ for important files (2 min)
3. **[docs/agent/OPERATIONAL_GUIDELINES.md](docs/agent/OPERATIONAL_GUIDELINES.md)** - Complete framework (15 min)
4. **[docs/admin/GENESIS_SETUP_GUIDE.md](docs/admin/GENESIS_SETUP_GUIDE.md)** - Genesis process (10 min)
5. **[README.md](README.md)** - Repository overview (5 min)
6. **[.codex/docs/COGNITIVE_BRAIN_COMPLETE_DOCS.md](.codex/docs/COGNITIVE_BRAIN_COMPLETE_DOCS.md)** - 🆕 Cognitive Brain System (20 min)

### Reference Documents

- [scripts/AUTONOMOUS_AGENT_README.md](scripts/AUTONOMOUS_AGENT_README.md) - Agent setup
- [docs/admin/CONTINUATION_ROADMAP.md](docs/admin/CONTINUATION_ROADMAP.md) - Future plans
- [.codex/change_log.md](.codex/change_log.md) - Audit trail
- [.github/workflow-archive/PARITY_CHECKLIST.md](.github/workflow-archive/PARITY_CHECKLIST.md) - Workflow consolidation (100% parity) 🆕
- [.github/workflow-archive/ARTIFACT_CATALOG.md](.github/workflow-archive/ARTIFACT_CATALOG.md) - GitHub Actions artifacts guide 🆕
- [.codex/plans/cognitive_brain_phase_implementation.md](.codex/plans/cognitive_brain_phase_implementation.md) - Cognitive Brain Phase Plan 🆕
- [scripts/cognitive/](scripts/cognitive/) - Cognitive Brain Scripts (22 files) 🆕

###human Workflow & Artifact Resources (Updated 2025-12-28)

**Workflow Consolidation**:
- **Status**: ✅ COMPLETE (100% parity confirmed)
- **Documentation**: [.github/workflow-archive/PARITY_CHECKLIST.md](.github/workflow-archive/PARITY_CHECKLIST.md)
- **Categories**: 8 of 8 verified (Testing, Docs, Container, Validation, Monitoring, Cache, Duplication, Post-Merge)
- **Patterns**: Monolithic, Distributed, Optimized, Automated consolidations
- **Active Workflows**: 49 (target: 48 - within tolerance)
- **Disabled**: 19 workflows (28.4% reduction)

**Artifact Retrieval for Copilot Sessions**:
- **Catalog**: [.github/workflow-archive/ARTIFACT_CATALOG.md](.github/workflow-archive/ARTIFACT_CATALOG.md)
- **Types**: 20+ artifact types documented
- **Methods**: GitHub CLI, API, Direct access
- **Examples**: Code quality, coverage, audits, tests, health metrics
- **Retention**: 30-180 days depending on type

**Quick Artifact Access**:
```bash
# View catalog
view .github/workflow-archive/ARTIFACT_CATALOG.md

# Download latest artifacts
gh run download --name code-quality-report
gh run download --name audit-results
gh run download --name workflow-trends-12345
```

---

## 🛡️ Safety & Constraints

### Active Safety Guards

**Three-Layer Protection:**
1. ✅ Workflow Guard: `if: false` in genesis-bootstrap.yml
2. ✅ Script Guard: `SAFE_MODE = True` in autonomous_agent.py
3. ✅ Config Guard: `autonomous_actions_enabled: false`

### Operational Constraints

**✅ Allowed (Pre-Genesis):**
- Answer questions about codebase
- Provide recommendations
- Create PRs for human review
- Run validation scripts
- Generate documentation

**❌ Prohibited (Pre-Genesis):**
- Direct commits to any branch
- Workflow execution
- Secret management
- Repository settings changes
- Autonomous code modifications

---

## 🚀 Genesis Protocol

### What is Genesis?

Genesis Protocol establishes AI agent authority through secure initialization:
- **Phase 1** ✅: Template creation (COMPLETE)
- **Phase 2** ⏳: Human admin injects secrets, enables workflows
- **Phase 3** 🔮: Full autonomous operations within guardrails

### Current Status: Pre-Genesis

**Completed:**
- Template files created
- Documentation comprehensive
- Safety guards active
- Ready for human review

**Awaiting:**
- Human admin secret injection
- Workflow enablement
- Genesis validation execution

**See:** [docs/admin/GENESIS_SETUP_GUIDE.md](docs/admin/GENESIS_SETUP_GUIDE.md)

---

## 📂 Repository Navigation

### Key Directories

```
_codex_/
├── .codex/              # Genesis configuration
├── .github/workflows/   # CI/CD (disabled pre-Genesis)
├── docs/
│   ├── admin/          # Human admin docs
│   └── agent/          # AI agent docs
├── scripts/            # Automation scripts
├── src/                # Source code
└── tests/              # Test suite
```

### Quick Navigation

| Need to... | Check... |
|------------|----------|
| Understand constraints | `.codex/guardrails.md` |
| Learn Genesis | `docs/admin/GENESIS_SETUP_GUIDE.md` |
| Agent capabilities | `docs/agent/OPERATIONAL_GUIDELINES.md` |
| Current status | `.codex/change_log.md` |

---

## 🎯 Decision Framework

```
Risk Assessment → Action

LOW RISK (Post-Genesis)
• Documentation → Execute autonomously
• Code formatting → Execute autonomously  
• Testing → Execute autonomously

MEDIUM RISK
• Optimization → Create PR, await approval
• Refactoring → Create PR, await approval
• Dependencies → Create PR, await approval

HIGH RISK
• Security → Escalate immediately
• Configuration → Escalate immediately
• Secrets → Escalate immediately
```

**When in doubt:** Escalate to @mbaetiong

---

## 🚨 Escalation

### When to Escalate

- **Critical:** Security issues, data loss risk
- **High:** Config changes, breaking changes
- **Medium:** Optimizations, refactoring

### How to Escalate

1. Create GitHub issue with [ESCALATION] tag
2. Include: severity, impact, recommendation
3. Assign to @mbaetiong
4. Wait for human response

---

## 📊 Logging

All operations must be logged to:
- `.codex/action_log.ndjson` - Operations log
- `.codex/change_log.md` - Change audit trail
- `.codex/results.md` - Results summary

---

## 🛠️ Tools Available

- `view` - Read files
- `edit` - Modify files
- `create` - Create files
- `grep` - Search content (ripgrep)
- `glob` - Find files by pattern
- `bash` - Execute commands (limited pre-Genesis)

---

## ✅ Best Practices

**Do:**
- ✅ Cite sources and references
- ✅ Explain rationale clearly
- ✅ Document all decisions
- ✅ Validate all changes
- ✅ Respect safety guards

**Don't:**
- ❌ Commit secrets
- ❌ Bypass safety mechanisms
- ❌ Make assumptions
- ❌ Skip documentation
- ❌ Ignore warnings

---

## 🤖 Specialized Agents

The repository includes specialized GitHub Copilot agents designed for specific tasks:

### Available Agents

| Agent | Purpose | Location | Status |
|-------|---------|----------|--------|
| **CI Testing Agent** | Debug CI/CD pipelines, test failures, import errors | [.github/agents/ci-testing-agent.md](.github/agents/ci-testing-agent.md) | ✅ Active |
| **Codex Reviewer** | Code review and quality checks | [.github/agents/codex-reviewer.agent.yml](.github/agents/codex-reviewer.agent.yml) | ✅ Active |
| **Security Agent** | Security vulnerability scanning and fixes | [.github/copilot-security/security_agent.py](.github/copilot-security/security_agent.py) | ✅ Active |
| **QA Walkthrough Agent** | Repository-wide QA walkthrough execution and audit evidence | [.github/agents/qa-walkthrough-agent.md](.github/agents/qa-walkthrough-agent.md) | ✅ Active |
| **Dependency Conflict Agent** | Diagnose pip resolver conflicts and recommend compatible pins | [.github/agents/dependency-conflict-agent.md](.github/agents/dependency-conflict-agent.md) | ✅ Active |

### Using Specialized Agents

Activate specialized agents using the `@copilot` command:

```markdown
@copilot Use the CI Testing Agent to debug the test failure in tests/monitoring/
```

### Creating New Agents

To create a new specialized agent:

1. Create agent file in `.github/agents/[agent-name].md`
2. Follow the template in [.github/agents/README.md](.github/agents/README.md)
3. Document agent capabilities, responsibilities, and activation commands
4. Add agent to the table above
5. Test agent activation and behavior

---

## 📞 Support

**For Agents:**
- Search this documentation
- Check operational guidelines
- Create escalation issue if needed

**For Humans:**
- Critical: @mbaetiong
- General: GitHub Issues
- Features: Discussions

---

## 📝 Document Status

**Version:** 2.1.0  
**Last Updated:** 2025-12-28T12:50:00Z  
**Status:** ✅ UP-TO-DATE (Workflow consolidation & artifact catalog added)  
**Next Review:** After Phase 2 completion

---

**Complete Documentation:**
- Full details: [docs/agent/OPERATIONAL_GUIDELINES.md](docs/agent/OPERATIONAL_GUIDELINES.md)
- Genesis guide: [docs/admin/GENESIS_SETUP_GUIDE.md](docs/admin/GENESIS_SETUP_GUIDE.md)
- Future plans: [docs/admin/CONTINUATION_ROADMAP.md](docs/admin/CONTINUATION_ROADMAP.md)

**Questions?** Create an issue or contact @mbaetiong
