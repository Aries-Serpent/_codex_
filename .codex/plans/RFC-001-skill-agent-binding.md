# RFC-001: Skill-Agent Binding

**Status:** PROPOSED
**Author:** Copilot Coding Agent (S299)
**Created:** 2026-04-03
**PR:** #3854 (0D_base_)

---

## Problem Statement

The orchestrator (`orchestrator_routing.py`) routes tasks to agents by matching task
descriptions against `capability_tags` in `AGENT_REGISTRY.yaml` via a FAISS corpus.

However:
1. **No declared skills** — agents in the registry expose `capability_tags` (nouns: what
   the agent covers) but no `skills:` array (verbs: what actions the agent can invoke at
   runtime). Consequently, the orchestrator can route *to* an agent but cannot determine
   *which skill handler* to invoke.
2. **Scripts are not skill-wrapped** — The `scripts/ci/` tooling layer contains valuable
   session-start primitives (`pre_session_context.py`, `scan_failing_workflows.py`,
   `discussion_context_store.py`) that have no `src/codex/skills/` wrappers and are
   therefore invisible to the skill dispatcher.
3. **No priority scoring** — When multiple agents declare the same capability, there is no
   scoring function to surface the best candidate for a given task context.
4. **No graduation pipeline** — New scripts go through an informal path from `scripts/ci/`
   script → skill handler → agent capability. There is no documented, automated pipeline
   to promote a script to a fully registry-bound skill.

---

## Proposed Solution

### A. Add `skills:` Array to AGENT_REGISTRY.yaml

Extend each registry entry with an optional `skills:` key listing the bound skill handlers.
Each entry names the skill module path and describes its trigger phrase pattern.

```yaml
# Example — copilot-agent-checkin entry (abbreviated)
- id: copilot-agent-checkin
  capability_tags:
    - ci_health
    - pre_session_context
  skills:
    - id: pre_session_context
      module: scripts.ci.pre_session_context
      entrypoint: build_briefing
      trigger_pattern: "session start|pre.session|context brief"
    - id: scan_failing_workflows
      module: scripts.ci.scan_failing_workflows
      entrypoint: scan
      trigger_pattern: "failing checks|workflow status|eta"
```

Constraints:
- `module` must be importable from the repo root (either `scripts/ci/` or `src/codex/skills/`).
- `entrypoint` must be a callable that accepts a `dict` of kwargs and returns a `str`.
- `trigger_pattern` is a regex; the orchestrator uses it for fast pre-filter before FAISS.

### B. Priority Scoring Algorithm

When multiple agents match a task, rank by:

```
Priority = (Impact × CB_Alignment × Recurrence) / Effort
```

| Factor | Range | Description |
|--------|-------|-------------|
| `Impact` | 1–5 | Estimated fix completeness (5 = resolves CI, 1 = cosmetic) |
| `CB_Alignment` | 1–3 | Cognitive Brain phase alignment (3 = active phase, 1 = future) |
| `Recurrence` | 1–5 | PDA pattern hit count for this failure type (normalised to 1–5) |
| `Effort` | 1–5 | Estimated tokens/time to invoke (5 = expensive, 1 = cheap) |

The orchestrator should store `(agent_id, score, skill_id)` triples and return the
top-scoring skill rather than the top-scoring agent.

### C. Skill Graduation Pipeline

```
Stage 0 — Script in scripts/ci/
  └─ Rule: ≥10 manual invocations OR referenced in ≥3 CI workflows

Stage 1 — Skill wrapper in src/codex/skills/<name>/handler.py
  └─ Rule: entrypoint(inputs: dict) → str; tests in tests/skills/test_<name>.py

Stage 2 — AGENT_REGISTRY binding
  └─ Rule: added to skills: array of relevant agent(s); capability_tags updated

Stage 3 — Copilot-accessible
  └─ Rule: Skill ID in orchestrator_routing.py skill dispatch table; docs updated
```

Scripts that qualify for Stage 0 → Stage 1 today:
- `scripts/ci/pre_session_context.py` (`build_briefing`)
- `scripts/ci/scan_failing_workflows.py` (`scan`)
- `scripts/ci/discussion_context_store.py` (`build_comment_context`)
- `scripts/ci/post_rescue_comment.py` (no wrapper; called only by CI)

### D. Orchestrator Routing Update

`orchestrator_routing.py` should gain a `select_skill()` function:

```python
def select_skill(
    task: str,
    context: dict | None = None,
    top_k: int = 3,
) -> list[dict]:
    """Return ranked list of {agent_id, skill_id, score, module, entrypoint}."""
```

The existing `select_specialist()` remains for backwards compatibility but delegates to
`select_skill()` internally, returning `result[0]["agent_id"]`.

---

## Implementation Plan

### Phase 1 — Schema extension (this RFC)
- [x] RFC written (this document)
- [ ] Add `skills` optional key to `.codex/schemas/AgentRegistrySchema.json`
- [ ] Update `AGENT_REGISTRY.yaml` with `skills:` entries for 5 pilot agents:
  `copilot-agent-checkin`, `ci-testing-agent`, `ci-failure-resolution-agent`,
  `autonomous-test-healer-agent`, `workflow-ci-fixer`

### Phase 2 — Skill wrappers
- [ ] `src/codex/skills/pre_session_context/handler.py` wrapping `build_briefing()`
- [ ] `src/codex/skills/scan_failing_workflows/handler.py` wrapping `scan()`
- [ ] `src/codex/skills/discussion_context/handler.py` wrapping `build_comment_context()`
- [ ] Tests for each wrapper in `tests/skills/`

### Phase 3 — Orchestrator upgrade
- [ ] `orchestrator_routing.py`: add `select_skill()`, priority scoring, skill dispatch
- [ ] `AGENT_REGISTRY.yaml`: all 159 agents — add `skills:` where applicable
- [ ] `enforce_registry.py`: validate `skills[*].module` is importable

### Phase 4 — Documentation & graduation
- [ ] Update `docs/agent/OPERATIONAL_GUIDELINES.md` with graduation pipeline
- [ ] Update `AGENTS.md` with skill-agent binding section
- [ ] Add `RP-SKILL-UNBOUND` pattern to `.codex/aftermath/failure_pattern_solutions.yaml`

---

## Acceptance Criteria

1. `python scripts/ci/orchestrator_routing.py select-skill "pre-session context briefing"` returns
   `pre_session_context.build_briefing` with score ≥ 3.
2. `AGENT_REGISTRY.yaml` passes `agent-registry-validation.yml` with `skills:` fields present.
3. Skill wrapper for `pre_session_context` passes 100% of its unit tests.
4. `enforce_registry.py` fails CI when a `skills[*].module` is not importable.

---

## Notes

- `capability_tags` are kept as nouns (what domain the agent covers); `skills` are verbs
  (what the agent can _do_). They are complementary, not redundant.
- The FAISS corpus was built from agent `.md` files. Skill trigger_patterns supplement
  FAISS for precise skill-level routing without corpus rebuild on every new script.
- This RFC supersedes the stub at `.codex/plans/RFC-001-skill-mapping.md` (Phase 3 plan).
  That file remains as historical reference.

---

_RFC-001 · Proposed in PR #3854 S299 · 2026-04-03_
