# AI Agent Team Development Process
> **Version**: 1.0.0 | **Created**: Session 51 (2026-02-20) | **Owner**: @mbaetiong
> **Repository**: Aries-Serpent/_codex_ | **Protocol**: CTEP-compliant

---

## 🎯 Purpose

This document establishes the multi-agent cooperative development process for resolving CI failures, technical debt, and codebase-wide issues in the `_codex_` repository. It defines:

1. **Agent roles and responsibilities** (who does what)
2. **Escalation and routing protocols** (how work flows between agents)
3. **Self-healing loops** (how agents iterate autonomously)
4. **Deep research integration** (when to search internally vs externally)
5. **Quality gates** (D1–D4 pre-merge enforcement)
6. **Session methodology integration** (alignment with Agentic Session Methodology v1.0)

---

## 🏗️ Architecture: Multi-Agent Team Structure

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         AGENT ORCHESTRATOR                                │
│                   (routes tasks, grades output, 0-100)                   │
│                    .github/agents/agent-orchestrator.md                   │
└────────────┬─────────────┬──────────────┬──────────────┬─────────────────┘
             │             │              │              │
      ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐ ┌────▼──────────┐
      │  CI/Test    │ │Security │ │ Code Quality│ │ Documentation │
      │   Squad     │ │  Squad  │ │   Squad     │ │    Squad      │
      └──────┬──────┘ └────┬────┘ └──────┬──────┘ └────┬──────────┘
             │             │              │              │
      [see §3 below]
```

### Team Structure

#### 🔧 CI/Test Squad
| Agent | Role | Specialization |
|-------|------|----------------|
| `ci-testing-agent` v4.0 | Lead | 17 fix patterns, 5-iteration self-healing |
| `test-alignment-fixer` | Executor | API drift fixes, mock corrections |
| `coverage-roadmap-agent` | Coverage | Threshold enforcement |
| `meta-tensor-validator` | Validator | PyTorch meta tensor patterns |
| `ci-importerror-agent` | Import | Circular imports, optional deps |

#### 🛡️ Security Squad
| Agent | Role | Specialization |
|-------|------|----------------|
| `security-alert-verification-agent` | Lead | CodeQL/Semgrep triage |
| `codebase-health-guardian` | Enforcer | D1-D4 pre-commit gate |
| `bridge-security-monitor` | Monitor | IPC security validation |
| `pii-scrubber` | Privacy | GDPR/CCPA content filtering |

#### 🎨 Code Quality Squad
| Agent | Role | Specialization |
|-------|------|----------------|
| `datetime-modernizer` | Executor | naive→aware datetime migration |
| `dependency-conflict-agent` | Analyzer | pip resolver conflicts |
| `performance-regression-detector` | Monitor | latency/throughput baselines |
| `repository-hygiene-agent` | Cleaner | structure, naming, artifact hygiene |

#### 📚 Documentation Squad
| Agent | Role | Specialization |
|-------|------|----------------|
| `documentation-quality-agent` | Lead | MkDocs, quality scoring |
| `link-validator-agent` | Validator | broken links, cross-references |
| `doc-freshness-checker` | Monitor | stale docs detection |

---

## 📋 Core Process: PDCA-MARL Loop

Each issue goes through this cycle:

```
PLAN ─→ DISCOVER ─→ ASSIGN ─→ EXECUTE ─→ VALIDATE ─→ DOCUMENT ─→ CLOSE
  │                                            │                       │
  └──────── ESCALATE if 3 failures ────────────┘                      │
                                                                       ▼
                                                              .codex/TECH_DEBT_REGISTRY.md
```

### Phase 1: PLAN (Mandatory Session Startup — MSP)

```python
# MSP-1: Load context
load_memories()
load_tech_debt_registry(".codex/TECH_DEBT_REGISTRY.md")
load_lessons_learned(".codex/PRODUCTION_READINESS_CONSOLIDATION_MAP.md", section="§11")
load_codebase_agency_policy()

# MSP-2: CI awareness (via GitHub MCP)
runs = list_workflow_runs(branch=current_branch, status="completed", per_page=5)
for run in runs.filter(conclusion="failure"):
    failures = get_job_logs(run.failed_jobs, tail_lines=200)
    categorize_failures(failures)  # → assigns to TD-xxx

# MSP-3: Git baseline
baseline_sha = git_log_HEAD()
changed_files = git_diff_base_branch()
```

### Phase 2: DISCOVER (Root Cause Analysis)

```python
# For each failure:
def analyze_failure(failure_message):
    # Step 1: Internal search
    rca = grep_codebase(failure_message.extract_key_term())
    if rca.is_conclusive():
        return FixPlan(rca)

    # Step 2: Memory lookup
    rca = search_memories(failure_message.error_type)
    if rca.is_known_pattern():
        return FixPlan(rca, known_pattern=True)

    # Step 3: Deep research
    if failure_message.is_external_library_bug():
        return DeepResearchQuery(
            internal=f"grep for {failure_message.library} usage",
            external=f"site:github.com {failure_message.library} {failure_message.error}"
        )

    # Step 4: Escalate
    return Escalation(priority="P1", assignee="@mbaetiong")
