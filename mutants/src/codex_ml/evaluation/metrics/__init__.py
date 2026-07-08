"""
Metric Adapters for Evaluation (WP-C)

This module provides pluggable metric adapters for common evaluation metrics.
All adapters implement the MetricAdapter interface from runner.py.

Available Metrics:
- AccuracyMetric: Classification accuracy
- BleuMetric: BLEU score for translation/generation
- RougeMetric: ROUGE scores for summarization
- PerplexityMetric: Language model perplexity
- LatencyMetric: Inference latency measurement

Usage:
    from codex_ml.evaluation.metrics import AccuracyMetric, RougeMetric

    metrics = [
        AccuracyMetric(),
        RougeMetric(['rouge1', 'rouge2', 'rougeL']),
    ]
"""

from codex_ml.evaluation.metrics.accuracy import AccuracyMetric
from codex_ml.evaluation.metrics.bleu import BleuMetric
from codex_ml.evaluation.metrics.latency import LatencyMetric
from codex_ml.evaluation.metrics.perplexity import PerplexityMetric
from codex_ml.evaluation.metrics.rouge import RougeMetric

__all__ = [
    "AccuracyMetric",
    "BleuMetric",
    "LatencyMetric",
    "PerplexityMetric",
    "RougeMetric",
]
