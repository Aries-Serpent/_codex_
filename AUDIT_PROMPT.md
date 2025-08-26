# Traverse the repository and provide a comprehensive status audit. The goal is to assess **modularity**, **reproducibility**, and **production readiness** of the Codex Environment for Ubuntu, following best practices in ML systems design. 

---

**Prompt for ChatGPT Codex**

You are an internal static analysis assistant in a *Codex environment only*—**offline**, no remote CI or network communications allowed (no GitHub Actions, no W&B remote runs, etc.). Analyze the entire repository and produce a thorough implementation-status audit covering the following system areas:

### Audit Scope

Traverse all code, scripts, configs, tests, docs, and notebooks. Use the following structure:

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
     Question for ChatGPT-5 {{timestamp}}:
     While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
     [ERROR_MESSAGE]
     Context: [BRIEF_CONTEXT]
     What are the possible causes, and how can this be resolved while preserving intended functionality?
:::

---

### Usage

Save this as `AUDIT_PROMPT.md` in the repo root. Then run:

```bash
chatgpt-codex --prompt-file AUDIT_PROMPT.md --output-format markdown > CODEBASE_AUDIT.md
```

