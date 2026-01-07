# [Prompt Template]: Intent Validation & Plan of Action Approval Gate
> Generated: 2025-11-11 07:12:59 UTC | Author: mbaetiong
> 🧠 Roles: [Primary: Execution Lead], [Secondary: Audit Orchestrator]
> ⚡ Energy: 5
> ⚛️ Physics:
> Path🛤️ [Assess → Plan → Execute → Verify]
> Fields🔄 [Eval/Train, Logging, Security, Docs]
> Patterns👁️ [Determinism, Offline-first, “No need to reinvent the wheel”]
> Redundancy🔀 [Unit+Integration+Artifacts]
> Balance⚖️ [Score gain vs. change risk]

---

## Assumptions (✓ confirmed, ? uncertain, ⚠️ needs clarification)
- ✓ Offline-first remains the default; deep web search is for research only (no network in runtime paths).
- ✓ Local gates (nox tests/lint/typecheck/docs/security) are canonical; CI changes out-of-scope.
- ✓ PR #2201 will merge or rebase to 0D_base_ before Iteration 1 to avoid drift.
- ✓ Scoring rubric: audit v1.4.0 (weights: functionality 0.25, consistency 0.20, tests 0.25, safeguards 0.15, documentation 0.15).
- ✓ Minimum coverage thresholds for new/updated modules this cycle: 95% lines/branches for Iterations 1–2; later target 96–99%.
- ✓ Dependency policy for pip-audit findings: fix where feasible; fail on High/Critical; warn-only + JSON artifact for others with documented allowlist and expiry.

---

## Open Questions → Resolved Answers (based on your feedback)
1) CLI framework for new evaluation/utility commands:
   - Selected: D) Hybrid — Typer primary (built on Click) with lightweight argparse adapters where embedding is needed.

2) Minimum coverage threshold for new modules (loop/eval/registry/CLI):
   - Selected: C) 95% (lines and branches).

3) pip-audit policy for non-exploitable or pinned transitive CVEs:
   - Selected: B) Warn-only with JSON artifact; fail on High/Critical.

4) Experiment config format for schema validation:
   - Selected: D) Support JSON + TOML (with JSONSchema as the single source of truth).

5) System metrics in logging registry (CPU/RAM/ETA) default behavior:
   - Selected: A) Disabled by default; enable via flag (e.g., --sys-metrics).

6) AST CLI target audience for outputs:
   - Selected: C) Hybrid (human-readable by default; --json produces machine-readable JSON/NDJSON).

7) Style normalization strategy for E501/E402/E741:
   - Selected: D) One-shot repo-wide autofix PR + opportunistic per-module fixes.

8) Docker baseline target:
   - Selected: A) CPU-only Dockerfile mirroring nox env.

---

