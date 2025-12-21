"""
Security Validation Components

This module contains security vulnerability detection and validation logic.
"""

from typing import Dict, List, Any
import re
import logging

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
        """Initialize security validator with configurable patterns."""
        self.secret_patterns = SecretPatterns.get_compiled_patterns()
        self.placeholder_patterns = SecretPatterns.get_compiled_placeholder_patterns()
    
    async def scan(self, context) -> List[Dict[str, Any]]:
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
    
    async def _detect_secrets(self, diff: str, files: List[str]) -> List[Dict[str, Any]]:
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
    
    async def _check_sql_injection(self, files: List[str], diff: str) -> List[Dict[str, Any]]:
        """Check for SQL injection vulnerabilities."""
        vulnerabilities = []
        
        # Look for string formatting in SQL queries
        sql_patterns = [
            r'execute\(["\'].*%s.*["\']\s*%',
            r'\.format\(.*\).*SELECT|INSERT|UPDATE|DELETE',
            r'f["\'].*SELECT.*\{.*\}',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                vulnerabilities.append({
                    "type": "sql_injection",
                    "severity": "high",
                    "category": "security",
                    "description": "Potential SQL injection vulnerability detected",
                    "suggestion": "Use parameterized queries or ORM methods instead of string formatting"
                })
        
        return vulnerabilities
    
    async def _check_xss(self, files: List[str], diff: str) -> List[Dict[str, Any]]:
        """Check for XSS vulnerabilities."""
        vulnerabilities = []
        
        # Look for unsafe HTML rendering
        xss_patterns = [
            r'innerHTML\s*=',
            r'dangerouslySetInnerHTML',
            r'\.html\([^)]*\+',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, diff):
                vulnerabilities.append({
                    "type": "xss",
                    "severity": "high",
                    "category": "security",
                    "description": "Potential XSS vulnerability detected",
                    "suggestion": "Sanitize user input before rendering as HTML"
                })
        
        return vulnerabilities
    
    async def _check_dependencies(self, files: List[str]) -> List[Dict[str, Any]]:
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
    
    async def _check_command_injection(self, diff: str) -> List[Dict[str, Any]]:
        """Check for potential command injection vulnerabilities."""
        vulnerabilities = []
        
        # Patterns that might indicate command injection risks
        dangerous_patterns = [
            (r'os\.system\s*\(', "os.system() with user input"),
            (r'subprocess\.call\s*\([^,]*\+', "subprocess.call with string concatenation"),
            (r'subprocess\.run\s*\([^,]*\+', "subprocess.run with string concatenation"),
            (r'shell=True', "subprocess with shell=True"),
            (r'eval\s*\(', "eval() with potential user input"),
            (r'exec\s*\(', "exec() with potential user input"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, diff):
                vulnerabilities.append({
                    "type": "command_injection_risk",
                    "severity": "high",
                    "category": "security",
                    "description": f"Potential command injection: {description}",
                    "suggestion": "Use parameterized commands, avoid shell=True, validate all user inputs"
                })
        
        return vulnerabilities
    
    async def _check_path_traversal(self, diff: str) -> List[Dict[str, Any]]:
        """Check for potential path traversal vulnerabilities."""
        vulnerabilities = []
        
        # Patterns indicating path operations that might be vulnerable
        path_patterns = [
            (r'open\s*\([^,]*\+', "File open with string concatenation"),
            (r'os\.path\.join\s*\([^,]*\+', "Path join with concatenation"),
            (r'Path\s*\([^,]*\+', "Path construction with concatenation"),
        ]
        
        for pattern, description in path_patterns:
            if re.search(pattern, diff):
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
