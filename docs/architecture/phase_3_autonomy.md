# Phase 3: Autonomy Architecture

**Status**: Active quick-wins plan  
**Updated**: 2026-05-08  
**Audience**: Maintainers, Copilot cloud agent sessions, Cognitive Brain operators

---

## Overview

Phase 3 is the transition from isolated self-healing to dependable repository-wide
autonomous execution. The current codebase already has many autonomy ingredients
(`PDA` loop logging, Cognitive Brain documents, self-healing workflows, MCP-based
CI triage), but the next reliability ceiling is not model intelligence — it is
operational consistency under minimal CI environments.

The highest-priority gap observed during PR #4368 self-healing is:

> **Autonomous paths still depend on many distributed, ad-hoc optional dependency
> fallbacks instead of one shared compatibility layer.**

That gap causes Copilot cloud agent sessions to repeatedly spend tokens and time
recovering from import-time failures (`hydra`, `tokenizers`, `transformers`,
`prometheus_client`, stubbed `torch`, package-vs-module differences) before they
can perform useful work.

---

## Cognitive Brain Analysis: What Must Improve Next

### Current strength

- CI failures are increasingly diagnosable in-session via GitHub MCP tools.
- The Cognitive Brain / PDA loop already captures patterns and session lessons.
- The repository has self-healing workflows plus accountability/reporting loops.

### Current autonomy blocker

The Cognitive Brain can recognize patterns, but the execution surfaces still fail
too early and too inconsistently for that intelligence to compound efficiently.

This appears in three recurring classes of failure:

1. **Import-time brittleness**
   - modules assume full-featured optional packages as soon as `import X` works
   - partial stubs / fallback modules break later on missing attributes

2. **Test expectations lag runtime fallbacks**
   - tests assume empty stderr, strict package origins, or full dependency stacks
   - real CI environments intentionally run with missing or stubbed dependencies

3. **Distributed rate-limit handling**
   - API-aware workflows already have good patterns in some files
   - those protections are not yet uniformly applied across all autonomy surfaces
   - autonomous sessions can still waste attempts on avoidable GitHub API pressure

---

## Rate-Limit-Aware Autonomy Requirement

Autonomous agency must treat GitHub API budget as a first-class resource.

### Why this matters

- Copilot cloud agent sessions, self-healing workflows, check dispatchers, and
  rescue-comment systems all compete for the same repository API budget.
- A technically correct agent can still become operationally unreliable if it
  triggers secondary failures via repeated list/read/update loops.

### Immediate rule

Every code path that performs repeated GitHub API reads or writes should:

1. **Check budget early**
   - use a pre-flight budget check where available
2. **Prefer file/artifact handoff over large env/output payloads**
   - avoids retries and truncation failures
3. **Short-circuit on low remaining quota**
   - degrade to summary mode rather than continue exhaustive enumeration
4. **Batch reads, minimize writes**
   - especially in PR comments, variable sync, workflow triage, and status refresh
5. **Make rate-limit state visible to the Cognitive Brain**
   - so repeated sessions learn to avoid the same pressure patterns

---

## Immediate Quick Wins for Codebase-Wide Autonomy

These are ordered for the **Copilot cloud agent** first, not for generic local
developer environments.

### Quick Win 1 — Shared optional-dependency compatibility layer

**Goal:** Stop repeated import-time breakage across autonomous/test surfaces.

**Implement immediately:**
- Add a small shared utility for:
  - safe optional imports
  - stub capability checks (`hasattr`/callable surface validation)
  - no-op decorator fallbacks (for `hydra.main`-style entrypoints)
  - path fallback helpers (`to_absolute_path`-style compatibility)
- Replace repeated ad-hoc fallback logic in autonomy-critical modules.

**Cloud-agent benefit:** fewer failed exploratory turns, faster reliable startup.

### Quick Win 2 — Standardize “minimal environment” test semantics

**Goal:** Align tests with the offline/stubbed CI environment the cloud agent
actually sees.

**Implement immediately:**
- Treat known fallback stderr as acceptable where stdout contracts matter.
- Skip tests when optional packages are genuinely unavailable instead of failing
  on polluted module state.
- Validate behavior, not package implementation details, when running in stubs.

