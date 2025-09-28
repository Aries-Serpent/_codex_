# Logging & Monitoring Runbook

This runbook captures the minimal steps to enable Codex ML's optional telemetry
stack offline.

## Feature flags

| Capability | Config knobs | Notes |
| --- | --- | --- |
| TensorBoard | `TrainConfig.tensorboard`, `TrainConfig.tensorboard_dir` | Uses the lightweight `TBWriter` wrapper; safe when TensorBoard is missing. |
| Weights & Biases | `TrainConfig.wandb_enable`, env `WANDB_MODE=offline` | The shim falls back to a local dummy if the SDK is absent or fails to init. |
| System metrics | `TrainConfig.metrics_out`, `TrainConfig.system_metrics_interval` | Writes NDJSON snapshots; `0` interval disables the background sampler. |

## Troubleshooting

### TensorBoard not installed

* Symptom: enabling TensorBoard produces no `.event` files.
* Action: install `torch` with the TensorBoard extras (`pip install torch tensorboard`).
* Mitigation: the `TBWriter` wrapper degrades to a no-op so training continues.

### W&B fails to initialise

* Symptom: console shows `wandb` import errors or network failures.
* Action: set `WANDB_MODE=offline` and ensure `TrainConfig.wandb_enable = True`.
* Mitigation: the shim yields a dummy logger when the SDK cannot start; metrics
  continue to write to NDJSON/TensorBoard.

### GPU metrics missing

* Symptom: NDJSON lacks `gpu_*` keys.
* Action: install NVIDIA's NVML bindings (`pip install pynvml`) and set
  `CODEX_MONITORING_ENABLE_GPU=1` before launch.
* Mitigation: CPU/RAM telemetry continues without GPU metrics; no restart needed.

### Disable system sampler

* Set `TrainConfig.system_metrics_interval = 0` to skip spawning the background
  thread entirely (useful for very short runs or constrained environments).

## Operational tips

* Metrics land in `.codex/metrics.ndjson` by default; rotate or archive this file
  alongside checkpoints.
* When running headless, forward TensorBoard scalars via `tensorboard --logdir` and
  sync W&B runs manually once connectivity is available (`wandb sync <run-dir>`).
