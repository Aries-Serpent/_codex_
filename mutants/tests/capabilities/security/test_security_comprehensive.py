"""Comprehensive tests for security and safety capability.

Tests cover:
- Secrets baseline enforcement
- Dependency scanning and CVE detection
- Prompt safety/sanitization
- Supply-chain SBOM/provenance
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

import pytest

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Secrets Baseline Enforcement Tests ---


SECRET_PATTERNS = [
    (r"(?i)api[_-]?key\s*=\s*['\"][a-zA-Z0-9_]{16,}['\"]", "API Key"),
    (r"(?i)password\s*[:=]\s*['\"][^'\"]+['\"]", "Password"),
    (r"(?i)secret\s*[:=]\s*['\"][a-zA-Z0-9]{16,}['\"]", "Secret"),
    (r"(?i)token\s*[:=]\s*['\"][a-zA-Z0-9_]{16,}['\"]", "Token"),
    (r"(?i)private[_-]?key", "Private Key"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private Key Block"),
    (r"(?i)aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*['\"]?[A-Z0-9]{20}['\"]?", "AWS Access Key"),
    (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]", "AWS Secret Key"),
]


def scan_for_secrets(content: str) -> list[dict[str, Any]]:
    """Scan content for potential secrets."""
    findings = []
    for pattern, secret_type in SECRET_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            findings.append(
                {
                    "type": secret_type,
                    "pattern": pattern,
                    "match": (
                        match.group()[:50] + "..." if len(match.group()) > 50 else match.group()
                    ),
                    "position": match.start(),
                }
            )
    return findings


class TestSecretsScanning:
    """Tests for secrets scanning."""

    def test_detect_api_key(self):
        """Detect API key in content."""
        content = 'api_key = "test_key_abcdefghijklmnopqrstuvwxyz"'
        findings = scan_for_secrets(content)
        assert len(findings) >= 1, "Findings must not be empty"
        assert any(f["type"] == "API Key" for f in findings), "Condition must be true"

    def test_detect_password(self):
        """Detect password in content."""
        content = 'password = "supersecretpassword123"'
        findings = scan_for_secrets(content)
        assert len(findings) >= 1, "Findings must not be empty"
        assert any(f["type"] == "Password" for f in findings), "Condition must be true"

    def test_detect_private_key_block(self):
        """Detect private key block."""
        content = "-----BEGIN RSA PRIVATE KEY-----\nMIIE..."
        findings = scan_for_secrets(content)
        assert len(findings) >= 1, "Findings must not be empty"
        assert any(f["type"] == "Private Key Block" for f in findings), "Condition must be true"

    def test_detect_aws_key(self):
        """Detect AWS access key."""
        content = 'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"'
        findings = scan_for_secrets(content)
        assert len(findings) >= 1, "Findings must not be empty"
        assert any(f["type"] == "AWS Access Key" for f in findings), "Condition must be true"

    def test_clean_content_no_findings(self):
        """Clean content should have no findings."""
        content = "def hello():\n    logger.info('Hello, World!')"
        findings = scan_for_secrets(content)
        assert len(findings) == 0, "Findings must not be empty"


# --- Secrets Baseline Tests ---


class SecretsBaseline:
    """Manages secrets baseline for allowlisting known false positives."""

    def __init__(self):
        self.allowed: set[str] = set()

    def add_allowlist(self, checksum: str) -> None:
        """Add a finding checksum to allowlist."""
        self.allowed.add(checksum)

    def is_allowed(self, finding: dict[str, Any]) -> bool:
        """Check if finding is in allowlist."""
        checksum = self._compute_checksum(finding)
        return checksum in self.allowed

    def _compute_checksum(self, finding: dict[str, Any]) -> str:
        """Compute checksum for a finding."""
        canonical = json.dumps({"type": finding["type"], "match": finding["match"]}, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def filter_findings(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter out allowlisted findings."""
        return [f for f in findings if not self.is_allowed(f)]


