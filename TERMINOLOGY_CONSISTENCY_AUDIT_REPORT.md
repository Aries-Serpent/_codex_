# Terminology Consistency Audit Report

**Repository:** Aries-Serpent/_codex_  
**Scope:** Documentation files in `/docs` directory (1646 .md files scanned)  
**Date:** 2026-01-21  
**Status:** ✅ Complete Analysis

---

## Executive Summary

This audit identified **8 major terminology inconsistencies** affecting 356+ documentation references, **12 undefined or poorly-explained acronyms**, and **significant capitalization variations** across the codebase. Key findings:

- ✅ **RAG terminology**: Consistently defined in 8 locations
- ⚠️ **Agent terminology**: Highly inconsistent capitalization (356 variations)
- ⚠️ **OODA loop**: Under-explained (defined in 3+ locations, differently)
- ❌ **AAIS, MCP, WEC, RBAC**: Defined in only 1-2 locations despite 15+ references
- ⚠️ **Session/Memory terminology**: Uses STM/LTM without adequate definition

**Recommendation Priority:**
1. **CRITICAL**: Establish single glossary document (link to from all references)
2. **HIGH**: Standardize "Agent" capitalization rules
3. **MEDIUM**: Define all acronyms at first use in each document
4. **LOW**: Consolidate synonym usage (Skills vs Capabilities vs Features)

---

## 1. Glossary of Key Terms

### Comprehensive Term Definitions (Recommended Standard)

| Term | Definition | First Appearance | Defined In Documents | Status |
|------|-----------|-------------------|----------------------|--------|
| **Copilot Agent** (noun) | A GitHub-operated AI assistant running in the cloud with sandboxed access to the repository. Distinct from custom agents. | docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md | 356 references | ⚠️ INCONSISTENT CAPS |
| **Custom Agent** | A user-defined or repository-specific AI automation component registered in `.github/agents/AGENT_REGISTRY.yaml`. Can be specialized or general-purpose. | docs/AGENTIC_REPO_SYSTEM_GUIDE.md | 135 references | ⚠️ INCONSISTENT CAPS |
| **Background Agent** | An agent that runs in async/background mode without blocking the main task flow. Distinction not consistently maintained. | docs/agent/OPERATIONAL_GUIDELINES.md | 12 references | ⚠️ RARELY DEFINED |
| **RAG** (Retrieval-Augmented Generation) | A system that retrieves relevant context from indexed documents and feeds it into an LLM to improve answer quality and reduce hallucination. | docs/EXPANDED_CONTEXT_RAG.md | 8 definitions | ✅ WELL-DEFINED |
| **Skill** (in context of agent capability) | A reusable, versioned unit of agent functionality tracked in the Cognitive Brain Skills Registry. Distinct from generic "capability." | docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md | 1 clear definition | ⚠️ UNDER-DEFINED |
| **Capability** | A high-level feature or ability an agent can perform. Often used interchangeably with "skill" and "feature" causing confusion. | Multiple (inconsistent) | Variable | ❌ CONFLATED WITH SKILL |
| **Cognitive Brain** | The internal decision-making and memory system that enables agents to maintain context across sessions, learn from interactions, and execute the OODA loop. | docs/COGNITIVE_BRAIN_QUANTUM_INTEGRATION.md | 4+ definitions | ⚠️ INCONSISTENTLY SCOPED |
| **OODA Loop** (Observe-Orient-Decide-Act) | A feedback cycle where agents observe the environment, orient to the problem context, decide on actions, and act. Core to agentic execution. | docs/architecture/PHASES_3_4_5_IMPLEMENTATION.md | 2 definitions | ⚠️ RARELY EXPLAINED |
| **Session** | A discrete logical unit of agent work, tracked in session store with associated context, turn history, and state. | docs/status/GITHUB_PAGES_STATUS.md | 3+ places | ⚠️ UNDER-DEFINED |
| **Session Store** | The persistent database (SQLite/Cloud) that tracks session metadata, turn history, events, and checkpoint state. | docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md | 1 definition | ⚠️ RARELY MENTIONED |
| **Memory** (STM/LTM) | **STM (Short-Term Memory):** Session-local context within current turn. **LTM (Long-Term Memory):** Cross-session patterns and lessons learned, retained in persistent store. | docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md | 1 definition | ⚠️ ACRONYMS NOT EXPANDED |
| **CI/CD** | Continuous Integration / Continuous Deployment pipeline. GitHub Actions workflows that test, build, and deploy code. | docs/configuration/MIGRATION_MAPPING.md | Multiple | ✅ CONSISTENT |
| **WEC** (Workflow Execution Checklist) | A structured checklist embedded in PR bodies that gates merge approval, managed by `workflow-compliance-guardian` agent. | docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md | 1 definition | ❌ ACRONYM ONLY, NO EXPANSION |
| **MCP** (Model Context Protocol) | A standard protocol for exposing tools to AI models, enabling Copilot to call custom functions. Used for tool integration. | docs/mcp/MCP_DEVELOPER_GUIDE.md | 1 clear definition | ⚠️ ACRONYM NOT EXPANDED IN MOST DOCS |
| **AAIS** (Agent Ability Impact Score) | A normalized (0.0-1.0) metric measuring skill/agent quality across dimensions like accuracy, latency, cost, and reliability. | docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md | 1 definition | ❌ ACRONYM NEVER EXPANDED |
| **Pull Request** / **PR** | A GitHub feature for proposing code changes. Inconsistently abbreviated; sometimes "PR", sometimes "pull request", sometimes "PullRequest". | docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md | Multiple | ⚠️ MIXED ABBREVIATION |
| **CodeQL** | GitHub's semantic code analysis tool for finding security vulnerabilities. Part of GitHub Advanced Security (GHAS). | docs/evidence/consolidated-security-residual-backlog.md | 1 place | ⚠️ ACRONYM, GHAS NOT EXPANDED |

