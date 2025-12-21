"""
Security Validation Components

This module contains security vulnerability detection and validation logic.
"""

from typing import Dict, List, Any
import re
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """
    Security vulnerability detection and validation.
    
    Scans for:
    - Hardcoded secrets
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Insecure dependencies
    - Common security anti-patterns
    """
    
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
        secrets = await self._detect_secrets(context.diff)
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
        
        logger.info(f"Found {len(vulnerabilities)} security vulnerabilities")
        return vulnerabilities
    
    async def _detect_secrets(self, diff: str) -> List[Dict[str, Any]]:
        """
        Detect hardcoded secrets in diff.
        
        Uses regex patterns to identify common secret patterns.
        """
        secrets = []
        
        # Define secret patterns
        patterns = {
            "api_key": r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']',
            "password": r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            "token": r'token["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']',
            "secret": r'secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{16,})["\']',
        }
        
        for secret_type, pattern in patterns.items():
            matches = re.finditer(pattern, diff, re.IGNORECASE)
            for match in matches:
                # Skip if it's obviously a placeholder
                value = match.group(1)
                if any(placeholder in value.lower() for placeholder in ["example", "placeholder", "your_", "xxx"]):
                    continue
                
                secrets.append({
                    "type": "hardcoded_secret",
                    "secret_type": secret_type,
                    "severity": "critical",
                    "category": "security",
                    "line": self._get_line_number(diff, match.start()),
                    "description": f"Hardcoded {secret_type} detected",
                    "suggestion": f"Remove hardcoded {secret_type} and use environment variables or secrets manager"
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
        
        # Check if dependency files are modified
        dep_files = ["requirements.txt", "package.json", "Gemfile", "pom.xml"]
        if any(f in files for f in dep_files):
            vulnerabilities.append({
                "type": "dependency_update",
                "severity": "low",
                "category": "security",
                "description": "Dependencies modified - ensure security scan is run",
                "suggestion": "Run dependency security scanner (e.g., Snyk, Dependabot)"
            })
        
        return vulnerabilities
    
    def _get_line_number(self, text: str, position: int) -> int:
        """Get line number for a position in text."""
        return text[:position].count('\n') + 1