```

### Phase 3: ASSIGN (Agent Routing)

Decision tree for agent assignment:

```
CI failure → check error type:
├── ImportError/ModuleNotFoundError → ci-importerror-agent
├── isinstance/union type (PyTorch) → ci-testing-agent + meta-tensor-validator
├── datetime naive/aware → datetime-modernizer
├── mock patch path mismatch → test-alignment-fixer
├── missing API method/attribute → test-alignment-fixer
├── CircularImport → ci-importerror-agent
├── CodeQL alert → security-alert-verification-agent
├── performance threshold → performance-regression-detector
├── doc link broken → link-validator-agent
├── coverage < threshold → coverage-roadmap-agent
└── unknown → ci-testing-agent v4.0 (general purpose)
```

### Phase 4: EXECUTE (Self-Healing Loop)

Each agent follows the 5-iteration self-healing protocol:

```python
MAX_ITERATIONS = 5
for i in range(MAX_ITERATIONS):
    fix = generate_fix(failure)
    apply_fix(fix)
    validate = run_targeted_tests(fix.affected_tests)

    if validate.all_pass():
        run_lint(fix.affected_files)
        run_type_check(fix.affected_files)
        return SUCCESS(commit=True)

    if i < MAX_ITERATIONS - 1:
        # Self-healing: analyze what went wrong
        new_context = analyze_residual_failures(validate.failures)
        failure = update_fix_strategy(failure, new_context)
    else:
        # Escalate after max attempts
        classify_as_preexisting_or_escalate(failure)
```

### Phase 5: VALIDATE (Pre-Commit Gate)

The `codebase-health-guardian` enforces D1–D4 before every `report_progress` commit:

```
D1 — Workflow Health:    All required CI checks green (or documented xfail/preexisting)
D2 — Python Quality:     ruff check + isort + black pass on changed files
D3 — Test Policy:        No new test regression; skip guards properly documented
D4 — Artifact Hygiene:   No tmp files, no build artifacts, no secrets in diff
```

### Phase 6: DOCUMENT

After each fix:
1. Update `.codex/TECH_DEBT_REGISTRY.md` (mark resolved, add lessons learned)
2. Update `.codex/PRODUCTION_READINESS_CONSOLIDATION_MAP.md` §11
3. Store memory via `store_memory()` for cross-session knowledge transfer
4. Update cognitive brain status file

---

## 🔍 Deep Research Protocol

When internal grep/memory lookup fails:

### Level 1: Internal Codebase Search
```bash
# Use semantic-search agent for conceptual queries
semantic-search query: "how does X work in this codebase"

# Use grep for exact patterns
grep pattern: "error_keyword" glob: "src/**/*.py"

# Use explore agent for synthesized answers
explore: "Where is X defined and how is it used?"
```

### Level 2: Memory / Known Patterns
```python
# Check stored memories for this error type
memories = search_memories(error_type=failure.category, tags=["CI", "session_49"])
if memories.has_exact_match():
    return apply_known_fix(memories.best_match)
```

### Level 3: Web Search (External)
```python
# Trigger web_search for:
# - External library bugs
# - New API patterns
# - Framework-specific issues

search_queries = [
    f"site:github.com/{library.org}/{library.name} {error_message}",
    f"{error_message} Python 3.12 {library} fix workaround",
    f"{library} changelog {current_version} {next_version} breaking change",
]
```

### Level 4: Escalation
If 3+ web search attempts yield no actionable fix:
- Create GitHub issue with `[DEEP-RESEARCH]` tag
- Add to `.codex/TECH_DEBT_REGISTRY.md` DR-xxx entry
- Assign `@mbaetiong` for human review

---

## 🔄 Continuous Self-Review Loop

After completing all task iterations, agents MUST perform self-review:

```python
def final_self_review():
    # 1. Code review tool
    code_review_result = code_review(
        prTitle=session.title,
        prDescription=session.description
    )

    for comment in code_review_result.comments:
        if comment.is_valid and comment.is_actionable:
            fix = generate_fix(comment)
            apply_and_validate(fix)

    # 2. CodeQL security scan
    codeql_result = codeql_checker()
    for alert in codeql_result.alerts:
        if alert.is_fixable_locally:
            fix_security_alert(alert)

    # 3. Final regression check
    run_targeted_tests(all_changed_files)

    # 4. Update documentation
    update_pr_description()
    update_tech_debt_registry()
    store_session_memory()
