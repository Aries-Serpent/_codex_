# Agent Consolidation Master Matrix

> **Consolidated Master Document** for Codex Agent System  
> **Created**: 2026-07-08  
> **Consolidation Campaign**: Phase 12 WS3  
> **Status**: ✅ Active Master Document

**Consolidated from** 18 source files:
- .codex/archive/deprecated/AGENTS.md (3 copies in root, scripts/, .github/)
- AGENT_CONSOLIDATION_MATRIX.md
- Agent deprecation docs (Google Home, Energy Conversion)
- Agent implementation mappings & designs
- Agent ecosystem catalogs
- Autonomous agent documentation

---

## Table of Contents

1. [Agent Registry & Catalog](#agent-registry--catalog)
2. [Custom Agent Types](#custom-agent-types)
3. [Agent Implementation Mapping](#agent-implementation-mapping)
4. [Deprecated Agents](#deprecated-agents)
5. [Agent Ecosystem Architecture](#agent-ecosystem-architecture)
6. [Agent Integration Guide](#agent-integration-guide)
7. [Quick Reference](#quick-reference)

---

## Agent Registry & Catalog

### Built-in Agent Types

**Standard Agents** (Available via CLI/UI):

1. **explore** - Codebase exploration & research
   - Fast parallel investigation
   - Best for multi-threaded research
   - Uses Haiku model

2. **task** - Command execution with reporting
   - Verbose output on failure
   - Summary on success
   - Best for builds, tests, lints

3. **general-purpose** - Full-capability agent
   - Subprocess with complete toolset
   - Best for complex multi-step tasks
   - Uses Sonnet model

4. **code-review** - High signal-to-noise code review
   - Analyzes diffs/branches
   - Only surfaces important issues
   - Minimizes false positives

5. **research** - Thorough web research
   - GitHub repo searches
   - File fetching & verification
   - Citation-based findings

6. **security-review** - Security-focused analysis
   - 11 vulnerability categories
   - >80% confidence thresholds
   - Severity scoring (CRITICAL/HIGH/MEDIUM/LOW)

### Custom Agent Registry

**Count**: 100+ custom agents deployed  
**Deployment Status**: Phase 12 WS3 consolidation complete

#### Tier 1 Custom Agents (Core Ecosystem)

| Agent | Owner | Status | Model | Integration |
|-------|-------|--------|-------|-------------|
| orchestrator-agent | Skills Master | ✅ Active | Sonnet | AGENT_REGISTRY.yaml |
| skills-master-agent | Codex Core | ✅ Active | Sonnet | Apex knowledge agent |
| cognitive-brain-session-injector | PDA Loop | ✅ Active | Haiku | Session lifecycle mgmt |
| mypy-manager-agent | Type Checker | ✅ Active | Haiku | .mypy_baseline mgmt |

#### Tier 2 Custom Agents (Specialized Domain)

**CI/CD & Testing** (18 agents):
- ci-auto-healer-agent
- ci-testing-agent
- ci-failure-resolution-agent
- ci-emergency-response-agent
- autonomous-test-healer-agent
- test-alignment-fixer-enhanced
- test-coverage-agent (deprecated → unified-coverage-agent)

**Security & Compliance** (12 agents):
- security-audit-agent
- codeql-alert-resolution-agent
- dependency-vulnerability-scanner
- secret-detection-agent
- security-alert-verification-agent

**Code Quality** (15 agents):
- code-analysis-agent
- code-scanning-remediation-agent
- test-enhancement-agent
- fragile-test-guardian
- mutation-testing-agent

**Documentation** (8 agents):
- unified-doc-agent (primary)
- documentation-consolidator (deprecated → unified-doc-agent)
- documentation-quality-agent
- link-validator-agent
- doc-freshness-checker

**Infrastructure & DevOps** (14 agents):
- workflow-ci-fixer
- workflow-health-monitor
- ci-docker-build-healer
- cache-management-agent
- performance-monitor-agent

**Miscellaneous** (33 agents):
- [See detailed list below]

---

## Custom Agent Implementation Mapping

### Agent Activation Patterns

**Pattern 1: Direct Task Invocation**
```bash
@copilot Use [agent-name] for [task]
task agent_type="agent-name" prompt="[instructions]"
```

**Pattern 2: Auto-routing via Orchestrator**
```bash
@copilot Execute [task]  # Routes to appropriate agent
```

**Pattern 3: GitHub Actions Workflow**
```yaml
- name: Run Agent
  uses: ./.github/actions/agent-runner
  with:
    agent: agent-name
    parameters: |
      target: path
      mode: full
```

### Agent Tool Access Matrix

| Agent Type | Bash | View | Edit/Create | Grep | Git | Subprocess |
|------------|------|------|-------------|------|-----|-----------|
| explore | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| task | ✅ | ✅ | ❌ | ✅ | ✅ | ⚠️ |
| general-purpose | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| code-review | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| security-review | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |

---

## Deprecated Agents

### Agent Consolidations (Active → Unified)

| Deprecated | Replacement | Status | Migration |
|-----------|-------------|--------|-----------|
| documentation-consolidator | unified-doc-agent v1.0 | ✅ Merged 2026-06-11 | Use unified-doc-agent |
| coverage-gapfill-agent | unified-coverage-agent | ✅ Merged 2026-05-15 | Use unified-coverage-agent |
| coverage-maintenance-agent | unified-coverage-agent | ✅ Merged 2026-05-15 | Use unified-coverage-agent |
| coverage-roadmap-agent | unified-coverage-agent | ✅ Merged 2026-05-15 | Use unified-coverage-agent |
| test-coverage-agent | unified-coverage-agent | ✅ Merged 2026-05-15 | Use unified-coverage-agent |
| test-coverage-monitor | unified-coverage-agent | ✅ Merged 2026-05-15 | Use unified-coverage-agent |

### Deprecated Agents (Out-of-Scope)

| Agent | Reason | Status | Deprecation Date |
|-------|--------|--------|------------------|
| energy-conversion-agent | Out-of-scope domain (energy systems) | ✅ Archived | 2026-07-01 |
| google-home-script-agent | Out-of-scope domain (smart-home) | ✅ Archived | 2026-07-01 |

**Archive Reference**: See `.codex/archive/deprecated/ENERGY_CONVERSION_AGENT_DEPRECATION.md`, `.codex/archive/deprecated/GOOGLE_HOME_SCRIPT_AGENT_DEPRECATION.md`

---

## Agent Ecosystem Architecture

### Multi-Tier Agent Structure

```
┌─────────────────────────────────────────────────┐
│ User/Frontend Layer                             │
│ (CLI, IDE Extension, Web UI)                    │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│ Copilot CLI / Copilot Coding Agent              │
│ (Central Task Dispatcher)                        │
└──────────────┬──────────────────────────────────┘
               │
      ┌────────┼────────┬─────────┐
      ▼        ▼        ▼         ▼
┌──────────┬──────────┬──────────┬───────────┐
│Tier 1    │Tier 2    │Tier 2    │Tier 3    │
│(Core)    │(Spec.)   │(Custom)  │(Utility) │
│          │          │          │          │
│ Orchest. │CI/CD (18)│Custom    │Log       │
│ Skills   │Security  │Agents    │Retrieval │
│ Cognitive│Docs (8)  │(100+)    │PII       │
│ MyPy     │Code (15) │          │Scrubber  │
│ Session  │Infra(14) │          │          │
│ Injector │Misc (33) │          │          │
└──────────┴──────────┴──────────┴───────────┘
```

### Agent Lifecycle

```
1. DESIGN
   └─→ Create agent prompt & capability tags

2. REGISTER
   └─→ Add to AGENT_REGISTRY.yaml with metadata

3. PUBLISH
   └─→ Make available via CLI/Agent Marketplace

4. EXECUTE
   └─→ Route tasks → Run in subprocess with tools

5. MONITOR
   └─→ Track IQ score, success rate, session logs

6. CONSOLIDATE (if needed)
   └─→ Merge into unified agent (e.g., unified-doc-agent)

7. ARCHIVE (if deprecated)
   └─→ Mark as archived in registry, update docs
```

---

## Agent Integration Guide

### Skills Master Agent Integration

The **Skills Master Agent** is the apex knowledge agent for Codex:

```python
from agents.skills_master import SkillsMaster

skills_master = SkillsMaster()
skills_master.discover()      # Find available skills
skills_master.install()       # Install skill
skills_master.execute()       # Run skill
skills_master.score()         # Rate IQ effectiveness
skills_master.compress()      # Optimize for storage
skills_master.train()         # Train new agents
```

### Cognitive Brain Integration

**Integration Level**: Level 1 (Cognitive Access)

```python
# Topology Manager - Semantic navigation
from scripts.cognitive.topology_manager import TopologyManager

topology = TopologyManager()
relevant_files = topology.find_by_concept("documentation")
optimal_path = topology.find_optimal_path("source", "target")

# Cache Manager - Multi-layer cache intelligence
from scripts.cognitive.cache_manager import CacheIntelligence

cache = CacheIntelligence()
cached_results = cache.query("doc_links_validation")
cache.optimize()  # Get optimization suggestions
```

### Orchestrator Agent Pattern

```yaml
orchestrator:
  function: agent-orchestrator
  inputs:
    - semantic_search: Find relevant agent by capability tags
    - task_analysis: Decompose complex tasks
    - agent_selection: Route to specialist agents
    - result_aggregation: Combine sub-agent outputs
  outputs:
    - execution_result
    - status_report
    - performance_metrics
```

---

## Custom Agent Ecosystem (Full List)

### Tier 1: Core System (5 agents)

1. **orchestrator-agent** - Multi-agent workflow coordination
2. **skills-master-agent** - Apex agent, skill discovery/training
3. **cognitive-brain-session-injector** - Session lifecycle management
4. **mypy-manager-agent** - Type checking & .mypy_baseline management
5. **agent-iq-scoring-gate** - Quality thresholds before deployment

### Tier 2: CI/CD & Testing (18 agents)

1. ci-auto-healer-agent
2. ci-testing-agent
3. ci-failure-resolution-agent
4. ci-emergency-response-agent
5. ci-docker-build-healer
6. ci-importerror-agent
7. ci-log-retrieval-agent
8. ci-optimization-agent
9. ci-parameter-mismatch-healer
10. ci-pattern-guardian
11. ci-resilience-emergency-response-agent
12. ci-triage-pipeline-agent
13. autonomous-test-healer-agent
14. test-alignment-fixer-enhanced
15. test-alignment-fixer
16. test-enhancement-agent
17. test-failure-analyzer-agent
18. self-healing-orchestrator-agent

### Tier 2: Security & Compliance (12 agents)

1. security-audit-agent
2. security-review-agent (built-in)
3. codeql-alert-resolution-agent
4. code-scanning-remediation-agent
5. dependency-vulnerability-scanner
6. dependency-security-review-agent
7. dependency-conflict-agent
8. secret-detection-agent
9. security-alert-verification-agent
10. secret-detection-agent
11. unified-security-scanner
12. owner-approval-guard

### Tier 2: Code Quality (15 agents)

1. code-analysis-agent
2. code-review-agent (built-in)
3. test-pattern-guardian
4. test-coverage-agent (deprecated → unified-coverage-agent)
5. fragile-test-guardian
6. mutation-testing-agent
7. claim-verification-agent
8. json-serialization-expert
9. meta-tensor-validator
10. test-enhancement-agent
11. datetime-modernizer
12. cross-platform-filename-validator
13. terminology-consistency-agent
14. python-312-type-fixer
15. unified-coverage-agent

### Tier 2: Documentation (8 agents)

1. **unified-doc-agent** (primary master)
2. documentation-consolidator (deprecated → unified-doc-agent)
3. documentation-quality-agent
4. documentation-consolidator
5. link-validator-agent
6. doc-freshness-checker
7. doc-refactor-test-agent
8. post-merge-doc-alignment-agent

### Tier 2: Infrastructure & DevOps (14 agents)

1. workflow-ci-fixer
2. workflow-health-monitor
3. workflow-management-agent
4. workflow-optimization-agent
5. workflow-analytics-agent
6. workflow-compliance-guardian
7. cache-management-agent
8. cache-manager-integration
9. performance-monitor-agent
10. performance-regression-detector
11. artifact-monitor-agent
12. ci-health-alert-agent
13. rag-freshness-loop-agent
14. rag-index-manager

### Tier 2: Miscellaneous (33 agents)

1. artifact-monitor-agent
2. branch-divergence-resolution-agent
3. bridge-security-monitor
4. cache-manager-integration
5. claim-verification-agent
6. cognitive-ooda-loop-agent
7. config-migration-assistant
8. config-validator
9. codebase-health-guardian
10. cross-agent-knowledge-graph
11. cross-platform-filename-validator
12. datetime-modernizer
13. github-guru-agent
14. github-pages-manager
15. integration-test-runner
16. json-serialization-expert
17. memory-sync-agent
18. meta-tensor-validator
19. ml-validation-suite-agent
20. msv-dashboard-monitor
21. pii-scrubber
22. policy-coach-agent
23. pr-check-remediation-agent
24. pr-test-infrastructure-fixer
25. pypi-publishing-operations-agent
26. python-architect-agent
27. qa-walkthrough-agent
28. quantum-compliance-tuning-agent
29. rag-meta-tensor-guardian
30. rag-meta-tensor-regression-agent
31. rag-module-management-agent
32. recon-scout-agent
33. reference-updater-agent

---

## Quick Reference

### Find the Right Agent

**Need to fix CI/CD?** → `ci-auto-healer-agent`, `ci-testing-agent`, `workflow-ci-fixer`

**Need security review?** → `security-audit-agent`, `codeql-alert-resolution-agent`

**Need documentation help?** → `unified-doc-agent`, `link-validator-agent`

**Need code quality?** → `code-analysis-agent`, `mutation-testing-agent`, `test-enhancement-agent`

**Need infrastructure?** → `workflow-health-monitor`, `cache-management-agent`, `performance-monitor-agent`

**Need to train an agent?** → `skills-master-agent`

### Agent Command Template

```bash
# Via task tool
task agent_type="agent-name" prompt="[instructions]"

# Via CLI (future)
copilot agent run [agent-name] --prompt "[instructions]"

# Via GitHub Actions
@copilot Use [agent-name] for [task]
```

### Key Documentation Links

- [Custom Agent Token Reference](../agents/CUSTOM_AGENT_TOKEN_QUICK_REFERENCE.md)
- [Agent Ecosystem Map](./.github/agents/AGENT_ECOSYSTEM_MAP.md)
- [Governance Framework](./.codex/GOVERNANCE_POLICY_FRAMEWORK.md)
- [RBAC Policy](./patch_rbac_engine.py)

---

**This document is the authoritative agent registry and consolidation matrix for Codex.**

*Last Updated: 2026-07-08*  
*Consolidation Status: ✅ Complete (18 files merged into unified matrix)*
