"""Code metrics aggregation and analysis."""

import statistics
from dataclasses import dataclass
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
class CodeMetrics:
    """Aggregated code quality metrics for a code entity."""

    cyclomatic_complexity: int
    cognitive_complexity: float
    lines_of_code: int
    comment_lines: int
    maintainability_index: float

    @property
    def quality_tier(self) -> str:
        """Compute quality grade (A-F) from maintainability index."""
        if self.maintainability_index >= 85:
            return "A"
        elif self.maintainability_index >= 70:
            return "B"
        elif self.maintainability_index >= 55:
            return "C"
        elif self.maintainability_index >= 40:
            return "D"
        else:
            return "F"

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "cognitive_complexity": self.cognitive_complexity,
            "lines_of_code": self.lines_of_code,
            "comment_lines": self.comment_lines,
            "maintainability_index": self.maintainability_index,
            "quality_tier": self.quality_tier,
        }


class MetricsAggregator:
    """Aggregate and correlate metrics from multiple sources."""

    def xǁMetricsAggregatorǁ__init____mutmut_orig(self):
        self.metrics: dict[str, CodeMetrics] = {}

    def xǁMetricsAggregatorǁ__init____mutmut_1(self):
        self.metrics: dict[str, CodeMetrics] = None
    
    xǁMetricsAggregatorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsAggregatorǁ__init____mutmut_1': xǁMetricsAggregatorǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsAggregatorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMetricsAggregatorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMetricsAggregatorǁ__init____mutmut_orig)
    xǁMetricsAggregatorǁ__init____mutmut_orig.__name__ = 'xǁMetricsAggregatorǁ__init__'

    def xǁMetricsAggregatorǁstore_metrics__mutmut_orig(self, entity_id: str, metrics: CodeMetrics) -> None:
        """Store metrics for an entity."""
        self.metrics[entity_id] = metrics

    def xǁMetricsAggregatorǁstore_metrics__mutmut_1(self, entity_id: str, metrics: CodeMetrics) -> None:
        """Store metrics for an entity."""
        self.metrics[entity_id] = None
    
    xǁMetricsAggregatorǁstore_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsAggregatorǁstore_metrics__mutmut_1': xǁMetricsAggregatorǁstore_metrics__mutmut_1
    }
    
    def store_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsAggregatorǁstore_metrics__mutmut_orig"), object.__getattribute__(self, "xǁMetricsAggregatorǁstore_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    store_metrics.__signature__ = _mutmut_signature(xǁMetricsAggregatorǁstore_metrics__mutmut_orig)
    xǁMetricsAggregatorǁstore_metrics__mutmut_orig.__name__ = 'xǁMetricsAggregatorǁstore_metrics'

    def xǁMetricsAggregatorǁaggregate__mutmut_orig(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_1(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_2(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(None, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_3(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, None, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_4(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, None, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_5(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, None, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_6(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, None)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_7(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_8(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_9(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_10(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_11(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, )

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_12(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(1, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_13(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 1.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_14(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 1, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_15(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 1, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_16(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 101.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_17(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=None,
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_18(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=None,
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_19(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=None,
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_20(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=None,
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_21(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=None,
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_22(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_23(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_24(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_25(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_26(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            )

    def xǁMetricsAggregatorǁaggregate__mutmut_27(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(None),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_28(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(None),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_29(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(None),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_30(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(None),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def xǁMetricsAggregatorǁaggregate__mutmut_31(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(None),
        )
    
    xǁMetricsAggregatorǁaggregate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsAggregatorǁaggregate__mutmut_1': xǁMetricsAggregatorǁaggregate__mutmut_1, 
        'xǁMetricsAggregatorǁaggregate__mutmut_2': xǁMetricsAggregatorǁaggregate__mutmut_2, 
        'xǁMetricsAggregatorǁaggregate__mutmut_3': xǁMetricsAggregatorǁaggregate__mutmut_3, 
        'xǁMetricsAggregatorǁaggregate__mutmut_4': xǁMetricsAggregatorǁaggregate__mutmut_4, 
        'xǁMetricsAggregatorǁaggregate__mutmut_5': xǁMetricsAggregatorǁaggregate__mutmut_5, 
        'xǁMetricsAggregatorǁaggregate__mutmut_6': xǁMetricsAggregatorǁaggregate__mutmut_6, 
        'xǁMetricsAggregatorǁaggregate__mutmut_7': xǁMetricsAggregatorǁaggregate__mutmut_7, 
        'xǁMetricsAggregatorǁaggregate__mutmut_8': xǁMetricsAggregatorǁaggregate__mutmut_8, 
        'xǁMetricsAggregatorǁaggregate__mutmut_9': xǁMetricsAggregatorǁaggregate__mutmut_9, 
        'xǁMetricsAggregatorǁaggregate__mutmut_10': xǁMetricsAggregatorǁaggregate__mutmut_10, 
        'xǁMetricsAggregatorǁaggregate__mutmut_11': xǁMetricsAggregatorǁaggregate__mutmut_11, 
        'xǁMetricsAggregatorǁaggregate__mutmut_12': xǁMetricsAggregatorǁaggregate__mutmut_12, 
        'xǁMetricsAggregatorǁaggregate__mutmut_13': xǁMetricsAggregatorǁaggregate__mutmut_13, 
        'xǁMetricsAggregatorǁaggregate__mutmut_14': xǁMetricsAggregatorǁaggregate__mutmut_14, 
        'xǁMetricsAggregatorǁaggregate__mutmut_15': xǁMetricsAggregatorǁaggregate__mutmut_15, 
        'xǁMetricsAggregatorǁaggregate__mutmut_16': xǁMetricsAggregatorǁaggregate__mutmut_16, 
        'xǁMetricsAggregatorǁaggregate__mutmut_17': xǁMetricsAggregatorǁaggregate__mutmut_17, 
        'xǁMetricsAggregatorǁaggregate__mutmut_18': xǁMetricsAggregatorǁaggregate__mutmut_18, 
        'xǁMetricsAggregatorǁaggregate__mutmut_19': xǁMetricsAggregatorǁaggregate__mutmut_19, 
        'xǁMetricsAggregatorǁaggregate__mutmut_20': xǁMetricsAggregatorǁaggregate__mutmut_20, 
        'xǁMetricsAggregatorǁaggregate__mutmut_21': xǁMetricsAggregatorǁaggregate__mutmut_21, 
        'xǁMetricsAggregatorǁaggregate__mutmut_22': xǁMetricsAggregatorǁaggregate__mutmut_22, 
        'xǁMetricsAggregatorǁaggregate__mutmut_23': xǁMetricsAggregatorǁaggregate__mutmut_23, 
        'xǁMetricsAggregatorǁaggregate__mutmut_24': xǁMetricsAggregatorǁaggregate__mutmut_24, 
        'xǁMetricsAggregatorǁaggregate__mutmut_25': xǁMetricsAggregatorǁaggregate__mutmut_25, 
        'xǁMetricsAggregatorǁaggregate__mutmut_26': xǁMetricsAggregatorǁaggregate__mutmut_26, 
        'xǁMetricsAggregatorǁaggregate__mutmut_27': xǁMetricsAggregatorǁaggregate__mutmut_27, 
        'xǁMetricsAggregatorǁaggregate__mutmut_28': xǁMetricsAggregatorǁaggregate__mutmut_28, 
        'xǁMetricsAggregatorǁaggregate__mutmut_29': xǁMetricsAggregatorǁaggregate__mutmut_29, 
        'xǁMetricsAggregatorǁaggregate__mutmut_30': xǁMetricsAggregatorǁaggregate__mutmut_30, 
        'xǁMetricsAggregatorǁaggregate__mutmut_31': xǁMetricsAggregatorǁaggregate__mutmut_31
    }
    
    def aggregate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsAggregatorǁaggregate__mutmut_orig"), object.__getattribute__(self, "xǁMetricsAggregatorǁaggregate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    aggregate.__signature__ = _mutmut_signature(xǁMetricsAggregatorǁaggregate__mutmut_orig)
    xǁMetricsAggregatorǁaggregate__mutmut_orig.__name__ = 'xǁMetricsAggregatorǁaggregate'

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_orig(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_1(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 and len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_2(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) <= 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_3(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 3 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_4(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) <= 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_5(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 3:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_6(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                None
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_7(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) == len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_8(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                None
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_9(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = None
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_10(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(None)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_11(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = None

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_12(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(None)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_13(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = None

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_14(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            None
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_15(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) / (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_16(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c + mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_17(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v + mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_18(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(None, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_19(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, None)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_20(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_21(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, )
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_22(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = None
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_23(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) * 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_24(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum(None)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_25(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) * 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_26(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c + mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_27(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 3 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_28(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 1.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_29(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = None

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_30(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) * 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_31(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum(None)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_32(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) * 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_33(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c + mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_34(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 3 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_35(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 1.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_36(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc / denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_37(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov != 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_38(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 1:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_39(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 1.0

        return numerator / (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_40(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator * (denom_cc * denom_cov)

    def xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_41(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov) for c, v in zip(complexity_metrics, coverage_metrics)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc / denom_cov)
    
    xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_1': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_1, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_2': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_2, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_3': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_3, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_4': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_4, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_5': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_5, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_6': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_6, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_7': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_7, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_8': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_8, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_9': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_9, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_10': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_10, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_11': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_11, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_12': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_12, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_13': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_13, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_14': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_14, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_15': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_15, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_16': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_16, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_17': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_17, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_18': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_18, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_19': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_19, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_20': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_20, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_21': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_21, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_22': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_22, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_23': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_23, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_24': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_24, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_25': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_25, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_26': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_26, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_27': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_27, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_28': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_28, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_29': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_29, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_30': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_30, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_31': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_31, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_32': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_32, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_33': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_33, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_34': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_34, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_35': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_35, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_36': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_36, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_37': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_37, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_38': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_38, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_39': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_39, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_40': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_40, 
        'xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_41': xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_41
    }
    
    def correlate_complexity_coverage(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_orig"), object.__getattribute__(self, "xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_mutants"), args, kwargs, self)
        return result 
    
    correlate_complexity_coverage.__signature__ = _mutmut_signature(xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_orig)
    xǁMetricsAggregatorǁcorrelate_complexity_coverage__mutmut_orig.__name__ = 'xǁMetricsAggregatorǁcorrelate_complexity_coverage'

    def xǁMetricsAggregatorǁsummary__mutmut_orig(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_1(self) -> dict:
        """Get summary statistics of all metrics."""
        if self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_2(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = None
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_3(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = None
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_4(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = None

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_5(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "XXtotal_entitiesXX": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_6(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "TOTAL_ENTITIES": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_7(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "XXtotal_lines_of_codeXX": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_8(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "TOTAL_LINES_OF_CODE": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_9(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(None),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_10(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "XXaverage_cyclomatic_complexityXX": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_11(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "AVERAGE_CYCLOMATIC_COMPLEXITY": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_12(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(None),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_13(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "XXmax_cyclomatic_complexityXX": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_14(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "MAX_CYCLOMATIC_COMPLEXITY": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_15(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(None),
            "average_maintainability_index": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_16(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "XXaverage_maintainability_indexXX": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_17(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "AVERAGE_MAINTAINABILITY_INDEX": statistics.mean(mis),
        }

    def xǁMetricsAggregatorǁsummary__mutmut_18(self) -> dict:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(None),
        }
    
    xǁMetricsAggregatorǁsummary__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricsAggregatorǁsummary__mutmut_1': xǁMetricsAggregatorǁsummary__mutmut_1, 
        'xǁMetricsAggregatorǁsummary__mutmut_2': xǁMetricsAggregatorǁsummary__mutmut_2, 
        'xǁMetricsAggregatorǁsummary__mutmut_3': xǁMetricsAggregatorǁsummary__mutmut_3, 
        'xǁMetricsAggregatorǁsummary__mutmut_4': xǁMetricsAggregatorǁsummary__mutmut_4, 
        'xǁMetricsAggregatorǁsummary__mutmut_5': xǁMetricsAggregatorǁsummary__mutmut_5, 
        'xǁMetricsAggregatorǁsummary__mutmut_6': xǁMetricsAggregatorǁsummary__mutmut_6, 
        'xǁMetricsAggregatorǁsummary__mutmut_7': xǁMetricsAggregatorǁsummary__mutmut_7, 
        'xǁMetricsAggregatorǁsummary__mutmut_8': xǁMetricsAggregatorǁsummary__mutmut_8, 
        'xǁMetricsAggregatorǁsummary__mutmut_9': xǁMetricsAggregatorǁsummary__mutmut_9, 
        'xǁMetricsAggregatorǁsummary__mutmut_10': xǁMetricsAggregatorǁsummary__mutmut_10, 
        'xǁMetricsAggregatorǁsummary__mutmut_11': xǁMetricsAggregatorǁsummary__mutmut_11, 
        'xǁMetricsAggregatorǁsummary__mutmut_12': xǁMetricsAggregatorǁsummary__mutmut_12, 
        'xǁMetricsAggregatorǁsummary__mutmut_13': xǁMetricsAggregatorǁsummary__mutmut_13, 
        'xǁMetricsAggregatorǁsummary__mutmut_14': xǁMetricsAggregatorǁsummary__mutmut_14, 
        'xǁMetricsAggregatorǁsummary__mutmut_15': xǁMetricsAggregatorǁsummary__mutmut_15, 
        'xǁMetricsAggregatorǁsummary__mutmut_16': xǁMetricsAggregatorǁsummary__mutmut_16, 
        'xǁMetricsAggregatorǁsummary__mutmut_17': xǁMetricsAggregatorǁsummary__mutmut_17, 
        'xǁMetricsAggregatorǁsummary__mutmut_18': xǁMetricsAggregatorǁsummary__mutmut_18
    }
    
    def summary(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricsAggregatorǁsummary__mutmut_orig"), object.__getattribute__(self, "xǁMetricsAggregatorǁsummary__mutmut_mutants"), args, kwargs, self)
        return result 
    
    summary.__signature__ = _mutmut_signature(xǁMetricsAggregatorǁsummary__mutmut_orig)
    xǁMetricsAggregatorǁsummary__mutmut_orig.__name__ = 'xǁMetricsAggregatorǁsummary'
