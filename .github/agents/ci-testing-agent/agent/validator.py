"""
Coverage Delta Evaluator
Validates coverage improvements and identifies gaps.
"""
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


class CoverageValidator:
    """Validates test coverage and computes deltas."""

    def __init__(self, workspace: Path):
        """
        Initialize CoverageValidator.
        
        Args:
            workspace: Path to repository workspace
        """
        self.workspace = workspace

    def validate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate coverage meets target threshold.
        
        Args:
            task: Task dictionary containing:
                - baseline: Path to baseline coverage file (optional)
                - threshold: Target coverage threshold (default: 85)
                - modules: List of modules to validate (optional)
        
        Returns:
            Dictionary with:
                - status: 'success', 'below_threshold', or 'error'
                - baseline_coverage: Baseline coverage percentage
                - current_coverage: Current coverage percentage
                - delta: Coverage delta (current - baseline)
                - threshold: Target threshold
                - meets_threshold: Boolean indicating if threshold is met
                - gaps: List of coverage gaps
        """
        baseline_file = task.get("baseline", "baseline_coverage.txt")
        target_threshold = task.get("threshold", 85)
        modules = task.get("modules", [])

        try:
            # Parse baseline coverage
            baseline = self._parse_baseline(baseline_file)

            # Run coverage analysis
            current = self._run_coverage(modules)

            # Compute delta
            delta = self._compute_delta(baseline, current)

            # Validate threshold
            meets_threshold = current["total"] >= target_threshold

            # Identify gaps
            gaps = self._identify_gaps(current, target_threshold)

            return {
                "status": "success" if meets_threshold else "below_threshold",
                "baseline_coverage": baseline["total"],
                "current_coverage": current["total"],
                "delta": delta,
                "threshold": target_threshold,
                "meets_threshold": meets_threshold,
                "gaps": gaps,
                "module_coverage": current.get("modules", {}),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "baseline_coverage": 0.0,
                "current_coverage": 0.0,
                "delta": 0.0,
                "threshold": target_threshold,
                "meets_threshold": False,
                "gaps": [],
            }

    def _parse_baseline(self, baseline_file: str) -> Dict[str, Any]:
        """
        Parse baseline coverage report file.
        
        Args:
            baseline_file: Path to baseline coverage file
        
        Returns:
            Dictionary with coverage data
        """
        baseline_path = self.workspace / baseline_file

        if not baseline_path.exists():
            # No baseline - return 0
            return {"total": 0.0, "modules": {}}

        try:
            with open(baseline_path) as f:
                content = f.read()

                # Parse coverage percentage from output
                # Format: "TOTAL    1234    567    54%"
                for line in content.splitlines():
                    if "TOTAL" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            coverage_str = parts[-1].rstrip("%")
                            try:
                                coverage = float(coverage_str)
                                return {"total": coverage, "modules": {}}
                            except ValueError:
                                pass

        except (FileNotFoundError, IOError, json.JSONDecodeError, ValueError):
            # Return default if baseline parsing fails
            pass

        return {"total": 0.0, "modules": {}}

    def _run_coverage(self, modules: List[str]) -> Dict[str, Any]:
        """
        Run coverage analysis on current codebase.
        
        Args:
            modules: List of modules to analyze
        
        Returns:
            Dictionary with coverage data
        """
        # Build coverage command
        cmd = ["pytest", "--cov=src", "--cov-report=json", "--cov-report=term"]

        # Add module filters
        if modules:
            for module in modules:
                cmd.append(f"--cov={module}")

        try:
            result = subprocess.run(
                cmd, cwd=self.workspace, capture_output=True, text=True, timeout=300
            )

            # Parse JSON coverage report
            coverage_json = self.workspace / "coverage.json"
            if coverage_json.exists():
                with open(coverage_json) as f:
                    data = json.load(f)
                    total_coverage = data["totals"]["percent_covered"]

                    # Extract per-module coverage
                    module_coverage = {}
                    for file_path, file_data in data.get("files", {}).items():
                        module_coverage[file_path] = file_data["summary"][
                            "percent_covered"
                        ]

                    return {"total": total_coverage, "modules": module_coverage}

            # Fallback: parse terminal output
            for line in result.stdout.splitlines():
                if "TOTAL" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        coverage_str = parts[-1].rstrip("%")
                        try:
                            coverage = float(coverage_str)
                            return {"total": coverage, "modules": {}}
                        except ValueError:
                            pass

        except subprocess.TimeoutExpired:
            # Return default if coverage command times out
            pass
        except (FileNotFoundError, IOError, json.JSONDecodeError, subprocess.CalledProcessError):
            # Return default if coverage report or runner is unavailable/malformed
            pass

        return {"total": 0.0, "modules": {}}

    def _compute_delta(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> float:
        """
        Compute coverage delta.
        
        Args:
            baseline: Baseline coverage data
            current: Current coverage data
        
        Returns:
            Coverage delta as float
        """
        return current["total"] - baseline["total"]

    def _identify_gaps(
        self, current: Dict[str, Any], threshold: float
    ) -> List[str]:
        """
        Identify modules below coverage threshold.
        
        Args:
            current: Current coverage data
            threshold: Target threshold
        
        Returns:
            List of coverage gap descriptions
        """
        gaps = []

        # Check overall coverage
        if current["total"] < threshold:
            gap = threshold - current["total"]
            gaps.append(
                f"Overall coverage {current['total']:.2f}% is {gap:.2f}% below target {threshold}%"
            )

        # Check per-module coverage
        for module, coverage in current.get("modules", {}).items():
            if coverage < threshold:
                gap = threshold - coverage
                gaps.append(
                    f"Module {module}: {coverage:.2f}% coverage ({gap:.2f}% below target)"
                )

        return gaps

    def generate_coverage_report(self) -> Path:
        """
        Generate comprehensive coverage report.
        
        Returns:
            Path to generated report
        """
        report_dir = self.workspace / ".reports" / "coverage"
        report_dir.mkdir(parents=True, exist_ok=True)

        # Generate HTML coverage report
        subprocess.run(
            [
                "pytest",
                "--cov=src",
                f"--cov-report=html:{report_dir}",
                "--cov-report=term",
            ],
            cwd=self.workspace,
        )

        return report_dir / "index.html"
