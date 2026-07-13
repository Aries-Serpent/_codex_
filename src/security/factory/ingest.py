"""
S1: Scanner Ingestion & Normalization

Aggregates findings from multiple security sources and normalizes to canonical format.

Sources:
- CodeQL
- SAST (Ruff, Pylint)
- Dependency scanners (pip-audit, safety)
- Custom scanners

Output: Normalized findings list + ingest metrics
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import hashlib
from datetime import datetime


class FindingSeverity(str, Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class NormalizedFinding:
    """Canonical finding format."""
    finding_id: str  # Unique identifier
    title: str
    description: str
    severity: FindingSeverity
    cwe: Optional[str] = None  # CWE ID if applicable
    cve: Optional[str] = None  # CVE ID if applicable
    path: Optional[str] = None  # File path
    line: Optional[int] = None  # Line number
    column: Optional[int] = None  # Column number
    source_tool: str = "unknown"  # CodeQL, ruff, pip-audit, etc.
    raw_data: Dict[str, Any] = field(default_factory=dict)  # Original finding data
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def compute_hash(self) -> str:
        """Compute finding hash for deduplication."""
        key = f"{self.path}:{self.line}:{self.title}:{self.severity}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]


@dataclass
class IngestMetrics:
    """Metrics for ingest operation."""
    total_findings: int
    unique_findings: int
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_tool: Dict[str, int] = field(default_factory=dict)
    deduplication_ratio: float = 0.0

    def __post_init__(self):
        """Calculate deduplication ratio."""
        if self.total_findings > 0:
            self.deduplication_ratio = (
                self.total_findings - self.unique_findings
            ) / self.total_findings
        else:
            self.deduplication_ratio = 0.0


class SecurityIngestor:
    """Ingests and normalizes security findings from multiple sources."""

    def __init__(self):
        """Initialize ingestor."""
        self.normalized_findings: List[NormalizedFinding] = []
        self.metrics = IngestMetrics(total_findings=0, unique_findings=0)

    def ingest_codeql(self, findings: List[Dict[str, Any]]) -> None:
        """Ingest CodeQL findings."""
        for finding in findings:
            normalized = self._normalize_codeql(finding)
            self.normalized_findings.append(normalized)

    def ingest_sast(self, findings: List[Dict[str, Any]]) -> None:
        """Ingest SAST findings (Ruff, Pylint, etc.)."""
        for finding in findings:
            normalized = self._normalize_sast(finding)
            self.normalized_findings.append(normalized)

    def ingest_dependencies(self, findings: List[Dict[str, Any]]) -> None:
        """Ingest dependency vulnerability findings."""
        for finding in findings:
            normalized = self._normalize_dependency(finding)
            self.normalized_findings.append(normalized)

    def ingest_custom(self, findings: List[Dict[str, Any]]) -> None:
        """Ingest findings from custom scanners."""
        for finding in findings:
            normalized = self._normalize_custom(finding)
            self.normalized_findings.append(normalized)

    @staticmethod
    def _normalize_codeql(raw: Dict[str, Any]) -> NormalizedFinding:
        """Normalize CodeQL finding to canonical format."""
        severity_map = {
            "error": FindingSeverity.HIGH,
            "warning": FindingSeverity.MEDIUM,
            "note": FindingSeverity.LOW,
        }
        return NormalizedFinding(
            finding_id=raw.get("id", ""),
            title=raw.get("message", ""),
            description=raw.get("description", ""),
            severity=severity_map.get(raw.get("level", "warning"), FindingSeverity.MEDIUM),
            cwe=raw.get("cwe"),
            path=raw.get("path"),
            line=raw.get("start_line"),
            column=raw.get("start_column"),
            source_tool="codeql",
            raw_data=raw,
        )

    @staticmethod
    def _normalize_sast(raw: Dict[str, Any]) -> NormalizedFinding:
        """Normalize SAST finding to canonical format."""
        severity_map = {
            "error": FindingSeverity.HIGH,
            "warning": FindingSeverity.MEDIUM,
            "note": FindingSeverity.LOW,
        }
        return NormalizedFinding(
            finding_id=raw.get("id", ""),
            title=raw.get("title", ""),
            description=raw.get("message", ""),
            severity=severity_map.get(raw.get("severity", "warning"), FindingSeverity.MEDIUM),
            path=raw.get("filename"),
            line=raw.get("line"),
            column=raw.get("column"),
            source_tool=raw.get("tool", "sast"),
            raw_data=raw,
        )

    @staticmethod
    def _normalize_dependency(raw: Dict[str, Any]) -> NormalizedFinding:
        """Normalize dependency vulnerability finding."""
        severity_map = {
            "critical": FindingSeverity.CRITICAL,
            "high": FindingSeverity.HIGH,
            "medium": FindingSeverity.MEDIUM,
            "low": FindingSeverity.LOW,
        }
        return NormalizedFinding(
            finding_id=raw.get("id", ""),
            title=raw.get("package", ""),
            description=raw.get("description", ""),
            severity=severity_map.get(raw.get("severity", "medium"), FindingSeverity.MEDIUM),
            cve=raw.get("cve"),
            source_tool=raw.get("tool", "pip-audit"),
            raw_data=raw,
        )

    @staticmethod
    def _normalize_custom(raw: Dict[str, Any]) -> NormalizedFinding:
        """Normalize custom scanner finding."""
        severity_map = {
            "critical": FindingSeverity.CRITICAL,
            "high": FindingSeverity.HIGH,
            "medium": FindingSeverity.MEDIUM,
            "low": FindingSeverity.LOW,
            "info": FindingSeverity.INFO,
        }
        return NormalizedFinding(
            finding_id=raw.get("id", ""),
            title=raw.get("title", ""),
            description=raw.get("description", ""),
            severity=severity_map.get(raw.get("severity", "medium"), FindingSeverity.MEDIUM),
            cwe=raw.get("cwe"),
            cve=raw.get("cve"),
            path=raw.get("path"),
            line=raw.get("line"),
            column=raw.get("column"),
            source_tool=raw.get("source_tool", "custom"),
            raw_data=raw,
        )

    def deduplicate(self) -> List[NormalizedFinding]:
        """Remove duplicate findings."""
        seen: Set[str] = set()
        unique = []

        for finding in self.normalized_findings:
            finding_hash = finding.compute_hash()
            if finding_hash not in seen:
                seen.add(finding_hash)
                unique.append(finding)

        return unique

    def compute_metrics(self) -> IngestMetrics:
        """Compute ingest metrics."""
        self.metrics.total_findings = len(self.normalized_findings)
        self.metrics.unique_findings = len(self.deduplicate())

        # Count by severity
        severity_counts: Dict[str, int] = {}
        for finding in self.normalized_findings:
            severity_counts[finding.severity.value] = (
                severity_counts.get(finding.severity.value, 0) + 1
            )
        self.metrics.by_severity = severity_counts

        # Count by tool
        tool_counts: Dict[str, int] = {}
        for finding in self.normalized_findings:
            tool_counts[finding.source_tool] = (
                tool_counts.get(finding.source_tool, 0) + 1
            )
        self.metrics.by_tool = tool_counts

        return self.metrics


def normalize_finding(raw: Dict[str, Any], source_tool: str = "custom") -> NormalizedFinding:
    """Normalize a single finding based on source tool."""
    if source_tool == "codeql":
        return SecurityIngestor._normalize_codeql(raw)
    elif source_tool in ("ruff", "pylint"):
        return SecurityIngestor._normalize_sast(raw)
    elif source_tool in ("pip-audit", "safety"):
        return SecurityIngestor._normalize_dependency(raw)
    else:
        return SecurityIngestor._normalize_custom(raw)


def deduplicate_findings(
    findings: List[NormalizedFinding],
) -> List[NormalizedFinding]:
    """Deduplicate a list of findings."""
    seen: Set[str] = set()
    unique = []

    for finding in findings:
        finding_hash = finding.compute_hash()
        if finding_hash not in seen:
            seen.add(finding_hash)
            unique.append(finding)

    return unique
