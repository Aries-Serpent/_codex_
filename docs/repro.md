`set_reproducible()` seeds Python, NumPy and PyTorch, enables deterministic
algorithms and disables cuDNN benchmarking. The custom training loop in
`training/functional_training.py` asserts that `torch.backends.cudnn.deterministic`
is set when CUDA is available, helping catch non-deterministic operations
early. Call `set_reproducible()` or set `torch.backends.cudnn.deterministic = True`
before training on GPU to satisfy this check.

Checkpoints now embed the current Git commit and a small environment summary so
runs can be traced back to the exact code and runtime. The demo training loop
exports `environment.json`, `environment.ndjson`, and `pip-freeze.txt` on every
invocation, removing the need for manual provenance calls. Passing
`dataset_sources` to `run_training` writes a `dataset_checksums.json` manifest so
dataset drift is detectable after the fact. Dataset splits cached via
`split_dataset` include a SHA256 checksum of the source data and are invalidated
when the data changes. Use `scripts/export_env_info.py` at run start to record
environment variables and key library versions when integrating custom flows.
Install dependencies from the provided lock files to ensure consistent builds.

### Checkpointing & Resume

`codex_ml.utils.checkpoint.save_checkpoint` now snapshots the Python, NumPy and
PyTorch RNG state into `rng.pt` and emits a `checkpoint.sha256` sidecar covering
the binary state files. When `load_checkpoint` resumes training the checksum is
verified and RNG state restored, ensuring subsequent random draws match the
original run. The helper also maintains a tiny `index.json` inside the
checkpoint directory that tracks the best *k* checkpoints (lower metrics are
preferred) and prunes older snapshots automatically.

To resume deterministically, point `load_checkpoint` at the epoch directory and
handle any `ValueError` raised when the checksum mismatches.

```python
from pathlib import Path
from codex_ml.utils.checkpoint import load_checkpoint

metadata = load_checkpoint(
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    ckpt_dir=Path("runs/model/checkpoints/epoch-4"),
)
print("Restored epoch", metadata.get("epoch"))
```

If the `.sha256` digest does not match the on-disk files the load call raises a
`ValueError`, signalling that the checkpoint is corrupted or incomplete.
