"""
Reasoning Evaluation Metrics

Implements specialized metrics for evaluating reasoning capabilities including:
- win_rate: Comparative performance against baseline
- critique_density: Quality and depth of explanations
- latency_delta: Response time comparison
- judge_disagreement: Inter-rater reliability
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)


@dataclass
class ReasoningMetrics:
    """Container for reasoning evaluation metrics"""

    win_rate: float = 0.0
    critique_density: float = 0.0
    latency_p95: float = 0.0
    judge_disagreement: float = 0.0
    trace_coverage: float = 0.0
    explanation_depth: float = 0.0
    consistency: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary"""
        return {
            "win_rate": self.win_rate,
            "critique_density": self.critique_density,
            "latency_p95": self.latency_p95,
            "judge_disagreement": self.judge_disagreement,
            "trace_coverage": self.trace_coverage,
            "explanation_depth": self.explanation_depth,
            "consistency": self.consistency,
        }


def calculate_win_rate(
    predictions: list[str],
    references: list[str],
    baseline_predictions: Optional[list[str]] = None,
) -> float:
    """
    Calculate win rate against baseline or references.

    Win rate measures how often the model's response is preferred
    over a baseline response.

    Args:
        predictions: Model predictions
        references: Reference responses
        baseline_predictions: Optional baseline model predictions

    Returns:
        Win rate (0.0-1.0)
    """
    if not predictions or not references:
        return 0.0

    if len(predictions) != len(references):
        logger.warning(
            f"Length mismatch: {len(predictions)} predictions vs {len(references)} references"
        )
        return 0.0

    wins = 0
    total = 0

    for pred, ref in zip(predictions, references, strict=False):
        # Simple heuristic: longer, more detailed responses often better
        # In production, use a trained judge model
        pred_score = _score_response_quality(pred)
        ref_score = _score_response_quality(ref)

        if baseline_predictions and total < len(baseline_predictions):
            baseline = baseline_predictions[total]
            baseline_score = _score_response_quality(baseline)
            # Win if better than baseline
            if pred_score > baseline_score:
                wins += 1
        else:
            # Win if close to reference
            if abs(pred_score - ref_score) < ref_score * 0.2:  # Within 20%
                wins += 1

        total += 1

    return wins / total if total > 0 else 0.0


def calculate_critique_density(
    responses: list[str],
) -> float:
    """
    Calculate critique density - measure of explanation quality.

    Critique density captures:
    - Presence of reasoning steps
    - Use of examples
    - Acknowledgment of edge cases
    - Depth of explanation

    Args:
        responses: list of response strings

    Returns:
        Critique density score (0.0-1.0)
    """
    if not responses:
        return 0.0

    total_density = 0.0

    for response in responses:
        density = 0.0
        response_lower = response.lower()

        # Check for reasoning indicators
        reasoning_markers = [
            "because",
            "therefore",
            "thus",
            "since",
            "let me",
            "step by step",
            "first",
            "second",
            "finally",
        ]
        density += sum(0.05 for marker in reasoning_markers if marker in response_lower)

        # Check for examples
        example_markers = ["example", "for instance", "such as", "e.g.", "i.e."]
        density += sum(0.10 for marker in example_markers if marker in response_lower)

        # Check for edge cases / qualifications
        qualification_markers = [
            "however",
            "but",
            "although",
            "except",
            "note that",
            "important",
            "caveat",
        ]
        density += sum(0.08 for marker in qualification_markers if marker in response_lower)

        # Check for mathematical notation
        if re.search(r"[=+\-*/^<>≤≥]|\d+\s*[+\-*/]\s*\d+", response):
            density += 0.15

        # Check for structured formatting (numbered lists, bullets)
        if re.search(r"^\s*[\d•\-*]\s+", response, re.MULTILINE):
            density += 0.10

        # Length factor (longer explanations often more detailed)
        words = len(response.split())
        if words > 100:
            density += 0.10
        if words > 200:
            density += 0.10

        # Cap at 1.0
        total_density += min(density, 1.0)

    return total_density / len(responses)


