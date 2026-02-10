# Agent Operational Guidelines

> Generated: 2026-01-26T20:41:00Z | Author: autonomous-codebase-health-agent
> Status: 🟡 Under Development

## 📋 Overview

This document provides comprehensive operational guidelines for all AI agents working within the `Aries-Serpent/_codex_` repository. These guidelines complement the [AI Codebase Agency Policy](../../../.codex/CODEBASE_AGENCY_POLICY.md) with practical operational procedures.

## 🧠 Agent Categories

### 1. Infrastructure Agents
- **CI Testing Agent**: Test infrastructure and pipeline management
- **Workflow Analytics Agent**: Performance monitoring and optimization
- **Dependency Conflict Agent**: Package dependency resolution

### 2. Quality Assurance Agents
- **QA Walkthrough Agent**: Repository-wide quality audits
- **Coverage Roadmap Agent**: Test coverage improvement
- **Test Alignment Fixer**: Test-code synchronization

### 3. Documentation Agents
- **Documentation Quality Agent**: Documentation validation and improvement
- **Link Validator Agent**: Cross-reference and link validation

### 4. Security Agents
- **Security Agent**: Vulnerability scanning and remediation
- **PII Scrubber**: Privacy compliance validation

## 🔄 Standard Operating Procedures

### Pre-Execution Checklist

- [ ] Read and understand the task requirements
- [ ] Review relevant sections of `.codex/CODEBASE_AGENCY_POLICY.md`
- [ ] Identify affected systems and dependencies
- [ ] Create detailed implementation plan
- [ ] Report initial progress with plan checklist

### Execution Protocol

1. **Plan**: Document all tasks as checklist
2. **Execute**: Implement changes incrementally
3. **Validate**: Run tests and checks after each change
4. **Report**: Use `report_progress` frequently
5. **Review**: Perform 5+ self-review iterations

### Post-Execution Protocol

- [ ] All tests passing
- [ ] No linting errors introduced
- [ ] Documentation updated
- [ ] Change log updated
- [ ] Cognitive brain updated
- [ ] Self-review completed (5+ iterations)
- [ ] Follow-up prompt created (if work incomplete)

## 🎯 Decision Framework

### Risk Assessment Matrix

| Risk Level | Example Actions | Approval Required |
|------------|-----------------|-------------------|
| **Low** | Documentation updates, formatting | No - Execute autonomously |
| **Medium** | Code refactoring, optimization | No - but report changes |
| **High** | Breaking changes, security fixes | Yes - create PR for review |
| **Critical** | Secrets, deployment, data loss | Yes - escalate immediately |

### Authority Levels

1. **Read-Only**: Information gathering, analysis, reporting
2. **Limited Write**: Documentation, tests, non-critical fixes
3. **Full Write**: Code changes, refactoring, optimization
4. **Administrative**: Configuration, secrets, deployment

## 📊 Quality Standards

### Code Quality

- All code must pass linting (ruff, mypy)
- Test coverage must not decrease
- Breaking changes must be documented
- Security vulnerabilities must be addressed

### Documentation Quality

- All public APIs must have docstrings
- Links must be valid (internal and external)
- Examples must be functional
- Metadata must be current

### Testing Standards

- New code requires tests (80%+ coverage)
- Tests must be deterministic
- Tests must be isolated
- Tests must be maintainable

## 🔗 Integration Points

### With GitHub Actions

- Agents can trigger workflows
- Agents can read workflow results
- Agents can create artifacts
- Agents can update workflow files

### With Git Repository

- Agents can create branches
- Agents can commit changes
- Agents can push to remote
- Agents cannot force push or rebase

### With Documentation

- Agents must update change logs
- Agents must maintain cognitive brain
- Agents must document decisions
- Agents must create follow-up prompts

## 🛡️ Safety Guardrails

### Prohibited Actions

- ❌ Committing secrets or credentials
- ❌ Deleting production data
- ❌ Force pushing or rebasing
- ❌ Bypassing security checks
- ❌ Ignoring test failures

### Required Actions

- ✅ Address ALL issues (not just new ones)
- ✅ Follow planning-before-execution protocol
- ✅ Perform 5+ self-review iterations
- ✅ Document all changes
- ✅ Create follow-up prompts for incomplete work

## 📝 Reporting Requirements

### Progress Reports

Use `report_progress` tool to:
- Share initial plan as checklist
- Update after each meaningful unit of work
- Show completed vs remaining tasks
- Commit and push changes

### Change Logs

Update `.codex/change_log.md` with:
- Timestamp and agent identity
- Problem description
- Root cause analysis
- Solution implemented
- Validation results

### Cognitive Brain Updates

Update `.codex/cognitive_brain.md` with:
- Current phase status
- Recent completions
- Active work items
- Health metrics
- Next phase plans

## 🔄 Self-Healing Protocol

### Failure Detection

1. Monitor CI/CD results
2. Analyze error patterns
3. Identify root causes
4. Classify severity (P0-P3)

### Automated Response

- **P0 (Critical)**: Immediate autonomous fix
- **P1 (High)**: Autonomous fix with reporting
- **P2 (Medium)**: Create fix PR for review
- **P3 (Low)**: Document for future work

### Iteration Limits

- Maximum 5 iterations per fix attempt
- Escalate after 3 failed iterations
- Document all attempts
- Provide rollback plan

## 🎓 Learning & Improvement

### Knowledge Capture

- Store successful patterns
- Document failure modes
- Share lessons learned
- Update utility registry

### Continuous Improvement

- Review past decisions
- Optimize workflows
- Enhance automation
- Reduce manual intervention

## 🔗 Related Documentation

- [AI Codebase Agency Policy](../../../.codex/CODEBASE_AGENCY_POLICY.md)
- [Agent Registry](../../agents/AGENT_REGISTRY.md)
- Cognitive Brain
- [Change Log](../../../.codex/change_log.md)

---
*This is a living document maintained by autonomous agents. Last updated: 2026-02-10*
