"""Comprehensive tests for dependency management capability.

Tests cover:
- Lockfile enforcement
- CVE detection
- Upgrade cadence
- Vendor verification
- Dependency graph analysis
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import total_ordering
from typing import Any

import pytest

pytest.importorskip("hypothesis", reason="hypothesis required for property tests")


# --- Dependency Version Tests ---


@total_ordering
class DependencyVersion:
    """Dependency version representation."""

    VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-.]?(.+))?$")

    def __init__(self, major: int, minor: int, patch: int, prerelease: str | None = None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease

    @classmethod
    def parse(cls, version_str: str) -> "DependencyVersion":
        """Parse version string."""
        match = cls.VERSION_PATTERN.match(version_str)
        if not match:
            raise ValueError(f"Invalid version: {version_str}")
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4),
        )

    def __str__(self) -> str:
        v = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            v += f"-{self.prerelease}"
        return v

    def __lt__(self, other: "DependencyVersion") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DependencyVersion):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch))


class TestDependencyVersion:
    """Tests for dependency version."""

    def test_parse_simple(self):
        """Parse simple version."""
        v = DependencyVersion.parse("1.2.3")
        assert v.major == 1, "major is not valid"
        assert v.minor == 2, "minor is not valid"
        assert v.patch == 3, "patch is not valid"

    def test_parse_prerelease(self):
        """Parse version with prerelease."""
        v = DependencyVersion.parse("1.0.0-alpha")
        assert v.prerelease == "alpha", "prerelease is not valid"

    def test_version_comparison(self):
        """Compare versions."""
        v1 = DependencyVersion.parse("1.0.0")
        v2 = DependencyVersion.parse("1.1.0")
        assert v1 < v2, "v1 is not valid"


# --- Lockfile Tests ---


class LockfileEntry:
    """Lockfile entry for a dependency."""

    def __init__(self, name: str, version: str, checksum: str):
        self.name = name
        self.version = version
        self.checksum = checksum
        self.dependencies: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "checksum": self.checksum,
            "dependencies": self.dependencies,
        }


class Lockfile:
    """Dependency lockfile."""

    def __init__(self):
        self.entries: dict[str, LockfileEntry] = {}
        self.hash: str = ""

    def add_entry(self, entry: LockfileEntry) -> None:
        """Add entry to lockfile."""
        self.entries[entry.name] = entry
        self._update_hash()

    def _update_hash(self) -> None:
        """Update lockfile hash."""
        content = json.dumps({n: e.to_dict() for n, e in self.entries.items()}, sort_keys=True)
        self.hash = hashlib.sha256(content.encode()).hexdigest()

    def get_entry(self, name: str) -> LockfileEntry | None:
        """Get entry by name."""
        return self.entries.get(name)

    def verify(self, expected_hash: str) -> bool:
        """Verify lockfile integrity."""
        return self.hash == expected_hash


class TestLockfile:
    """Tests for lockfile management."""

    def test_add_entry(self):
        """Add entry to lockfile."""
        lockfile = Lockfile()
        entry = LockfileEntry("requests", "2.28.0", "sha256:abc123")
        lockfile.add_entry(entry)
        assert lockfile.get_entry("requests") is not None, "Value must be initialized"

    def test_lockfile_hash(self):
        """Lockfile has hash."""
        lockfile = Lockfile()
        lockfile.add_entry(LockfileEntry("pkg", "1.0.0", "sha256:123"))
        assert len(lockfile.hash) == 64, "Collection must not be empty"

    def test_verify_integrity(self):
        """Verify lockfile integrity."""
        lockfile = Lockfile()
        lockfile.add_entry(LockfileEntry("pkg", "1.0.0", "sha256:123"))
        valid_hash = lockfile.hash
        assert lockfile.verify(valid_hash), "Condition must be true"
        assert not lockfile.verify("wrong_hash"), "Condition must be true"


# --- CVE Detection Tests ---


class CVE:
    """CVE vulnerability representation."""

    def __init__(self, cve_id: str, severity: str, affected_versions: list[str]):
        self.cve_id = cve_id
        self.severity = severity
        self.affected_versions = affected_versions
        self.description: str = ""
        self.fixed_in: str | None = None

    def affects_version(self, version: str) -> bool:
        """Check if CVE affects version."""
        return version in self.affected_versions


class CVEDatabase:
    """CVE vulnerability database."""

    def __init__(self):
        self.cves: dict[str, list[CVE]] = {}  # package_name -> CVEs

    def add_cve(self, package: str, cve: CVE) -> None:
        """Add CVE to database."""
        if package not in self.cves:
            self.cves[package] = []
        self.cves[package].append(cve)

    def check_package(self, name: str, version: str) -> list[CVE]:
        """Check package for vulnerabilities."""
        vulnerabilities = []
        for cve in self.cves.get(name, []):
            if cve.affects_version(version):
                vulnerabilities.append(cve)
        return vulnerabilities


class TestCVEDetection:
    """Tests for CVE detection."""

    def test_add_cve(self):
        """Add CVE to database."""
        db = CVEDatabase()
        cve = CVE("CVE-2023-0001", "HIGH", ["1.0.0", "1.0.1"])
        db.add_cve("vulnerable-pkg", cve)
        assert len(db.cves["vulnerable-pkg"]) == 1, "Collection must not be empty"

    def test_detect_vulnerability(self):
        """Detect vulnerability in package."""
        db = CVEDatabase()
        cve = CVE("CVE-2023-0001", "HIGH", ["1.0.0", "1.0.1"])
        db.add_cve("pkg", cve)
        vulns = db.check_package("pkg", "1.0.0")
        assert len(vulns) == 1, "Vulns must not be empty"

    def test_no_vulnerability(self):
        """No vulnerability in safe version."""
        db = CVEDatabase()
        cve = CVE("CVE-2023-0001", "HIGH", ["1.0.0"])
        db.add_cve("pkg", cve)
        vulns = db.check_package("pkg", "2.0.0")
        assert len(vulns) == 0, "Vulns must not be empty"


# --- Upgrade Cadence Tests ---


class UpgradePolicy:
    """Dependency upgrade policy."""

    def __init__(self):
        self.max_major_versions_behind: int = 1
        self.max_minor_versions_behind: int = 3
        self.security_update_days: int = 7

    def should_upgrade(
        self, current: DependencyVersion, latest: DependencyVersion
    ) -> dict[str, Any]:
        """Check if upgrade is recommended."""
        major_diff = latest.major - current.major
        minor_diff = latest.minor - current.minor if major_diff == 0 else 0

        return {
            "should_upgrade": major_diff > self.max_major_versions_behind
            or minor_diff > self.max_minor_versions_behind,
            "major_versions_behind": major_diff,
            "minor_versions_behind": minor_diff,
            "urgency": "high" if major_diff > 1 else "normal",
        }


class TestUpgradePolicy:
    """Tests for upgrade policy."""

    def test_no_upgrade_needed(self):
        """No upgrade when up to date."""
        policy = UpgradePolicy()
        current = DependencyVersion(1, 0, 0)
        latest = DependencyVersion(1, 1, 0)
        result = policy.should_upgrade(current, latest)
        assert not result["should_upgrade"], "Result must not be empty"

    def test_upgrade_needed(self):
        """Upgrade needed when behind."""
        policy = UpgradePolicy()
        current = DependencyVersion(1, 0, 0)
        latest = DependencyVersion(3, 0, 0)
        result = policy.should_upgrade(current, latest)
        assert result["should_upgrade"], "Result must not be empty"
        assert result["urgency"] == "high", "Result must not be empty"


# --- Dependency Graph Tests ---


class DependencyGraph:
    """Dependency graph for analysis."""

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[str, list[str]] = {}

    def add_package(self, name: str, version: str) -> None:
        """Add package to graph."""
        self.nodes[name] = {"version": version}
        if name not in self.edges:
            self.edges[name] = []

    def add_dependency(self, from_pkg: str, to_pkg: str) -> None:
        """Add dependency edge."""
        if from_pkg not in self.edges:
            self.edges[from_pkg] = []
        self.edges[from_pkg].append(to_pkg)

    def get_dependencies(self, name: str, recursive: bool = False) -> list[str]:
        """Get dependencies for package."""
        direct = self.edges.get(name, [])
        if not recursive:
            return direct
        all_deps = set(direct)
        for dep in direct:
            all_deps.update(self.get_dependencies(dep, recursive=True))
        return list(all_deps)

    def find_cycles(self) -> list[list[str]]:
        """Find dependency cycles."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: list[str]) -> None:
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return
            if node in visited:
                return
            visited.add(node)
            rec_stack.add(node)
            for dep in self.edges.get(node, []):
                dfs(dep, path + [node])
            rec_stack.remove(node)

        for node in self.nodes:
            dfs(node, [])
        return cycles


