"""
False positive filtering module.

Filters security findings based on patterns, confidence scores, and historical data.

#AFTERMATH_PATTERN_IDENTIFIED - Pattern-based false positive reduction
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from .parser import Finding

logger = logging.getLogger(__name__)


@dataclass
class FilterRule:
    """Rule for filtering findings."""
    
    rule_id_pattern: str | None = None
    file_path_pattern: str | None = None
    message_pattern: str | None = None
    min_confidence: float = 0.5
    reason: str = ""


class FalsePositiveFilter:
    """
    Filter for reducing false positives in security scan results.
    
    Uses pattern matching and confidence scoring to filter out likely false positives.
    
    #AFTERMATH_LESSON_LEARNED - Configurable filtering prevents alert fatigue
    """
    
    def __init__(self) -> None:
        """Initialize the filter with default rules."""
        self.rules: list[FilterRule] = []
        self._load_default_rules()
        
        logger.info("FalsePositiveFilter initialized with %d rules", len(self.rules))
    
    def _load_default_rules(self) -> None:
        """Load default filtering rules."""
        # Test files often have intentional security issues
        self.rules.append(FilterRule(
            file_path_pattern=r"test_.*\.py$",
            reason="Test files may contain intentional security issues"
        ))
        
        self.rules.append(FilterRule(
            file_path_pattern=r"tests/.*",
            reason="Test directory files may contain intentional security issues"
        ))
        
        # Example/demo code
        self.rules.append(FilterRule(
            file_path_pattern=r"examples?/.*",
            reason="Example code may be intentionally simplified"
        ))
        
        # Docs and comments
        self.rules.append(FilterRule(
            file_path_pattern=r".*\.md$",
            reason="Documentation files are not executable"
        ))
        
        # Low confidence findings
        self.rules.append(FilterRule(
            min_confidence=0.3,
            reason="Low confidence finding"
        ))
    
    def add_rule(self, rule: FilterRule) -> None:
        """
        Add a custom filtering rule.
        
        Args:
            rule: Filter rule to add
        """
        self.rules.append(rule)
        logger.info("Added filter rule: %s", rule.reason)
    
    def filter_findings(
        self,
        findings: list[Finding],
        apply_default_rules: bool = True
    ) -> tuple[list[Finding], list[Finding]]:
        """
        Filter findings, separating valid from filtered.
        
        Args:
            findings: List of findings to filter
            apply_default_rules: Whether to apply default rules
            
        Returns:
            Tuple of (valid_findings, filtered_findings)
            
        #AFTERMATH_QUALITY_CHECK - Preserves both valid and filtered for audit trail
        """
        valid = []
        filtered = []
        
        for finding in findings:
            if self._should_filter(finding, apply_default_rules):
                filtered.append(finding)
            else:
                valid.append(finding)
        
        logger.info(
            "Filtered %d findings, %d remain valid",
            len(filtered),
            len(valid)
        )
        
        return valid, filtered
    
    def _should_filter(
        self,
        finding: Finding,
        apply_default_rules: bool
    ) -> bool:
        """
        Determine if a finding should be filtered.
        
        Args:
            finding: Finding to evaluate
            apply_default_rules: Whether to apply default rules
            
        Returns:
            True if finding should be filtered
        """
        rules_to_check = self.rules if apply_default_rules else [
            r for r in self.rules if not self._is_default_rule(r)
        ]
        
        for rule in rules_to_check:
            if self._rule_matches(rule, finding):
                logger.debug(
                    "Finding filtered: rule_id=%s, reason=%s",
                    finding.rule_id,
                    rule.reason
                )
                return True
        
        return False
    
    def _rule_matches(self, rule: FilterRule, finding: Finding) -> bool:
        """
        Check if a rule matches a finding.
        
        Args:
            rule: Filter rule
            finding: Finding to check
            
        Returns:
            True if rule matches
        """
        # Check rule_id pattern
        if rule.rule_id_pattern:
            if not re.search(rule.rule_id_pattern, finding.rule_id, re.IGNORECASE):
                return False
        
        # Check file path pattern
        if rule.file_path_pattern:
            matched = False
            for location in finding.locations:
                if re.search(rule.file_path_pattern, location.file_path, re.IGNORECASE):
                    matched = True
                    break
            if not matched:
                return False
        
        # Check message pattern
        if rule.message_pattern:
            if not re.search(rule.message_pattern, finding.message, re.IGNORECASE):
                return False
        
        # Check confidence (if available in metadata)
        if "confidence" in finding.metadata:
            confidence = finding.metadata.get("confidence", 1.0)
            if confidence < rule.min_confidence:
                return True
        
        return True
    
    def _is_default_rule(self, rule: FilterRule) -> bool:
        """
        Check if a rule is a default rule.
        
        Args:
            rule: Rule to check
            
        Returns:
            True if rule is default
        """
        # Default rules have specific patterns
        default_patterns = [
            r"test_.*\.py$",
            r"tests/.*",
            r"examples?/.*",
            r".*\.md$",
        ]
        
        if rule.file_path_pattern in default_patterns:
            return True
        
        if rule.min_confidence == 0.3:
            return True
        
        return False
    
    def get_filter_stats(
        self,
        filtered_findings: list[Finding]
    ) -> dict[str, Any]:
        """
        Get statistics about filtered findings.
        
        Args:
            filtered_findings: List of filtered findings
            
        Returns:
            Dictionary with filter statistics
        """
        stats = {
            "total_filtered": len(filtered_findings),
            "by_rule_id": {},
            "by_file": {},
            "by_level": {},
        }
        
        for finding in filtered_findings:
            # Count by rule ID
            rule_id = finding.rule_id
            stats["by_rule_id"][rule_id] = stats["by_rule_id"].get(rule_id, 0) + 1
            
            # Count by file
            for location in finding.locations:
                file_path = location.file_path
                stats["by_file"][file_path] = stats["by_file"].get(file_path, 0) + 1
            
            # Count by level
            level = finding.level
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
        
        return stats


# #AFTERMATH_METRIC - False positive filter with pattern matching
# #AFTERMATH_PATTERN_IDENTIFIED - Configurable rule-based filtering