def calculate_latency_delta(
    latencies: list[float],
    baseline_latencies: Optional[list[float]] = None,
    percentile: int = 95,
) -> float:
    """
    Calculate latency delta at specified percentile.

    Args:
        latencies: Response latencies in milliseconds
        baseline_latencies: Optional baseline latencies for comparison
        percentile: Percentile to calculate (default 95)

    Returns:
        Latency delta (negative = faster than baseline)
    """
    if not latencies:
        return 0.0

    try:
        import numpy as np

        latencies_array = np.array(latencies)
        p_latency = np.percentile(latencies_array, percentile)

        if baseline_latencies:
            baseline_array = np.array(baseline_latencies)
            baseline_p = np.percentile(baseline_array, percentile)
            delta = p_latency - baseline_p
            return float(delta)

        return float(p_latency)
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        # Fallback without numpy
        sorted_latencies = sorted(latencies)
        idx = int(len(sorted_latencies) * percentile / 100.0)
        idx = min(idx, len(sorted_latencies) - 1)
        p_latency = sorted_latencies[idx]

        if baseline_latencies:
            sorted_baseline = sorted(baseline_latencies)
            b_idx = int(len(sorted_baseline) * percentile / 100.0)
            b_idx = min(b_idx, len(sorted_baseline) - 1)
            baseline_p = sorted_baseline[b_idx]
            return float(p_latency - baseline_p)

        return float(p_latency)


def calculate_judge_disagreement(
    judge_ratings: list[list[float]],
) -> float:
    """
    Calculate inter-rater disagreement among judges.

    Lower disagreement = more consensus = better reliability.

    Args:
        judge_ratings: list of rating lists, where each inner list contains
                      ratings from different judges for one response

    Returns:
        Disagreement score (0.0-1.0, lower is better)
    """
    if not judge_ratings:
        return 0.0

    try:
        import numpy as np

        disagreements = []

        for ratings in judge_ratings:
            if len(ratings) < 2:
                continue

            # Calculate coefficient of variation (normalized std dev)
            ratings_array = np.array(ratings)
            mean = np.mean(ratings_array)

            if mean == 0:
                disagreements.append(0.0)
            else:
                std = np.std(ratings_array)
                cv = std / mean
                disagreements.append(min(cv, 1.0))  # Cap at 1.0

        return float(np.mean(disagreements)) if disagreements else 0.0
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        # Fallback without numpy
        disagreements = []

        for ratings in judge_ratings:
            if len(ratings) < 2:
                continue

            mean = sum(ratings) / len(ratings)
            if mean == 0:
                disagreements.append(0.0)
            else:
                variance = sum((x - mean) ** 2 for x in ratings) / len(ratings)
                std = variance**0.5
                cv = std / mean
                disagreements.append(min(cv, 1.0))

        return sum(disagreements) / len(disagreements) if disagreements else 0.0


def calculate_trace_coverage(
    responses: list[str],
    required_steps: Optional[list[list[str]]] = None,
) -> float:
    """
    Calculate trace coverage - how many reasoning steps are present.

    Args:
        responses: list of response strings
        required_steps: Optional list of required reasoning steps per response

    Returns:
        Trace coverage (0.0-1.0)
    """
    if not responses:
        return 0.0

    if required_steps and len(required_steps) != len(responses):
        logger.warning("Mismatch between responses and required steps")
        return 0.0

    total_coverage = 0.0

    for i, response in enumerate(responses):
        response_lower = response.lower()

        if required_steps and i < len(required_steps):
            # Check for specific required steps
            steps_found = sum(1 for step in required_steps[i] if step.lower() in response_lower)
            coverage = steps_found / len(required_steps[i]) if required_steps[i] else 0.0
        else:
            # Generic step detection
            step_indicators = [
                "step 1",
                "step 2",
                "step 3",
                "first",
                "second",
                "third",
                "finally",
                "then",
                "next",
            ]
            steps_found = sum(1 for indicator in step_indicators if indicator in response_lower)
            coverage = min(steps_found / 5.0, 1.0)  # Normalize to max 5 steps

        total_coverage += coverage

    return total_coverage / len(responses)


