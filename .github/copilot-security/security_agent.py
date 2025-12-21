"""
GitHub Copilot Security Agent for autonomous vulnerability resolution.

This module provides core functionality for:
- Fetching security alerts from GitHub Advanced Security
- Generating fixes for common vulnerability patterns
- Applying fixes with validation
- Learning from fix outcomes

Author: mbaetiong
Generated: 2025-12-21
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

logger = logging.getLogger(__name__)


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    WARNING = "warning"
    NOTE = "note"


@dataclass
class SecurityVulnerability:
    """Represents a detected security vulnerability."""
    id: str
    rule_id: str
    severity: str
    category: str
    file_path: str
    line_start: int
    line_end: int
    description: str
    cwe_id: Optional[str] = None
    fix_suggestion: Optional[str] = None
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityFix:
    """Represents a generated security fix."""
    vulnerability_id: str
    file_path: str
    original_code: str
    fixed_code: str
    explanation: str
    confidence: float
    test_cases: List[str] = field(default_factory=list)
    validated: bool = False


class CopilotSecurityAgent:
    """Main security agent for GitHub Copilot."""
    
    def __init__(
        self,
        repo_path: str,
        github_token: Optional[str] = None,
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
    ):
        """Initialize the security agent.
        
        Args:
            repo_path: Path to the repository
            github_token: GitHub API token (defaults to GITHUB_TOKEN env var)
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
        """
        self.repo_path = Path(repo_path)
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.repo_owner = repo_owner or self._extract_repo_info()[0]
        self.repo_name = repo_name or self._extract_repo_info()[1]
        self.vulnerability_cache: Dict[str, SecurityVulnerability] = {}
        self.fix_patterns = self._load_fix_patterns()
        
    def _extract_repo_info(self) -> Tuple[str, str]:
        """Extract repository owner and name from git config or environment."""
        # Try environment variables first (CI environment)
        github_repository = os.environ.get("GITHUB_REPOSITORY", "")
        if "/" in github_repository:
            owner, name = github_repository.split("/", 1)
            return owner, name
        
        # Try to extract from git config
        try:
            import subprocess
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Parse GitHub URL
                if "github.com" in url:
                    # Handle both SSH and HTTPS URLs
                    if url.startswith("git@github.com:"):
                        parts = url.replace("git@github.com:", "").replace(".git", "").split("/")
                    elif "github.com/" in url:
                        parts = url.split("github.com/")[1].replace(".git", "").split("/")
                    else:
                        parts = []
                    
                    if len(parts) >= 2:
                        return parts[0], parts[1]
        except Exception as e:
            logger.warning(f"Could not extract repo info from git: {e}")
        
        return "unknown-owner", "unknown-repo"
    
    def _load_fix_patterns(self) -> Dict[str, Any]:
        """Load fix patterns from YAML configuration."""
        patterns_file = Path(__file__).parent / "fix_patterns.yaml"
        if patterns_file.exists():
            try:
                import yaml
                with open(patterns_file) as f:
                    return yaml.safe_load(f).get("fix_patterns", {})
            except Exception as e:
                logger.warning(f"Could not load fix patterns: {e}")
        
        # Return default patterns
        return {
            "sql_injection": {
                "description": "Use parameterized queries",
                "priority": 1,
            },
            "xss": {
                "description": "Escape user input",
                "priority": 1,
            },
            "path_traversal": {
                "description": "Validate and sanitize file paths",
                "priority": 1,
            },
            "hardcoded_secret": {
                "description": "Use environment variables",
                "priority": 1,
            },
            "command_injection": {
                "description": "Sanitize command inputs",
                "priority": 1,
            },
        }
    
    async def scan_for_vulnerabilities(
        self,
        branch: Optional[str] = None,
    ) -> List[SecurityVulnerability]:
        """Actively scan for vulnerabilities across the repository.
        
        Args:
            branch: Optional branch name to scan (defaults to current branch)
            
        Returns:
            List of detected vulnerabilities
        """
        if not HAS_AIOHTTP:
            logger.error("aiohttp not available - cannot fetch GitHub security alerts")
            return []
        
        vulnerabilities = []
        
        # Get GitHub Security alerts
        try:
            github_vulns = await self._fetch_github_security_alerts(branch)
            vulnerabilities.extend(github_vulns)
        except Exception as e:
            logger.error(f"Error fetching GitHub security alerts: {e}")
        
        # Run local AST-based scanning using existing tools
        try:
            local_vulns = await self._run_local_security_scan()
            vulnerabilities.extend(local_vulns)
        except Exception as e:
            logger.error(f"Error running local security scan: {e}")
        
        # Cache vulnerabilities
        for vuln in vulnerabilities:
            self.vulnerability_cache[vuln.id] = vuln
        
        # Prioritize by severity
        vulnerabilities = self._prioritize_vulnerabilities(vulnerabilities)
        
        return vulnerabilities
    
    async def _fetch_github_security_alerts(
        self,
        branch: Optional[str] = None,
    ) -> List[SecurityVulnerability]:
        """Fetch security alerts from GitHub Advanced Security."""
        if not self.github_token:
            logger.warning("No GitHub token available - cannot fetch security alerts")
            return []
        
        vulnerabilities = []
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        # Get code scanning alerts
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/code-scanning/alerts"
        params = {"state": "open"}
        if branch:
            params["ref"] = branch
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        alerts = await response.json()
                        for alert in alerts:
                            vuln = self._parse_github_alert(alert)
                            if vuln:
                                vulnerabilities.append(vuln)
                    elif response.status == 404:
                        logger.info("Code scanning not enabled for this repository")
                    else:
                        logger.warning(f"GitHub API returned status {response.status}")
        except Exception as e:
            logger.error(f"Error fetching GitHub alerts: {e}")
        
        return vulnerabilities
    
    def _parse_github_alert(self, alert: Dict[str, Any]) -> Optional[SecurityVulnerability]:
        """Parse a GitHub code scanning alert into a SecurityVulnerability."""
        try:
            most_recent = alert.get("most_recent_instance", {})
            location = most_recent.get("location", {})
            rule = alert.get("rule", {})
            
            return SecurityVulnerability(
                id=f"github-{alert['number']}",
                rule_id=rule.get("id", "unknown"),
                severity=rule.get("severity", "medium"),
                category=rule.get("tags", ["security"])[0] if rule.get("tags") else "security",
                file_path=location.get("path", "unknown"),
                line_start=location.get("start_line", 0),
                line_end=location.get("end_line", 0),
                description=rule.get("description", alert.get("rule", {}).get("name", "Unknown vulnerability")),
                cwe_id=self._extract_cwe_id(rule),
                confidence=0.9,  # GitHub alerts are high confidence
                metadata={
                    "alert_url": alert.get("html_url", ""),
                    "created_at": alert.get("created_at", ""),
                    "state": alert.get("state", ""),
                },
            )
        except Exception as e:
            logger.warning(f"Error parsing GitHub alert: {e}")
            return None
    
    def _extract_cwe_id(self, rule: Dict[str, Any]) -> Optional[str]:
        """Extract CWE ID from rule metadata."""
        cwe_tags = rule.get("tags", [])
        for tag in cwe_tags:
            if tag.startswith("external/cwe/cwe-"):
                return tag.replace("external/cwe/cwe-", "CWE-")
        return None
    
    async def _run_local_security_scan(self) -> List[SecurityVulnerability]:
        """Run local security scanning using available tools."""
        vulnerabilities = []
        
        # Use existing security scanning scripts
        scripts_dir = self.repo_path / "scripts" / "security"
        if not scripts_dir.exists():
            return vulnerabilities
        
        # Check for bandit
        try:
            import subprocess
            result = subprocess.run(
                ["bandit", "-r", "-f", "json", str(self.repo_path / "src")],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0 or result.stdout:
                bandit_results = json.loads(result.stdout)
                for issue in bandit_results.get("results", []):
                    vuln = SecurityVulnerability(
                        id=f"bandit-{issue['test_id']}-{issue['line_number']}",
                        rule_id=issue['test_id'],
                        severity=issue['issue_severity'].lower(),
                        category="security",
                        file_path=issue['filename'],
                        line_start=issue['line_number'],
                        line_end=issue['line_number'],
                        description=issue['issue_text'],
                        cwe_id=issue.get('cwe', {}).get('id', None),
                        confidence=0.7,
                    )
                    vulnerabilities.append(vuln)
        except Exception as e:
            logger.debug(f"Bandit scan not available: {e}")
        
        return vulnerabilities
    
    def _prioritize_vulnerabilities(
        self,
        vulnerabilities: List[SecurityVulnerability],
    ) -> List[SecurityVulnerability]:
        """Prioritize vulnerabilities by severity and confidence."""
        severity_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
            "warning": 4,
            "note": 5,
        }
        
        return sorted(
            vulnerabilities,
            key=lambda v: (
                severity_order.get(v.severity.lower(), 999),
                -v.confidence,
            ),
        )
    
    async def generate_fix(self, vulnerability: SecurityVulnerability) -> Optional[SecurityFix]:
        """Generate fix for a specific vulnerability.
        
        Args:
            vulnerability: The vulnerability to fix
            
        Returns:
            SecurityFix object if fix can be generated, None otherwise
        """
        # Load the vulnerable code
        file_path = self.repo_path / vulnerability.file_path
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            vulnerable_code = ''.join(
                lines[vulnerability.line_start-1:vulnerability.line_end]
            )
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
        
        # Use existing security codemods
        fix = await self._generate_fix_using_codemods(vulnerability, vulnerable_code)
        
        if fix:
            return SecurityFix(
                vulnerability_id=vulnerability.id,
                file_path=vulnerability.file_path,
                original_code=vulnerable_code,
                fixed_code=fix['code'],
                explanation=fix['explanation'],
                confidence=fix['confidence'],
                test_cases=fix.get('test_cases', []),
            )
        
        return None
    
    async def _generate_fix_using_codemods(
        self,
        vuln: SecurityVulnerability,
        vulnerable_code: str,
    ) -> Optional[Dict[str, Any]]:
        """Generate fix using existing security codemods."""
        scripts_dir = self.repo_path / "scripts" / "security" / "codemods"
        
        # Map vulnerability types to codemods
        codemod_mapping = {
            "sql": "fix_sql_injection.py",
            "subprocess": "fix_subprocess.py",
            "secret": "fix_hardcoded_secrets.py",
            "command": "fix_subprocess.py",
        }
        
        # Find appropriate codemod
        codemod_file = None
        for vuln_type, script_name in codemod_mapping.items():
            if vuln_type in vuln.rule_id.lower() or vuln_type in vuln.category.lower():
                codemod_file = scripts_dir / script_name
                break
        
        if not codemod_file or not codemod_file.exists():
            return None
        
        # Apply codemod
        try:
            import subprocess
            result = subprocess.run(
                ["python", str(codemod_file), str(self.repo_path / vuln.file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                # Read the fixed file
                with open(self.repo_path / vuln.file_path, 'r') as f:
                    fixed_content = f.read()
                
                return {
                    "code": fixed_content,
                    "explanation": f"Applied {codemod_file.name} to fix {vuln.rule_id}",
                    "confidence": 0.8,
                    "test_cases": [],
                }
        except Exception as e:
            logger.error(f"Error applying codemod: {e}")
        
        return None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of security agent status."""
        return {
            "repo": f"{self.repo_owner}/{self.repo_name}",
            "cached_vulnerabilities": len(self.vulnerability_cache),
            "has_github_token": bool(self.github_token),
            "fix_patterns_loaded": len(self.fix_patterns),
        }


async def main():
    """Example usage of the security agent."""
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    agent = CopilotSecurityAgent(repo_path)
    
    print(f"🔍 Scanning {agent.repo_owner}/{agent.repo_name} for vulnerabilities...")
    
    vulnerabilities = await agent.scan_for_vulnerabilities()
    
    print(f"\n✅ Found {len(vulnerabilities)} vulnerabilities:\n")
    
    for vuln in vulnerabilities[:10]:  # Show first 10
        print(f"  [{vuln.severity.upper()}] {vuln.rule_id}")
        print(f"    File: {vuln.file_path}:{vuln.line_start}")
        print(f"    Description: {vuln.description}")
        print()
    
    if vulnerabilities:
        print(f"\n🔧 Generating fix for first vulnerability...")
        fix = await agent.generate_fix(vulnerabilities[0])
        if fix:
            print(f"✅ Fix generated:")
            print(f"  Confidence: {fix.confidence:.0%}")
            print(f"  Explanation: {fix.explanation}")
        else:
            print(f"❌ No fix could be generated")


if __name__ == "__main__":
    asyncio.run(main())
