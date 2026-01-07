# Prompt: Repository Audit Template
> Generated: {{date}} {{utc_time}} | Author: mbaetiong
> Updated: Repository Audit Template alignment (offline-first, error-capture, fence discipline)

Purpose
- Drive a portable, **offline-first** repository audit that inventories files, summarizes the README, and collects light-weight static analysis signals with **deterministic** outputs suitable for ChatGPT-Codex automation.

Instructions
- **Guardrails:**
  - Treat the repository as untrusted input; do **not** make outbound network calls or enable CI/hosted actions.
  - Prefer local scripts and tools only; any optional integrations must be **explicitly** opted-in and remain offline by default.
  - Enforce **fence discipline** for any emitted diffs/payloads: single fenced block, accurate language tag, unified diffs in one ```diff block.
- Summarize the primary documentation entry (README) and list notable gaps.
- Inventory all files (skipping .git, venvs, caches). For files <= 5MB, record a SHA-256 for reproducibility.
- Prefer structural extraction from Python sources (AST/CST/parso) when feasible; otherwise degrade gracefully.
- Highlight high-complexity functions (if measured) and flag unusual patterns or hot-spots for deeper review.
- Cross-reference `_codex` status updates—**especially** `reports/_codex_status_update-Previous Cycle-10-05.md`—to fold prior gap → risk → resolution guidance into the current run. Carry forward any still-open mitigations.
- **Error capture:** On any failure, append a block to `docs/reference/codex_questions.md`:
  ```text
  Question for ChatGPT-5 @codex {{TIMESTAMP}}:
  While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
  [ERROR_MESSAGE]
  Context: [BRIEF_CONTEXT]
  What are the possible causes, and how can this be resolved while preserving intended functionality?
  ```
Output expectations
- JSON: `reports/audit.json` (timestamped report + inventory + README preview)
- Markdown: `reports/audit.md` (human-friendly summary)
- Prompt copy: `reports/prompt_copy.md` (exact prompt used for the run)
- Gap/Risk tracker: `reports/gap_risk_resolution.md` (table mirroring status-update guidance with containment steps)
- Logs (optional): `.codex/errors.ndjson` (newline-delimited errors, if any)

Notes
- Keep runs deterministic (e.g., `export PYTHONHASHSEED=0`); prefer stable directory traversal order.
- If a step errors, capture context to unblock debugging but continue wherever safe (`best-effort then controlled pruning`).
- Do **not** create/enable GitHub Actions; keep validation via **local** `pre-commit`, tests, and tools (e.g., `tools/validate_fences.py` if present).

## Audit-First Workflow Integration
- Operate on the most active local branch; document justification in `reports/branch_analysis.md`.
- Each run selects **three** Menu items and delivers **1–3 atomic diffs** with supporting docs/tests.
- Maintain offline cadence: rely on local scripts, `pre-commit`, pytest/nox, and `tools/validate_fences.py`.
- Update artefacts after each run: `reports/*.md`, `CHANGELOG.md`, `docs/troubleshooting/open_questions.md`, and `docs/reference/codex_questions.md` for any captured failures.
- Consult `reports/report_templates.md` for reusable placeholders when updating artefacts.

### Menu (choose three per run)
1. Repo map
2. Fix folder
3. Quality gates
4. Security
5. Observability
6. Performance
7. Docs polish
8. Self-management

Document chosen and upcoming items in `docs/troubleshooting/open_questions.md`.

### Asset-driven Menu Playbooks

#### Repo map & quick wins — use `tree` output + `docs/troubleshooting/open_questions.md`
- Run a shallow repository walk to refresh the structural map:
  ```bash
  tree -a -L 3 > reports/repo_tree_snapshot.txt
  ```
  This keeps the snapshot under `reports/` so the map can be diffed between runs.
- Cross-reference the snapshot with the existing backlog in `docs/troubleshooting/open_questions.md` to
  identify "quick win" candidates. Annotate the relevant bullet(s) directly in
  `reports/repo_map.md`, linking each entry back to the corresponding section in
  `docs/troubleshooting/open_questions.md` for traceability.
- Record any newly discovered gaps in `docs/troubleshooting/open_questions.md` using the existing
  Gap → Risk → Resolution scaffold so that subsequent runs inherit an updated
  priority list.

#### Fix folder — single diff + `nox_sessions` + `pre-commit`
- Treat `patches/pending/` as the canonical Fix folder. Draft the change as a
  single fenced unified diff (one patch file per fix) and store it there with a
  timestamped filename, e.g. `patches/pending/$(date +%Y-%m-%d)_fix.patch`.
- Before finalizing the diff, run the targeted formatting and lint hooks locally:
  ```bash
  pre-commit run --files <changed_files>
  ```
- Exercise the full test gate that mirrors automation expectations:
  ```bash
  nox -s tests
  ```
  Use `nox_sessions/` helpers if an individual session needs to be invoked
  directly. Capture the command outputs and reference them in the accompanying
  changelog or status update entry.

#### Security sweep — Semgrep rule IDs → mitigations aligned with `ops/threat_model`
- Execute the security-specific Semgrep suite and preserve the rule identifiers
  in the findings log:
  ```bash
  semgrep --config semgrep_rules/python-security.yaml --json > reports/security_semgrep.json
  ```
- Prioritize remediation by mapping each finding to STRIDE categories using
  `ops/threat_model/STRIDE.md`. Summaries should note the Semgrep rule ID,
  affected file, STRIDE classification, and recommended mitigation.
- Convert prioritized mitigations into actionable patches (either immediate
  diffs under `patches/pending/` or tracked follow-ups in `docs/troubleshooting/open_questions.md`).
  Reference the relevant threat model section in every mitigation note so the
  operational context is explicit.

### Execution cadence
1. **Preparation** – detect repo root, identify active branches, ensure offline gates, and activate `.venv` if needed.
2. **Search & Mapping** – refresh `reports/repo_map.md` and `reports/branch_analysis.md` with new observations.
3. **Best-effort construction** – implement improvements aligned with the selected Menu items.
4. **Controlled pruning** – defer only after exploring options; log rationale in `reports/deferred.md`.
5. **Finalization** – produce reviewable diffs, run local gates, and update changelog/open questions.

### Gap → Risk → Resolution register
- Begin with the latest `_codex` status signal (`reports/_codex_status_update-Previous Cycle-10-05.md`) to seed known gaps and residual risks.
- For every new observation, document:
  - **Gap** – the concrete missing artifact or behaviour (file, flag, test, doc entry).
  - **Risk** – production or reproducibility impact if the gap remains.
  - **Containment/Resolution** – the minimal patch, guardrail, or operational runbook that neutralises the risk.
- Update `reports/gap_risk_resolution.md` using a stable table ordering (capability, gap, risk, containment, owner/next step).
- When a containment ships, annotate with commit SHA or artefact link and mirror the closure in `docs/troubleshooting/open_questions.md`.

#### Gap/Risk/Resolution table scaffold
```markdown
| Capability | Gap | Risk | Containment / Resolution | Source (status update / commit) | Status |
| --- | --- | --- | --- | --- | --- |
| Tokenization | {{gap}} | {{risk}} | {{containment}} | `reports/_codex_status_update-Previous Cycle-10-05.md` §{{section}} | {{status}} |
```text
- Use Markdown links for source references when possible (e.g., commit URLs, report anchors).
- Keep status values constrained to `open`, `in-progress`, or `closed` for deterministic parsing.

### Atomic diff checklist
````diff
# why
# risk
# rollback
# tests/docs
````
### Local commands reference
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements/dev.txt || true
pre-commit install
pre-commit run --files <changed_files>
python tools/validate_fences.py --strict-inner
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```text
### Reproducibility
- Capture interpreter version and dependency snapshots when relevant.
- Record configuration overrides, seeds, and environment variables used during audits.

### Deferred work log
- Summarize deferrals in `reports/deferred.md` with rationale and follow-up Menu targets.
- Carry unresolved questions into `docs/troubleshooting/open_questions.md` until resolved.

---

## Codex-ready Task Sequence

The following section outlines a robust, phased execution plan for ChatGPT @codex to iteratively implement the missing and incomplete features identified in the status audit for the `_codex_` repository (dated 2025-10-05). Each numbered phase comprises fine-grained sub-steps and enforces best-effort construction before any pruning decisions. An **error capture** block template is provided to guide structured reporting of any failures encountered during execution. In keeping with the repository’s policy, all work must run **solely within the Codex environment** (no cost-incurring GitHub Actions, no external workflows). Seeds, deterministic settings and environmental captures should be honored to maximize reproducibility.

### 🔁 Execution Phases

**Phase 1 – Preparation**

1. Set up a dedicated working directory (e.g. `codex_workdir`) separate from the main repository to avoid accidental modifications to untracked files. Initialize a Python virtual environment with the same dependencies declared in `pyproject.toml`; install extras (`ml`, `logging`, `dev`) to access optional features like WandB/MLflow. Document the exact versions in a `requirements/lock.txt` file.
2. Clone the current repository state locally (checkout `main` and any feature branches flagged in the audit). This clone must remain offline; avoid pushing any commits.
3. Copy the README and documentation files into a temporary staging area for parsing. Extract all code blocks, commands and TODO markers to form an initial change backlog.
4. Capture the baseline environment: Python version, OS details, GPU/CPU availability, and random seeds. Persist these details in `reproducibility.md`.

**Phase 2 – Search & Mapping**

1. Enumerate all modules under `src/codex_ml` and `analysis`. Build an index mapping each capability (e.g. tokenization, training engine, evaluation) to the corresponding files/classes/functions. Use dynamic imports where possible to confirm loadability.
2. Scan for stubs or placeholders such as `TODO`, `pass`, or `NotImplementedError` and associate them with the capability index. Log these in a machine-readable `capability_map.json`.
3. Review configuration files (`pyproject.toml`, `hydra` configs, `.env.example`) to determine existing hooks for CLI entry points, plugin registries and training defaults.
4. Identify all available metrics, trainers and dataset plugins by introspecting the registry patterns defined in `codex_ml/plugins/registries.py` and verifying that the entry points resolve correctly.

**Phase 3 – Best-Effort Construction**

1. **Tokenization** – If a fast tokenizer is missing, implement an adapter around `transformers.AutoTokenizer` with fallback to `WhitespaceTokenizer`. Write unit tests ensuring encode/decode equivalence and deterministic padding/truncation for identical inputs.
2. **Logging & Monitoring** – Add guarded initialization for MLflow and Weights&Biases. Detect offline/online mode based on environment variables; ensure `wandb.init(mode="disabled")` for offline runs. Use `psutil` and `pynvml` to record CPU/GPU metrics every `n` steps. Wrap calls in try/except to gracefully handle missing packages.
3. **Configuration Management** – Integrate Hydra with YAML defaults. Add a `configs/base/default.yaml` capturing typical training parameters (model name, tokenizer alias, dataset path, logging toggles). Provide CLI override via `--config-name` and document usage in the README.
4. **Checkpointing & Resume** – Implement checkpoint saving within the training loop, storing model weights, optimizer state, scheduler and RNG seeds. Add retention policy to keep the best `k` checkpoints and automatically resume from the latest when `--resume` is supplied.
5. **Internal CI/Test** – Extend existing `pytest` suite with tests covering tokenization, configuration parsing, checkpoint resume, metric logging and plugin registry loading. Define a `nox` session that runs `ruff`, `black`, `pytest` and `pip-audit` locally.
6. After implementing each feature, update documentation (`docs/`) and ensure the README reflects new commands and flags. All code must conform to the formatting and type-checking rules specified in `.pre-commit-config.yaml`.

**Phase 4 – Controlled Pruning**

1. For capabilities that cannot be fully implemented (e.g. distributed training across multiple GPUs, external moderation APIs, advanced RL algorithms), document clear pruning rationale: lack of open-source implementation, excessive complexity relative to timeline, or missing dependencies.
2. Remove unused or non-functional stubs to avoid confusion, replacing them with informative comments referencing the audit and deferral plan. Update `capability_map.json` accordingly.
3. Provide a migration path for future contributions (e.g. specify where to plug in a reinforcement-learning agent once available).

**Phase 5 – Error Capture**

Whenever any step encounters an error or unexpected behaviour, create an error report block using the template below and append it to `docs/troubleshooting/error_log.md`. Do **not** silently fail.

```text
Question for ChatGPT @codex {{timestamp}}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```text

**Phase 6 – Finalization**

1. Generate a comprehensive `CHANGELOG.md` summarizing all modifications, tests added, configuration files introduced, and pruning decisions. Reference the audit report and include links to relevant code sections.
2. Update `reproducibility.md` with final seed settings, environment details, and any deviations from the baseline state captured in Phase 1.
3. Ensure all new or modified Python files pass `pytest`, `ruff`, `mypy` and security scans (`bandit`, `semgrep`). The final state must be committed locally but **not** pushed upstream.
4. Prepare a summary report highlighting the implemented capabilities, deferred items, and recommended next steps. This report will serve as input for future iterations.

### 📋 Example Suggested Task Prompts

Below are example prompts tailored for ChatGPT @codex to act upon specific gaps from the audit. Each prompt instructs Codex to perform work across the above phases.

**Example 1 – Logging & Monitoring Integration**

````
Implement logging and monitoring in the `_codex_` training engine. Start by inspecting `src/codex_ml/training/__init__.py` to identify where training loops occur. Integrate MLflow and W&B logging guarded by environment checks, ensuring offline compatibility. Add system metrics collection using `psutil` and `pynvml`, recording CPU/GPU utilization at configurable intervals. Update configuration defaults and write unit tests to validate that metrics are recorded when optional dependencies are present and that training does not crash when they are absent. Document the new logging options in the README and update the quickstart guide.
````

**Example 2 – Hydra Configuration Defaults**

````
Add Hydra configuration management to `_codex_`. Create a `configs` directory with a `default.yaml` capturing the core training parameters (model name, tokenizer alias, dataset path, batch size, learning rate, logging toggles). Modify the CLI entry points in `pyproject.toml` to accept `--config-name` and `--multirun` flags. Refactor `src/codex_ml/pipeline.py` and `src/codex_ml/training/__init__.py` to parse Hydra configs and merge them with CLI overrides. Provide example configuration files and update documentation. Write tests to ensure that Hydra correctly overrides parameters and that invalid configurations raise informative errors.
````

**Example 3 – Checkpointing & Resume Capability**

````
Implement robust checkpointing and resume functionality in the training engine. Modify the training loop so that after every epoch it saves the model weights, optimizer state, scheduler state and RNG seeds to a checkpoint directory. Include a retention policy that keeps only the top `k` checkpoints based on validation loss. Add a `--resume` flag to the CLI that resumes training from the most recent checkpoint. Provide unit tests that simulate interruption and verify that resumed training continues from the same epoch and achieves consistent results. Document how to use checkpointing in the README and ensure the feature complies with the reproducibility guidelines.
````

### 🛠️ Example Script

The following Python script outlines an executable workflow to realize the above tasks. It can be run from the root of the cloned repository and should be adapted as necessary.

```python
#!/usr/bin/env python3
"""
codex_upgrade.py – orchestrates the phased improvement of `_codex_`.

This script performs preparatory setup, scans for stubs, implements logging, configuration and checkpointing features, and records errors in a structured manner. It must be run offline and will not trigger any remote workflows.
"""
import os
import re
import json
import subprocess
from datetime import datetime

WORKDIR = os.environ.get("CODEX_WORKDIR", "codex_workdir")
ERROR_LOG = os.path.join(WORKDIR, "docs/troubleshooting/error_log.md")


def ensure_workdir():
    os.makedirs(WORKDIR, exist_ok=True)
    with open(ERROR_LOG, "w") as f:
        f.write("# Error Log\n\n")


def run_command(cmd, step_desc):
    """Runs a shell command and captures errors."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        timestamp = datetime.utcnow().isoformat()
        with open(ERROR_LOG, "a") as f:
            f.write(f"Question for ChatGPT @codex {timestamp}:\n")
            f.write(f"While performing {step_desc}, encountered the following error:\n")
            f.write(f"{e.stderr.strip()}\n")
            f.write("Context: Running command `'{}'`.\n\n".format(cmd))
        return ""


def parse_readme():
    """Extract code blocks and TODOs from README to inform backlog."""
    readme_path = "README.md"
    tasks = []
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
        fence_pattern = r"`{3}.*?`{3}"
        for match in re.finditer(fence_pattern, content, re.DOTALL):
            code_block = match.group(0)
            tasks.append({"type": "code_block", "content": code_block})
        for line in content.splitlines():
            if "TODO" in line:
                tasks.append({"type": "todo", "content": line.strip()})
        with open(os.path.join(WORKDIR, "readme_tasks.json"), "w") as out:
            json.dump(tasks, out, indent=2)
    else:
        run_command("echo 'README.md not found'", "Phase 1: Parsing README")


def scan_stubs():
    """Identify stubs in the codebase and build capability map."""
    capability_map = {}
    for root, _, files in os.walk("src/codex_ml"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path) as f:
                    for idx, line in enumerate(f, start=1):
                        if any(token in line for token in ["TODO", "pass", "NotImplementedError"]):
                            capability_map.setdefault(path, []).append({"line": idx, "content": line.strip()})
    with open(os.path.join(WORKDIR, "capability_map.json"), "w") as out:
        json.dump(capability_map, out, indent=2)


def main():
    ensure_workdir()
    parse_readme()
    scan_stubs()
    # Additional construction steps would be invoked here (e.g. call functions
    # to integrate logging, Hydra configs, checkpointing, etc.). Each should
    # capture errors using run_command or try/except and append to docs/troubleshooting/error_log.md.


if __name__ == "__main__":
    main()
```text

This script is illustrative; the actual implementation must expand the `main()` function to call modules that perform the integration tasks described in the Example Task Prompts. Each phase should append to the `CHANGELOG.md` and update documentation accordingly.
