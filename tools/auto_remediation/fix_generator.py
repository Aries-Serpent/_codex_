"""
Intelligent Fix Generator for Auto-Remediation.

This module provides context-aware patching capabilities for common security
vulnerabilities and code quality issues detected by the ML threat detector.
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class FixStrategy(Enum):
    """Available fix strategies."""

    SHELL_INJECTION = "shell_injection"
    EVAL_EXEC_REMOVAL = "eval_exec_removal"
    PICKLE_SECURE = "pickle_secure"
    XML_SECURE_PARSER = "xml_secure_parser"
    INPUT_VALIDATION = "input_validation"
    WEAK_CRYPTO = "weak_crypto"
    FILE_PERMISSION = "file_permission"
    SQL_INJECTION = "sql_injection"
    XSS_PREVENTION = "xss_prevention"
    CORS_HARDENING = "cors_hardening"


@dataclass
class FixContext:
    """Context information for generating fixes."""

    file_path: str
    code: str
    vulnerability_type: str
    risk_score: float
    line_numbers: List[int]
    metadata: Dict[str, Any]


@dataclass
class GeneratedFix:
    """A generated fix with metadata."""

    strategy: FixStrategy
    original_code: str
    fixed_code: str
    explanation: str
    confidence: float
    file_path: str
    line_numbers: List[int]
    validation_passed: bool = False


class IntelligentFixGenerator:
    """
    Generates intelligent, context-aware fixes for security vulnerabilities.

    Features:
    - Multi-strategy fix selection
    - Code style preservation
    - Validation before application
    - ML threat detector integration
    """

    def __init__(self, preserve_style: bool = True, validate_syntax: bool = True):
        self.preserve_style = preserve_style
        self.validate_syntax = validate_syntax
        self.fix_strategies = {
            FixStrategy.SHELL_INJECTION: self._fix_shell_injection,
            FixStrategy.EVAL_EXEC_REMOVAL: self._fix_eval_exec,
            FixStrategy.PICKLE_SECURE: self._fix_pickle_usage,
            FixStrategy.XML_SECURE_PARSER: self._fix_xml_parser,
            FixStrategy.INPUT_VALIDATION: self._add_input_validation,
            FixStrategy.WEAK_CRYPTO: self._fix_weak_crypto,
            FixStrategy.FILE_PERMISSION: self._fix_file_permissions,
        }

    def generate_fix(self, context: FixContext) -> Optional[GeneratedFix]:
        """
        Generate a fix for the given vulnerability context.

        Args:
            context: FixContext with vulnerability information

        Returns:
            GeneratedFix if successful, None otherwise
        """
        # Determine appropriate strategy
        strategy = self._select_strategy(context)
        if not strategy:
            return None

        # Generate fix using selected strategy
        fix_func = self.fix_strategies.get(strategy)
        if not fix_func:
            return None

        try:
            fixed_code, explanation, confidence = fix_func(context)

            # Validate syntax if enabled
            validation_passed = True
            if self.validate_syntax:
                validation_passed = self._validate_syntax(fixed_code)

            return GeneratedFix(
                strategy=strategy,
                original_code=context.code,
                fixed_code=fixed_code,
                explanation=explanation,
                confidence=confidence,
                file_path=context.file_path,
                line_numbers=context.line_numbers,
                validation_passed=validation_passed,
            )

        except Exception as e:
            print(f"Error generating fix: {e}")
            return None

    def generate_multiple_fixes(self, context: FixContext) -> List[GeneratedFix]:
        """
        Generate multiple fix options for the same vulnerability.

        Args:
            context: FixContext with vulnerability information

        Returns:
            List of possible fixes, sorted by confidence
        """
        fixes = []

        # Try multiple strategies
        strategies = self._get_applicable_strategies(context)
        for strategy in strategies:
            fix_func = self.fix_strategies.get(strategy)
            if not fix_func:
                continue

            try:
                fixed_code, explanation, confidence = fix_func(context)
                validation_passed = True
                if self.validate_syntax:
                    validation_passed = self._validate_syntax(fixed_code)

                fixes.append(
                    GeneratedFix(
                        strategy=strategy,
                        original_code=context.code,
                        fixed_code=fixed_code,
                        explanation=explanation,
                        confidence=confidence,
                        file_path=context.file_path,
                        line_numbers=context.line_numbers,
                        validation_passed=validation_passed,
                    )
                )
            except Exception:
                continue

        # Sort by confidence (descending)
        fixes.sort(key=lambda f: f.confidence, reverse=True)
        return fixes

    def _select_strategy(self, context: FixContext) -> Optional[FixStrategy]:
        """Select the most appropriate fix strategy."""
        vuln_type = context.vulnerability_type.lower()

        strategy_map = {
            "shell": FixStrategy.SHELL_INJECTION,
            "subprocess": FixStrategy.SHELL_INJECTION,
            "eval": FixStrategy.EVAL_EXEC_REMOVAL,
            "exec": FixStrategy.EVAL_EXEC_REMOVAL,
            "pickle": FixStrategy.PICKLE_SECURE,
            "xml": FixStrategy.XML_SECURE_PARSER,
            "input": FixStrategy.INPUT_VALIDATION,
            "md5": FixStrategy.WEAK_CRYPTO,
            "sha1": FixStrategy.WEAK_CRYPTO,
            "file": FixStrategy.FILE_PERMISSION,
        }

        for keyword, strategy in strategy_map.items():
            if keyword in vuln_type:
                return strategy

        return None

    def _get_applicable_strategies(self, context: FixContext) -> List[FixStrategy]:
        """Get all applicable strategies for the context."""
        strategies = []
        vuln_type = context.vulnerability_type.lower()

        if "shell" in vuln_type or "subprocess" in vuln_type:
            strategies.append(FixStrategy.SHELL_INJECTION)
        if "eval" in vuln_type or "exec" in vuln_type:
            strategies.append(FixStrategy.EVAL_EXEC_REMOVAL)
        if "pickle" in vuln_type:
            strategies.append(FixStrategy.PICKLE_SECURE)
        if "xml" in vuln_type:
            strategies.append(FixStrategy.XML_SECURE_PARSER)
        if "input" in vuln_type:
            strategies.append(FixStrategy.INPUT_VALIDATION)
        if "md5" in vuln_type or "sha1" in vuln_type:
            strategies.append(FixStrategy.WEAK_CRYPTO)

        return strategies

    def _fix_shell_injection(self, context: FixContext) -> Tuple[str, str, float]:
        """Fix shell injection vulnerabilities."""
        code = context.code

        # Replace shell=True with shell=False and use list arguments
        if "shell=True" in code:
            fixed = re.sub(r"shell\s*=\s*True", "shell=False", code)

            # Try to convert string command to list if possible
            match = re.search(r"subprocess\.(run|call|Popen)\(['\"]([^'\"]+)['\"]", fixed)
            if match:
                func, cmd = match.groups()
                cmd_list = cmd.split()
                fixed = re.sub(
                    r"subprocess\.(run|call|Popen)\(['\"][^'\"]+['\"]",
                    f"subprocess.{func}({cmd_list!r}",
                    fixed,
                )

            explanation = "Replaced shell=True with shell=False and converted command to list format to prevent shell injection"
            confidence = 0.90
            return fixed, explanation, confidence

        # Use shlex.split for safe command parsing
        if "subprocess" in code and "shell=False" not in code:
            fixed = code
            if "import shlex" not in fixed:
                fixed = "import shlex\n" + fixed

            explanation = "Added shlex import for safe command parsing"
            confidence = 0.85
            return fixed, explanation, confidence

        return code, "No changes needed", 0.50

    def _fix_eval_exec(self, context: FixContext) -> Tuple[str, str, float]:
        """Fix eval/exec usage."""
        code = context.code

        # Remove eval/exec or replace with safer alternatives
        if "eval(" in code:
            # Try to replace with ast.literal_eval for simple cases
            if "ast.literal_eval" not in code:
                fixed = re.sub(r"\beval\(", "ast.literal_eval(", code)
                if "import ast" not in fixed:
                    fixed = "import ast\n" + fixed
                explanation = "Replaced eval() with ast.literal_eval() for safer evaluation"
                confidence = 0.85
                return fixed, explanation, confidence

        if "exec(" in code:
            fixed = re.sub(r"\bexec\([^)]+\)", "# REMOVED: exec() call - security risk", code)
            explanation = "Removed exec() call as it poses a security risk"
            confidence = 0.75
            return fixed, explanation, confidence

        return code, "No changes needed", 0.50

    def _fix_pickle_usage(self, context: FixContext) -> Tuple[str, str, float]:
        """Fix unsafe pickle usage."""
        code = context.code

        if "pickle.loads" in code:
            # Replace with json for simple cases or add warning
            if "json" not in code:
                fixed = re.sub(r"pickle\.loads", "json.loads", code)
                fixed = re.sub(r"import pickle", "import json", fixed)
                explanation = "Replaced pickle.loads with json.loads for safer deserialization"
                confidence = 0.80
                return fixed, explanation, confidence

        return code, "Manual review required for pickle usage", 0.60

    def _fix_xml_parser(self, context: FixContext) -> Tuple[str, str, float]:
        """Fix XML parser vulnerabilities."""
        code = context.code

        # Replace ElementTree with defusedxml
        if "xml.etree.ElementTree" in code:
            fixed = re.sub(r"xml\.etree\.ElementTree", "defusedxml.ElementTree", code)
            fixed = re.sub(r"import xml\.etree\.ElementTree", "import defusedxml.ElementTree", fixed)
            explanation = "Replaced xml.etree.ElementTree with defusedxml for XXE protection"
            confidence = 0.90
            return fixed, explanation, confidence

        return code, "No changes needed", 0.50

    def _add_input_validation(self, context: FixContext) -> Tuple[str, str, float]:
        """Add input validation."""
        code = context.code

        # Add basic validation for user input
        if "input(" in code or "request." in code:
            validation_code = """
