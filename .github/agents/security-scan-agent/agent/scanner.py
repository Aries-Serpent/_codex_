"""
Security scanner orchestration module.

Runs multiple security scanning tools (Bandit, Semgrep, Safety) and aggregates results.

#AFTERMATH_PATTERN_IDENTIFIED - Multi-tool security scanning
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result from a security scan."""
    
    tool: str
    findings_count: int
    sarif_path: Path | None = None
    exit_code: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SecurityScanner:
    """
    Orchestrates multiple security scanning tools.
    
    Runs:
    - Bandit: Python SAST
    - Semgrep: Multi-language SAST
    - Safety: Dependency vulnerability check
    
    #AFTERMATH_LESSON_LEARNED - Defensive scanning with error isolation per tool
    """
    
    def __init__(self, workspace: Path, output_dir: Path | None = None) -> None:
        """
        Initialize the security scanner.
        
        Args:
            workspace: Repository workspace directory
            output_dir: Directory for scan output files
        """
        self.workspace = workspace.resolve()
        self.output_dir = output_dir or (workspace / ".security-scan")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("SecurityScanner initialized: workspace=%s", self.workspace)
    
    def run_all_scans(
        self,
        skip_bandit: bool = False,
        skip_semgrep: bool = False,
        skip_safety: bool = False,
    ) -> dict[str, ScanResult]:
        """
        Run all security scans.
        
        Args:
            skip_bandit: Skip Bandit scan
            skip_semgrep: Skip Semgrep scan
            skip_safety: Skip Safety scan
            
        Returns:
            Dictionary mapping tool name to scan result
            
        #AFTERMATH_QUALITY_CHECK - Error isolation prevents one tool failure from blocking others
        """
        results = {}
        
        if not skip_bandit:
            try:
                results["bandit"] = self.run_bandit()
            except Exception as e:
                logger.error("Bandit scan failed: %s", e)
                results["bandit"] = ScanResult(
                    tool="bandit",
                    findings_count=0,
                    exit_code=-1,
                    errors=[str(e)]
                )
        
        if not skip_semgrep:
            try:
                results["semgrep"] = self.run_semgrep()
            except Exception as e:
                logger.error("Semgrep scan failed: %s", e)
                results["semgrep"] = ScanResult(
                    tool="semgrep",
                    findings_count=0,
                    exit_code=-1,
                    errors=[str(e)]
                )
        
        if not skip_safety:
            try:
                results["safety"] = self.run_safety()
            except Exception as e:
                logger.error("Safety scan failed: %s", e)
                results["safety"] = ScanResult(
                    tool="safety",
                    findings_count=0,
                    exit_code=-1,
                    errors=[str(e)]
                )
        
        logger.info("Completed %d security scans", len(results))
        return results
    
    def run_bandit(self, target: str = ".") -> ScanResult:
        """
        Run Bandit Python SAST scanner.
        
        Args:
            target: Target directory or file to scan
            
        Returns:
            Scan result with SARIF output
        """
        sarif_output = self.output_dir / "bandit.sarif"
        
        cmd = [
            "bandit",
            "-r",
            target,
            "-f",
            "sarif",
            "-o",
            str(sarif_output),
        ]
        
        logger.info("Running Bandit: %s", " ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            
            findings_count = self._count_sarif_findings(sarif_output)
            
            return ScanResult(
                tool="bandit",
                findings_count=findings_count,
                sarif_path=sarif_output if sarif_output.exists() else None,
                exit_code=result.returncode,
                metadata={"stdout": result.stdout, "stderr": result.stderr}
            )
        
        except subprocess.TimeoutExpired:
            logger.error("Bandit scan timed out")
            return ScanResult(
                tool="bandit",
                findings_count=0,
                exit_code=-1,
                errors=["Scan timed out after 300 seconds"]
            )
    
    def run_semgrep(self, config: str = "auto") -> ScanResult:
        """
        Run Semgrep multi-language SAST scanner.
        
        Args:
            config: Semgrep config (auto, p/security, p/owasp-top-10, etc.)
            
        Returns:
            Scan result with SARIF output
        """
        sarif_output = self.output_dir / "semgrep.sarif"
        
        cmd = [
            "semgrep",
            "--config",
            config,
            "--sarif",
            "--output",
            str(sarif_output),
            ".",
        ]
        
        logger.info("Running Semgrep: %s", " ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            
            findings_count = self._count_sarif_findings(sarif_output)
            
            return ScanResult(
                tool="semgrep",
                findings_count=findings_count,
                sarif_path=sarif_output if sarif_output.exists() else None,
                exit_code=result.returncode,
                metadata={"stdout": result.stdout, "stderr": result.stderr}
            )
        
        except subprocess.TimeoutExpired:
            logger.error("Semgrep scan timed out")
            return ScanResult(
                tool="semgrep",
                findings_count=0,
                exit_code=-1,
                errors=["Scan timed out after 600 seconds"]
            )
    
    def run_safety(self, requirements_file: str = "requirements.txt") -> ScanResult:
        """
        Run Safety dependency vulnerability scanner.
        
        Args:
            requirements_file: Path to requirements file
            
        Returns:
            Scan result with findings
        """
        json_output = self.output_dir / "safety.json"
        req_path = self.workspace / requirements_file
        
        if not req_path.exists():
            logger.warning("Requirements file not found: %s", req_path)
            return ScanResult(
                tool="safety",
                findings_count=0,
                errors=[f"Requirements file not found: {requirements_file}"]
            )
        
        cmd = [
            "safety",
            "check",
            "--file",
            str(req_path),
            "--json",
            "--output",
            str(json_output),
        ]
        
        logger.info("Running Safety: %s", " ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )
            
            findings_count = self._count_safety_findings(json_output)
            
            return ScanResult(
                tool="safety",
                findings_count=findings_count,
                exit_code=result.returncode,
                metadata={
                    "json_path": str(json_output) if json_output.exists() else None,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            )
        
        except subprocess.TimeoutExpired:
            logger.error("Safety scan timed out")
            return ScanResult(
                tool="safety",
                findings_count=0,
                exit_code=-1,
                errors=["Scan timed out after 120 seconds"]
            )
    
    def _count_sarif_findings(self, sarif_path: Path) -> int:
        """
        Count findings in SARIF file.
        
        Args:
            sarif_path: Path to SARIF JSON file
            
        Returns:
            Number of findings
        """
        if not sarif_path.exists():
            return 0
        
        try:
            with open(sarif_path) as f:
                sarif_data = json.load(f)
            
            # Count results across all runs
            total = 0
            for run in sarif_data.get("runs", []):
                results = run.get("results", [])
                total += len(results)
            
            return total
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse SARIF: %s", e)
            return 0
    
    def _count_safety_findings(self, json_path: Path) -> int:
        """
        Count findings in Safety JSON output.
        
        Args:
            json_path: Path to Safety JSON file
            
        Returns:
            Number of vulnerabilities found
        """
        if not json_path.exists():
            return 0
        
        try:
            with open(json_path) as f:
                safety_data = json.load(f)
            
            # Safety JSON has vulnerabilities array
            vulns = safety_data.get("vulnerabilities", [])
            return len(vulns)
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse Safety JSON: %s", e)
            return 0


# #AFTERMATH_METRIC - Scanner module with 3 tool integrations
# #AFTERMATH_PATTERN_IDENTIFIED - Error isolation pattern for multi-tool scanning