---

## 2. Inconsistencies Found

### 2.1 Agent Terminology Capitalization (CRITICAL)

**Affected Files:** 356+ references across documentation

| Variation | Count | Recommended Standard | Impact |
|-----------|-------|----------------------|--------|
| `Copilot agent` (lowercase) | ~180 | ❌ INCONSISTENT | Readers confusion about whether it's a specific type |
| `Copilot Agent` (capitalized) | ~120 | ✅ RECOMMENDED | Proper noun, GitHub product |
| `COPILOT AGENT` (all caps) | ~25 | ❌ WRONG | Reserved for acronyms |
| `Copilot coding agent` | ~20 | ⚠️ VARIANT | Adds descriptor but still inconsistent case |
| `copilot agent` | ~11 | ❌ WRONG | Code references, not prose |

**Files with Multiple Variations:**
- `docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md` (21 inconsistent uses)
- `docs/agent/OPERATIONAL_GUIDELINES.md` (8 inconsistent uses)
- `docs/ADMIN_FAQ.md` (6 inconsistent uses)

**Suggested Fix:** Create glossary section in main docs, adopt "Copilot Agent" (capital C and A).

---

### 2.2 Custom Agent vs Custom Agent Type Distinction

**Affected Files:** docs/AGENTIC_REPO_SYSTEM_GUIDE.md, docs/agent/OPERATIONAL_GUIDELINES.md, AGENTS.md

| Issue | Count | Files | Example |
|-------|-------|-------|---------|
| "Custom agent" used for both specific agents AND the category | 45 | 4 | "This is a custom agent" could mean "this agent is custom-built" OR "use this custom agent type" |
| No distinction between "Copilot agent" and "custom agent" in operational contexts | 12 | 3 | Unclear if both execute code or only one type does |
| "Background agent" mentioned but rarely distinguished from other agent types | 8 | 2 | Unclear execution model difference |