# Input validation
def validate_input(data, max_length=1000):
    if not isinstance(data, str):
        raise ValueError("Invalid input type")
    if len(data) > max_length:
        raise ValueError("Input too long")
    return data.strip()
"""
            fixed = validation_code + "\n" + code
            explanation = "Added input validation function"
            confidence = 0.70
            return fixed, explanation, confidence

        return code, "No validation added", 0.50

    def _fix_weak_crypto(self, context: FixContext) -> Tuple[str, str, float]:
        """Fix weak cryptography."""
        code = context.code

        # Replace MD5/SHA1 with SHA256
        if "hashlib.md5" in code or "hashlib.sha1" in code:
            fixed = re.sub(r"hashlib\.(md5|sha1)", "hashlib.sha256", code)
            explanation = "Replaced MD5/SHA1 with SHA256 for stronger hashing"
            confidence = 0.95
            return fixed, explanation, confidence

        return code, "No changes needed", 0.50

    def _fix_file_permissions(self, context: FixContext) -> Tuple[str, str, float]:
        """Fix file permission issues."""
        code = context.code

        # Add mode parameter to open() calls
        if "open(" in code and "mode=" not in code:
            fixed = re.sub(r"open\(([^,]+),\s*['\"]w['\"]", r"open(\1, 'w', encoding='utf-8'", code)
            explanation = "Added explicit encoding to file operations"
            confidence = 0.85
            return fixed, explanation, confidence

        return code, "No changes needed", 0.50

    def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax of fixed code."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def apply_fix(self, fix: GeneratedFix) -> bool:
        """
        Apply a generated fix to the file.

        Args:
            fix: GeneratedFix to apply

        Returns:
            True if successful, False otherwise
        """
        if not fix.validation_passed:
            print(f"Fix validation failed for {fix.file_path}")
            return False

        try:
            file_path = Path(fix.file_path)
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Use occurrence counting to detect ambiguous replacements
            occurrences = content.count(fix.original_code)
            if occurrences == 0:
                print(f"Warning: Original code not found in {fix.file_path}")
                return False
            elif occurrences > 1:
                print(f"Warning: Ambiguous replacement - code appears {occurrences} times in {fix.file_path}")
                print("Consider using AST-based or line-number-specific replacement")
                # Only replace first occurrence to avoid unintended changes
                new_content = content.replace(fix.original_code, fix.fixed_code, 1)
            else:
                new_content = content.replace(fix.original_code, fix.fixed_code)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return True

        except Exception as e:
            print(f"Error applying fix: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    generator = IntelligentFixGenerator()

    # Example: Fix shell injection
    context = FixContext(
        file_path="example.py",
        code='subprocess.run("ls -la", shell=True)',
        vulnerability_type="shell_injection",
        risk_score=0.85,
        line_numbers=[10],
        metadata={},
    )

    fix = generator.generate_fix(context)
    if fix:
        print(f"Strategy: {fix.strategy}")
        print(f"Original: {fix.original_code}")
        print(f"Fixed: {fix.fixed_code}")
        print(f"Explanation: {fix.explanation}")
        print(f"Confidence: {fix.confidence:.2%}")
        print(f"Validation: {'✅' if fix.validation_passed else '❌'}")
