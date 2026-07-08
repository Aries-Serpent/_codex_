# Terminology Style Guide
**Version:** 1.0.0  
**Date:** 2026-07-08  
**Type:** Documentation Standards  
**Audience:** All contributors  
**Authority:** Phase 12 WS3 Documentation  
**Status:** ✅ Production Ready

---

## 📖 Purpose

This style guide establishes terminology standards for all documentation contributors and agents contributing to the _codex_ repository. It serves as the authoritative reference for consistent language use and terminology choices.

---

## 🎯 Core Principles

1. **Clarity First** - Use terminology that clearly communicates intent
2. **Consistency** - Use same term for same concept across all documents
3. **Precision** - Use specific terms; avoid ambiguous language
4. **Accessibility** - Define specialized terms on first use
5. **Documentation** - Maintain glossary as source of truth

---

## 📚 Quick Reference: What to Use

### Phase/Workstream References
```
CORRECT:  "Phase 12 WS1", "Phase 12 WS2", "Phase 12 WS3"
WRONG:    "Phase 12 Wave 1", "Wave 1", "Phase12 Wave"
CONTEXT:  Use when referring to phase/workstream organization
```

### Agent Terminology
```
CORRECT:  "Copilot Coding Agent", "Custom Agent", "Agent"
WRONG:    "GitHub Agent", "Coding Agent", "Copilot Agent"
CONTEXT:  Copilot agents = "Copilot Coding Agent"; user-defined = "Custom Agent"
```

### ML Decision System
```
CORRECT:  "Strategy Selector", "ML Strategy", "Decision Tree"
WRONG:    "OODA Loop", "Strategy system", "Decision logic"
CONTEXT:  System component = "Strategy Selector"; strategic planning = "ML Strategy"; algorithm = "Decision Tree"
```

### Brain/Cognitive System
```
CORRECT:  "Cognitive Brain", "Cognitive Brain module"
WRONG:    "CB", "Brain module" (without "Cognitive"), "The Brain"
CONTEXT:  Always use full "Cognitive Brain" except in captions/headers where "Brain" is acceptable
```

### Workflow/Execution
```
CORRECT:  "Workflow", "Workflow job"
WRONG:    "Pipeline" (in GitHub Actions context), "Job" (without context)
CONTEXT:  GitHub Actions = "Workflow"; processes = "Workflow"; K8s = "Pipeline"
```

### Governance/Access Control
```
CORRECT:  "Governance", "Governance policy", "RBAC", "Access control"
WRONG:    "Policy" (alone), "Authorization" (without context)
CONTEXT:  System = "Governance"; policies = "Governance policy"; roles = "RBAC"
```

### Process Execution
```
CORRECT:  "Iteration N", "multi-iteration"
WRONG:    "Turn N" (in process context), "multi-turn" (in process context)
CONTEXT:  Process steps = "Iteration"; conversation history = "Turn"
```

---

## 1️⃣ PHASE/WORKSTREAM TERMINOLOGY

### Standard Form
```
Phase 12 WS[N]
```

### Usage Rules

#### ✅ DO
- Always include phase number: "Phase 12"
- Use "WS" for workstream (not "Wave")
- Include workstream number: "WS1", "WS2", "WS3"
- Format with space: "Phase 12 WS1" (not "Phase12WS1")
- Use in references: "As described in Phase 12 WS3..."

#### ❌ DON'T
- Use "Wave": "Phase 12 Wave 1" ❌
- Omit phase number: "WS1" (alone) ❌
- Abbreviate without context: "P12 WS1" ❌
- Mix formats: "Phase12 Wave1" ❌

### Examples

#### Document Headers
```markdown
# Phase 12 WS3 Documentation Plan
# Phase 12 WS2 Testing Results
```

#### Body Text
```markdown
This work is part of Phase 12 WS1 infrastructure improvements.

Phase 12 WS3 focuses on documentation standardization.

As established in Phase 12 WS2...
```

#### Captions/Metadata
```markdown
**Phase:** Phase 12 WS3  
**Authority:** Phase 12 WS3 Documentation  
```

