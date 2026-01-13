"""
Fix Verification System for Auto-Remediation.

This module provides comprehensive validation and testing of automated fixes
before and after application, including regression detection.
"""

import ast
import difflib
import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class PreFixSnapshot:
    """Snapshot of system state before applying fix."""

    file_hash: str
    file_content: str
    test_results: Dict[str, Any]
    metrics: Dict[str, float]
    timestamp: str


@dataclass
class PostFixSnapshot:
    """Snapshot of system state after applying fix."""

    file_hash: str
    file_content: str
    test_results: Dict[str, Any]
    metrics: Dict[str, float]
    timestamp: str


@dataclass
class VerificationResult:
    """Result of fix verification."""

    success: bool
    pre_snapshot: PreFixSnapshot
    post_snapshot: PostFixSnapshot
    regressions_detected: List[str]
    improvements: List[str]
    confidence_score: float
    explanation: str


class FixVerifier:
    """
    Verifies automated fixes before and after application.

    Features:
    - Pre-fix state capture
    - Post-fix validation
    - Regression testing
    - Success metrics
    """

    def __init__(self, test_command: str = "pytest -x"):
        self.test_command = test_command
        self.verification_history: List[VerificationResult] = []

    def verify_fix(self, file_path: str, original_code: str, fixed_code: str) -> VerificationResult:
        """
        Verify a fix by capturing before/after state and running tests.

        Args:
            file_path: Path to file being fixed
            original_code: Original code before fix
            fixed_code: Fixed code after fix

        Returns:
            VerificationResult with validation outcome
        """
        # Capture pre-fix snapshot
        pre_snapshot = self._capture_pre_fix_snapshot(file_path, original_code)

        # Apply fix temporarily
        self._apply_fix_temp(file_path, fixed_code)

        # Capture post-fix snapshot
        post_snapshot = self._capture_post_fix_snapshot(file_path, fixed_code)

        # Detect regressions
        regressions = self._detect_regressions(pre_snapshot, post_snapshot)

        # Detect improvements
        improvements = self._detect_improvements(pre_snapshot, post_snapshot)

        # Calculate confidence score
        confidence = self._calculate_confidence(pre_snapshot, post_snapshot, regressions)

        # Determine success
        success = len(regressions) == 0 and post_snapshot.test_results.get("passed", False)

        # Generate explanation
        explanation = self._generate_explanation(regressions, improvements, success)

        result = VerificationResult(
            success=success,
            pre_snapshot=pre_snapshot,
            post_snapshot=post_snapshot,
            regressions_detected=regressions,
            improvements=improvements,
            confidence_score=confidence,
            explanation=explanation,
        )

        self.verification_history.append(result)
        return result

    def _capture_pre_fix_snapshot(self, file_path: str, code: str) -> PreFixSnapshot:
        """Capture system state before applying fix."""
        file_hash = self._calculate_hash(code)

        # Run tests before fix
        test_results = self._run_tests()

        # Collect metrics
        metrics = self._collect_metrics(code)

        return PreFixSnapshot(
            file_hash=file_hash,
            file_content=code,
            test_results=test_results,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
        )

    def _capture_post_fix_snapshot(self, file_path: str, code: str) -> PostFixSnapshot:
        """Capture system state after applying fix."""
        file_hash = self._calculate_hash(code)

        # Run tests after fix
        test_results = self._run_tests()

        # Collect metrics
        metrics = self._collect_metrics(code)

        return PostFixSnapshot(
            file_hash=file_hash,
            file_content=code,
            test_results=test_results,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
        )

    def _apply_fix_temp(self, file_path: str, fixed_code: str) -> None:
        """Temporarily apply fix to file."""
        path = Path(file_path)
        if path.exists():
            with open(path, "w", encoding="utf-8") as f:
                f.write(fixed_code)

    def _run_tests(self) -> Dict[str, Any]:
        """Run test suite and collect results."""
        try:
            result = subprocess.run(
                self.test_command.split(),
                capture_output=True,
                text=True,
                timeout=60,
            )

            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout[:500],  # Limit output size
                "stderr": result.stderr[:500],
            }

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Test timeout"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _collect_metrics(self, code: str) -> Dict[str, float]:
        """Collect code quality metrics."""
        metrics = {}

        # Lines of code
        metrics["lines_of_code"] = len(code.split("\n"))

        # Cyclomatic complexity (simplified)
        metrics["complexity"] = self._calculate_complexity(code)

        # Security score (simplified)
        metrics["security_score"] = self._calculate_security_score(code)

        return metrics

    def _calculate_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity."""
        try:
            tree = ast.parse(code)
            complexity = 1

            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1

            return float(complexity)

        except SyntaxError:
            return 999.0  # High complexity for invalid syntax

    def _calculate_security_score(self, code: str) -> float:
        """Calculate simple security score (0-100)."""
        score = 100.0

        # Deduct points for risky patterns
        risky_patterns = [
            ("shell=True", 10),
            ("eval(", 15),
            ("exec(", 15),
            ("pickle.loads", 10),
            ("md5(", 5),
            ("sha1(", 5),
        ]

        for pattern, deduction in risky_patterns:
            if pattern in code:
                score -= deduction

        return max(0.0, score)

    def _detect_regressions(self, pre: PreFixSnapshot, post: PostFixSnapshot) -> List[str]:
        """Detect any regressions introduced by fix."""
        regressions = []

        # Check if tests broke
        if pre.test_results.get("passed") and not post.test_results.get("passed"):
            regressions.append("Tests that previously passed now fail")

        # Check if complexity increased significantly
        pre_complexity = pre.metrics.get("complexity", 0)
        post_complexity = post.metrics.get("complexity", 0)
        if post_complexity > pre_complexity * 1.5:
            regressions.append(f"Complexity increased from {pre_complexity} to {post_complexity}")

        # Check if security score decreased
        pre_security = pre.metrics.get("security_score", 0)
        post_security = post.metrics.get("security_score", 0)
        if post_security < pre_security - 5:
            regressions.append(f"Security score decreased from {pre_security} to {post_security}")

        return regressions

    def _detect_improvements(self, pre: PreFixSnapshot, post: PostFixSnapshot) -> List[str]:
        """Detect improvements made by fix."""
        improvements = []

        # Check if tests started passing
        if not pre.test_results.get("passed") and post.test_results.get("passed"):
            improvements.append("Previously failing tests now pass")

        # Check if security score improved
        pre_security = pre.metrics.get("security_score", 0)
        post_security = post.metrics.get("security_score", 0)
        if post_security > pre_security + 5:
            improvements.append(f"Security score improved from {pre_security:.1f} to {post_security:.1f}")

        # Check if complexity decreased
        pre_complexity = pre.metrics.get("complexity", 999)
        post_complexity = post.metrics.get("complexity", 999)
        if post_complexity < pre_complexity * 0.8:
            improvements.append(f"Complexity reduced from {pre_complexity} to {post_complexity}")

        return improvements

    def _calculate_confidence(
        self, pre: PreFixSnapshot, post: PostFixSnapshot, regressions: List[str]
    ) -> float:
        """Calculate confidence score for fix (0-1)."""
        confidence = 1.0

        # Deduct for regressions
        confidence -= len(regressions) * 0.3

        # Deduct if tests don't pass
        if not post.test_results.get("passed"):
            confidence -= 0.4

        # Bonus for security improvement
        pre_security = pre.metrics.get("security_score", 0)
        post_security = post.metrics.get("security_score", 0)
        if post_security > pre_security:
            confidence += 0.1

        return max(0.0, min(1.0, confidence))

    def _generate_explanation(self, regressions: List[str], improvements: List[str], success: bool) -> str:
        """Generate human-readable explanation of verification."""
        if success:
            explanation = "✅ Fix verified successfully\n\n"
        else:
            explanation = "❌ Fix verification failed\n\n"

        if improvements:
            explanation += "Improvements:\n"
            for improvement in improvements:
                explanation += f"  • {improvement}\n"
            explanation += "\n"

        if regressions:
            explanation += "Regressions detected:\n"
            for regression in regressions:
                explanation += f"  • {regression}\n"
            explanation += "\n"

        if not improvements and not regressions:
            explanation += "No significant changes detected\n"

        return explanation

    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def generate_diff(self, original: str, fixed: str) -> str:
        """Generate unified diff between original and fixed code."""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            fixed.splitlines(keepends=True),
            fromfile="original",
            tofile="fixed",
            lineterm="",
        )
        return "".join(diff)

    def save_verification_report(self, result: VerificationResult, output_path: str) -> None:
        """Save verification report to file."""
        report = {
            "success": result.success,
            "confidence_score": result.confidence_score,
            "explanation": result.explanation,
            "regressions": result.regressions_detected,
            "improvements": result.improvements,
            "pre_snapshot": {
                "file_hash": result.pre_snapshot.file_hash,
                "test_passed": result.pre_snapshot.test_results.get("passed"),
                "metrics": result.pre_snapshot.metrics,
                "timestamp": result.pre_snapshot.timestamp,
            },
            "post_snapshot": {
                "file_hash": result.post_snapshot.file_hash,
                "test_passed": result.post_snapshot.test_results.get("passed"),
                "metrics": result.post_snapshot.metrics,
                "timestamp": result.post_snapshot.timestamp,
            },
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def get_success_rate(self) -> float:
        """Calculate overall success rate of verified fixes."""
        if not self.verification_history:
            return 0.0

        successful = sum(1 for v in self.verification_history if v.success)
        return successful / len(self.verification_history)


if __name__ == "__main__":
    # Example usage
    verifier = FixVerifier()

    original_code = 'subprocess.run("ls", shell=True)'
    fixed_code = 'subprocess.run(["ls"], shell=False)'

    result = verifier.verify_fix("example.py", original_code, fixed_code)

    print(f"Success: {result.success}")
    print(f"Confidence: {result.confidence_score:.2%}")
    print(f"\n{result.explanation}")

    if result.regressions_detected:
        print("Regressions:")
        for reg in result.regressions_detected:
            print(f"  - {reg}")

    if result.improvements:
        print("Improvements:")
        for imp in result.improvements:
            print(f"  - {imp}")
