"""
S2: Root-Cause Family Grouping

Groups similar findings by root-cause family using:
- CWE similarity
- Description embedding similarity
- Location proximity

Success metric: Family recall >95%, precision >90%
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .ingest import FindingSeverity, NormalizedFinding


@dataclass
class FindingFamily:
    """A group of similar findings with common root cause."""
    family_id: str
    root_cwe: Optional[str] = None
    findings: List[NormalizedFinding] = field(default_factory=list)
    description: str = ""
    severity_level: FindingSeverity = FindingSeverity.MEDIUM

    def add_finding(self, finding: NormalizedFinding) -> None:
        """Add a finding to this family."""
        self.findings.append(finding)
        # Update severity to max using a defined order rather than string ordering.
        severity_rank = {
            FindingSeverity.INFO: 0,
            FindingSeverity.LOW: 1,
            FindingSeverity.MEDIUM: 2,
            FindingSeverity.HIGH: 3,
            FindingSeverity.CRITICAL: 4,
        }
        if severity_rank.get(finding.severity, 0) > severity_rank.get(self.severity_level, 0):
            self.severity_level = finding.severity

    def aggregate_risk(self) -> float:
        """Compute aggregate risk for this family."""
        if not self.findings:
            return 0.0
        severity_scores = {
            FindingSeverity.CRITICAL: 1.0,
            FindingSeverity.HIGH: 0.75,
            FindingSeverity.MEDIUM: 0.5,
            FindingSeverity.LOW: 0.25,
            FindingSeverity.INFO: 0.1,
        }
        avg_severity = sum(
            severity_scores.get(f.severity, 0.5) for f in self.findings
        ) / len(self.findings)
        return avg_severity * len(self.findings)  # Scale by count


class FindingClusterer:
    """Groups findings into families based on root-cause similarity."""

    SIMILARITY_THRESHOLD = 0.85

    def __init__(self, similarity_threshold: float = 0.85):
        """Initialize clusterer."""
        self.similarity_threshold = similarity_threshold
        self.families: Dict[str, FindingFamily] = {}

    def cluster(self, findings: List[NormalizedFinding]) -> Dict[str, FindingFamily]:
        """Cluster findings into families."""
        if not findings:
            return {}

        # Start with first finding in its own family
        for i, finding in enumerate(findings):
            family_id = f"family_{i:05d}"
            family = FindingFamily(
                family_id=family_id,
                root_cwe=finding.cwe,
                description=finding.title,
                severity_level=finding.severity,
            )
            family.add_finding(finding)
            self.families[family_id] = family

        # Attempt to merge similar findings
        self._merge_similar_families()

        return self.families

    def _merge_similar_families(self) -> None:
        """Merge families with high similarity."""
        families_list = list(self.families.items())

        for i, (fid1, fam1) in enumerate(families_list):
            if fid1 not in self.families:
                continue

            for j in range(i + 1, len(families_list)):
                fid2, fam2 = families_list[j]
                if fid2 not in self.families:
                    continue

                similarity = self._compute_family_similarity(fam1, fam2)
                if similarity >= self.similarity_threshold:
                    # Merge fam2 into fam1
                    for finding in fam2.findings:
                        fam1.add_finding(finding)
                    del self.families[fid2]

    @staticmethod
    def _compute_family_similarity(fam1: FindingFamily, fam2: FindingFamily) -> float:
        """Compute similarity between two families (0 to 1)."""
        similarity = 0.0

        # CWE similarity (0.4 weight)
        if fam1.root_cwe and fam2.root_cwe and fam1.root_cwe == fam2.root_cwe:
            similarity += 0.4

        # Description similarity (0.3 weight)
        desc_sim = FindingClusterer._text_similarity(
            fam1.description,
            fam2.description,
        )
        similarity += desc_sim * 0.3

        # Severity similarity (0.3 weight)
        if fam1.severity_level == fam2.severity_level:
            similarity += 0.3

        return similarity

    @staticmethod
    def _text_similarity(text1: str, text2: str) -> float:
        """Simple text similarity using common words."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        return intersection / union

    def get_families(self) -> Dict[str, FindingFamily]:
        """Get all families."""
        return self.families

    def get_family_by_id(self, family_id: str) -> Optional[FindingFamily]:
        """Get a specific family by ID."""
        return self.families.get(family_id)

    def get_largest_families(self, count: int = 10) -> List[FindingFamily]:
        """Get the N largest families by finding count."""
        families = sorted(
            self.families.values(),
            key=lambda f: len(f.findings),
            reverse=True,
        )
        return families[:count]

    def compute_metrics(self) -> Dict[str, Any]:
        """Compute clustering metrics."""
        total_families = len(self.families)
        total_findings = sum(len(f.findings) for f in self.families.values())
        avg_findings_per_family = (
            total_findings / total_families if total_families > 0 else 0
        )

        return {
            "total_families": total_families,
            "total_findings": total_findings,
            "avg_findings_per_family": avg_findings_per_family,
            "largest_family_size": (
                max(len(f.findings) for f in self.families.values())
                if self.families
                else 0
            ),
        }


def build_finding_families(
    findings: List[NormalizedFinding],
    similarity_threshold: float = 0.85,
) -> Dict[str, FindingFamily]:
    """Build finding families from a list of normalized findings."""
    clusterer = FindingClusterer(similarity_threshold=similarity_threshold)
    return clusterer.cluster(findings)
