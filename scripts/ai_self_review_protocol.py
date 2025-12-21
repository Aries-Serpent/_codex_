#!/usr/bin/env python3
"""
AI Assistant Self-Review Protocol Implementation

This module implements a comprehensive self-review protocol that ensures
AI assistants perform thorough validation before concluding any interaction.
It provides a deterministic, iterative process that prevents premature
completion through autonomous self-healing cycles.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import json
import hashlib
from pathlib import Path
import sys


class Priority(Enum):
    """Priority levels for identified issues."""
    CRITICAL = 1  # Must fix before proceeding
    HIGH = 2      # Should fix in this session
    MEDIUM = 3    # Can defer with documentation
    LOW = 4       # Nice to have


class IssueType(Enum):
    """Types of issues that can be identified."""
    GAP = "gap"
    RISK = "risk"
    INCOMPLETE = "incomplete"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"
    INCONSISTENCY = "inconsistency"
    MISSING_TEST = "missing_test"
    MISSING_DOC = "missing_doc"


class ReviewStatus(Enum):
    """Status of the review cycle."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    FIXING = "fixing"
    VALIDATING = "validating"
    STABLE = "stable"
    COMPLETE = "complete"


@dataclass
class Issue:
    """Represents a discovered issue during self-review."""
    id: str
    type: IssueType
    priority: Priority
    description: str
    location: str  # File, function, or component
    discovered_at: str
    fixed: bool = False
    fix_description: Optional[str] = None
    mitigation: Optional[str] = None
    validation_status: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            content = f"{self.type.value}:{self.location}:{self.description}"
            self.id = hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass
class ReviewCycle:
    """Represents a single iteration of the self-review cycle."""
    cycle_number: int
    started_at: str
    completed_at: Optional[str] = None
    issues_identified: List[Issue] = field(default_factory=list)
    issues_fixed: List[str] = field(default_factory=list)  # Issue IDs
    issues_deferred: List[str] = field(default_factory=list)  # Issue IDs
    changes_made: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    convergence_score: float = 0.0


@dataclass
class ReviewReport:
    """Complete self-review report."""
    session_id: str
    task_description: str
    started_at: str
    completed_at: Optional[str] = None
    status: ReviewStatus = ReviewStatus.DRAFT
    cycles: List[ReviewCycle] = field(default_factory=list)
    total_issues_identified: int = 0
    total_issues_fixed: int = 0
    total_issues_deferred: int = 0
    remaining_high_priority: int = 0
    production_ready: bool = False
    final_notes: str = ""