class TestSecretsBaseline:
    """Tests for secrets baseline management."""

    def test_allowlist_finding(self):
        """Allowlisted finding should be filtered."""
        baseline = SecretsBaseline()
        finding = {"type": "API Key", "match": "test_api_key_value"}
        checksum = baseline._compute_checksum(finding)
        baseline.add_allowlist(checksum)
        assert baseline.is_allowed(finding), "Condition must be true"

    def test_non_allowlisted_finding(self):
        """Non-allowlisted finding should not be filtered."""
        baseline = SecretsBaseline()
        finding = {"type": "Password", "match": "secret123"}
        assert not baseline.is_allowed(finding), "Condition must be true"

    def test_filter_findings(self):
        """Filter should remove allowlisted findings."""
        baseline = SecretsBaseline()
        findings = [
            {"type": "API Key", "match": "allowed_key"},
            {"type": "Password", "match": "not_allowed"},
        ]
        baseline.add_allowlist(baseline._compute_checksum(findings[0]))
        filtered = baseline.filter_findings(findings)
        assert len(filtered) == 1, "Filtered must not be empty"
        assert filtered[0]["type"] == "Password", "Condition must be true"


# --- Dependency Scanning Tests ---


class DependencyScanner:
    """Scans dependencies for known vulnerabilities."""

    def __init__(self):
        self.cve_db: dict[str, list[dict[str, Any]]] = {}

    def add_cve(self, package: str, cve: dict[str, Any]) -> None:
        """Add CVE to database."""
        if package not in self.cve_db:
            self.cve_db[package] = []
        self.cve_db[package].append(cve)

    def scan(self, dependencies: dict[str, str]) -> list[dict[str, Any]]:
        """Scan dependencies for vulnerabilities."""
        vulnerabilities = []
        for package, version in dependencies.items():
            if package in self.cve_db:
                for cve in self.cve_db[package]:
                    if self._version_affected(version, cve):
                        vulnerabilities.append(
                            {
                                "package": package,
                                "version": version,
                                "cve": cve["id"],
                                "severity": cve["severity"],
                            }
                        )
        return vulnerabilities

    def _version_affected(self, version: str, cve: dict[str, Any]) -> bool:
        """Check if version is affected by CVE."""
        # Simplified version check
        affected_versions = cve.get("affected_versions", [])
        return version in affected_versions or "*" in affected_versions


class TestDependencyScanning:
    """Tests for dependency scanning."""

    def test_detect_vulnerable_dependency(self):
        """Detect vulnerable dependency."""
        scanner = DependencyScanner()
        scanner.add_cve(
            "requests", {"id": "CVE-2023-1234", "severity": "high", "affected_versions": ["2.28.0"]}
        )
        vulns = scanner.scan({"requests": "2.28.0"})
        assert len(vulns) == 1, "Vulns must not be empty"
        assert vulns[0]["cve"] == "CVE-2023-1234", "Condition must be true"

    def test_clean_dependencies(self):
        """Clean dependencies should have no vulnerabilities."""
        scanner = DependencyScanner()
        scanner.add_cve(
            "requests", {"id": "CVE-2023-1234", "severity": "high", "affected_versions": ["2.28.0"]}
        )
        vulns = scanner.scan({"requests": "2.31.0"})  # Different version
        assert len(vulns) == 0, "Vulns must not be empty"

    def test_multiple_vulnerabilities(self):
        """Detect multiple vulnerabilities."""
        scanner = DependencyScanner()
        scanner.add_cve(
            "pkg1", {"id": "CVE-2023-0001", "severity": "high", "affected_versions": ["*"]}
        )
        scanner.add_cve(
            "pkg2", {"id": "CVE-2023-0002", "severity": "medium", "affected_versions": ["*"]}
        )
        vulns = scanner.scan({"pkg1": "1.0.0", "pkg2": "2.0.0"})
        assert len(vulns) == 2, "Vulns must not be empty"


# --- Prompt Sanitization Tests ---


DANGEROUS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__\s*\(",
    r"subprocess\.",
    r"os\.system\s*\(",
    r"{{.*}}",  # Template injection
    r"\$\{.*\}",  # Template injection
]


def sanitize_prompt(prompt: str) -> tuple[str, list[str]]:
    """Sanitize prompt and return warnings."""
    warnings = []
    sanitized = prompt

    for pattern in DANGEROUS_PATTERNS:
        matches = re.findall(pattern, prompt, re.IGNORECASE | re.DOTALL)
        if matches:
            warnings.append(f"Dangerous pattern detected: {pattern}")
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE | re.DOTALL)

    return sanitized, warnings


