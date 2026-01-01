"""
scanner.py - PERCEIVE Phase for infra-linter-agent.v1

Discovers and scans Infrastructure-as-Code files across the repository.
Supports: Terraform, Kubernetes, CloudFormation, Docker, Ansible

#AFTERMATH_PATTERN_IDENTIFIED: iac_scanning_patterns
#AFTERMATH_METRIC: files_scanned
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import time

# Cognitive Brain integration
try:
    from ..core.cognitive_brain import CognitiveBrain
except ImportError:
    # Fallback for testing
    class CognitiveBrain:
        def __init__(self, db_path: Optional[str] = None):
            pass
        
        def query_patterns(self, **kwargs):
            return []


@dataclass
class Finding:
    """Represents a single linting finding"""
    severity: str  # CRITICAL/HIGH/MEDIUM/LOW
    rule_id: str
    message: str
    file_path: str
    line: int
    suggested_fix: Optional[str] = None


@dataclass
class ScanResult:
    """Results from scanning a single IaC file"""
    file_path: str
    tool: str  # terraform/kubernetes/cloudformation/docker/ansible
    linter: str  # tfsec/kubectl/cfn-lint/hadolint/ansible-lint
    findings: List[Finding] = field(default_factory=list)
    scan_duration: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class IaCScanner:
    """
    PERCEIVE Phase: Discover and scan IaC files
    
    Responsibilities:
    - Find all IaC files in repository
    - Detect which IaC tools are used
    - Run appropriate linters for each tool
    - Collect and aggregate scan results
    """
    
    # File extension mappings
    TOOL_EXTENSIONS = {
        "terraform": [".tf", ".tfvars"],
        "kubernetes": [".yaml", ".yml"],  # Need context to distinguish from other YAML
        "cloudformation": [".yaml", ".yml", ".json"],  # CFN templates
        "docker": ["Dockerfile", ".dockerfile"],
        "ansible": [".yaml", ".yml"],  # Ansible playbooks
    }
    
    # Linter commands (best-effort, skip if not installed)
    LINTERS = {
        "terraform": ["tfsec", "terraform validate", "tflint"],
        "kubernetes": ["kubectl --dry-run", "kube-score"],
        "cloudformation": ["cfn-lint", "cfn-nag"],
        "docker": ["hadolint"],
        "ansible": ["ansible-lint"],
    }
    
    def __init__(self, repo_path: Path, db_path: Optional[str] = None):
        """
        Initialize IaC scanner
        
        Args:
            repo_path: Path to repository to scan
            db_path: Path to cognitive brain database (optional)
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        # Initialize cognitive brain
        db_path = db_path or os.getenv("CODEX_DB_PATH", ":memory:")
        self.brain = CognitiveBrain(db_path)
        
        # #AFTERMATH_METRIC: files_scanned
        self.files_scanned_count = 0
    
    def scan(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point: Discover and scan all IaC files
        
        Args:
            config: Configuration dict with:
                - ignore_paths: List of paths to ignore (e.g., [".terraform/", "vendor/"])
                - tools: List of specific tools to scan (defaults to all)
                - timeout: Timeout for each linter (default: 30s)
        
        Returns:
            Aggregated scan results with metadata
        """
        config = config or {}
        ignore_paths = config.get("ignore_paths", [".terraform/", "vendor/", "node_modules/"])
        tools_filter = config.get("tools", None)
        
        start_time = time.time()
        
        # Discover IaC files
        files = self._discover_iac_files(ignore_paths)
        
        # Filter by tool if specified
        if tools_filter:
            files = [f for f in files if f["tool"] in tools_filter]
        
        # Scan each file
        results = []
        for file_info in files:
            try:
                result = self._scan_file(file_info, config)
                results.append(result)
                self.files_scanned_count += 1
            except Exception as e:
                # Best-effort: continue scanning other files
                results.append(ScanResult(
                    file_path=file_info["path"],
                    tool=file_info["tool"],
                    linter="unknown",
                    success=False,
                    error_message=str(e)
                ))
        
        duration = time.time() - start_time
        
        # #AFTERMATH_PATTERN_IDENTIFIED: iac_scanning_patterns
        return self._aggregate_results(results, duration)
    
    def _discover_iac_files(self, ignore_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Find all IaC files in repository
        
        Args:
            ignore_paths: List of path patterns to ignore
        
        Returns:
            List of file info dicts with path and detected tool
        """
        files = []
        
        for root, dirs, filenames in os.walk(self.repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not any(ign in str(Path(root) / d) for ign in ignore_paths)]
            
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.repo_path)
                
                # Skip if in ignore list
                if any(ign in str(rel_path) for ign in ignore_paths):
                    continue
                
                # Detect tool
                tool = self._detect_tool(file_path, rel_path)
                if tool:
                    files.append({
                        "path": str(file_path),
                        "relative_path": str(rel_path),
                        "tool": tool
                    })
        
        return files
    
    def _detect_tool(self, file_path: Path, rel_path: Path) -> Optional[str]:
        """
        Determine which IaC tool this file belongs to
        
        Args:
            file_path: Absolute path to file
            rel_path: Relative path from repo root
        
        Returns:
            Tool name or None if not IaC file
        """
        filename = file_path.name
        
        # Docker: Dockerfile
        if filename.lower().startswith("dockerfile"):
            return "docker"
        
        # Terraform: .tf or .tfvars
        if file_path.suffix in [".tf", ".tfvars"]:
            return "terraform"
        
        # YAML/JSON files need content-based detection
        if file_path.suffix in [".yaml", ".yml", ".json"]:
            try:
                content = file_path.read_text()[:500]  # Read first 500 chars
                
                # Kubernetes: has apiVersion and kind
                if "apiVersion:" in content and "kind:" in content:
                    return "kubernetes"
                
                # CloudFormation: has AWSTemplateFormatVersion or Resources
                if "AWSTemplateFormatVersion" in content or '"Resources"' in content:
                    return "cloudformation"
                
                # Ansible: has playbook markers
                if "- hosts:" in content or "- name:" in content and "tasks:" in content:
                    return "ansible"
                
            except Exception:
                # Best-effort: if can't read file, skip it
                pass
        
        return None
    
    def _scan_file(self, file_info: Dict[str, Any], config: Dict[str, Any]) -> ScanResult:
        """
        Run appropriate linter(s) for this file
        
        Args:
            file_info: Dict with path and tool type
            config: Scan configuration
        
        Returns:
            ScanResult with findings
        """
        tool = file_info["tool"]
        file_path = Path(file_info["path"])
        
        if tool == "terraform":
            return self._scan_terraform(file_path, config)
        elif tool == "kubernetes":
            return self._scan_kubernetes(file_path, config)
        elif tool == "cloudformation":
            return self._scan_cloudformation(file_path, config)
        elif tool == "docker":
            return self._scan_docker(file_path, config)
        elif tool == "ansible":
            return self._scan_ansible(file_path, config)
        else:
            return ScanResult(
                file_path=str(file_path),
                tool=tool,
                linter="unknown",
                success=False,
                error_message=f"Unsupported tool: {tool}"
            )
    
    def _scan_terraform(self, file_path: Path, config: Dict[str, Any]) -> ScanResult:
        """
        Scan Terraform file with tfsec
        
        Best-effort: If tfsec not installed, returns empty result
        """
        start_time = time.time()
        findings = []
        
        try:
            # Try tfsec first (most common)
            result = subprocess.run(
                ["tfsec", str(file_path), "--format=json", "--no-color"],
                capture_output=True,
                timeout=config.get("timeout", 30),
                cwd=self.repo_path
            )
            
            if result.returncode == 0 or result.returncode == 1:  # 1 = findings found
                try:
                    output = json.loads(result.stdout.decode())
                    for issue in output.get("results", []):
                        findings.append(Finding(
                            severity=issue.get("severity", "MEDIUM").upper(),
                            rule_id=issue.get("rule_id", "unknown"),
                            message=issue.get("description", "No description"),
                            file_path=str(file_path),
                            line=issue.get("location", {}).get("start_line", 0),
                            suggested_fix=issue.get("resolution", None)
                        ))
                except json.JSONDecodeError:
                    pass  # Best-effort: continue without findings
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Best-effort: tfsec not installed or timed out
            pass
        
        duration = time.time() - start_time
        return ScanResult(
            file_path=str(file_path),
            tool="terraform",
            linter="tfsec",
            findings=findings,
            scan_duration=duration,
            success=True
        )
    
    def _scan_kubernetes(self, file_path: Path, config: Dict[str, Any]) -> ScanResult:
        """
        Scan Kubernetes manifest with kube-score
        
        Best-effort: If kube-score not installed, returns empty result
        """
        start_time = time.time()
        findings = []
        
        try:
            result = subprocess.run(
                ["kube-score", "score", str(file_path), "--output-format=json"],
                capture_output=True,
                timeout=config.get("timeout", 30)
            )
            
            if result.returncode == 0 or result.returncode == 1:
                try:
                    output = json.loads(result.stdout.decode())
                    for obj in output:
                        for check in obj.get("checks", []):
                            if check.get("grade", 10) < 7:  # Failed or warning
                                severity = "HIGH" if check.get("grade", 10) < 5 else "MEDIUM"
                                findings.append(Finding(
                                    severity=severity,
                                    rule_id=check.get("check", {}).get("id", "unknown"),
                                    message=check.get("comments", ["No details"])[0],
                                    file_path=str(file_path),
                                    line=0
                                ))
                except json.JSONDecodeError:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Best-effort
        
        duration = time.time() - start_time
        return ScanResult(
            file_path=str(file_path),
            tool="kubernetes",
            linter="kube-score",
            findings=findings,
            scan_duration=duration,
            success=True
        )
    
    def _scan_cloudformation(self, file_path: Path, config: Dict[str, Any]) -> ScanResult:
        """
        Scan CloudFormation template with cfn-lint
        
        Best-effort: If cfn-lint not installed, returns empty result
        """
        start_time = time.time()
        findings = []
        
        try:
            result = subprocess.run(
                ["cfn-lint", str(file_path), "--format=json"],
                capture_output=True,
                timeout=config.get("timeout", 30)
            )
            
            if result.returncode == 0 or result.returncode == 2:  # 2 = violations found
                try:
                    output = json.loads(result.stdout.decode())
                    for issue in output:
                        severity_map = {"error": "HIGH", "warning": "MEDIUM", "informational": "LOW"}
                        findings.append(Finding(
                            severity=severity_map.get(issue.get("Level", "warning"), "MEDIUM"),
                            rule_id=issue.get("Rule", {}).get("Id", "unknown"),
                            message=issue.get("Message", "No message"),
                            file_path=str(file_path),
                            line=issue.get("Location", {}).get("Start", {}).get("LineNumber", 0)
                        ))
                except json.JSONDecodeError:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Best-effort
        
        duration = time.time() - start_time
        return ScanResult(
            file_path=str(file_path),
            tool="cloudformation",
            linter="cfn-lint",
            findings=findings,
            scan_duration=duration,
            success=True
        )
    
    def _scan_docker(self, file_path: Path, config: Dict[str, Any]) -> ScanResult:
        """
        Scan Dockerfile with hadolint
        
        Best-effort: If hadolint not installed, returns empty result
        """
        start_time = time.time()
        findings = []
        
        try:
            result = subprocess.run(
                ["hadolint", str(file_path), "--format=json"],
                capture_output=True,
                timeout=config.get("timeout", 30)
            )
            
            if result.returncode == 0 or result.returncode == 1:
                try:
                    output = json.loads(result.stdout.decode())
                    for issue in output:
                        severity_map = {"error": "HIGH", "warning": "MEDIUM", "info": "LOW", "style": "LOW"}
                        findings.append(Finding(
                            severity=severity_map.get(issue.get("level", "info"), "MEDIUM"),
                            rule_id=issue.get("code", "unknown"),
                            message=issue.get("message", "No message"),
                            file_path=str(file_path),
                            line=issue.get("line", 0)
                        ))
                except json.JSONDecodeError:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Best-effort
        
        duration = time.time() - start_time
        return ScanResult(
            file_path=str(file_path),
            tool="docker",
            linter="hadolint",
            findings=findings,
            scan_duration=duration,
            success=True
        )
    
    def _scan_ansible(self, file_path: Path, config: Dict[str, Any]) -> ScanResult:
        """
        Scan Ansible playbook with ansible-lint
        
        Best-effort: If ansible-lint not installed, returns empty result
        """
        start_time = time.time()
        findings = []
        
        try:
            result = subprocess.run(
                ["ansible-lint", str(file_path), "--format=json"],
                capture_output=True,
                timeout=config.get("timeout", 30)
            )
            
            if result.returncode == 0 or result.returncode == 2:
                try:
                    output = json.loads(result.stdout.decode())
                    for issue in output:
                        findings.append(Finding(
                            severity="MEDIUM",  # ansible-lint doesn't have severity levels
                            rule_id=issue.get("rule", {}).get("id", "unknown"),
                            message=issue.get("message", "No message"),
                            file_path=str(file_path),
                            line=issue.get("linenumber", 0)
                        ))
                except json.JSONDecodeError:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # Best-effort
        
        duration = time.time() - start_time
        return ScanResult(
            file_path=str(file_path),
            tool="ansible",
            linter="ansible-lint",
            findings=findings,
            scan_duration=duration,
            success=True
        )
    
    def _aggregate_results(self, results: List[ScanResult], total_duration: float) -> Dict[str, Any]:
        """
        Aggregate scan results into summary format
        
        Args:
            results: List of ScanResult objects
            total_duration: Total scan duration in seconds
        
        Returns:
            Aggregated results dict
        """
        # Count findings by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        all_findings = []
        tools_detected = set()
        
        for result in results:
            tools_detected.add(result.tool)
            for finding in result.findings:
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
                all_findings.append(finding)
        
        return {
            "files_scanned": len(results),
            "tools_detected": sorted(list(tools_detected)),
            "scan_results": results,
            "total_findings": len(all_findings),
            "severity_counts": severity_counts,
            "duration_seconds": round(total_duration, 2),
            "successful_scans": sum(1 for r in results if r.success),
            "failed_scans": sum(1 for r in results if not r.success)
        }
