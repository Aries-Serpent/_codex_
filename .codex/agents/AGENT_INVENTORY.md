# Canonical Agent Inventory (this checkout)

**Generated:** 2026-10-19 from the working tree of branch
`copilot/develop-evidence-based-assessment`. This file is the ground
truth for what is *present in this checkout*; historical counts in
`AGENT_CONSOLIDATION_MATRIX.md` (164/148), `REPOSITORY_EXPLANATION.md`
(131), `AGENTIC_REPO_STATE.md` (145), and `AGENT_MASTER_REFERENCE.md`
(100+) describe other branches/aspirational states and **must not** be
treated as the live registry.

## Verifiable agent surfaces in this checkout

| Surface | Location | Status |
|---|---|---|
| Executable helper agents | `.codex/agents/security-input-validator/run.py`, `.codex/agents/rfc-compliance-checker/run.py`, `.codex/agents/test-coverage-guardian/run.py` | Present; executable scripts. Registration in a *custom-agent registry* is not verifiable from this checkout. |
| Subsystem registry | `.codex/AGENT_REGISTRY.yaml` | Contains 4 subsystem records (quantum-compliance, cognitive-brain, rag-system, ml-pipeline) — a subsystem registry, **not** a custom-agent registry. |
| Recursive improvement evaluator | `.codex/agents/recursive-improvement-evaluator/SPEC.md` | **New** — read-only evaluator of the E2E loop. |

## Runtime observers

`AgentEcosystemObserver` no longer reports a hard-coded total (formerly
145). It reads `.codex/agent_registry.json` when present and otherwise
reports an empty ecosystem — missing data is never rendered as healthy.

## Honesty rule

Until one run proves every link of the improvement loop (signal →
pattern → proposal → isolated gates → PR → post-merge measurement →
confidence update), this repository describes itself as a set of
**partially integrated components**, not a confirmed autonomous
recursive self-improvement runtime.
