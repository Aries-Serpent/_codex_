Check for must recent active branch:
//fetch https://github.com/Aries-Serpent/_codex_/activity?time_period=day

Branches:
//fetch https://github.com/Aries-Serpent/_codex_
//fetch https://github.com/Aries-Serpent/_codex_/tree/*/

Objective:
> {{objective_summary}}
---

Audit Scope

# 📍_codex_: Status Update ({{date}})

1. **Repo Map**
   - {{repo_map_summary}}

2. **Capability Audit Table**

| Capability | Status | Existing Artifacts | Gaps | Risks | Gap Resolution Plan | Rollback Plan | Resolution Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tokenization (fast tokenizer, vocab, encode/decode, padding/truncation) | {{tokenization_status}} | {{tokenization_artifacts}} | {{tokenization_gaps}} | {{tokenization_risks}} | {{tokenization_resolution}} | {{tokenization_rollback}} | {{tokenization_resolution_status}} |
| ChatGPT Codex Modeling (model init, dtype, device placement, LoRA/PEFT hooks) | {{modeling_status}} | {{modeling_artifacts}} | {{modeling_gaps}} | {{modeling_risks}} | {{modeling_resolution}} | {{modeling_rollback}} | {{modeling_resolution_status}} |
| Training Engine (HF Trainer or custom loop, precision, gradient accumulation) | {{training_status}} | {{training_artifacts}} | {{training_gaps}} | {{training_risks}} | {{training_resolution}} | {{training_rollback}} | {{training_resolution_status}} |
| Configuration Management (Hydra/YAML structure, overrides, sweeps) | {{config_status}} | {{config_artifacts}} | {{config_gaps}} | {{config_risks}} | {{config_resolution}} | {{config_rollback}} | {{config_resolution_status}} |
| Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging) | {{evaluation_status}} | {{evaluation_artifacts}} | {{evaluation_gaps}} | {{evaluation_risks}} | {{evaluation_resolution}} | {{evaluation_rollback}} | {{evaluation_resolution_status}} |
| Logging & Monitoring (TensorBoard / W&B / MLflow, system metrics via `psutil`/NVML) | {{logging_status}} | {{logging_artifacts}} | {{logging_gaps}} | {{logging_risks}} | {{logging_resolution}} | {{logging_rollback}} | {{logging_resolution_status}} |
| Checkpointing & Resume (weights, optimizer state, scheduler, RNG, best-k retention) | {{checkpointing_status}} | {{checkpointing_artifacts}} | {{checkpointing_gaps}} | {{checkpointing_risks}} | {{checkpointing_resolution}} | {{checkpointing_rollback}} | {{checkpointing_resolution_status}} |
| Data Handling (dataset splits, deterministic shuffling, caching) | {{data_status}} | {{data_artifacts}} | {{data_gaps}} | {{data_risks}} | {{data_resolution}} | {{data_rollback}} | {{data_resolution_status}} |
| Security & Safety (dependency locking, secrets scanning, prompt safety) | {{security_status}} | {{security_artifacts}} | {{security_gaps}} | {{security_risks}} | {{security_resolution}} | {{security_rollback}} | {{security_resolution_status}} |
| Continuous Integration & Gates (pytest, nox, lint, type-checking) | {{ci_status}} | {{ci_artifacts}} | {{ci_gaps}} | {{ci_risks}} | {{ci_resolution}} | {{ci_rollback}} | {{ci_resolution_status}} |
| Deployment & Packaging (Docker, release automation, environment parity) | {{deployment_status}} | {{deployment_artifacts}} | {{deployment_gaps}} | {{deployment_risks}} | {{deployment_resolution}} | {{deployment_rollback}} | {{deployment_resolution_status}} |
| Documentation & Guides (quickstarts, architecture, safety docs) | {{docs_status}} | {{docs_artifacts}} | {{docs_gaps}} | {{docs_risks}} | {{docs_resolution}} | {{docs_rollback}} | {{docs_resolution_status}} |
| Experiment Tracking & Telemetry (MLflow, TensorBoard, artifact logging) | {{tracking_status}} | {{tracking_artifacts}} | {{tracking_gaps}} | {{tracking_risks}} | {{tracking_resolution}} | {{tracking_rollback}} | {{tracking_resolution_status}} |
| Extensibility & Integrations (plugin architecture, external APIs, adapters) | {{extensibility_status}} | {{extensibility_artifacts}} | {{extensibility_gaps}} | {{extensibility_risks}} | {{extensibility_resolution}} | {{extensibility_rollback}} | {{extensibility_resolution_status}} |

