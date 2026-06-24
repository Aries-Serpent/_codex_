#!/usr/bin/env python3
"""
PHASE 9.1: D_CAPABLE Confidence Scoring Algorithm

Implements multi-factor confidence scoring (0-100 scale) for autonomous decisions.

Scoring Algorithm:
  Final Confidence = (
      Historical Accuracy × 0.40 +
      Context Complexity × 0.30 +
      Test Coverage × 0.20 +
      Manual Signals × 0.10
  )

Features:
  - Fast evaluation (<100ms with caching)
  - Multi-factor weighting
  - Per-agent baseline calibration
  - Real-time context analysis
  - Manual override signals
  - LRU caching for performance

Usage:
  scorer = ConfidenceScorer()

  # Score a decision
  score = scorer.score_decision(
      agent_id="test-assertion-updater",
      historical_accuracy=80.9,
      context_complexity=2,  # 0-5 scale
      test_coverage=95,
      manual_signals=0,
  )

  # Score with full context
  score_info = scorer.score_with_context(
      agent_id="ci-testing-agent",
      decision_context={
          "files_affected": 12,
          "dependencies": 3,
          "test_coverage": 98,
      },
      manual_override="--high-confidence",
  )
"""

import json
import sqlite3
from functools import lru_cache
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
import argparse
from datetime import datetime


@dataclass
class ScoringFactors:
    """Components of confidence score."""
    historical_accuracy: float
    context_complexity: float
    test_coverage: float
    manual_signals: float


