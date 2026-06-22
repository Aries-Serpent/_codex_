<!-- Use this as a writer's guide when constructing Codex survey prompts/output -->
# Repo Survey — <branch> & PR <PR> — <YYYY-MM-DD> (UTC)

**Last Updated:** 2026-06-22

**Ref:** branch `<branch>`  commit `<short-sha>`  •  **Artifacts:** `docs/status_updates/artifacts/<date>-survey-<branch>-and-<PR>/`

---

## 1) Scope & Goal
- Branch: `<branch>`
- PR: `#<PR>`
- Date (UTC): `<YYYY-MM-DD>`
- Objective: Capture authoritative ground truth to finalize docs, knobs, and diffs.

## 2) Targets Collected
- A) Trainer/orchestration
- B) Reasoning harness (vectorization/trace)
- C) Baseline reasoning config & curricula
- D) Evaluation surfaces
- E) CLI / repo-map
- F) Deployment promises (docs)
- G) Referenced-missing assets
- H) Ring mentions (0A/0B/0C/0D/main)
- I) `ReasoningTrainer` presence
- J) CLI mismatch audit

## 3) Findings (Highlights)
- **Summary:** `<bullet points>`
- **Actionables:** `<bullet points>`

## 4) Evidence
### 4.1 Files and Excerpts
> For each section, include labeled blocks as:
>
> **FILE:** `<path>@<ref>`
>
> [BEGIN CONTENT]
> ...excerpt or content...
> [END CONTENT]
>
> The sanitizer wraps each `[BEGIN/END CONTENT]` block in ```text fences for readable Markdown.

### 4.2 CLI/Docs Mismatches
- `<bullets>`

## 5) Gaps & Remediations

| Gap | Impact | Fix (owner) | Target Ring |
|---|---|---|---|
| `<gap>` | `<impact>` | `<plan>` | `<0A/0B/0C/0D/main>` |

## 6) Promotion Signal
Let readiness be \( R = \alpha \cdot E + \beta \cdot T + \gamma \cdot D \),
with \( \alpha, \beta, \gamma \in [0,1], \alpha+\beta+\gamma=1 \).
- E (Eval completeness): `<0..1>`
- T (Trace quality): `<0..1>`
- D (Docs parity): `<0..1>`
- Weights: α=`<0..1>`, β=`<0..1>`, γ=`<0..1>`
- **R = <computed>** → **Recommendation:** `[Block | Proceed]`

## 7) Artifacts
- `docs/status_updates/artifacts/<date>-survey-<branch>-and-<PR>/report.md`
- `docs/status_updates/artifacts/<date>-survey-<branch>-and-<PR>/metrics/*.ndjson`
- `docs/status_updates/artifacts/<date>-survey-<branch>-and-<PR>/logs/*.txt`

## 8) Changelog
- `<bullets>`

## 9) Next Steps
- `<bullets>`
