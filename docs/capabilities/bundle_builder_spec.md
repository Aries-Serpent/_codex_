# Bundle Builder Spec (Canonical)

This document defines the canonical mathematical model for the bundle builder,
plus actionable artifacts for AI agents (BundleManifest schema + example) and
the explicit Create Agent UI projection map.

---

## Notation

- Requirements state: \( |R\rangle \)
- Bundle state: \( |B\rangle \)
- Create Agent UI state: \( |C\rangle \)
- Hard constraint set: \( \Omega \)
- Energy/loss: \( \mathcal{E}(\cdot) \)
- Indicator: \( \mathbf{1}\{\cdot\} \)

---

## 0) Bundle as a state vector with required subspaces

Define the bundle Hilbert space as a direct sum:

\[
\mathcal{H}_B
=
\mathcal{H}_{agent}
\oplus
\mathcal{H}_{knowledge}
\oplus
\mathcal{H}_{prompts}
\oplus
\mathcal{H}_{tests}
\oplus
\mathcal{H}_{gui}
\]

And the bundle state:

\[
|B\rangle
=
|A\rangle \oplus |K\rangle \oplus |P\rangle \oplus |T\rangle \oplus |G\rangle
\]

Where:

- \( |A\rangle \): Agent config (Name, Description, Instructions, capability toggles)
- \( |K\rangle \): Knowledge config (websites list, web search gate, strict-source gate, org-people reference)
- \( |P\rangle \): Suggested prompts (Title/Message list)
- \( |T\rangle \): Validation & test prompts (conformance measurements)
- \( |G\rangle \): GUI state (tabs/toggles/preview/export)

---

## 1) Bundle generation as constrained energy minimization (explicit completeness)

The generator is an optimizer:

\[
|B^\star\rangle
=
\arg\min_{|B\rangle \in \Omega}\;
\mathcal{E}(B)
\]

Define the energy:

\[
\mathcal{E}(B)
=
\lambda_{miss}\,\mathcal{L}_{missing}(B)
\;+\;
\lambda_{map}\,\mathcal{L}_{ui\_map}(B)
\;+\;
\lambda_{src}\,\mathcal{L}_{source}(B)
\;+\;
\lambda_{fmt}\,\mathcal{L}_{format}(B)
\;+\;
\lambda_{test}\,\mathcal{L}_{test\_fail}(B)
\;-\;
\lambda_{util}\,\mathcal{R}_{utility}(B)
\]

### Missingness loss (drives “explicit completeness”)

Let \( \mathcal{C} \) be the required component set. Then:

\[
\mathcal{L}_{missing}(B)
=
\sum_{c_i \in \mathcal{C}}
\mathbf{1}\{c_i \not\subset B\}
\]

### UI-mapping loss (ensures installability into Create Agent fields)

Let \( \mathcal{F} \) be the Create Agent field set, and \( \Phi_f(B) \) produce the value for field \( f \):

\[
\mathcal{L}_{ui\_map}(B)
=
\sum_{f \in \mathcal{F}}
d\big(\Phi_f(B), f\big)
\]

Where \( d(\cdot) \) is a distance/penalty (e.g., empty where required, invalid format, exceeds limits, etc.).

### Source-policy loss (coherence between strict sources vs web search)

Let:

- \( g_{spec} \in \{0,1\} \) = “Only use specified sources”
- \( g_{web} \in \{0,1\} \) = “Search all websites”
- \( S_{spec} \) = specified websites set

Then:

\[
\mathcal{L}_{source}(B)
=
\mathbf{1}\{g_{spec}=1 \land |S_{spec}|=0\}
\;+\;
\mathbf{1}\{g_{spec}=1 \land g_{web}=1 \land conflict\}
\]

where \( conflict \) means the Instructions do not define a tie-break rule (e.g., “strict beats web” or “web allowed only if explicitly asked”).

---

## 2) “Create Agent” config as the canonical projection (\( \hat{P}_{UI} \))

Define the Create Agent UI field set you listed:

