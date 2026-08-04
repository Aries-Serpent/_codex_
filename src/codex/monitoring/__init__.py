"""Monitoring module - re-exports from aries_serpent_core."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aries_serpent_core.monitoring import Histogram as Histogram
    from aries_serpent_core.monitoring import PerformanceSnapshot as PerformanceSnapshot
else:
    try:
        from aries_serpent_core.monitoring import Histogram, PerformanceSnapshot
    except ImportError:
        # Fallback implementations if not available
        class Histogram:
            """Histogram metric for monitoring."""
            def __init__(self, name, help_text="", buckets=None):
                self.name = name
                self.help_text = help_text
                self.buckets = buckets or []
        
        class PerformanceSnapshot:
            """Performance metrics snapshot."""
            def __init__(self):
                self.metrics = {}

__all__ = ["Histogram", "PerformanceSnapshot"]
