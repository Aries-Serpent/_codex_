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
            re.compile(
                r"(?i)(?:;\s*drop\s+table|union\s+select|insert\s+into\s+.*\s+values\s*\(|delete\s+from\s+.*)"
            ),
            re.compile(r'execute\s*\(["\'].*%s.*["\']\s*%', re.IGNORECASE),
            re.compile(r"\.format\s*\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE)", re.IGNORECASE),
            re.compile(
                r'f["\'].*(?:\bSELECT\s+.+\bFROM\b|\bINSERT\s+INTO\b|\bUPDATE\s+\w+\s+SET\b|\bDELETE\s+FROM\b).*\{.*\}',
                re.IGNORECASE,
            ),
        ]

        # Pre-compile XSS patterns
        self._xss_patterns = [
            re.compile(
                r"(?i)<script\b|onerror\s*=|javascript\s*:|innerHTML\s*=|dangerouslySetInnerHTML"
            ),
            re.compile(r"innerHTML\s*="),
            re.compile(r"dangerouslySetInnerHTML"),
            re.compile(r"\.html\s*\([^)]*\+"),
        ]

        # Pre-compile command injection patterns
        self._cmd_patterns = [
            (re.compile(r"os\.system\s*\("), "os.system() with user input"),
            (
                re.compile(r"subprocess\.call\s*\([^,]*\+"),
                "subprocess.call with string concatenation",
            ),
            (
                re.compile(r"subprocess\.run\s*\([^,]*\+"),
                "subprocess.run with string concatenation",
            ),
            (re.compile(r"shell=True"), "subprocess with shell=True"),
            (re.compile(r"eval\s*\("), "eval() with potential user input"),
            (re.compile(r"exec\s*\("), "exec() with potential user input"),
        ]

        # Pre-compile path traversal patterns. Require an executable sink rather
        # than treating every relative path in docs/workflows as user input.
        self._path_patterns = [
            (
                re.compile(
                    r'(?:open|Path|os\.path\.join)\s*\([^)]*(?:["\'][^"\']*["\']\s*\+\s*[A-Za-z_(]|[A-Za-z_)][A-Za-z0-9_.()]*\s*\+\s*["\'])[^)]*\)'
                ),
                "Path operation with string concatenation",
            ),
        ]

    @staticmethod
    def _added_lines(diff: str) -> list[tuple[str, str]]:
        """Return file-aware added source lines from a unified diff."""
        current_file = ""
        result: list[tuple[str, str]] = []
        for raw_line in diff.splitlines():
            if raw_line.startswith("+++ b/"):
                current_file = raw_line[6:]
                continue
            if raw_line.startswith("+") and not raw_line.startswith("+++"):
                result.append((current_file, raw_line[1:]))
        return result

    @staticmethod
    def _executable_prefix(line: str) -> str:
        """Drop Python/YAML comments before applying executable sink heuristics."""
        return line.split("#", 1)[0]

    @staticmethod
    def _without_string_literals(line: str) -> str:
        """Remove quoted literals so operators inside values do not trigger sinks."""
        return re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', "", line)

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

        logger.info(
            f"Found {len(vulnerabilities)} security vulnerabilities"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return vulnerabilities

    async def _detect_secrets(self, diff: str, files: list[str]) -> list[dict[str, Any]]:
        """
        Detect hardcoded secrets in diff using pattern matching and entropy analysis.

        Uses configurable patterns from secret_patterns module and entropy analysis
        to reduce false positives.
        """
        secrets = []

        # Pattern-based detection on added lines only. Unified-diff metadata and
        # known fixture values are never treated as committed credentials.
        added_lines = self._added_lines(diff)
        for file, line in added_lines:
            if SecretPatterns.should_exclude_file(file):
                continue
            for secret_type, pattern in self.secret_patterns.items():
                for match in pattern.finditer(line):
                    try:
                        value = match.group(1) if match.groups() else match.group(0)
                    except IndexError:
                        value = match.group(0)
                    lower_line = line.casefold()
                    lower_value = value.casefold()
                    test_file = "/tests/" in f"/{file}" or file.startswith("tests/")
                    known_fixture = any(
                        marker in lower_line or marker in lower_value
                        for marker in (
                            "canary",
                            "akiaiosfodnn7example",
                            "ghp_1234567890abcdefghij123456789012",
                        )
                    )
                    if SecretPatterns.is_placeholder(value) or (test_file and known_fixture):
                        continue
                    if secret_type in {"token", "secret", "api_key", "password"} and not re.search(
                        r"[:=]\s*[\"']", line
                    ):
                        continue

                    confidence = "high" if has_high_entropy(value) else "medium"
                    secrets.append(
                        {
                            "type": "hardcoded_secret",
                            "secret_type": secret_type,
                            "severity": "critical",
                            "category": "security",
                            "confidence": confidence,
                            "line": self._get_line_number(diff, diff.find(line)),
                            "file": file,
                            "description": f"Hardcoded {secret_type} detected",
                            "suggestion": f"Remove hardcoded {secret_type} and use environment variables or secrets manager",
                        }
                    )

        # High-risk file check
        for file in files:
            if SecretPatterns.is_high_risk_file(file):
                secrets.append(
                    {
                        "type": "high_risk_file",
                        "secret_type": "file",
                        "severity": "high",
                        "category": "security",
                        "file": file,
                        "description": f"High-risk file detected: {file}",
                        "suggestion": "Ensure this file is in .gitignore and not committed to repository",
                    }
                )

        return secrets

    async def _check_sql_injection(self, files: list[str], diff: str) -> list[dict[str, Any]]:
        """Check for SQL injection vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        lines = [self._executable_prefix(line) for _file, line in self._added_lines(diff)]
        for pattern in self._sql_patterns:
            if any(pattern.search(line) for line in lines):
                vulnerabilities.append(
                    {
                        "type": "sql_injection",
                        "severity": "high",
                        "category": "security",
                        "description": "Potential SQL injection vulnerability detected",
                        "suggestion": "Use parameterized queries or ORM methods instead of string formatting",
                    }
                )
                break  # Only report once per diff

        return vulnerabilities

    async def _check_xss(self, files: list[str], diff: str) -> list[dict[str, Any]]:
        """Check for XSS vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        lines = [self._executable_prefix(line) for _file, line in self._added_lines(diff)]
        for pattern in self._xss_patterns:
            if any(pattern.search(line) for line in lines):
                vulnerabilities.append(
                    {
                        "type": "xss",
                        "severity": "high",
                        "category": "security",
                        "description": "Potential XSS vulnerability detected",
                        "suggestion": "Sanitize user input before rendering as HTML",
                    }
                )
                break  # Only report once per diff

        return vulnerabilities

    async def _check_dependencies(self, files: list[str]) -> list[dict[str, Any]]:
        """Leave dependency advisories to dedicated lockfile/audit scanners."""
        return []

    async def _check_command_injection(self, diff: str) -> list[dict[str, Any]]:
        """Check for potential command injection vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        lines = [self._executable_prefix(line) for _file, line in self._added_lines(diff)]
        for pattern, description in self._cmd_patterns:
            if any(pattern.search(line) for line in lines):
                vulnerabilities.append(
                    {
                        "type": "command_injection_risk",
                        "severity": "high",
                        "category": "security",
                        "description": f"Potential command injection: {description}",
                        "suggestion": "Use parameterized commands, avoid shell=True, validate all user inputs",
                    }
                )

        return vulnerabilities

    async def _check_path_traversal(self, diff: str) -> list[dict[str, Any]]:
        """Check for potential path traversal vulnerabilities using pre-compiled patterns."""
        vulnerabilities = []

        lines = [
            self._without_string_literals(self._executable_prefix(line))
            for _file, line in self._added_lines(diff)
        ]
        for pattern, description in self._path_patterns:
            if any(pattern.search(line) for line in lines):
                vulnerabilities.append(
                    {
                        "type": "path_traversal_risk",
                        "severity": "medium",
                        "category": "security",
                        "description": f"Potential path traversal: {description}",
                        "suggestion": "Validate file paths, use Path.resolve(), check for '..' in paths",
                    }
                )

        return vulnerabilities

    def _get_line_number(self, text: str, position: int) -> int:
        """Get line number for a position in text."""
        return text[:position].count("\n") + 1
