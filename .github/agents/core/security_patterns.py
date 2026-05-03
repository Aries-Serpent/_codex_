"""
Security Pattern Matcher - Advanced Security Vulnerability Detection
Part of Cognitive Brain Pattern Recognition Enhancement (Phase 2)

Detects:
- SQL Injection vulnerabilities
- XSS (Cross-Site Scripting) vulnerabilities
- Hardcoded secrets and credentials
- Insecure cryptographic practices
- Command injection vulnerabilities
- Path traversal vulnerabilities

#AFTERMATH_PATTERN_IDENTIFIED: security_pattern_detection
#AFTERMATH_METRIC: vulnerabilities_detected
Integrates with cognitive brain for learning and pattern evolution.
"""
import ast
import re
from dataclasses import dataclass
from pathlib import Path

from .pattern_recognizer import Pattern, PatternMatcher


@dataclass
class SecurityPattern(Pattern):
    """Extended pattern with security-specific metadata"""
    severity: str = "medium"  # low, medium, high, critical
    cwe_id: str = ""  # Common Weakness Enumeration ID
    remediation: str = ""  # Suggested fix


class SecurityPatternMatcher(PatternMatcher):
    """
    #AFTERMATH_PATTERN_IDENTIFIED: security_vulnerability_detection

    Advanced security pattern detection using:
    1. Static analysis (AST parsing)
    2. Regex patterns for common vulnerabilities
    3. Semantic analysis for context-aware detection
    4. Cognitive brain integration for learning

    PDA Loop Integration:
    - PERCEIVE: Scan code for security patterns
    - DECIDE: Classify severity and prioritize
    - ACT: Record findings in cognitive brain
    - AFTERMATH: Learn from false positives/negatives
    """

    def __init__(self):
        """Initialize security pattern matcher with detection rules"""
        super().__init__()

        # SQL Injection patterns
        self.sql_injection_patterns = [
            # String concatenation with SQL
            (r'execute\(["\'].*?\+', "SQL query with string concatenation", "high"),
            (r'cursor\.execute\(["\'][^"\']*%s', "SQL with string formatting", "high"),
            (r'SELECT.*FROM.*WHERE.*\+', "SQL SELECT with concatenation", "critical"),
            (r'\.format\(.*\).*execute', "SQL with .format()", "high"),
            (r'f["\']SELECT.*{.*}', "SQL with f-string interpolation", "medium"),
        ]

        # XSS patterns
        self.xss_patterns = [
            (r'innerHTML\s*=\s*[^"\']', "Direct innerHTML assignment", "high"),
            (r'document\.write\([^)]*\+', "document.write with concatenation", "medium"),
            (r'eval\([^)]*request', "eval() with user input", "critical"),
            (r'dangerouslySetInnerHTML', "React dangerouslySetInnerHTML", "medium"),
            (r'v-html=["\']\{\{', "Vue v-html with template", "medium"),
        ]

        # Secret/credential patterns
        self.secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded password", "critical"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key", "critical"),
            (r'secret\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded secret", "critical"),
            (r'token\s*=\s*["\'][^"\']{20,}["\']', "Hardcoded token", "critical"),
            (r'AWS_SECRET_ACCESS_KEY\s*=', "AWS secret key", "critical"),
            (r'PRIVATE_KEY\s*=\s*["\']', "Private key in code", "critical"),
        ]

        # Insecure crypto patterns
        self.crypto_patterns = [
            (r'hashlib\.md5\(', "MD5 usage (insecure)", "medium"),
            (r'hashlib\.sha1\(', "SHA1 usage (deprecated)", "low"),
            (r'Random\(\)', "Insecure random (not cryptographic)", "medium"),
            (r'DES\.new\(', "DES encryption (insecure)", "high"),
            (r'mode=ECB', "ECB mode (insecure)", "high"),
        ]

        # Command injection patterns
        self.command_injection_patterns = [
            (r'os\.system\([^)]*\+', "os.system with concatenation", "critical"),
            (r'subprocess\.call\(.*shell=True', "subprocess with shell=True", "high"),
            (r'eval\(', "eval() usage (dangerous)", "high"),
            (r'exec\(', "exec() usage (dangerous)", "high"),
        ]

        # Path traversal patterns
        self.path_traversal_patterns = [
            (r'open\([^)]*\+.*["\']\.\.', "Path with .. traversal", "high"),
            (r'os\.path\.join\([^)]*request', "Path join with user input", "medium"),
            (r'file_path\s*=\s*request', "Direct file path from request", "high"),
        ]

    def detect(self, file_path: Path) -> list[Pattern]:
        """
        #AFTERMATH_PATTERN_IDENTIFIED: security_detection_pda_loop

        PERCEIVE: Analyze file for security vulnerabilities
        DECIDE: Classify findings by severity
        ACT: Return detected patterns
        AFTERMATH: Patterns stored in cognitive brain for learning
        """
        detected: list[SecurityPattern] = []

        if not file_path.exists():
            return detected

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # PERCEIVE Phase: Multi-layer security analysis
            detected.extend(self._detect_sql_injection(content, file_path))
            detected.extend(self._detect_xss(content, file_path))
            detected.extend(self._detect_secrets(content, file_path))
            detected.extend(self._detect_crypto_issues(content, file_path))
            detected.extend(self._detect_command_injection(content, file_path))
            detected.extend(self._detect_path_traversal(content, file_path))

            # Python-specific AST analysis
            if file_path.suffix == '.py':
                detected.extend(self._ast_security_analysis(content, file_path))

            # #AFTERMATH_METRIC: vulnerabilities_detected
            # Metrics tracked: total_vulns, by_severity, by_type

        except Exception as e:
            # Record analysis failure as a pattern
            detected.append(SecurityPattern(
                name="analysis_error",
                pattern_type="security",
                description=f"Security analysis failed: {str(e)}",
                locations=[str(file_path)],
                confidence=0.1,
                metadata={"error": str(e), "file": str(file_path)},
                severity="low",
                cwe_id="N/A"
            ))

        return detected

    def _detect_sql_injection(self, content: str, file_path: Path) -> list[SecurityPattern]:
        """Detect SQL injection vulnerabilities"""
        findings = []
        for pattern, description, severity in self.sql_injection_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                findings.append(SecurityPattern(
                    name="sql_injection",
                    pattern_type="security",
                    description=f"Potential SQL injection: {description}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.8,
                    metadata={
                        "line": line_num,
                        "matched_pattern": match.group(0),
                        "file": str(file_path)
                    },
                    severity=severity,
                    cwe_id="CWE-89",
                    remediation="Use parameterized queries or ORM methods"
                ))
        return findings

    def _detect_xss(self, content: str, file_path: Path) -> list[SecurityPattern]:
        """Detect XSS vulnerabilities"""
        findings = []
        for pattern, description, severity in self.xss_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                findings.append(SecurityPattern(
                    name="xss_vulnerability",
                    pattern_type="security",
                    description=f"Potential XSS: {description}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.7,
                    metadata={
                        "line": line_num,
                        "matched_pattern": match.group(0),
                        "file": str(file_path)
                    },
                    severity=severity,
                    cwe_id="CWE-79",
                    remediation="Sanitize user input, use safe APIs, escape output"
                ))
        return findings

    def _detect_secrets(self, content: str, file_path: Path) -> list[SecurityPattern]:
        """Detect hardcoded secrets and credentials"""
        findings = []
        for pattern, description, severity in self.secret_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                findings.append(SecurityPattern(
                    name="hardcoded_secret",
                    pattern_type="security",
                    description=f"Security risk: {description}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.9,
                    metadata={
                        "line": line_num,
                        "secret_type": description,
                        "file": str(file_path)
                    },
                    severity=severity,
                    cwe_id="CWE-798",
                    remediation="Use environment variables or secret management service"
                ))
        return findings

    def _detect_crypto_issues(self, content: str, file_path: Path) -> list[SecurityPattern]:
        """Detect insecure cryptographic practices"""
        findings = []
        for pattern, description, severity in self.crypto_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                findings.append(SecurityPattern(
                    name="insecure_crypto",
                    pattern_type="security",
                    description=f"Cryptographic issue: {description}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.85,
                    metadata={
                        "line": line_num,
                        "issue": description,
                        "file": str(file_path)
                    },
                    severity=severity,
                    cwe_id="CWE-327",
                    remediation="Use modern crypto: SHA256+, AES-GCM, secrets module"
                ))
        return findings

    def _detect_command_injection(self, content: str, file_path: Path) -> list[SecurityPattern]:
        """Detect command injection vulnerabilities"""
        findings = []
        for pattern, description, severity in self.command_injection_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                findings.append(SecurityPattern(
                    name="command_injection",
                    pattern_type="security",
                    description=f"Command injection risk: {description}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.85,
                    metadata={
                        "line": line_num,
                        "pattern": match.group(0),
                        "file": str(file_path)
                    },
                    severity=severity,
                    cwe_id="CWE-78",
                    remediation="Avoid shell=True, validate input, use subprocess safely"
                ))
        return findings

    def _detect_path_traversal(self, content: str, file_path: Path) -> list[SecurityPattern]:
        """Detect path traversal vulnerabilities"""
        findings = []
        for pattern, description, severity in self.path_traversal_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                findings.append(SecurityPattern(
                    name="path_traversal",
                    pattern_type="security",
                    description=f"Path traversal risk: {description}",
                    locations=[f"{file_path}:{line_num}"],
                    confidence=0.75,
                    metadata={
                        "line": line_num,
                        "pattern": match.group(0),
                        "file": str(file_path)
                    },
                    severity=severity,
                    cwe_id="CWE-22",
                    remediation="Validate paths, use Path.resolve(), restrict to safe directories"
                ))
        return findings

    def _ast_security_analysis(self, content: str, file_path: Path) -> list[SecurityPattern]:
        """
        Deep AST-based security analysis for Python code

        #AFTERMATH_PATTERN_IDENTIFIED: ast_security_analysis
        More accurate than regex for Python-specific vulnerabilities
        """
        findings = []

        try:
            tree = ast.parse(content)

            # Analyze dangerous function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Check for dangerous built-ins
                        if node.func.id in ['eval', 'exec', '__import__']:
                            findings.append(SecurityPattern(
                                name="dangerous_builtin",
                                pattern_type="security",
                                description=f"Dangerous built-in: {node.func.id}()",
                                locations=[f"{file_path}:{node.lineno}"],
                                confidence=0.9,
                                metadata={
                                    "line": node.lineno,
                                    "function": node.func.id,
                                    "file": str(file_path)
                                },
                                severity="high",
                                cwe_id="CWE-94",
                                remediation=f"Avoid {node.func.id}(), use safer alternatives"
                            ))

                    elif isinstance(node.func, ast.Attribute):
                        # Check for dangerous library calls
                        if node.func.attr == 'system' and isinstance(node.func.value, ast.Name):
                            if node.func.value.id == 'os':
                                findings.append(SecurityPattern(
                                    name="os_system_call",
                                    pattern_type="security",
                                    description="os.system() call detected (use subprocess)",
                                    locations=[f"{file_path}:{node.lineno}"],
                                    confidence=0.9,
                                    metadata={
                                        "line": node.lineno,
                                        "file": str(file_path)
                                    },
                                    severity="high",
                                    cwe_id="CWE-78",
                                    remediation="Use subprocess.run() with list arguments"
                                ))

        except SyntaxError:
            # Skip files with syntax errors
            pass

        return findings

    def get_pattern_type(self) -> str:
        """Return pattern type for cognitive brain categorization"""
        return "security"

    def get_severity_stats(self, patterns: list[SecurityPattern]) -> dict[str, int]:
        """
        Calculate severity distribution for metrics

        #AFTERMATH_METRIC: security_severity_distribution
        """
        stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for pattern in patterns:
            if isinstance(pattern, SecurityPattern):
                stats[pattern.severity] = stats.get(pattern.severity, 0) + 1
        return stats