class TestDependencyGraph:
    """Tests for dependency graph."""

    def test_add_package(self):
        """Add package to graph."""
        graph = DependencyGraph()
        graph.add_package("requests", "2.28.0")
        assert "requests" in graph.nodes, "Condition must be true"

    def test_get_dependencies(self):
        """Get direct dependencies."""
        graph = DependencyGraph()
        graph.add_package("myapp", "1.0.0")
        graph.add_package("requests", "2.28.0")
        graph.add_package("urllib3", "1.26.0")
        graph.add_dependency("myapp", "requests")
        graph.add_dependency("requests", "urllib3")
        deps = graph.get_dependencies("myapp")
        assert "requests" in deps, "Condition must be true"

    def test_recursive_dependencies(self):
        """Get recursive dependencies."""
        graph = DependencyGraph()
        graph.add_package("a", "1.0.0")
        graph.add_package("b", "1.0.0")
        graph.add_package("c", "1.0.0")
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        deps = graph.get_dependencies("a", recursive=True)
        assert "b" in deps, "Condition must be true"
        assert "c" in deps, "Condition must be true"


# --- Vendor Verification Tests ---


class VendorEntry:
    """Vendored dependency entry."""

    def __init__(self, name: str, version: str, source_url: str):
        self.name = name
        self.version = version
        self.source_url = source_url
        self.checksum: str = ""
        self.license: str = ""

    def compute_checksum(self, content: bytes) -> str:
        """Compute checksum of vendored content."""
        self.checksum = hashlib.sha256(content).hexdigest()
        return self.checksum


