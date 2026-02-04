"""MCP observability for metrics, tracing, and logging.

This module provides observability features including:
- Metrics collection and export
- Request tracing with context propagation
- Structured logging
- Performance monitoring
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from contextlib import contextmanager
from functools import wraps
import threading


logger = logging.getLogger(__name__)
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
class MetricValue:
    """A single metric value with metadata."""
    
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metric_type: str = "gauge"  # gauge, counter, histogram


@dataclass
class TraceSpan:
    """A trace span for request tracking."""
    
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    status: str = "ok"
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000


class MetricsRegistry:
    """Registry for collecting and exporting metrics."""
    
    def xǁMetricsRegistryǁ__init____mutmut_orig(self) -> None:
        """Initialize the metrics registry."""
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._labels: dict[str, dict[str, str]] = {}
        
    
    def xǁMetricsRegistryǁ__init____mutmut_1(self) -> None:
        """Initialize the metrics registry."""
        self._counters: dict[str, float] = None
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._labels: dict[str, dict[str, str]] = {}
        
    
    def xǁMetricsRegistryǁ__init____mutmut_2(self) -> None:
        """Initialize the metrics registry."""
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = None
        self._histograms: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._labels: dict[str, dict[str, str]] = {}
        
    
    def xǁMetricsRegistryǁ__init____mutmut_3(self) -> None:
        """Initialize the metrics registry."""
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = None
        self._lock = threading.Lock()
        self._labels: dict[str, dict[str, str]] = {}
        
    
    def xǁMetricsRegistryǁ__init____mutmut_4(self) -> None:
        """Initialize the metrics registry."""
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._lock = None
        self._labels: dict[str, dict[str, str]] = {}
        
    
    def xǁMetricsRegistryǁ__init____mutmut_5(self) -> None:
        """Initialize the metrics registry."""
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._labels: dict[str, dict[str, str]] = None
        
    
    xǁMetricsRegistryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsRegistryǁ__init____mutmut_1': xǁMetricsRegistryǁ__init____mutmut_1, 
        'xǁMetricsRegistryǁ__init____mutmut_2': xǁMetricsRegistryǁ__init____mutmut_2, 
        'xǁMetricsRegistryǁ__init____mutmut_3': xǁMetricsRegistryǁ__init____mutmut_3, 
        'xǁMetricsRegistryǁ__init____mutmut_4': xǁMetricsRegistryǁ__init____mutmut_4, 
        'xǁMetricsRegistryǁ__init____mutmut_5': xǁMetricsRegistryǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsRegistryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMetricsRegistryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMetricsRegistryǁ__init____mutmut_orig)
    xǁMetricsRegistryǁ__init____mutmut_orig.__name__ = 'xǁMetricsRegistryǁ__init__'
    def xǁMetricsRegistryǁincrement_counter__mutmut_orig(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_1(
        self,
        name: str,
        value: float = 2.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_2(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = None
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_3(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(None, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_4(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, None)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_5(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_6(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, )
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_7(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = None
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_8(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) - value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_9(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(None, 0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_10(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, None) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_11(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(0.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_12(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, ) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_13(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 1.0) + value
            if labels:
                self._labels[key] = labels
    def xǁMetricsRegistryǁincrement_counter__mutmut_14(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name.
            value: Amount to increment by.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value
            if labels:
                self._labels[key] = None
    
    xǁMetricsRegistryǁincrement_counter__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsRegistryǁincrement_counter__mutmut_1': xǁMetricsRegistryǁincrement_counter__mutmut_1, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_2': xǁMetricsRegistryǁincrement_counter__mutmut_2, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_3': xǁMetricsRegistryǁincrement_counter__mutmut_3, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_4': xǁMetricsRegistryǁincrement_counter__mutmut_4, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_5': xǁMetricsRegistryǁincrement_counter__mutmut_5, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_6': xǁMetricsRegistryǁincrement_counter__mutmut_6, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_7': xǁMetricsRegistryǁincrement_counter__mutmut_7, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_8': xǁMetricsRegistryǁincrement_counter__mutmut_8, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_9': xǁMetricsRegistryǁincrement_counter__mutmut_9, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_10': xǁMetricsRegistryǁincrement_counter__mutmut_10, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_11': xǁMetricsRegistryǁincrement_counter__mutmut_11, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_12': xǁMetricsRegistryǁincrement_counter__mutmut_12, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_13': xǁMetricsRegistryǁincrement_counter__mutmut_13, 
        'xǁMetricsRegistryǁincrement_counter__mutmut_14': xǁMetricsRegistryǁincrement_counter__mutmut_14
    }
    
    def increment_counter(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsRegistryǁincrement_counter__mutmut_orig"), object.__getattribute__(self, "xǁMetricsRegistryǁincrement_counter__mutmut_mutants"), args, kwargs, self)
        return result 
    
    increment_counter.__signature__ = _mutmut_signature(xǁMetricsRegistryǁincrement_counter__mutmut_orig)
    xǁMetricsRegistryǁincrement_counter__mutmut_orig.__name__ = 'xǁMetricsRegistryǁincrement_counter'
    
    def xǁMetricsRegistryǁset_gauge__mutmut_orig(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁset_gauge__mutmut_1(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = None
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁset_gauge__mutmut_2(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(None, labels)
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁset_gauge__mutmut_3(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, None)
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁset_gauge__mutmut_4(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(labels)
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁset_gauge__mutmut_5(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, )
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁset_gauge__mutmut_6(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = None
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁset_gauge__mutmut_7(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value
            if labels:
                self._labels[key] = None
    
    xǁMetricsRegistryǁset_gauge__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsRegistryǁset_gauge__mutmut_1': xǁMetricsRegistryǁset_gauge__mutmut_1, 
        'xǁMetricsRegistryǁset_gauge__mutmut_2': xǁMetricsRegistryǁset_gauge__mutmut_2, 
        'xǁMetricsRegistryǁset_gauge__mutmut_3': xǁMetricsRegistryǁset_gauge__mutmut_3, 
        'xǁMetricsRegistryǁset_gauge__mutmut_4': xǁMetricsRegistryǁset_gauge__mutmut_4, 
        'xǁMetricsRegistryǁset_gauge__mutmut_5': xǁMetricsRegistryǁset_gauge__mutmut_5, 
        'xǁMetricsRegistryǁset_gauge__mutmut_6': xǁMetricsRegistryǁset_gauge__mutmut_6, 
        'xǁMetricsRegistryǁset_gauge__mutmut_7': xǁMetricsRegistryǁset_gauge__mutmut_7
    }
    
    def set_gauge(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsRegistryǁset_gauge__mutmut_orig"), object.__getattribute__(self, "xǁMetricsRegistryǁset_gauge__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_gauge.__signature__ = _mutmut_signature(xǁMetricsRegistryǁset_gauge__mutmut_orig)
    xǁMetricsRegistryǁset_gauge__mutmut_orig.__name__ = 'xǁMetricsRegistryǁset_gauge'
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_orig(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_1(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = None
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_2(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(None, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_3(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, None)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_4(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_5(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, )
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_6(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            if key in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_7(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = None
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_8(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(None)
            if labels:
                self._labels[key] = labels
    
    def xǁMetricsRegistryǁobserve_histogram__mutmut_9(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        """Record an observation for a histogram metric.
        
        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional metric labels.
        """
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            if labels:
                self._labels[key] = None
    
    xǁMetricsRegistryǁobserve_histogram__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsRegistryǁobserve_histogram__mutmut_1': xǁMetricsRegistryǁobserve_histogram__mutmut_1, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_2': xǁMetricsRegistryǁobserve_histogram__mutmut_2, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_3': xǁMetricsRegistryǁobserve_histogram__mutmut_3, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_4': xǁMetricsRegistryǁobserve_histogram__mutmut_4, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_5': xǁMetricsRegistryǁobserve_histogram__mutmut_5, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_6': xǁMetricsRegistryǁobserve_histogram__mutmut_6, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_7': xǁMetricsRegistryǁobserve_histogram__mutmut_7, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_8': xǁMetricsRegistryǁobserve_histogram__mutmut_8, 
        'xǁMetricsRegistryǁobserve_histogram__mutmut_9': xǁMetricsRegistryǁobserve_histogram__mutmut_9
    }
    
    def observe_histogram(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsRegistryǁobserve_histogram__mutmut_orig"), object.__getattribute__(self, "xǁMetricsRegistryǁobserve_histogram__mutmut_mutants"), args, kwargs, self)
        return result 
    
    observe_histogram.__signature__ = _mutmut_signature(xǁMetricsRegistryǁobserve_histogram__mutmut_orig)
    xǁMetricsRegistryǁobserve_histogram__mutmut_orig.__name__ = 'xǁMetricsRegistryǁobserve_histogram'
    
    def xǁMetricsRegistryǁ_make_key__mutmut_orig(
        self,
        name: str,
        labels: Optional[dict[str, str]] = None
    ) -> str:
        """Make a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def xǁMetricsRegistryǁ_make_key__mutmut_1(
        self,
        name: str,
        labels: Optional[dict[str, str]] = None
    ) -> str:
        """Make a unique key for a metric with labels."""
        if labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def xǁMetricsRegistryǁ_make_key__mutmut_2(
        self,
        name: str,
        labels: Optional[dict[str, str]] = None
    ) -> str:
        """Make a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = None
        return f"{name}{{{label_str}}}"
    
    def xǁMetricsRegistryǁ_make_key__mutmut_3(
        self,
        name: str,
        labels: Optional[dict[str, str]] = None
    ) -> str:
        """Make a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = ",".join(None)
        return f"{name}{{{label_str}}}"
    
    def xǁMetricsRegistryǁ_make_key__mutmut_4(
        self,
        name: str,
        labels: Optional[dict[str, str]] = None
    ) -> str:
        """Make a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = "XX,XX".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def xǁMetricsRegistryǁ_make_key__mutmut_5(
        self,
        name: str,
        labels: Optional[dict[str, str]] = None
    ) -> str:
        """Make a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(None))
        return f"{name}{{{label_str}}}"
    
    xǁMetricsRegistryǁ_make_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsRegistryǁ_make_key__mutmut_1': xǁMetricsRegistryǁ_make_key__mutmut_1, 
        'xǁMetricsRegistryǁ_make_key__mutmut_2': xǁMetricsRegistryǁ_make_key__mutmut_2, 
        'xǁMetricsRegistryǁ_make_key__mutmut_3': xǁMetricsRegistryǁ_make_key__mutmut_3, 
        'xǁMetricsRegistryǁ_make_key__mutmut_4': xǁMetricsRegistryǁ_make_key__mutmut_4, 
        'xǁMetricsRegistryǁ_make_key__mutmut_5': xǁMetricsRegistryǁ_make_key__mutmut_5
    }
    
    def _make_key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsRegistryǁ_make_key__mutmut_orig"), object.__getattribute__(self, "xǁMetricsRegistryǁ_make_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _make_key.__signature__ = _mutmut_signature(xǁMetricsRegistryǁ_make_key__mutmut_orig)
    xǁMetricsRegistryǁ_make_key__mutmut_orig.__name__ = 'xǁMetricsRegistryǁ_make_key'
    
    def xǁMetricsRegistryǁ_extract_metric_name__mutmut_orig(self, key: str) -> str:
        """Extract metric name from a key with labels.
        
        Args:
            key: Metric key that may contain labels in braces.
            
        Returns:
            The metric name without labels.
        """
        return key.split("{")[0]
    
    def xǁMetricsRegistryǁ_extract_metric_name__mutmut_1(self, key: str) -> str:
        """Extract metric name from a key with labels.
        
        Args:
            key: Metric key that may contain labels in braces.
            
        Returns:
            The metric name without labels.
        """
        return key.split(None)[0]
    
    def xǁMetricsRegistryǁ_extract_metric_name__mutmut_2(self, key: str) -> str:
        """Extract metric name from a key with labels.
        
        Args:
            key: Metric key that may contain labels in braces.
            
        Returns:
            The metric name without labels.
        """
        return key.split("XX{XX")[0]
    
    def xǁMetricsRegistryǁ_extract_metric_name__mutmut_3(self, key: str) -> str:
        """Extract metric name from a key with labels.
        
        Args:
            key: Metric key that may contain labels in braces.
            
        Returns:
            The metric name without labels.
        """
        return key.split("{")[1]
    
    xǁMetricsRegistryǁ_extract_metric_name__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsRegistryǁ_extract_metric_name__mutmut_1': xǁMetricsRegistryǁ_extract_metric_name__mutmut_1, 
        'xǁMetricsRegistryǁ_extract_metric_name__mutmut_2': xǁMetricsRegistryǁ_extract_metric_name__mutmut_2, 
        'xǁMetricsRegistryǁ_extract_metric_name__mutmut_3': xǁMetricsRegistryǁ_extract_metric_name__mutmut_3
    }
    
    def _extract_metric_name(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsRegistryǁ_extract_metric_name__mutmut_orig"), object.__getattribute__(self, "xǁMetricsRegistryǁ_extract_metric_name__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _extract_metric_name.__signature__ = _mutmut_signature(xǁMetricsRegistryǁ_extract_metric_name__mutmut_orig)
    xǁMetricsRegistryǁ_extract_metric_name__mutmut_orig.__name__ = 'xǁMetricsRegistryǁ_extract_metric_name'
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_orig(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_1(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = None
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_2(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = None
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_3(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(None)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_4(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = None
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_5(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(None, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_6(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, None)
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_7(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get({})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_8(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, )
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_9(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(None)
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_10(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=None,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_11(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=None,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_12(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=None,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_13(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type=None
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_14(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_15(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_16(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_17(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_18(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="XXcounterXX"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_19(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="COUNTER"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_20(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = None
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_21(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(None)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_22(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = None
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_23(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(None, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_24(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, None)
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_25(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get({})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_26(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, )
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_27(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(None)
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_28(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=None,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_29(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=None,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_30(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=None,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_31(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type=None
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_32(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_33(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_34(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_35(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_36(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="XXgaugeXX"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_37(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="GAUGE"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_38(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = None
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_39(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(None)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_40(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = None
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_41(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(None, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_42(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, None)
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_43(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get({})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_44(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, )
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_45(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(None)
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_46(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=None,
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_47(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=None,
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_48(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=None,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_49(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type=None
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_50(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_51(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_52(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_53(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_54(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(None),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_55(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="XXcounterXX"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_56(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="COUNTER"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_57(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(None)
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_58(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=None,
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_59(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=None,
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_60(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=None,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_61(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type=None
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_62(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        value=sum(values),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_63(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_64(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_65(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_66(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(None),
                        labels=labels,
                        metric_type="counter"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_67(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="XXcounterXX"
                    ))
        
        return metrics
    
    def xǁMetricsRegistryǁget_all_metrics__mutmut_68(self) -> list[MetricValue]:
        """Get all collected metrics.
        
        Returns:
            list of all metric values.
        """
        metrics: list[MetricValue] = []
        
        with self._lock:
            for key, value in self._counters.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="counter"
                ))
            
            for key, value in self._gauges.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                metrics.append(MetricValue(
                    name=name,
                    value=value,
                    labels=labels,
                    metric_type="gauge"
                ))
            
            for key, values in self._histograms.items():
                name = self._extract_metric_name(key)
                labels = self._labels.get(key, {})
                # Export histogram as multiple metrics
                if values:
                    metrics.append(MetricValue(
                        name=f"{name}_count",
                        value=float(len(values)),
                        labels=labels,
                        metric_type="counter"
                    ))
                    metrics.append(MetricValue(
                        name=f"{name}_sum",
                        value=sum(values),
                        labels=labels,
                        metric_type="COUNTER"
                    ))
        
        return metrics
    
    xǁMetricsRegistryǁget_all_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsRegistryǁget_all_metrics__mutmut_1': xǁMetricsRegistryǁget_all_metrics__mutmut_1, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_2': xǁMetricsRegistryǁget_all_metrics__mutmut_2, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_3': xǁMetricsRegistryǁget_all_metrics__mutmut_3, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_4': xǁMetricsRegistryǁget_all_metrics__mutmut_4, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_5': xǁMetricsRegistryǁget_all_metrics__mutmut_5, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_6': xǁMetricsRegistryǁget_all_metrics__mutmut_6, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_7': xǁMetricsRegistryǁget_all_metrics__mutmut_7, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_8': xǁMetricsRegistryǁget_all_metrics__mutmut_8, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_9': xǁMetricsRegistryǁget_all_metrics__mutmut_9, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_10': xǁMetricsRegistryǁget_all_metrics__mutmut_10, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_11': xǁMetricsRegistryǁget_all_metrics__mutmut_11, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_12': xǁMetricsRegistryǁget_all_metrics__mutmut_12, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_13': xǁMetricsRegistryǁget_all_metrics__mutmut_13, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_14': xǁMetricsRegistryǁget_all_metrics__mutmut_14, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_15': xǁMetricsRegistryǁget_all_metrics__mutmut_15, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_16': xǁMetricsRegistryǁget_all_metrics__mutmut_16, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_17': xǁMetricsRegistryǁget_all_metrics__mutmut_17, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_18': xǁMetricsRegistryǁget_all_metrics__mutmut_18, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_19': xǁMetricsRegistryǁget_all_metrics__mutmut_19, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_20': xǁMetricsRegistryǁget_all_metrics__mutmut_20, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_21': xǁMetricsRegistryǁget_all_metrics__mutmut_21, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_22': xǁMetricsRegistryǁget_all_metrics__mutmut_22, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_23': xǁMetricsRegistryǁget_all_metrics__mutmut_23, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_24': xǁMetricsRegistryǁget_all_metrics__mutmut_24, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_25': xǁMetricsRegistryǁget_all_metrics__mutmut_25, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_26': xǁMetricsRegistryǁget_all_metrics__mutmut_26, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_27': xǁMetricsRegistryǁget_all_metrics__mutmut_27, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_28': xǁMetricsRegistryǁget_all_metrics__mutmut_28, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_29': xǁMetricsRegistryǁget_all_metrics__mutmut_29, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_30': xǁMetricsRegistryǁget_all_metrics__mutmut_30, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_31': xǁMetricsRegistryǁget_all_metrics__mutmut_31, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_32': xǁMetricsRegistryǁget_all_metrics__mutmut_32, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_33': xǁMetricsRegistryǁget_all_metrics__mutmut_33, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_34': xǁMetricsRegistryǁget_all_metrics__mutmut_34, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_35': xǁMetricsRegistryǁget_all_metrics__mutmut_35, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_36': xǁMetricsRegistryǁget_all_metrics__mutmut_36, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_37': xǁMetricsRegistryǁget_all_metrics__mutmut_37, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_38': xǁMetricsRegistryǁget_all_metrics__mutmut_38, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_39': xǁMetricsRegistryǁget_all_metrics__mutmut_39, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_40': xǁMetricsRegistryǁget_all_metrics__mutmut_40, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_41': xǁMetricsRegistryǁget_all_metrics__mutmut_41, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_42': xǁMetricsRegistryǁget_all_metrics__mutmut_42, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_43': xǁMetricsRegistryǁget_all_metrics__mutmut_43, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_44': xǁMetricsRegistryǁget_all_metrics__mutmut_44, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_45': xǁMetricsRegistryǁget_all_metrics__mutmut_45, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_46': xǁMetricsRegistryǁget_all_metrics__mutmut_46, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_47': xǁMetricsRegistryǁget_all_metrics__mutmut_47, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_48': xǁMetricsRegistryǁget_all_metrics__mutmut_48, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_49': xǁMetricsRegistryǁget_all_metrics__mutmut_49, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_50': xǁMetricsRegistryǁget_all_metrics__mutmut_50, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_51': xǁMetricsRegistryǁget_all_metrics__mutmut_51, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_52': xǁMetricsRegistryǁget_all_metrics__mutmut_52, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_53': xǁMetricsRegistryǁget_all_metrics__mutmut_53, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_54': xǁMetricsRegistryǁget_all_metrics__mutmut_54, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_55': xǁMetricsRegistryǁget_all_metrics__mutmut_55, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_56': xǁMetricsRegistryǁget_all_metrics__mutmut_56, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_57': xǁMetricsRegistryǁget_all_metrics__mutmut_57, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_58': xǁMetricsRegistryǁget_all_metrics__mutmut_58, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_59': xǁMetricsRegistryǁget_all_metrics__mutmut_59, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_60': xǁMetricsRegistryǁget_all_metrics__mutmut_60, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_61': xǁMetricsRegistryǁget_all_metrics__mutmut_61, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_62': xǁMetricsRegistryǁget_all_metrics__mutmut_62, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_63': xǁMetricsRegistryǁget_all_metrics__mutmut_63, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_64': xǁMetricsRegistryǁget_all_metrics__mutmut_64, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_65': xǁMetricsRegistryǁget_all_metrics__mutmut_65, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_66': xǁMetricsRegistryǁget_all_metrics__mutmut_66, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_67': xǁMetricsRegistryǁget_all_metrics__mutmut_67, 
        'xǁMetricsRegistryǁget_all_metrics__mutmut_68': xǁMetricsRegistryǁget_all_metrics__mutmut_68
    }
    
    def get_all_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsRegistryǁget_all_metrics__mutmut_orig"), object.__getattribute__(self, "xǁMetricsRegistryǁget_all_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_all_metrics.__signature__ = _mutmut_signature(xǁMetricsRegistryǁget_all_metrics__mutmut_orig)
    xǁMetricsRegistryǁget_all_metrics__mutmut_orig.__name__ = 'xǁMetricsRegistryǁget_all_metrics'
    
    def reset(self) -> None:
        """Reset all metrics (for testing)."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._labels.clear()


class Tracer:
    """Simple tracer for request tracing."""
    
    def xǁTracerǁ__init____mutmut_orig(self) -> None:
        """Initialize the tracer."""
        self._spans: list[TraceSpan] = []
        self._lock = threading.Lock()
        self._span_counter = 0
        
    
    def xǁTracerǁ__init____mutmut_1(self) -> None:
        """Initialize the tracer."""
        self._spans: list[TraceSpan] = None
        self._lock = threading.Lock()
        self._span_counter = 0
        
    
    def xǁTracerǁ__init____mutmut_2(self) -> None:
        """Initialize the tracer."""
        self._spans: list[TraceSpan] = []
        self._lock = None
        self._span_counter = 0
        
    
    def xǁTracerǁ__init____mutmut_3(self) -> None:
        """Initialize the tracer."""
        self._spans: list[TraceSpan] = []
        self._lock = threading.Lock()
        self._span_counter = None
        
    
    def xǁTracerǁ__init____mutmut_4(self) -> None:
        """Initialize the tracer."""
        self._spans: list[TraceSpan] = []
        self._lock = threading.Lock()
        self._span_counter = 1
        
    
    xǁTracerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracerǁ__init____mutmut_1': xǁTracerǁ__init____mutmut_1, 
        'xǁTracerǁ__init____mutmut_2': xǁTracerǁ__init____mutmut_2, 
        'xǁTracerǁ__init____mutmut_3': xǁTracerǁ__init____mutmut_3, 
        'xǁTracerǁ__init____mutmut_4': xǁTracerǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTracerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTracerǁ__init____mutmut_orig)
    xǁTracerǁ__init____mutmut_orig.__name__ = 'xǁTracerǁ__init__'
    def xǁTracerǁ_generate_id__mutmut_orig(self) -> str:
        """Generate a unique ID."""
        with self._lock:
            self._span_counter += 1
            return f"span-{self._span_counter:08x}"
    def xǁTracerǁ_generate_id__mutmut_1(self) -> str:
        """Generate a unique ID."""
        with self._lock:
            self._span_counter = 1
            return f"span-{self._span_counter:08x}"
    def xǁTracerǁ_generate_id__mutmut_2(self) -> str:
        """Generate a unique ID."""
        with self._lock:
            self._span_counter -= 1
            return f"span-{self._span_counter:08x}"
    def xǁTracerǁ_generate_id__mutmut_3(self) -> str:
        """Generate a unique ID."""
        with self._lock:
            self._span_counter += 2
            return f"span-{self._span_counter:08x}"
    
    xǁTracerǁ_generate_id__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracerǁ_generate_id__mutmut_1': xǁTracerǁ_generate_id__mutmut_1, 
        'xǁTracerǁ_generate_id__mutmut_2': xǁTracerǁ_generate_id__mutmut_2, 
        'xǁTracerǁ_generate_id__mutmut_3': xǁTracerǁ_generate_id__mutmut_3
    }
    
    def _generate_id(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracerǁ_generate_id__mutmut_orig"), object.__getattribute__(self, "xǁTracerǁ_generate_id__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_id.__signature__ = _mutmut_signature(xǁTracerǁ_generate_id__mutmut_orig)
    xǁTracerǁ_generate_id__mutmut_orig.__name__ = 'xǁTracerǁ_generate_id'
    
    def xǁTracerǁstart_span__mutmut_orig(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_1(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = None
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_2(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=None,
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_3(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=None,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_4(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=None,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_5(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=None,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_6(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=None
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_7(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_8(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_9(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_10(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_11(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_12(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id and self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_13(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags and {}
        )
        
        with self._lock:
            self._spans.append(span)
        
        return span
    
    def xǁTracerǁstart_span__mutmut_14(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ) -> TraceSpan:
        """Start a new trace span.
        
        Args:
            operation_name: Name of the operation being traced.
            trace_id: Optional trace ID for correlation.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Returns:
            A new TraceSpan instance.
        """
        span = TraceSpan(
            trace_id=trace_id or self._generate_id(),
            span_id=self._generate_id(),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        with self._lock:
            self._spans.append(None)
        
        return span
    
    xǁTracerǁstart_span__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracerǁstart_span__mutmut_1': xǁTracerǁstart_span__mutmut_1, 
        'xǁTracerǁstart_span__mutmut_2': xǁTracerǁstart_span__mutmut_2, 
        'xǁTracerǁstart_span__mutmut_3': xǁTracerǁstart_span__mutmut_3, 
        'xǁTracerǁstart_span__mutmut_4': xǁTracerǁstart_span__mutmut_4, 
        'xǁTracerǁstart_span__mutmut_5': xǁTracerǁstart_span__mutmut_5, 
        'xǁTracerǁstart_span__mutmut_6': xǁTracerǁstart_span__mutmut_6, 
        'xǁTracerǁstart_span__mutmut_7': xǁTracerǁstart_span__mutmut_7, 
        'xǁTracerǁstart_span__mutmut_8': xǁTracerǁstart_span__mutmut_8, 
        'xǁTracerǁstart_span__mutmut_9': xǁTracerǁstart_span__mutmut_9, 
        'xǁTracerǁstart_span__mutmut_10': xǁTracerǁstart_span__mutmut_10, 
        'xǁTracerǁstart_span__mutmut_11': xǁTracerǁstart_span__mutmut_11, 
        'xǁTracerǁstart_span__mutmut_12': xǁTracerǁstart_span__mutmut_12, 
        'xǁTracerǁstart_span__mutmut_13': xǁTracerǁstart_span__mutmut_13, 
        'xǁTracerǁstart_span__mutmut_14': xǁTracerǁstart_span__mutmut_14
    }
    
    def start_span(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracerǁstart_span__mutmut_orig"), object.__getattribute__(self, "xǁTracerǁstart_span__mutmut_mutants"), args, kwargs, self)
        return result 
    
    start_span.__signature__ = _mutmut_signature(xǁTracerǁstart_span__mutmut_orig)
    xǁTracerǁstart_span__mutmut_orig.__name__ = 'xǁTracerǁstart_span'
    
    def xǁTracerǁfinish_span__mutmut_orig(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_1(self, span: TraceSpan, status: str = "XXokXX") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_2(self, span: TraceSpan, status: str = "OK") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_3(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = None
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_4(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = None
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_5(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            None,
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_6(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            None,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_7(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            None,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_8(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            None
        )
    
    def xǁTracerǁfinish_span__mutmut_9(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_10(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_11(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_12(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            )
    
    def xǁTracerǁfinish_span__mutmut_13(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "XXSpan completed: %s (duration: %.2fms, status: %s)XX",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_14(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_15(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "SPAN COMPLETED: %S (DURATION: %.2FMS, STATUS: %S)",
            span.operation_name,
            span.duration_ms or 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_16(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms and 0,
            span.status
        )
    
    def xǁTracerǁfinish_span__mutmut_17(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.
        
        Args:
            span: The span to finish.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status
        
        logger.debug(
            "Span completed: %s (duration: %.2fms, status: %s)",
            span.operation_name,
            span.duration_ms or 1,
            span.status
        )
    
    xǁTracerǁfinish_span__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracerǁfinish_span__mutmut_1': xǁTracerǁfinish_span__mutmut_1, 
        'xǁTracerǁfinish_span__mutmut_2': xǁTracerǁfinish_span__mutmut_2, 
        'xǁTracerǁfinish_span__mutmut_3': xǁTracerǁfinish_span__mutmut_3, 
        'xǁTracerǁfinish_span__mutmut_4': xǁTracerǁfinish_span__mutmut_4, 
        'xǁTracerǁfinish_span__mutmut_5': xǁTracerǁfinish_span__mutmut_5, 
        'xǁTracerǁfinish_span__mutmut_6': xǁTracerǁfinish_span__mutmut_6, 
        'xǁTracerǁfinish_span__mutmut_7': xǁTracerǁfinish_span__mutmut_7, 
        'xǁTracerǁfinish_span__mutmut_8': xǁTracerǁfinish_span__mutmut_8, 
        'xǁTracerǁfinish_span__mutmut_9': xǁTracerǁfinish_span__mutmut_9, 
        'xǁTracerǁfinish_span__mutmut_10': xǁTracerǁfinish_span__mutmut_10, 
        'xǁTracerǁfinish_span__mutmut_11': xǁTracerǁfinish_span__mutmut_11, 
        'xǁTracerǁfinish_span__mutmut_12': xǁTracerǁfinish_span__mutmut_12, 
        'xǁTracerǁfinish_span__mutmut_13': xǁTracerǁfinish_span__mutmut_13, 
        'xǁTracerǁfinish_span__mutmut_14': xǁTracerǁfinish_span__mutmut_14, 
        'xǁTracerǁfinish_span__mutmut_15': xǁTracerǁfinish_span__mutmut_15, 
        'xǁTracerǁfinish_span__mutmut_16': xǁTracerǁfinish_span__mutmut_16, 
        'xǁTracerǁfinish_span__mutmut_17': xǁTracerǁfinish_span__mutmut_17
    }
    
    def finish_span(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracerǁfinish_span__mutmut_orig"), object.__getattribute__(self, "xǁTracerǁfinish_span__mutmut_mutants"), args, kwargs, self)
        return result 
    
    finish_span.__signature__ = _mutmut_signature(xǁTracerǁfinish_span__mutmut_orig)
    xǁTracerǁfinish_span__mutmut_orig.__name__ = 'xǁTracerǁfinish_span'
    
    def xǁTracerǁadd_log__mutmut_orig(self, span: TraceSpan, event: str, **kwargs: Any) -> None:
        """Add a log event to a span.
        
        Args:
            span: The span to add the log to.
            event: Log event name.
            **kwargs: Additional log fields.
        """
        span.logs.append({
            "timestamp": time.time(),
            "event": event,
            **kwargs
        })
    
    def xǁTracerǁadd_log__mutmut_1(self, span: TraceSpan, event: str, **kwargs: Any) -> None:
        """Add a log event to a span.
        
        Args:
            span: The span to add the log to.
            event: Log event name.
            **kwargs: Additional log fields.
        """
        span.logs.append(None)
    
    def xǁTracerǁadd_log__mutmut_2(self, span: TraceSpan, event: str, **kwargs: Any) -> None:
        """Add a log event to a span.
        
        Args:
            span: The span to add the log to.
            event: Log event name.
            **kwargs: Additional log fields.
        """
        span.logs.append({
            "XXtimestampXX": time.time(),
            "event": event,
            **kwargs
        })
    
    def xǁTracerǁadd_log__mutmut_3(self, span: TraceSpan, event: str, **kwargs: Any) -> None:
        """Add a log event to a span.
        
        Args:
            span: The span to add the log to.
            event: Log event name.
            **kwargs: Additional log fields.
        """
        span.logs.append({
            "TIMESTAMP": time.time(),
            "event": event,
            **kwargs
        })
    
    def xǁTracerǁadd_log__mutmut_4(self, span: TraceSpan, event: str, **kwargs: Any) -> None:
        """Add a log event to a span.
        
        Args:
            span: The span to add the log to.
            event: Log event name.
            **kwargs: Additional log fields.
        """
        span.logs.append({
            "timestamp": time.time(),
            "XXeventXX": event,
            **kwargs
        })
    
    def xǁTracerǁadd_log__mutmut_5(self, span: TraceSpan, event: str, **kwargs: Any) -> None:
        """Add a log event to a span.
        
        Args:
            span: The span to add the log to.
            event: Log event name.
            **kwargs: Additional log fields.
        """
        span.logs.append({
            "timestamp": time.time(),
            "EVENT": event,
            **kwargs
        })
    
    xǁTracerǁadd_log__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracerǁadd_log__mutmut_1': xǁTracerǁadd_log__mutmut_1, 
        'xǁTracerǁadd_log__mutmut_2': xǁTracerǁadd_log__mutmut_2, 
        'xǁTracerǁadd_log__mutmut_3': xǁTracerǁadd_log__mutmut_3, 
        'xǁTracerǁadd_log__mutmut_4': xǁTracerǁadd_log__mutmut_4, 
        'xǁTracerǁadd_log__mutmut_5': xǁTracerǁadd_log__mutmut_5
    }
    
    def add_log(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracerǁadd_log__mutmut_orig"), object.__getattribute__(self, "xǁTracerǁadd_log__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_log.__signature__ = _mutmut_signature(xǁTracerǁadd_log__mutmut_orig)
    xǁTracerǁadd_log__mutmut_orig.__name__ = 'xǁTracerǁadd_log'
    
    @contextmanager
    def trace(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[dict[str, Any]] = None
    ):
        """Context manager for tracing an operation.
        
        Args:
            operation_name: Name of the operation.
            trace_id: Optional trace ID.
            parent_span_id: Optional parent span ID.
            tags: Optional span tags.
            
        Yields:
            The trace span.
        """
        span = self.start_span(
            operation_name,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            tags=tags
        )
        try:
            yield span
            self.finish_span(span, status="ok")
        except Exception as e:
            logger.debug(f"Exception: {e}")
            span.tags["error"] = True
            span.tags["error.message"] = str(e)
            self.finish_span(span, status="error")
            raise
    
    def xǁTracerǁget_spans__mutmut_orig(self, trace_id: Optional[str] = None) -> list[TraceSpan]:
        """Get collected spans.
        
        Args:
            trace_id: Optional filter by trace ID.
            
        Returns:
            list of trace spans.
        """
        with self._lock:
            if trace_id:
                return [s for s in self._spans if s.trace_id == trace_id]
            return list(self._spans)
    
    def xǁTracerǁget_spans__mutmut_1(self, trace_id: Optional[str] = None) -> list[TraceSpan]:
        """Get collected spans.
        
        Args:
            trace_id: Optional filter by trace ID.
            
        Returns:
            list of trace spans.
        """
        with self._lock:
            if trace_id:
                return [s for s in self._spans if s.trace_id != trace_id]
            return list(self._spans)
    
    def xǁTracerǁget_spans__mutmut_2(self, trace_id: Optional[str] = None) -> list[TraceSpan]:
        """Get collected spans.
        
        Args:
            trace_id: Optional filter by trace ID.
            
        Returns:
            list of trace spans.
        """
        with self._lock:
            if trace_id:
                return [s for s in self._spans if s.trace_id == trace_id]
            return list(None)
    
    xǁTracerǁget_spans__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTracerǁget_spans__mutmut_1': xǁTracerǁget_spans__mutmut_1, 
        'xǁTracerǁget_spans__mutmut_2': xǁTracerǁget_spans__mutmut_2
    }
    
    def get_spans(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTracerǁget_spans__mutmut_orig"), object.__getattribute__(self, "xǁTracerǁget_spans__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_spans.__signature__ = _mutmut_signature(xǁTracerǁget_spans__mutmut_orig)
    xǁTracerǁget_spans__mutmut_orig.__name__ = 'xǁTracerǁget_spans'
    
    def clear(self) -> None:
        """Clear all collected spans (for testing)."""
        with self._lock:
            self._spans.clear()


class MCPMetrics:
    """Pre-defined MCP metrics."""
    
    def xǁMCPMetricsǁ__init____mutmut_orig(self, registry: MetricsRegistry) -> None:
        """Initialize MCP metrics.
        
        Args:
            registry: Metrics registry to use.
        """
        self._registry = registry
    
    def xǁMCPMetricsǁ__init____mutmut_1(self, registry: MetricsRegistry) -> None:
        """Initialize MCP metrics.
        
        Args:
            registry: Metrics registry to use.
        """
        self._registry = None
    
    xǁMCPMetricsǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁ__init____mutmut_1': xǁMCPMetricsǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPMetricsǁ__init____mutmut_orig)
    xǁMCPMetricsǁ__init____mutmut_orig.__name__ = 'xǁMCPMetricsǁ__init__'
    
    def xǁMCPMetricsǁrecord_request__mutmut_orig(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_1(
        self,
        method: str,
        duration_ms: float,
        status: str = "XXsuccessXX"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_2(
        self,
        method: str,
        duration_ms: float,
        status: str = "SUCCESS"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_3(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = None
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_4(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"XXmethodXX": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_5(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"METHOD": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_6(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "XXstatusXX": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_7(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "STATUS": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_8(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter(None, labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_9(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=None)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_10(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter(labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_11(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", )
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_12(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("XXmcp_requests_totalXX", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_13(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("MCP_REQUESTS_TOTAL", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_14(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            None,
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_15(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            None,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_16(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels=None
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_17(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_18(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_19(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            )
    
    def xǁMCPMetricsǁrecord_request__mutmut_20(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "XXmcp_request_duration_msXX",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_21(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "MCP_REQUEST_DURATION_MS",
            duration_ms,
            labels={"method": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_22(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"XXmethodXX": method}
        )
    
    def xǁMCPMetricsǁrecord_request__mutmut_23(
        self,
        method: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record an MCP request.
        
        Args:
            method: RPC method name.
            duration_ms: Request duration in milliseconds.
            status: Request status.
        """
        labels = {"method": method, "status": status}
        self._registry.increment_counter("mcp_requests_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_request_duration_ms",
            duration_ms,
            labels={"METHOD": method}
        )
    
    xǁMCPMetricsǁrecord_request__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁrecord_request__mutmut_1': xǁMCPMetricsǁrecord_request__mutmut_1, 
        'xǁMCPMetricsǁrecord_request__mutmut_2': xǁMCPMetricsǁrecord_request__mutmut_2, 
        'xǁMCPMetricsǁrecord_request__mutmut_3': xǁMCPMetricsǁrecord_request__mutmut_3, 
        'xǁMCPMetricsǁrecord_request__mutmut_4': xǁMCPMetricsǁrecord_request__mutmut_4, 
        'xǁMCPMetricsǁrecord_request__mutmut_5': xǁMCPMetricsǁrecord_request__mutmut_5, 
        'xǁMCPMetricsǁrecord_request__mutmut_6': xǁMCPMetricsǁrecord_request__mutmut_6, 
        'xǁMCPMetricsǁrecord_request__mutmut_7': xǁMCPMetricsǁrecord_request__mutmut_7, 
        'xǁMCPMetricsǁrecord_request__mutmut_8': xǁMCPMetricsǁrecord_request__mutmut_8, 
        'xǁMCPMetricsǁrecord_request__mutmut_9': xǁMCPMetricsǁrecord_request__mutmut_9, 
        'xǁMCPMetricsǁrecord_request__mutmut_10': xǁMCPMetricsǁrecord_request__mutmut_10, 
        'xǁMCPMetricsǁrecord_request__mutmut_11': xǁMCPMetricsǁrecord_request__mutmut_11, 
        'xǁMCPMetricsǁrecord_request__mutmut_12': xǁMCPMetricsǁrecord_request__mutmut_12, 
        'xǁMCPMetricsǁrecord_request__mutmut_13': xǁMCPMetricsǁrecord_request__mutmut_13, 
        'xǁMCPMetricsǁrecord_request__mutmut_14': xǁMCPMetricsǁrecord_request__mutmut_14, 
        'xǁMCPMetricsǁrecord_request__mutmut_15': xǁMCPMetricsǁrecord_request__mutmut_15, 
        'xǁMCPMetricsǁrecord_request__mutmut_16': xǁMCPMetricsǁrecord_request__mutmut_16, 
        'xǁMCPMetricsǁrecord_request__mutmut_17': xǁMCPMetricsǁrecord_request__mutmut_17, 
        'xǁMCPMetricsǁrecord_request__mutmut_18': xǁMCPMetricsǁrecord_request__mutmut_18, 
        'xǁMCPMetricsǁrecord_request__mutmut_19': xǁMCPMetricsǁrecord_request__mutmut_19, 
        'xǁMCPMetricsǁrecord_request__mutmut_20': xǁMCPMetricsǁrecord_request__mutmut_20, 
        'xǁMCPMetricsǁrecord_request__mutmut_21': xǁMCPMetricsǁrecord_request__mutmut_21, 
        'xǁMCPMetricsǁrecord_request__mutmut_22': xǁMCPMetricsǁrecord_request__mutmut_22, 
        'xǁMCPMetricsǁrecord_request__mutmut_23': xǁMCPMetricsǁrecord_request__mutmut_23
    }
    
    def record_request(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁrecord_request__mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁrecord_request__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_request.__signature__ = _mutmut_signature(xǁMCPMetricsǁrecord_request__mutmut_orig)
    xǁMCPMetricsǁrecord_request__mutmut_orig.__name__ = 'xǁMCPMetricsǁrecord_request'
    
    def xǁMCPMetricsǁrecord_error__mutmut_orig(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total",
            labels={"method": method, "error_type": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_1(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            None,
            labels={"method": method, "error_type": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_2(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total",
            labels=None
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_3(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            labels={"method": method, "error_type": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_4(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total",
            )
    
    def xǁMCPMetricsǁrecord_error__mutmut_5(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "XXmcp_errors_totalXX",
            labels={"method": method, "error_type": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_6(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "MCP_ERRORS_TOTAL",
            labels={"method": method, "error_type": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_7(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total",
            labels={"XXmethodXX": method, "error_type": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_8(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total",
            labels={"METHOD": method, "error_type": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_9(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total",
            labels={"method": method, "XXerror_typeXX": error_type}
        )
    
    def xǁMCPMetricsǁrecord_error__mutmut_10(self, method: str, error_type: str) -> None:
        """Record an MCP error.
        
        Args:
            method: RPC method name.
            error_type: Type of error.
        """
        self._registry.increment_counter(
            "mcp_errors_total",
            labels={"method": method, "ERROR_TYPE": error_type}
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
    
    def xǁMCPMetricsǁset_active_connections__mutmut_orig(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge("mcp_active_connections", float(count))
    
    def xǁMCPMetricsǁset_active_connections__mutmut_1(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge(None, float(count))
    
    def xǁMCPMetricsǁset_active_connections__mutmut_2(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge("mcp_active_connections", None)
    
    def xǁMCPMetricsǁset_active_connections__mutmut_3(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge(float(count))
    
    def xǁMCPMetricsǁset_active_connections__mutmut_4(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge("mcp_active_connections", )
    
    def xǁMCPMetricsǁset_active_connections__mutmut_5(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge("XXmcp_active_connectionsXX", float(count))
    
    def xǁMCPMetricsǁset_active_connections__mutmut_6(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge("MCP_ACTIVE_CONNECTIONS", float(count))
    
    def xǁMCPMetricsǁset_active_connections__mutmut_7(self, count: int) -> None:
        """set the number of active connections.
        
        Args:
            count: Number of active connections.
        """
        self._registry.set_gauge("mcp_active_connections", float(None))
    
    xǁMCPMetricsǁset_active_connections__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁset_active_connections__mutmut_1': xǁMCPMetricsǁset_active_connections__mutmut_1, 
        'xǁMCPMetricsǁset_active_connections__mutmut_2': xǁMCPMetricsǁset_active_connections__mutmut_2, 
        'xǁMCPMetricsǁset_active_connections__mutmut_3': xǁMCPMetricsǁset_active_connections__mutmut_3, 
        'xǁMCPMetricsǁset_active_connections__mutmut_4': xǁMCPMetricsǁset_active_connections__mutmut_4, 
        'xǁMCPMetricsǁset_active_connections__mutmut_5': xǁMCPMetricsǁset_active_connections__mutmut_5, 
        'xǁMCPMetricsǁset_active_connections__mutmut_6': xǁMCPMetricsǁset_active_connections__mutmut_6, 
        'xǁMCPMetricsǁset_active_connections__mutmut_7': xǁMCPMetricsǁset_active_connections__mutmut_7
    }
    
    def set_active_connections(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁset_active_connections__mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁset_active_connections__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_active_connections.__signature__ = _mutmut_signature(xǁMCPMetricsǁset_active_connections__mutmut_orig)
    xǁMCPMetricsǁset_active_connections__mutmut_orig.__name__ = 'xǁMCPMetricsǁset_active_connections'
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_orig(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_1(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "XXsuccessXX"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_2(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "SUCCESS"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_3(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = None
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_4(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"XXtoolXX": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_5(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"TOOL": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_6(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "XXstatusXX": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_7(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "STATUS": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_8(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter(None, labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_9(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=None)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_10(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter(labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_11(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", )
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_12(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("XXmcp_tool_invocations_totalXX", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_13(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("MCP_TOOL_INVOCATIONS_TOTAL", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_14(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            None,
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_15(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            None,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_16(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels=None
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_17(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_18(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_19(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_20(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "XXmcp_tool_duration_msXX",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_21(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "MCP_TOOL_DURATION_MS",
            duration_ms,
            labels={"tool": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_22(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"XXtoolXX": tool_name}
        )
    
    def xǁMCPMetricsǁrecord_tool_invocation__mutmut_23(
        self,
        tool_name: str,
        duration_ms: float,
        status: str = "success"
    ) -> None:
        """Record a tool invocation.
        
        Args:
            tool_name: Name of the tool.
            duration_ms: Invocation duration in milliseconds.
            status: Invocation status.
        """
        labels = {"tool": tool_name, "status": status}
        self._registry.increment_counter("mcp_tool_invocations_total", labels=labels)
        self._registry.observe_histogram(
            "mcp_tool_duration_ms",
            duration_ms,
            labels={"TOOL": tool_name}
        )
    
    xǁMCPMetricsǁrecord_tool_invocation__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPMetricsǁrecord_tool_invocation__mutmut_1': xǁMCPMetricsǁrecord_tool_invocation__mutmut_1, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_2': xǁMCPMetricsǁrecord_tool_invocation__mutmut_2, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_3': xǁMCPMetricsǁrecord_tool_invocation__mutmut_3, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_4': xǁMCPMetricsǁrecord_tool_invocation__mutmut_4, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_5': xǁMCPMetricsǁrecord_tool_invocation__mutmut_5, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_6': xǁMCPMetricsǁrecord_tool_invocation__mutmut_6, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_7': xǁMCPMetricsǁrecord_tool_invocation__mutmut_7, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_8': xǁMCPMetricsǁrecord_tool_invocation__mutmut_8, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_9': xǁMCPMetricsǁrecord_tool_invocation__mutmut_9, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_10': xǁMCPMetricsǁrecord_tool_invocation__mutmut_10, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_11': xǁMCPMetricsǁrecord_tool_invocation__mutmut_11, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_12': xǁMCPMetricsǁrecord_tool_invocation__mutmut_12, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_13': xǁMCPMetricsǁrecord_tool_invocation__mutmut_13, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_14': xǁMCPMetricsǁrecord_tool_invocation__mutmut_14, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_15': xǁMCPMetricsǁrecord_tool_invocation__mutmut_15, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_16': xǁMCPMetricsǁrecord_tool_invocation__mutmut_16, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_17': xǁMCPMetricsǁrecord_tool_invocation__mutmut_17, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_18': xǁMCPMetricsǁrecord_tool_invocation__mutmut_18, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_19': xǁMCPMetricsǁrecord_tool_invocation__mutmut_19, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_20': xǁMCPMetricsǁrecord_tool_invocation__mutmut_20, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_21': xǁMCPMetricsǁrecord_tool_invocation__mutmut_21, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_22': xǁMCPMetricsǁrecord_tool_invocation__mutmut_22, 
        'xǁMCPMetricsǁrecord_tool_invocation__mutmut_23': xǁMCPMetricsǁrecord_tool_invocation__mutmut_23
    }
    
    def record_tool_invocation(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPMetricsǁrecord_tool_invocation__mutmut_orig"), object.__getattribute__(self, "xǁMCPMetricsǁrecord_tool_invocation__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_tool_invocation.__signature__ = _mutmut_signature(xǁMCPMetricsǁrecord_tool_invocation__mutmut_orig)
    xǁMCPMetricsǁrecord_tool_invocation__mutmut_orig.__name__ = 'xǁMCPMetricsǁrecord_tool_invocation'


def x_traced__mutmut_orig(operation_name: Optional[str] = None):
    """Decorator for tracing function execution.
    
    Args:
        operation_name: Optional operation name. Uses function name if not provided.
        
    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return await func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


def x_traced__mutmut_1(operation_name: Optional[str] = None):
    """Decorator for tracing function execution.
    
    Args:
        operation_name: Optional operation name. Uses function name if not provided.
        
    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        op_name = None
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return await func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


def x_traced__mutmut_2(operation_name: Optional[str] = None):
    """Decorator for tracing function execution.
    
    Args:
        operation_name: Optional operation name. Uses function name if not provided.
        
    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name and func.__name__
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return await func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


def x_traced__mutmut_3(operation_name: Optional[str] = None):
    """Decorator for tracing function execution.
    
    Args:
        operation_name: Optional operation name. Uses function name if not provided.
        
    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with get_tracer().trace(op_name):
                return await func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(None):
            return async_wrapper
        return wrapper
    
    return decorator

x_traced__mutmut_mutants : ClassVar[MutantDict] = {
'x_traced__mutmut_1': x_traced__mutmut_1, 
    'x_traced__mutmut_2': x_traced__mutmut_2, 
    'x_traced__mutmut_3': x_traced__mutmut_3
}

def traced(*args, **kwargs):
    result = _mutmut_trampoline(x_traced__mutmut_orig, x_traced__mutmut_mutants, args, kwargs)
    return result 

traced.__signature__ = _mutmut_signature(x_traced__mutmut_orig)
x_traced__mutmut_orig.__name__ = 'x_traced'


# Global instances
_metrics_registry: Optional[MetricsRegistry] = None
_tracer: Optional[Tracer] = None
_mcp_metrics: Optional[MCPMetrics] = None


def x_get_metrics_registry__mutmut_orig() -> MetricsRegistry:
    """Get or create the global metrics registry."""
    global _metrics_registry
    if _metrics_registry is None:
        _metrics_registry = MetricsRegistry()
    return _metrics_registry


def x_get_metrics_registry__mutmut_1() -> MetricsRegistry:
    """Get or create the global metrics registry."""
    global _metrics_registry
    if _metrics_registry is not None:
        _metrics_registry = MetricsRegistry()
    return _metrics_registry


def x_get_metrics_registry__mutmut_2() -> MetricsRegistry:
    """Get or create the global metrics registry."""
    global _metrics_registry
    if _metrics_registry is None:
        _metrics_registry = None
    return _metrics_registry

x_get_metrics_registry__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_metrics_registry__mutmut_1': x_get_metrics_registry__mutmut_1, 
    'x_get_metrics_registry__mutmut_2': x_get_metrics_registry__mutmut_2
}

def get_metrics_registry(*args, **kwargs):
    result = _mutmut_trampoline(x_get_metrics_registry__mutmut_orig, x_get_metrics_registry__mutmut_mutants, args, kwargs)
    return result 

get_metrics_registry.__signature__ = _mutmut_signature(x_get_metrics_registry__mutmut_orig)
x_get_metrics_registry__mutmut_orig.__name__ = 'x_get_metrics_registry'


def x_get_tracer__mutmut_orig() -> Tracer:
    """Get or create the global tracer."""
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer


def x_get_tracer__mutmut_1() -> Tracer:
    """Get or create the global tracer."""
    global _tracer
    if _tracer is not None:
        _tracer = Tracer()
    return _tracer


def x_get_tracer__mutmut_2() -> Tracer:
    """Get or create the global tracer."""
    global _tracer
    if _tracer is None:
        _tracer = None
    return _tracer

x_get_tracer__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_tracer__mutmut_1': x_get_tracer__mutmut_1, 
    'x_get_tracer__mutmut_2': x_get_tracer__mutmut_2
}

def get_tracer(*args, **kwargs):
    result = _mutmut_trampoline(x_get_tracer__mutmut_orig, x_get_tracer__mutmut_mutants, args, kwargs)
    return result 

get_tracer.__signature__ = _mutmut_signature(x_get_tracer__mutmut_orig)
x_get_tracer__mutmut_orig.__name__ = 'x_get_tracer'


def x_get_mcp_metrics__mutmut_orig() -> MCPMetrics:
    """Get or create the global MCP metrics."""
    global _mcp_metrics
    if _mcp_metrics is None:
        _mcp_metrics = MCPMetrics(get_metrics_registry())
    return _mcp_metrics


def x_get_mcp_metrics__mutmut_1() -> MCPMetrics:
    """Get or create the global MCP metrics."""
    global _mcp_metrics
    if _mcp_metrics is not None:
        _mcp_metrics = MCPMetrics(get_metrics_registry())
    return _mcp_metrics


def x_get_mcp_metrics__mutmut_2() -> MCPMetrics:
    """Get or create the global MCP metrics."""
    global _mcp_metrics
    if _mcp_metrics is None:
        _mcp_metrics = None
    return _mcp_metrics


def x_get_mcp_metrics__mutmut_3() -> MCPMetrics:
    """Get or create the global MCP metrics."""
    global _mcp_metrics
    if _mcp_metrics is None:
        _mcp_metrics = MCPMetrics(None)
    return _mcp_metrics

x_get_mcp_metrics__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_mcp_metrics__mutmut_1': x_get_mcp_metrics__mutmut_1, 
    'x_get_mcp_metrics__mutmut_2': x_get_mcp_metrics__mutmut_2, 
    'x_get_mcp_metrics__mutmut_3': x_get_mcp_metrics__mutmut_3
}

def get_mcp_metrics(*args, **kwargs):
    result = _mutmut_trampoline(x_get_mcp_metrics__mutmut_orig, x_get_mcp_metrics__mutmut_mutants, args, kwargs)
    return result 

get_mcp_metrics.__signature__ = _mutmut_signature(x_get_mcp_metrics__mutmut_orig)
x_get_mcp_metrics__mutmut_orig.__name__ = 'x_get_mcp_metrics'


def x_reset_observability__mutmut_orig() -> None:
    """Reset all observability state (for testing)."""
    global _metrics_registry, _tracer, _mcp_metrics
    if _metrics_registry:
        _metrics_registry.reset()
    if _tracer:
        _tracer.clear()
    _mcp_metrics = None


def x_reset_observability__mutmut_1() -> None:
    """Reset all observability state (for testing)."""
    global _metrics_registry, _tracer, _mcp_metrics
    if _metrics_registry:
        _metrics_registry.reset()
    if _tracer:
        _tracer.clear()
    _mcp_metrics = ""

x_reset_observability__mutmut_mutants : ClassVar[MutantDict] = {
'x_reset_observability__mutmut_1': x_reset_observability__mutmut_1
}

def reset_observability(*args, **kwargs):
    result = _mutmut_trampoline(x_reset_observability__mutmut_orig, x_reset_observability__mutmut_mutants, args, kwargs)
    return result 

reset_observability.__signature__ = _mutmut_signature(x_reset_observability__mutmut_orig)
x_reset_observability__mutmut_orig.__name__ = 'x_reset_observability'
