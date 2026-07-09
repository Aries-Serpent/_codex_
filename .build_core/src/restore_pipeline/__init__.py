"""
restore_pipeline — CPU-only image restoration + vivid colorization pipeline.

Public API::

    from restore_pipeline import process

    restored, metrics = process(image, mask=None, reference=None, config=None)
"""

from restore_pipeline.config import PipelineConfig
from restore_pipeline.pipeline import process

__all__ = ["PipelineConfig", "process"]
__version__ = "0.1.0"
