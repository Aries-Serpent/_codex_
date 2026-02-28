"""codex_ml.backends — optional hardware-accelerated inference backends.

Tier 2 (guarded): each backend falls back to CPU-only PyTorch when the
optional acceleration library is not installed or the device is unavailable.

See docs/ops/hardware_compatibility_matrix.md for Tier policy.
"""
