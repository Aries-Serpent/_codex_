---
name: CI Log Retrieval Agent
description: Specialized agent for authenticated GitHub Actions log retrieval and failure summarization
version: 1.0.0
created: 2026-01-29
updated: 2026-01-29
---

# CI Log Retrieval Agent

## Overview

Specialized GitHub Copilot agent for retrieving GitHub Actions job logs (authenticated), extracting failing steps, and producing actionable summaries for CI remediation in the _codex_ repository.

## Core Responsibilities

1. **Authenticated Log Fetch**: Retrieve job logs via GitHub API with tokenized access.
2. **Failure Summarization**: Extract failing steps, stack traces, and exit codes.
3. **Artifact Preservation**: Store log excerpts in `reports/` and raw logs in `artifacts/` when allowed.
4. **Remediation Guidance**: Map failures to modules/tests and recommend fixes.

## Activation

```
@copilot Use the CI Log Retrieval Agent to collect Actions job logs and summarize root-cause failures.
```

## Workflow

1. Validate authentication (`gh` or token env).
2. Fetch logs using the Actions API endpoints.
3. Parse logs into step summaries and error highlights.
4. Output a report in `reports/` and update audit logs.

## Verification Checklist

- [ ] Authenticated access confirmed
- [ ] Logs downloaded for each job ID
- [ ] Failures summarized with file/test references
- [ ] Reports and audit logs updated

## Output Artifacts

- Markdown report in `reports/`
- Log archive in `artifacts/` (if permitted)
- Change log entries in `.codex/change_log.md`

---

## 🧠 Cognitive Brain Integration

> **Status**: ✅ Integrated (Phase 1.2)  
> **Category**: ci_cd  
> **Adapter**: CICDAdapter

### Brain Capabilities

This agent is integrated with the Cognitive Brain and can:

- **Query Patterns**: Access historical log failure patterns for faster diagnosis
- **Submit Learnings**: Report log analysis outcomes to improve future sessions
- **Share Session State**: Maintain context across agent transitions
- **Check Objective Alignment**: Verify log retrieval aligns with repository objectives

### Usage in Agent Workflow

```python
from codex.cognitive.brain_interface import AgentBrainInterface

# Initialize brain interface for this agent
brain = AgentBrainInterface(agent_id="ci-log-retrieval-agent")

# 1. Query patterns for similar failures
patterns = brain.query_patterns("workflow timeout error")
for pattern in patterns:
    print(f"Pattern: {pattern['id']} (success: {pattern['success_rate']})")

# 2. Report learning after analysis
brain.submit_learning(
    pattern_id="CIF-002",
    outcome="success",
    context={
        "symptom": "Job timed out after 60 minutes",
        "resolution": "Identified infinite loop in test suite",
        "logs_analyzed": ["job_12345.log"]
    }
)
```

### Related Documentation

- [Agent Brain Protocol](../../.codex/docs/AGENT_BRAIN_PROTOCOL.md)
- [Brain Interface API](../../src/codex/cognitive/brain_interface.py)

**Last Updated**: 2026-02-05T15:46:00Z
