`set_reproducible()` seeds Python, NumPy and PyTorch, enables deterministic
algorithms and disables cuDNN benchmarking. The custom training loop in
`training/functional_training.py` asserts that `torch.backends.cudnn.deterministic`
is set when CUDA is available, helping catch non-deterministic operations
early. Call `set_reproducible()` or set `torch.backends.cudnn.deterministic = True`
before training on GPU to satisfy this check. The Hydra `codex_ml.cli.train`
entrypoint now applies `codex_ml.utils.repro.set_seed()` as soon as the
configuration is loaded, preferring the explicit `seed` override, falling back
to `reproducibility.seed`, and defaulting to `0` when neither is supplied. This
keeps trainer runs deterministic even when the caller does not supply a seed.

Hydra-based entrypoints register structured (dataclass) configs in code. Every
run captures the resolved configuration under the Hydra output directory and
rejects overrides with incompatible types early, so keep CLI overrides in commit
history for reproducibility. Presets like `experiment=fast` are just additional
dataclass nodes registered in the same ConfigStore and can be combined with
ad-hoc overrides (for example, `training.max_epochs=2`).

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
`make -f configs/development/Makefile setup` now enforces the presence of
`requirements/lock.txt` and aborts if the file is missing instead of silently
falling back to floating requirements.

For user-controlled splits, prefer `codex_ml.data.split_utils.deterministic_split`
which shuffles indices with a dedicated seed and keeps the remainder in the
training subset to avoid silent data loss. When iterating over large JSONL
datasets rely on `codex_ml.data.jsonl_stream.iter_jsonl()` to keep memory usage
bounded and write cached shards via
`codex_ml.data.cache.write_jsonl_with_crc()`—the CRC sidecar gives a fast
corruption check before reuse. Training loops can now build workers through
`codex_ml.training.build_dataloader()` which wires the generator seed and
worker-init hook. If PyTorch is absent the factory falls back to `iter(dataset)`;
this keeps CPU-only tooling working but omits shuffling, so plan accordingly for
benchmark-quality experiments.

Checkpointing & Resume`codex_ml.utils.checkpoint.save_checkpoint` now snapshots
the Python, NumPy and PyTorch RNG state into a JSON sidecar (`rng.json`) and, when
PyTorch is present, keeps a legacy `rng.pt` for backward compatibility. Each
checkpoint writes a `model.pt.sha256` checksum alongside the aggregate
`checkpoint.sha256` used by older releases. When `load_checkpoint` resumes
training the digests are validated (use `strict=True` to error on mismatches)
before restoring model weights, optimizer state and RNG streams so subsequent
random draws match the original run. The helper continues to maintain the tiny
`index.json` manifest that tracks the best *k* checkpoints (lower metrics are
preferred) and prunes older snapshots automatically.

The new `codex_ml.training.rng_checkpoint.RNGState` wrapper exposes
`capture()`, `restore()` and `save_to_file()` helpers which the unified trainer
uses to persist RNG snapshots alongside every emitted checkpoint
(`checkpoint.pt.rng.json`). When resuming from a checkpoint the orchestrator
loads this sidecar and restores Python/NumPy/Torch seeds before the first batch,
ensuring resumed runs follow the exact same random sequence.

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
```text

If the `.sha256` digest does not match the on-disk files the load call raises a
`ValueError`, signalling that the checkpoint is corrupted or incomplete.
