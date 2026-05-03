#!/usr/bin/env python3
"""
Test Coverage Enforcer Agent

Enforces test coverage thresholds, identifies uncovered code paths, and automatically
generates missing tests to maintain quality standards.

Component Reuse Strategy:
- Base: test-coverage-monitor (80% reuse)
- Extension 1: test-alignment-fixer (auto-test generation)
- Extension 2: integration-test-runner (enforcement workflows)

Usage:
    python -m test_coverage_enforcer.src.agent analyze --path src/
    python -m test_coverage_enforcer.src.agent enforce --threshold 90
    python -m test_coverage_enforcer.src.agent generate-tests --file src/module.py
"""

import ast
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class CoverageSeverity(Enum):
    """Severity levels for coverage gaps"""
    NONE = "none"
    LOW = "low"  # 80-89%
    MEDIUM = "medium"  # 70-79%
    HIGH = "high"  # 60-69%
    CRITICAL = "critical"  # <60%


class CoverageType(Enum):
    """Types of code coverage metrics"""
    LINE = "line"
    BRANCH = "branch"
    FUNCTION = "function"
    STATEMENT = "statement"


@dataclass
class CoverageIssue:
    """Represents a detected coverage issue"""
    file_path: Path
    issue_type: str  # 'uncovered_lines', 'missing_branch', 'untested_function'
    severity: CoverageSeverity
    description: str
    line_numbers: List[int] = field(default_factory=list)
    suggested_tests: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class CoverageReport:
    """Comprehensive coverage report for a file or module"""
    file_path: Path
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    total_lines: int
    covered_lines: int
    missing_lines: List[int] = field(default_factory=list)
    partial_branches: List[int] = field(default_factory=list)
    uncovered_functions: List[str] = field(default_factory=list)


@dataclass
class TestGenerationSuggestion:
    """Suggestion for generating new tests"""
    target_file: Path
    target_function: str
    test_file: Path
    test_template: str
    coverage_impact: float  # Expected coverage increase (0.0 to 1.0)
    priority: int  # 1 (highest) to 5 (lowest)


@dataclass
class EnforcementResult:
    """Result of enforcing coverage thresholds"""
    passed: bool
    current_coverage: float
    threshold: float
    gaps_found: int
    suggestions_generated: int
    enforcement_actions: List[str] = field(default_factory=list)