**Cloud-agent benefit:** self-healing sessions spend time fixing real regressions,
not re-fighting the same environment mismatch.

### Quick Win 3 — Rate-limit-aware GitHub operations policy

**Goal:** Make autonomous GitHub operations resilient under shared API budgets.

**Implement immediately:**
- Reuse the existing rate-limit patterns already present in selected workflows.
- Add a short repository reference doc that maps:
  - when to pre-check quota
  - when to stop paginating
  - when to switch from API chatter to artifact/file handoff
- Feed rate-limit outcomes into PDA/AfterMath summaries.

**Cloud-agent benefit:** more stable multi-workflow autonomy and fewer cascading
GitHub-side failures.

### Quick Win 4 — Copilot cloud agent environment bootstrap plan

**Goal:** Make the cloud agent deterministically ready for the repo’s common
autonomy tasks.

**Implement immediately in planning / next implementation step:**
- add/update `.github/workflows/copilot-setup-steps.yml` on the default branch
- preinstall the repo’s most frequently needed validation stack
- cache only where the repository layout reliably supports it
- keep permissions minimal and bootstrap time bounded

**Recommended setup focus:**
- Python toolchain aligned with repository tests
- pre-commit / Ruff / mypy baseline helpers
- optional test extras most often required by self-healing sessions
- deterministic environment variables for offline-first execution

**Cloud-agent benefit:** less trial-and-error package installation, fewer startup
failures, faster convergence on code fixes.

### Quick Win 5 — Cognitive Brain operational memory enrichment

**Goal:** Convert recurring CI/environment fixes into reusable autonomy memory.

**Implement immediately:**
- explicitly record:
  - optional dependency mismatch patterns
  - rate-limit exhaustion patterns
  - reusable-workflow vs local-job validation rules
  - cloud-agent bootstrap assumptions
- surface those patterns at session start, not only after failure

**Cloud-agent benefit:** the agent starts closer to the correct fix path.

---

## Copilot Cloud Agent Tailoring

The cloud agent is the primary execution environment to optimize first.

### Tailoring principles

1. **Fast startup beats maximal completeness**
   - install the dependencies needed for common healing loops first
2. **Offline-first defaults**
   - avoid remote fetch requirements unless explicitly needed
3. **Minimal permissions**
   - preserve least-privilege job configuration
4. **Deterministic fallbacks**
   - if a dependency is unavailable, degrade predictably and visibly
5. **Rate-limit-aware GitHub usage**
   - prefer fewer, smarter API interactions

### Immediate cloud-agent planning checklist

- [ ] Define the minimum dependency set required for common self-healing sessions
- [ ] Add or refine `copilot-setup-steps.yml` with deterministic bootstrap steps
- [ ] Document which optional packages are “recommended preinstall” vs “skip/soft-fail”
- [ ] Centralize compatibility shims for `hydra`, tokenizer stacks, and stubbed ML deps
- [ ] Expose GitHub API budget heuristics to autonomy workflows and session memory

---

## Implementation Order

### Week 1 quick wins

1. Shared compatibility helpers for optional imports / decorator fallbacks
2. Copilot cloud agent bootstrap planning and workflow draft
3. Rate-limit-aware operations reference for autonomous workflows

### Week 2 quick wins

4. Migrate high-churn autonomy entrypoints to the shared helpers
5. Update flaky/minimal-environment tests to match real fallback behavior
6. Feed new patterns into Cognitive Brain pre-load/session injection

---

## Success Criteria

Phase 3 quick wins are successful when:

- Copilot cloud agent sessions spend less time on environment recovery
- self-healing loops fail later (on real logic) rather than at import time
- GitHub API-heavy workflows back off gracefully under quota pressure
- repeated autonomy fixes become memory-first instead of rediscovered each session

---

## Related Documentation

- [docs/cognitive_brain_integration_master_plan.md](../cognitive_brain_integration_master_plan.md)
- [.codex/plans/autonomous_implementation_master_plan.md](../../.codex/plans/autonomous_implementation_master_plan.md)
- [docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md](../ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md)
- [docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md](../reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md)
- [.codex/docs/GITHUB_API_AND_MCP_REFERENCE.md](../../.codex/docs/GITHUB_API_AND_MCP_REFERENCE.md)