class ConfidenceScorer:
    """Multi-factor confidence scoring algorithm."""

    # Agent-specific calibration (baseline historical accuracy, 0-100)
    AGENT_BASELINES = {
        "ci-health-alert-agent": 92.0,
        "ci-testing-agent": 82.0,
        "copilot-session-chain": 78.0,
        "energy-conversion-agent": 80.0,
        "packaging-validation-agent": 88.0,
        "rust-error-validator": 86.0,
        "test-assertion-updater": 79.0,
        "test-pattern-guardian": 90.0,
        "workflow-ci-fixer": 87.0,
    }

    # Weights for confidence factors
    WEIGHTS = {
        "historical_accuracy": 0.40,
        "context_complexity": 0.30,
        "test_coverage": 0.20,
        "manual_signals": 0.10,
    }

    # Escalation thresholds by agent
    ESCALATION_THRESHOLDS = {
        "ci-health-alert-agent": 65.0,
        "ci-testing-agent": 60.0,
        "copilot-session-chain": 60.0,
        "energy-conversion-agent": 65.0,
        "packaging-validation-agent": 65.0,
        "rust-error-validator": 70.0,
        "test-assertion-updater": 60.0,
        "test-pattern-guardian": 65.0,
        "workflow-ci-fixer": 70.0,
    }

    def __init__(self, db_path: str = ".codex/phase_9_1_decisions.db"):
        """Initialize confidence scorer."""
        self.db_path = db_path
        self._agent_decision_cache = {}

    @lru_cache(maxsize=256)
    def _get_historical_accuracy(self, agent_id: str) -> float:
        """Get historical accuracy baseline from decision log."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN outcome = 'SUCCESS' THEN 1 ELSE 0 END) as successful
                FROM decision_log
                WHERE agent_id = ? AND outcome IN ('SUCCESS', 'FAILED')
            """, (agent_id,))

            row = cursor.fetchone()
            conn.close()

            if not row or row[0] == 0:
                return self.AGENT_BASELINES.get(agent_id, 75.0)

            total = row[0]
            successful = row[1] or 0
            accuracy = (successful / total * 100) if total > 0 else 0
            return min(100.0, max(0.0, accuracy))
        except Exception:
            return self.AGENT_BASELINES.get(agent_id, 75.0)

    def _analyze_context_complexity(
        self,
        context: Dict[str, Any],
    ) -> Tuple[int, str]:
        """
        Analyze decision context to determine complexity level.

        Complexity Levels:
        - 0 (Simple): Single-agent, no dependencies
        - 1 (Low): Single-agent, 1-2 dependencies
        - 2 (Medium): Multi-agent or complex analysis
        - 3 (High): Cross-system impact, multiple dependencies
        - 4 (Critical): System-wide impact, many unknowns
        - 5 (Unknown): Novel scenario, insufficient data
        """
        files_affected = len(context.get("files_affected", []))
        dependencies = len(context.get("dependencies", []))
        cross_system = context.get("cross_system_impact", False)
        novel_scenario = context.get("novel_scenario", False)

        # Complexity scoring
        complexity_score = 0
        details = []

        if novel_scenario:
            complexity_score = 5
            details.append("Novel scenario, insufficient data")
        elif cross_system and dependencies > 3:
            complexity_score = 4
            details.append("Critical: system-wide impact, multiple dependencies")
        elif cross_system or dependencies > 3:
            complexity_score = 3
            details.append(f"High: cross-system impact with {dependencies} dependencies")
        elif files_affected > 10 or dependencies > 1:
            complexity_score = 2
            details.append(f"Medium: {files_affected} files, {dependencies} dependencies")
        elif dependencies > 0:
            complexity_score = 1
            details.append(f"Low: {dependencies} dependencies")
        else:
            complexity_score = 0
            details.append("Simple: single-agent, no dependencies")

        return complexity_score, " | ".join(details)

    def _complexity_to_score(self, complexity_level: int) -> float:
        """Convert complexity level to confidence score component."""
        mapping = {
            0: 100.0,  # Simple → full confidence
            1: 80.0,   # Low complexity → 80% confidence
            2: 60.0,   # Medium complexity → 60% confidence
            3: 40.0,   # High complexity → 40% confidence
            4: 20.0,   # Critical complexity → 20% confidence
            5: 0.0,    # Unknown → 0% confidence
        }
        return mapping.get(complexity_level, 0.0)

    def _analyze_test_coverage(self, context: Dict[str, Any]) -> float:
        """Analyze test coverage for this decision type."""
        test_coverage = context.get("test_coverage", 0)
        test_pass_rate = context.get("test_pass_rate", 100)
        relevant_tests = context.get("relevant_tests", 0)

        # Coverage score (0-100)
        if relevant_tests < 10:
            # Insufficient test coverage
            return 0.0
        elif test_coverage < 50:
            return 40.0
        elif test_coverage < 75:
            return 70.0
        elif test_coverage < 90:
            return 85.0
        else:
            return test_pass_rate  # Use pass rate as final score

    def _evaluate_manual_signals(self, signals: Optional[Dict[str, Any]]) -> float:
        """Evaluate manual override signals."""
        if not signals:
            return 0.0

        score = 0.0

        # Explicit overrides
        if signals.get("high_confidence"):
            score += 15.0
        if signals.get("caution"):
            score -= 20.0
        if signals.get("block"):
            score -= 100.0  # Force escalation

        return max(-100.0, min(15.0, score))

    def score_decision(
        self,
        agent_id: str,
        historical_accuracy: Optional[float] = None,
        context_complexity: Optional[int] = None,
        test_coverage: Optional[float] = None,
        manual_signals: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate confidence score (0-100).

        Fast calculation with optional caching.
        """
        # Use provided values or estimate from database
        if historical_accuracy is None:
            historical_accuracy = self._get_historical_accuracy(agent_id)

        if context_complexity is None and context:
            context_complexity, _ = self._analyze_context_complexity(context)

        if context_complexity is not None:
            complexity_score = self._complexity_to_score(context_complexity)
        else:
            complexity_score = 50.0  # Neutral default

        if test_coverage is None and context:
            test_coverage = self._analyze_test_coverage(context)

        if test_coverage is None:
            test_coverage = 50.0  # Neutral default

        if manual_signals is None and context and "manual_signals" in context:
            manual_signals = self._evaluate_manual_signals(context["manual_signals"])

        if manual_signals is None:
            manual_signals = 0.0

        # Calculate weighted confidence score
        confidence = (
            historical_accuracy * self.WEIGHTS["historical_accuracy"] +
            complexity_score * self.WEIGHTS["context_complexity"] +
            test_coverage * self.WEIGHTS["test_coverage"] +
            manual_signals * self.WEIGHTS["manual_signals"]
        )

        return max(0.0, min(100.0, confidence))

    def score_with_context(
        self,
        agent_id: str,
        decision_context: Dict[str, Any],
        manual_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Score a decision with full context analysis."""
        # Prepare signals
        signals = None
        if manual_override:
            signals = {
                "high_confidence": "--high-confidence" in manual_override,
                "caution": "--caution" in manual_override,
                "block": "--block" in manual_override,
            }

        # Analyze components
        complexity_level, complexity_detail = self._analyze_context_complexity(decision_context)
        complexity_score = self._complexity_to_score(complexity_level)

        historical_accuracy = self._get_historical_accuracy(agent_id)
        test_coverage = self._analyze_test_coverage(decision_context)
        manual_signals = self._evaluate_manual_signals(signals)

        # Calculate final confidence
        confidence = self.score_decision(
            agent_id=agent_id,
            historical_accuracy=historical_accuracy,
            context_complexity=complexity_level,
            test_coverage=test_coverage,
            manual_signals=manual_signals,
            context=decision_context,
        )

        escalation_threshold = self.ESCALATION_THRESHOLDS.get(agent_id, 60.0)
        requires_escalation = confidence < escalation_threshold or (signals and signals.get("block"))

        return {
            "agent_id": agent_id,
            "confidence_score": round(confidence, 2),
            "escalation_required": requires_escalation,
            "escalation_threshold": escalation_threshold,
            "factors": {
                "historical_accuracy": {
                    "value": round(historical_accuracy, 2),
                    "weight": self.WEIGHTS["historical_accuracy"],
                    "contribution": round(historical_accuracy * self.WEIGHTS["historical_accuracy"], 2),
                },
                "context_complexity": {
                    "level": complexity_level,
                    "detail": complexity_detail,
                    "value": round(complexity_score, 2),
                    "weight": self.WEIGHTS["context_complexity"],
                    "contribution": round(complexity_score * self.WEIGHTS["context_complexity"], 2),
                },
                "test_coverage": {
                    "value": round(test_coverage, 2),
                    "weight": self.WEIGHTS["test_coverage"],
                    "contribution": round(test_coverage * self.WEIGHTS["test_coverage"], 2),
                },
                "manual_signals": {
                    "value": round(manual_signals, 2),
                    "weight": self.WEIGHTS["manual_signals"],
                    "contribution": round(manual_signals * self.WEIGHTS["manual_signals"], 2),
                    "signals": signals,
                },
            },
            "decision_action": (
                "BLOCK" if signals and signals.get("block")
                else "ESCALATE" if requires_escalation
                else "EXECUTE"
            ),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def get_agent_confidence_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get confidence statistics for an agent."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    AVG(confidence_score) as avg,
                    MIN(confidence_score) as min,
                    MAX(confidence_score) as max,
                    STDDEV(confidence_score) as stddev
                FROM decision_log
                WHERE agent_id = ?
            """, (agent_id,))

            row = cursor.fetchone()
            conn.close()

            if not row or row[0] == 0:
                return {
                    "agent_id": agent_id,
                    "total_decisions": 0,
                    "avg_confidence": self.AGENT_BASELINES.get(agent_id, 75.0),
                }

            return {
                "agent_id": agent_id,
                "total_decisions": row[0],
                "avg_confidence": round(row[1], 2) if row[1] else 0,
                "min_confidence": round(row[2], 2) if row[2] else 0,
                "max_confidence": round(row[3], 2) if row[3] else 0,
                "stddev_confidence": round(row[4], 2) if row[4] else 0,
            }
        except Exception:
            return {
                "agent_id": agent_id,
                "avg_confidence": self.AGENT_BASELINES.get(agent_id, 75.0),
            }


def main():
    """CLI interface for confidence scorer."""
    parser = argparse.ArgumentParser(description="Confidence Scoring Algorithm")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Score command
    score_parser = subparsers.add_parser("score", help="Score a decision")
    score_parser.add_argument("--agent", required=True, help="Agent ID")
    score_parser.add_argument("--accuracy", type=float, help="Historical accuracy")
    score_parser.add_argument("--complexity", type=int, help="Context complexity (0-5)")
    score_parser.add_argument("--coverage", type=float, help="Test coverage percent")
    score_parser.add_argument("--override", help="Manual override signal")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get agent statistics")
    stats_parser.add_argument("--agent", required=True, help="Agent ID")

    # Algorithm command
    algorithm_parser = subparsers.add_parser("algorithm", help="Show algorithm")

    args = parser.parse_args()
    scorer = ConfidenceScorer()

    if args.command == "score":
        context = {
            "files_affected": [],
            "dependencies": [],
            "test_coverage": args.coverage or 75.0,
            "test_pass_rate": 100.0,
            "relevant_tests": 50,
        }
        if args.override:
            context["manual_signals"] = {
                "high_confidence": "--high-confidence" in args.override,
                "caution": "--caution" in args.override,
                "block": "--block" in args.override,
            }

        result = scorer.score_with_context(args.agent, context, args.override)
        print(json.dumps(result, indent=2))

    elif args.command == "stats":
        stats = scorer.get_agent_confidence_stats(args.agent)
        print(json.dumps(stats, indent=2))

    elif args.command == "algorithm":
        print("PHASE 9.1: Confidence Scoring Algorithm")
        print("=" * 60)
        print("\nFormula:")
        print("  Confidence = (Historical × 0.40) + (Complexity × 0.30)")
        print("             + (Coverage × 0.20) + (Signals × 0.10)")
        print("\nComplexity Levels:")
        print("  0 (Simple)    → 100 points")
        print("  1 (Low)       → 80 points")
        print("  2 (Medium)    → 60 points")
        print("  3 (High)      → 40 points")
        print("  4 (Critical)  → 20 points")
        print("  5 (Unknown)   → 0 points")
        print("\nAgent Escalation Thresholds:")
        for agent, threshold in sorted(scorer.ESCALATION_THRESHOLDS.items()):
            print(f"  {agent}: <{threshold}%")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
