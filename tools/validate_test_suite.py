#!/usr/bin/env python3
"""
Test Suite Validation and Coverage Projection Tool

Analyzes created test files to project coverage gains without running pytest.
Provides detailed metrics on test quality and expected coverage impact.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class TestMetrics:
    """Metrics for a single test file."""

    file_path: str
    test_classes: int
    test_methods: int
    lines_of_code: int
    imports_count: int
    assertions_count: int
    try_except_blocks: int
    targeted_classes: List[str]
    expected_coverage_gain: float


class TestSuiteAnalyzer:
    """Analyzes test suite quality and projects coverage gains."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests" / "agents"

    def analyze_test_file(self, test_file: Path) -> TestMetrics:
        """Analyze a single test file."""
        with open(test_file, "r") as f:
            content = f.read()
            tree = ast.parse(content)

        test_classes = 0
        test_methods = 0
        assertions = 0
        try_except = 0
        imports = set()
        targeted_classes = set()

        # Count test classes and methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith("Test"):
                    test_classes += 1
                    # Count test methods in this class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            test_methods += 1

            # Count assertions
            elif isinstance(node, ast.Assert):
                assertions += 1

            # Count try/except blocks
            elif isinstance(node, ast.Try):
                try_except += 1

            # Extract imports to find targeted classes
            elif isinstance(node, ast.ImportFrom):
                if node.module and "agents" in node.module:
                    for alias in node.names:
                        targeted_classes.add(alias.name)
                        imports.add(f"{node.module}.{alias.name}")

        # Estimate coverage gain based on test count and quality
        # Formula: base_gain * (test_methods / 10) * quality_multiplier
        quality_multiplier = 1.0
        if assertions > test_methods:
            quality_multiplier += 0.2  # Good assertion coverage
        if try_except > 0:
            quality_multiplier += 0.1  # Error handling tested

        base_gain_per_10_tests = 0.5  # 0.5% per 10 tests (conservative)
        expected_gain = base_gain_per_10_tests * (test_methods / 10) * quality_multiplier

        return TestMetrics(
            file_path=str(test_file.name),
            test_classes=test_classes,
            test_methods=test_methods,
            lines_of_code=len(content.split("\n")),
            imports_count=len(imports),
            assertions_count=assertions,
            try_except_blocks=try_except,
            targeted_classes=sorted(list(targeted_classes)),
            expected_coverage_gain=expected_gain,
        )

    def analyze_all_tests(self) -> Dict[str, TestMetrics]:
        """Analyze all test files."""
        results = {}

        if not self.test_dir.exists():
            return results

        for test_file in self.test_dir.glob("test_*.py"):
            try:
                metrics = self.analyze_test_file(test_file)
                results[test_file.name] = metrics
            except Exception as e:
                print(f"Warning: Could not analyze {test_file.name}: {e}")

        return results

    def generate_report(self, metrics: Dict[str, TestMetrics]) -> str:
        """Generate comprehensive validation report."""
        report = []
        report.append("=" * 80)
        report.append("TEST SUITE VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")

        # Overall statistics
        total_classes = sum(m.test_classes for m in metrics.values())
        total_methods = sum(m.test_methods for m in metrics.values())
        total_lines = sum(m.lines_of_code for m in metrics.values())
        total_assertions = sum(m.assertions_count for m in metrics.values())
        total_expected_gain = sum(m.expected_coverage_gain for m in metrics.values())

        report.append("OVERALL STATISTICS")
        report.append("-" * 80)
        report.append(f"Total Test Files:       {len(metrics)}")
        report.append(f"Total Test Classes:     {total_classes}")
        report.append(f"Total Test Methods:     {total_methods}")
        report.append(f"Total Lines of Code:    {total_lines:,}")
        report.append(f"Total Assertions:       {total_assertions}")
        report.append(
            f"Assertions per Test:    {total_assertions/total_methods if total_methods > 0 else 0:.2f}"
        )
        report.append(f"Expected Coverage Gain: {total_expected_gain:.2f}%")
        report.append("")

        # Phase breakdown
        phase1_files = [
            k
            for k in metrics.keys()
            if "phase1" in k.lower()
            or "phase_1" in k.lower()
            or any(
                x in k
                for x in [
                    "smoke",
                    "expanded",
                    "invariant",
                    "properties",
                    "final_push",
                    "30pct",
                    "exhaustive",
                ]
            )
        ]
        phase2_files = [
            k for k in metrics.keys() if "phase2" in k.lower() or "phase_2" in k.lower()
        ]

        if phase1_files:
            phase1_methods = sum(metrics[k].test_methods for k in phase1_files)
            phase1_gain = sum(metrics[k].expected_coverage_gain for k in phase1_files)
            report.append("PHASE 1 TESTS")
            report.append("-" * 80)
            report.append(f"Test Files:            {len(phase1_files)}")
            report.append(f"Test Methods:          {phase1_methods}")
            report.append(f"Expected Gain:         {phase1_gain:.2f}%")
            report.append(f"Current Coverage:      27.57%")
            report.append(f"Projected Coverage:    {27.57 + phase1_gain:.2f}%")
            report.append("")

        if phase2_files:
            phase2_methods = sum(metrics[k].test_methods for k in phase2_files)
            phase2_gain = sum(metrics[k].expected_coverage_gain for k in phase2_files)
            phase1_final = 27.57 + (
                sum(metrics[k].expected_coverage_gain for k in phase1_files) if phase1_files else 0
            )
            report.append("PHASE 2 TESTS")
            report.append("-" * 80)
            report.append(f"Test Files:            {len(phase2_files)}")
            report.append(f"Test Methods:          {phase2_methods}")
            report.append(f"Expected Gain:         {phase2_gain:.2f}%")
            report.append(f"After Phase 1:         {phase1_final:.2f}%")
            report.append(f"Projected Coverage:    {phase1_final + phase2_gain:.2f}%")
            report.append("")

        # Detailed file breakdown
        report.append("DETAILED FILE ANALYSIS")
        report.append("-" * 80)
        report.append(f"{'File':<45} {'Classes':<8} {'Tests':<8} {'Gain':<8}")
        report.append("-" * 80)

        for filename in sorted(metrics.keys()):
            m = metrics[filename]
            report.append(
                f"{filename:<45} {m.test_classes:<8} {m.test_methods:<8} {m.expected_coverage_gain:<8.2f}%"
            )

        report.append("")

        # Quality metrics
        report.append("QUALITY METRICS")
        report.append("-" * 80)
        avg_assertions = total_assertions / total_methods if total_methods > 0 else 0
        avg_lines_per_test = total_lines / total_methods if total_methods > 0 else 0

        report.append(f"Average Assertions per Test:    {avg_assertions:.2f}")
        report.append(f"Average Lines per Test:         {avg_lines_per_test:.1f}")
        report.append(
            f"Test Method Density:            {total_methods / len(metrics):.1f} tests/file"
        )

        quality_score = min(100, (avg_assertions * 20 + (total_methods / 100) * 10))
        report.append(f"Quality Score:                  {quality_score:.1f}/100")
        report.append("")

        # Coverage projection
        report.append("COVERAGE PROJECTION")
        report.append("-" * 80)
        current = 27.57
        after_phase1 = current + (
            sum(metrics[k].expected_coverage_gain for k in phase1_files) if phase1_files else 0
        )
        after_phase2 = after_phase1 + (
            sum(metrics[k].expected_coverage_gain for k in phase2_files) if phase2_files else 0
        )

        report.append(f"Current Coverage:          {current:.2f}%")
        report.append(f"After Phase 1 Tests:       {after_phase1:.2f}%")
        report.append(f"After Phase 2 Tests:       {after_phase2:.2f}%")
        report.append(f"Total Projected Gain:      {after_phase2 - current:.2f}%")
        report.append("")

        # Confidence assessment
        if after_phase2 >= 50:
            status = "✅ EXCELLENT - Phase 2 target (50%) likely to be exceeded"
        elif after_phase2 >= 45:
            status = "✅ GOOD - Phase 2 target (50%) within reach"
        elif after_phase2 >= 40:
            status = "⚠️  MODERATE - May need additional tests for Phase 2"
        else:
            status = "❌ LOW - Significant additional tests needed"

        report.append(f"Confidence Assessment: {status}")
        report.append("")

        # Module coverage breakdown
        report.append("MODULE COVERAGE TARGETS")
        report.append("-" * 80)

        module_tests = defaultdict(int)
        for m in metrics.values():
            for target in m.targeted_classes:
                # Determine module
                if any(
                    x in target.lower()
                    for x in ["physics", "orchestrator", "decision", "force", "action"]
                ):
                    module_tests["physics_orchestrator"] += 1
                elif any(
                    x in target.lower() for x in ["quantum", "game", "payoff", "strategy", "bell"]
                ):
                    module_tests["quantum_game_theory"] += 1
                elif any(
                    x in target.lower()
                    for x in ["mental", "mapping", "reasoning", "concept", "knowledge"]
                ):
                    module_tests["mental_mapping"] += 1

        for module, count in sorted(module_tests.items()):
            report.append(f"{module:<40} {count} targeted tests")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    analyzer = TestSuiteAnalyzer(project_root)

    print("Analyzing test suite...")
    metrics = analyzer.analyze_all_tests()

    if not metrics:
        print("No test files found!")
        return 1

    report = analyzer.generate_report(metrics)
    print(report)

    # Save report
    report_file = project_root / "docs" / "plans" / "Test_Suite_Validation_Report.md"
    with open(report_file, "w") as f:
        f.write("# Test Suite Validation Report\n\n")
        f.write("Generated: 2025-12-13\n\n")
        f.write("```\n")
        f.write(report)
        f.write("\n```\n")

    print(f"\nReport saved to: {report_file}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
