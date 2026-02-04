"""
MCP Metrics - Telemetry and monitoring for MCP operations.

This module provides metrics collection for MCP adapter operations.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Thread-safe metric collection
- Bounded metric history
- Defensive error handling
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_METRIC_HISTORY = 10000
MAX_LABEL_LENGTH = 100
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""

    name: str
    count: int
    total: float
    min_value: float
    max_value: float
    avg_value: float


class MetricCollector:
    """Thread-safe metric collector for MCP operations.

    Features:
    - Counter, gauge, and histogram metrics
    - Label support for dimensions
    - Export to various formats

    Safeguards:
    - Thread-safe operations
    - Bounded history to prevent memory issues
    """

    def xǁMetricCollectorǁ__init____mutmut_orig(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_1(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = None
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_2(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = None
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_3(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(None)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_4(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = None
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_5(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = None
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_6(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(None)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_7(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = None
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_8(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = None

        logger.info("MetricCollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_9(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info(None, max_history)

    def xǁMetricCollectorǁ__init____mutmut_10(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", None)

    def xǁMetricCollectorǁ__init____mutmut_11(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info(max_history)

    def xǁMetricCollectorǁ__init____mutmut_12(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("MetricCollector initialized (max_history=%d)", )

    def xǁMetricCollectorǁ__init____mutmut_13(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("XXMetricCollector initialized (max_history=%d)XX", max_history)

    def xǁMetricCollectorǁ__init____mutmut_14(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("metriccollector initialized (max_history=%d)", max_history)

    def xǁMetricCollectorǁ__init____mutmut_15(self, max_history: int = MAX_METRIC_HISTORY) -> None:
        """Initialize the metric collector."""
        self._lock = threading.Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._history: list[MetricPoint] = []
        self._max_history = max_history

        logger.info("METRICCOLLECTOR INITIALIZED (MAX_HISTORY=%D)", max_history)
    
    xǁMetricCollectorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁ__init____mutmut_1': xǁMetricCollectorǁ__init____mutmut_1, 
        'xǁMetricCollectorǁ__init____mutmut_2': xǁMetricCollectorǁ__init____mutmut_2, 
        'xǁMetricCollectorǁ__init____mutmut_3': xǁMetricCollectorǁ__init____mutmut_3, 
        'xǁMetricCollectorǁ__init____mutmut_4': xǁMetricCollectorǁ__init____mutmut_4, 
        'xǁMetricCollectorǁ__init____mutmut_5': xǁMetricCollectorǁ__init____mutmut_5, 
        'xǁMetricCollectorǁ__init____mutmut_6': xǁMetricCollectorǁ__init____mutmut_6, 
        'xǁMetricCollectorǁ__init____mutmut_7': xǁMetricCollectorǁ__init____mutmut_7, 
        'xǁMetricCollectorǁ__init____mutmut_8': xǁMetricCollectorǁ__init____mutmut_8, 
        'xǁMetricCollectorǁ__init____mutmut_9': xǁMetricCollectorǁ__init____mutmut_9, 
        'xǁMetricCollectorǁ__init____mutmut_10': xǁMetricCollectorǁ__init____mutmut_10, 
        'xǁMetricCollectorǁ__init____mutmut_11': xǁMetricCollectorǁ__init____mutmut_11, 
        'xǁMetricCollectorǁ__init____mutmut_12': xǁMetricCollectorǁ__init____mutmut_12, 
        'xǁMetricCollectorǁ__init____mutmut_13': xǁMetricCollectorǁ__init____mutmut_13, 
        'xǁMetricCollectorǁ__init____mutmut_14': xǁMetricCollectorǁ__init____mutmut_14, 
        'xǁMetricCollectorǁ__init____mutmut_15': xǁMetricCollectorǁ__init____mutmut_15
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMetricCollectorǁ__init____mutmut_orig)
    xǁMetricCollectorǁ__init____mutmut_orig.__name__ = 'xǁMetricCollectorǁ__init__'

    def xǁMetricCollectorǁincrement__mutmut_orig(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_1(
        self,
        name: str,
        value: float = 2.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_2(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = None
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_3(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels and {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_4(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = None

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_5(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(None, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_6(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, None)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_7(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_8(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, )

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_9(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] = value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_10(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] -= value
            self._record_point(name, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_11(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(None, self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_12(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, None, labels)

    def xǁMetricCollectorǁincrement__mutmut_13(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], None)

    def xǁMetricCollectorǁincrement__mutmut_14(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(self._counters[key], labels)

    def xǁMetricCollectorǁincrement__mutmut_15(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, labels)

    def xǁMetricCollectorǁincrement__mutmut_16(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Value to add (default 1).
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._counters[key] += value
            self._record_point(name, self._counters[key], )
    
    xǁMetricCollectorǁincrement__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁincrement__mutmut_1': xǁMetricCollectorǁincrement__mutmut_1, 
        'xǁMetricCollectorǁincrement__mutmut_2': xǁMetricCollectorǁincrement__mutmut_2, 
        'xǁMetricCollectorǁincrement__mutmut_3': xǁMetricCollectorǁincrement__mutmut_3, 
        'xǁMetricCollectorǁincrement__mutmut_4': xǁMetricCollectorǁincrement__mutmut_4, 
        'xǁMetricCollectorǁincrement__mutmut_5': xǁMetricCollectorǁincrement__mutmut_5, 
        'xǁMetricCollectorǁincrement__mutmut_6': xǁMetricCollectorǁincrement__mutmut_6, 
        'xǁMetricCollectorǁincrement__mutmut_7': xǁMetricCollectorǁincrement__mutmut_7, 
        'xǁMetricCollectorǁincrement__mutmut_8': xǁMetricCollectorǁincrement__mutmut_8, 
        'xǁMetricCollectorǁincrement__mutmut_9': xǁMetricCollectorǁincrement__mutmut_9, 
        'xǁMetricCollectorǁincrement__mutmut_10': xǁMetricCollectorǁincrement__mutmut_10, 
        'xǁMetricCollectorǁincrement__mutmut_11': xǁMetricCollectorǁincrement__mutmut_11, 
        'xǁMetricCollectorǁincrement__mutmut_12': xǁMetricCollectorǁincrement__mutmut_12, 
        'xǁMetricCollectorǁincrement__mutmut_13': xǁMetricCollectorǁincrement__mutmut_13, 
        'xǁMetricCollectorǁincrement__mutmut_14': xǁMetricCollectorǁincrement__mutmut_14, 
        'xǁMetricCollectorǁincrement__mutmut_15': xǁMetricCollectorǁincrement__mutmut_15, 
        'xǁMetricCollectorǁincrement__mutmut_16': xǁMetricCollectorǁincrement__mutmut_16
    }
    
    def increment(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁincrement__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁincrement__mutmut_mutants"), args, kwargs, self)
        return result 
    
    increment.__signature__ = _mutmut_signature(xǁMetricCollectorǁincrement__mutmut_orig)
    xǁMetricCollectorǁincrement__mutmut_orig.__name__ = 'xǁMetricCollectorǁincrement'

    def xǁMetricCollectorǁset_gauge__mutmut_orig(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_1(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = None
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_2(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels and {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_3(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = None

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_4(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(None, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_5(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, None)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_6(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_7(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, )

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_8(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = None
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_9(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(None, value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_10(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, None, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_11(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, None)

    def xǁMetricCollectorǁset_gauge__mutmut_12(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(value, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_13(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, labels)

    def xǁMetricCollectorǁset_gauge__mutmut_14(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Current value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._gauges[key] = value
            self._record_point(name, value, )
    
    xǁMetricCollectorǁset_gauge__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁset_gauge__mutmut_1': xǁMetricCollectorǁset_gauge__mutmut_1, 
        'xǁMetricCollectorǁset_gauge__mutmut_2': xǁMetricCollectorǁset_gauge__mutmut_2, 
        'xǁMetricCollectorǁset_gauge__mutmut_3': xǁMetricCollectorǁset_gauge__mutmut_3, 
        'xǁMetricCollectorǁset_gauge__mutmut_4': xǁMetricCollectorǁset_gauge__mutmut_4, 
        'xǁMetricCollectorǁset_gauge__mutmut_5': xǁMetricCollectorǁset_gauge__mutmut_5, 
        'xǁMetricCollectorǁset_gauge__mutmut_6': xǁMetricCollectorǁset_gauge__mutmut_6, 
        'xǁMetricCollectorǁset_gauge__mutmut_7': xǁMetricCollectorǁset_gauge__mutmut_7, 
        'xǁMetricCollectorǁset_gauge__mutmut_8': xǁMetricCollectorǁset_gauge__mutmut_8, 
        'xǁMetricCollectorǁset_gauge__mutmut_9': xǁMetricCollectorǁset_gauge__mutmut_9, 
        'xǁMetricCollectorǁset_gauge__mutmut_10': xǁMetricCollectorǁset_gauge__mutmut_10, 
        'xǁMetricCollectorǁset_gauge__mutmut_11': xǁMetricCollectorǁset_gauge__mutmut_11, 
        'xǁMetricCollectorǁset_gauge__mutmut_12': xǁMetricCollectorǁset_gauge__mutmut_12, 
        'xǁMetricCollectorǁset_gauge__mutmut_13': xǁMetricCollectorǁset_gauge__mutmut_13, 
        'xǁMetricCollectorǁset_gauge__mutmut_14': xǁMetricCollectorǁset_gauge__mutmut_14
    }
    
    def set_gauge(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁset_gauge__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁset_gauge__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_gauge.__signature__ = _mutmut_signature(xǁMetricCollectorǁset_gauge__mutmut_orig)
    xǁMetricCollectorǁset_gauge__mutmut_orig.__name__ = 'xǁMetricCollectorǁset_gauge'

    def xǁMetricCollectorǁobserve__mutmut_orig(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_1(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = None
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_2(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels and {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_3(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = None

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_4(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(None, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_5(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, None)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_6(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_7(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, )

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_8(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(None)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_9(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) >= self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_10(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = None
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_11(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][+self._max_history:]
            self._record_point(name, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_12(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(None, value, labels)

    def xǁMetricCollectorǁobserve__mutmut_13(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, None, labels)

    def xǁMetricCollectorǁobserve__mutmut_14(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, None)

    def xǁMetricCollectorǁobserve__mutmut_15(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(value, labels)

    def xǁMetricCollectorǁobserve__mutmut_16(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, labels)

    def xǁMetricCollectorǁobserve__mutmut_17(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram observation.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional dimension labels.
        """
        labels = labels or {}
        key = self._make_key(name, labels)

        with self._lock:
            self._histograms[key].append(value)
            # Bound histogram size (safeguard)
            if len(self._histograms[key]) > self._max_history:
                self._histograms[key] = self._histograms[key][-self._max_history:]
            self._record_point(name, value, )
    
    xǁMetricCollectorǁobserve__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁobserve__mutmut_1': xǁMetricCollectorǁobserve__mutmut_1, 
        'xǁMetricCollectorǁobserve__mutmut_2': xǁMetricCollectorǁobserve__mutmut_2, 
        'xǁMetricCollectorǁobserve__mutmut_3': xǁMetricCollectorǁobserve__mutmut_3, 
        'xǁMetricCollectorǁobserve__mutmut_4': xǁMetricCollectorǁobserve__mutmut_4, 
        'xǁMetricCollectorǁobserve__mutmut_5': xǁMetricCollectorǁobserve__mutmut_5, 
        'xǁMetricCollectorǁobserve__mutmut_6': xǁMetricCollectorǁobserve__mutmut_6, 
        'xǁMetricCollectorǁobserve__mutmut_7': xǁMetricCollectorǁobserve__mutmut_7, 
        'xǁMetricCollectorǁobserve__mutmut_8': xǁMetricCollectorǁobserve__mutmut_8, 
        'xǁMetricCollectorǁobserve__mutmut_9': xǁMetricCollectorǁobserve__mutmut_9, 
        'xǁMetricCollectorǁobserve__mutmut_10': xǁMetricCollectorǁobserve__mutmut_10, 
        'xǁMetricCollectorǁobserve__mutmut_11': xǁMetricCollectorǁobserve__mutmut_11, 
        'xǁMetricCollectorǁobserve__mutmut_12': xǁMetricCollectorǁobserve__mutmut_12, 
        'xǁMetricCollectorǁobserve__mutmut_13': xǁMetricCollectorǁobserve__mutmut_13, 
        'xǁMetricCollectorǁobserve__mutmut_14': xǁMetricCollectorǁobserve__mutmut_14, 
        'xǁMetricCollectorǁobserve__mutmut_15': xǁMetricCollectorǁobserve__mutmut_15, 
        'xǁMetricCollectorǁobserve__mutmut_16': xǁMetricCollectorǁobserve__mutmut_16, 
        'xǁMetricCollectorǁobserve__mutmut_17': xǁMetricCollectorǁobserve__mutmut_17
    }
    
    def observe(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁobserve__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁobserve__mutmut_mutants"), args, kwargs, self)
        return result 
    
    observe.__signature__ = _mutmut_signature(xǁMetricCollectorǁobserve__mutmut_orig)
    xǁMetricCollectorǁobserve__mutmut_orig.__name__ = 'xǁMetricCollectorǁobserve'

    def xǁMetricCollectorǁ_make_key__mutmut_orig(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        # Truncate labels (safeguard)
        truncated = {
            k[:MAX_LABEL_LENGTH]: v[:MAX_LABEL_LENGTH]
            for k, v in labels.items()
        }
        label_str = ",".join(f"{k}={v}" for k, v in sorted(truncated.items()))
        return f"{name}{{{label_str}}}"

    def xǁMetricCollectorǁ_make_key__mutmut_1(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if labels:
            return name
        # Truncate labels (safeguard)
        truncated = {
            k[:MAX_LABEL_LENGTH]: v[:MAX_LABEL_LENGTH]
            for k, v in labels.items()
        }
        label_str = ",".join(f"{k}={v}" for k, v in sorted(truncated.items()))
        return f"{name}{{{label_str}}}"

    def xǁMetricCollectorǁ_make_key__mutmut_2(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        # Truncate labels (safeguard)
        truncated = None
        label_str = ",".join(f"{k}={v}" for k, v in sorted(truncated.items()))
        return f"{name}{{{label_str}}}"

    def xǁMetricCollectorǁ_make_key__mutmut_3(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        # Truncate labels (safeguard)
        truncated = {
            k[:MAX_LABEL_LENGTH]: v[:MAX_LABEL_LENGTH]
            for k, v in labels.items()
        }
        label_str = None
        return f"{name}{{{label_str}}}"

    def xǁMetricCollectorǁ_make_key__mutmut_4(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        # Truncate labels (safeguard)
        truncated = {
            k[:MAX_LABEL_LENGTH]: v[:MAX_LABEL_LENGTH]
            for k, v in labels.items()
        }
        label_str = ",".join(None)
        return f"{name}{{{label_str}}}"

    def xǁMetricCollectorǁ_make_key__mutmut_5(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        # Truncate labels (safeguard)
        truncated = {
            k[:MAX_LABEL_LENGTH]: v[:MAX_LABEL_LENGTH]
            for k, v in labels.items()
        }
        label_str = "XX,XX".join(f"{k}={v}" for k, v in sorted(truncated.items()))
        return f"{name}{{{label_str}}}"

    def xǁMetricCollectorǁ_make_key__mutmut_6(self, name: str, labels: dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        # Truncate labels (safeguard)
        truncated = {
            k[:MAX_LABEL_LENGTH]: v[:MAX_LABEL_LENGTH]
            for k, v in labels.items()
        }
        label_str = ",".join(f"{k}={v}" for k, v in sorted(None))
        return f"{name}{{{label_str}}}"
    
    xǁMetricCollectorǁ_make_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁ_make_key__mutmut_1': xǁMetricCollectorǁ_make_key__mutmut_1, 
        'xǁMetricCollectorǁ_make_key__mutmut_2': xǁMetricCollectorǁ_make_key__mutmut_2, 
        'xǁMetricCollectorǁ_make_key__mutmut_3': xǁMetricCollectorǁ_make_key__mutmut_3, 
        'xǁMetricCollectorǁ_make_key__mutmut_4': xǁMetricCollectorǁ_make_key__mutmut_4, 
        'xǁMetricCollectorǁ_make_key__mutmut_5': xǁMetricCollectorǁ_make_key__mutmut_5, 
        'xǁMetricCollectorǁ_make_key__mutmut_6': xǁMetricCollectorǁ_make_key__mutmut_6
    }
    
    def _make_key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁ_make_key__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁ_make_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _make_key.__signature__ = _mutmut_signature(xǁMetricCollectorǁ_make_key__mutmut_orig)
    xǁMetricCollectorǁ_make_key__mutmut_orig.__name__ = 'xǁMetricCollectorǁ_make_key'

    def xǁMetricCollectorǁ_record_point__mutmut_orig(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_1(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = None
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_2(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=None,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_3(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=None,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_4(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=None,
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_5(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=None,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_6(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_7(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_8(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_9(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_10(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(None).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_11(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(None)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_12(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) >= self._max_history:
            self._history = self._history[-self._max_history:]

    def xǁMetricCollectorǁ_record_point__mutmut_13(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = None

    def xǁMetricCollectorǁ_record_point__mutmut_14(
        self,
        name: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Record a metric point to history."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            labels=labels,
        )
        self._history.append(point)

        # Bound history (safeguard)
        if len(self._history) > self._max_history:
            self._history = self._history[+self._max_history:]
    
    xǁMetricCollectorǁ_record_point__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁ_record_point__mutmut_1': xǁMetricCollectorǁ_record_point__mutmut_1, 
        'xǁMetricCollectorǁ_record_point__mutmut_2': xǁMetricCollectorǁ_record_point__mutmut_2, 
        'xǁMetricCollectorǁ_record_point__mutmut_3': xǁMetricCollectorǁ_record_point__mutmut_3, 
        'xǁMetricCollectorǁ_record_point__mutmut_4': xǁMetricCollectorǁ_record_point__mutmut_4, 
        'xǁMetricCollectorǁ_record_point__mutmut_5': xǁMetricCollectorǁ_record_point__mutmut_5, 
        'xǁMetricCollectorǁ_record_point__mutmut_6': xǁMetricCollectorǁ_record_point__mutmut_6, 
        'xǁMetricCollectorǁ_record_point__mutmut_7': xǁMetricCollectorǁ_record_point__mutmut_7, 
        'xǁMetricCollectorǁ_record_point__mutmut_8': xǁMetricCollectorǁ_record_point__mutmut_8, 
        'xǁMetricCollectorǁ_record_point__mutmut_9': xǁMetricCollectorǁ_record_point__mutmut_9, 
        'xǁMetricCollectorǁ_record_point__mutmut_10': xǁMetricCollectorǁ_record_point__mutmut_10, 
        'xǁMetricCollectorǁ_record_point__mutmut_11': xǁMetricCollectorǁ_record_point__mutmut_11, 
        'xǁMetricCollectorǁ_record_point__mutmut_12': xǁMetricCollectorǁ_record_point__mutmut_12, 
        'xǁMetricCollectorǁ_record_point__mutmut_13': xǁMetricCollectorǁ_record_point__mutmut_13, 
        'xǁMetricCollectorǁ_record_point__mutmut_14': xǁMetricCollectorǁ_record_point__mutmut_14
    }
    
    def _record_point(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁ_record_point__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁ_record_point__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _record_point.__signature__ = _mutmut_signature(xǁMetricCollectorǁ_record_point__mutmut_orig)
    xǁMetricCollectorǁ_record_point__mutmut_orig.__name__ = 'xǁMetricCollectorǁ_record_point'

    def xǁMetricCollectorǁget_counter__mutmut_orig(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(key, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_1(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = None
        with self._lock:
            return self._counters.get(key, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_2(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(None, labels or {})
        with self._lock:
            return self._counters.get(key, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_3(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, None)
        with self._lock:
            return self._counters.get(key, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_4(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(labels or {})
        with self._lock:
            return self._counters.get(key, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_5(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, )
        with self._lock:
            return self._counters.get(key, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_6(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels and {})
        with self._lock:
            return self._counters.get(key, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_7(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(None, 0.0)

    def xǁMetricCollectorǁget_counter__mutmut_8(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(key, None)

    def xǁMetricCollectorǁget_counter__mutmut_9(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(0.0)

    def xǁMetricCollectorǁget_counter__mutmut_10(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(key, )

    def xǁMetricCollectorǁget_counter__mutmut_11(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(key, 1.0)
    
    xǁMetricCollectorǁget_counter__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁget_counter__mutmut_1': xǁMetricCollectorǁget_counter__mutmut_1, 
        'xǁMetricCollectorǁget_counter__mutmut_2': xǁMetricCollectorǁget_counter__mutmut_2, 
        'xǁMetricCollectorǁget_counter__mutmut_3': xǁMetricCollectorǁget_counter__mutmut_3, 
        'xǁMetricCollectorǁget_counter__mutmut_4': xǁMetricCollectorǁget_counter__mutmut_4, 
        'xǁMetricCollectorǁget_counter__mutmut_5': xǁMetricCollectorǁget_counter__mutmut_5, 
        'xǁMetricCollectorǁget_counter__mutmut_6': xǁMetricCollectorǁget_counter__mutmut_6, 
        'xǁMetricCollectorǁget_counter__mutmut_7': xǁMetricCollectorǁget_counter__mutmut_7, 
        'xǁMetricCollectorǁget_counter__mutmut_8': xǁMetricCollectorǁget_counter__mutmut_8, 
        'xǁMetricCollectorǁget_counter__mutmut_9': xǁMetricCollectorǁget_counter__mutmut_9, 
        'xǁMetricCollectorǁget_counter__mutmut_10': xǁMetricCollectorǁget_counter__mutmut_10, 
        'xǁMetricCollectorǁget_counter__mutmut_11': xǁMetricCollectorǁget_counter__mutmut_11
    }
    
    def get_counter(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁget_counter__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁget_counter__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_counter.__signature__ = _mutmut_signature(xǁMetricCollectorǁget_counter__mutmut_orig)
    xǁMetricCollectorǁget_counter__mutmut_orig.__name__ = 'xǁMetricCollectorǁget_counter'

    def xǁMetricCollectorǁget_gauge__mutmut_orig(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(key, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_1(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = None
        with self._lock:
            return self._gauges.get(key, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_2(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(None, labels or {})
        with self._lock:
            return self._gauges.get(key, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_3(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, None)
        with self._lock:
            return self._gauges.get(key, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_4(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(labels or {})
        with self._lock:
            return self._gauges.get(key, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_5(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, )
        with self._lock:
            return self._gauges.get(key, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_6(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels and {})
        with self._lock:
            return self._gauges.get(key, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_7(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(None, 0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_8(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(key, None)

    def xǁMetricCollectorǁget_gauge__mutmut_9(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(0.0)

    def xǁMetricCollectorǁget_gauge__mutmut_10(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(key, )

    def xǁMetricCollectorǁget_gauge__mutmut_11(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(key, 1.0)
    
    xǁMetricCollectorǁget_gauge__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁget_gauge__mutmut_1': xǁMetricCollectorǁget_gauge__mutmut_1, 
        'xǁMetricCollectorǁget_gauge__mutmut_2': xǁMetricCollectorǁget_gauge__mutmut_2, 
        'xǁMetricCollectorǁget_gauge__mutmut_3': xǁMetricCollectorǁget_gauge__mutmut_3, 
        'xǁMetricCollectorǁget_gauge__mutmut_4': xǁMetricCollectorǁget_gauge__mutmut_4, 
        'xǁMetricCollectorǁget_gauge__mutmut_5': xǁMetricCollectorǁget_gauge__mutmut_5, 
        'xǁMetricCollectorǁget_gauge__mutmut_6': xǁMetricCollectorǁget_gauge__mutmut_6, 
        'xǁMetricCollectorǁget_gauge__mutmut_7': xǁMetricCollectorǁget_gauge__mutmut_7, 
        'xǁMetricCollectorǁget_gauge__mutmut_8': xǁMetricCollectorǁget_gauge__mutmut_8, 
        'xǁMetricCollectorǁget_gauge__mutmut_9': xǁMetricCollectorǁget_gauge__mutmut_9, 
        'xǁMetricCollectorǁget_gauge__mutmut_10': xǁMetricCollectorǁget_gauge__mutmut_10, 
        'xǁMetricCollectorǁget_gauge__mutmut_11': xǁMetricCollectorǁget_gauge__mutmut_11
    }
    
    def get_gauge(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁget_gauge__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁget_gauge__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_gauge.__signature__ = _mutmut_signature(xǁMetricCollectorǁget_gauge__mutmut_orig)
    xǁMetricCollectorǁget_gauge__mutmut_orig.__name__ = 'xǁMetricCollectorǁget_gauge'

    def xǁMetricCollectorǁget_histogram_summary__mutmut_orig(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_1(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = None
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_2(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(None, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_3(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, None)
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_4(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_5(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, )
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_6(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels and {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_7(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = None
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_8(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(None, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_9(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, None)
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_10(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get([])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_11(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, )
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_12(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_13(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=None,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_14(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=None,
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_15(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=None,
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_16(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=None,
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_17(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=None,
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_18(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=None,
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_19(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_20(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_21(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_22(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_23(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_24(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_25(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(None),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_26(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(None),
                max_value=max(values),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_27(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(None),
                avg_value=sum(values) / len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_28(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) * len(values),
            )

    def xǁMetricCollectorǁget_histogram_summary__mutmut_29(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> MetricSummary | None:
        """Get summary statistics for a histogram."""
        key = self._make_key(name, labels or {})
        with self._lock:
            values = self._histograms.get(key, [])
            if not values:
                return None
            return MetricSummary(
                name=name,
                count=len(values),
                total=sum(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(None) / len(values),
            )
    
    xǁMetricCollectorǁget_histogram_summary__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁget_histogram_summary__mutmut_1': xǁMetricCollectorǁget_histogram_summary__mutmut_1, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_2': xǁMetricCollectorǁget_histogram_summary__mutmut_2, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_3': xǁMetricCollectorǁget_histogram_summary__mutmut_3, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_4': xǁMetricCollectorǁget_histogram_summary__mutmut_4, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_5': xǁMetricCollectorǁget_histogram_summary__mutmut_5, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_6': xǁMetricCollectorǁget_histogram_summary__mutmut_6, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_7': xǁMetricCollectorǁget_histogram_summary__mutmut_7, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_8': xǁMetricCollectorǁget_histogram_summary__mutmut_8, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_9': xǁMetricCollectorǁget_histogram_summary__mutmut_9, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_10': xǁMetricCollectorǁget_histogram_summary__mutmut_10, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_11': xǁMetricCollectorǁget_histogram_summary__mutmut_11, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_12': xǁMetricCollectorǁget_histogram_summary__mutmut_12, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_13': xǁMetricCollectorǁget_histogram_summary__mutmut_13, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_14': xǁMetricCollectorǁget_histogram_summary__mutmut_14, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_15': xǁMetricCollectorǁget_histogram_summary__mutmut_15, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_16': xǁMetricCollectorǁget_histogram_summary__mutmut_16, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_17': xǁMetricCollectorǁget_histogram_summary__mutmut_17, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_18': xǁMetricCollectorǁget_histogram_summary__mutmut_18, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_19': xǁMetricCollectorǁget_histogram_summary__mutmut_19, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_20': xǁMetricCollectorǁget_histogram_summary__mutmut_20, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_21': xǁMetricCollectorǁget_histogram_summary__mutmut_21, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_22': xǁMetricCollectorǁget_histogram_summary__mutmut_22, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_23': xǁMetricCollectorǁget_histogram_summary__mutmut_23, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_24': xǁMetricCollectorǁget_histogram_summary__mutmut_24, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_25': xǁMetricCollectorǁget_histogram_summary__mutmut_25, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_26': xǁMetricCollectorǁget_histogram_summary__mutmut_26, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_27': xǁMetricCollectorǁget_histogram_summary__mutmut_27, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_28': xǁMetricCollectorǁget_histogram_summary__mutmut_28, 
        'xǁMetricCollectorǁget_histogram_summary__mutmut_29': xǁMetricCollectorǁget_histogram_summary__mutmut_29
    }
    
    def get_histogram_summary(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁget_histogram_summary__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁget_histogram_summary__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_histogram_summary.__signature__ = _mutmut_signature(xǁMetricCollectorǁget_histogram_summary__mutmut_orig)
    xǁMetricCollectorǁget_histogram_summary__mutmut_orig.__name__ = 'xǁMetricCollectorǁget_histogram_summary'

    def xǁMetricCollectorǁget_all_metrics__mutmut_orig(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_1(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "XXcountersXX": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_2(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "COUNTERS": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_3(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(None),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_4(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "XXgaugesXX": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_5(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "GAUGES": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_6(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(None),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_7(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "XXhistogramsXX": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_8(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "HISTOGRAMS": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_9(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "XXcountXX": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_10(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "COUNT": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_11(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "XXsumXX": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_12(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "SUM": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_13(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(None),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_14(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "XXminXX": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_15(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "MIN": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_16(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(None) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_17(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 1,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_18(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "XXmaxXX": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_19(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "MAX": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_20(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(None) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def xǁMetricCollectorǁget_all_metrics__mutmut_21(self) -> dict[str, Any]:
        """Export all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 1,
                    }
                    for k, v in self._histograms.items()
                },
            }
    
    xǁMetricCollectorǁget_all_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁget_all_metrics__mutmut_1': xǁMetricCollectorǁget_all_metrics__mutmut_1, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_2': xǁMetricCollectorǁget_all_metrics__mutmut_2, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_3': xǁMetricCollectorǁget_all_metrics__mutmut_3, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_4': xǁMetricCollectorǁget_all_metrics__mutmut_4, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_5': xǁMetricCollectorǁget_all_metrics__mutmut_5, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_6': xǁMetricCollectorǁget_all_metrics__mutmut_6, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_7': xǁMetricCollectorǁget_all_metrics__mutmut_7, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_8': xǁMetricCollectorǁget_all_metrics__mutmut_8, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_9': xǁMetricCollectorǁget_all_metrics__mutmut_9, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_10': xǁMetricCollectorǁget_all_metrics__mutmut_10, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_11': xǁMetricCollectorǁget_all_metrics__mutmut_11, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_12': xǁMetricCollectorǁget_all_metrics__mutmut_12, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_13': xǁMetricCollectorǁget_all_metrics__mutmut_13, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_14': xǁMetricCollectorǁget_all_metrics__mutmut_14, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_15': xǁMetricCollectorǁget_all_metrics__mutmut_15, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_16': xǁMetricCollectorǁget_all_metrics__mutmut_16, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_17': xǁMetricCollectorǁget_all_metrics__mutmut_17, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_18': xǁMetricCollectorǁget_all_metrics__mutmut_18, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_19': xǁMetricCollectorǁget_all_metrics__mutmut_19, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_20': xǁMetricCollectorǁget_all_metrics__mutmut_20, 
        'xǁMetricCollectorǁget_all_metrics__mutmut_21': xǁMetricCollectorǁget_all_metrics__mutmut_21
    }
    
    def get_all_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁget_all_metrics__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁget_all_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_all_metrics.__signature__ = _mutmut_signature(xǁMetricCollectorǁget_all_metrics__mutmut_orig)
    xǁMetricCollectorǁget_all_metrics__mutmut_orig.__name__ = 'xǁMetricCollectorǁget_all_metrics'

    def xǁMetricCollectorǁreset__mutmut_orig(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._history.clear()
        logger.info("Metrics reset")

    def xǁMetricCollectorǁreset__mutmut_1(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._history.clear()
        logger.info(None)

    def xǁMetricCollectorǁreset__mutmut_2(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._history.clear()
        logger.info("XXMetrics resetXX")

    def xǁMetricCollectorǁreset__mutmut_3(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._history.clear()
        logger.info("metrics reset")

    def xǁMetricCollectorǁreset__mutmut_4(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._history.clear()
        logger.info("METRICS RESET")
    
    xǁMetricCollectorǁreset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricCollectorǁreset__mutmut_1': xǁMetricCollectorǁreset__mutmut_1, 
        'xǁMetricCollectorǁreset__mutmut_2': xǁMetricCollectorǁreset__mutmut_2, 
        'xǁMetricCollectorǁreset__mutmut_3': xǁMetricCollectorǁreset__mutmut_3, 
        'xǁMetricCollectorǁreset__mutmut_4': xǁMetricCollectorǁreset__mutmut_4
    }
    
    def reset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricCollectorǁreset__mutmut_orig"), object.__getattribute__(self, "xǁMetricCollectorǁreset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    reset.__signature__ = _mutmut_signature(xǁMetricCollectorǁreset__mutmut_orig)
    xǁMetricCollectorǁreset__mutmut_orig.__name__ = 'xǁMetricCollectorǁreset'


class MCPMetrics:
    """High-level metrics for MCP operations.

    Pre-defined metrics for common MCP operations.
    """

    def xǁMCPMetricsǁ__init____mutmut_orig(self, collector: MetricCollector | None = None) -> None:
        """Initialize MCP metrics."""
        self.collector = collector or MetricCollector()

    def xǁMCPMetricsǁ__init____mutmut_1(self, collector: MetricCollector | None = None) -> None:
        """Initialize MCP metrics."""
        self.collector = None

    def xǁMCPMetricsǁ__init____mutmut_2(self, collector: MetricCollector | None = None) -> None:
        """Initialize MCP metrics."""
        self.collector = collector and MetricCollector()
    
    xǁMCPMetricsǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁ__init____mutmut_1': xǁMCPMetricsǁ__init____mutmut_1, 
        'xǁMCPMetricsǁ__init____mutmut_2': xǁMCPMetricsǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPMetricsǁ__init____mutmut_orig)
    xǁMCPMetricsǁ__init____mutmut_orig.__name__ = 'xǁMCPMetricsǁ__init__'

    def xǁMCPMetricsǁrecord_query__mutmut_orig(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_1(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 1,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_2(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = None

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_3(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"XXadapterXX": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_4(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"ADAPTER": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_5(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "XXsuccessXX": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_6(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "SUCCESS": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_7(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).upper()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_8(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(None).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_9(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment(None, labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_10(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=None)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_11(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment(labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_12(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", )
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_13(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("XXmcp_queries_totalXX", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_14(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("MCP_QUERIES_TOTAL", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_15(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = None
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_16(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"XXadapterXX": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_17(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"ADAPTER": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_18(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            None, duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_19(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", None, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_20(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=None
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_21(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_22(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_23(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_24(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "XXmcp_query_duration_msXX", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_25(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "MCP_QUERY_DURATION_MS", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_26(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            None, result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_27(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", None, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_28(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, labels=None
        )

    def xǁMCPMetricsǁrecord_query__mutmut_29(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_30(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_31(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "mcp_query_results", result_count, )

    def xǁMCPMetricsǁrecord_query__mutmut_32(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "XXmcp_query_resultsXX", result_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_query__mutmut_33(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        result_count: int = 0,
    ) -> None:
        """Record a query operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_queries_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_query_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.observe(
            "MCP_QUERY_RESULTS", result_count, labels=adapter_labels
        )
    
    xǁMCPMetricsǁrecord_query__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁrecord_query__mutmut_1': xǁMCPMetricsǁrecord_query__mutmut_1, 
        'xǁMCPMetricsǁrecord_query__mutmut_2': xǁMCPMetricsǁrecord_query__mutmut_2, 
        'xǁMCPMetricsǁrecord_query__mutmut_3': xǁMCPMetricsǁrecord_query__mutmut_3, 
        'xǁMCPMetricsǁrecord_query__mutmut_4': xǁMCPMetricsǁrecord_query__mutmut_4, 
        'xǁMCPMetricsǁrecord_query__mutmut_5': xǁMCPMetricsǁrecord_query__mutmut_5, 
        'xǁMCPMetricsǁrecord_query__mutmut_6': xǁMCPMetricsǁrecord_query__mutmut_6, 
        'xǁMCPMetricsǁrecord_query__mutmut_7': xǁMCPMetricsǁrecord_query__mutmut_7, 
        'xǁMCPMetricsǁrecord_query__mutmut_8': xǁMCPMetricsǁrecord_query__mutmut_8, 
        'xǁMCPMetricsǁrecord_query__mutmut_9': xǁMCPMetricsǁrecord_query__mutmut_9, 
        'xǁMCPMetricsǁrecord_query__mutmut_10': xǁMCPMetricsǁrecord_query__mutmut_10, 
        'xǁMCPMetricsǁrecord_query__mutmut_11': xǁMCPMetricsǁrecord_query__mutmut_11, 
        'xǁMCPMetricsǁrecord_query__mutmut_12': xǁMCPMetricsǁrecord_query__mutmut_12, 
        'xǁMCPMetricsǁrecord_query__mutmut_13': xǁMCPMetricsǁrecord_query__mutmut_13, 
        'xǁMCPMetricsǁrecord_query__mutmut_14': xǁMCPMetricsǁrecord_query__mutmut_14, 
        'xǁMCPMetricsǁrecord_query__mutmut_15': xǁMCPMetricsǁrecord_query__mutmut_15, 
        'xǁMCPMetricsǁrecord_query__mutmut_16': xǁMCPMetricsǁrecord_query__mutmut_16, 
        'xǁMCPMetricsǁrecord_query__mutmut_17': xǁMCPMetricsǁrecord_query__mutmut_17, 
        'xǁMCPMetricsǁrecord_query__mutmut_18': xǁMCPMetricsǁrecord_query__mutmut_18, 
        'xǁMCPMetricsǁrecord_query__mutmut_19': xǁMCPMetricsǁrecord_query__mutmut_19, 
        'xǁMCPMetricsǁrecord_query__mutmut_20': xǁMCPMetricsǁrecord_query__mutmut_20, 
        'xǁMCPMetricsǁrecord_query__mutmut_21': xǁMCPMetricsǁrecord_query__mutmut_21, 
        'xǁMCPMetricsǁrecord_query__mutmut_22': xǁMCPMetricsǁrecord_query__mutmut_22, 
        'xǁMCPMetricsǁrecord_query__mutmut_23': xǁMCPMetricsǁrecord_query__mutmut_23, 
        'xǁMCPMetricsǁrecord_query__mutmut_24': xǁMCPMetricsǁrecord_query__mutmut_24, 
        'xǁMCPMetricsǁrecord_query__mutmut_25': xǁMCPMetricsǁrecord_query__mutmut_25, 
        'xǁMCPMetricsǁrecord_query__mutmut_26': xǁMCPMetricsǁrecord_query__mutmut_26, 
        'xǁMCPMetricsǁrecord_query__mutmut_27': xǁMCPMetricsǁrecord_query__mutmut_27, 
        'xǁMCPMetricsǁrecord_query__mutmut_28': xǁMCPMetricsǁrecord_query__mutmut_28, 
        'xǁMCPMetricsǁrecord_query__mutmut_29': xǁMCPMetricsǁrecord_query__mutmut_29, 
        'xǁMCPMetricsǁrecord_query__mutmut_30': xǁMCPMetricsǁrecord_query__mutmut_30, 
        'xǁMCPMetricsǁrecord_query__mutmut_31': xǁMCPMetricsǁrecord_query__mutmut_31, 
        'xǁMCPMetricsǁrecord_query__mutmut_32': xǁMCPMetricsǁrecord_query__mutmut_32, 
        'xǁMCPMetricsǁrecord_query__mutmut_33': xǁMCPMetricsǁrecord_query__mutmut_33
    }
    
    def record_query(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁrecord_query__mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁrecord_query__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_query.__signature__ = _mutmut_signature(xǁMCPMetricsǁrecord_query__mutmut_orig)
    xǁMCPMetricsǁrecord_query__mutmut_orig.__name__ = 'xǁMCPMetricsǁrecord_query'

    def xǁMCPMetricsǁrecord_upsert__mutmut_orig(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_1(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 1,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_2(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = None

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_3(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"XXadapterXX": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_4(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"ADAPTER": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_5(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "XXsuccessXX": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_6(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "SUCCESS": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_7(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).upper()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_8(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(None).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_9(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment(None, labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_10(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=None)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_11(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment(labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_12(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", )
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_13(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("XXmcp_upserts_totalXX", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_14(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("MCP_UPSERTS_TOTAL", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_15(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = None
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_16(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"XXadapterXX": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_17(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"ADAPTER": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_18(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            None, duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_19(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", None, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_20(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=None
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_21(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_22(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_23(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_24(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "XXmcp_upsert_duration_msXX", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_25(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "MCP_UPSERT_DURATION_MS", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_26(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            None, vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_27(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", None, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_28(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, labels=None
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_29(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_30(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_31(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "mcp_vectors_upserted", vector_count, )

    def xǁMCPMetricsǁrecord_upsert__mutmut_32(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "XXmcp_vectors_upsertedXX", vector_count, labels=adapter_labels
        )

    def xǁMCPMetricsǁrecord_upsert__mutmut_33(
        self,
        adapter: str,
        duration_ms: float,
        success: bool,
        vector_count: int = 0,
    ) -> None:
        """Record an upsert operation."""
        labels = {"adapter": adapter, "success": str(success).lower()}

        self.collector.increment("mcp_upserts_total", labels=labels)
        adapter_labels = {"adapter": adapter}
        self.collector.observe(
            "mcp_upsert_duration_ms", duration_ms, labels=adapter_labels
        )
        self.collector.increment(
            "MCP_VECTORS_UPSERTED", vector_count, labels=adapter_labels
        )
    
    xǁMCPMetricsǁrecord_upsert__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁrecord_upsert__mutmut_1': xǁMCPMetricsǁrecord_upsert__mutmut_1, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_2': xǁMCPMetricsǁrecord_upsert__mutmut_2, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_3': xǁMCPMetricsǁrecord_upsert__mutmut_3, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_4': xǁMCPMetricsǁrecord_upsert__mutmut_4, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_5': xǁMCPMetricsǁrecord_upsert__mutmut_5, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_6': xǁMCPMetricsǁrecord_upsert__mutmut_6, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_7': xǁMCPMetricsǁrecord_upsert__mutmut_7, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_8': xǁMCPMetricsǁrecord_upsert__mutmut_8, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_9': xǁMCPMetricsǁrecord_upsert__mutmut_9, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_10': xǁMCPMetricsǁrecord_upsert__mutmut_10, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_11': xǁMCPMetricsǁrecord_upsert__mutmut_11, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_12': xǁMCPMetricsǁrecord_upsert__mutmut_12, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_13': xǁMCPMetricsǁrecord_upsert__mutmut_13, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_14': xǁMCPMetricsǁrecord_upsert__mutmut_14, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_15': xǁMCPMetricsǁrecord_upsert__mutmut_15, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_16': xǁMCPMetricsǁrecord_upsert__mutmut_16, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_17': xǁMCPMetricsǁrecord_upsert__mutmut_17, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_18': xǁMCPMetricsǁrecord_upsert__mutmut_18, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_19': xǁMCPMetricsǁrecord_upsert__mutmut_19, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_20': xǁMCPMetricsǁrecord_upsert__mutmut_20, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_21': xǁMCPMetricsǁrecord_upsert__mutmut_21, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_22': xǁMCPMetricsǁrecord_upsert__mutmut_22, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_23': xǁMCPMetricsǁrecord_upsert__mutmut_23, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_24': xǁMCPMetricsǁrecord_upsert__mutmut_24, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_25': xǁMCPMetricsǁrecord_upsert__mutmut_25, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_26': xǁMCPMetricsǁrecord_upsert__mutmut_26, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_27': xǁMCPMetricsǁrecord_upsert__mutmut_27, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_28': xǁMCPMetricsǁrecord_upsert__mutmut_28, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_29': xǁMCPMetricsǁrecord_upsert__mutmut_29, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_30': xǁMCPMetricsǁrecord_upsert__mutmut_30, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_31': xǁMCPMetricsǁrecord_upsert__mutmut_31, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_32': xǁMCPMetricsǁrecord_upsert__mutmut_32, 
        'xǁMCPMetricsǁrecord_upsert__mutmut_33': xǁMCPMetricsǁrecord_upsert__mutmut_33
    }
    
    def record_upsert(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁrecord_upsert__mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁrecord_upsert__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_upsert.__signature__ = _mutmut_signature(xǁMCPMetricsǁrecord_upsert__mutmut_orig)
    xǁMCPMetricsǁrecord_upsert__mutmut_orig.__name__ = 'xǁMCPMetricsǁrecord_upsert'

    def xǁMCPMetricsǁrecord_error__mutmut_orig(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total",
            labels={"adapter": adapter, "error_type": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_1(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            None,
            labels={"adapter": adapter, "error_type": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_2(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total",
            labels=None
        )

    def xǁMCPMetricsǁrecord_error__mutmut_3(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            labels={"adapter": adapter, "error_type": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_4(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total",
            )

    def xǁMCPMetricsǁrecord_error__mutmut_5(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "XXmcp_errors_totalXX",
            labels={"adapter": adapter, "error_type": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_6(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "MCP_ERRORS_TOTAL",
            labels={"adapter": adapter, "error_type": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_7(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total",
            labels={"XXadapterXX": adapter, "error_type": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_8(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total",
            labels={"ADAPTER": adapter, "error_type": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_9(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total",
            labels={"adapter": adapter, "XXerror_typeXX": error_type}
        )

    def xǁMCPMetricsǁrecord_error__mutmut_10(self, adapter: str, error_type: str) -> None:
        """Record an error."""
        self.collector.increment(
            "mcp_errors_total",
            labels={"adapter": adapter, "ERROR_TYPE": error_type}
        )
    
    xǁMCPMetricsǁrecord_error__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁrecord_error__mutmut_1': xǁMCPMetricsǁrecord_error__mutmut_1, 
        'xǁMCPMetricsǁrecord_error__mutmut_2': xǁMCPMetricsǁrecord_error__mutmut_2, 
        'xǁMCPMetricsǁrecord_error__mutmut_3': xǁMCPMetricsǁrecord_error__mutmut_3, 
        'xǁMCPMetricsǁrecord_error__mutmut_4': xǁMCPMetricsǁrecord_error__mutmut_4, 
        'xǁMCPMetricsǁrecord_error__mutmut_5': xǁMCPMetricsǁrecord_error__mutmut_5, 
        'xǁMCPMetricsǁrecord_error__mutmut_6': xǁMCPMetricsǁrecord_error__mutmut_6, 
        'xǁMCPMetricsǁrecord_error__mutmut_7': xǁMCPMetricsǁrecord_error__mutmut_7, 
        'xǁMCPMetricsǁrecord_error__mutmut_8': xǁMCPMetricsǁrecord_error__mutmut_8, 
        'xǁMCPMetricsǁrecord_error__mutmut_9': xǁMCPMetricsǁrecord_error__mutmut_9, 
        'xǁMCPMetricsǁrecord_error__mutmut_10': xǁMCPMetricsǁrecord_error__mutmut_10
    }
    
    def record_error(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁrecord_error__mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁrecord_error__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_error.__signature__ = _mutmut_signature(xǁMCPMetricsǁrecord_error__mutmut_orig)
    xǁMCPMetricsǁrecord_error__mutmut_orig.__name__ = 'xǁMCPMetricsǁrecord_error'

    def xǁMCPMetricsǁset_connection_status__mutmut_orig(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            1.0 if connected else 0.0,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_1(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            None,
            1.0 if connected else 0.0,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_2(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            None,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_3(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            1.0 if connected else 0.0,
            labels=None
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_4(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            1.0 if connected else 0.0,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_5(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_6(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            1.0 if connected else 0.0,
            )

    def xǁMCPMetricsǁset_connection_status__mutmut_7(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "XXmcp_connectedXX",
            1.0 if connected else 0.0,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_8(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "MCP_CONNECTED",
            1.0 if connected else 0.0,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_9(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            2.0 if connected else 0.0,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_10(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            1.0 if connected else 1.0,
            labels={"adapter": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_11(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            1.0 if connected else 0.0,
            labels={"XXadapterXX": adapter}
        )

    def xǁMCPMetricsǁset_connection_status__mutmut_12(self, adapter: str, connected: bool) -> None:
        """Set connection status gauge."""
        self.collector.set_gauge(
            "mcp_connected",
            1.0 if connected else 0.0,
            labels={"ADAPTER": adapter}
        )
    
    xǁMCPMetricsǁset_connection_status__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁset_connection_status__mutmut_1': xǁMCPMetricsǁset_connection_status__mutmut_1, 
        'xǁMCPMetricsǁset_connection_status__mutmut_2': xǁMCPMetricsǁset_connection_status__mutmut_2, 
        'xǁMCPMetricsǁset_connection_status__mutmut_3': xǁMCPMetricsǁset_connection_status__mutmut_3, 
        'xǁMCPMetricsǁset_connection_status__mutmut_4': xǁMCPMetricsǁset_connection_status__mutmut_4, 
        'xǁMCPMetricsǁset_connection_status__mutmut_5': xǁMCPMetricsǁset_connection_status__mutmut_5, 
        'xǁMCPMetricsǁset_connection_status__mutmut_6': xǁMCPMetricsǁset_connection_status__mutmut_6, 
        'xǁMCPMetricsǁset_connection_status__mutmut_7': xǁMCPMetricsǁset_connection_status__mutmut_7, 
        'xǁMCPMetricsǁset_connection_status__mutmut_8': xǁMCPMetricsǁset_connection_status__mutmut_8, 
        'xǁMCPMetricsǁset_connection_status__mutmut_9': xǁMCPMetricsǁset_connection_status__mutmut_9, 
        'xǁMCPMetricsǁset_connection_status__mutmut_10': xǁMCPMetricsǁset_connection_status__mutmut_10, 
        'xǁMCPMetricsǁset_connection_status__mutmut_11': xǁMCPMetricsǁset_connection_status__mutmut_11, 
        'xǁMCPMetricsǁset_connection_status__mutmut_12': xǁMCPMetricsǁset_connection_status__mutmut_12
    }
    
    def set_connection_status(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁset_connection_status__mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁset_connection_status__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_connection_status.__signature__ = _mutmut_signature(xǁMCPMetricsǁset_connection_status__mutmut_orig)
    xǁMCPMetricsǁset_connection_status__mutmut_orig.__name__ = 'xǁMCPMetricsǁset_connection_status'

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of MCP metrics."""
        return self.collector.get_all_metrics()
