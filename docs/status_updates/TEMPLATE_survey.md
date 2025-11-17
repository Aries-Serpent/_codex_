# Survey — <RING> and <PR_OR_REF> — <YYYY-MM-DD>

> **Purpose:** Capture an auditable, human-readable snapshot of ground truth pulled from a specific ring/PR/ref.
> **Save As:** `docs/status_updates/survey-<ring>-and-<pr-or-ref>-<YYYY-MM-DD>.md`
>
> **Notation (readiness aide):** Let the survey readiness aide be
> \( R = \alpha \cdot E + \beta \cdot T + \gamma \cdot D \),
> where \(E\)=evaluation surface completeness, \(T\)=trace capture signal quality, \(D\)=docs parity.
> Choose \(\alpha,\beta,\gamma \in [0,1]\), \(\alpha+\beta+\gamma=1\). This is advisory, not a gate.

---

## 1) Metadata
- **Ring:** `<0A_base_ | 0B_base_ | 0C_base_ | 0D_base_ | main>`
- **Branch/Ref:** `<branch-or-sha>`
- **PR:** `#<pr-number | N/A>`
- **Commit:** `<short-sha>`
- **Date (UTC):** `<YYYY-MM-DD>`
- **Owner(s):** `<name(s)>`
- **Artifacts dir:** `docs/status_updates/artifacts/<YYYY-MM-DD>-<slug>/`

---

## 2) Survey Scope
This survey collects:
- Core training/orchestration files
- Reasoning harness & configs (Hydra overlays + curricula)
- Evaluation surfaces + CLI UX affordances
- Docs promises vs. assets (deployment, quickstart, gates)

**Requested refs:** Clearly label each file as `<path>@<ref>` and keep code/text readable.

---

## 3) Highlights (Summary for Humans)
- **Wins:** `<bullets>`
- **Gaps:** `<bullets>`
- **Actions recommended:** `<bullets>`

---

## 4) Ground Truth Artifacts (Normalized)
> All embedded as fenced code blocks to preserve readability.  
> Use a consistent header for each file or search result:
>
> `>>> FILE: <path>@<ref>`
>
> Then wrap content in triple backticks.

### 4.1 Files & Excerpts
```text
<Paste normalized file excerpts here>
```text

### 4.2 Search Results
```text
<Paste normalized grep/ag/ripgrep results here>
```text

---

## 5) Docs Parity (Promises vs Assets)
- Missing or mismatched references explicitly listed here (path + line)
- Example:
  - `docs/deployment/reasoning_pod.md` → `<FOUND | MISSING>`
  - `configs/deploy/reasoning_pod.yaml` → `<FOUND | MISSING>`

---

## 6) Readiness Aide (Optional)
Provide your chosen weights and component scores:
- α=`<0..1>`, β=`<0..1>`, γ=`<0..1>`
- E=`<0..1>`, T=`<0..1>`, D=`<0..1>`

**Calculation:**  
`R = α·E + β·T + γ·D = <value>`

---

## 7) Attachments
Place supporting files here:
- `docs/status_updates/artifacts/<date>/report.md`
- `docs/status_updates/artifacts/<date>/metrics/*.ndjson`
- `docs/status_updates/artifacts/<date>/logs/*.txt`

---

## 8) Changelog (since prior survey)
- `<bullet>`
- `<bullet>`

---

## 9) Next Steps
- `<short plan>`
