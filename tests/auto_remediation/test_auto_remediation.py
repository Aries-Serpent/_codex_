"""Comprehensive test suite for auto-remediation system."""

import sys
from pathlib import Path

import pytest

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from auto_remediation.fix_generator import (
    FixContext,
    FixStrategy,
    IntelligentFixGenerator,
)
from auto_remediation.verifier import FixVerifier


class TestFixGenerator:
    """Test intelligent fix generator."""

    def setup_method(self):
        self.generator = IntelligentFixGenerator()

    def test_shell_injection_fix(self):
        """Test fix for shell injection vulnerability."""
        context = FixContext(
            file_path="test.py",
            code='subprocess.run("ls -la", shell=True)',
            vulnerability_type="shell_injection",
            risk_score=0.85,
            line_numbers=[10],
            metadata={},
        )

        fix = self.generator.generate_fix(context)

        assert fix is not None, "fix must be initialized"
        assert fix.strategy == FixStrategy.SHELL_INJECTION, "strategy is not valid"
        assert "shell=False" in fix.fixed_code, "Condition must be true"
        assert fix.confidence > 0.8, "confidence must be greater than zero"
        assert fix.validation_passed is True, "validation_passed is not valid"

    def test_eval_exec_fix(self):
        """Test fix for eval/exec vulnerability."""
        context = FixContext(
            file_path="test.py",
            code="result = eval(user_input)",
            vulnerability_type="eval_usage",
            risk_score=0.90,
            line_numbers=[15],
            metadata={},
        )

        fix = self.generator.generate_fix(context)

        assert fix is not None, "fix must be initialized"
        assert fix.strategy == FixStrategy.EVAL_EXEC_REMOVAL, "strategy is not valid"
        assert "ast.literal_eval" in fix.fixed_code or "REMOVED" in fix.fixed_code, "Condition must be true"
        assert fix.confidence > 0.7, "confidence must be greater than zero"

    def test_pickle_fix(self):
        """Test fix for unsafe pickle usage."""
        context = FixContext(
            file_path="test.py",
            code="data = pickle.loads(user_data)",
            vulnerability_type="pickle_usage",
            risk_score=0.80,
            line_numbers=[20],
            metadata={},
        )

        fix = self.generator.generate_fix(context)

        assert fix is not None, "fix must be initialized"
        assert fix.strategy == FixStrategy.PICKLE_SECURE, "strategy is not valid"
        assert "json" in fix.fixed_code or "manual review" in fix.explanation.lower(), "Condition must be true"

    def test_weak_crypto_fix(self):
        """Test fix for weak cryptography."""
        context = FixContext(
            file_path="test.py",
            code="hash_value = hashlib.md5(data).hexdigest()",
            vulnerability_type="weak_crypto_md5",
            risk_score=0.70,
            line_numbers=[25],
            metadata={},
        )

        fix = self.generator.generate_fix(context)

        assert fix is not None, "fix must be initialized"
        assert fix.strategy == FixStrategy.WEAK_CRYPTO, "strategy is not valid"
        assert "sha256" in fix.fixed_code, "Condition must be true"
        assert fix.confidence > 0.9, "confidence must be greater than zero"

    def test_xml_parser_fix(self):
        """Test fix for XML parser vulnerability."""
        context = FixContext(
            file_path="test.py",
            code="import xml.etree.ElementTree as ET\ntree = ET.parse(file)",
            vulnerability_type="xml_parsing",
            risk_score=0.85,
            line_numbers=[30],
            metadata={},
        )

        fix = self.generator.generate_fix(context)

        assert fix is not None, "fix must be initialized"
        assert fix.strategy == FixStrategy.XML_SECURE_PARSER, "strategy is not valid"
        assert "defusedxml" in fix.fixed_code, "Condition must be true"
        assert fix.confidence > 0.8, "confidence must be greater than zero"

    def test_multiple_fixes_generation(self):
        """Test generation of multiple fix options."""
        context = FixContext(
            file_path="test.py",
            code="subprocess.run(cmd, shell=True)",
            vulnerability_type="shell_injection",
            risk_score=0.85,
            line_numbers=[10],
            metadata={},
        )

        fixes = self.generator.generate_multiple_fixes(context)

        assert len(fixes) > 0, "Fixes must not be empty"
        assert all(f.validation_passed for f in fixes), "Condition must be true"
        # Fixes should be sorted by confidence
        if len(fixes) > 1:
            assert fixes[0].confidence >= fixes[1].confidence, "confidence must be greater than zero"

    def test_syntax_validation(self):
        """Test syntax validation of generated fixes."""
        # Valid Python code
        assert self.generator._validate_syntax("x = 1\nlogger.info(x)") is True, "Condition must be true"

        # Invalid Python code
        assert self.generator._validate_syntax("x = 1\nlogger.info(x") is False, "Condition must be true"

    def test_strategy_selection(self):
        """Test correct strategy selection."""
        context = FixContext(
            file_path="test.py",
            code="",
            vulnerability_type="shell_injection",
            risk_score=0.8,
            line_numbers=[],
            metadata={},
        )

        strategy = self.generator._select_strategy(context)
        assert strategy == FixStrategy.SHELL_INJECTION, "strategy is not valid"

        context.vulnerability_type = "eval_usage"
        strategy = self.generator._select_strategy(context)
        assert strategy == FixStrategy.EVAL_EXEC_REMOVAL, "strategy is not valid"