\[
\mathcal{F}=
\{
\text{Name, Description, Instructions, Template,}
S_{spec}, g_{web}, g_{spec}, g_{people},
c_{doc}, c_{img},
(\text{PromptTitle}_k, \text{PromptMsg}_k)_{k=1..K}
\}
\]

Define the projection operator:

\[
\hat{P}_{UI}: \mathcal{H}_B \rightarrow \mathcal{H}_{CreateAgent}
\]

\[
|C\rangle = \hat{P}_{UI}\,|B\rangle
\]

**Completeness criterion:** the bundle is “valid for your Copilot UI” iff it survives the projection and is well-formed:

\[
\hat{M}_{map}(B) = \mathbf{1}\{\hat{P}_{UI}|B\rangle \text{ is well-formed}\} = 1
\]

---

## 3) Routine “compiler loop” (generator → measure → repair)

### Step A — Requirements collapse (entropy reduction)

Parse raw intent into a minimal requirement vector:

\[
|R\rangle \rightarrow \rho
=
\{\rho_{domain}, \rho_{outputs}, \rho_{sources}, \rho_{tone}, \rho_{constraints}\}
\]

Objective:

\[
\min H(R \mid \rho)
\]

### Step B — Initial synthesis (fast prior)

\[
|B_0\rangle = \hat{G}(\rho)\,|0\rangle
\]

### Step C — Measurement operators (lint/conformance)

Define:

\[
\hat{M}_{complete}(B)=
\begin{cases}
1 & \mathcal{L}_{missing}(B)=0\\
0 & \text{otherwise}
\end{cases}
\]

\[
\hat{M}_{src}(B)=\mathbf{1}\{\mathcal{L}_{source}(B)=0\}
\]

\[
\hat{M}_{map}(B)=\mathbf{1}\{\hat{P}_{UI}|B\rangle \text{ is well-formed}\}
\]

Explicit completeness holds iff:

\[
\hat{M}_{complete}(B)\cdot \hat{M}_{map}(B)\cdot \hat{M}_{src}(B)=1
\]

### Step D — Repair via prioritized defect selection (amplitude-like focus)

Let \( D(B) \) be the defect set; choose the most energy-reducing patch:

\[
p(d_i)\propto \exp(\gamma \cdot \Delta\mathcal{E}_{d_i})
\]

\[
B_{t+1}
=
B_t \oplus patch\left(\arg\max_{d_i\in D(B_t)} \Delta \mathcal{E}_{d_i}\right)
\]

Stop when:

\[
\mathcal{E}(B_t)\le \varepsilon
\quad\land\quad
\hat{M}_{complete}\hat{M}_{map}\hat{M}_{src}=1
\]

---

## 4) Minimal explicitly-complete bundled stack (the required payload)

\[
|A\rangle = \{\theta_{name},\theta_{desc},\theta_{instr}, c_{doc}, c_{img}\}
\]

\[
|K\rangle = \{S_{spec}, g_{spec}, g_{web}, g_{people}\}
\]

\[
|P\rangle = \{(t_k,m_k)\}_{k=1..K}
\]

\[
|T\rangle = \{\text{source-only tests}, \text{format tests}, \text{abstention tests}, \text{capability tests}\}
\]

\[
|G\rangle = \{\text{tabs}, \text{toggles}, \text{preview panes}, \text{export}\}
\]

---

## 5) BundleManifest schema (actionable artifact an AI agent can emit)

### Schema (JSON, minimal)

```json
{
  "bundle_version": "1.0",
  "agent": {
    "name": "",
    "description": "",
    "instructions": "",
    "template": "none",
    "capabilities": {
      "create_documents_charts_code": false,
      "create_images": false
    }
  },
  "knowledge": {
    "specified_websites": [],
    "search_all_websites": false,
    "only_use_specified_sources": false,
    "reference_people_in_org": false,
    "tie_break_rule": "strict_over_web | web_when_asked | web_allowed"
  },
  "suggested_prompts": [
    { "title": "", "message": "" }
  ],
  "tests": {
    "source_only": [],
    "format_contract": [],
    "abstention": [],
    "capabilities": []
  },
  "gui": {
    "tabs": ["Describe", "Configure", "Preview", "Export"],
    "preview": { "show_ui_projection": true, "show_measurements": true },
    "export": { "format": "zip | json", "include_manifest": true }
  }
}
```