3. **High-Signal Findings**

- {{high_signal_01}}
- {{high_signal_02}}
- {{high_signal_03}}
- {{high_signal_04}}
- {{high_signal_05}}
- {{high_signal_06}}
- {{high_signal_07}}
- {{high_signal_08}}
- {{high_signal_09}}
- {{high_signal_10}}

4. **Atomic Diffs**

### Atomic Diff 1 — {{atomic_diff_1_title}}
- **Why:** {{atomic_diff_1_why}}
- **Risk:** {{atomic_diff_1_risk}}
- **Rollback:** {{atomic_diff_1_rollback}}
- **Tests/docs:** {{atomic_diff_1_tests}}
```diff
{{atomic_diff_1_patch}}
```
### Atomic Diff 2 — {{atomic_diff_2_title}}
- **Why:** {{atomic_diff_2_why}}
- **Risk:** {{atomic_diff_2_risk}}
- **Rollback:** {{atomic_diff_2_rollback}}
- **Tests/docs:** {{atomic_diff_2_tests}}
```diff
{{atomic_diff_2_patch}}
```
### Atomic Diff 3 — {{atomic_diff_3_title}}
- **Why:** {{atomic_diff_3_why}}
- **Risk:** {{atomic_diff_3_risk}}
- **Rollback:** {{atomic_diff_3_rollback}}
- **Tests/docs:** {{atomic_diff_3_tests}}
```diff
{{atomic_diff_3_patch}}
```
5. **Local Tests & Gates**

| Gate | Status | Command | Notes |
| --- | --- | --- | --- |
| nox -s tests | {{local_tests_status}} | {{local_tests_command}} | {{local_tests_notes}} |
| pytest tests/docs/test_status_update_template.py | {{status_update_tests_status}} | {{status_update_tests_command}} | {{status_update_tests_notes}} |

6. **Reproducibility Checklist**

| Item | Status | Notes |
| --- | --- | --- |
| Seeds | {{repro_seeds_status}} | {{repro_seeds_notes}} |
| Environment | {{repro_env_status}} | {{repro_env_notes}} |
| Data | {{repro_data_status}} | {{repro_data_notes}} |
| Configuration | {{repro_config_status}} | {{repro_config_notes}} |
| Hardware | {{repro_hardware_status}} | {{repro_hardware_notes}} |
| Results parity | {{repro_results_status}} | {{repro_results_notes}} |

7. **Deferred Items**

- {{deferred_item_01}}
- {{deferred_item_02}}
- {{deferred_item_03}}

8. **Error Capture Blocks**

- {{error_capture_summary}}

## Canonical Question Reference
- Reference outstanding questions in `docs/status_update_outstanding_questions.md` and add new/resolved entries there.

## Codex-ready Task Sequence

```yaml
preparation:
  - {{task_sequence_preparation_step_1}}
  - {{task_sequence_preparation_step_2}}
execution:
  - {{task_sequence_execution_step_1}}
  - {{task_sequence_execution_step_2}}
validation:
  - {{task_sequence_validation_step_1}}
error_capture:
  - {{task_sequence_error_capture_step_1}}
```
**Additional Deliverable — Executable Script**

```python
"""Codex remediation workflow template."""
from __future__ import annotations

from pathlib import Path


def main() -> None:
    """Entry point for Codex remediation."""
    raise NotImplementedError("{{implement_context_loader}}")


if __name__ == "__main__":
    main()
    print("{{script_completion_message}}")
```
**Supplied Task (expand on task as needed for Codex to action each until completion):**

1. {{codex_supplied_task_01}}
2. {{codex_supplied_task_02}}
3. {{codex_supplied_task_03}}

---

_Update generated {{generated_timestamp}}_