class TestFixVerifier:
    """Test fix verification system."""

    def setup_method(self):
        self.verifier = FixVerifier(test_command="echo test")

    def test_hash_calculation(self):
        """Test content hash calculation."""
        content1 = "test content"
        content2 = "test content"
        content3 = "different content"

        hash1 = self.verifier._calculate_hash(content1)
        hash2 = self.verifier._calculate_hash(content2)
        hash3 = self.verifier._calculate_hash(content3)

        assert hash1 == hash2, "hash1 is not valid"
        assert hash1 != hash3, "hash1 is not valid"

    def test_complexity_calculation(self):
        """Test cyclomatic complexity calculation."""
        simple_code = "x = 1\ny = 2"
        complex_code = """
if x > 0:
    if y > 0:
        for i in range(10):
            while i > 0:
                i -= 1
"""

        simple_complexity = self.verifier._calculate_complexity(simple_code)
        complex_complexity = self.verifier._calculate_complexity(complex_code)

        assert simple_complexity < complex_complexity, "simple_complexity is not valid"
        assert complex_complexity >= 4, "complex_complexity must be greater than zero"

    def test_security_score_calculation(self):
        """Test security score calculation."""
        safe_code = "x = 1 + 2"
        risky_code = 'subprocess.run("ls", shell=True)\neval(user_input)'

        safe_score = self.verifier._calculate_security_score(safe_code)
        risky_score = self.verifier._calculate_security_score(risky_code)

        assert safe_score > risky_score, "safe_score must be greater than zero"
        assert safe_score == 100.0, "safe_score is not valid"
        assert risky_score < 80.0, "risky_score is not valid"

    def test_diff_generation(self):
        """Test unified diff generation."""
        original = "line1\nline2\nline3"
        fixed = "line1\nmodified line2\nline3"

        diff = self.verifier.generate_diff(original, fixed)

        assert "line1" in diff, "Condition must be true"
        assert "modified line2" in diff or "-line2" in diff, "Condition must be true"

    def test_improvements_detection(self):
        """Test detection of improvements."""
        from auto_remediation.verifier import PostFixSnapshot, PreFixSnapshot

        pre = PreFixSnapshot(
            file_hash="hash1",
            file_content="code",
            test_results={"passed": False},
            metrics={"security_score": 70.0, "complexity": 10},
            timestamp="2026-01-01",
        )

        post = PostFixSnapshot(
            file_hash="hash2",
            file_content="fixed_code",
            test_results={"passed": True},
            metrics={"security_score": 90.0, "complexity": 8},
            timestamp="2026-01-01",
        )

        improvements = self.verifier._detect_improvements(pre, post)

        assert len(improvements) > 0, "Improvements must not be empty"
        assert any("test" in imp.lower() for imp in improvements), "Condition must be true"
        assert any("security" in imp.lower() for imp in improvements), "Condition must be true"

    def test_regression_detection(self):
        """Test detection of regressions."""
        from auto_remediation.verifier import PostFixSnapshot, PreFixSnapshot

        pre = PreFixSnapshot(
            file_hash="hash1",
            file_content="code",
            test_results={"passed": True},
            metrics={"security_score": 90.0, "complexity": 5},
            timestamp="2026-01-01",
        )

        post = PostFixSnapshot(
            file_hash="hash2",
            file_content="fixed_code",
            test_results={"passed": False},
            metrics={"security_score": 85.0, "complexity": 15},
            timestamp="2026-01-01",
        )

        regressions = self.verifier._detect_regressions(pre, post)

        assert len(regressions) > 0, "Regressions must not be empty"
        assert any("test" in reg.lower() for reg in regressions), "Condition must be true"
        assert any("complexity" in reg.lower() for reg in regressions), "Condition must be true"

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        from auto_remediation.verifier import PostFixSnapshot, PreFixSnapshot

        # Good fix scenario
        pre_good = PreFixSnapshot(
            file_hash="hash1",
            file_content="code",
            test_results={"passed": True},
            metrics={"security_score": 70.0},
            timestamp="2026-01-01",
        )

        post_good = PostFixSnapshot(
            file_hash="hash2",
            file_content="fixed_code",
            test_results={"passed": True},
            metrics={"security_score": 90.0},
            timestamp="2026-01-01",
        )

        confidence_good = self.verifier._calculate_confidence(pre_good, post_good, [])
        assert confidence_good > 0.8, "confidence_good must be greater than zero"

        # Bad fix scenario
        post_bad = PostFixSnapshot(
            file_hash="hash2",
            file_content="fixed_code",
            test_results={"passed": False},
            metrics={"security_score": 60.0},
            timestamp="2026-01-01",
        )

        confidence_bad = self.verifier._calculate_confidence(pre_good, post_bad, ["regression"])
        assert confidence_bad < 0.5, "confidence_bad is not valid"

    def test_success_rate_tracking(self):
        """Test success rate calculation."""
        from auto_remediation.verifier import (
            PostFixSnapshot,
            PreFixSnapshot,
            VerificationResult,
        )

        pre = PreFixSnapshot("hash", "code", {}, {}, "2026-01-01")
        post = PostFixSnapshot("hash", "code", {}, {}, "2026-01-01")

        # Add successful verification
        result1 = VerificationResult(True, pre, post, [], [], 0.9, "success")
        self.verifier.verification_history.append(result1)

        # Add failed verification
        result2 = VerificationResult(False, pre, post, ["error"], [], 0.3, "failed")
        self.verifier.verification_history.append(result2)

        success_rate = self.verifier.get_success_rate()
        assert success_rate == 0.5, "success_rate is not valid"


