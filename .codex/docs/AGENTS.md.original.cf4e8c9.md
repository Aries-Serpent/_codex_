# AGENTS.md - AI Agent Documentation

> **Status:** ✅ UP-TO-DATE (Previous Cycle-12-26)  
> **Repository:** Aries-Serpent/_codex_ (ID: 1040037790)  
> **Genesis Status:** Phase 1 Complete - Pre-Token Setup

---

## 🎯 Quick Start

**New AI Agent?** Read this first (5 min orientation):

1. **Repository Status:** Pre-Genesis (Template Mode - SAFE_MODE active)
2. **Your Role:** Advisory only - No autonomous actions yet
3. **Key Constraints:** See [.codex/guardrails.md](.codex/guardrails.md)
4. **Operational Guide:** See [docs/agent/OPERATIONAL_GUIDELINES.md](docs/agent/OPERATIONAL_GUIDELINES.md)

---

## 📊 Current Repository State

```
Repository: Aries-Serpent/_codex_
Repository ID: 1040037790
Language: Python (78.3%), Markdown (18%), Shell (2.5%)
Tests: 1500+ | Coverage: 72% | Security: 0 vulnerabilities

Genesis Protocol Status:
├─ Phase 1: ✅ COMPLETE (Pre-token templates created)
├─ Phase 2: 🔄 PLANNED (Advanced automation)
└─ Phase 3: ⏳ FUTURE (ML-based decisions)

Agent Authority: PRE-GENESIS (Template Mode)
├─ autonomous_actions_enabled: false
├─ SAFE_MODE: True
└─ Workflows: Disabled (if: false guard)
```

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
2. **[docs/agent/OPERATIONAL_GUIDELINES.md](docs/agent/OPERATIONAL_GUIDELINES.md)** - Complete framework (15 min)
3. **[docs/admin/GENESIS_SETUP_GUIDE.md](docs/admin/GENESIS_SETUP_GUIDE.md)** - Genesis process (10 min)
4. **[README.md](README.md)** - Repository overview (5 min)

### Reference Documents

- [scripts/AUTONOMOUS_AGENT_README.md](scripts/AUTONOMOUS_AGENT_README.md) - Agent setup
- [docs/admin/CONTINUATION_ROADMAP.md](docs/admin/CONTINUATION_ROADMAP.md) - Future plans
- [.codex/change_log.md](.codex/change_log.md) - Audit trail

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

**Version:** 2.0.0  
**Last Updated:** Previous Cycle-12-26T08:35:00Z  
**Status:** ✅ UP-TO-DATE  
**Next Review:** After Phase 2 completion

---

**Complete Documentation:**
- Full details: [docs/agent/OPERATIONAL_GUIDELINES.md](docs/agent/OPERATIONAL_GUIDELINES.md)
- Genesis guide: [docs/admin/GENESIS_SETUP_GUIDE.md](docs/admin/GENESIS_SETUP_GUIDE.md)
- Future plans: [docs/admin/CONTINUATION_ROADMAP.md](docs/admin/CONTINUATION_ROADMAP.md)

**Questions?** Create an issue or contact @mbaetiong