class SelfReviewProtocol:
    """Implements the autonomous self-review protocol."""

    # Convergence criteria
    MAX_CYCLES = 10
    CONVERGENCE_THRESHOLD = 0.9  # 90% of high-priority issues resolved
    MIN_CYCLES = 2  # At least 2 cycles for thorough review

    def __init__(self, task_description: str, output_dir: Optional[Path] = None):
        self.task_description = task_description
        self.output_dir = output_dir or Path(".codex/self_review")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate session ID
        timestamp = datetime.now().isoformat()
        session_content = f"{task_description}:{timestamp}"
        session_id = hashlib.md5(session_content.encode()).hexdigest()[:16]
        
        self.report = ReviewReport(
            session_id=session_id,
            task_description=task_description,
            started_at=timestamp
        )
        
        self.current_cycle = 0
        self.all_issues: Dict[str, Issue] = {}  # Issue ID -> Issue

    def start_cycle(self) -> ReviewCycle:
        """Start a new review cycle."""
        self.current_cycle += 1
        cycle = ReviewCycle(
            cycle_number=self.current_cycle,
            started_at=datetime.now().isoformat()
        )
        self.report.cycles.append(cycle)
        self.report.status = ReviewStatus.IN_REVIEW
        return cycle

    def identify_issue(
        self,
        issue_type: IssueType,
        priority: Priority,
        description: str,
        location: str,
        mitigation: Optional[str] = None
    ) -> Issue:
        """Identify and register a new issue."""
        issue = Issue(
            id="",  # Will be auto-generated
            type=issue_type,
            priority=priority,
            description=description,
            location=location,
            discovered_at=datetime.now().isoformat(),
            mitigation=mitigation
        )
        
        # Add to tracking
        self.all_issues[issue.id] = issue
        
        # Add to current cycle
        if self.report.cycles:
            self.report.cycles[-1].issues_identified.append(issue)
        
        self.report.total_issues_identified += 1
        
        return issue

    def fix_issue(self, issue_id: str, fix_description: str) -> bool:
        """Mark an issue as fixed with description."""
        if issue_id not in self.all_issues:
            return False
        
        issue = self.all_issues[issue_id]
        issue.fixed = True
        issue.fix_description = fix_description
        issue.validation_status = "pending"
        
        # Track in current cycle
        if self.report.cycles:
            self.report.cycles[-1].issues_fixed.append(issue_id)
        
        self.report.total_issues_fixed += 1
        
        return True

    def defer_issue(self, issue_id: str, reason: str) -> bool:
        """Defer an issue with documented reason."""
        if issue_id not in self.all_issues:
            return False
        
        issue = self.all_issues[issue_id]
        issue.mitigation = reason
        
        # Track in current cycle
        if self.report.cycles:
            self.report.cycles[-1].issues_deferred.append(issue_id)
        
        self.report.total_issues_deferred += 1
        
        return True

    def validate_fix(self, issue_id: str, validation_result: str) -> bool:
        """Validate that a fix works correctly."""
        if issue_id not in self.all_issues:
            return False
        
        issue = self.all_issues[issue_id]
        issue.validation_status = validation_result
        
        return True

    def calculate_convergence(self) -> float:
        """Calculate convergence score based on resolved issues."""
        high_priority_issues = [
            issue for issue in self.all_issues.values()
            if issue.priority in (Priority.CRITICAL, Priority.HIGH)
        ]
        
        if not high_priority_issues:
            return 1.0
        
        fixed_high_priority = sum(
            1 for issue in high_priority_issues if issue.fixed
        )
        
        return fixed_high_priority / len(high_priority_issues)

    def check_convergence(self) -> Tuple[bool, str]:
        """Check if the review has converged (ready to complete)."""
        # Must have minimum cycles
        if self.current_cycle < self.MIN_CYCLES:
            return False, f"Need at least {self.MIN_CYCLES} cycles (current: {self.current_cycle})"
        
        # Check convergence score
        convergence = self.calculate_convergence()
        if convergence < self.CONVERGENCE_THRESHOLD:
            return False, f"Convergence {convergence:.1%} below threshold {self.CONVERGENCE_THRESHOLD:.0%}"
        
        # Check for critical issues
        critical_unfixed = [
            issue for issue in self.all_issues.values()
            if issue.priority == Priority.CRITICAL and not issue.fixed
        ]
        
        if critical_unfixed:
            return False, f"{len(critical_unfixed)} critical issue(s) remain unfixed"
        
        # Max cycles reached
        if self.current_cycle >= self.MAX_CYCLES:
            return True, f"Max cycles ({self.MAX_CYCLES}) reached"
        
        return True, "Convergence criteria met"

    def complete_cycle(self, changes_made: List[str]) -> ReviewCycle:
        """Complete the current review cycle."""
        if not self.report.cycles:
            raise ValueError("No active cycle to complete")
        
        cycle = self.report.cycles[-1]
        cycle.completed_at = datetime.now().isoformat()
        cycle.changes_made = changes_made
        cycle.convergence_score = self.calculate_convergence()
        
        return cycle

    def finalize_review(self, final_notes: str = "") -> ReviewReport:
        """Finalize the review and generate report."""
        self.report.completed_at = datetime.now().isoformat()
        self.report.status = ReviewStatus.COMPLETE
        self.report.final_notes = final_notes
        
        # Calculate remaining high-priority issues
        self.report.remaining_high_priority = len([
            issue for issue in self.all_issues.values()
            if issue.priority in (Priority.CRITICAL, Priority.HIGH) and not issue.fixed
        ])
        
        # Determine production readiness
        convergence = self.calculate_convergence()
        self.report.production_ready = (
            convergence >= self.CONVERGENCE_THRESHOLD and
            self.report.remaining_high_priority == 0
        )
        
        return self.report

    def save_report(self, filename: Optional[str] = None) -> Path:
        """Save the review report to disk."""
        if not filename:
            filename = f"review_{self.report.session_id}.json"
        
        report_path = self.output_dir / filename
        
        # Convert to dict for JSON serialization
        report_dict = self._to_dict()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)
        
        return report_path

    def _to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        report_dict = asdict(self.report)
        
        # Convert enums in issues
        for cycle in report_dict['cycles']:
            for issue in cycle['issues_identified']:
                issue['type'] = issue['type'].value if isinstance(issue['type'], Enum) else issue['type']
                issue['priority'] = issue['priority'].value if isinstance(issue['priority'], Enum) else issue['priority']
        
        report_dict['status'] = self.report.status.value
        
        return report_dict

    def print_summary(self):
        """Print a summary of the review."""
        print("\n" + "="*70)
        print(f"Self-Review Protocol Summary - Session {self.report.session_id}")
        print("="*70)
        print(f"Task: {self.report.task_description}")
        print(f"Status: {self.report.status.value}")
        print(f"Cycles Completed: {len(self.report.cycles)}")
        print(f"\nIssues:")
        print(f"  Total Identified: {self.report.total_issues_identified}")
        print(f"  Fixed: {self.report.total_issues_fixed}")
        print(f"  Deferred: {self.report.total_issues_deferred}")
        print(f"  Remaining High-Priority: {self.report.remaining_high_priority}")
        print(f"\nConvergence: {self.calculate_convergence():.1%}")
        print(f"Production Ready: {'✓ Yes' if self.report.production_ready else '✗ No'}")
        
        # Show critical/high priority issues
        critical_issues = [
            issue for issue in self.all_issues.values()
            if issue.priority in (Priority.CRITICAL, Priority.HIGH) and not issue.fixed
        ]
        
        if critical_issues:
            print(f"\n⚠ Remaining High-Priority Issues:")
            for issue in critical_issues[:5]:  # Show top 5
                print(f"  - [{issue.priority.name}] {issue.description}")
                print(f"    Location: {issue.location}")
                if issue.mitigation:
                    print(f"    Mitigation: {issue.mitigation}")
        
        print("="*70)


