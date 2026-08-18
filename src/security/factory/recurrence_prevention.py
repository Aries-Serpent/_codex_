"""
S6: Recurrence Prevention

Generates suppression patterns from remediated findings.
Updates policy rules to prevent similar findings.

Success metric: Recurrence rate <5% (same type within 30 days)
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .clustering import FindingFamily
from .ingest import NormalizedFinding


@dataclass
class SuppressionPattern:
    """Pattern to suppress similar findings."""
    pattern_id: str
    description: str
    cwe: Optional[str] = None
    pattern_rules: List[str] = field(default_factory=list)  # Regex or literal rules
    affected_families: int = 0
    effectiveness: float = 0.0  # 0-1, where 1 = 100% effective


@dataclass
class RecurrencePrevention:
    """Generates and manages suppression patterns."""
    patterns: List[SuppressionPattern] = field(default_factory=list)
    total_patterns_applied: int = 0
    pattern_effectiveness: Dict[str, float] = field(default_factory=dict)

    def generate_patterns_from_family(
        self,
        family: FindingFamily,
    ) -> List[SuppressionPattern]:
        """Generate suppression patterns from a remediated family."""
        patterns = []

        # Pattern 1: CWE-based suppression
        if family.root_cwe:
            pattern = SuppressionPattern(
                pattern_id=f"cwe_{family.root_cwe.replace('-', '_')}",
                description=f"Suppress {family.root_cwe} findings",
                cwe=family.root_cwe,
                pattern_rules=[f"^{re.escape(family.root_cwe)}$"],
                affected_families=1,
            )
            patterns.append(pattern)

        # Pattern 2: Title-based suppression
        if family.description:
            # Create a normalized title pattern
            title_pattern = self._normalize_title_pattern(family.description)
            pattern = SuppressionPattern(
                pattern_id=f"title_{hash(title_pattern) & 0xFFFFFFFF:08x}",
                description=f"Suppress findings matching: {family.description[:50]}",
                pattern_rules=[title_pattern],
                affected_families=len(family.findings),
            )
            patterns.append(pattern)

        # Pattern 3: Tool-specific suppression
        tools_in_family = set(f.source_tool for f in family.findings)
        for tool in tools_in_family:
            if len([f for f in family.findings if f.source_tool == tool]) > 1:
                pattern = SuppressionPattern(
                    pattern_id=f"tool_{tool}_{family.root_cwe or 'generic'}",
                    description=f"Suppress repeated {tool} findings for {family.root_cwe}",
                    cwe=family.root_cwe,
                    pattern_rules=[f"source_tool={tool}"],
                    affected_families=1,
                )
                patterns.append(pattern)

        # Calculate effectiveness (% of family's findings this pattern would suppress)
        for pattern in patterns:
            pattern.effectiveness = self._estimate_pattern_effectiveness(
                pattern,
                family.findings,
            )

        self.patterns.extend(patterns)
        return patterns

    @staticmethod
    def _normalize_title_pattern(title: str) -> str:
        """Normalize a finding title into a regex pattern."""
        # Remove specific identifiers, keep generic pattern.
        # Use a raw replacement string so Python does not treat \d as an invalid escape.
        normalized = re.sub(r"[0-9]+", r"\\d+", title)
        normalized = re.sub(r"'[^']*'", r"'[^']*'", normalized)
        return normalized

    @staticmethod
    def _estimate_pattern_effectiveness(
        pattern: SuppressionPattern,
        findings: List[NormalizedFinding],
    ) -> float:
        """Estimate how effective this pattern would be."""
        if not findings:
            return 0.0

        # Check how many findings would match
        matched = 0
        for finding in findings:
            for rule in pattern.pattern_rules:
                try:
                    if re.search(rule, finding.title):
                        matched += 1
                        break
                except re.error:
                    # If regex fails, fall back to literal match
                    if rule in finding.title:
                        matched += 1
                        break

        return matched / len(findings) if findings else 0.0

    def apply_pattern(self, pattern: SuppressionPattern) -> int:
        """Apply a suppression pattern (returns count of suppressions)."""
        self.total_patterns_applied += 1
        self.pattern_effectiveness[pattern.pattern_id] = pattern.effectiveness
        return int(pattern.effectiveness * 100)  # Rough estimate

    def get_active_patterns(self) -> List[SuppressionPattern]:
        """Get all active suppression patterns."""
        return sorted(
            self.patterns,
            key=lambda p: p.effectiveness,
            reverse=True,
        )

    def get_pattern_effectiveness_report(self) -> Dict[str, Any]:
        """Generate effectiveness report."""
        if not self.patterns:
            return {
                "total_patterns": 0,
                "avg_effectiveness": 0.0,
            }

        avg_effectiveness = (
            sum(p.effectiveness for p in self.patterns) / len(self.patterns)
        )

        return {
            "total_patterns": len(self.patterns),
            "avg_effectiveness": avg_effectiveness,
            "total_patterns_applied": self.total_patterns_applied,
            "highest_effectiveness": max(p.effectiveness for p in self.patterns),
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "description": p.description,
                    "effectiveness": p.effectiveness,
                }
                for p in self.get_active_patterns()[:10]
            ],
        }


def generate_suppression_patterns(
    families: List[FindingFamily],
) -> List[SuppressionPattern]:
    """Generate suppression patterns from remediated families."""
    prevention = RecurrencePrevention()
    all_patterns = []

    for family in families:
        patterns = prevention.generate_patterns_from_family(family)
        all_patterns.extend(patterns)

    return all_patterns
