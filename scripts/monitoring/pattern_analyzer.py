#!/usr/bin/env python3
"""
Pattern Analyzer - Intelligent failure pattern recognition.

This module provides:
- Regex-based error signature matching
- Statistical analysis (failure rates, flakiness detection)
- Confidence score calculation
- Category and severity assignment

Usage:
    from scripts.monitoring.pattern_analyzer import PatternAnalyzer

    analyzer = PatternAnalyzer(pattern_db_path)
    matches = analyzer.analyze_logs(log_content)

Author: Artifact Monitor Agent
Version: 1.0.0
Created: 2026-01-22
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes workflow logs for known error patterns."""

    def __init__(self, pattern_db_path: Path):
        """
        Initialize pattern analyzer.

        Args:
            pattern_db_path: Path to error signatures YAML file
        """
        self.pattern_db_path = pattern_db_path
        self.patterns = self._load_patterns()
        self.statistical_patterns = self._load_statistical_patterns()

        logger.info(f"Loaded {len(self.patterns)} patterns from {pattern_db_path}")

    def _load_patterns(self) -> list[dict[str, Any]]:
        """Load error patterns from YAML database."""
        if not self.pattern_db_path.exists():
            logger.warning(f"Pattern database not found: {self.pattern_db_path}")
            return []

        with open(self.pattern_db_path) as f:
            data = yaml.safe_load(f)

        return data.get('patterns', [])

    def _load_statistical_patterns(self) -> list[dict[str, Any]]:
        """Load statistical patterns from YAML database."""
        if not self.pattern_db_path.exists():
            return []

        with open(self.pattern_db_path) as f:
            data = yaml.safe_load(f)

        return data.get('statistical_patterns', [])

    def analyze_logs(
        self,
        log_content: str,
        confidence_threshold: float = 0.6
    ) -> list[dict[str, Any]]:
        """
        Analyze log content for error patterns.

        Args:
            log_content: Workflow log content as string
            confidence_threshold: Minimum confidence score to include

        Returns:
            List of matched patterns with confidence scores
        """
        matches = []

        for pattern in self.patterns:
            match_result = self._match_pattern(pattern, log_content)
            if match_result and match_result['confidence'] >= confidence_threshold:
                matches.append(match_result)

        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)

        logger.info(f"Found {len(matches)} pattern matches (threshold: {confidence_threshold})")

        return matches

    def _match_pattern(
        self,
        pattern: dict[str, Any],
        log_content: str
    ) -> Optional[dict[str, Any]]:
        """
        Match a single pattern against log content.

        Args:
            pattern: Pattern definition
            log_content: Log content to search

        Returns:
            Match result with confidence score or None
        """
        regex = pattern.get('regex')
        if not regex:
            return None

        try:
            # Search for pattern in logs
            match = re.search(regex, log_content, re.IGNORECASE | re.MULTILINE)

            if match:
                # Extract matched groups
                groups = match.groups()

                # Build result
                result = {
                    'id': pattern.get('id'),
                    'name': pattern.get('name'),
                    'regex': regex,
                    'category': pattern.get('category'),
                    'severity': pattern.get('severity'),
                    'confidence': pattern.get('confidence', 0.5),
                    'description': pattern.get('description'),
                    'suggestion': self._format_suggestion(pattern.get('suggestion', ''), groups),
                    'agent': pattern.get('agent'),
                    'documentation': pattern.get('documentation'),
                    'matched_text': match.group(0)[:200],  # First 200 chars
                    'match_groups': list(groups)
                }

                logger.debug(f"Pattern matched: {pattern['id']} ({pattern['name']})")
                return result

        except re.error as e:
            logger.error(f"Invalid regex in pattern {pattern.get('id')}: {e}")

        return None

    def _format_suggestion(self, suggestion: str, match_groups: tuple) -> str:
        """
        Format suggestion string with captured groups.

        Args:
            suggestion: Suggestion template
            match_groups: Captured regex groups

        Returns:
            Formatted suggestion
        """
        if not match_groups:
            return suggestion

        # Replace {match_group_N} with actual captured values
        for i, group in enumerate(match_groups, 1):
            placeholder = f"{{match_group_{i}}}"
            if placeholder in suggestion and group:
                suggestion = suggestion.replace(placeholder, group)

        return suggestion

    def analyze_statistical_patterns(
        self,
        metrics: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Analyze metrics for statistical patterns (flakiness, degradation).

        Args:
            metrics: Workflow metrics (failure_rate, flakiness_score, etc.)

        Returns:
            List of matched statistical patterns
        """
        matches = []

        for pattern in self.statistical_patterns:
            match_result = self._match_statistical_pattern(pattern, metrics)
            if match_result:
                matches.append(match_result)

        return matches

    def _match_statistical_pattern(
        self,
        pattern: dict[str, Any],
        metrics: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Match a statistical pattern against metrics.

        Args:
            pattern: Statistical pattern definition
            metrics: Workflow metrics

        Returns:
            Match result or None
        """
        detection_method = pattern.get('detection_method')
        thresholds = pattern.get('thresholds', {})

        # Flaky test detection
        if detection_method == 'failure_rate':
            failure_rate = metrics.get('failure_rate', 0) / 100  # Convert to 0-1
            min_rate = thresholds.get('failure_rate_min', 0)
            max_rate = thresholds.get('failure_rate_max', 1)

            if min_rate <= failure_rate <= max_rate:
                return {
                    'id': pattern.get('id'),
                    'name': pattern.get('name'),
                    'category': pattern.get('category'),
                    'severity': pattern.get('severity'),
                    'confidence': pattern.get('confidence', 0.7),
                    'description': pattern.get('description'),
                    'suggestion': pattern.get('suggestion'),
                    'agent': pattern.get('agent'),
                    'detection_method': detection_method,
                    'matched_metrics': {
                        'failure_rate': failure_rate,
                        'threshold_min': min_rate,
                        'threshold_max': max_rate
                    }
                }

        # Performance degradation detection
        elif detection_method == 'duration_trend':
            # This would require historical data comparison
            # Placeholder for future implementation
            pass

        return None

    def categorize_failure(
        self,
        matches: list[dict[str, Any]]
    ) -> tuple[str, str]:
        """
        Determine overall category and severity from matches.

        Args:
            matches: List of pattern matches

        Returns:
            (category, severity) tuple
        """
        if not matches:
            return ('unknown', 'medium')

        # Use highest confidence match
        top_match = matches[0]
        category = top_match.get('category', 'unknown')
        severity = top_match.get('severity', 'medium')

        return category, severity

    def get_agent_recommendation(
        self,
        matches: list[dict[str, Any]]
    ) -> Optional[str]:
        """
        Get recommended agent based on pattern matches.

        Args:
            matches: List of pattern matches

        Returns:
            Agent name or None
        """
        if not matches:
            return None

        # Use agent from highest confidence match
        return matches[0].get('agent')

    def generate_pattern_report(
        self,
        matches: list[dict[str, Any]],
        max_patterns: int = 5
    ) -> str:
        """
        Generate a formatted report of matched patterns.

        Args:
            matches: List of pattern matches
            max_patterns: Maximum patterns to include

        Returns:
            Markdown formatted report
        """
        if not matches:
            return "_No error patterns detected. Manual investigation required._"

        report = ""

        for i, match in enumerate(matches[:max_patterns], 1):
            report += f"\n### Pattern {i}: {match['name']}\n\n"
            report += f"- **ID**: `{match['id']}`\n"
            report += f"- **Category**: {match['category']}\n"
            report += f"- **Severity**: {match['severity']}\n"
            report += f"- **Confidence**: {match['confidence'] * 100:.0f}%\n\n"

            if match.get('description'):
                report += f"**Description**: {match['description']}\n\n"

            if match.get('matched_text'):
                report += f"**Matched Text**:\n```\n{match['matched_text']}\n```\n\n"

            if match.get('suggestion'):
                report += f"**Suggested Fix**: {match['suggestion']}\n\n"

            if match.get('documentation'):
                report += f"**Documentation**: {match['documentation']}\n\n"

            if match.get('agent'):
                report += f"**Recommended Agent**: {match['agent']}\n\n"

            report += "---\n"

        if len(matches) > max_patterns:
            report += f"\n_... and {len(matches) - max_patterns} more patterns matched_\n"

        return report

    def calculate_overall_confidence(
        self,
        matches: list[dict[str, Any]]
    ) -> float:
        """
        Calculate overall confidence score from all matches.

        Args:
            matches: List of pattern matches

        Returns:
            Overall confidence score (0.0-1.0)
        """
        if not matches:
            return 0.0

        # Weighted average with exponential decay for lower-ranked matches
        total_weight = 0.0
        weighted_sum = 0.0

        for i, match in enumerate(matches):
            weight = 0.5 ** i  # Exponential decay: 1.0, 0.5, 0.25, 0.125, ...
            confidence = match.get('confidence', 0.5)

            weighted_sum += confidence * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0


def main():
    """Test pattern analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description='Test pattern analyzer')
    parser.add_argument(
        '--pattern-db',
        type=Path,
        default=Path('.codex/monitoring/patterns/error_signatures.yaml'),
        help='Path to pattern database'
    )
    parser.add_argument(
        '--log-file',
        type=Path,
        help='Path to log file to analyze'
    )
    parser.add_argument(
        '--test-string',
        help='Test string to analyze'
    )

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = PatternAnalyzer(args.pattern_db)

    # Get log content
    if args.log_file:
        with open(args.log_file) as f:
            log_content = f.read()
    elif args.test_string:
        log_content = args.test_string
    else:
        print("Error: Provide --log-file or --test-string")
        return 1

    # Analyze
    matches = analyzer.analyze_logs(log_content)

    # Print results
    print("\nPattern Analysis Results")
    print("=" * 60)
    print(f"Patterns matched: {len(matches)}")
    print(f"Overall confidence: {analyzer.calculate_overall_confidence(matches):.2f}")

    if matches:
        category, severity = analyzer.categorize_failure(matches)
        agent = analyzer.get_agent_recommendation(matches)

        print(f"Category: {category}")
        print(f"Severity: {severity}")
        print(f"Recommended agent: {agent}")
        print("\n" + analyzer.generate_pattern_report(matches))

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