def main():
    """Demo usage of the self-review protocol."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Self-Review Protocol")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--output", type=Path, help="Output directory")
    parser.add_argument("--demo", action="store_true", help="Run demo cycle")
    
    args = parser.parse_args()
    
    # Initialize protocol
    protocol = SelfReviewProtocol(args.task, args.output)
    
    if args.demo:
        # Demo cycle 1
        print("Starting Cycle 1: Initial Review")
        protocol.start_cycle()
        
        # Identify some issues
        protocol.identify_issue(
            IssueType.MISSING_TEST,
            Priority.HIGH,
            "Core functionality lacks unit tests",
            "src/module.py",
            "Add tests in next iteration"
        )
        
        protocol.identify_issue(
            IssueType.MISSING_DOC,
            Priority.MEDIUM,
            "API documentation incomplete",
            "README.md",
            "Document in separate PR"
        )
        
        protocol.complete_cycle(["Identified 2 issues"])
        
        # Demo cycle 2
        print("\nStarting Cycle 2: Fix and Validate")
        protocol.start_cycle()
        
        # Fix the high-priority issue
        issues = list(protocol.all_issues.keys())
        if issues:
            protocol.fix_issue(issues[0], "Added comprehensive unit tests")
            protocol.validate_fix(issues[0], "Tests passing")
        
        protocol.complete_cycle(["Fixed high-priority testing issue"])
        
        # Check convergence
        converged, reason = protocol.check_convergence()
        print(f"\nConvergence Check: {converged} - {reason}")
        
        # Finalize
        protocol.finalize_review("Demo cycle completed successfully")
        
        # Print summary
        protocol.print_summary()
        
        # Save report
        report_path = protocol.save_report()
        print(f"\n✓ Report saved: {report_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