### Context Examples

| Situation | Correct Usage |
|-----------|---------------|
| Referring to multiple workstreams | "Phase 12 WS1, WS2, and WS3" |
| Phase-only reference | "Phase 12 governance" (no WS modifier) |
| Possessive form | "Phase 12 WS1's completion" |
| Abbreviation (captions) | "Phase 12 WS3" (not "P12 WS3") |
| Comparative | "Phase 12 WS1 vs. Phase 12 WS2" |

---

## 2️⃣ AGENT TERMINOLOGY

### Standard Forms
- **Primary:** Copilot Coding Agent
- **Secondary:** Custom Agent
- **Generic:** Agent

### Usage Rules

#### ✅ DO
- Use "Copilot Coding Agent" for GitHub's AI coding assistant
- Use "Custom Agent" for user-defined agents
- Use "Agent" when type is unimportant or generic
- Clarify agent type on first mention: "The Copilot Coding Agent..."
- Use consistent form throughout document

#### ❌ DON'T
- Mix forms in same document: "Copilot Agent" then "Coding Agent" ❌
- Use "GitHub Agent" (ambiguous) ❌
- Use "AI Agent" (too generic) ❌
- Abbreviate to "CA" or "CCA" ❌

### Examples

#### Introducing Agents
```markdown
The Copilot Coding Agent is GitHub's AI-powered coding assistant 
that autonomously executes development tasks.

Custom Agents are user-defined agents within the Cognitive Brain ecosystem.
```

#### Referencing Agents
```markdown
Configure the Copilot Coding Agent by setting...

Each Custom Agent has access to...

Agents in the registry can be discovered via...
```

#### Possessive/Attributive
```markdown
The Copilot Coding Agent's execution model...

Custom Agent creation requires...

Agent registry lookup...
```

### Decision Tree
```
Does the agent belong to GitHub? → YES → "Copilot Coding Agent"
Does the user define it? → YES → "Custom Agent"
Is type unimportant? → YES → "Agent"
```

---

## 3️⃣ ML STRATEGY TERMINOLOGY

### Standard Forms
- **System Component:** Strategy Selector
- **Strategic Planning:** ML Strategy  
- **Algorithm/Logic:** Decision Tree
- **[DEPRECATED]:** OODA Loop (use Strategy Selector instead)

### Usage Rules

#### ✅ DO
- Use "Strategy Selector" when discussing the system component
- Use "ML Strategy" in strategic/planning contexts
- Use "Decision Tree" for algorithm/logic discussion
- Specify context to avoid ambiguity
- Update "OODA Loop" references to "Strategy Selector"

#### ❌ DON'T
- Use "OODA Loop" in new documentation ❌
- Mix "Strategy Selector" and "ML Strategy" for same concept ❌
- Use bare "Strategy" without qualifier ❌
- Use "Decision" without context ❌

### Context-Specific Examples

#### Technical Architecture (Use "Strategy Selector")
```markdown
The Strategy Selector component determines which ML models to use 
based on the current task context.

Strategy Selector Architecture:
- Input analysis
- Model selection logic
- Execution dispatch
```

#### Strategic Planning (Use "ML Strategy")
```markdown
Our ML Strategy for Phase 12 WS3 emphasizes interpretability.

The ML Strategy defines our approach to model selection across 
different task categories.
```

#### Algorithm Discussion (Use "Decision Tree")
```markdown
The Strategy Selector uses a Decision Tree to classify tasks:
1. Is task classification-heavy? → Use classifier model
2. Is task generation-heavy? → Use generator model
...
```

#### Operational Process (Use "Strategy Selector cycle")
```markdown
Each Strategy Selector cycle analyzes the incoming task and 
selects the appropriate model.

The Strategy Selector cycle repeats until task completion.
```

### Decision Tree
```
Discussing system architecture? → "Strategy Selector"
Discussing strategic direction? → "ML Strategy"
Discussing decision logic? → "Decision Tree"
Otherwise → context-dependent
```

---

## 4️⃣ COGNITIVE BRAIN TERMINOLOGY

