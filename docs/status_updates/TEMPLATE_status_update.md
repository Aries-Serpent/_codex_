# Status Update — Reasoning Readiness & Promotion Gate

**Last Updated:** 2026-06-22

> **When to use:** After each ring run (0A → 0D) or major PR affecting reasoning,
> fill this template to create an auditable record of progress. Save as:
> `docs/status_updates/<slug>-<YYYY-MM-DD>.md`.
>
> **Notation:** Let overall readiness be
> \( R = \alpha \cdot E + \beta \cdot T + \gamma \cdot D \),
> where \(E\)=evaluation completeness, \(T\)=trace quality, \(D\)=docs parity.
> Use \(\alpha,\beta,\gamma\in[0,1]\) with \(\alpha+\beta+\gamma=1\).

## 1) Metadata
- **Ring:** [0A_base_ | 0B_base_ | 0C_base_ | 0D_base_ | main]
- **Branch/PR:** `<branch>` / `#<pr-number>`
- **Commit:** `<short-sha>`
- **Date (UTC):** `<YYYY-MM-DD>`
- **Owner(s):** `<name(s)>`
- **Artifacts folder:** `docs/status_updates/artifacts/<YYYY-MM-DD>-<slug>/`

## 2) Objectives (what today's update aims to prove)
- [ ] Curriculum knobs validated (phases, budgets, tool adapters).
- [ ] Trace capture mode exercised (activations vs. placeholders).
- [ ] Evaluation gates executed (proof/math/tool probes).
- [ ] Deployment docs/presets in sync (no missing references).

## 3) Knobs Snapshot (control surface)

| Knob | Current | Rationale | Next Experiment |
|---|---|---|---|
| Curriculum phase | `<phase-id>` | `<why>` | `<next>` |
| Trace capture | `<activations|weights|mixed>` | `<why>` | `<next>` |
| Eval preset | `<configs/evaluation/reasoning/*.yaml>` | `<why>` | `<next>` |
| Deployment preset | `<preset-name or N/A>` | `<why>` | `<next>` |

## 4) Evidence
### 4.1 Evaluation Summary
- **Ran:** `<cmd>`
- **Metrics NDJSON:** `docs/status_updates/artifacts/<date>/metrics/*.ndjson`
- **Highlights:** `<brief bullet points>`

### 4.2 Trace Quality
- **Mode:** `<activations|weights|mixed>`
- **Coverage:** `<% samples>`
- **Notes:** `<observations & anomalies>`

### 4.3 Docs Parity Check
- Missing references resolved? `[Yes|No]`
- Links verified: `docs/README_ROOT.md`, `docs/README.md`, `docs/guides/*`, `docs/deployment/*`

## 5) Gaps & Remediations

| Gap | Impact | Fix (owner) | Target Ring |
|---|---|---|---|
| `<gap>` | `<impact>` | `<plan>` | `<0A/0B/0C/0D/main>` |

## 6) Promotion Recommendation
- **Gate result:** `[Block | Proceed to next ring]`
- **Rationale:** `<short argument>`
- **Readiness score:** `R = α·E + β·T + γ·D = <value>`
  - α=`<0..1>`, β=`<0..1>`, γ=`<0..1>`, E=`<0..1>`, T=`<0..1>`, D=`<0..1>`

## 7) Artifacts (attach and list)
- `docs/status_updates/artifacts/<date>/report.md`
- `docs/status_updates/artifacts/<date>/metrics/*.ndjson`
- `docs/status_updates/artifacts/<date>/logs/*.txt`

## 8) Changelog (since last update)
- `<bullet 1>`
- `<bullet 2>`

## 9) Next Steps
- `<short bulleted plan>`

---

## Template Usage Notes

### Readiness Formula Explanation
The weighted readiness score \(R\) represents overall promotion confidence:
- **E (Evaluation)**: Fraction of eval gates passed (0.0 = none, 1.0 = all)
- **T (Trace Quality)**: Coverage and fidelity of reasoning traces
- **D (Docs Parity)**: Documentation completeness (broken links, missing refs)

**Example**: For α=0.4, β=0.3, γ=0.3, E=0.9, T=0.8, D=1.0:
  R = 0.4×0.9 + 0.3×0.8 + 0.3×1.0 = 0.36 + 0.24 + 0.30 = **0.90** (90% ready)
