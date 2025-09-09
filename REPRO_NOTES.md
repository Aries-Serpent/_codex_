Python: 3.12.10
OS: Linux-6.12.13-x86_64-with-glibc2.39
CUDA Driver: N/A
GPU: N/A
Torch: 2.8.0+cu128
Transformers: 4.56.0
Seed: 42
Determinism: torch.use_deterministic_algorithms(True)

## Reproducibility Tips

- Run `python scripts/env/export_env_snapshot.py` at the start of an
  experiment to record OS, GPU, and package versions along with all
  environment variables.
- Checkpoints written with `save_checkpoint` now emit a sibling
  `*.meta.json` file capturing the Git commit and system summary.
- Use `split_dataset(..., checksum_path=path)` to persist dataset
  checksums alongside cached train/validation splits.
