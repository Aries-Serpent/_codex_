# Repo Survey — main & PR 0 — 2024-10-30 (UTC)

**Ref:** branch `main`  commit `0a6b27b0`  •  **Artifacts:** `docs/status_updates/artifacts/Previous Cycle-10-30-survey-main-and-0`

---

```text
Repo Survey — main — 2024-10-30 (UTC)

Scope & Goal:
- Branch: main
- Date (UTC): 2024-10-30
- Objective: Refresh survey artifacts for main after ring alignment.

Targets Collected:
- Reasoning surface (templates/curricula)
- Training orchestrator (unified_training, train_loop)
- Evaluator bindings + readiness signals
- CLI/Docs parity for reasoning pod dry-run

Findings (highlights):
- Baseline reasoning template present; curricula and evaluation presets resolvable.
- Doc → CLI parity: confirm `codex repo-map --reasoning` and dry-run deploy flags.
- Sanitizer: `[BEGIN/END CONTENT]` blocks wrapped as fenced text in the final MD.

Evidence:
- configs/training/reasoning/baseline.yaml
- src/codex_ml/training/unified_training.py
- src/codex_ml/train_loop.py
- src/codex_ml/eval/evaluator.py
- docs/status_updates/readiness.schema.json

Gaps & Remediations:
- None blocking. Keep `--dry-run` enforcement in deploy command for this ring.

Promotion Signal:
Let R = α·E + β·T + γ·D, with (α,β,γ)=(0.2,0.2,0.6).
- E: Evaluation pass ratio (offline) … measure below
- T: Trace coverage proxy … measure below
- D: Docs/CLI/Deploy dry-run parity … measure below

Next Steps:
- Generate readiness.json with measured (or placeholder) scores.
- Validate against readiness.schema.json.
- Commit refreshed artifacts.

```text

---
_Generated with `scripts/survey.sh` • R = α·E + β·T + γ·D (α+β+γ=1)_
