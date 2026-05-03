"""
Flaky Test Detector - PERCEIVE Phase

Analyzes GitHub Actions logs and test results to identify flaky tests.

#AFTERMATH_PATTERN_IDENTIFIED: flaky_test_detection
#AFTERMATH_METRIC: tests_analyzed

PDA Loop: PERCEIVE Phase
- Fetch workflow runs from GitHub Actions
- Parse test results and timing data
- Analyze test code with pattern matchers
- Query cognitive brain for historical patterns
"""

# Import pattern matchers
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from concurrency_patterns import ConcurrencyPatternMatcher
from performance_patterns import PerformancePatternMatcher


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    status: str  # "passed", "failed", "skipped"
    duration: float  # seconds
    workflow_run_id: str
    timestamp: datetime
    error_message: Optional[str] = None


@dataclass
class TestStatistics:
    """Statistical analysis of test behavior."""
    test_name: str
    total_runs: int
    passed_count: int
    failed_count: int
    pass_rate: float
    avg_duration: float
    std_duration: float
    min_duration: float
    max_duration: float
    duration_variance: float


class FlakyTestDetector:
    """
    Detector for flaky tests - PERCEIVE Phase.

    #AFTERMATH_PATTERN_IDENTIFIED: test_analysis

    Responsibilities:
    - Parse GitHub Actions workflow logs
    - Extract test results and timing data
    - Run pattern matchers on test code
    - Calculate flakiness indicators
    - Query cognitive brain for patterns
    """

    def __init__(self, repo_path: Path, lookback_days: int = 30):
        """
        Initialize detector.

        Args:
            repo_path: Path to repository
            lookback_days: Number of days to analyze
        """
        self.repo_path = repo_path
        self.lookback_days = lookback_days
        self.performance_matcher = PerformancePatternMatcher()
        self.concurrency_matcher = ConcurrencyPatternMatcher()

        #AFTERMATH_METRIC: detector_initialized

    def perceive(self, workflow_runs: list[dict[str, Any]]) -> dict[str, Any]:
        """
        PERCEIVE phase - analyze test data.

        #AFTERMATH_PATTERN_IDENTIFIED: perception_phase

        Args:
            workflow_runs: List of workflow run data

        Returns:
            Context dictionary with analyzed data
        """
        context = {
            "test_results": self._parse_test_results(workflow_runs),
            "test_statistics": {},
            "code_patterns": {},
            "timing_anomalies": [],
            "historical_patterns": []
        }

        # Calculate statistics for each test
        test_results_by_name = self._group_by_test_name(context["test_results"])
        for test_name, results in test_results_by_name.items():
            context["test_statistics"][test_name] = self._calculate_statistics(results)

        # Analyze test code with pattern matchers
        context["code_patterns"] = self._analyze_test_code()

        # Detect timing anomalies
        context["timing_anomalies"] = self._detect_timing_anomalies(
            context["test_statistics"]
        )

        #AFTERMATH_METRIC: tests_analyzed = len(context["test_results"])
        #AFTERMATH_METRIC: patterns_found = len(context["code_patterns"])

        return context

    def _parse_test_results(self, workflow_runs: list[dict[str, Any]]) -> list[TestResult]:
        """
        Parse test results from workflow runs.

        #AFTERMATH_PATTERN_IDENTIFIED: log_parsing
        """
        results = []

        for run in workflow_runs:
            # In real implementation, would fetch logs via GitHub API
            # For now, simulate parsing
            run_results = self._extract_test_results_from_run(run)
            results.extend(run_results)

        #AFTERMATH_METRIC: workflow_runs_parsed = len(workflow_runs)
        return results

    def _extract_test_results_from_run(self, run: dict[str, Any]) -> list[TestResult]:
        """
        Extract test results from a single workflow run.

        Args:
            run: Workflow run data

        Returns:
            List of test results
        """
        # Simulate test result extraction
        # In production, would parse actual GitHub Actions logs
        return []

        # Example: Parse pytest output, unittest output, etc.
        # Pattern: "test_name ... PASSED/FAILED [duration]"

        #AFTERMATH_PATTERN_IDENTIFIED: pytest_log_parsing

    def _group_by_test_name(self, results: list[TestResult]) -> dict[str, list[TestResult]]:
        """Group test results by test name."""
        grouped = {}
        for result in results:
            if result.name not in grouped:
                grouped[result.name] = []
            grouped[result.name].append(result)
        return grouped

    def _calculate_statistics(self, results: list[TestResult]) -> TestStatistics:
        """
        Calculate statistics for a test.

        #AFTERMATH_PATTERN_IDENTIFIED: statistical_analysis
        """
        if not results:
            return TestStatistics(
                test_name="unknown",
                total_runs=0,
                passed_count=0,
                failed_count=0,
                pass_rate=0.0,
                avg_duration=0.0,
                std_duration=0.0,
                min_duration=0.0,
                max_duration=0.0,
                duration_variance=0.0
            )

        test_name = results[0].name
        total_runs = len(results)
        passed_count = sum(1 for r in results if r.status == "passed")
        failed_count = sum(1 for r in results if r.status == "failed")
        pass_rate = passed_count / total_runs if total_runs > 0 else 0.0

        durations = [r.duration for r in results]
        avg_duration = sum(durations) / len(durations)

        # Calculate standard deviation
        variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
        std_duration = variance ** 0.5

        return TestStatistics(
            test_name=test_name,
            total_runs=total_runs,
            passed_count=passed_count,
            failed_count=failed_count,
            pass_rate=pass_rate,
            avg_duration=avg_duration,
            std_duration=std_duration,
            min_duration=min(durations),
            max_duration=max(durations),
            duration_variance=variance
        )

    def _analyze_test_code(self) -> dict[str, list]:
        """
        Analyze test code with pattern matchers.

        #AFTERMATH_PATTERN_IDENTIFIED: code_pattern_analysis
        """
        patterns = {
            "performance": [],
            "concurrency": []
        }

        # Find test files
        test_files = list(self.repo_path.glob("**/test_*.py"))
        test_files.extend(list(self.repo_path.glob("**/*_test.py")))

        for test_file in test_files[:10]:  # Limit to first 10 for performance
            # Analyze with performance matcher
            perf_patterns = self.performance_matcher.analyze_file(test_file)
            patterns["performance"].extend(perf_patterns)

            # Analyze with concurrency matcher
            conc_patterns = self.concurrency_matcher.analyze_file(test_file)
            patterns["concurrency"].extend(conc_patterns)

        #AFTERMATH_METRIC: test_files_analyzed = len(test_files[:10])
        return patterns

    def _detect_timing_anomalies(self, statistics: dict[str, TestStatistics]) -> list[dict]:
        """
        Detect tests with timing anomalies (indicator of flakiness).

        #AFTERMATH_PATTERN_IDENTIFIED: timing_anomaly_detection
        """
        anomalies = []

        for test_name, stats in statistics.items():
            # High variance in duration is a flakiness indicator
            if stats.std_duration > stats.avg_duration * 0.5:  # 50% coefficient of variation
                anomalies.append({
                    "test_name": test_name,
                    "type": "high_duration_variance",
                    "avg_duration": stats.avg_duration,
                    "std_duration": stats.std_duration,
                    "coefficient_of_variation": stats.std_duration / stats.avg_duration
                })

            # Large difference between min and max duration
            if stats.max_duration > stats.min_duration * 3:  # 3x difference
                anomalies.append({
                    "test_name": test_name,
                    "type": "duration_range_anomaly",
                    "min_duration": stats.min_duration,
                    "max_duration": stats.max_duration,
                    "ratio": stats.max_duration / stats.min_duration
                })

        #AFTERMATH_METRIC: timing_anomalies_detected = len(anomalies)
        return anomalies

    def get_summary(self) -> dict[str, Any]:
        """
        Generate detector summary.

        #AFTERMATH_METRIC: detector_summary_generated

        Returns:
            Summary dictionary
        """
        return {
            "repo_path": str(self.repo_path),
            "lookback_days": self.lookback_days,
            "pattern_matchers": ["performance", "concurrency"]
        }

        #AFTERMATH_LESSON_LEARNED: detector_patterns_identified
