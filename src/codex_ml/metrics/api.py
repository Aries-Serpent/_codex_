"""Public metrics facade for codex_ml.

Re-export stable metric utilities here to avoid import churn downstream.
Keep imports lazy/minimal to prevent import-time cost.
"""

from __future__ import annotations

__all__ = [
    # add stable public names here, e.g. "accuracy", "f1_macro"
]

# Example of lazy binding if/when internals land:
# def accuracy(*args, **kwargs):
#     from ._internals import accuracy as _impl
#     return _impl(*args, **kwargs)