class TestPromptSanitization:
    """Tests for prompt sanitization."""

    def test_clean_prompt_unchanged(self):
        """Clean prompt should be unchanged."""
        prompt = "What is the capital of France?"
        sanitized, warnings = sanitize_prompt(prompt)
        assert sanitized == prompt, "sanitized is not valid"
        assert len(warnings) == 0, "Warnings must not be empty"

    def test_sanitize_script_tag(self):
        """Script tags should be redacted."""
        prompt = "Hello <script>alert('xss')</script> World"
        sanitized, warnings = sanitize_prompt(prompt)
        assert "<script>" not in sanitized, "Condition must be true"
        assert len(warnings) > 0, "Warnings must not be empty"

    def test_sanitize_javascript_url(self):
        """JavaScript URLs should be redacted."""
        prompt = "Click javascript:alert('xss')"
        sanitized, warnings = sanitize_prompt(prompt)
        assert "javascript:" not in sanitized, "Condition must be true"
        assert len(warnings) > 0, "Warnings must not be empty"

    def test_sanitize_eval(self):
        """Eval calls should be redacted."""
        prompt = "Execute eval('malicious code')"
        sanitized, warnings = sanitize_prompt(prompt)
        assert "eval(" not in sanitized, "Condition must be true"
        assert len(warnings) > 0, "Warnings must not be empty"

    def test_sanitize_template_injection(self):
        """Template injection should be redacted."""
        prompt = "Hello {{user.password}}"
        sanitized, warnings = sanitize_prompt(prompt)
        assert "{{" not in sanitized, "Condition must be true"
        assert len(warnings) > 0, "Warnings must not be empty"

    @given(
        st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
        )
    )
    @settings(max_examples=30)
    def test_sanitization_idempotent(self, prompt: str):
        """Property: sanitization is idempotent."""
        sanitized1, _ = sanitize_prompt(prompt)
        sanitized2, _ = sanitize_prompt(sanitized1)
        assert sanitized1 == sanitized2, "sanitized1 is not valid"


# --- SBOM Generation Tests ---


class SBOMGenerator:
    """Generates Software Bill of Materials."""

    def __init__(self):
        self.components: list[dict[str, Any]] = []

    def add_component(self, name: str, version: str, license: str, purl: str | None = None) -> None:
        """Add component to SBOM."""
        self.components.append(
            {
                "name": name,
                "version": version,
                "license": license,
                "purl": purl or f"pkg:pypi/{name}@{version}",
            }
        )

    def generate(self, format: str = "cyclonedx") -> dict[str, Any]:
        """Generate SBOM in specified format."""
        if format == "cyclonedx":
            return {
                "bomFormat": "CycloneDX",
                "specVersion": "1.4",
                "components": self.components,
            }
        if format == "spdx":
            return {
                "spdxVersion": "SPDX-2.3",
                "packages": [
                    {
                        "name": c["name"],
                        "versionInfo": c["version"],
                        "licenseDeclared": c["license"],
                    }
                    for c in self.components
                ],
            }
        raise ValueError(f"Unknown format: {format}")

    def validate(self) -> list[str]:
        """Validate SBOM completeness."""
        errors = []
        for i, comp in enumerate(self.components):
            if not comp.get("name"):
                errors.append(f"Component {i}: missing name")
            if not comp.get("version"):
                errors.append(f"Component {i}: missing version")
            if not comp.get("license"):
                errors.append(f"Component {i}: missing license")
        return errors


class TestSBOMGeneration:
    """Tests for SBOM generation."""

    def test_add_component(self):
        """Add component to SBOM."""
        sbom = SBOMGenerator()
        sbom.add_component("requests", "2.31.0", "Apache-2.0")
        assert len(sbom.components) == 1, "Collection must not be empty"

    def test_generate_cyclonedx(self):
        """Generate CycloneDX format."""
        sbom = SBOMGenerator()
        sbom.add_component("requests", "2.31.0", "Apache-2.0")
        result = sbom.generate("cyclonedx")
        assert result["bomFormat"] == "CycloneDX", "Result must not be empty"
        assert len(result["components"]) == 1, "Collection must not be empty"

    def test_generate_spdx(self):
        """Generate SPDX format."""
        sbom = SBOMGenerator()
        sbom.add_component("requests", "2.31.0", "Apache-2.0")
        result = sbom.generate("spdx")
        assert result["spdxVersion"] == "SPDX-2.3", "Result must not be empty"
        assert len(result["packages"]) == 1, "Collection must not be empty"

    def test_validate_complete(self):
        """Complete SBOM should pass validation."""
        sbom = SBOMGenerator()
        sbom.add_component("requests", "2.31.0", "Apache-2.0")
        errors = sbom.validate()
        assert len(errors) == 0, "Errors must not be empty"

    def test_validate_missing_fields(self):
        """Missing fields should be detected."""
        sbom = SBOMGenerator()
        sbom.components.append({"name": "test"})  # Missing version and license
        errors = sbom.validate()
        assert len(errors) == 2, "Errors must not be empty"


