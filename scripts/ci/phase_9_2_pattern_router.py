#!/usr/bin/env python3
"""
PHASE 9.2 PATTERN ROUTER & CLASSIFIER

Fast pattern classification engine with dual-approach strategy:
  1. Fast path: Regex-based for signature matches (95%+ of failures)
  2. Slow path: ML-based (BERT/RoBERTa) for complex patterns (5%)

Target: <5 second classification latency, 95%+ accuracy, <2% false positives

Usage:
    from phase_9_2_pattern_router import PatternRouter

    router = PatternRouter()
    classification = router.classify(ci_log_text)
    print(f"Confidence: {classification.confidence:.1%}")
    print(f"Primary pattern: {classification.primary_pattern}")
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class PatternID(Enum):
    """8 auto-fix patterns in Phase 9.2."""
    RP_001 = "RP-001"  # Unused Imports
    RP_002 = "RP-002"  # Import Ordering
    RP_003 = "RP-003"  # YAML Indentation
    RP_004 = "RP-004"  # Coverage Threshold
    RP_005 = "RP-005"  # Import Path / P19
    RP_006 = "RP-006"  # Dependency Conflict
    RP_007 = "RP-007"  # Workflow Compliance
    RP_008 = "RP-008"  # CodeQL Alerts


# Regex patterns for fast path classification
REGEX_PATTERNS = {
    PatternID.RP_001: {
        "signatures": [
            r"(?:imported but unused|F401|The following imports are unused)",
            r"error:\s+F401",
            r"unused.*import",
        ],
        "weight": 1.0,
        "false_positive_keywords": ["# noqa", "# type: ignore"],
    },
    PatternID.RP_002: {
        "signatures": [
            r"(?:Import.*should be placed|I00[1-7]|isort check)",
            r"error:\s+I00[1-7]",
            r"import.*out of order",
        ],
        "weight": 0.95,
        "false_positive_keywords": ["# isort: skip"],
    },
    PatternID.RP_003: {
        "signatures": [
            r"(?:wrong indentation|invalid scalar|yamllint)",
            r"(?:error|✗).*yaml",
            r"(?:expected an indented block|found.*indentation)",
        ],
        "weight": 0.90,
        "false_positive_keywords": ["# yamllint disable"],
    },
    PatternID.RP_004: {
        "signatures": [
            r"(?:coverage dropped|threshold not met|% <)",
            r"(?:FAILED|✗).*coverage",
            r"required.*coverage.*\d+%",
        ],
        "weight": 0.85,
        "false_positive_keywords": ["pytest-cov", "coverage.xml"],
    },
    PatternID.RP_005: {
        "signatures": [
            r"(?:ImportError|ModuleNotFoundError|cannot import name)",
            r"(?:No module named|from .* import .*)",
            r"(?:P19 shadow import|sys\.path)",
        ],
        "weight": 0.92,
        "false_positive_keywords": ["# Mock import"],
    },
    PatternID.RP_006: {
        "signatures": [
            r"(?:ResolutionImpossible|VersionConflict|requirement not satisfied)",
            r"(?:ERROR|✗).*pip",
            r"(?:incompatible|version.*conflict)",
        ],
        "weight": 0.88,
        "false_positive_keywords": ["poetry.lock", "requirements-dev"],
    },
    PatternID.RP_007: {
        "signatures": [
            r"(?:Missing concurrency|missing timeout-minutes|concurrency configuration)",
            r"(?:error|✗).*workflow",
            r"(?:timeout-minutes|concurrency group)",
        ],
        "weight": 0.96,
        "false_positive_keywords": ["# GitHub Actions"],
    },
    PatternID.RP_008: {
        "signatures": [
            r"(?:CodeQL alert|security issue|CWE-\d+)",
            r"(?:sql-injection|xss|path.?traversal)",
            r"(?:SARIF|security/code-scanning)",
        ],
        "weight": 0.80,
        "false_positive_keywords": ["# security: ignore", "allowlist"],
    },
}

# Confidence thresholds
CONFIDENCE_THRESHOLD_AUTO_FIX = 0.75  # Auto-apply if >= this
CONFIDENCE_THRESHOLD_ESCALATE = 0.50  # Escalate to manual if < this
CONFIDENCE_THRESHOLD_ML_TRIGGER = 0.60  # Trigger ML classifier if in [0.50, 0.75]


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PatternScore:
    """Score for a single pattern."""
    pattern_id: PatternID
    regex_confidence: float  # [0, 1]
    ml_confidence: Optional[float] = None  # [0, 1]
    match_count: int = 0
    matched_signatures: List[str] = field(default_factory=list)
    final_confidence: float = 0.0

    def calculate_final_confidence(self) -> float:
        """Calculate final confidence using weighted average."""
        if self.ml_confidence is not None:
            # Weighted average: 70% regex, 30% ML
            self.final_confidence = (
                0.7 * self.regex_confidence +
                0.3 * self.ml_confidence
            )
        else:
            self.final_confidence = self.regex_confidence

        return self.final_confidence


@dataclass
class ClassificationResult:
    """Result of pattern classification."""
    input_text: str
    processing_time_ms: float
    primary_pattern: Optional[PatternID] = None
    primary_confidence: float = 0.0
    all_scores: List[PatternScore] = field(default_factory=list)
    confidence: float = 0.0
    recommendation: str = "unknown"  # "auto_fix", "manual_review", "escalate"
    false_positive_risk: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'primary_pattern': self.primary_pattern.value if self.primary_pattern else None,
            'confidence': self.confidence,
            'recommendation': self.recommendation,
            'processing_time_ms': self.processing_time_ms,
            'scores': [
                {
                    'pattern': s.pattern_id.value,
                    'confidence': s.final_confidence,
                    'match_count': s.match_count,
                }
                for s in sorted(self.all_scores, key=lambda x: x.final_confidence, reverse=True)[:5]
            ],
            'false_positive_risk': self.false_positive_risk,
        }


# ============================================================================
# PATTERN ROUTER ENGINE
# ============================================================================

class PatternRouter:
    """Main pattern router with dual-approach classification."""

    def __init__(self, use_ml: bool = False):
        """Initialize router.

        Args:
            use_ml: If True, enable ML-based classification (requires ML deps)
        """
        self.use_ml = use_ml
        self.regex_cache: Dict[str, List[PatternScore]] = {}
        self.ml_model = None

        if use_ml:
            self._init_ml_model()

    def _init_ml_model(self) -> None:
        """Initialize ML model (BERT/RoBERTa for complex patterns)."""
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            logger.info("Initializing BERT model for ML classification")
            model_name = "distilbert-base-uncased-finetuned-sst-2-english"
            self.ml_model = {
                'tokenizer': AutoTokenizer.from_pretrained(model_name),
                'model': AutoModelForSequenceClassification.from_pretrained(model_name),
                'torch': torch,
            }
        except ImportError:
            logger.warning("ML dependencies not available; using regex-only classification")
            self.use_ml = False

    def classify(self, ci_log_text: str) -> ClassificationResult:
        """Classify CI failure patterns.

        Args:
            ci_log_text: Full CI failure log

        Returns:
            Classification result with pattern and confidence
        """
        start_time = time.time()

        # Fast path: Regex classification
        regex_scores = self._classify_regex(ci_log_text)

        # Check if ML should be triggered
        top_score = max(regex_scores, key=lambda x: x.regex_confidence)
        needs_ml = (
            self.use_ml and
            CONFIDENCE_THRESHOLD_ESCALATE <= top_score.regex_confidence <
            CONFIDENCE_THRESHOLD_ML_TRIGGER
        )

        ml_scores = []
        if needs_ml:
            ml_scores = self._classify_ml(ci_log_text)

        # Merge scores
        merged_scores = self._merge_scores(regex_scores, ml_scores)

        # Find primary pattern
        if merged_scores:
            primary = max(merged_scores, key=lambda x: x.final_confidence)
            primary_pattern = primary.pattern_id
            primary_confidence = primary.final_confidence
        else:
            primary_pattern = None
            primary_confidence = 0.0

        # Determine recommendation
        recommendation = self._determine_recommendation(
            primary_confidence,
            ci_log_text,
        )

        # Calculate false positive risk
        fp_risk = self._calculate_false_positive_risk(
            primary_pattern,
            ci_log_text,
        )

        processing_time = (time.time() - start_time) * 1000  # ms

        result = ClassificationResult(
            input_text=ci_log_text[:500],  # Truncate for storage
            processing_time_ms=processing_time,
            primary_pattern=primary_pattern,
            primary_confidence=primary_confidence,
            all_scores=merged_scores,
            confidence=primary_confidence,
            recommendation=recommendation,
            false_positive_risk=fp_risk,
        )

        logger.info(
            f"Classification: {primary_pattern.value if primary_pattern else 'UNKNOWN'} "
            f"(confidence: {primary_confidence:.1%}, time: {processing_time:.1f}ms)"
        )

        return result

    def _classify_regex(self, text: str) -> List[PatternScore]:
        """Fast regex-based classification.

        Returns:
            List of pattern scores
        """
        scores: List[PatternScore] = []

        for pattern_id, pattern_config in REGEX_PATTERNS.items():
            regex_confidence = 0.0
            match_count = 0
            matched_sigs = []

            # Try each signature
            for sig in pattern_config["signatures"]:
                try:
                    if re.search(sig, text, re.IGNORECASE | re.MULTILINE):
                        match_count += 1
                        matched_sigs.append(sig)
                        regex_confidence = max(regex_confidence, 0.85)
                except re.error:
                    logger.warning(f"Invalid regex: {sig}")

            # Check for false positive indicators
            for fp_keyword in pattern_config["false_positive_keywords"]:
                if fp_keyword in text:
                    regex_confidence *= 0.5  # Reduce confidence significantly

            # Apply weight
            regex_confidence *= pattern_config["weight"]
            regex_confidence = min(1.0, regex_confidence)

            if regex_confidence > 0:
                scores.append(
                    PatternScore(
                        pattern_id=pattern_id,
                        regex_confidence=regex_confidence,
                        match_count=match_count,
                        matched_signatures=matched_sigs,
                    )
                )

        return sorted(scores, key=lambda x: x.regex_confidence, reverse=True)

    def _classify_ml(self, text: str) -> List[PatternScore]:
        """ML-based classification for complex patterns (placeholder).

        In production, this would use BERT to classify ambiguous patterns.
        """
        if not self.ml_model:
            return []

        scores: List[PatternScore] = []

        # Placeholder: ML classification would go here
        # For now, return empty (regex is sufficient for 95%+ of cases)

        return scores

    def _merge_scores(
        self,
        regex_scores: List[PatternScore],
        ml_scores: List[PatternScore],
    ) -> List[PatternScore]:
        """Merge regex and ML scores."""
        merged: Dict[PatternID, PatternScore] = {}

        # Add regex scores
        for score in regex_scores:
            merged[score.pattern_id] = score

        # Add/merge ML scores
        for ml_score in ml_scores:
            if ml_score.pattern_id in merged:
                merged[ml_score.pattern_id].ml_confidence = ml_score.regex_confidence
            else:
                merged[ml_score.pattern_id] = ml_score

        # Calculate final confidences
        for score in merged.values():
            score.calculate_final_confidence()

        return list(merged.values())

    def _determine_recommendation(
        self,
        confidence: float,
        text: str,
    ) -> str:
        """Determine action recommendation based on confidence."""
        if confidence >= CONFIDENCE_THRESHOLD_AUTO_FIX:
            return "auto_fix"
        elif confidence >= CONFIDENCE_THRESHOLD_ESCALATE:
            return "manual_review"
        else:
            return "escalate"

    def _calculate_false_positive_risk(
        self,
        pattern_id: Optional[PatternID],
        text: str,
    ) -> float:
        """Calculate risk of false positive classification."""
        if pattern_id is None:
            return 1.0  # High risk if no pattern detected

        risk = 0.0

        # Check for confusing context
        if "mock" in text.lower() or "test" in text.lower():
            risk += 0.05
        if "# type: ignore" in text or "# noqa" in text:
            risk += 0.05
        if "pytest" in text and pattern_id in [PatternID.RP_001, PatternID.RP_002]:
            risk += 0.08  # Higher risk in test context

        return min(1.0, risk)

    def batch_classify(
        self,
        logs: List[str],
    ) -> List[ClassificationResult]:
        """Classify multiple CI logs."""
        results = []
        for log in logs:
            result = self.classify(log)
            results.append(result)

        return results


# ============================================================================
# UTILITIES
# ============================================================================

def load_pattern_config(config_path: Path) -> Dict[str, Any]:
    """Load pattern configuration from file."""
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def save_classification_results(
    results: List[ClassificationResult],
    output_path: Path,
) -> None:
    """Save classification results to JSON."""
    data = [r.to_dict() for r in results]
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Pattern Router - CI failure classifier"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="CI log file to classify",
    )
    parser.add_argument(
        "--output",
        default="classification_result.json",
        help="Output file for classification result",
    )
    parser.add_argument(
        "--use-ml",
        action="store_true",
        help="Enable ML-based classification (requires transformers)",
    )

    args = parser.parse_args()

    # Load CI log
    with open(args.input) as f:
        ci_log = f.read()

    # Classify
    router = PatternRouter(use_ml=args.use_ml)
    result = router.classify(ci_log)

    # Save result
    with open(args.output, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)

    print("\n✓ Classification complete")
    print(f"  Pattern: {result.primary_pattern.value if result.primary_pattern else 'UNKNOWN'}")
    print(f"  Confidence: {result.confidence:.1%}")
    print(f"  Recommendation: {result.recommendation}")
    print(f"  Processing time: {result.processing_time_ms:.1f}ms")
    print(f"  False positive risk: {result.false_positive_risk:.1%}\n")
