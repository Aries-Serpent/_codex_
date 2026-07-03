"""CVE Database Monitor for Dependency Management.

Keeps track of known vulnerabilities and checks dependencies.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from codex.logging.structured_logger import logger


@dataclass
class CVEEntry:
    """CVE vulnerability entry."""

    cve_id: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    package: str
    affected_versions: list[str]
    fixed_in: str | None = None
    description: str = ""
    published: str = ""

    def affects(self, version: str) -> bool:
        """Check if CVE affects given version."""
        return version in self.affected_versions


@dataclass
class CVEDatabase:
    """CVE vulnerability database."""

    entries: dict[str, list[CVEEntry]] = field(default_factory=dict)
    last_updated: str = ""
    checksum: str = ""

    def add_cve(self, cve: CVEEntry) -> None:
        """Add CVE to database."""
        if cve.package not in self.entries:
            self.entries[cve.package] = []
        self.entries[cve.package].append(cve)
        self._update_checksum()

    def _update_checksum(self) -> None:
        """Update database checksum."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        self.checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
        self.last_updated = datetime.now(timezone.utc).isoformat()

    def check_package(self, package: str, version: str) -> list[CVEEntry]:
        """Check package for vulnerabilities."""
        vulns = []
        for cve in self.entries.get(package, []):
            if cve.affects(version):
                vulns.append(cve)
        return vulns

    def check_all(self, dependencies: dict[str, str]) -> dict[str, list[CVEEntry]]:
        """Check all dependencies for vulnerabilities."""
        results = {}
        for package, version in dependencies.items():
            vulns = self.check_package(package, version)
            if vulns:
                results[package] = vulns
        return results

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entries": {
                pkg: [
                    {
                        "cve_id": cve.cve_id,
                        "severity": cve.severity,
                        "affected_versions": cve.affected_versions,
                        "fixed_in": cve.fixed_in,
                    }
                    for cve in cves
                ]
                for pkg, cves in self.entries.items()
            },
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CVEDatabase:
        """Create from dictionary."""
        db = cls()
        for pkg, cves in data.get("entries", {}).items():
            for cve_data in cves:
                cve = CVEEntry(
                    cve_id=cve_data["cve_id"],
                    severity=cve_data["severity"],
                    package=pkg,
                    affected_versions=cve_data["affected_versions"],
                    fixed_in=cve_data.get("fixed_in"),
                )
                db.add_cve(cve)
        # Set last_updated AFTER adding CVEs so add_cve/_update_checksum
        # doesn't overwrite the persisted timestamp from data.
        db.last_updated = data.get("last_updated", "")
        return db


class DependencyMonitor:
    """Monitor dependencies for vulnerabilities."""

    def __init__(self, cve_db: CVEDatabase):
        self.cve_db = cve_db
        self.alerts: list[dict[str, Any]] = []

    def scan(self, dependencies: dict[str, str]) -> dict[str, Any]:
        """Scan dependencies for vulnerabilities."""
        results = self.cve_db.check_all(dependencies)

        critical = []
        high = []
        medium = []
        low = []

        for pkg, vulns in results.items():
            for vuln in vulns:
                entry = {"package": pkg, "cve": vuln.cve_id, "fixed_in": vuln.fixed_in}
                if vuln.severity == "CRITICAL":
                    critical.append(entry)
                elif vuln.severity == "HIGH":
                    high.append(entry)
                elif vuln.severity == "MEDIUM":
                    medium.append(entry)
                else:
                    low.append(entry)

        return {
            "vulnerable_packages": len(results),
            "total_vulnerabilities": sum(len(v) for v in results.values()),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "safe": len(results) == 0,
        }

    def generate_report(self, scan_results: dict[str, Any]) -> str:
        """Generate vulnerability report."""
        lines = [
            "# Dependency Vulnerability Report",
            "",
            f"**Vulnerable Packages:** {scan_results['vulnerable_packages']}",
            f"**Total Vulnerabilities:** {scan_results['total_vulnerabilities']}",
            f"**Status:** {'✅ SAFE' if scan_results['safe'] else '⚠️ VULNERABILITIES FOUND'}",
            "",
        ]

        if scan_results["critical"]:
            lines.append("## Critical")
            for v in scan_results["critical"]:
                lines.append(f"- {v['package']}: {v['cve']} (fix: {v['fixed_in']})")

        if scan_results["high"]:
            lines.append("## High")
            for v in scan_results["high"]:
                lines.append(f"- {v['package']}: {v['cve']} (fix: {v['fixed_in']})")

        return "\n".join(lines)


# Sample CVE database for testing
def get_sample_cve_database() -> CVEDatabase:
    """Get sample CVE database."""
    db = CVEDatabase()

    # Add sample CVEs (these are examples, not real)
    db.add_cve(
        CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0", "2.25.1", "2.26.0"],
            fixed_in="2.27.0",
        )
    )

    db.add_cve(
        CVEEntry(
            cve_id="CVE-2024-0002",
            severity="CRITICAL",
            package="urllib3",
            affected_versions=["1.25.0", "1.25.1"],
            fixed_in="1.26.0",
        )
    )

    return db


if __name__ == "__main__":
    # Example usage
    db = get_sample_cve_database()
    monitor = DependencyMonitor(db)

    deps = {
        "requests": "2.26.0",
        "urllib3": "1.25.1",
        "numpy": "1.21.0",
    }

    results = monitor.scan(deps)
    logger.info(monitor.generate_report(results))