```

---

## 📊 Grading Rubric (0–100)

Used by `agent-orchestrator` to score each agent's output:

| Category | Weight | Criteria |
|----------|--------|----------|
| **Correctness** | 35% | All targeted tests pass; no new failures introduced |
| **Completeness** | 25% | All issues in the PLANSET addressed; no silent skips |
| **Code Quality** | 20% | ruff/black/isort clean; no magic strings; proper typing |
| **Documentation** | 10% | Memory stored; registry updated; PR description current |
| **Security** | 10% | CodeQL clean; no secrets; no new vulnerabilities |

**Thresholds**:
- ≥85: ✅ PASS — commit and proceed
- 70–84: ⚠️ WARNING — fix before next session
- <70: ❌ FAIL — do not merge; escalate to @mbaetiong

---

## 🚦 Priority Matrix for Agent Activation

```
╔════════════════════════════════════════════════════════════════╗
║  IMPACT →         LOW              MEDIUM           HIGH       ║
║  URGENCY ↓                                                     ║
║  ─────────────────────────────────────────────────────────     ║
║  CRITICAL    codebase-health   ci-testing-agent   HUMAN+agent  ║
║  HIGH        test-alignment    ci-testing-agent   ci-testing   ║
║  MEDIUM      doc-quality       coverage-roadmap   test-align   ║
║  LOW         repo-hygiene      doc-quality        coverage     ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 📅 Session Template (PLANSET Structure)

Every session follows this template:

```markdown
## Session N PLANSET

### Pre-flight (always, ~5 min)
- [ ] MSP-1: Load memories + tech debt registry + codebase agency policy
- [ ] MSP-2: Check CI via GitHub MCP (list failed jobs, get logs)
- [ ] MSP-3: Git baseline snapshot

### Priority 1 (must complete this session)
- [ ] [P1 items from tech debt registry prioritized by CI impact]

### Priority 2 (complete if time permits)
- [ ] [P2 items from tech debt registry]

### Priority 3 (stretch goals)
- [ ] [P3 items from tech debt registry]

### Post-flight (always, ~10 min)
- [ ] D1–D4 guardian check
- [ ] code_review tool
- [ ] codeql_checker tool
- [ ] Update tech debt registry (close resolved, add new)
- [ ] store_memory (at least 3 new facts)
- [ ] Update cognitive brain status
- [ ] Reply to PR comments
- [ ] Post follow-up prompt as PR comment
```

---

## 📬 Follow-Up Prompt Template

At the end of every session, post this as a PR comment:

```markdown
## 🤖 @copilot — Session N+1 Continuation Prompt

**Continue Work**: Follow the Agentic Session Methodology v1.0
(`.codex/plans/AGENTIC_SESSION_METHODOLOGY.md`)

**MSP-1 Load**:
- `.codex/TECH_DEBT_REGISTRY.md` (current priorities)
- `.codex/PRODUCTION_READINESS_CONSOLIDATION_MAP.md` §11
- Stored memories (last 5 sessions)

**MSP-2 CI**: Check latest run on `copilot/sub-pr-3336`

**Session N+1 PLANSET**:
[current session's unresolved P1 items + next priority tier]

**Deferred from Session N**:
[list of items deferred with reason]

**Grading from Session N**: [0-100 score with breakdown]
```

---

## 🧠 Memory Storage Convention

Each agent MUST store facts using `store_memory` with these conventions:

```python
# Pattern: store after each session when facts are verified
store_memory(
    subject="[area]-[component]",  # e.g., "CI-PyTorch", "datetime-migration"
    fact="Concise, actionable fact (< 200 chars)",
    category="general|file_specific|bootstrap_and_build|user_preferences",
    citations="path/to/file.py:line, commit SHA",
    reason="Why this matters for future sessions; which tasks it helps"
)

# Minimum 3 store_memory calls per session
# Prioritize: root causes > API contracts > fix patterns > env constraints
```

---

## 🔗 References

- **Agentic Session Methodology v1.0**: `.codex/plans/AGENTIC_SESSION_METHODOLOGY.md`
- **Tech Debt Registry**: `.codex/TECH_DEBT_REGISTRY.md`
- **Cognitive Brain Status**: `.codex/cognitive_brain/status/`
- **Production Readiness Map**: `.codex/PRODUCTION_READINESS_CONSOLIDATION_MAP.md`
- **Agent Roster**: `.codex/archive/deprecated/AGENTS.md` (54 agents)
- **CI Auto-Fix System**: `.codex/docs/CI_AUTO_FIX_SYSTEM.md`
- **Codebase Agency Policy**: `.codex/CODEBASE_AGENCY_POLICY.md`

---

*Document version 1.0.0 — Session 51 (2026-02-20)*
*Next review: Session 52*
