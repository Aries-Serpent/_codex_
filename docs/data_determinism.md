# Data Determinism

* Seed all RNGs (Python, NumPy, torch when used).
* Deterministic shuffles and splits (document the seed used).
* Avoid nondeterministic kernels; note AMP/precision trade-offs.