## Finalized Specs (frozen for Iterations 1–3)
- Modules and Entrypoints:
  - Evaluation loop: src/codex_ml/evaluation/loop.py (pure-Python, CPU-safe, lazy heavy imports).
  - CLI: Typer application “codex-eval” with subcommands run, report; human by default; --json flag.
  - Logging: src/codex_ml/logging/registry.py integrated into train/eval loops; NDJSON default; MLflow optional/offline guarded via flags.
  - Checkpoint retention: best‑k implementation with atomic metadata writes and safe deletion.
  - Security gate: nox -s security runs pip-audit; emits artifacts/security_report.json; fails on High/Critical; documents allowlist with expiry tags.
  - Config schema: configs/experiments/*.json and *.toml supported; JSONSchema in configs/schemas/experiments.schema.json; tools/validate_experiments.py validates both formats; nox session validate-configs.
  - Determinism: tests/repro/* for cross-process reproducibility with seeded loaders; env snapshot captured.
  - CPU Docker: docker/Dockerfile.cpu mirrors nox env; docs/deploy/cpu_local.md; default CMD runs pytest or nox.

- Coverage Targets:
  - Iterations 1–2: ≥95% lines/branches on new/modified modules (loop/eval/registry/CLI/checkpointing/schema/AST CLI).
  - Post-Iteration Prompt (next cycle): 96–99% focus via additional integration and edge-case tests.

---

## Phases of Action

### Phase 0 — Research & Alignment (no code, research artifacts included below)
Objective: Curate “no-reinventing” OSS patterns and finalize execution specs.
- Steps:
  - Deep web research on: robust PyTorch evaluation loops; pip-audit + nox policy; atomic best‑k retention; Typer modular CLI; JSON/TOML + JSONSchema validation; determinism recipes; CPU-only Docker mirroring local nox/pytest.
  - Freeze module names, flags, CLI interface, schema layout, and acceptance criteria.
- Decision gate: This document approved with resolved answers and specs.
- Effort/deps: 0.5–1 day.

### Phase 1 — Iteration 1 (Eval loop + logging wiring + pip‑audit + best‑k retention)
Objective: Land core execution path upgrades with tests and security gates (≥95% coverage).
- Tasks:
  - Implement evaluation.loop and Typer CLI (“codex-eval run …”; “codex-eval report …”).
  - Wire logging registry into train/eval loops; add optional system metrics via flag.
  - Implement best‑k retention with atomic metadata (write temp + os.replace) and safe deletions.
  - Add nox -s security: pip-audit; JSON artifact; fail on High/Critical; allowlist with expiry.
  - Tests: unit + integration for eval loop; logging wiring; best‑k pruning; golden JSON outputs; coverage ≥95%.
  - Docs: docs/api/loop_eval.md; docs/security/safeguards.md.
- Decision gate: All new tests ≥95%; nox security gate produces artifact; zero breaking changes; updated audit artifacts committed.

### Phase 2 — Iteration 2 (Quickstart + config schema + AST CLI integration)
Objective: Make the system discoverable and reproducible end-to-end (≥95% coverage).
- Tasks:
  - Write docs/quickstart_local_training.md covering tokenization → data → model → train → eval → checkpoint → report.
  - Add JSON+TOML experiment configs; JSONSchema + validator tool; nox validate-configs.
  - Enhance AST CLI subcommands (analyze/audit/diff), add --json output; stable exit codes; integration tests.
  - Update docs/ops/promotion_checklist.md to reflect new gates.
- Decision gate: Docs approved; schema validator green on samples; AST CLI tests pass; artifacts updated; coverage ≥95%.

### Phase 3 — Iteration 3 (Style normalization + determinism polish + CPU Dockerfile)
Objective: Maximize consistency and reproducibility; reduce friction to run.
- Tasks:
  - One-shot style pass: E501 (line length), targeted E402, E741 rename; update ruff config if needed.
  - Determinism tests: cross-process reproducibility suite; env snapshot gates; manifest hash chain proved.
  - Add docker/Dockerfile.cpu; docs/deploy/cpu_local.md; smoke test Quickstart inside container.
- Decision gate: Lint/typecheck clean; determinism tests pass; Docker build + Quickstart run OK.

---

## Risks and Mitigations
| Risk | Severity | Mitigation |
|---|---|---|
| Over-broad style changes create merge conflicts | Medium | Isolate in Phase 3; rebase early; small focused commits |
| pip-audit flags transient CVEs | Medium | Pin/upgrade; allowlist with rationale + expiry; rerun before merge |
| CLI contract churn | Low | Spec locked here; provide --json and robust help; add integration tests |
| Template/hash drift in audit artifacts | Low | Regenerate artifacts in single deterministic run; avoid manual post-edit edits |
| Optional MLflow dependency friction | Low | Keep disabled by default; lazy import; document usage and offline constraints |

---

## Deliverables
- Phase 0: Research notes + finalized specs; Open Question selections (this file).
- Phase 1: evaluation.loop + CLI; logging wiring; best‑k retention; pip-audit nox session; tests (≥95%); API doc; security artifact.
- Phase 2: Quickstart doc; experiments JSONSchema + samples (JSON+TOML); validator + nox session; AST CLI enhancements + tests (≥95%).
- Phase 3: Style normalization PR; determinism test suite; CPU Dockerfile + deployment doc.
- Final: Updated audit_artifacts (raw/scored/context/manifest), daily status report, coverage summaries, acceptance checklist.

---

## Acceptance Criteria
- This plan approved; answers frozen.
- New/changed code paths have ≥95% coverage; coverage report attached.
- Security gate emits artifacts/security_report.json and enforces fail-on High/Critical.
- Quickstart reproduces end-to-end workflow on CPU-only env; passes locally.
- AST CLI hybrid output works (human by default, --json for machines) with stable exit codes.
- Lint/typecheck clean; Docker CPU image builds and runs Quickstart successfully.
- Audit composite score shows uplift with updated capabilities_scored.json.

---

## Research Notes (Deep web search; reused patterns with citations)

### Robust PyTorch evaluation loop and metrics logging
A minimal and robust PyTorch evaluation loop should focus on clarity, correctness, and efficient metrics logging. Here are the best practices distilled from leading resources:

### 1. Core Evaluation Loop Structure
- Switch model to evaluation mode: Use model.eval() before starting so layers like Dropout and BatchNorm behave consistently.
- Disable gradients: Wrap evaluation with torch.no_grad() to save memory and compute.
- Iterate over validation/test dataloader: Send batches to device (CPU/GPU), perform forward pass.
- Accumulate predictions and targets: For metrics, gather all predictions and true labels if feasible (memory permitting).
- Compute loss and metrics per batch (or whole epoch): Log batch/epoch loss and other metrics like accuracy, F1, etc.
- Restore training mode after evaluation: Use model.train() for subsequent training phases[1](https://www.compilenrun.com/docs/library/pytorch/pytorch-training-loop/pytorch-validation-loop/)[[2]](https://www.slingacademy.com/article/how-to-write-a-pytorch-testing-loop/)[[3]](https://apxml.com/courses/getting-started-with-pytorch/chapter-6-implementing-training-loop/implementing-evaluation-loop)[[4]](https://www.slingacademy.com/article/analyzing-model-performance-with-pytorch-testing-loops/)[[5]](https://www.codegenes.net/blog/pytorch-validation-loop/).

Sample Pattern:
```python
def evaluate(model, data_loader, criterion, device):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    all_targets, all_preds = [], []

    with torch.no_grad():
        for inputs, targets in data_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            correct += (predicted == targets).sum().item()
            total += targets.size(0)
            all_targets += targets.cpu().tolist()
            all_preds += predicted.cpu().tolist()
    val_loss = running_loss / total
    val_acc = correct / total
    return val_loss, val_acc, all_targets, all_preds
```text
This pattern can be extended to log additional metrics[5](https://www.codegenes.net/blog/pytorch-validation-loop/)[[1]](https://www.compilenrun.com/docs/library/pytorch/pytorch-training-loop/pytorch-validation-loop/)[[4]](https://www.slingacademy.com/article/analyzing-model-performance-with-pytorch-testing-loops/).

---

### 2. Best Practices for Metrics Logging

- Systematic Logging: Track key metrics like loss, accuracy, F1-score, etc., at epoch or batch level. Use Python's logging, TensorBoard, or tools like Weights & Biases for visualization and comparison[6](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/logging-metrics-training-evaluation)[[7]](https://www.geeksforgeeks.org/deep-learning/monitoring-model-training-in-pytorch-with-callbacks-and-logging/).
- Avoid Redundant Boilerplate: Use dictionaries or objects to store metrics, making code more extensible and avoid metric-specific lists. For example:
    ```python
    metrics = {'loss': [], 'accuracy': [], 'f1': []}
    # During loop
    metrics['loss'].append(batch_loss)
    # After epoch, compute mean and log
    ```
- Compute on GPU Where Possible: For large datasets or complicated metrics (e.g., confusion matrix, F1), do in-place aggregation with PyTorch tensors before moving results to CPU for final calculation. Directly use torch ops for metrics like accuracy to reduce CPU transfer overhead[8](https://stackoverflow.com/questions/56643503/efficient-metrics-evaluation-in-pytorch)[[9]](https://discuss.pytorch.org/t/best-practices-for-collecting-metrics/181881).

- Use Established Libraries for Complex Metrics: Libraries like torchmetrics or frameworks like PyTorch Lightning abstract much metric handling and logging with callback systems, making it easy to extend and log dozens of metrics without boilerplate[9](https://discuss.pytorch.org/t/best-practices-for-collecting-metrics/181881).
- Keep Logging Frequency Reasonable: Logging every batch can be noisy; prefer epoch-level logging unless you need fine-grained debugging.

- Integrate with Visualization Tools: Use TensorBoard or W&B for better analysis and model comparison. PyTorch offers native TensorBoard support for scalars, histograms, images, etc.[6](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/logging-metrics-training-evaluation).

---

### 3. Additional Recommendations

- Early Stopping & Checkpoints: Monitor validation metrics for stopping training and saving best models.
- OOP/Callback Pattern: Consider encasing logging in a callback-like structure or class, especially when handling multiple metrics, as in custom logger classes[7](https://www.geeksforgeeks.org/deep-learning/monitoring-model-training-in-pytorch-with-callbacks-and-logging/).
- Reproducibility: Log all relevant hyperparameters and random seeds.

---

### Resources & References
- Example minimal validation loop and metric logging: CompileNRun, CodeGenes, SlingAcademy[1](https://www.compilenrun.com/docs/library/pytorch/pytorch-training-loop/pytorch-validation-loop/)[[5]](https://www.codegenes.net/blog/pytorch-validation-loop/)[[4]](https://www.slingacademy.com/article/analyzing-model-performance-with-pytorch-testing-loops/)
- Efficient metrics evaluation and aggregation on GPU: StackOverflow, PyTorch Forums[8](https://stackoverflow.com/questions/56643503/efficient-metrics-evaluation-in-pytorch)[[9]](https://discuss.pytorch.org/t/best-practices-for-collecting-metrics/181881)
- Logging best practices: apxml.com, GeeksforGeeks[6](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/logging-metrics-training-evaluation)[[7]](https://www.geeksforgeeks.org/deep-learning/monitoring-model-training-in-pytorch-with-callbacks-and-logging/)

---

Summary:  
A minimal and robust PyTorch evaluation loop requires correct mode setting, efficient metric computation, and systematic logging. For many metrics or complex workflows, leveraging libraries like torchmetrics or frameworks like PyTorch Lightning can reduce boilerplate and keep your code extensible and maintainable.[1](https://www.compilenrun.com/docs/library/pytorch/pytorch-training-loop/pytorch-validation-loop/)[[5]](https://www.codegenes.net/blog/pytorch-validation-loop/)[[6]](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/logging-metrics-training-evaluation)[[9]](https://discuss.pytorch.org/t/best-practices-for-collecting-metrics/181881)[[8]](https://stackoverflow.com/questions/56643503/efficient-metrics-evaluation-in-pytorch)

---

1. [PyTorch Validation Loop - Compile N Run](https://www.compilenrun.com/docs/library/pytorch/pytorch-training-loop/pytorch-validation-loop/)
2. [How to Write a PyTorch Testing Loop - Sling Academy](https://www.slingacademy.com/article/how-to-write-a-pytorch-testing-loop/)
3. [PyTorch Evaluation Loop | Model Testing - apxml.com](https://apxml.com/courses/getting-started-with-pytorch/chapter-6-implementing-training-loop/implementing-evaluation-loop)
4. [Analyzing Model Performance with PyTorch Testing Loops](https://www.slingacademy.com/article/analyzing-model-performance-with-pytorch-testing-loops/)
5. [Mastering the PyTorch Validation Loop — codegenes.net](https://www.codegenes.net/blog/pytorch-validation-loop/)
6. [Log Metrics in PyTorch Training - apxml.com](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/logging-metrics-training-evaluation)
7. [Monitoring Model Training in PyTorch with Callbacks and Logging](https://www.geeksforgeeks.org/deep-learning/monitoring-model-training-in-pytorch-with-callbacks-and-logging/)
8. [Efficient metrics evaluation in PyTorch - Stack Overflow](https://stackoverflow.com/questions/56643503/efficient-metrics-evaluation-in-pytorch)
9. [Best practices for collecting metrics - PyTorch Forums](https://discuss.pytorch.org/t/best-practices-for-collecting-metrics/181881)

---

### pip-audit in Nox; fail on High/Critical

To use pip-audit in a Nox session and fail the session if high or critical vulnerabilities are found, you need to do the following:

1. Install pip-audit inside the Nox session:  
   Ensure pip-audit is installed in the Nox-managed environment, so you can call its CLI.

2. Run pip-audit and output results in JSON:  
   Use the -f json argument for machine-readable results.

3. Parse the JSON to check severity levels:  
   Since pip-audit itself does not have a built-in "fail on severity" option, you must parse the output to look for vulnerabilities with severity "high" or "critical". If found, fail the session.

Below is a practical example noxfile.py illustrating these steps:

```python
import nox
import json

@nox.session
def audit(session):
    session.install("pip-audit")
    # Run pip-audit, outputting JSON
    result = session.run("pip-audit", "-f", "json", external=True, stdout=subprocess.PIPE)
    # Parse results
    vulnerabilities = json.loads(result)
    high_or_critical_found = any(
        vuln.get('severity') in ("HIGH", "CRITICAL")
        for pkg in vulnerabilities
        for vuln in pkg.get("vulns", [])
    )
    if high_or_critical_found:
        session.error("High or critical vulnerabilities found! Failing session.")
```text

### Notes:

- You may need to adjust subprocess usage, depending on your Nox version (stdout=subprocess.PIPE is an example).
- You can also run against a requirements.txt file with:  
  session.run("pip-audit", "-r", "requirements.txt", "-f", "json", external=True, ...)
- session.error() will terminate and fail the session if vulnerabilities of specified severity are found.

### Why This Works & Best Practices

- pip-audit is designed to scan installed packages (or requirements file) for known vulnerabilities using various databases[1](https://pypi.org/project/pip-audit/)[[2]](https://github.com/pypa/pip-audit)[[3]](https://github.com/pypa/pip-audit/blob/main/README.md).
- The JSON output lets you programmatically inspect vulnerability severity, making it easier to enforce strict policies in automated test environments like Nox[3](https://github.com/pypa/pip-audit/blob/main/README.md).
- Failing your session on high/critical vulnerabilities helps "shift left" your supply-chain security, catching issues before deployment or release[4](https://dev.to/jakeespinosa/pip-audit-managing-pip-vulnerabilities-kbg)[[5]](https://www.packetcoders.io/how-to-check-your-python-dependencies-for-vulnerabilities/).

### Documentation & References

- [pip-audit documentation and CLI options](https://github.com/pypa/pip-audit)[2](https://github.com/pypa/pip-audit)[[3]](https://github.com/pypa/pip-audit/blob/main/README.md)
- [Nox documentation for session management and error handling](https://nox.thea.codes/en/stable/index.html)[6](https://nox.thea.codes/en/stable/index.html)[[7]](https://nox.thea.codes/en/stable/usage.html)
- [Dev Community article on pip-audit usage](https://dev.to/jakeespinosa/pip-audit-managing-pip-vulnerabilities-kbg)[4](https://dev.to/jakeespinosa/pip-audit-managing-pip-vulnerabilities-kbg)

Let me know if you need a more advanced example, such as parsing or filtering specific vulnerability IDs or exporting results!

---

1. [pip-audit · PyPI](https://pypi.org/project/pip-audit/)
2. [GitHub - pypa/pip-audit: Audits Python environments, requirements files ...](https://github.com/pypa/pip-audit)
3. [pip-audit/README.md at main · pypa/pip-audit · GitHub](https://github.com/pypa/pip-audit/blob/main/README.md)
4. [pip-audit: Managing pip Vulnerabilities - DEV Community](https://dev.to/jakeespinosa/pip-audit-managing-pip-vulnerabilities-kbg)
5. [How to Check Your Python Dependencies for Vulnerabilities](https://www.packetcoders.io/how-to-check-your-python-dependencies-for-vulnerabilities/)
6. [Welcome to Nox — Nox Previous Cycle.10.16 documentation](https://nox.thea.codes/en/stable/index.html)
7. [Command-line usage — Nox Previous Cycle.10.16 documentation](https://nox.thea.codes/en/stable/usage.html)

---

### Safe best‑k checkpoint retention (atomic deletion pattern)
A safe and robust "best-k checkpoint retention deletion pattern" in Python ensures that only the most recent k "best" checkpoints (based on a metric, such as validation loss or accuracy) are retained, while older/unneeded checkpoints are deleted in such a way that you never end up in a partially-deleted state due to interruptions or race conditions. This pattern is widely used when disk space or cloud storage is a concern and your training script needs to keep only the best few checkpoints over multiple epochs or steps.

### Key Principles

1. Atomic Deletion: To avoid issues from interruptions or simultaneous training runs, first save the new checkpoint, update your list of retained checkpoints, then delete old checkpoints only after confirming the list has been updated.
2. Sorting and Pruning: Always sort your available checkpoints by their relevant metric and timestamp, keeping the top k, and deleting anything older.
3. Separate Last/Best Checkpoints: Many frameworks allow you to keep both the single "last" (most recent) checkpoint and the best k checkpoints as distinct concepts for robustness in resuming interrupted training[1](https://github.com/Lightning-AI/pytorch-lightning/issues/2141)[[2]](https://deepwiki.com/PINTO0309/gazelle-dinov3/4.6-checkpoint-management)[[3]](https://deepwiki.com/ostris/ai-toolkit/15-model-saving-and-checkpointing)[[4]](https://deepwiki.com/huggingface/accelerate/7.3-project-configuration-and-checkpoint-management).

### Safe Implementation Steps

Here’s an outline and code pattern for atomic best-k retention in Python (for local or cloud storage):

#### 1. Save Checkpoint
After an epoch, save a new checkpoint (`checkpoint_N.pt`, with associated metric metadata in a file or separate index).

#### 2. Update Index/Metadata
Maintain a metadata file (JSON, YAML, Pickle, etc.) storing a list of checkpoint paths and their metrics, update it atomically after each save using something like write-to-temp-and-rename.

#### 3. Find Top k
On each new checkpoint save, load/check the metadata, sort the available checkpoints (e.g., by metric, then timestamp), and keep only the top k entries.

#### 4. Delete Excess (Atomically)
After successfully saving and updating the index, delete files not in the new top k list, using file system atomicity (os.remove is atomic for most local disk/file systems). For cloud, ensure you handle partial failures gracefully and verify after deletion.

Here's a simplified sample code pattern:

```python
import os
import json

def save_checkpoint(state_dict, metric, checkpoint_dir, metadata_file, k=5):
    # Save new checkpoint
    checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_{metric:.4f}.pt")
    torch.save(state_dict, checkpoint_path)

    # Load old metadata
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
    else:
        metadata = []

    # Update metadata (add new checkpoint)
    metadata.append({"path": checkpoint_path, "metric": metric})
    metadata = sorted(metadata, key=lambda x: x["metric"])[:k]  # lower metric=better, top-k

    # Atomically update metadata
    temp_file = metadata_file + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(metadata, f)
    os.replace(temp_file, metadata_file)

    # Delete old checkpoints not in top k
    valid_paths = set(item["path"] for item in metadata)
    # ... compute obsolete list from previous index if needed and delete safely
```text

### Framework Examples

- PyTorch Lightning supports save_top_k and save_last options, and deletes old checkpoints automatically while keeping the process robust to interruptions[1](https://github.com/Lightning-AI/pytorch-lightning/issues/2141).
- AI Toolkit and Hugging Face Accelerate offer native retention configurations which clean up older checkpoints based on max_to_keep settings, using similar mechanisms[3](https://deepwiki.com/ostris/ai-toolkit/15-model-saving-and-checkpointing)[[4]](https://deepwiki.com/huggingface/accelerate/7.3-project-configuration-and-checkpoint-management).

### Additional Context and Best Practices

- For cloud storage, batch or multiphase deletion and eventual consistency checks are recommended for atomicity.
- Always handle exceptions in the deletion phase to avoid unintentionally deleting recent/best checkpoints.
- Keep checkpoint metadata (metrics, paths) outside the checkpoint files for easier management.
- If you use frameworks, prefer their built-in callback patterns for checkpoint retention, as these have been tested for atomicity and race conditions.

### References and More Reading

- DeepWiki: Checkpoint Management for code patterns and pruning policies[2](https://deepwiki.com/PINTO0309/gazelle-dinov3/4.6-checkpoint-management)
- PyTorch Lightning GitHub Issue discussing retention logic[1](https://github.com/Lightning-AI/pytorch-lightning/issues/2141)
- Model saving and checkpointing in AI Toolkit, Hugging Face Accelerate config patterns[3](https://deepwiki.com/ostris/ai-toolkit/15-model-saving-and-checkpointing)[[4]](https://deepwiki.com/huggingface/accelerate/7.3-project-configuration-and-checkpoint-management)

If you're dealing with very large files or mission-critical checkpoints, consider writing checkpoint files to a staging area and renaming them into place for even greater safety.

If you need a pattern for cloud-specific atomic deletion, or integration with frameworks (TensorFlow, Hugging Face, etc.), let me know the specifics!

---

1. [`save_last` should only keep the most recent checkpoint (along with the ...](https://github.com/Lightning-AI/pytorch-lightning/issues/2141)
2. [Checkpoint Management | PINTO0309/gazelle-dinov3 | DeepWiki](https://deepwiki.com/PINTO0309/gazelle-dinov3/4.6-checkpoint-management)
3. [Model Saving and Checkpointing | ostris/ai-toolkit | DeepWiki](https://deepwiki.com/ostris/ai-toolkit/15-model-saving-and-checkpointing)
4. [Project Configuration and Checkpoint Management | huggingface ...](https://deepwiki.com/huggingface/accelerate/7.3-project-configuration-and-checkpoint-management)

---

### Typer CLI structure with subcommands (best practices)
When structuring a Typer CLI app with subcommands in Python, following best practices ensures your command-line application is maintainable, scalable, and user-friendly. Here’s a synthesis of the recommended strategies, patterns, and code organization tips from top resources:

## 1. Modular Structure: Split Commands Into Separate Modules

For larger CLI apps, break down your commands and subcommands into different Python modules or files. Each module can define related commands using a Typer instance; your main app then imports and combines them using app.add_typer():

```python
# commands/create.py
import typer
create_app = typer.Typer()

@create_app.command()
def user(name: str):
    typer.echo(f"Creating user {name}")

@create_app.command()
def item(name: str):
    typer.echo(f"Creating item {name}")

# main.py
import typer
from commands.create import create_app

app = typer.Typer()
app.add_typer(create_app, name="create")

if __name__ == "__main__":
    app()
```text
This enables hierarchical and nested commands, e.g., python main.py create user John[1](https://pytutorial.com/python-typer-subcommands-and-modular-cli/)[[2]](https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/).

## 2. Use Groups and Nested Subcommands for Scalability

Typer supports deeply nested command groups, allowing you to separate concerns and provide logical organization (like git remote add). Use add_typer recursively to build nested structures:

```python
app.add_typer(sub_app, name="subgroup")
```text
This way, each part of your app is easy to maintain and expand[3](https://typer.tiangolo.com/tutorial/subcommands/)[[2]](https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/).

## 3. Only Use Explicit Command Names for Larger Interfaces

If your CLI has only one command, Typer will optimize and let users call it directly (no extra command name required). But with multiple commands or subcommands, provide clear, descriptive names and usage text to guide users[4](https://stackoverflow.com/questions/79486643/python-command-line-tool-with-subcommands-in-typer-how-do-i-include-a-typer-in)[[5]](https://www.projectrules.ai/rules/typer).

## 4. Provide Consistent Help Text and Metadata

Typer auto-generates help, but you should use the help argument in add_typer and command decorators to make your CLI self-explanatory. Add docstrings for each command function:

```python
@app.command(help="Create a new user")
def user(name: str):
    """Create a user by name."""
    ...
```text
This keeps your CLI discoverable and friendly[1](https://pytutorial.com/python-typer-subcommands-and-modular-cli/)[[6]](https://coderivers.org/blog/typer-python/).

## 5. Leverage Type Hints Throughout

Typer uses Python type hints for argument parsing and validation, which improves code readability, IDE auto-completion, and error handling.

## 6. Group Related Commands and Use Consistent Naming

Commands should each perform a single, well-defined task. Group related commands logically, and follow a consistent naming scheme so users can guess functionality intuitively.

## 7. Testing and Error Handling

Test your CLI using Typer’s CliRunner together with pytest. Handle errors with appropriate messages using try/except blocks, and consider integrating logging for debugging and operational visibility[7](https://realpython.com/python-typer-cli/)[[5]](https://www.projectrules.ai/rules/typer).

## 8. Common Patterns

- Main entry point: Use if __name__ == "__main__": app() only in your script entry point.
- Options and arguments: Use typer.Option for named options and default values.
- Documentation: Write clear docstrings and make use of Typer’s automatic documentation features.

---

Resources for further learning and examples:

- Typer official documentation on subcommands and nested subcommands[3](https://typer.tiangolo.com/tutorial/subcommands/)[[2]](https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/)
- PyTutorial’s Typer modular CLI guide[1](https://pytutorial.com/python-typer-subcommands-and-modular-cli/)
- Real Python Typer tutorials covering project layout, testing, and code organization[7](https://realpython.com/python-typer-cli/)
- CodeRivers Typer best practices summary[6](https://coderivers.org/blog/typer-python/)
- DMAC.Tech’s Typer CLI app design discussion[8](https://blog.dmac.tech/posts/python-typer-powerful-cli-apps/)
- Stack Overflow for practical structuring tips[4](https://stackoverflow.com/questions/79486643/python-command-line-tool-with-subcommands-in-typer-how-do-i-include-a-typer-in)

By following these guidelines, your Typer CLI app will remain well-organized, user-friendly, and ready for future expansion.

---

1. [Python Typer Subcommands and Modular CLI - PyTutorial](https://pytutorial.com/python-typer-subcommands-and-modular-cli/)
2. [Nested SubCommands - Typer](https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/)
3. [SubCommands - Command Groups - Typer](https://typer.tiangolo.com/tutorial/subcommands/)
4. [Python command line tool with subcommands in typer - Stack Overflow](https://stackoverflow.com/questions/79486643/python-command-line-tool-with-subcommands-in-typer-how-do-i-include-a-typer-in)
5. [Typer CLI Best Practices and Coding Standards - Project Rules](https://www.projectrules.ai/rules/typer)
6. [Mastering Typer in Python: A Comprehensive Guide](https://coderivers.org/blog/typer-python/)
7. [Build a Command-Line To-Do App With Python and Typer](https://realpython.com/python-typer-cli/)
8. [Python Typer: Powerful CLI Apps | DMAC.tech](https://blog.dmac.tech/posts/python-typer-powerful-cli-apps/)

---

### Validate TOML and JSON against JSON Schema
To validate TOML and JSON configuration files against a JSON Schema in Python, you can follow these steps:

---

### 1. Load TOML and JSON Configurations into Python Dictionaries

- TOML: Use the built-in tomllib (Python 3.11+) or tomli for earlier versions.
    ```python
    import tomllib  # Python 3.11+
    with open("config.toml", "rb") as f:
        toml_data = tomllib.load(f)
    ```

- JSON: Use the standard json library.
    ```python
    import json
    with open("config.json") as f:
        json_data = json.load(f)
    ```

---

### 2. Load the JSON Schema

Schemas are typically stored in files, e.g. schema.json:
```python
with open("schema.json") as f:
    schema = json.load(f)
```text

---

### 3. Validate Configurations Using jsonschema

- jsonschema: The most popular library for validation in Python.
    ```python
    from jsonschema import validate, ValidationError

    try:
        validate(instance=json_data, schema=schema)
        print("JSON config is valid!")
    except ValidationError as e:
        print("JSON config is invalid:", e)

    try:
        validate(instance=toml_data, schema=schema)
        print("TOML config is valid!")
    except ValidationError as e:
        print("TOML config is invalid:", e)
    ```
- The schema's definitions must correspond to the resultant Python objects, e.g., TOML tables as JSON objects, arrays as lists, etc. There are a few caveats on how TOML types map to JSON types, but in general, it's a straightforward one-to-one mapping for core types, as discussed by the TOML community[1](https://github.com/toml-lang/toml/discussions/1038)[[2]](https://realpython.com/python-toml/)[[3]](https://json-schema-everywhere.github.io/toml).

---

### 4. Using Multi-Format Validators (Optional for Automation)

If you want to validate TOML, JSON, and even YAML configs automatically (e.g., in CI/pre-commit workflows), you can use tools like check-jsonschema:
- Install: pip install check-jsonschema
- CLI Example:
    ```shell
    check-jsonschema --schemafile schema.json config.toml config.json
    ```
This tool supports JSON, YAML, TOML, and JSON5 files, and integrates with pre-commit for development workflows[4](https://deepwiki.com/python-jsonschema/check-jsonschema/1-overview)[[5]](https://deepwiki.com/python-jsonschema/check-jsonschema/3-command-line-interface).

---

### References and Further Reading
- [Official jsonschema documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/)[6](https://python-jsonschema.readthedocs.io/en/stable/validate/)
- [Real Python: Working with TOML](https://realpython.com/python-toml/)[2](https://realpython.com/python-toml/)
- [Stack Overflow Example on JSON Validation](https://stackoverflow.com/questions/54491156/validate-json-data-using-python)[7](https://stackoverflow.com/questions/54491156/validate-json-data-using-python)
- [DeepWiki: check-jsonschema overview](https://deepwiki.com/python-jsonschema/check-jsonschema/1-overview)[4](https://deepwiki.com/python-jsonschema/check-jsonschema/1-overview)
- [TOML validation discussion at toml-lang](https://github.com/toml-lang/toml/discussions/1038)[1](https://github.com/toml-lang/toml/discussions/1038)

---

#### Summary

- Parse your config (TOML or JSON) to a Python dictionary.
- Load your JSON Schema as a Python dictionary.
- Use jsonschema.validate(instance, schema) for validation.
- For CI/dev workflows, consider check-jsonschema CLI for multi-format support.

If you need advanced error messages or custom features, explore alternatives like syntaxTrees or voluptuous, but jsonschema remains the standard for JSON Schema compliance.

---

1. [Documenting how to validate TOML with JSON schema](https://github.com/toml-lang/toml/discussions/1038)
2. [Python and TOML: Read, Write, and Configure with tomllib](https://realpython.com/python-toml/)
3. [Schema Validation for TOML - JSON Schema Everywhere](https://json-schema-everywhere.github.io/toml)
4. [python-jsonschema/check-jsonschema | DeepWiki](https://deepwiki.com/python-jsonschema/check-jsonschema/1-overview)
5. [Command-line Interface | python-jsonschema/check-jsonschema | DeepWiki](https://deepwiki.com/python-jsonschema/check-jsonschema/3-command-line-interface)
6. [Schema Validation - jsonschema 4.25.1 documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/)
7. [Validate JSON data using python - Stack Overflow](https://stackoverflow.com/questions/54491156/validate-json-data-using-python)

---

### Deterministic ML experiments (PyTorch/Numpy/Seeds)
To achieve deterministic machine learning (ML) experiments in Python and PyTorch, it’s crucial to control all sources of randomness—this includes global seeds for Python, NumPy, and PyTorch, as well as configuring hardware-specific options like cuDNN. Here are the best practices gathered from multiple expert sources:

### 1. Seed All Random Generators
- Python random library: random.seed(SEED)
- NumPy: np.random.seed(SEED)
- PyTorch (CPU): torch.manual_seed(SEED)
- PyTorch (GPU): torch.cuda.manual_seed_all(SEED) (for all GPUs)[1](https://www.codegenes.net/blog/how-to-train-a-model-deterministic-pytorch/)[[2]](https://docs.pytorch.org/docs/stable/notes/randomness.html)[[3]](https://pieriantraining.com/how-to-set-the-seed-in-pytorch-for-reproducible-results/)[[4]](https://www.codegenes.net/blog/deterministic-pytorch/)

### 2. Control cuDNN Behavior (for GPU)
- Set deterministic convolution algorithms:  
  ```python
  torch.backends.cudnn.deterministic = True
  torch.backends.cudnn.benchmark = False
  ```
  This disables the dynamic benchmarking of cuDNN algorithms, forcing PyTorch to select deterministic ones at a trade-off of speed for reproducibility[5](https://runebook.dev/en/articles/pytorch/backends/torch.backends.cudnn.deterministic)[[6]](https://www.codegenes.net/blog/different-result-with-deterministic-setting-in-pytorch/)[[7]](https://gist.github.com/Guitaricet/28fbb2a753b1bb888ef0b2731c03c031)[[8]](https://stackoverflow.com/questions/56354461/reproducibility-and-performance-in-pytorch).

### 3. Consistent Data Loading
- When using DataLoader, pass a fixed seed to its generator argument for reproducible shuffling:
  ```python
  from torch.utils.data import DataLoader
  generator = torch.Generator().manual_seed(SEED)
  loader = DataLoader(dataset, shuffle=True, generator=generator)
  ```
  This prevents randomness in the order of mini-batches[1](https://www.codegenes.net/blog/how-to-train-a-model-deterministic-pytorch/)[[9]](https://www.geeksforgeeks.org/deep-learning/reproducibility-in-pytorch/).

### 4. Log All Hyperparameters and Initial States
- Record hyperparameters, dataset splits (especially if randomized), model initialization, and optimizer state at the start. Use tools like W&B or TensorBoard for comprehensive experiment tracking[7](https://gist.github.com/Guitaricet/28fbb2a753b1bb888ef0b2731c03c031).

### 5. Version and Save Code and Data
- Tag your repository with experiment versions, save complete preprocessing pipelines and split data when possible—especially important if you share or revisit work in the future[7](https://gist.github.com/Guitaricet/28fbb2a753b1bb888ef0b2731c03c031).

### 6. Hardware and Environment Consistency
- Be aware: Results Phase 5 differ between hardware or driver versions, or across different PyTorch releases. Try to keep your software and hardware stack as unchanged as possible for full reproducibility[10](https://github.com/backend-developers-ltd/deterministic-ml)[[8]](https://stackoverflow.com/questions/56354461/reproducibility-and-performance-in-pytorch)[[5]](https://runebook.dev/en/articles/pytorch/backends/torch.backends.cudnn.deterministic).

### 7. Performance Trade-offs
- Deterministic settings can significantly slow down training, as certain optimized non-deterministic CUDA operations are disabled. Profile your workflow to understand these trade-offs, and use selective determinism only where strictly needed for reproducibility or debugging purposes[8](https://stackoverflow.com/questions/56354461/reproducibility-and-performance-in-pytorch)[[5]](https://runebook.dev/en/articles/pytorch/backends/torch.backends.cudnn.deterministic)[[6]](https://www.codegenes.net/blog/different-result-with-deterministic-setting-in-pytorch/).

### 8. Use Comprehensive Deterministic Mode in Modern PyTorch
- In recent PyTorch versions, torch.use_deterministic_algorithms(True) can ensure all operations either run deterministically or raise errors if not possible, simplifying checking for full determinism[5](https://runebook.dev/en/articles/pytorch/backends/torch.backends.cudnn.deterministic).

---

#### Example Starter Script for Deterministic PyTorch Experiments

```python
import random
import numpy as np
import torch
import os

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
os.environ['PYTHONHASHSEED'] = str(SEED)

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# For newer PyTorch releases
torch.use_deterministic_algorithms(True)

# When creating DataLoader
generator = torch.Generator().manual_seed(SEED)
loader = DataLoader(dataset, shuffle=True, generator=generator)
```text
---

Key Takeaways:  
- Set all relevant seeds and control hardware-dependent randomness.
- Accept performance reductions in favor of experiment reproducibility.
- Log and version everything: code, data, parameters, initializations.
- Reproducibility can be strictly guaranteed only under identical hardware/software setups for some advanced models[10](https://github.com/backend-developers-ltd/deterministic-ml)[[7]](https://gist.github.com/Guitaricet/28fbb2a753b1bb888ef0b2731c03c031).

For deeper guides and troubleshooting, PyTorch’s official reproducibility notes and documentation, as well as blogs focused on deterministic practices, are excellent resources[2](https://docs.pytorch.org/docs/stable/notes/randomness.html)[[1]](https://www.codegenes.net/blog/how-to-train-a-model-deterministic-pytorch/)[[3]](https://pieriantraining.com/how-to-set-the-seed-in-pytorch-for-reproducible-results/)[[4]](https://www.codegenes.net/blog/deterministic-pytorch/).

---

1. [Training a Deterministic Model in PyTorch - codegenes.net](https://www.codegenes.net/blog/how-to-train-a-model-deterministic-pytorch/)
2. [Reproducibility — PyTorch 2.9 documentation](https://docs.pytorch.org/docs/stable/notes/randomness.html)
3. [How to Set the Seed in PyTorch for Reproducible Results](https://pieriantraining.com/how-to-set-the-seed-in-pytorch-for-reproducible-results/)
4. [Deterministic PyTorch: A Comprehensive Guide - codegenes.net](https://www.codegenes.net/blog/deterministic-pytorch/)
5. [Achieving Determinism in PyTorch with cudnn.deterministic](https://runebook.dev/en/articles/pytorch/backends/torch.backends.cudnn.deterministic)
6. [Achieving Reproducibility: Understanding Different Results with ...](https://www.codegenes.net/blog/different-result-with-deterministic-setting-in-pytorch/)
7. [Notes on reproducibility in PyTorch · GitHub](https://gist.github.com/Guitaricet/28fbb2a753b1bb888ef0b2731c03c031)
8. [Reproducibility and performance in PyTorch - Stack Overflow](https://stackoverflow.com/questions/56354461/reproducibility-and-performance-in-pytorch)
9. [Reproducibility in PyTorch - GeeksforGeeks](https://www.geeksforgeeks.org/deep-learning/reproducibility-in-pytorch/)
10. [Deterministic ML Models execution using Python frameworks](https://github.com/backend-developers-ltd/deterministic-ml)

---

### CPU-only Dockerfile mirroring local dev (nox/pytest) with caching
Here are best practices for creating an efficient, CPU-only Python Dockerfile that mirrors your local development environment (especially with tools like nox and pytest), while leveraging Docker build caching for faster, reproducible builds:

1. Use the Official, Minimal Base Image
- Prefer images like python:3.x-slim to reduce image size and the attack surface. Always specify the version (avoid latest) for determinism in builds.
- Example: FROM python:3.10-slim[1](https://snyk.io/blog/best-practices-containerizing-python-docker/)[[2]](https://collabnix.com/10-essential-docker-best-practices-for-python-developers-in-Previous Cycle/)[[3]](https://darekdari.com/how-to-optimize-dockerfile-for-python/)[[4]](https://dev.to/rajeshgheware/dockerfile-best-practices-the-ultimate-guide-to-optimizing-your-container-builds-2d0p)

2. Use a .dockerignore File
- Exclude files/directories not needed in the container (like .venv/, __pycache__/, .git/ etc.) to reduce context size and speed up the build[2](https://collabnix.com/10-essential-docker-best-practices-for-python-developers-in-Previous Cycle/)[[5]](https://testdriven.io/blog/docker-best-practices/).

3. Optimize Layer Caching
- Copy dependency files before the rest of your code; this leverages cache if requirements haven’t changed.
- Example:
  
  COPY requirements.txt ./
  
  RUN pip install --no-cache-dir -r requirements.txt
  
  COPY . .
- For nox: copy your noxfile.py and test requirements first for caching test dependencies.

4. Multi-Stage Builds (Recommended for Production)
- Build wheels in a first stage, then copy only the wheels and runtime code to a slimmer final stage. This keeps dev/build tools out of your runtime image.
- Example for production:
  ```dockerfile
  FROM python:3.10-slim as builder
  WORKDIR /app
  COPY requirements.txt ./
  RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt 

  FROM python:3.10-slim
  WORKDIR /app
  COPY --from=builder /wheels /wheels
  RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt
  COPY . .
  ```
  For local dev/test, you can combine stages, but production should separate build/runtime[5](https://testdriven.io/blog/docker-best-practices/)[[4]](https://dev.to/rajeshgheware/dockerfile-best-practices-the-ultimate-guide-to-optimizing-your-container-builds-2d0p)[[6]](https://support.tools/dockerfile-best-practices-guide/).

5. Non-Root User
- Improve security by creating and switching to a non-root user:
  ```dockerfile
  RUN useradd --create-home appuser
  USER appuser
  ```

6. Set WORKDIR
- Ensures your application runs from a predictable location:
  
  WORKDIR /app

7. Environment Variables
- For development, set envs like PYTHONUNBUFFERED=1 and PIP_NO_CACHE_DIR=off to see logs in real-time.
  
  ENV PYTHONUNBUFFERED=1
  
  ENV PIP_NO_CACHE_DIR=off

8. Integrating Nox/Pytest
- To run tests inside the container:
  - Copy your test files and noxfile.py.
  - Add a build stage (or entrypoint) for running nox:
    ```dockerfile
    RUN pip install nox pytest
    CMD ["nox", "-s", "tests"]
    ```
  Or, for CI, invoke pytest directly in an override entrypoint:
    ```dockerfile
    CMD ["pytest"]
    ```
- For local dev “mirroring,” you might mount your code into the container (using volumes), so code changes are reflected without rebuilds.

9. Caching and Layer Order
- Changing files rarely at the top, frequently at the bottom.
- Always keep dependency installation ahead of code copy (see above)[6](https://support.tools/dockerfile-best-practices-guide/)[[5]](https://testdriven.io/blog/docker-best-practices/)[[4]](https://dev.to/rajeshgheware/dockerfile-best-practices-the-ultimate-guide-to-optimizing-your-container-builds-2d0p)[[3]](https://darekdari.com/how-to-optimize-dockerfile-for-python/).

10. CPU-Only Configuration
- No special instructions required for CPU-only unless you’re avoiding GPU libraries (don’t install any CUDA/cuDNN deps).
- If you want to control resource usage, use the --cpus flag on docker run, e.g. docker run --cpus="2" (though for dev parity, don’t artificially restrict).

Summary Example Dockerfile:

```dockerfile
FROM python:3.10-slim

# Security: non-root user
RUN useradd --create-home appuser
USER appuser

WORKDIR /app

# Dependencies for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# For local dev (nox/pytest)
RUN pip install nox pytest

# Environment variables
ENV PYTHONUNBUFFERED=1

# Default: run tests (for CI), or override as needed
CMD ["pytest"]
```text

References & Deep Dive:
- Multi-stage builds, caching, security, and layer ordering:[5](https://testdriven.io/blog/docker-best-practices/)[[6]](https://support.tools/dockerfile-best-practices-guide/)[[3]](https://darekdari.com/how-to-optimize-dockerfile-for-python/)[[4]](https://dev.to/rajeshgheware/dockerfile-best-practices-the-ultimate-guide-to-optimizing-your-container-builds-2d0p)
- Why non-root users matter and .dockerignore:[2](https://collabnix.com/10-essential-docker-best-practices-for-python-developers-in-Previous Cycle/)[[5]](https://testdriven.io/blog/docker-best-practices/)[[1]](https://snyk.io/blog/best-practices-containerizing-python-docker/)
- Setting up for dev parity between Docker and local:[7](https://codezup.com/dockerizing-your-python-app-best-practices-workflow/)[[8]](https://www.geeksforgeeks.org/python/setting-up-docker-for-python-projects-a-step-by-step-guide/)

If you need a docker-compose setup for matching local dev flow further, you can mount your source as a volume, map ports, and mirror environment variables with .env.dev files. For CI pipelines, always use fresh builds and explicit dependency pinning.

---

1. [Best practices for containerizing Python applications with Docker - Snyk](https://snyk.io/blog/best-practices-containerizing-python-docker/)
2. [Top 10 Docker Best Practices for Python Developers](https://collabnix.com/10-essential-docker-best-practices-for-python-developers-in-Previous Cycle/)
3. [Optimized Dockerfile For Python Previous Cycle Best Guide](https://darekdari.com/how-to-optimize-dockerfile-for-python/)
4. [Dockerfile Best Practices: The Ultimate Guide to ... - DEV Community](https://dev.to/rajeshgheware/dockerfile-best-practices-the-ultimate-guide-to-optimizing-your-container-builds-2d0p)
5. [Docker Best Practices for Python Developers | TestDriven.io](https://testdriven.io/blog/docker-best-practices/)
6. [Dockerfile Best Practices: A Comprehensive Guide for Previous Cycle](https://support.tools/dockerfile-best-practices-guide/)
7. [Dockerizing Your Python App: Best Practices and Workflow](https://codezup.com/dockerizing-your-python-app-best-practices-workflow/)
8. [Setting Up Docker for Python Projects: A Step-by-Step Guide](https://www.geeksforgeeks.org/python/setting-up-docker-for-python-projects-a-step-by-step-guide/)

---

## Tailored Copilot Prompt (Next Iteration: push coverage from 95% → 96–99%)

Goal: Raise test coverage on evaluation loop, logging registry integration, checkpoint best‑k retention, AST CLI, and config schema validator to 96–99% without altering public contracts.

Context:
- Repo: Aries-Serpent/_codex_
- Modules to target: src/codex_ml/evaluation/loop.py, src/codex_ml/logging/registry.py (integration), checkpoint retention code, src/codex/ast/cli.py enhancements, tools/validate_experiments.py, configs/schemas/experiments.schema.json
- Current target: 95% achieved; stretch to 96–99%.
- Constraints: Offline-first; deterministic tests (seeded DataLoaders); no external networks; NDJSON logging default with MLflow optional & disabled.

Request to Copilot:
- Generate additional tests that:
  - Cover edge cases: empty dataloaders; single-batch; large-batch; metric exceptions; logger backpressure; file I/O errors in best‑k.
  - Simulate failures: corrupted checkpoint metadata; atomic rename failures (use monkeypatch); permission errors.
  - Validate CLI behaviors: Typer command parsing (human and --json outputs), exit codes, help text; invalid option handling.
  - Validate schema tooling: invalid configs (type mismatches, missing required fields), TOML/JSON parity; JSONSchema draft compliance errors.
  - Reproducibility: run the same evaluation twice with seeded environment and assert identical outputs (hash or equality).
- Add golden files (small JSON/NDJSON) where appropriate for stable outputs.
- Provide coverage reports and annotate any lines intentionally excluded (pragma: no cover) with rationale.
- Do not modify public function signatures or CLI flags.

Acceptance:
- Coverage reports show ≥96% on targeted modules; all tests deterministic across repeated runs; nox -s tests, lint, typecheck, docs_build, security all pass; artifacts updated.

---

## Rollback / Fallback Plan
- All additions are flag-guarded or additive; revert by removing new modules/flags.
- Best‑k retention: fallback to previous non-pruning path via flag if issues arise.
- pip-audit enforcement can switch to warn-only temporarily with documented allowlists.
- Style normalization is formatting-only; easy git revert.
- Docker artifacts are non-invasive; safe to remove.

