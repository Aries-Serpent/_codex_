"""
S3: Risk-Weighted Prioritization & Wave Planning

Scores findings based on CVSS, exploitability, and impact.
Plans waves for parallel remediation:
- Wave 1: 10% (Week 1) — highest risk
- Wave 2: 50% (Week 2) — high risk
- Wave 3: 100% (Week 3+) — remaining

Success metric: Top 50% of wave 1 findings = 80% of total risk
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from .clustering import FindingFamily
from .ingest import FindingSeverity


class Exploitability(str, Enum):
    """Exploitability levels."""
    NOT_KNOWN = "not_known"
    UNPROVEN = "unproven"
    POC = "poc"
    FUNCTIONAL = "functional"
    HIGH = "high"


@dataclass
class ScoredFamily:
    """A finding family with computed risk score."""
    family: FindingFamily
    risk_score: float = 0.0  # 0-10 scale
    exploitability: Exploitability = Exploitability.NOT_KNOWN
    impact_score: float = 0.5  # 0-1 scale
    wave: int = 0  # Wave assignment (1, 2, or 3)

    @property
    def family_id(self) -> str:
        """Return the family identifier for downstream pipeline contracts."""
        return self.family.family_id

    @property
    def root_cwe(self) -> str | None:
        """Expose the root cause CWE for downstream consumers."""
        return self.family.root_cwe

    def __lt__(self, other: "ScoredFamily") -> bool:
        """Compare by risk score (for sorting)."""
        return self.risk_score > other.risk_score  # Higher risk first


@dataclass
class WavePlan:
    """Plan for remediation waves."""
    wave_1: List[ScoredFamily] = field(default_factory=list)  # 10% of findings
    wave_2: List[ScoredFamily] = field(default_factory=list)  # 50% of findings
    wave_3: List[ScoredFamily] = field(default_factory=list)  # 100% of findings
    total_risk: float = 0.0
    wave_1_risk: float = 0.0
    wave_2_risk: float = 0.0

    def risk_concentration(self) -> float:
        """Compute risk concentration in wave 1 (should be >80%)."""
        if self.total_risk == 0:
            return 0.0
        return self.wave_1_risk / self.total_risk


class RiskScorer:
    """Scores findings based on multiple factors."""

    # Risk score weights
    SEVERITY_WEIGHT = 0.50
    EXPLOITABILITY_WEIGHT = 0.30
    IMPACT_WEIGHT = 0.20

    def __init__(self):
        """Initialize scorer."""
        self.scored_families: List[ScoredFamily] = []

    def score_families(
        self,
        families: Dict[str, FindingFamily],
    ) -> List[ScoredFamily]:
        """Score all families."""
        self.scored_families = []

        for family in families.values():
            scored = self._score_family(family)
            self.scored_families.append(scored)

        # Sort by risk score (descending)
        self.scored_families.sort()

        return self.scored_families

    def _score_family(self, family: FindingFamily) -> ScoredFamily:
        """Score a single family."""
        # Severity score (0-1)
        severity_score = self._severity_to_score(family.severity_level)

        # Exploitability (estimated from CWE if available)
        exploitability = self._estimate_exploitability(family.root_cwe)
        exploitability_score = self._exploitability_to_score(exploitability)

        # Impact score
        impact_score = self._compute_impact_score(family)

        # Composite risk score (0-10)
        risk_score = (
            severity_score * self.SEVERITY_WEIGHT * 10
            + exploitability_score * self.EXPLOITABILITY_WEIGHT * 10
            + impact_score * self.IMPACT_WEIGHT * 10
        )

        return ScoredFamily(
            family=family,
            risk_score=min(10.0, risk_score),
            exploitability=exploitability,
            impact_score=impact_score,
        )

    @staticmethod
    def _severity_to_score(severity: FindingSeverity) -> float:
        """Convert severity to 0-1 score."""
        severity_scores = {
            FindingSeverity.CRITICAL: 1.0,
            FindingSeverity.HIGH: 0.75,
            FindingSeverity.MEDIUM: 0.5,
            FindingSeverity.LOW: 0.25,
            FindingSeverity.INFO: 0.1,
        }
        return severity_scores.get(severity, 0.5)

    @staticmethod
    def _estimate_exploitability(cwe: str | None = None) -> Exploitability:
        """Estimate exploitability based on CWE."""
        if not cwe:
            return Exploitability.NOT_KNOWN

        # Common highly exploitable CWEs
        high_exploit_cwes = {
            "CWE-89": "SQL Injection",  # SQL Injection
            "CWE-79": "Cross-site Scripting (XSS)",  # XSS
            "CWE-94": "Code Injection",  # Code Injection
            "CWE-95": "Improper Neutralization of Directives in Dynamically Evaluated Code",
            "CWE-78": "OS Command Injection",  # OS Command Injection
        }

        if cwe in high_exploit_cwes:
            return Exploitability.FUNCTIONAL
        elif cwe.startswith("CWE-"):
            # Default to POC for known CWEs
            return Exploitability.POC

        return Exploitability.NOT_KNOWN

    @staticmethod
    def _exploitability_to_score(exploitability: Exploitability) -> float:
        """Convert exploitability to 0-1 score."""
        scores = {
            Exploitability.NOT_KNOWN: 0.3,
            Exploitability.UNPROVEN: 0.4,
            Exploitability.POC: 0.6,
            Exploitability.FUNCTIONAL: 0.8,
            Exploitability.HIGH: 1.0,
        }
        return scores.get(exploitability, 0.3)

    @staticmethod
    def _compute_impact_score(family: FindingFamily) -> float:
        """Compute impact score based on family size and severity."""
        # Base impact on severity
        severity_scores = {
            FindingSeverity.CRITICAL: 1.0,
            FindingSeverity.HIGH: 0.8,
            FindingSeverity.MEDIUM: 0.5,
            FindingSeverity.LOW: 0.3,
            FindingSeverity.INFO: 0.1,
        }
        base_impact = severity_scores.get(family.severity_level, 0.5)

        # Scale by number of affected files
        # More files = higher impact
        affected_files = len(set(f.path for f in family.findings if f.path))
        file_factor = min(1.0, math.log(max(1, affected_files) + 1) / math.log(10))

        return base_impact * (0.7 + 0.3 * file_factor)

    def plan_waves(
        self,
        scored_families: List[ScoredFamily] | None = None,
    ) -> WavePlan:
        """Plan remediation waves."""
        if scored_families is None:
            scored_families = self.scored_families

        if not scored_families:
            return WavePlan()

        # Calculate total risk
        total_risk = sum(f.risk_score for f in scored_families)

        # Wave 1: Top 10% of findings (should contain ~80% of risk)
        wave_1_count = max(1, len(scored_families) // 10)
        wave_1 = scored_families[:wave_1_count]
        wave_1_risk = sum(f.risk_score for f in wave_1)

        # Wave 2: Next 40% (cumulative 50%)
        wave_2_count = max(1, len(scored_families) // 2 - wave_1_count)
        wave_2 = scored_families[wave_1_count : wave_1_count + wave_2_count]
        wave_2_risk = sum(f.risk_score for f in wave_2)

        # Wave 3: Remaining 50%
        wave_3 = scored_families[wave_1_count + wave_2_count :]

        # Assign wave numbers
        for family in wave_1:
            family.wave = 1
        for family in wave_2:
            family.wave = 2
        for family in wave_3:
            family.wave = 3

        return WavePlan(
            wave_1=wave_1,
            wave_2=wave_2,
            wave_3=wave_3,
            total_risk=total_risk,
            wave_1_risk=wave_1_risk,
            wave_2_risk=wave_2_risk,
        )


def plan_waves(
    scored_families: List[ScoredFamily],
) -> WavePlan:
    """Plan remediation waves."""
    scorer = RiskScorer()
    return scorer.plan_waves(scored_families)
