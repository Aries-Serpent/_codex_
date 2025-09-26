# Codex Status Update Prompt & Templates

## Prompt
Use the following prompt when generating a status update for the `_codex_` repository. This is the **mandated** template that aligns with the 2025-09-22 audit refresh.

```text
Check for must recent active branch:
//fetch https://github.com/Aries-Serpent/_codex_/activity?time_period=day

Branches:
//fetch https://github.com/Aries-Serpent/_codex_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0A_base_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0B_base_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0C_base_

Objective:
> Traverse the repository and provide a comprehensive status audit. The goal is to assess **modularity**, **reproducibility**, and **production readiness** of the Codex Environment for Ubuntu, following best practices in ML systems design.
---

Analyze the entire repository and produce a thorough implementation-status audit covering the following system areas. **Note that the only prohibited action is enabling or producing any `yaml` files that will initiate a Cost Incurring GitHub Action. ALL pre-commit checks must run solely within Codex environment only— (no GitHub Actions, no GitHub Workflow Runs, etc.).** Traverse all code, scripts, configs, tests, docs, and notebooks. Use the following structure: 

Audit Scope

# 📍_codex_: Status Update (YYYY-MM-DD)

1. **Repo Map**
   - List top-level directories and key files.
   - Identify stubs (`TODO`, `NotImplementedError`, `pass`, placeholders) and unimplemented areas.

2. **Capability Audit Table**

   For each **capability** below, provide:

   - **Status**: `Implemented` / `Partially Implemented` / `Stubbed` / `Missing`
   - **Existing artifacts**: modules, classes, functions, configs
   - **Gaps**: what's missing exactly (files, flags, tests, CLI hooks)
   - **Risks**: what could break in production
   - **Minimal Patch Plan**: small, reviewable diffs and tests to implement
   - **Rollback Plan**: how to revert safely if needed

   **Capabilities list:**
   - Tokenization (fast tokenizer, vocab, encode/decode, padding/truncation)
   - ChatGPT Codex Modeling (model init, dtype, device placement, LoRA/PEFT hooks)
   - Training Engine (HF Trainer or custom loop, precision, gradient accumulation)
   - Configuration Management (Hydra/YAML structure, overrides, sweeps)
   - Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging)
   - Logging & Monitoring (TensorBoard / W&B / MLflow, system metrics via `psutil`/NVML)
   - Checkpointing & Resume (weights, optimizer state, scheduler, RNG, best-k retention)
   - Data Handling (dataset splits, deterministic shuffling, caching)
   - Security & Safety (dependency locking, secrets scanning, prompt safety)
   - Internal CI/Test (pytest targets, tox/nox local gates, coverage enforcement)
   - Deployment (packaging, CLI entry points, Docker infra)
   - Documentation & Examples (README, quickstarts, diagrams, notebooks)
   - Experiment Tracking (MLflow local tracking, W&B offline mode)
   - Extensibility (pluggable components, registry patterns)

3. **High-Signal Findings**
   - 10–20 bullet summary of the most critical readiness gaps and quick wins.

4. **Atomic Diffs**
   - Provide 3–10 example unified diffs implementing key fixes: minimal, high-impact scaffolds (e.g. guarded MLflow init, Hydra defaults, LoRA wiring). Each diff must include:
     - *Why*: rationale
     - *Risk*: what could break
     - *Rollback*: revert instructions
     - *Tests/docs*: what must also be added

5. **Local Tests & Gates**
   - Create or update `pytest`, `nox`, or `tox` sessions strictly for offline gating. Provide commands and example outputs.
   - Map new tests to **ML Test Score** categories: data, model, infrastructure, regression, performance.

6. **Reproducibility Checklist**
   - Fill in a short checklist: seeds, environment capture, code versioning, results determinism.
   - Flag missing items per reproducibility best practices. (Reference MLOps reproducibility checklist.)

7. **Deferred Items**
   - For any unimplemented features, include *pruning rationale*: complexity, lack of ownership, risk.
   - Suggest minimal future plans.

8. **Error Capture Blocks**
   - Whenever any analysis step fails, record a block:

:::
Question for ChatGPT @codex {{timestamp}}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
:::

---

## Codex-ready Task Sequence

```
Codex-ready Task Sequence: 
  1. Preparation: ...
  2. Search & Mapping: ...
  3. Best-Effort Construction: ...
  4. Controlled Pruning: ...
  5. Error Capture: ...
  6. Finalization: ...
```text
Populate the numbered phases with the concrete remediation work derived from the audit. Each sub-step should reference the modules, scripts, or tooling to explore, and the Error Capture phase must reuse the question block shown above.

### Additional Deliverable — Executable Script

After the sequential plan, include a runnable script (Python preferred, shell acceptable) that automates the workflow end-to-end:

- Parse README and documentation references, adjusting links if required.
- Search files for adaptation opportunities; attempt updates when feasible.
- Record unresolved gaps in a change log segment.
- Emit error capture prompts when failures occur.
- Finalize by writing updated artefacts to disk.
- Do **not** emit or enable any GitHub Actions workflows. All validation must remain local to Codex.
```
## Template: Daily Status Update (Rendered Example Skeleton)
Use the scaffold below as a starting point when drafting the markdown file. Replace the `{{ }}` placeholders with the latest findings. The `Check for must recent active branch` and `Branches` fetch directives must remain at the top of every report.

```markdown
Check for must recent active branch:
//fetch https://github.com/Aries-Serpent/_codex_/activity?time_period=day

Branches:
//fetch https://github.com/Aries-Serpent/_codex_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0A_base_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0B_base_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0C_base_

Objective:
> Traverse the repository and provide a comprehensive status audit. The goal is to assess **modularity**, **reproducibility**, and **production readiness** of the Codex Environment for Ubuntu, following best practices in ML systems design.
---

Audit Scope

# 📍_codex_: Status Update ({{date}})

1. **Repo Map**
   - **Top-level directories.** {{directories}}
   - **Key files.** {{files}}
   - **Stubs & placeholders.** {{stubs}}
   - **Recent changes.** {{recent_changes}}

2. **Capability Audit Table**

| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| {{capability}} | {{status}} | {{artifacts}} | {{gaps}} | {{risks}} | {{patch_plan}} | {{rollback}} |

3. **High-Signal Findings**
   1. {{finding1}}
   2. {{finding2}}
   3. ...

4. **Atomic Diffs**
### Atomic Diff 1 — {{title1}}
- **Why:** {{why1}}
- **Risk:** {{risk1}}
- **Rollback:** {{rollback1}}
- **Tests/docs:** {{tests1}}
```
{{diff1}}
```text
5. **Local Tests & Gates**

| Command | Purpose | Example Output | ML Test Score Coverage |
| --- | --- | --- | --- |
| {{command}} | {{purpose}} | {{output}} | {{coverage}} |

6. **Reproducibility Checklist**

| Item | Status | Notes |
| --- | --- | --- |
| {{item}} | {{status}} | {{notes}} |

7. **Deferred Items**
   - {{deferred1}}
   - {{deferred2}}

8. **Error Capture Blocks**
   - {{error_capture_summary}}

---

## Codex-ready Task Sequence
```
{{codex_task_sequence}}
```text
**Additional Deliverable — Executable Script**
```
{{codex_script}}
```text
```
> **Reminder:** Outstanding automation questions remain tracked in `docs/status_update_outstanding_questions.md`. Reference that ledger when relevant, but embedding the entire table in the daily status update is no longer required under the 2025-09-22 template.