def calculate_explanation_depth(
    responses: list[str],
) -> float:
    """
    Calculate explanation depth based on reasoning complexity.

    Args:
        responses: list of response strings

    Returns:
        Explanation depth score (0.0-1.0)
    """
    if not responses:
        return 0.0

    total_depth = 0.0

    for response in responses:
        depth = 0.0

        # Multi-level reasoning (nested explanations)
        indent_pattern = r"^\s{2,}[\-*•\d]"
        nested_levels = len(re.findall(indent_pattern, response, re.MULTILINE))
        depth += min(nested_levels * 0.15, 0.45)

        # Causal chains (because X, therefore Y)
        causal_pattern = r"(because|since|thus|therefore|hence)"
        causal_count = len(re.findall(causal_pattern, response, re.IGNORECASE))
        depth += min(causal_count * 0.10, 0.30)

        # Mathematical derivations
        if re.search(r"derive|proof|qed|∴|∵", response, re.IGNORECASE):
            depth += 0.25

        total_depth += min(depth, 1.0)

    return total_depth / len(responses)


def calculate_consistency(
    responses: list[str],
    _reference_facts: Optional[list[dict[str, Any]]] = None,
) -> float:
    """
    Calculate logical consistency of responses.

    Args:
        responses: list of response strings
        _reference_facts: Optional known facts to check against (unused)

    Returns:
        Consistency score (0.0-1.0)
    """
    if not responses:
        return 0.0

    # Simple heuristic: check for logical contradictions
    # In production, use more sophisticated NLI models

    total_consistency = 0.0

    for response in responses:
        consistency = 1.0  # Start with perfect score

        # Check for explicit contradictions
        contradiction_patterns = [
            (r"is true.*is false", 0.5),
            (r"always.*never", 0.3),
            (r"all.*none", 0.3),
            (r"must.*cannot", 0.3),
        ]

        for pattern, penalty in contradiction_patterns:
            if re.search(pattern, response, re.IGNORECASE | re.DOTALL):
                consistency -= penalty

        # Ensure non-negative
        consistency = max(consistency, 0.0)
        total_consistency += consistency

    return total_consistency / len(responses)


def _score_response_quality(response: str) -> float:
    """Internal helper to score response quality"""
    score = 0.0

    # Length (normalized)
    words = len(response.split())
    score += min(words / 100.0, 1.0) * 0.3

    # Structure (paragraphs, lists)
    paragraphs = len(response.split("\n\n"))
    score += min(paragraphs / 3.0, 1.0) * 0.2

    # Reasoning markers
    reasoning_markers = ["because", "therefore", "thus", "step", "example"]
    markers_found = sum(1 for m in reasoning_markers if m in response.lower())
    score += min(markers_found / 3.0, 1.0) * 0.3

    # Completeness (contains conclusion/answer)
    if any(word in response.lower() for word in ["answer", "conclusion", "therefore", "result"]):
        score += 0.2

    return min(score, 1.0)


def evaluate_reasoning(
    predictions: list[str],
    references: list[str],
    baseline_predictions: Optional[list[str]] = None,
    latencies: Optional[list[float]] = None,
    judge_ratings: Optional[list[list[float]]] = None,
) -> ReasoningMetrics:
    """
    Comprehensive reasoning evaluation.

    Args:
        predictions: Model predictions
        references: Reference responses
        baseline_predictions: Optional baseline predictions
        latencies: Optional response latencies
        judge_ratings: Optional multi-judge ratings

    Returns:
        ReasoningMetrics with all computed metrics
    """
    metrics = ReasoningMetrics()

    # Calculate metrics
    metrics.win_rate = calculate_win_rate(predictions, references, baseline_predictions)
    metrics.critique_density = calculate_critique_density(predictions)
    metrics.trace_coverage = calculate_trace_coverage(predictions)
    metrics.explanation_depth = calculate_explanation_depth(predictions)
    metrics.consistency = calculate_consistency(predictions)

    if latencies:
        metrics.latency_p95 = calculate_latency_delta(latencies)

    if judge_ratings:
        metrics.judge_disagreement = calculate_judge_disagreement(judge_ratings)

    # Add metadata
    metrics.metadata = {
        "num_predictions": len(predictions),
        "num_references": len(references),
        "has_baseline": baseline_predictions is not None,
        "has_latencies": latencies is not None,
        "has_judges": judge_ratings is not None,
    }

    return metrics


if __name__ == "__main__":
    # Example usage
    predictions = [
        "Let me solve this step by step: First, we identify the variables. Therefore, x = 5.",
        "The answer is 42 because of the calculation.",
    ]
    references = [
        "The solution is x = 5 after solving the equation.",
        "The result is 42.",
    ]

    metrics = evaluate_reasoning(predictions, references)
    logger.info(f"Reasoning Metrics: {metrics.to_dict()}")
