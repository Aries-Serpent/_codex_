# Cognitive Brain Package Boundary

**Decision (this checkout):** `codex.cognitive_brain` is the authoritative
runtime/kernel package; `aries_serpent_core.brain` hosts the OODA +
memory components. They are integrated, not duplicated.

## Seam

| Layer | Package | Role |
|---|---|---|
| Contracts | `codex_cognitive_sdk` (`packages/cognitive_sdk`) | Dependency-free frozen dataclass contracts: OODA, governance, memory, **evidence** (`ImprovementEvent`/`ImprovementResult`). |
| Kernel & policy | `codex.cognitive_brain` | `kernel.py`, `authority.py` (authority envelope), `improvement_pipeline.py`, `isolated_execution.py`, `outcome_tracking.py`. |
| OODA & memory | `aries_serpent_core.brain` | `ooda_observer/orienter/decider/actor`, `memory_sync.py`, `checkpoint_manager.py`. |
| Pattern interface | `aries_serpent_core.cognitive.brain_interface` | Lexical pattern match + `submit_learning` EMA seam. |

## Rules

1. Policy, authorization, evidence, and GitHub interaction live in
   Python (the control plane). Rust (`codex_swarm`) is an optional bounded
   executor only; it never makes policy decisions or holds credentials.
2. Observers never fabricate health: unavailable data is reported as
   `unavailable`/`error`, distinct from `measured`.
3. Confidence moves only on verified, traceable post-merge outcomes.

## Packaging note (Stage 6)

Root `pyproject.toml` uses `setuptools.build_meta` and does **not** build
the Rust extension; `[tool.maturin]` configures the separate `codex_swarm`
wheel. This is intentional: the MVP distribution is the Python control
plane plus `codex-cognitive-sdk` contracts; `codex_swarm` ships as an
optional, separately-versioned wheel once its task/result contract is
stable.
