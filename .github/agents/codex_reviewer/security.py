"""
Security Validation Components

This module contains security vulnerability detection and validation logic.
"""

import logging
import re
from typing import Any

from .secret_patterns import SecretPatterns, has_high_entropy

logger = logging.getLogger(__name__)


class SecurityValidator:
    """
    Security vulnerability detection and validation.

    Scans for:
    - Hardcoded secrets (with entropy analysis)
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Insecure dependencies
    - Common security anti-patterns
    """

    def __init__(self):
        """Initialize security validator with configurable patterns and compiled regexes."""
        self.secret_patterns = SecretPatterns.get_compiled_patterns()
        self.placeholder_patterns = SecretPatterns.get_compiled_placeholder_patterns()

        # Pre-compile SQL injection patterns for performance
        self._sql_patterns = [
            re.compile(r'execute\s*\(["\'].*%s.*["\']\s*%', re.IGNORECASE),
            re.compile(r'\.format\s*\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE)', re.IGNORECASE),
            re.compile(r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*\{.*\}', re.IGNORECASE),
        ]

        # Pre-compile XSS patterns
        self._xss_patterns = [
            re.compile(r'innerHTML\s*='),
            re.compile(r'dangerouslySetInnerHTML'),
            re.compile(r'\.html\s*\([^)]*\+'),
        ]

        # Pre-compile command injection patterns
        self._cmd_patterns = [
            (re.compile(r'os\.system\s*\('), "os.system() with user input"),
            (re.compile(r'subprocess\.call\s*\([^,]*\+'), "subprocess.call with string concatenation"),
            (re.compile(r'subprocess\.run\s*\([^,]*\+'), "subprocess.run with string concatenation"),
            (re.compile(r'shell=True'), "subprocess with shell=True"),
            (re.compile(r'eval\s*\('), "eval() with potential user input"),
            (re.compile(r'exec\s*\('), "exec() with potential user input"),
        ]

        # Pre-compile path traversal patterns
        self._path_patterns = [
            (re.compile(r'open\s*\([^,]*\+'), "File open with string concatenation"),
            (re.compile(r'os\.path\.join\s*\([^,]*\+'), "Path join with concatenation"),
            (re.compile(r'Path\s*\([^,]*\+'), "Path construction with concatenation"),
        ]

    async def scan(self, context) -> list[dict[str, Any]]:
        """
        Perform comprehensive security scan.

        Args:
            context: ReviewContext with PR information

        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []

        # Check for hardcoded secrets
        secrets = await self._detect_secrets(context.diff, context.files_changed)
        vulnerabilities.extend(secrets)

        # Check for SQL injection
        sql_injection = await self._check_sql_injection(context.files_changed, context.diff)
        vulnerabilities.extend(sql_injection)

        # Check for XSS vulnerabilities
        xss = await self._check_xss(context.files_changed, context.diff)
        vulnerabilities.extend(xss)

        # Check for insecure dependencies
        deps = await self._check_dependencies(context.files_changed)
        vulnerabilities.extend(deps)

        # Check for command injection
        cmd_injection = await self._check_command_injection(context.diff)
        vulnerabilities.extend(cmd_injection)

        # Check for path traversal
        path_traversal = await self._check_path_traversal(context.diff)
        vulnerabilities.extend(path_traversal)

        logger.info(f"Found {len(vulnerabilities)} security vulnerabilities")
        return vulnerabilities

    async def _detect_secrets(self, diff: str, files: list[str]) -> list[dict[str, Any]]:
        """
        Detect hardcoded secrets in diff using pattern matching and entropy analysis.

        Uses configurable patterns from secret_patterns module and entropy analysis
        to reduce false positives.
        """
        secrets = []

        # Pattern-based detection
        for secret_type, pattern in self.secret_patterns.items():
            matches = pattern.finditer(diff)
            for match in matches:
                # Extract the captured value
                try:
                    value = match.group(1) if match.groups() else match.group(0)
                except IndexError:
                    value = match.group(0)

                # Skip if it's a placeholder
                if SecretPatterns.is_placeholder(value):
                    continue

                # Additional entropy check for high-confidence detection
                confidence = "high" if has_high_entropy(value) else "medium"

                secrets.append({
                    "type": "hardcoded_secret",
                    "secret_type": secret_type,
                    "severity": "critical",
                    "category": "security",
                    "confidence": confidence,
                    "line": self._get_line_number(diff, match.start()),
                    "description": f"Hardcoded {secret_type} detected",
                    "suggestion": f"Remove hardcoded {secret_type} and use environment variables or secrets manager"
                })

        # High-risk file check
        for file in files:
            if SecretPatterns.is_high_risk_file(file):
                secrets.append({
                    "type": "high_risk_file",
                    "secret_type": "file",
                    "severity": "high",
                    "category": "security",
                    "file": file,
                    "description": f"High-risk file detected: {file}",
                    "suggestion": "Ensure this file is in .gitignore and not committed to repository"
                })

        return secrets

    async def _check_sql_injection(self, files: list[str], diff: str) -> list[dict[str, Any]]:
        """Check for SQL injection vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        for pattern in self._sql_patterns:
            if pattern.search(diff):
                vulnerabilities.append({
                    "type": "sql_injection",
                    "severity": "high",
                    "category": "security",
                    "description": "Potential SQL injection vulnerability detected",
                    "suggestion": "Use parameterized queries or ORM methods instead of string formatting"
                })
                break  # Only report once per diff

        return vulnerabilities

    async def _check_xss(self, files: list[str], diff: str) -> list[dict[str, Any]]:
        """Check for XSS vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        for pattern in self._xss_patterns:
            if pattern.search(diff):
                vulnerabilities.append({
                    "type": "xss",
                    "severity": "high",
                    "category": "security",
                    "description": "Potential XSS vulnerability detected",
                    "suggestion": "Sanitize user input before rendering as HTML"
                })
                break  # Only report once per diff

        return vulnerabilities

    async def _check_dependencies(self, files: list[str]) -> list[dict[str, Any]]:
        """Check for insecure dependencies."""
        vulnerabilities = []

        # Dependency file mapping with ecosystems
        dep_files_mapping = {
            "requirements.txt": "Python (pip)",
            "Pipfile": "Python (pipenv)",
            "pyproject.toml": "Python (poetry/PDM)",
            "package.json": "JavaScript (npm)",
            "yarn.lock": "JavaScript (yarn)",
            "Gemfile": "Ruby (bundler)",
            "Gemfile.lock": "Ruby (bundler)",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java (Gradle)",
            "Cargo.toml": "Rust (cargo)",
            "go.mod": "Go",
            "composer.json": "PHP (composer)",
        }

        for file in files:
            for dep_file, ecosystem in dep_files_mapping.items():
                if dep_file in file:
                    vulnerabilities.append({
                        "type": "dependency_update",
                        "severity": "medium",
                        "category": "security",
                        "file": file,
                        "ecosystem": ecosystem,
                        "description": f"Dependencies modified in {ecosystem}",
                        "suggestion": f"Run security scanner for {ecosystem} dependencies (e.g., Snyk, Dependabot, Safety)"
                    })
                    break

        return vulnerabilities

    async def _check_command_injection(self, diff: str) -> list[dict[str, Any]]:
        """Check for potential command injection vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        for pattern, description in self._cmd_patterns:
            if pattern.search(diff):
                vulnerabilities.append({
                    "type": "command_injection_risk",
                    "severity": "high",
                    "category": "security",
                    "description": f"Potential command injection: {description}",
                    "suggestion": "Use parameterized commands, avoid shell=True, validate all user inputs"
                })

        return vulnerabilities

    async def _check_path_traversal(self, diff: str) -> list[dict[str, Any]]:
        """Check for potential path traversal vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        for pattern, description in self._path_patterns:
            if pattern.search(diff):
                vulnerabilities.append({
                    "type": "path_traversal_risk",
                    "severity": "medium",
                    "category": "security",
                    "description": f"Potential path traversal: {description}",
                    "suggestion": "Validate file paths, use Path.resolve(), check for '..' in paths"
                })

        return vulnerabilities

    def _get_line_number(self, text: str, position: int) -> int:
        """Get line number for a position in text."""
        return text[:position].count('\n') + 1