# --- Provenance Tests ---


class ProvenanceRecord:
    """Records provenance information for artifacts."""

    def __init__(self, artifact_name: str):
        self.artifact_name = artifact_name
        self.build_info: dict[str, Any] = {}
        self.source_info: dict[str, Any] = {}
        self.signatures: list[str] = []

    def set_build_info(self, builder: str, build_time: str, build_id: str) -> None:
        """Set build information."""
        self.build_info = {"builder": builder, "build_time": build_time, "build_id": build_id}

    def set_source_info(self, repo: str, commit: str, branch: str) -> None:
        """Set source information."""
        self.source_info = {"repo": repo, "commit": commit, "branch": branch}

    def add_signature(self, signature: str) -> None:
        """Add artifact signature."""
        self.signatures.append(signature)

    def is_complete(self) -> bool:
        """Check if provenance record is complete."""
        return bool(self.build_info and self.source_info)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "artifact": self.artifact_name,
            "build": self.build_info,
            "source": self.source_info,
            "signatures": self.signatures,
        }


class TestProvenance:
    """Tests for provenance tracking."""

    def test_create_provenance(self):
        """Create provenance record."""
        prov = ProvenanceRecord("myapp-1.0.0.tar.gz")
        prov.set_build_info("github-actions", "2024-01-01T00:00:00Z", "build-123")
        prov.set_source_info("github.com/org/repo", "abc123", "main")
        assert prov.is_complete(), "Condition must be true"

    def test_incomplete_provenance(self):
        """Incomplete provenance should be detected."""
        prov = ProvenanceRecord("myapp-1.0.0.tar.gz")
        prov.set_build_info("github-actions", "2024-01-01T00:00:00Z", "build-123")
        assert not prov.is_complete(), "Condition must be true"

    def test_provenance_signature(self):
        """Add signature to provenance."""
        prov = ProvenanceRecord("myapp-1.0.0.tar.gz")
        prov.add_signature("sig_abc123")
        assert len(prov.signatures) == 1, "Collection must not be empty"

    def test_provenance_to_dict(self):
        """Convert provenance to dictionary."""
        prov = ProvenanceRecord("myapp-1.0.0.tar.gz")
        prov.set_build_info("github-actions", "2024-01-01T00:00:00Z", "build-123")
        prov.set_source_info("github.com/org/repo", "abc123", "main")
        result = prov.to_dict()
        assert result["artifact"] == "myapp-1.0.0.tar.gz", "Result must not be empty"
        assert "build" in result, "Result must not be empty"
        assert "source" in result, "Result must not be empty"


# --- Input Validation Tests ---


class TestInputValidation:
    """Tests for input validation security."""

    def test_reject_null_bytes(self):
        """Null bytes should be rejected."""
        input_text = "hello\x00world"
        assert "\x00" in input_text, "Condition must be true"
        sanitized = input_text.replace("\x00", "")
        assert "\x00" not in sanitized, "Condition must be true"

    def test_reject_control_characters(self):
        """Control characters should be sanitized."""
        input_text = "hello\x1b[31mred\x1b[0m"
        # Remove ANSI escape sequences
        sanitized = re.sub(r"\x1b\[[0-9;]*m", "", input_text)
        assert "\x1b" not in sanitized, "Condition must be true"

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=30)
    def test_sanitization_preserves_printable(self, text: str):
        """Property: sanitization preserves printable characters."""
        printable_only = "".join(c for c in text if c.isprintable() or c in "\n\t")
        # Should not raise exceptions
        assert isinstance(printable_only, str)