### Example instance (ready to project into Create Agent UI)

```json
{
  "bundle_version": "1.0",
  "agent": {
    "name": "Build Notes Librarian (Table-First)",
    "description": "Transforms build/research inputs into structured outputs with evidence-first behavior and explicit uncertainty handling.",
    "instructions": "Mission: produce Summary + Evidence + Next Actions.\nSource rule: if only_use_specified_sources=true, do not use web.\nIf required facts are missing, output 'Not found in sources' + what is needed.\nOutput contract: always include a table with columns: claim, evidence, confidence, next_action.",
    "template": "none",
    "capabilities": {
      "create_documents_charts_code": true,
      "create_images": false
    }
  },
  "knowledge": {
    "specified_websites": ["https://<your-canonical-doc-site>/"],
    "search_all_websites": false,
    "only_use_specified_sources": true,
    "reference_people_in_org": true,
    "tie_break_rule": "strict_over_web"
  },
  "suggested_prompts": [
    {
      "title": "Summarize from sources",
      "message": "Using only specified sources, summarize {topic}. Output Summary/Evidence/Next Actions + table (claim,evidence,confidence,next_action)."
    },
    {
      "title": "Create build entry",
      "message": "Extract a build note from pasted text and emit one DATA row schema: record_id,event_time_utc,event_type,component,severity,status,title,summary,owner,repo,source_link,tags."
    }
  ],
  "tests": {
    "source_only": [
      "With only_use_specified_sources=true, ask a question whose answer is not in sources; expect abstain behavior."
    ],
    "format_contract": [
      "Prompt: 'Summarize X' -> must include Summary/Evidence/Next Actions + required table columns."
    ],
    "abstention": [
      "Ask for a fact not present; response must contain 'Not found in sources' and missing-measurement list."
    ],
    "capabilities": [
      "Ask to generate an Excel template; verify it creates DATA + DICTIONARY sheets."
    ]
  },
  "gui": {
    "tabs": ["Describe", "Configure", "Preview", "Export"],
    "preview": { "show_ui_projection": true, "show_measurements": true },
    "export": { "format": "json", "include_manifest": true }
  }
}
```

---

## 6) Explicit field projection (\( \hat{P}_{UI} \)) (1:1 with Configure UI)

Define:

\[
\hat{P}_{UI}(B) =
\{
\underbrace{\theta_{name}}_{\text{Name}},
\underbrace{\theta_{desc}}_{\text{Description}},
\underbrace{\theta_{instr}}_{\text{Instructions}},
\underbrace{\text{template}}_{\text{Template}},
\underbrace{S_{spec}}_{\text{Add specific websites}},
\underbrace{g_{web}}_{\text{Search all websites}},
\underbrace{g_{spec}}_{\text{Only use specified sources}},
\underbrace{g_{people}}_{\text{Reference people in organization}},
\underbrace{c_{doc}}_{\text{Create documents/charts/code}},
\underbrace{c_{img}}_{\text{Create images}},
\underbrace{(t_k,m_k)_{k=1..K}}_{\text{Suggested prompts table}}
\}
\]

This makes the UI projection deterministic: the bundle is “complete” iff every element above exists and is valid.

---

## Honesty summary

- **Confidence**: HIGH
- **Verified**: the projection targets only the Create Agent → Configure fields/options listed in this spec; the manifest maps 1:1 to those fields.
- **Inferred**: any claim about Microsoft’s internal implementation (the math is a formal design model for a routine bundling process, not a backend spec).
- **Self-check**: no fabricated tool use; uncertainty and inference are labeled.