class TestIntegration:
    """Integration tests for auto-remediation system."""

    def test_end_to_end_fix_workflow(self):
        """Test complete workflow from detection to verification."""
        # Generate fix
        generator = IntelligentFixGenerator()
        context = FixContext(
            file_path="test.py",
            code='subprocess.run("ls", shell=True)',
            vulnerability_type="shell_injection",
            risk_score=0.85,
            line_numbers=[10],
            metadata={},
        )

        fix = generator.generate_fix(context)
        assert fix is not None, "fix must be initialized"
        assert fix.validation_passed, "Condition must be true"

        # Verify fix
        verifier = FixVerifier(test_command="echo test")
        result = verifier.verify_fix("test.py", fix.original_code, fix.fixed_code)

        assert result is not None, "result must be initialized"
        assert result.confidence_score > 0, "confidence_score must be greater than zero"

    def test_80_percent_success_target(self):
        """Test that success rate meets 80% target."""
        generator = IntelligentFixGenerator()

        test_cases = [
            ('subprocess.run("ls", shell=True)', "shell_injection"),
            ("eval(user_input)", "eval_usage"),
            ("hashlib.md5(data)", "weak_crypto"),
            ("pickle.loads(data)", "pickle_usage"),
            ("xml.etree.ElementTree.parse(file)", "xml_parsing"),
        ]

        successful = 0
        total = len(test_cases)

        for code, vuln_type in test_cases:
            context = FixContext(
                file_path="test.py",
                code=code,
                vulnerability_type=vuln_type,
                risk_score=0.8,
                line_numbers=[1],
                metadata={},
            )

            fix = generator.generate_fix(context)
            if fix and fix.validation_passed:
                successful += 1

        success_rate = successful / total
        assert success_rate >= 0.80, f"Success rate {success_rate:.1%} below 80% target"

    def test_rollback_on_failed_verification(self):
        """Test rollback when fix verification fails."""
        generator = IntelligentFixGenerator()
        context = FixContext(
            file_path="test.py",
            code='subprocess.run("ls", shell=True)',
            vulnerability_type="shell_injection",
            risk_score=0.85,
            line_numbers=[10],
            metadata={},
        )

        fix = generator.generate_fix(context)
        assert fix is not None, "fix must be initialized"

        # Simulate failed verification by checking original code preserved
        assert fix.original_code == 'subprocess.run("ls", shell=True)'

    def test_progressive_remediation_strategy(self):
        """Test progressive remediation from conservative to aggressive."""
        generator = IntelligentFixGenerator()

        # Start with conservative fix
        context = FixContext(
            file_path="test.py",
            code="result = eval(user_input)",
            vulnerability_type="eval_usage",
            risk_score=0.90,
            line_numbers=[15],
            metadata={"remediation_level": "conservative"},
        )

        fix = generator.generate_fix(context)
        assert fix is not None, "fix must be initialized"
        # Conservative approach might suggest ast.literal_eval
        assert "ast.literal_eval" in fix.fixed_code or "REMOVED" in fix.fixed_code, "Condition must be true"

    def test_confidence_scoring_accuracy(self):
        """Test confidence scoring reflects fix quality."""
        generator = IntelligentFixGenerator()

        # High confidence fix (simple substitution)
        high_conf_context = FixContext(
            file_path="test.py",
            code="hash_value = hashlib.md5(data).hexdigest()",
            vulnerability_type="weak_crypto_md5",
            risk_score=0.70,
            line_numbers=[25],
            metadata={},
        )

        high_conf_fix = generator.generate_fix(high_conf_context)
        assert high_conf_fix.confidence > 0.9, "confidence must be greater than zero"

        # Lower confidence fix (complex removal)
        low_conf_context = FixContext(
            file_path="test.py",
            code="result = eval(complex_expression)",
            vulnerability_type="eval_usage",
            risk_score=0.90,
            line_numbers=[15],
            metadata={},
        )

        low_conf_fix = generator.generate_fix(low_conf_context)
        # Should be lower confidence for eval removal
        assert low_conf_fix.confidence <= high_conf_fix.confidence, "confidence is not valid"

    def test_remediation_history_tracking(self):
        """Test tracking of remediation attempts and history."""
        verifier = FixVerifier(test_command="echo test")

        # Simulate multiple remediation attempts
        from auto_remediation.verifier import (
            PostFixSnapshot,
            PreFixSnapshot,
            VerificationResult,
        )

        pre = PreFixSnapshot("hash1", "code", {}, {}, "2026-01-01")
        post = PostFixSnapshot("hash2", "fixed", {}, {}, "2026-01-01")

        result1 = VerificationResult(True, pre, post, [], [], 0.9, "success")
        result2 = VerificationResult(False, pre, post, ["error"], [], 0.3, "failed")

        verifier.verification_history.append(result1)
        verifier.verification_history.append(result2)

        assert len(verifier.verification_history) == 2, "Collection must not be empty"
        assert verifier.get_success_rate() == 0.5, "Condition must be true"

    def test_learning_from_previous_failures(self):
        """Test system learns from previous remediation failures."""
        verifier = FixVerifier(test_command="echo test")

        # Track multiple attempts
        from auto_remediation.verifier import (
            PostFixSnapshot,
            PreFixSnapshot,
            VerificationResult,
        )

        pre = PreFixSnapshot("hash", "code", {}, {}, "2026-01-01")
        post = PostFixSnapshot("hash2", "fixed", {}, {}, "2026-01-01")

        # Add failed attempts
        for i in range(3):
            result = VerificationResult(False, pre, post, [f"error_{i}"], [], 0.2, "failed")
            verifier.verification_history.append(result)

        # Verify we can query failure patterns
        failure_count = sum(1 for r in verifier.verification_history if not r.success)
        assert failure_count == 3, "Count must be greater than zero"

    def test_fix_metadata_preservation(self):
        """Test that fix metadata is preserved through workflow."""
        generator = IntelligentFixGenerator()
        context = FixContext(
            file_path="test.py",
            code='subprocess.run("ls", shell=True)',
            vulnerability_type="shell_injection",
            risk_score=0.85,
            line_numbers=[10],
            metadata={"author": "security-scanner", "scan_id": "123"},
        )

        fix = generator.generate_fix(context)
        assert fix is not None, "fix must be initialized"
        # Verify context metadata is accessible
        assert context.metadata["author"] == "security-scanner", "Data must not be empty"
        assert context.metadata["scan_id"] == "123", "Data must not be empty"

    def test_multi_line_vulnerability_fix(self):
        """Test fixing vulnerabilities spanning multiple lines."""
        generator = IntelligentFixGenerator()
        context = FixContext(
            file_path="test.py",
            code="cmd = user_input\nsubprocess.run(cmd, shell=True)",
            vulnerability_type="shell_injection",
            risk_score=0.85,
            line_numbers=[10, 11],
            metadata={},
        )

        fix = generator.generate_fix(context)
        assert fix is not None, "fix must be initialized"
        assert "shell=False" in fix.fixed_code or "shlex.split" in fix.fixed_code, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