class VendorRegistry:
    """Registry of vendored dependencies."""

    def __init__(self):
        self.entries: dict[str, VendorEntry] = {}

    def add_entry(self, entry: VendorEntry) -> None:
        """Add vendored entry."""
        self.entries[entry.name] = entry

    def verify_all(self, checksums: dict[str, str]) -> dict[str, bool]:
        """Verify all entries against expected checksums."""
        results = {}
        for name, entry in self.entries.items():
            expected = checksums.get(name)
            results[name] = entry.checksum == expected if expected else False
        return results


class TestVendorVerification:
    """Tests for vendor verification."""

    def test_compute_checksum(self):
        """Compute vendor checksum."""
        entry = VendorEntry("lib", "1.0.0", "https://example.com/lib.tar.gz")
        checksum = entry.compute_checksum(b"content")
        assert len(checksum) == 64, "Checksum must not be empty"

    def test_verify_all(self):
        """Verify all vendored entries."""
        registry = VendorRegistry()
        entry = VendorEntry("lib", "1.0.0", "url")
        entry.checksum = "abc123"
        registry.add_entry(entry)
        results = registry.verify_all({"lib": "abc123"})
        assert results["lib"], "Result must not be empty"


# --- Requirements File Tests ---


class RequirementsFile:
    """Parse and manage requirements files."""

    def __init__(self):
        self.dependencies: list[dict[str, Any]] = []

    def parse_line(self, line: str) -> dict[str, Any] | None:
        """Parse requirements line."""
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        # Match package==version or package>=version
        match = re.match(r"([a-zA-Z0-9_-]+)([<>=!]+)?(.+)?", line)
        if match:
            return {
                "name": match.group(1),
                "operator": match.group(2) or "",
                "version": match.group(3) or "",
            }
        return None

    def parse(self, content: str) -> list[dict[str, Any]]:
        """Parse requirements file content."""
        self.dependencies = []
        for line in content.split("\n"):
            parsed = self.parse_line(line)
            if parsed:
                self.dependencies.append(parsed)
        return self.dependencies


class TestRequirementsFile:
    """Tests for requirements file parsing."""

    def test_parse_simple(self):
        """Parse simple requirement."""
        rf = RequirementsFile()
        result = rf.parse_line("requests==2.28.0")
        assert result["name"] == "requests", "Result must not be empty"
        assert result["version"] == "2.28.0", "Result must not be empty"

    def test_parse_file(self):
        """Parse requirements file."""
        rf = RequirementsFile()
        content = """
        requests==2.28.0
        # Comment
        numpy>=1.20.0
        """
        deps = rf.parse(content)
        assert len(deps) == 2, "Deps must not be empty"

    def test_skip_comments(self):
        """Skip comment lines."""
        rf = RequirementsFile()
        result = rf.parse_line("# This is a comment")
        assert result is None, "Result must not be empty"
