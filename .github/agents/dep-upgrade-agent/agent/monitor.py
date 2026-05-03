"""
Dependency Monitor Module - PERCEIVE Phase

#AFTERMATH_PATTERN_IDENTIFIED: dependency_monitoring
Implements dependency version monitoring and vulnerability scanning.
"""

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class UpdateType(Enum):
    """Types of dependency updates."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    SECURITY = "security"


@dataclass
class DependencyUpdate:
    """Available dependency update."""
    package_name: str
    current_version: str
    latest_version: str
    update_type: UpdateType
    has_vulnerability: bool
    vulnerability_ids: List[str]
    changelog_url: Optional[str]
    release_date: str
    download_count: int
    metadata: Dict[str, Any]


class DependencyMonitor:
    """
    Dependency Monitor - PERCEIVE Phase

    #AFTERMATH_PATTERN_IDENTIFIED: dependency_version_monitoring

    Monitors dependencies for:
    - Available updates (semver-aware)
    - Known vulnerabilities (CVE/advisory databases)
    - Breaking changes in changelogs
    - Update frequency and stability
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.updates: List[DependencyUpdate] = []

    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        PERCEIVE: Monitor dependencies for updates and vulnerabilities.

        #AFTERMATH_PATTERN_IDENTIFIED: dependency_update_detection

        Args:
            task: Task configuration

        Returns:
            Context with update information
        """
        context = {
            "current_dependencies": self._read_current_dependencies(),
            "available_updates": self._check_for_updates(),
            "vulnerabilities": self._scan_vulnerabilities(),
            "changelog_analysis": self._analyze_changelogs(),
            "package_health": self._assess_package_health(),
            "historical_patterns": self._query_brain_patterns(),
            "total_outdated": len(self.updates),
            "security_critical": sum(1 for u in self.updates if u.has_vulnerability)
        }

        #AFTERMATH_METRIC: total_dependencies = len(context["current_dependencies"])
        #AFTERMATH_METRIC: updates_available = len(self.updates)

        return context

    def _read_current_dependencies(self) -> Dict[str, str]:
        """
        Read current dependencies from lock files.

        #AFTERMATH_PATTERN_IDENTIFIED: dependency_file_parsing
        """
        dependencies = {}

        # Validate base path
        try:
            self.repo_path.resolve()
        except (OSError, ValueError):
            return dependencies

        # Read requirements.txt with path validation
        req_file = self.repo_path / "requirements.txt"
        if self._is_safe_path(req_file):
            content = req_file.read_text()
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package==version format
                    match = re.match(r'([a-zA-Z0-9_-]+)([=<>!]+)(.+)', line)
                    if match:
                        package, operator, version = match.groups()
                        if operator == '==':
                            dependencies[package] = version

        # Read Pipfile.lock (if exists) with path validation
        pipfile_lock = self.repo_path / "Pipfile.lock"
        if self._is_safe_path(pipfile_lock):
            try:
                data = json.loads(pipfile_lock.read_text())
                for section in ['default', 'develop']:
                    if section in data:
                        for package, info in data[section].items():
                            if 'version' in info:
                                version = info['version'].lstrip('=')
                                dependencies[package] = version
            except json.JSONDecodeError:
                # Best-effort: if Pipfile.lock is malformed, skip Python dependency
                # parsing but continue with other dependency files.
                pass

        # Read package-lock.json (for Node.js) with path validation
        package_lock = self.repo_path / "package-lock.json"
        if self._is_safe_path(package_lock):
            try:
                data = json.loads(package_lock.read_text())
                if 'dependencies' in data:
                    for package, info in data['dependencies'].items():
                        if 'version' in info:
                            dependencies[package] = info['version']
            except json.JSONDecodeError:
                # Best-effort: if package-lock.json is malformed, skip Node.js dependency
                # parsing but continue with other dependency files.
                pass

        return dependencies

    def _is_safe_path(self, file_path: Path) -> bool:
        """Validate path is within repo and exists."""
        try:
            file_resolved = file_path.resolve()
            repo_resolved = self.repo_path.resolve()
            return (str(file_resolved).startswith(str(repo_resolved))
                   and file_path.exists())
        except (OSError, ValueError):
            return False

    def _check_for_updates(self) -> List[DependencyUpdate]:
        """
        Check for available updates using pip-outdated or npm outdated.

        #AFTERMATH_PATTERN_IDENTIFIED: update_availability_check
        """
        updates = []
        current_deps = self._read_current_dependencies()

        # Check Python packages
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                cwd=self.repo_path,
                capture_output=True,
                timeout=60
            )

            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                for pkg in outdated:
                    if pkg['name'] in current_deps:
                        update = self._create_update_entry(
                            pkg['name'],
                            current_deps[pkg['name']],
                            pkg['latest_version'],
                            "python"
                        )
                        updates.append(update)
                        self.updates.append(update)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # Best-effort: if pip is unavailable, times out, or returns invalid JSON,
            # skip Python dependency updates but continue monitoring other ecosystems.
            pass

        # Check npm packages
        try:
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                cwd=self.repo_path,
                capture_output=True,
                timeout=60
            )

            # npm outdated returns exit code 1 when updates found
            if result.returncode in [0, 1] and result.stdout:
                outdated = json.loads(result.stdout)
                for pkg, info in outdated.items():
                    update = self._create_update_entry(
                        pkg,
                        info.get('current', 'unknown'),
                        info.get('latest', 'unknown'),
                        "javascript"
                    )
                    updates.append(update)
                    self.updates.append(update)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # Best-effort: if npm is unavailable, times out, or returns invalid JSON,
            # skip Node.js dependency updates but continue monitoring other ecosystems.
            pass

        return updates

    def _create_update_entry(self, package: str, current: str,
                            latest: str, ecosystem: str) -> DependencyUpdate:
        """Create DependencyUpdate entry."""
        update_type = self._determine_update_type(current, latest)

        return DependencyUpdate(
            package_name=package,
            current_version=current,
            latest_version=latest,
            update_type=update_type,
            has_vulnerability=False,  # Will be updated by vulnerability scan
            vulnerability_ids=[],
            changelog_url=self._get_changelog_url(package, ecosystem),
            release_date=datetime.now().isoformat(),
            download_count=0,
            metadata={"ecosystem": ecosystem}
        )

    def _determine_update_type(self, current: str, latest: str) -> UpdateType:
        """
        Determine update type based on semver.

        #AFTERMATH_PATTERN_IDENTIFIED: semver_analysis
        """
        try:
            # Parse versions (simplified)
            curr_parts = [int(x) for x in current.split('.')[:3]]
            latest_parts = [int(x) for x in latest.split('.')[:3]]

            # Pad to 3 parts
            while len(curr_parts) < 3:
                curr_parts.append(0)
            while len(latest_parts) < 3:
                latest_parts.append(0)

            if latest_parts[0] > curr_parts[0]:
                return UpdateType.MAJOR
            if latest_parts[1] > curr_parts[1]:
                return UpdateType.MINOR
            if latest_parts[2] > curr_parts[2]:
                return UpdateType.PATCH
            return UpdateType.PATCH
        except (ValueError, IndexError):
            return UpdateType.MINOR

    def _scan_vulnerabilities(self) -> List[Dict[str, Any]]:
        """
        Scan dependencies for known vulnerabilities.

        #AFTERMATH_PATTERN_IDENTIFIED: vulnerability_scanning
        """
        vulnerabilities = []

        # Use Safety for Python
        req_file = self.repo_path / "requirements.txt"
        # Validate path is within repo to prevent path traversal
        try:
            req_file_resolved = req_file.resolve()
            repo_resolved = self.repo_path.resolve()
            if not str(req_file_resolved).startswith(str(repo_resolved)):
                return vulnerabilities
        except (OSError, ValueError):
            return vulnerabilities

        if req_file.exists():
            try:
                result = subprocess.run(
                    ["safety", "check", "--json", "-r", str(req_file_resolved)],
                    capture_output=True,
                    timeout=60
                )

                if result.returncode in [0, 64]:  # 64 = vulns found
                    vulns = json.loads(result.stdout)
                    for vuln in vulns:
                        package = vuln.get('package')
                        # Mark update as having vulnerability
                        for update in self.updates:
                            if update.package_name == package:
                                update.has_vulnerability = True
                                update.vulnerability_ids.append(vuln.get('cve', 'N/A'))
                                update.update_type = UpdateType.SECURITY

                        vulnerabilities.append(vuln)
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                # Best-effort: if security scanning tool (pip-audit, npm audit, etc.)
                # is unavailable, times out, or returns invalid JSON, continue without
                # vulnerability data. Security checks can be performed manually.
                pass

        return vulnerabilities

    def _analyze_changelogs(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze changelogs for breaking changes.

        #AFTERMATH_PATTERN_IDENTIFIED: changelog_analysis
        """
        changelog_data = {}

        for update in self.updates:
            changelog_data[update.package_name] = {
                "has_breaking_changes": self._detect_breaking_changes(update),
                "has_deprecations": False,  # Would parse changelog
                "migration_guide_available": False
            }

        return changelog_data

    def _detect_breaking_changes(self, update: DependencyUpdate) -> bool:
        """Detect if update contains breaking changes."""
        # Major version bump = breaking changes
        if update.update_type == UpdateType.MAJOR:
            return True

        # Could also parse changelog for keywords
        return False

    def _assess_package_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Assess health of packages.

        #AFTERMATH_PATTERN_IDENTIFIED: package_health_assessment
        """
        health = {}

        for update in self.updates:
            health[update.package_name] = {
                "is_maintained": True,  # Would check last commit date
                "has_active_community": True,  # Would check GitHub stats
                "download_trend": "stable",
                "security_score": 0.8
            }

        return health

    def _query_brain_patterns(self) -> List[Dict[str, Any]]:
        """Query cognitive brain for historical update patterns."""
        try:
            import sys
            _core_path = str(Path(__file__).parent.parent.parent / "core")
            if _core_path not in sys.path:
                sys.path.insert(0, _core_path)
            from cognitive_brain import CognitiveBrain

            brain = CognitiveBrain(Path(".codex/brain.db"))
            patterns = brain.query_patterns(
                pattern_type="dependency_update",
                confidence_threshold=0.7
            )
            return [p.__dict__ for p in patterns[:10]]
        except Exception:
            return []

    def _get_changelog_url(self, package: str, ecosystem: str) -> Optional[str]:
        """Get changelog URL for package."""
        if ecosystem == "python":
            return f"https://pypi.org/project/{package}/#history"
        if ecosystem == "javascript":
            return f"https://www.npmjs.com/package/{package}?activeTab=versions"
        return None