### Standard Forms
- **Full form:** Cognitive Brain
- **Module reference:** Cognitive Brain module
- **Captions only:** Brain (use sparingly)

### Usage Rules

#### ✅ DO
- Use "Cognitive Brain" in all body text
- Use "Cognitive Brain module" when discussing specific modules
- Use "Brain" ONLY in headers/captions (space-constrained contexts)
- Define "Cognitive Brain" on first use in documents
- Use consistently throughout document

#### ❌ DON'T
- Use abbreviation "CB" anywhere ❌
- Use "Brain" alone in body text ❌
- Use "The Brain system" (redundant) ❌
- Mix "CB" and "Cognitive Brain" ❌

### Examples

#### Body Text (Always Use "Cognitive Brain")
```markdown
The Cognitive Brain manages coordination between multiple agents.

The Cognitive Brain module is responsible for agent selection.

Configuration of the Cognitive Brain occurs in...
```

#### Headers/Captions (Can Use "Brain")
```markdown
# Brain Architecture
## Brain Module Components
**System:** Brain (Caption)
```

#### Module References
```markdown
The Cognitive Brain module for task analysis...

Cognitive Brain routing module...

Cognitive Brain coordination module...
```

#### First Mention
```markdown
The Cognitive Brain is a coordination system that manages 
multiple agents working together on complex tasks.
```

---

## 5️⃣ WORKFLOW TERMINOLOGY

### Standard Forms
- **GitHub Actions:** Workflow
- **CI/CD Jobs:** Workflow job (or "Job" if context clear)
- **Kubernetes:** Pipeline
- **Generic Process:** Workflow

### Usage Rules

#### ✅ DO
- Use "Workflow" for GitHub Actions (primary standard)
- Use "Workflow job" for individual CI/CD jobs
- Specify context when ambiguous: "GitHub Actions Workflow"
- Use "Pipeline" exclusively for Kubernetes
- Be consistent within document

#### ❌ DON'T
- Use "Pipeline" for GitHub Actions ❌
- Use bare "Job" without context ❌
- Mix "Workflow" and "Pipeline" for same GitHub Actions concept ❌
- Use "CI/CD Pipeline" when "Workflow" is clearer ❌

### Context-Based Examples

#### GitHub Actions (Use "Workflow")
```markdown
Create a new Workflow in your .github/workflows/ directory.

The Workflow automatically runs tests on every push.

Workflow triggers:
- push events
- pull_request events
- schedule events

Each Workflow job runs independently.
```

#### Kubernetes (Use "Pipeline")
```markdown
The deployment Pipeline includes:
1. Build stage
2. Test stage
3. Deploy stage

Deploy the Pipeline using kubectl apply...
```

#### Generic Process (Use "Workflow")
```markdown
The deployment Workflow includes testing, review, and merge steps.

Our Workflow ensures quality before production release.
```

#### Mixed Context (Be Specific)
```markdown
CORRECT: "Configure the GitHub Actions Workflow to run tests."
CORRECT: "Deploy the Kubernetes Pipeline to production."
WRONG: "The Pipeline runs tests." (ambiguous)
```

### Decision Tree
```
GitHub Actions context? → "Workflow"
Kubernetes context? → "Pipeline"
CI/CD job context? → "Workflow job" (or "Job" if clear)
Generic process? → "Workflow"
```

---

## 6️⃣ GOVERNANCE TERMINOLOGY

### Standard Forms
- **System:** Governance
- **Specific Rules:** Governance policy
- **Role-Based Access:** RBAC
- **General Access:** Access control

### Usage Rules

#### ✅ DO
- Use "Governance" for system-level references
- Use "Governance policy" for specific rules/requirements
- Use "RBAC" for role-based access control (technical)
- Use "Access control" for non-role-based access patterns
- Clarify context when discussing policies

#### ❌ DON'T
- Use "Policy" alone without qualifier ❌
- Use "Authorization" without specifying context ❌
- Mix "Policy" and "Governance policy" for same concept ❌
- Use "Auth" or "AuthZ" (too informal) ❌