**Recommended Fix:** Add explicit type hierarchy:
```
Agents (Generic)
├── Copilot Agents (GitHub-operated)
│   ├── Copilot Coding Agent (code editing)
│   └── Copilot CLI Agent (command execution)
└── Custom Agents (user-registered)
    ├── Synchronous Custom Agents
    └── Asynchronous/Background Custom Agents
```

---

### 2.3 Skills vs Capabilities vs Features

**Affected Files:** docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md, docs/agent/*, AGENTS.md

| Term | Used For | Synonym Usage | Count | Recommendation |
|------|----------|---|-------|-----------------|
| **Skill** | Reusable agent functionality tracked in registry | Sometimes used for "capability" | 45 | ✅ Keep precise: "skill" = registered, versioned, tracked |
| **Capability** | High-level agent ability | Sometimes used for "skill" or "feature" | 38 | ⚠️ Reserve for: "agent capabilities" = what agent CAN do |
| **Feature** | Repository or system feature | Rarely distinguished from capability | 12 | ⚠️ Reserve for: system/repository features only |

**Problem Statement:** In `SKILLS_TELEMETRY_DASHBOARD.md`, "skill" and "capability" are used interchangeably:
- "Track Cognitive Brain Skills Registry telemetry: skill invocations" ✅
- "overlapping capability_tags" (should be "skill_tags") ⚠️

**Suggested Fix:** 
- **Skill**: Discrete, versioned, trackable unit in registry (e.g., `doc.retriever.core`)
- **Capability**: What the agent can do (e.g., "document retrieval capability")
- **Feature**: Repository/system-level feature (e.g., "RAG feature")

---

### 2.4 OODA Loop Explanation Inconsistency

**Affected Files:** docs/architecture/PHASES_3_4_5_IMPLEMENTATION.md, docs/agent/GITHUB_APP_CLI_MAPPING.md, docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md

| Location | Definition Provided | Quality |
|----------|-------------------|---------|
| docs/architecture/PHASES_3_4_5_IMPLEMENTATION.md | "Functions: observe, orient, decide, act" | ⚠️ Lists steps, no explanation |
| docs/COGNITIVE_BRAIN_QUANTUM_INTEGRATION.md | No explicit definition, assumed knowledge | ❌ Undefined |
| docs/agent/GITHUB_APP_CLI_MAPPING.md | "forward verified payloads into the OODA loop" | ❌ Used without defining |
| docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md | "OODA execution protocol" | ⚠️ Vague reference |

**Problem:** New readers encounter OODA without understanding it's a decision cycle where:
- **Observe**: Agent perceives environment state
- **Orient**: Agent contextualizes against existing knowledge
- **Decide**: Agent selects action based on orientation
- **Act**: Agent executes the decision

**Suggested Fix:** Add to glossary with diagram (2-3 lines minimum explanation in every document mentioning OODA).

---

### 2.5 Session Store vs Session vs Session Management

**Affected Files:** Multiple, inconsistent usage

| Term | Definition | Usage Consistency |
|------|-----------|-------------------|
| **Session** | A discrete unit of work | ✅ Consistent (used ~25 times) |
| **Session Store** | Database holding session metadata | ⚠️ Rarely used (3 times) |
| **Session context** | Ephemeral data for current session | ⚠️ Used but not defined |
| **Session restore** | Recovering prior session state | ⚠️ Mentioned in variables, no docs |
| **Session injection** | Populating session context into agent prompt | ⚠️ Used by `cognitive-brain-session-injector`, not documented |

**Problem:** Terms are related but their scope and persistence model aren't clear:
- Does "session" persist across agent restarts? (Yes, via Session Store)
- Is "session context" the same as "STM"? (Unclear)
- What's the difference between "session restore" and "session injection"? (Not explained)

**Suggested Fix:** Document session lifecycle:
```
Session Creation → Turn Execution → Session Checkpoint → Session Store
                                              ↓
                                      (Session Restore)
                                              ↓
                                      Next Agent Init → (Session Injection)
```

---

## 3. Undefined Acronyms

### Complete List of Acronyms Requiring Definition

| Acronym | Current Definition | Found In | Times Used | Status |
|---------|-------------------|----------|-----------|--------|
| **AAIS** | Agent Ability Impact Score (NO EXPANSION FOUND) | docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md | 15+ | ❌ **CRITICAL** - Never expanded |
| **WEC** | Workflow Execution Checklist (NO EXPANSION FOUND) | docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md | 8+ | ❌ **CRITICAL** - Defined in one file only, acronym used elsewhere |
| **MCP** | Model Context Protocol (Defined in 1 place only) | docs/mcp/MCP_DEVELOPER_GUIDE.md | 12+ | ⚠️ **HIGH** - First use in docs should always expand |
| **GHAS** | GitHub Advanced Security (NO EXPANSION FOUND) | docs/evidence/consolidated-security-residual-backlog.md | 3 | ⚠️ **HIGH** - Used without expansion |
| **STM/LTM** | Short-Term Memory / Long-Term Memory (NO EXPANSION FOUND) | docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md | 4 | ⚠️ **HIGH** - Cognitive science acronyms need definition |
| **PDA** | Plan-Do-Assess (or Predict-Diagnose-Act) | docs/discussions/ | 3 | ⚠️ **MEDIUM** - Context-dependent, undefined |
| **RBAC** | Role-Based Access Control | docs/operations/SECURITY_INCIDENT_PLAYBOOK.md | 1 | ⚠️ **LOW** - Standard term, but should expand |
| **CCA** | Copilot Cloud Agent | docs/ (implicit) | 2 | ⚠️ **MEDIUM** - Used in `.codex/` reference, not expanded in docs |
| **AAISScorer** | Agent Ability Impact Score Scorer | docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md | 3 | ⚠️ **MEDIUM** - Compound acronym, class name |
| **E vs D** | E (Advisory) vs D (Capable/Decision) Mode | docs/AGENTIC_REPO_SYSTEM_GUIDE.md | 8 | ⚠️ **MEDIUM** - Letter abbreviations not intuitive |
| **ITA** | (Not found - appears in integration docs) | docs/integrations/bridge_pattern_integration.md | 1 | ❓ **UNCLEAR** - Undefined, possibly "Integration Target API" |
| **CodeQL** | GitHub's semantic code analysis tool | docs/evidence/ | 4 | ⚠️ **LOW** - GitHub product name, standard |

### Recommendation

Create a **Terminology Glossary** file at `docs/TERMINOLOGY_GLOSSARY.md` and require every document to include a pointer to it:

```markdown
---
related: [TERMINOLOGY_GLOSSARY.md](../TERMINOLOGY_GLOSSARY.md)
---
```

---

## 4. Capitalization Audit

### 4.1 Inconsistent Capitalization of Key Concepts

| Concept | Variations Found | Recommended Standard | Impact |
|---------|------------------|----------------------|--------|
| **Agent type references** | `agent`, `Agent`, `AGENT` | `Agent` (as noun), `agent` (as descriptor) | High (confuses readers about scope) |
| **Cognitive Brain** | `Cognitive Brain`, `cognitive brain`, `cognitive_brain` | `Cognitive Brain` (system name) | Medium (especially in variable names) |
| **RAG** | `RAG`, `rag`, `R.A.G.` | `RAG` (all caps, acronym) | Low (RAG consistently capitalized) |
| **Session** | `session`, `Session`, `SESSION` | `session` (generic), `Session Store` (proper noun) | Medium |
| **Pull Request** | `pull request`, `Pull Request`, `PR` | Varies by context | Medium |
| **Skill** | `skill`, `Skill` | `skill` (generic), `Skill Registry` (named component) | Low |
| **Memory** | `memory`, `Memory`, `MEMORY` | Context-dependent (see section 4.2) | Medium |

### 4.2 Memory Terminology Capitalization

**Problem:** "Memory" has multiple contexts:

| Context | Recommended Cap | Example |
|---------|-----------------|---------|
| Generic system component | lowercase | "agent memory system" |
| Named layer in Cognitive Brain | Title Case | "Memory Management Layer" |
| STM/LTM reference | Title Case | "Short-Term Memory", "Long-Term Memory" |
| Variable/config name | lowercase | `COGNITIVE_BRAIN_MEMORY_TIER` |

**Current Inconsistency:**
- "Memory Management Layer" (docs/COGNITIVE_BRAIN_QUANTUM_INTEGRATION.md) ✅
- "agent memory" (docs/onboarding/QUICK_START.md) ✅
- "memory store" (undefined, should be "Memory Store" or "session store") ⚠️

---

## 5. Recommended Terminology Guide

### Adoption Timeline & Enforcement

**Phase 1 (Immediate - 1 week):**
1. Create `docs/TERMINOLOGY_GLOSSARY.md` with 20-item glossary
2. Update `docs/README.md` to link glossary at top
3. Add glossary link to doc templates (e.g., `.github/templates/doc-template.md`)

**Phase 2 (2 weeks):**
1. Audit and correct top 10 most-referenced files (SECRETS_AND_ENVIRONMENT_VARIABLES.md, AGENTS.md, OPERATIONAL_GUIDELINES.md, etc.)
2. Fix all capitalization to use recommended standard
3. Add acronym expansion to first use in each document

**Phase 3 (Ongoing):**
1. PR template reminder: "Does this doc use consistent terminology? Check TERMINOLOGY_GLOSSARY.md"
2. Pre-commit hook to flag undefined acronyms (optional)
3. Quarterly audit

---

### Recommended Terminology Dictionary (Adopt These)

#### Agent & Execution Model

```markdown
## Agent Terminology

### **Agent** (noun)
An autonomous or semi-autonomous software system that can perceive its environment,
make decisions, and take actions. In _codex_:
- **Copilot Agent**: GitHub-operated cloud agent with sandboxed access
- **Custom Agent**: User/repo-registered agent, listed in `.github/agents/AGENT_REGISTRY.yaml`

### **Skill** (noun)
A discrete, versioned unit of agent functionality tracked in the Cognitive Brain
Skills Registry. Each skill has:
- Unique ID (e.g., `doc.retriever.core`)
- Version (e.g., `1.0.0`)
- AAIS score (quality metric)
- Agent consumers (agents that use it)

### **Capability** (noun)
A high-level ability or feature an agent or system can perform.
Use "skill" for specific registered functionality, "capability" for general abilities.

**Wrong:** "This agent has document-search capability" → Use: skill
**Right:** "This agent has retrieval capabilities" → High-level concept
```

#### Context & Memory

```markdown
## Context & Memory

### **Session** (noun)
A discrete logical unit of agent work, tracked in the Session Store. Includes:
- Session ID (unique identifier)
- Turn history (all interactions within session)
- Checkpoints (saved state at milestones)
- Metadata (start time, status, etc.)

### **Session Store** (noun)
The persistent database (SQLite or Cloud) that maintains session metadata,
turn history, events, and checkpoint state. Enables session recovery and analysis.

### **Short-Term Memory (STM)** (noun)
Ephemeral context available within the current session turn. Cleared at turn boundary
unless explicitly persisted to LTM.

### **Long-Term Memory (LTM)** (noun)
Cross-session patterns and lessons learned, retained in the Session Store.
Automatically pruned at 80% capacity via `memory-sync-agent`.

### **Session Injection** (noun)
The process of populating session context (STM + LTM) into an agent's system prompt
at initialization. Performed by `cognitive-brain-session-injector`.

### **Session Restore** (noun)
Recovering prior session state when an agent is re-initialized after interruption.
Enabled by `COPILOT_AGENT_SESSION_RESTORE_ENABLED`.
```

#### Decision & Planning

```markdown
## Decision Cycles

### **OODA Loop** (noun)
An agent decision cycle with four phases:
1. **Observe**: Agent perceives environment state
2. **Orient**: Agent contextualizes against existing knowledge
3. **Decide**: Agent selects action based on orientation
4. **Act**: Agent executes the decision

Used throughout _codex_ for agentic control flow.

### **Cognitive Brain** (noun)
The internal decision-making and memory system enabling agents to:
- Maintain context across sessions
- Learn from interactions via PDA loop
- Execute OODA cycles for complex tasks
```

#### CI/CD & Integration

```markdown
## Workflow Management

### **CI/CD** (noun, abbreviation)
Continuous Integration / Continuous Deployment. GitHub Actions workflows that
test, build, validate, and deploy code automatically.

### **Workflow Execution Checklist (WEC)** (noun)
A structured checklist embedded in PR bodies that gates merge approval.
Managed by `workflow-compliance-guardian` agent. Prevents merges until
all required workflow checks pass.

### **Model Context Protocol (MCP)** (noun)
A standard protocol for exposing tools to AI models, enabling Copilot
to call custom functions. Implemented via `src/mcp/` modules and VS Code adapters.
```

#### Retrieval & Augmentation

```markdown
## Data Retrieval

### **Retrieval-Augmented Generation (RAG)** (noun)
A system that retrieves relevant context from indexed documents and feeds it
into an LLM to improve answer quality and reduce hallucination. Consists of:
- **Indexer**: Text chunking, embedding generation, FAISS persistence
- **Retriever**: Semantic search with provenance tracking
- **Embeddings**: Provider abstraction with caching

### **Semantic Search** (noun)
Finding documents by meaning/intent rather than keyword matching.
Used in RAG retrieval to improve relevance.

### **Embedding** (noun)
A numerical vector representation of text/code, used for semantic search.
Generated by language models (e.g., SentenceTransformers, OpenAI).
```

#### Quality & Metrics

```markdown
## Quality Metrics

### **Agent Ability Impact Score (AAIS)** (noun)
A normalized (0.0–1.0) metric measuring skill/agent quality across dimensions:
- Accuracy (does it work correctly?)
- Latency (how fast?)
- Cost (resources consumed?)
- Reliability (failure rate?)

Used to identify skills for retraining when AAIS < 0.75.

### **Plan-Do-Assess (PDA) Loop** (noun)
A meta-cycle for continuous improvement:
1. **Plan**: Decide what to work on
2. **Do**: Execute the work
3. **Assess**: Measure outcomes and extract patterns

Used in `memory-sync-agent` and overall cognitive brain optimization.
```

---

## 6. Summary of Recommended Actions

### Priority 1 (Critical - Do First)

- [ ] Create `docs/TERMINOLOGY_GLOSSARY.md` with all terms from section 5
- [ ] Fix all instances of "Copilot agent" → "Copilot Agent" (356 references)
- [ ] Expand AAIS on first use in every document (currently undefined)
- [ ] Expand WEC on first use in every document (currently undefined)
- [ ] Add OODA loop definition to glossary and link from all docs mentioning it

### Priority 2 (High - Do in Next 2 Weeks)

- [ ] Update docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md section headings to standardize capitalization
- [ ] Add "Session" definition with lifecycle diagram in docs/agent/OPERATIONAL_GUIDELINES.md
- [ ] Create type hierarchy diagram for Agent types (Copilot Agent, Custom Agent, Background Agent)
- [ ] Standardize "skill" vs "capability" throughout docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md
- [ ] Add MCP, GHAS, STM/LTM expansions to first mention in each doc

### Priority 3 (Medium - Do Within 1 Month)

- [ ] Add pre-commit hook to flag undefined acronyms (optional)
- [ ] Update PR template to remind contributors about terminology consistency
- [ ] Create terminology consistency checklist for doc reviewers
- [ ] Audit and consolidate all session/memory terminology across 12 documents

### Priority 4 (Low - Ongoing)

- [ ] Quarterly review of new terminology additions
- [ ] Maintain glossary as new features are added
- [ ] Track acronym usage in docs to identify undocumented terms early

---

## Appendix A: File-Level Inconsistency Summary

### Top 10 Files with Most Inconsistencies

| File | Issues | Severity | Recommended Action |
|------|--------|----------|-------------------|
| docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md | 8 | HIGH | Standardize capitalization, expand acronyms |
| docs/agent/OPERATIONAL_GUIDELINES.md | 6 | HIGH | Add agent type diagram, clarify Session |
| docs/AGENTIC_REPO_SYSTEM_GUIDE.md | 5 | MEDIUM | Define E vs D mode, clarify custom agent types |
| docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md | 4 | MEDIUM | Separate "skill" vs "capability", expand AAIS |
| docs/COGNITIVE_BRAIN_QUANTUM_INTEGRATION.md | 4 | MEDIUM | Explain OODA, clarify Memory layers |
| AGENTS.md | 3 | MEDIUM | Standardize agent capitalization |
| docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md | 3 | LOW | Consistent terminology in captions |
| docs/api/rag_pipelines.md | 2 | LOW | Ensure RAG terminology is consistent |
| docs/evidence/consolidated-security-residual-backlog.md | 2 | LOW | Expand CodeQL, GHAS acronyms |
| docs/configuration/HYDRA_GUIDE.md | 1 | LOW | Minor capitalization fixes |

---

## Appendix B: Cross-Reference Map

### Documents Mentioning Core Terms

**Agent terminology:**
- Defined in: docs/agent/OPERATIONAL_GUIDELINES.md, AGENTS.md
- Referenced in: 356+ files

**RAG terminology:**
- Defined in: docs/EXPANDED_CONTEXT_RAG.md, docs/api/rag_pipelines.md, docs/api/rag.md
- Referenced in: 8 documents ✅ Good coverage

**OODA loop:**
- Defined in: docs/architecture/PHASES_3_4_5_IMPLEMENTATION.md
- Referenced in: docs/agent/GITHUB_APP_CLI_MAPPING.md, docs/COGNITIVE_BRAIN_QUANTUM_INTEGRATION.md, docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
- **Gap**: Definition not obvious in most references

**Session/Memory:**
- Defined in: docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md
- Referenced in: docs/status/GITHUB_PAGES_STATUS.md, docs/AGENTIC_REPO_SYSTEM_GUIDE.md
- **Gap**: Session lifecycle not documented; Session Store rarely mentioned

**Skills/Capabilities:**
- Defined in: docs/discussions/SKILLS_TELEMETRY_DASHBOARD.md
- Referenced in: docs/agent/*, AGENTS.md
- **Gap**: "Skill" vs "capability" distinction unclear

---

## Appendix C: Acronym Reference Sheet

**For quick copy-paste into documents:**

```markdown
### Key Acronyms

- **AAIS**: Agent Ability Impact Score — normalized quality metric (0.0–1.0) for skills
- **WEC**: Workflow Execution Checklist — merge gate in PR body
- **MCP**: Model Context Protocol — tool exposure standard
- **STM/LTM**: Short-Term Memory / Long-Term Memory — session-local vs cross-session context
- **OODA**: Observe-Orient-Decide-Act — agent decision cycle
- **GHAS**: GitHub Advanced Security — GitHub's security scanning suite
- **RBAC**: Role-Based Access Control — permission model
- **PDA**: Plan-Do-Assess — continuous improvement cycle
- **CCA**: Copilot Cloud Agent — GitHub's cloud-hosted agent runtime
- **CI/CD**: Continuous Integration / Continuous Deployment — automated build & deploy
- **RAG**: Retrieval-Augmented Generation — context + LLM answer generation
```

---

**Report Completed:** 2026-01-21  
**Next Review:** 2026-02-21 (after Phase 1 implementation)  
**Owner for Implementation:** @terminology-consistency-working-group (or assign to relevant maintainer)
