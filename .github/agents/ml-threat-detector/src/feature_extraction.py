"""Feature extraction module for ML threat detection."""

import ast
import re
from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class SecurityFeatures:
    """20 security-relevant features extracted from code."""

    # 1-3: Code complexity metrics
    lines_of_code: int
    cyclomatic_complexity: int
    max_nesting_depth: int

    # 4-10: Security-sensitive operations
    subprocess_calls: int
    shell_true_usage: int
    eval_exec_calls: int
    file_operations: int
    network_operations: int
    crypto_operations: int
    pickle_usage: int

    # 11-13: Data handling
    xml_parsing: int
    user_input_handling: int
    environment_var_access: int

    # 14-15: Authentication/Authorization
    auth_operations: int
    permission_checks: int

    # 16-18: Code quality indicators
    import_count: int
    external_lib_count: int
    unsafe_pattern_count: int

    # 19-20: Historical context
    file_change_frequency: int
    author_security_score: float


class FeatureExtractor:
    """Extract security-relevant features from Python code."""

    def __init__(self):
        self.unsafe_patterns = [
            r"eval\(",
            r"exec\(",
            r"__import__\(",
            r"compile\(",
            r"shell=True",
            r"pickle\.loads",
            r"yaml\.load\(",
            r"md5\(",
            r"sha1\(",
        ]

    def extract(self, code: str, metadata: Optional[dict[str, Any]] = None) -> SecurityFeatures:
        """
        Extract all 20 security features from code.

        Args:
            code: Source code to analyze
            metadata: Optional historical metadata

        Returns:
            SecurityFeatures dataclass with all 20 features
        """
        metadata = metadata or {}

        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            tree = None

        # 1-3: Code complexity
        loc = self._count_lines(code)
        complexity = self._calculate_complexity(tree) if tree else 20
        nesting = self._max_nesting_depth(tree) if tree else 10

        # 4-10: Security operations
        subprocess_calls = len(re.findall(r"subprocess\.(run|call|Popen|check_output)", code))
        shell_true = len(re.findall(r"shell\s*=\s*True", code))
        eval_exec = len(re.findall(r"\b(eval|exec)\s*\(", code))
        file_ops = len(re.findall(r"\b(open|file)\s*\(", code))
        network_ops = len(re.findall(r"(requests\.|urllib\.|http\.client|socket\.)", code))
        crypto_ops = len(re.findall(r"(hashlib\.|hmac\.|Crypto\.|cryptography\.)", code))
        pickle_ops = len(re.findall(r"pickle\.(load|loads|dump|dumps)", code))

        # 11-13: Data handling
        xml_parse = len(re.findall(r"(xml\.etree|ElementTree|lxml)", code))
        user_input = len(re.findall(r"(input\(|request\.|sys\.argv|os\.environ)", code))
        env_vars = len(re.findall(r"os\.environ", code))

        # 14-15: Auth/Authz
        auth_ops = len(re.findall(r"(authenticate|authorize|login|password|token)", code, re.I))
        perm_checks = len(re.findall(r"(permission|check_access|require_auth|@login_required)", code, re.I))

        # 16-18: Code quality
        imports = len(re.findall(r"^(import |from .* import )", code, re.M))
        external_libs = len(set(re.findall(r"(?:import|from)\s+(\w+)", code)))
        unsafe_count = sum(len(re.findall(pattern, code)) for pattern in self.unsafe_patterns)

        # 19-20: Historical context
        change_freq = metadata.get("change_frequency", 0)
        author_score = metadata.get("author_security_score", 0.5)

        return SecurityFeatures(
            lines_of_code=loc,
            cyclomatic_complexity=complexity,
            max_nesting_depth=nesting,
            subprocess_calls=subprocess_calls,
            shell_true_usage=shell_true,
            eval_exec_calls=eval_exec,
            file_operations=file_ops,
            network_operations=network_ops,
            crypto_operations=crypto_ops,
            pickle_usage=pickle_ops,
            xml_parsing=xml_parse,
            user_input_handling=user_input,
            environment_var_access=env_vars,
            auth_operations=auth_ops,
            permission_checks=perm_checks,
            import_count=imports,
            external_lib_count=external_libs,
            unsafe_pattern_count=unsafe_count,
            file_change_frequency=change_freq,
            author_security_score=author_score,
        )

    def extract_as_dict(self, code: str, metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Extract features and return as dictionary."""
        features = self.extract(code, metadata)
        return asdict(features)

    def extract_as_vector(self, code: str, metadata: Optional[dict[str, Any]] = None) -> list:
        """Extract features and return as list for ML model."""
        features = self.extract(code, metadata)
        return list(asdict(features).values())

    def _count_lines(self, code: str) -> int:
        """Count non-empty, non-comment lines."""
        lines = code.split("\n")
        return len([line for line in lines if line.strip() and not line.strip().startswith("#")])

    def _calculate_complexity(self, tree: Optional[ast.AST]) -> int:
        """Calculate cyclomatic complexity."""
        if not tree:
            return 0

        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _max_nesting_depth(self, tree: Optional[ast.AST]) -> int:
        """Calculate maximum nesting depth."""
        if not tree:
            return 0

        def depth(node: ast.AST, current: int = 0) -> int:
            max_d = current
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.FunctionDef, ast.ClassDef)):
                    max_d = max(max_d, depth(child, current + 1))
                else:
                    max_d = max(max_d, depth(child, current))
            return max_d

        return depth(tree)


if __name__ == "__main__":
    # Example usage
    extractor = FeatureExtractor()

    # Test with vulnerable code
    vulnerable_code = """
import subprocess
import pickle

def unsafe_function(user_input):
    # Multiple security issues
    subprocess.run(user_input, shell=True)
    data = pickle.loads(user_input)
    eval(user_input)
    return data
"""

    # Test with safe code
    safe_code = """
def safe_function(x, y):
    result = x + y
    return result
"""

    print("Vulnerable code features:")
    vuln_features = extractor.extract(vulnerable_code)
    print(vuln_features)

    print("\nSafe code features:")
    safe_features = extractor.extract(safe_code)
    print(safe_features)

    print("\nFeature vector format:")
    print(extractor.extract_as_vector(vulnerable_code))