### Examples

#### System References
```markdown
The Governance layer ensures consistent enforcement of...

Governance provides the framework for policy management.

Enable Governance by setting ENABLE_GOVERNANCE=true.
```

#### Specific Policies
```markdown
Governance policies require:
- Code review by 2+ team members
- All tests passing
- No security vulnerabilities

The governance policy for agent deployment states...

Our Governance policy prevents unauthorized access to...
```

#### Role-Based Access
```markdown
RBAC (Role-Based Access Control) is configured in...

Grant permissions using RBAC groups:
- admin: Full access
- developer: Limited write access
- viewer: Read-only access

RBAC rules are defined in...
```

#### General Access Control
```markdown
Access control mechanisms include:
- Authentication (who are you?)
- Authorization (what can you do?)
- Audit logging (record actions)

The access control layer validates all requests.
```

### Decision Tree
```
System-level reference? → "Governance"
Specific rule/policy? → "Governance policy"
Role-based access? → "RBAC"
General access patterns? → "Access control"
Security component? → Specify: "Access control" or "RBAC"
```

---

## 7️⃣ TURN/ITERATION TERMINOLOGY

### Standard Forms
- **Process Steps:** Iteration N
- **Conversation History:** Turn N (limited)
- **Compound Forms:** multi-iteration

### Usage Rules

#### ✅ DO
- Use "Iteration N" for process execution steps
- Use "Iteration" as default; use "Turn" only for conversation context
- Use "multi-iteration" for compound references
- Include number: "Iteration 1" (not just "Iteration")
- Be consistent within document

#### ❌ DON'T
- Use "Turn N" for process steps ❌
- Use "multi-turn" in process contexts ❌
- Mix "Iteration" and "Turn" for same concept ❌
- Use bare "Turn" without number ❌

### Examples

#### Process Execution (Use "Iteration")
```markdown
Iteration 1: Initial validation
Iteration 2: Model selection
Iteration 3: Execution
Iteration 4: Results analysis

During Iteration 2, the agent selects the appropriate model.

Each Iteration produces a set of results.

Repeat until Iteration N concludes successfully.
```

#### Multi-Iteration Processes (Use "multi-iteration")
```markdown
A multi-iteration process may require several passes to reach...

The multi-iteration execution model allows...

Configure multi-iteration behavior in settings.
```

#### Conversation Context (Turn - Limited Use)
```markdown
The conversation Turn sequence shows:
Turn 1: User asks question
Turn 2: Agent responds
Turn 3: User clarifies

The agent maintains state across conversation Turns.

In Turn 5 of the discussion...
```

#### Avoid Mixing
```markdown
CORRECT: "The agent refines results over multiple iterations."
WRONG: "The agent refines results over multiple turns."

CORRECT: "Turn 3 of the conversation shows..."
WRONG: "Turn 3 of the process shows..." (use Iteration instead)
```

### Decision Tree
```
Process execution step? → "Iteration N"
Conversation sequence? → "Turn N" (limited)
Compound term? → "multi-iteration" (not "multi-turn")
Ambiguous? → Prefer "Iteration"
```

---

## 📝 Writing Guidelines

### First Mention
Always define specialized terms on first mention:

```markdown
✅ CORRECT:
The Cognitive Brain (AI system managing agent coordination) provides...

✅ CORRECT:
Our ML Strategy for Phase 12 emphasizes... 

❌ WRONG:
The CB provides coordination.
Our ML Strategy emphasizes...
```

### Consistency Within Documents
Establish term usage in introduction and maintain throughout:

```markdown
In this document:
- "Workflow" refers to GitHub Actions execution units
- "Governance policy" refers to access control rules
- "Iteration" refers to process execution steps

[Rest of document uses these terms consistently]
```

### Context Clarification
When a term could be ambiguous, clarify context:

```markdown
✅ CORRECT:
"The GitHub Actions Workflow triggers on push events."
"The Kubernetes Pipeline deploys the application."

❌ WRONG:
"The Pipeline triggers on push events." (ambiguous)
"The Workflow deploys the application." (unclear if K8s)
```

