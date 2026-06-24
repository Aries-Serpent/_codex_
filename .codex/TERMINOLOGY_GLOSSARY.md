# Terminology Glossary & Standardization Guide

**Version:** 1.0.0  
**Last Updated:** 2026-06-22  
**Status:** Active  

---

## Purpose

This glossary establishes standardized terminology across the _codex_ repository to ensure clarity, consistency, and reduced ambiguity in documentation, code comments, and communications.

---

## Core Terminology Standards

### 1. Agent (AI/Automation)

**Standard Form:** `agent` (lowercase) in general context  
**Capitalized:** `Agent` only when starting sentences or in formal titles

**Definition:** An autonomous AI system (typically a Copilot custom agent) that can execute tasks, make decisions, and coordinate with other systems.

**Current Usage:** 6,796 lowercase + 4,190 capitalized = 10,986 total occurrences  
**Recommended:** Standardize to lowercase `agent` except in:
- Sentence starts
- Proper names (e.g., "CI Testing Agent", "unified-coverage-agent")
- Titles and headings

**Examples:**
- ✅ "The agent scanned the repository..."
- ✅ "The CI Testing Agent executed the task..."
- ✅ "Agent Accountability Report"
- ❌ "The Agent scanned the repository..." (mid-sentence capitalization)

**Related Terms:**
- `autonomous agent` - agent that operates without human intervention
- `custom agent` - specialized agent for a specific domain
- `agentic workflow` - workflow orchestrated by agents
- `agent registry` - centralized registry of all agents

---

### 2. Workflow (GitHub Actions)

**Standard Form:** `workflow` (lowercase) in general context  
**Capitalized:** `Workflow` when starting sentences or in formal names

**Definition:** An automated process defined in GitHub Actions (`.github/workflows/`) that executes tasks in response to repository events.

**Current Usage:** 3,995 lowercase + 1,938 capitalized = 5,933 total occurrences  
**Recommended:** Standardize to lowercase `workflow` except in:
- Sentence starts
- Proper workflow names with hyphens (e.g., "workflow-compliance-gate.yml")
- Titles and headings

**Examples:**
- ✅ "The workflow runs tests on every PR..."
- ✅ "The CI Testing Workflow validates code..."
- ✅ "Workflow Compliance Gate"
- ❌ "The Workflow runs tests..." (mid-sentence capitalization)

**Related Terms:**
- `workflow run` - single execution of a workflow
- `workflow dispatch` - manual trigger of a workflow
- `workflow state` - current execution state
- `workflow artifact` - output of a workflow run

---

### 3. Pull Request (PR)

**Standard Forms:**
- **First reference:** `pull request` (full form)
- **Subsequent references:** `PR` (uppercase acronym)
- **In URLs/technical contexts:** `pull-request` (hyphenated)

**Definition:** A request to merge changes from one branch into another, typically for code review and validation.

**Current Usage:** 7,519 PR + 91 pull-request + 51 "pull request" = 7,661 total  
**Recommended:** Standardize to:
- Use `PR` (uppercase) for the acronym in all contexts
- Use "pull request" (full form) in first mention
- Use `pull-request` only in technical identifiers or JSON keys

**Examples:**
- ✅ "This pull request adds new features. The PR must pass all checks..."
- ✅ "Go to the PR's conversation tab..."
- ✅ `pr_number: 5057` (technical context)
- ❌ "This pull-request adds features..." (avoid hyphen in text)
- ❌ "The pull request runs tests..." (should say PR in subsequent mentions)

**Related Terms:**
- `PR comment` - comment on a PR
- `PR check` - required status check on a PR
- `PR review` - code review on a PR
- `draft PR` - PR marked as not ready for merge

---

### 4. Repository

**Standard Form:** `repository` (lowercase) in general context  
**Capitalized:** `Repository` only when starting sentences or in formal names

**Definition:** The git repository containing the _codex_ project and all its code, documentation, workflows, and configuration.

**Current Usage:** 1,093 lowercase + 637 capitalized = 1,730 total occurrences  
**Recommended:** Standardize to lowercase `repository` with exceptions:
- Sentence starts
- Formal names (e.g., "Aries-Serpent/_codex_ Repository")
- Proper repository identifiers

**Examples:**
- ✅ "The repository contains 145 agents..."
- ✅ "This Repository Policy requires..."
- ✅ "Aries-Serpent/_codex_ Repository"
- ❌ "The Repository contains..." (mid-sentence)

**Shortcuts:**
- `repo` (lowercase) - acceptable shorthand for "repository"

**Related Terms:**
- `repository root` - top-level directory
- `repository structure` - organization of files/directories
- `repository variable` - GitHub repository-scoped secret variable
- `repository policy` - rules governing repository behavior

---

### 5. Component

**Standard Form:** `component` (lowercase) in general context  
**Capitalized:** `Component` only when starting sentences or in formal module names

**Definition:** A modular, reusable part of the system with a well-defined interface and responsibility.

**Current Usage:** 257 lowercase + 316 capitalized = 573 total occurrences  
**Recommended:** Standardize to lowercase `component` with exceptions:
- Sentence starts
- Names of specific components (e.g., "Query Engine Component", "Cache Layer Component")
- Section headings and titles

**Examples:**
- ✅ "The cache component manages memory..."
- ✅ "The Cache Component is responsible for..."
- ✅ "Cache Layer Component Architecture"
- ❌ "The Component manages memory..." (mid-sentence capitalization)

**Related Terms:**
- `component interface` - public API of a component
- `component integration` - connecting components together
- `component lifecycle` - initialization, execution, cleanup phases
- `cross-component` - spanning multiple components

---

### 6. Task

**Standard Form:** `task` (lowercase) in general context  
**Capitalized:** `Task` only when starting sentences or in formal names

