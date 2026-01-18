# Agent Integration Guide

> **Version:** 1.0.0
> **Created:** 2026-01-18
> **Purpose:** Guide for integrating and using custom AI agents

---

## Overview

This guide explains how to use the 8 production-ready custom AI agents in the Aries-Serpent/_codex_ repository.

---

## Available Agents

### 1. CI Testing Agent
**Directory:** `.github/agents/ci-testing-agent/`
**Purpose:** Debug and fix CI/CD pipeline issues, test failures, and build problems

**Usage:**
```
@copilot use ci-testing-agent to diagnose the failing workflow
```

### 2. Security Audit Agent
**Directory:** `.github/agents/security-scan-agent/`
**Purpose:** CVE monitoring, vulnerability scanning, security audits

**Usage:**
```
@copilot use security-audit-agent to scan for vulnerabilities
```

### 3. Test Coverage Agent
**Directory:** `.github/agents/test-coverage-enforcer/`
**Purpose:** Identify coverage gaps, generate tests, enforce thresholds

**Usage:**
```
@copilot use test-coverage-agent to analyze uncovered modules
```

### 4. Performance Monitor Agent
**Directory:** `.github/agents/performance-monitor-agent/`
**Purpose:** Benchmark tracking, regression detection, performance analysis

**Usage:**
```
@copilot use performance-monitor-agent to check for regressions
```

### 5. Doc Freshness Checker
**Directory:** `.github/agents/documentation-agent/`
**Purpose:** Documentation validation, freshness checks, link verification

**Usage:**
```
@copilot use doc-freshness-checker to validate documentation
```

### 6. Flaky Test Agent
**Directory:** `.github/agents/flaky-triage-agent/`
**Purpose:** Detect flaky tests, track reliability, quarantine unreliable tests

**Usage:**
```
@copilot use flaky-test-agent to identify flaky tests
```

### 7. Dependency Vulnerability Scanner
**Directory:** `.github/agents/dependency-conflict-resolver/`
**Purpose:** Scan dependencies for vulnerabilities, suggest updates

**Usage:**
```
@copilot use dependency-vulnerability-scanner to check dependencies
```

### 8. Workflow CI Fixer
**Directory:** `.github/agents/ci-optimizer-agent/`
**Purpose:** Fix GitHub Actions workflow issues, optimize pipelines

**Usage:**
```
@copilot use workflow-ci-fixer to fix the workflow syntax error
```

---

## Agent Configuration

Each agent has configuration files in its directory:

```
.github/agents/<agent-name>/
├── README.md           # Agent documentation
├── config.yml          # Agent configuration
├── prompts/            # Agent prompts
└── tests/              # Agent tests
```

---

## Calling Agents from GitHub Copilot

### Direct Invocation
```
@copilot Execute the ci-testing-agent to diagnose build failure
```

### With Parameters
```
@copilot Use test-coverage-agent to:
1. Analyze src/codex/ directory
2. Generate 20+ tests for uncovered modules
3. Target 95% coverage
```

### Chained Execution
```
@copilot Execute in sequence:
1. security-audit-agent - scan for vulnerabilities
2. dependency-vulnerability-scanner - check dependencies
3. workflow-ci-fixer - fix any CI issues
```

---

## Agent Functional Tests

All agents are validated by comprehensive functional tests:

**Test File:** `tests/agents/test_custom_agent_functional.py`
**Tests:** 173 passing
**Verification Commit:** 671a954

### Running Agent Tests
```bash
pytest tests/agents/test_custom_agent_functional.py -v
```

---

## Adding New Agents

### 1. Create Agent Directory
```bash
mkdir -p .github/agents/new-agent-name/
```

### 2. Add Configuration
```yaml
# .github/agents/new-agent-name/config.yml
name: new-agent-name
version: 1.0.0
description: Agent purpose
capabilities:
  - capability1
  - capability2
```

### 3. Add README
```markdown
# New Agent Name
Description of the agent...
```

### 4. Add Tests
```python
# tests/agents/test_new_agent.py
def test_new_agent_exists():
    assert Path(".github/agents/new-agent-name").exists()
```

### 5. Update Agent Registry
Add entry to `.github/agents/AGENT_REGISTRY.yaml`

---

## Best Practices

1. **Always verify agent output** - Agents may make mistakes
2. **Use specific prompts** - The more context, the better results
3. **Chain agents for complex tasks** - Multiple agents can work together
4. **Review changes before committing** - AI Agency Policy compliance
5. **Document agent usage** - Track which agents were used for what

---

## Troubleshooting

### Agent Not Found
Verify agent directory exists:
```bash
ls -la .github/agents/
```

### Agent Tests Failing
Run with verbose output:
```bash
pytest tests/agents/test_custom_agent_functional.py -v --tb=long
```

### Agent Not Responding
Check agent configuration:
```bash
cat .github/agents/<agent-name>/config.yml
```

---

## Related Documentation

- [Agent Specifications](.codex/agents/CUSTOM_AGENT_SPECIFICATIONS.md)
- [Agent Enhancements](.codex/agents/AGENT_ENHANCEMENTS_PHASES_11_18.md)
- [Agent Registry](.github/agents/AGENT_REGISTRY.md)
- [Agent Ecosystem Map](.github/agents/AGENT_ECOSYSTEM_MAP.md)
