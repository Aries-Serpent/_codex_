"""
Infrastructure Linter Agent - AFTERMATH Phase (Reporter)

This module tracks outcomes, extracts lessons learned, and records patterns
in the cognitive brain for continuous improvement of IaC scanning policies.

#AFTERMATH_PATTERN_IDENTIFIED: iac_outcome_tracking
#AFTERMATH_METRIC: outcomes_tracked
#AFTERMATH_LESSON_LEARNED: iac_patterns_learned
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import Counter

# Cognitive brain integration
try:
    from .....agents.cognitive_brain import CognitiveBrain
except ImportError:
    # Fallback if cognitive brain not available
    class CognitiveBrain:
        def __init__(self, db_path: Optional[str] = None):
            self.db_path = db_path
        
        def record_pattern(self, pattern_type: str, success: bool, metadata: Dict[str, Any]):
            pass


@dataclass
class AftermathReport:
    """Comprehensive outcome report for an IaC scanning cycle"""
    outcome: str  # approved/blocked/warnings_issued
    files_scanned: int
    issues_found: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    security_score: int
    most_common_issues: List[Dict[str, Any]]
    lessons_learned: Dict[str, str]
    pattern_recorded: bool
    timestamp: str
    tools_detected: List[str] = field(default_factory=list)
    blocking_issues: int = 0
    warning_issues: int = 0


class IaCReporter:
    """
    AFTERMATH phase - Track outcomes, learn patterns, update cognitive brain
    
    Responsibilities:
    - Determine final outcome (approved/blocked/warnings_issued)
    - Extract lessons learned from scan results
    - Record patterns in cognitive brain for future improvements
    - Track metrics over time
    - Generate long-term trend analysis
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize reporter with cognitive brain connection
        
        Args:
            db_path: Path to cognitive brain database (default: CODEX_DB_PATH env var)
        """
        if db_path is None:
            db_path = os.getenv("CODEX_DB_PATH", "/tmp/codex_brain.db")
        
        self.brain = CognitiveBrain(db_path)
        
        # #AFTERMATH_METRIC: outcomes_tracked
        self.outcomes_tracked = 0
    
    def generate_aftermath_report(
        self,
        scan_results: Dict[str, Any],
        validation_results: Dict[str, Any],
        enforcement_results: Dict[str, Any]
    ) -> AftermathReport:
        """
        Generate comprehensive aftermath report from all PDA Loop phases
        
        Args:
            scan_results: Output from scanner.py (PERCEIVE)
            validation_results: Output from validator.py (DECIDE)
            enforcement_results: Output from enforcer.py (ACT)
        
        Returns:
            AftermathReport with outcome, lessons, and recorded patterns
        """
        # Determine final outcome
        outcome = self._determine_outcome(enforcement_results, validation_results)
        
        # Extract lessons learned
        lessons = self._extract_lessons(scan_results, validation_results, enforcement_results)
        
        # Identify most common issues
        common_issues = self._identify_common_issues(scan_results)
        
        # Record pattern in cognitive brain
        pattern_recorded = self._record_pattern(
            scan_results,
            validation_results,
            enforcement_results,
            outcome
        )
        
        # Count issues by severity
        critical_count = validation_results.get("critical_issues", 0)
        high_count = validation_results.get("high_issues", 0)
        medium_count = validation_results.get("medium_issues", 0)
        low_count = validation_results.get("low_issues", 0)
        
        # Count blocking vs warning issues
        blocking_issues = len(validation_results.get("blockers", []))
        warning_issues = len(validation_results.get("warnings", []))
        
        # Track this outcome
        self.outcomes_tracked += 1
        
        # #AFTERMATH_PATTERN_IDENTIFIED: iac_outcome_tracking
        report = AftermathReport(
            outcome=outcome,
            files_scanned=scan_results.get("files_scanned", 0),
            issues_found=critical_count + high_count + medium_count + low_count,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            security_score=validation_results.get("security_score", 0),
            most_common_issues=common_issues,
            lessons_learned=lessons,
            pattern_recorded=pattern_recorded,
            timestamp=datetime.utcnow().isoformat() + "Z",
            tools_detected=scan_results.get("tools_detected", []),
            blocking_issues=blocking_issues,
            warning_issues=warning_issues
        )
        
        return report
    
    def _determine_outcome(
        self,
        enforcement_results: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> str:
        """
        Determine final outcome of IaC scanning cycle
        
        Returns:
            "blocked" if CI was blocked
            "approved" if no issues or only low severity
            "warnings_issued" if passed but with warnings
        """
        if enforcement_results.get("ci_blocked", False):
            return "blocked"
        
        # Check if any warnings were issued
        warnings = validation_results.get("warnings", [])
        if len(warnings) > 0:
            return "warnings_issued"
        
        return "approved"
    
    def _extract_lessons(
        self,
        scan_results: Dict[str, Any],
        validation_results: Dict[str, Any],
        enforcement_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Extract lessons learned from this scanning cycle
        
        #AFTERMATH_LESSON_LEARNED: iac_patterns_learned
        
        Returns:
            Dictionary of lesson categories and observations
        """
        lessons = {}
        
        # Tool coverage analysis
        tools_detected = scan_results.get("tools_detected", [])
        if tools_detected:
            tools_str = ", ".join(tools_detected)
            lessons["tool_coverage"] = f"IaC tools found: {tools_str}"
        else:
            lessons["tool_coverage"] = "No IaC files detected in repository"
        
        # Recurring pattern identification
        common_issues = self._identify_common_issues(scan_results)
        if common_issues:
            top_issue = common_issues[0]
            lessons["recurring_patterns"] = (
                f"{top_issue['rule_id']} appears {top_issue['count']} times"
            )
        else:
            lessons["recurring_patterns"] = "No recurring issues detected"
        
        # Policy effectiveness measurement
        total_issues = validation_results.get("critical_issues", 0) + \
                      validation_results.get("high_issues", 0) + \
                      validation_results.get("medium_issues", 0) + \
                      validation_results.get("low_issues", 0)
        
        blockers = validation_results.get("blockers", [])
        if total_issues > 0:
            blocked_pct = (len(blockers) / total_issues) * 100
            lessons["policy_effectiveness"] = (
                f"{blocked_pct:.0f}% of high-severity issues caught before merge"
            )
        else:
            lessons["policy_effectiveness"] = "No issues found - policies working well"
        
        # Risk calibration feedback
        security_score = validation_results.get("security_score", 100)
        risk_level = validation_results.get("risk_level", "low")
        lessons["risk_calibration"] = (
            f"Security score {security_score}/100 corresponds to '{risk_level}' risk"
        )
        
        return lessons
    
    def _identify_common_issues(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify most frequently occurring issues across all scanned files
        
        Returns:
            List of dicts with rule_id and count, sorted by frequency
        """
        issue_counter = Counter()
        
        for scan_result in scan_results.get("scan_results", []):
            for finding in scan_result.get("findings", []):
                rule_id = finding.get("rule_id", "unknown")
                issue_counter[rule_id] += 1
        
        # Return top 5 most common issues
        most_common = [
            {"rule_id": rule_id, "count": count}
            for rule_id, count in issue_counter.most_common(5)
        ]
        
        return most_common
    
    def _record_pattern(
        self,
        scan_results: Dict[str, Any],
        validation_results: Dict[str, Any],
        enforcement_results: Dict[str, Any],
        outcome: str
    ) -> bool:
        """
        Record this scanning cycle as a pattern in cognitive brain
        
        This enables the brain to learn from outcomes and improve future
        risk assessments and policy recommendations.
        
        Returns:
            True if pattern was recorded successfully
        """
        try:
            # Prepare metadata for cognitive brain
            metadata = {
                "tools_used": scan_results.get("tools_detected", []),
                "files_scanned": scan_results.get("files_scanned", 0),
                "security_score": validation_results.get("security_score", 0),
                "risk_level": validation_results.get("risk_level", "unknown"),
                "issues_count": (
                    validation_results.get("critical_issues", 0) +
                    validation_results.get("high_issues", 0) +
                    validation_results.get("medium_issues", 0) +
                    validation_results.get("low_issues", 0)
                ),
                "critical_issues": validation_results.get("critical_issues", 0),
                "high_issues": validation_results.get("high_issues", 0),
                "ci_blocked": enforcement_results.get("ci_blocked", False),
                "outcome": outcome,
                "scan_duration": scan_results.get("duration_seconds", 0)
            }
            
            # Record pattern in cognitive brain
            # Success = approved, Failure = blocked
            success = (outcome == "approved")
            
            self.brain.record_pattern(
                pattern_type="iac_scan_outcome",
                success=success,
                metadata=metadata
            )
            
            return True
        
        except Exception as e:
            # Best-effort: if brain recording fails, continue without it
            # This ensures IaC scanning still works even if brain is unavailable
            print(f"Warning: Failed to record pattern in cognitive brain: {e}")
            return False