**Definition:** A unit of work that needs to be completed, typically with inputs, execution, and outputs.

**Current Usage:** 622 lowercase + 926 capitalized = 1,548 total occurrences  
**Recommended:** Standardize to lowercase `task` with exceptions:
- Sentence starts
- Formal task names and identifiers
- Headings and titles

**Examples:**
- ✅ "Each task has a status field..."
- ✅ "This Task requires approval..."
- ✅ "High-Priority Task"
- ❌ "This Task processes data..." (mid-sentence)

**Related Terms:**
- `task status` - current state (pending, running, complete, failed)
- `task queue` - collection of tasks waiting to execute
- `task dependency` - one task depends on another
- `task result` - output of task execution

---

## Context-Specific Guidance

### GitHub Copilot Context
In Copilot-specific documentation:
- Use `agent` for the AI system performing actions
- Use `coding agent` or `Copilot agent` for the GitHub Copilot CLI agent
- Use `custom agent` for specialized agents in `.github/agents/`
- Use "Agent Accountability Report" (formal title) for session tracking

### CI/CD Context
In CI/CD and workflow documentation:
- Use `workflow` for GitHub Actions workflow files
- Use `workflow run` for individual executions
- Use `workflow dispatch` for manual triggers
- Use `workflow file` when referencing the YAML file

### Code Context
In Python code comments and docstrings:
- Use `agent` consistently (lowercase)
- Use `workflow_id`, `workflow_name` in variable names (snake_case)
- Use `repository` or `repo` in comments
- Use `task_status`, `task_queue` in snake_case

### Documentation Context
In Markdown documentation:
- Use standard forms above
- Use code formatting for identifiers: `` `agent` ``, `` `workflow` ``
- Use consistent capitalization in headers

---

## Problematic Patterns to Avoid

| Pattern | Issue | Fix |
|---------|-------|-----|
| "The Agent performed..." | Mid-sentence capitalization | "The agent performed..." |
| "workflow dispatch" in headings | Inconsistent capitalization | "Workflow Dispatch" |
| "using pull-requests" | Incorrect hyphenation | "using pull requests" or "using PRs" |
| "Repository structure" mid-sentence | Unnecessary capitalization | "repository structure" |
| "The task completed" in code comments | Missing consistency | "`task` completed" or lowercase |
| "Component Interface" mid-text | Inconsistent capitalization | "component interface" |

---

## Automated Enforcement

These patterns are automatically checked by:

1. **Markdownlint Rules** (`.markdownlintrc`)
   - Terminology pattern matching
   - Capitalization consistency checks
   - Hyphenation validation

2. **Pre-commit Hooks**
   - Terminology checker (runs on `.md` files)
   - Capitalization validator
   - Consistency auditor

3. **CI/CD Gates**
   - Documentation validation workflow
   - Terminology consistency checks
   - Automated reporting

---

## Glossary Terms by Category

### Agent Ecosystem
- `agent` - Primary AI system
- `autonomous agent` - Agent without human intervention
- `custom agent` - Domain-specific agent
- `agent registry` - Central registry
- `agent accountability` - Tracking and reporting
- `agentic` - Adjective form (agentic workflow, agentic system)

### Workflow & Execution
- `workflow` - GitHub Actions automation
- `workflow run` - Single execution
- `workflow dispatch` - Manual trigger
- `workflow file` - YAML definition
- `workflow artifact` - Output/results
- `workflow state` - Current execution state

### Code & Repository
- `repository` - Primary git repository
- `branch` - Git branch
- `commit` - Git commit
- `pull request` / `PR` - Change request
- `code review` - Review process

### Components & Architecture
- `component` - Modular system part
- `module` - Python/code module
- `service` - Externally-facing component
- `integration` - System combination
- `interface` - Component boundary

### Work & Tasks
- `task` - Unit of work
- `task status` - State tracking
- `task queue` - Work collection
- `job` - CI/CD job (use in Actions context)
- `step` - Workflow step

---

## Migration Path

### Phase 1: Documentation (Current)
- Update CONTRIBUTING.md with terminology section
- Create this glossary
- Add markdownlint rules

### Phase 2: Code Enforcement
- Implement pre-commit terminology checker
- Add CI/CD validation
- Generate automated reports

### Phase 3: Implementation
- Batch update 20+ key documentation files
- Update code comments for consistency
- Publish migration guide

### Phase 4: Monitoring
- Track compliance metrics
- Report improvements
- Iterate on rules

---

## Current Terminology Usage Summary

| Term | Lowercase | Capitalized | Total | Recommendation |
|------|-----------|------------|-------|---|
| agent | 6,796 | 4,190 | 10,986 | Standardize to lowercase |
| workflow | 3,995 | 1,938 | 5,933 | Standardize to lowercase |
| PR | 7,519 | - | 7,519 | Keep as uppercase |
| repository | 1,093 | 637 | 1,730 | Standardize to lowercase |
| task | 622 | 926 | 1,548 | Standardize to lowercase |
| component | 257 | 316 | 573 | Standardize to lowercase |
| pull request | 51 | - | 51 | Keep full form |
| pull-request | 91 | - | 91 | Use only in technical contexts |

**Total Terminology Occurrences:** ~37,937 across all documentation

---

## Questions & Discussions

For questions about terminology decisions:
- Check this glossary first
- Review CONTRIBUTING.md Terminology section
- Open a discussion in the repository
- See `terminology-consistency-agent` for automated enforcement

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-22 | Initial comprehensive glossary and standards |

---

**Related Documentation:**
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Terminology section
- [.markdownlintrc](../.markdownlintrc) - Automated rules
- [terminology-consistency-agent](./.github/agents/terminology-consistency-agent.md) - Enforcement agent
