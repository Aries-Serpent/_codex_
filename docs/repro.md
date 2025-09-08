`set_reproducible()` seeds Python, NumPy and PyTorch, enables deterministic
algorithms and disables cuDNN benchmarking. The custom training loop in
`training/functional_training.py` asserts that `torch.backends.cudnn.deterministic`
is set when CUDA is available, helping catch non-deterministic operations
early. Call `set_reproducible()` or set `torch.backends.cudnn.deterministic = True`
before training on GPU to satisfy this check.

Checkpoints now embed the current Git commit and a small environment summary so
runs can be traced back to the exact code and runtime. Dataset splits cached via
`split_dataset` include a SHA256 checksum of the source data and are invalidated
when the data changes. Use `scripts/export_env_info.py` at run start to record
environment variables and key library versions. Install dependencies from the
provided lock files to ensure consistent builds.