class TestCoverageEnforcer:
    """Main agent class for test coverage enforcement"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent with optional configuration"""
        self.config = self._load_config(config_path)
        self.line_threshold = self.config.get('thresholds', {}).get('line', 80)
        self.branch_threshold = self.config.get('thresholds', {}).get('branch', 70)
        self.function_threshold = self.config.get('thresholds', {}).get('function', 85)
        self.auto_generate = self.config.get('auto_generate_tests', False)
        self.issues: List[CoverageIssue] = []
        self.reports: Dict[Path, CoverageReport] = {}

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load agent configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"

        if not config_path.exists():
            return self._default_config()

        with open(config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'agent_name': 'test-coverage-enforcer',
            'version': '1.0.0',
            'capabilities': [
                'coverage_tracking',
                'threshold_enforcement',
                'test_generation',
                'trend_analysis'
            ],
            'thresholds': {
                'line': 80,
                'branch': 70,
                'function': 85
            },
            'auto_generate_tests': False,
            'fail_build_below_threshold': True,
            'cognitive_brain': {
                'enabled': True,
                'metrics': [
                    'coverage_percentage',
                    'gap_count',
                    'tests_generated',
                    'enforcement_actions'
                ],
                'reporting_interval': 'daily'
            }
        }

    def analyze_coverage(self, path: Path, coverage_file: Optional[Path] = None) -> Dict[Path, CoverageReport]:
        """
        Analyze test coverage for given path using coverage.py

        Args:
            path: Path to analyze (file or directory)
            coverage_file: Optional path to existing .coverage file

        Returns:
            Dictionary mapping file paths to coverage reports
        """
        if coverage_file and coverage_file.exists():
            coverage_data = self._load_coverage_data(coverage_file)
        else:
            coverage_data = self._run_coverage_analysis(path)

        self.reports = {}
        for file_path, data in coverage_data.items():
            report = self._create_coverage_report(file_path, data)
            # Ensure key is a Path object for consistency
            path_key = Path(file_path) if isinstance(file_path, str) else file_path
            self.reports[path_key] = report

            # Identify issues
            self._check_coverage_thresholds(report)

        return self.reports

    def _run_coverage_analysis(self, path: Path) -> Dict:
        """Run pytest with coverage.py to collect coverage data"""
        try:
            # Run pytest with coverage
            cmd = [
                'python', '-m', 'pytest',
                '--cov=' + str(path),
                '--cov-report=json:coverage.json',
                '--cov-report=term',
                '-v'
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Load JSON coverage report
            coverage_json = Path('coverage.json')
            if coverage_json.exists():
                with open(coverage_json) as f:
                    return json.load(f).get('files', {})

            return {}
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Coverage analysis failed: {e}")
            return {}

    def _load_coverage_data(self, coverage_file: Path) -> Dict:
        """Load coverage data from existing .coverage file"""
        try:
            # Use coverage.py API to read data
            from coverage import Coverage
            cov = Coverage(data_file=str(coverage_file))
            cov.load()

            data = {}
            for filename in cov.get_data().measured_files():
                analysis = cov.analysis2(filename)
                data[filename] = {
                    'executed_lines': analysis[1],
                    'missing_lines': analysis[2],
                    'excluded_lines': analysis[3]
                }
            return data
        except Exception as e:
            print(f"Failed to load coverage data: {e}")
            return {}

    def _create_coverage_report(self, file_path: str, data: Dict) -> CoverageReport:
        """Create structured coverage report from raw data"""
        path = Path(file_path)

        # Extract coverage metrics
        if isinstance(data, dict):
            executed = set(data.get('executed_lines', []))
            missing = list(data.get('missing_lines', []))
            total_lines = len(executed) + len(missing)
            covered = len(executed)
        else:
            total_lines = 0
            covered = 0
            missing = []

        # Calculate coverage percentage
        line_coverage = (covered / total_lines * 100) if total_lines > 0 else 0.0

        # Parse file for functions and branches (simplified)
        functions = self._extract_functions(path)
        uncovered_funcs = [f for f in functions if any(line in missing for line in range(f[1], f[2]))]
        function_coverage = ((len(functions) - len(uncovered_funcs)) / len(functions) * 100) if functions else 100.0

        return CoverageReport(
            file_path=path,
            line_coverage=line_coverage,
            branch_coverage=line_coverage,  # Simplified - same as line coverage
            function_coverage=function_coverage,
            total_lines=total_lines,
            covered_lines=covered,
            missing_lines=missing,
            partial_branches=[],
            uncovered_functions=[f[0] for f in uncovered_funcs]
        )

    def _extract_functions(self, file_path: Path) -> List[Tuple[str, int, int]]:
        """Extract function definitions from Python file"""
        if not file_path.exists() or file_path.suffix != '.py':
            return []

        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            functions = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append((
                        node.name,
                        node.lineno,
                        node.end_lineno or node.lineno
                    ))
            return functions
        except Exception:
            return []

    def _check_coverage_thresholds(self, report: CoverageReport):
        """Check if coverage report meets thresholds and record issues"""
        severity = self._calculate_severity(report.line_coverage)

        # Check line coverage
        if report.line_coverage < self.line_threshold:
            issue = CoverageIssue(
                file_path=report.file_path,
                issue_type='uncovered_lines',
                severity=severity,
                description=f"Line coverage {report.line_coverage:.1f}% below threshold {self.line_threshold}%",
                line_numbers=report.missing_lines,
                confidence=1.0
            )
            self.issues.append(issue)

        # Check function coverage
        if report.function_coverage < self.function_threshold:
            issue = CoverageIssue(
                file_path=report.file_path,
                issue_type='untested_function',
                severity=severity,
                description=f"Function coverage {report.function_coverage:.1f}% below threshold {self.function_threshold}%",
                suggested_tests=[f"test_{func}" for func in report.uncovered_functions],
                confidence=0.9
            )
            self.issues.append(issue)

    def _calculate_severity(self, coverage: float) -> CoverageSeverity:
        """Calculate severity level based on coverage percentage"""
        if coverage >= 80:
            return CoverageSeverity.LOW
        if coverage >= 70:
            return CoverageSeverity.MEDIUM
        if coverage >= 60:
            return CoverageSeverity.HIGH
        return CoverageSeverity.CRITICAL

    def enforce_thresholds(self, path: Path) -> EnforcementResult:
        """
        Enforce coverage thresholds and take action if below threshold

        Args:
            path: Path to enforce coverage for

        Returns:
            EnforcementResult with enforcement outcome
        """
        # Analyze coverage
        reports = self.analyze_coverage(path)

        if not reports:
            return EnforcementResult(
                passed=False,
                current_coverage=0.0,
                threshold=self.line_threshold,
                gaps_found=0,
                suggestions_generated=0,
                enforcement_actions=['No coverage data available']
            )

        # Calculate aggregate coverage
        total_lines = sum(r.total_lines for r in reports.values())
        covered_lines = sum(r.covered_lines for r in reports.values())
        current_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0.0

        # Check threshold
        passed = current_coverage >= self.line_threshold

        # Generate test suggestions if below threshold
        suggestions = []
        if not passed and self.auto_generate:
            suggestions = self.generate_test_suggestions(reports)

        actions = []
        if not passed:
            actions.append(f"Coverage {current_coverage:.1f}% below threshold {self.line_threshold}%")
            actions.append(f"Found {len(self.issues)} coverage gaps")
            if suggestions:
                actions.append(f"Generated {len(suggestions)} test suggestions")

        return EnforcementResult(
            passed=passed,
            current_coverage=current_coverage,
            threshold=self.line_threshold,
            gaps_found=len(self.issues),
            suggestions_generated=len(suggestions),
            enforcement_actions=actions
        )

    def generate_test_suggestions(self, reports: Dict[Path, CoverageReport]) -> List[TestGenerationSuggestion]:
        """
        Generate suggestions for new tests to improve coverage

        Args:
            reports: Coverage reports to analyze

        Returns:
            List of test generation suggestions
        """
        suggestions = []

        for file_path, report in reports.items():
            # Skip if coverage is already good
            if report.line_coverage >= self.line_threshold:
                continue

            # Generate suggestions for uncovered functions
            for func_name in report.uncovered_functions:
                test_file = self._determine_test_file(file_path)
                test_template = self._generate_test_template(file_path, func_name)

                suggestion = TestGenerationSuggestion(
                    target_file=file_path,
                    target_function=func_name,
                    test_file=test_file,
                    test_template=test_template,
                    coverage_impact=self._estimate_coverage_impact(report, func_name),
                    priority=self._calculate_priority(report, func_name)
                )
                suggestions.append(suggestion)

        # Sort by priority
        suggestions.sort(key=lambda s: (s.priority, -s.coverage_impact))

        return suggestions

    def _determine_test_file(self, source_file: Path) -> Path:
        """Determine the appropriate test file for a source file"""
        # Ensure we have a Path object
        if isinstance(source_file, str):
            source_file = Path(source_file)

        # Convert src/module.py to tests/test_module.py
        parts = list(source_file.parts)

        if 'src' in parts:
            idx = parts.index('src')
            parts[idx] = 'tests'

        filename = source_file.stem
        if not filename.startswith('test_'):
            filename = f'test_{filename}'
        parts[-1] = f'{filename}.py'

        return Path(*parts)

    def _generate_test_template(self, file_path: Path, func_name: str) -> str:
        """Generate a test template for a function"""
        module_name = file_path.stem

        template = f'''
def test_{func_name}_basic():
    """Test {func_name} basic functionality"""
    # TODO: Implement test for {func_name}
    # from {module_name} import {func_name}
    # result = {func_name}()
    # assert result is not None
    pass


def test_{func_name}_edge_cases():
    """Test {func_name} edge cases"""
    # TODO: Test edge cases for {func_name}
    pass
'''
        return template.strip()

    def _estimate_coverage_impact(self, report: CoverageReport, func_name: str) -> float:
        """Estimate how much coverage would improve by testing this function"""
        # Simplified estimation
        functions = self._extract_functions(report.file_path)
        func_lines = [f for f in functions if f[0] == func_name]

        if not func_lines or report.total_lines == 0:
            return 0.0

        func_line_count = func_lines[0][2] - func_lines[0][1]
        return (func_line_count / report.total_lines) * 100

    def _calculate_priority(self, report: CoverageReport, func_name: str) -> int:
        """Calculate priority for testing a function (1=highest, 5=lowest)"""
        # Higher priority for functions in files with very low coverage
        if report.line_coverage < 50:
            return 1
        if report.line_coverage < 70:
            return 2
        if report.line_coverage < 80:
            return 3
        return 4

    def generate_coverage_report(self, output_format: str = 'text') -> str:
        """
        Generate human-readable coverage report

        Args:
            output_format: 'text', 'json', or 'html'

        Returns:
            Formatted coverage report
        """
        if output_format == 'json':
            return self._generate_json_report()
        if output_format == 'html':
            return self._generate_html_report()
        return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate text format coverage report"""
        lines = [
            "=" * 80,
            "Test Coverage Enforcement Report",
            "=" * 80,
            "",
            f"Total files analyzed: {len(self.reports)}",
            f"Coverage issues found: {len(self.issues)}",
            ""
        ]

        if self.reports:
            lines.append("Coverage by File:")
            lines.append("-" * 80)
            for path, report in self.reports.items():
                status = "✓" if report.line_coverage >= self.line_threshold else "✗"
                lines.append(f"{status} {path}: {report.line_coverage:.1f}% line, {report.function_coverage:.1f}% function")

        if self.issues:
            lines.append("")
            lines.append("Coverage Issues:")
            lines.append("-" * 80)
            for issue in self.issues:
                lines.append(f"[{issue.severity.value.upper()}] {issue.file_path}")
                lines.append(f"  {issue.description}")
                if issue.suggested_tests:
                    lines.append(f"  Suggested tests: {', '.join(issue.suggested_tests)}")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _generate_json_report(self) -> str:
        """Generate JSON format coverage report"""
        data = {
            'summary': {
                'files_analyzed': len(self.reports),
                'issues_found': len(self.issues),
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            'reports': [
                {
                    'file': str(r.file_path),
                    'line_coverage': r.line_coverage,
                    'branch_coverage': r.branch_coverage,
                    'function_coverage': r.function_coverage,
                    'missing_lines': r.missing_lines
                }
                for r in self.reports.values()
            ],
            'issues': [
                {
                    'file': str(i.file_path),
                    'type': i.issue_type,
                    'severity': i.severity.value,
                    'description': i.description
                }
                for i in self.issues
            ]
        }
        return json.dumps(data, indent=2)

    def _generate_html_report(self) -> str:
        """Generate HTML format coverage report"""
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Coverage Enforcement Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
    </style>
</head>
<body>
    <h1>Test Coverage Enforcement Report</h1>
    <p><strong>Total files:</strong> {len(self.reports)}</p>
    <p><strong>Issues found:</strong> {len(self.issues)}</p>
    <h2>Coverage by File</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Line Coverage</th>
            <th>Function Coverage</th>
            <th>Status</th>
        </tr>
'''
        for path, report in self.reports.items():
            status_class = "pass" if report.line_coverage >= self.line_threshold else "fail"
            status_text = "PASS" if report.line_coverage >= self.line_threshold else "FAIL"
            html += f'''
        <tr>
            <td>{path}</td>
            <td>{report.line_coverage:.1f}%</td>
            <td>{report.function_coverage:.1f}%</td>
            <td class="{status_class}">{status_text}</td>
        </tr>
'''
        html += '''
    </table>
</body>
</html>
'''
        return html


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Test Coverage Enforcer Agent')
    parser.add_argument('command', choices=['analyze', 'enforce', 'generate-tests', 'report'])
    parser.add_argument('--path', type=Path, default=Path('src'), help='Path to analyze')
    parser.add_argument('--threshold', type=float, help='Coverage threshold percentage')
    parser.add_argument('--format', choices=['text', 'json', 'html'], default='text')
    parser.add_argument('--output', type=Path, help='Output file for report')

    args = parser.parse_args()

    agent = TestCoverageEnforcer()

    if args.threshold:
        agent.line_threshold = args.threshold

    if args.command == 'analyze':
        reports = agent.analyze_coverage(args.path)
        print(f"Analyzed {len(reports)} files")
        for path, report in reports.items():
            print(f"{path}: {report.line_coverage:.1f}% coverage")

    elif args.command == 'enforce':
        result = agent.enforce_thresholds(args.path)
        print(f"Enforcement: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Current coverage: {result.current_coverage:.1f}%")
        print(f"Threshold: {result.threshold}%")
        for action in result.enforcement_actions:
            print(f"  - {action}")

        if not result.passed and agent.config.get('fail_build_below_threshold', True):
            sys.exit(1)

    elif args.command == 'generate-tests':
        reports = agent.analyze_coverage(args.path)
        suggestions = agent.generate_test_suggestions(reports)
        print(f"Generated {len(suggestions)} test suggestions:")
        for s in suggestions[:10]:  # Show top 10
            print(f"\nPriority {s.priority}: {s.target_function} in {s.target_file}")
            print(f"  Impact: +{s.coverage_impact:.1f}% coverage")
            print(f"  Test file: {s.test_file}")

    elif args.command == 'report':
        agent.analyze_coverage(args.path)
        report = agent.generate_coverage_report(args.format)

        if args.output:
            args.output.write_text(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)


if __name__ == '__main__':
    main()