### Avoidance of Ambiguous Terms
Avoid terms that could mean multiple things:

```markdown
✅ CORRECT:
"The Copilot Coding Agent executes autonomously."
"Custom Agents are created by users."

❌ WRONG:
"The Agent executes autonomously." (which agent?)
"Agents are created by users." (which type?)
```

---

## 🔄 Updating Existing Documentation

### When to Update
- During regular documentation maintenance
- When creating new documents
- During code review (suggest updates)
- During quarterly documentation audits

### How to Update
1. Use search-and-replace with patterns from TERMINOLOGY_MAPPING.md
2. Manually review context-dependent replacements
3. Validate syntax after changes
4. Spot-check results

### What NOT to Update
- Code comments (unless critical for clarity)
- String literals in source code (avoid breaking changes)
- Historical/archived documents (preserve as-is)
- Quoted examples of deprecated terminology
- External API documentation (preserve as provided)

---

## ✅ Checklist for Contributors

### Before Submitting Documentation
- [ ] All Phase references use "Phase 12 WS[N]" format
- [ ] All GitHub agent references use "Copilot Coding Agent"
- [ ] All custom agent references use "Custom Agent"
- [ ] All Brain references use "Cognitive Brain" (not "CB")
- [ ] Workflow vs. Pipeline usage is context-appropriate
- [ ] Governance terminology is qualified ("Governance policy", not "Policy")
- [ ] Process step references use "Iteration" (not "Turn")
- [ ] Specialized terms are defined on first mention
- [ ] Terminology is consistent throughout document
- [ ] No deprecated terms (OODA Loop, etc.) used

### Before Code Review
- [ ] Terminology is consistent with this style guide
- [ ] Context is clear for potentially ambiguous terms
- [ ] Specialized terms are defined
- [ ] No mixing of related terms (Phase vs. Wave, etc.)

---

## 📚 Reference Materials

### Related Documents
- `.codex/TERMINOLOGY_STANDARDIZATION_GUIDE.md` - Canonical definitions
- `.codex/TERMINOLOGY_MAPPING.md` - Search-and-replace patterns
- `.codex/GLOSSARY.md` - 50+ term definitions

### Quick Links
- [Quick Reference](#-quick-reference-what-to-use) - Start here
- [Phase/Workstream Terminology](#1️⃣-phaseworkstream-terminology)
- [Agent Terminology](#2️⃣-agent-terminology)
- [ML Strategy Terminology](#3️⃣-ml-strategy-terminology)
- [Cognitive Brain Terminology](#4️⃣-cognitive-brain-terminology)
- [Workflow Terminology](#5️⃣-workflow-terminology)
- [Governance Terminology](#6️⃣-governance-terminology)
- [Turn/Iteration Terminology](#7️⃣-turniteration-terminology)

---

## 🆘 Questions & Clarification

### Common Questions

**Q: Should I update old documentation to follow this guide?**  
A: Yes, during regular maintenance or when creating related new content. Update incrementally to avoid large, hard-to-review changes.

**Q: What if context makes both terms valid?**  
A: Choose the most specific/clear term. When in doubt, refer to the decision trees.

**Q: How do I request updates to this style guide?**  
A: Submit issues or discussions with rationale. All terminology updates require consensus.

**Q: Can I use abbreviations?**  
A: No. The style guide prohibits abbreviations for main terms (CB, CCA, etc.) to ensure clarity.

**Q: What about historical documents with old terminology?**  
A: Archive/preserve historical docs as-is. Update only active/current documentation.

---

## 📋 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-07-08 | terminology-consistency-agent | Initial style guide creation |

---

## 📄 Document Metadata

**Owner:** terminology-consistency-agent  
**Campaign:** Phase 12 WS3 Documentation  
**Authority:** D-tier autonomous  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-07-08 16:25 UTC  
**Next Review:** 2026-08-08 (30 days)  
**Audience:** All contributors

---

**TERMINOLOGY STYLE GUIDE: PRODUCTION READY** ✅
