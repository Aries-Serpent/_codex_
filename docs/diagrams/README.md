# 📊 Mermaid Diagrams Index

> **Last updated:** 2026-05-14 (S1003-ctep)

All `.mmd` files in this directory are authoritative Mermaid source diagrams.
Render with the Mermaid CLI (`mmdc`), GitHub's native Mermaid rendering, or the
[Mermaid Live Editor](https://mermaid.live).

---

## Diagrams

| File | Purpose | Last Updated |
|------|---------|-------------|
| [`architecture.mmd`](architecture.mmd) | Full system architecture: ML core, tokenization, RAG, cognitive brain, logging, CI self-healing, GitHub Actions workflows | 2026-05-14 (S1003-ctep) |
| [`ci_self_healing_flow.mmd`](ci_self_healing_flow.mmd) | Detailed CI self-healing pipeline: push → agent-auth-delegation → auto_fix_all_missing (REQ-4/5/6/PDA) → pre-merge-validation → Pattern 30 scorecard → merge gate | 2026-05-14 (S1003-ctep) |
| [`runtime_logic_map.mmd`](runtime_logic_map.mmd) | Detailed runtime flow map: all CLI entry points, package-main orchestration, training strategies, tokenizer pipeline, ingestion, quantum orchestrator, Rust/Python hybrid | 2026-02-xx (S178) |
| [`audit_pipeline_v1.4.0.mmd`](audit_pipeline_v1.4.0.mmd) | 7-stage audit pipeline: context index → facet grouping → capability extraction → scoring → gap analysis → report rendering → manifest generation | 2025-xx (v1.4.0) |

---

## Key Concepts Shown

### `architecture.mmd`
High-level system map. Key additions since S1003-ctep:
- `fix_pda_entry_today()` hardened into `session_wrapup_autofix.py`
- `auto_fix_all_missing()` now includes REQ-PDA step
- Pattern 30 `pda_today` dimension changed from `pda_manual` → `pda_auto`

### `ci_self_healing_flow.mmd`
Shows the full self-healing loop from push to merge:
- Every push triggers `agent-auth-delegation.yml` → `session_wrapup_autofix.py`
- `auto_fix_all_missing()` runs REQ-4, REQ-5, REQ-6, **REQ-PDA (🆕)**, PR-DESC, WEC
- `pre-merge-validation.yml` runs the 32-pattern pipeline
- Pattern 30 scorecard (10 dimensions, 100 pts) gates merge readiness
- CodeQL alert count < 25 is the final merge gate

### `runtime_logic_map.mmd`
Narrative companion: [`docs/system/mermaid_logic_map.md`](../system/mermaid_logic_map.md)

---

## Rendering

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Render all diagrams to SVG
for f in docs/diagrams/*.mmd; do
  mmdc -i "$f" -o "${f%.mmd}.svg"
done
```
