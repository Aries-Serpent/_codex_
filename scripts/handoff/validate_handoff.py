#!/usr/bin/env python3
"""
Handoff Validation Utility

Validates agent handoffs for completeness, context transfer, and success criteria.
Provides pre-handoff and post-handoff validation checks.

Features:
- Validate context completeness
- Check deliverables exist
- Verify handoff chain integrity
- Generate validation reports
- Support retry logic for failed handoffs

Usage:
    python validate_handoff.py --check HO-001
    python validate_handoff.py --pre-check --phase "Plan 1"
    python validate_handoff.py --post-check HO-001
    python validate_handoff.py --chain-check
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Constants
REPO_ROOT = Path(__file__).parent.parent.parent
TRACKING_FILE = REPO_ROOT / ".codex" / "handoff_tracking.json"
ACTION_LOG_PATH = REPO_ROOT / ".codex" / "action_log.ndjson"
PATTERN_STORE = REPO_ROOT / ".codex" / "cognitive_brain" / "pattern_learning_store.json"


class ValidationResult:
    """Represents the result of a validation check."""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.severity = "info"  # info, warning, error
        self.details: Dict[str, Any] = {}

    def pass_check(self, message: str = "", details: Optional[Dict] = None):
        """Mark check as passed."""
        self.passed = True
        self.message = message or f"{self.name} passed"
        self.severity = "info"
        if details:
            self.details = details

    def warn(self, message: str, details: Optional[Dict] = None):
        """Mark check as passed with warning."""
        self.passed = True
        self.message = message
        self.severity = "warning"
        if details:
            self.details = details

    def fail(self, message: str, details: Optional[Dict] = None):
        """Mark check as failed."""
        self.passed = False
        self.message = message
        self.severity = "error"
        if details:
            self.details = details

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity,
            "details": self.details
        }


class ValidationReport:
    """Collection of validation results."""

    def __init__(self, title: str = "Handoff Validation Report"):
        self.title = title
        self.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.results: List[ValidationResult] = []
        self.summary: Dict[str, int] = {
            "total": 0,
            "passed": 0,
            "warnings": 0,
            "failed": 0
        }

    def add_result(self, result: ValidationResult):
        """Add a validation result."""
        self.results.append(result)
        self.summary["total"] += 1

        if result.passed:
            self.summary["passed"] += 1
            if result.severity == "warning":
                self.summary["warnings"] += 1
        else:
            self.summary["failed"] += 1

    @property
    def is_valid(self) -> bool:
        """Check if all validations passed."""
        return self.summary["failed"] == 0

    def to_markdown(self) -> str:
        """Generate markdown report."""
        # Status icon
        if self.summary["failed"] > 0:
            status_icon = "❌"
            status_text = "FAILED"
        elif self.summary["warnings"] > 0:
            status_icon = "⚠️"
            status_text = "PASSED WITH WARNINGS"
        else:
            status_icon = "✅"
            status_text = "PASSED"

        report = f"""## {status_icon} {self.title}

**Status**: {status_text}
**Timestamp**: {self.timestamp}

---

### 📊 Summary

| Metric | Count |
|--------|-------|
| Total Checks | {self.summary['total']} |
| ✅ Passed | {self.summary['passed']} |
| ⚠️ Warnings | {self.summary['warnings']} |
| ❌ Failed | {self.summary['failed']} |

---

### 📋 Check Results

"""
        for result in self.results:
            if result.severity == "error":
                icon = "❌"
            elif result.severity == "warning":
                icon = "⚠️"
            else:
                icon = "✅"

            report += f"- {icon} **{result.name}**: {result.message}\n"

            if result.details:
                for key, value in result.details.items():
                    report += f"  - {key}: {value}\n"

        report += f"""
---

**Generated**: {self.timestamp}
"""
        return report

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "timestamp": self.timestamp,
            "is_valid": self.is_valid,
            "summary": self.summary,
            "results": [r.to_dict() for r in self.results]
        }


class HandoffValidator:
    """Validates handoffs for completeness and correctness."""

    def __init__(self):
        self.tracking_data = self._load_tracking_data()

    def _load_tracking_data(self) -> Dict[str, Any]:
        """Load handoff tracking data."""
        if TRACKING_FILE.exists():
            try:
                with open(TRACKING_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"handoffs": [], "metrics": {}}

    def _save_tracking_data(self, data: Dict[str, Any]):
        """Save handoff tracking data."""
        data["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACKING_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def get_handoff(self, handoff_id: str) -> Optional[Dict[str, Any]]:
        """Get a handoff by ID."""
        for handoff in self.tracking_data.get("handoffs", []):
            if handoff["id"] == handoff_id:
                return handoff
        return None

    def validate_context_completeness(
        self,
        handoff: Dict[str, Any]
    ) -> ValidationResult:
        """Validate that handoff context is complete."""
        result = ValidationResult("Context Completeness")

        required_fields = [
            "id", "from_agent", "to_agent", "phase", "status", "created"
        ]

        missing = [f for f in required_fields if not handoff.get(f)]

        if missing:
            result.fail(
                f"Missing required fields: {', '.join(missing)}",
                {"missing_fields": missing}
            )
        else:
            result.pass_check("All required fields present")

        return result

    def validate_context_summary(
        self,
        handoff: Dict[str, Any]
    ) -> ValidationResult:
        """Validate context summary has meaningful data."""
        result = ValidationResult("Context Summary")

        summary = handoff.get("context_summary", {})

        if not summary:
            result.warn("No context summary provided")
            return result

        total_items = (
            summary.get("completed_tasks", 0) +
            summary.get("deliverables", 0) +
            summary.get("files_modified", 0)
        )

        if total_items == 0:
            result.warn(
                "Context summary has no completed work",
                {"summary": summary}
            )
        else:
            result.pass_check(
                f"Context includes {total_items} work items",
                {"summary": summary}
            )

        return result

    def validate_deliverables_exist(
        self,
        deliverable_paths: List[str]
    ) -> ValidationResult:
        """Validate that deliverable files exist."""
        result = ValidationResult("Deliverables Exist")

        if not deliverable_paths:
            result.warn("No deliverables specified")
            return result

        existing = []
        missing = []

        for path in deliverable_paths:
            full_path = REPO_ROOT / path
            if full_path.exists():
                existing.append(path)
            else:
                missing.append(path)

        if missing:
            result.fail(
                f"{len(missing)}/{len(deliverable_paths)} deliverables missing",
                {"missing": missing, "existing": existing}
            )
        else:
            result.pass_check(
                f"All {len(existing)} deliverables exist",
                {"existing": existing}
            )

        return result

    def validate_chain_integrity(self) -> ValidationResult:
        """Validate handoff chain has no gaps."""
        result = ValidationResult("Chain Integrity")

        handoffs = self.tracking_data.get("handoffs", [])

        if len(handoffs) < 2:
            result.pass_check("Chain too short to validate")
            return result

        # Sort by creation time
        sorted_handoffs = sorted(
            handoffs,
            key=lambda x: x.get("created", "")
        )

        issues = []

        for i in range(1, len(sorted_handoffs)):
            prev = sorted_handoffs[i - 1]
            curr = sorted_handoffs[i]

            # Check that to_agent of prev matches from_agent of curr
            if prev["to_agent"] != curr["from_agent"]:
                issues.append(
                    f"{prev['id']} → {curr['id']}: "
                    f"Agent mismatch ({prev['to_agent']} != {curr['from_agent']})"
                )

            # Check that previous is complete before next starts
            if prev["status"] not in ["complete", "skipped"]:
                if curr["status"] in ["in_progress", "complete"]:
                    issues.append(
                        f"{prev['id']} not complete before {curr['id']} started"
                    )

        if issues:
            result.fail(
                f"{len(issues)} chain integrity issues",
                {"issues": issues}
            )
        else:
            result.pass_check("Chain integrity verified")

        return result

    def validate_timeout(
        self,
        handoff: Dict[str, Any],
        timeout_minutes: int = 60
    ) -> ValidationResult:
        """Check if handoff has timed out."""
        result = ValidationResult("Timeout Check")

        if handoff["status"] not in ["pending", "in_progress"]:
            result.pass_check("Handoff not in active state")
            return result

        created_str = handoff.get("created", "")
        if not created_str:
            result.warn("No creation timestamp")
            return result

        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            now_utc = datetime.now(timezone.utc)
            elapsed = now_utc - created
            elapsed_minutes = elapsed.total_seconds() / 60

            if elapsed_minutes > timeout_minutes:
                result.fail(
                    f"Handoff timed out ({int(elapsed_minutes)} > {timeout_minutes} minutes)",
                    {"elapsed_minutes": int(elapsed_minutes)}
                )
            else:
                result.pass_check(
                    f"Within timeout ({int(elapsed_minutes)} < {timeout_minutes} minutes)"
                )
        except (ValueError, TypeError):
            result.warn("Could not parse creation timestamp")

        return result

    def validate_handoff(
        self,
        handoff_id: str
    ) -> ValidationReport:
        """Run all validations on a specific handoff."""
        report = ValidationReport(f"Validation: {handoff_id}")

        handoff = self.get_handoff(handoff_id)

        if not handoff:
            result = ValidationResult("Handoff Exists")
            result.fail(f"Handoff {handoff_id} not found")
            report.add_result(result)
            return report

        # Run validations
        report.add_result(self.validate_context_completeness(handoff))
        report.add_result(self.validate_context_summary(handoff))
        report.add_result(self.validate_timeout(handoff))

        return report

    def pre_handoff_check(self, phase: str = "") -> ValidationReport:
        """Run pre-handoff validation checks."""
        report = ValidationReport(f"Pre-Handoff Check: {phase or 'Current Session'}")

        # Check action log exists
        result = ValidationResult("Action Log Exists")
        if ACTION_LOG_PATH.exists():
            result.pass_check(f"Found at {ACTION_LOG_PATH}")
        else:
            result.warn("No action log found - handoff may have limited context")
        report.add_result(result)

        # Check pattern store exists
        result = ValidationResult("Pattern Store Available")
        if PATTERN_STORE.exists():
            result.pass_check(f"Found at {PATTERN_STORE}")
        else:
            result.warn("No pattern store - patterns won't be included")
        report.add_result(result)

        # Check tracking file
        result = ValidationResult("Tracking File Ready")
        if TRACKING_FILE.exists():
            result.pass_check("Tracking file exists")
        else:
            result.warn("Tracking file will be created")
        report.add_result(result)

        # Check for pending handoffs
        result = ValidationResult("No Pending Handoffs")
        pending = [
            h for h in self.tracking_data.get("handoffs", [])
            if h["status"] == "pending"
        ]
        if pending:
            result.warn(
                f"{len(pending)} pending handoffs exist",
                {"pending": [h["id"] for h in pending]}
            )
        else:
            result.pass_check("No pending handoffs")
        report.add_result(result)

        return report

    def post_handoff_check(self, handoff_id: str) -> ValidationReport:
        """Run post-handoff validation checks."""
        report = ValidationReport(f"Post-Handoff Check: {handoff_id}")

        handoff = self.get_handoff(handoff_id)

        if not handoff:
            result = ValidationResult("Handoff Recorded")
            result.fail(f"Handoff {handoff_id} not found in tracking")
            report.add_result(result)
            return report

        # Check handoff was recorded
        result = ValidationResult("Handoff Recorded")
        result.pass_check(f"Handoff {handoff_id} recorded successfully")
        report.add_result(result)

        # Check context summary
        report.add_result(self.validate_context_summary(handoff))

        # Check status is appropriate
        result = ValidationResult("Status Updated")
        status = handoff.get("status", "unknown")
        if status in ["pending", "in_progress"]:
            result.pass_check(f"Status: {status}")
        elif status == "complete":
            result.pass_check("Handoff completed")
        else:
            result.warn(f"Unusual status: {status}")
        report.add_result(result)

        return report

    def chain_validation(self) -> ValidationReport:
        """Run full chain validation."""
        report = ValidationReport("Chain Validation")

        # Check chain integrity
        report.add_result(self.validate_chain_integrity())

        # Check for stale handoffs
        result = ValidationResult("No Stale Handoffs")
        stale = []

        for handoff in self.tracking_data.get("handoffs", []):
            timeout_result = self.validate_timeout(handoff, timeout_minutes=120)
            if not timeout_result.passed:
                stale.append(handoff["id"])

        if stale:
            result.warn(
                f"{len(stale)} stale handoffs detected",
                {"stale_handoffs": stale}
            )
        else:
            result.pass_check("No stale handoffs")
        report.add_result(result)

        # Check success rate
        result = ValidationResult("Success Rate")
        metrics = self.tracking_data.get("metrics", {})
        success_rate = metrics.get("success_rate", 0)

        if success_rate >= 90:
            result.pass_check(f"Success rate: {success_rate}%")
        elif success_rate >= 70:
            result.warn(f"Success rate below target: {success_rate}%")
        else:
            result.fail(f"Low success rate: {success_rate}%")
        report.add_result(result)

        return report

    def mark_failed_for_retry(
        self,
        handoff_id: str,
        max_retries: int = 3
    ) -> Tuple[bool, str]:
        """Mark a failed handoff for retry."""
        handoff = self.get_handoff(handoff_id)

        if not handoff:
            return False, f"Handoff {handoff_id} not found"

        retry_count = handoff.get("retry_count", 0)

        if retry_count >= max_retries:
            return False, f"Max retries ({max_retries}) exceeded"

        # Update handoff
        handoff["status"] = "pending"
        handoff["retry_count"] = retry_count + 1
        handoff["updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Update metrics
        metrics = self.tracking_data.get("metrics", {})
        metrics["failed"] = max(0, metrics.get("failed", 0) - 1)
        metrics["pending"] = metrics.get("pending", 0) + 1

        self._save_tracking_data(self.tracking_data)

        return True, f"Handoff {handoff_id} marked for retry (attempt {retry_count + 1})"


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Handoff Validation Utility"
    )

    parser.add_argument(
        "--check", "-c",
        help="Validate a specific handoff by ID"
    )
    parser.add_argument(
        "--pre-check",
        action="store_true",
        help="Run pre-handoff validation"
    )
    parser.add_argument(
        "--post-check",
        help="Run post-handoff validation for ID"
    )
    parser.add_argument(
        "--chain-check",
        action="store_true",
        help="Validate entire handoff chain"
    )
    parser.add_argument(
        "--phase",
        default="",
        help="Phase name for pre-check"
    )
    parser.add_argument(
        "--retry",
        help="Mark handoff for retry"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for validation report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    validator = HandoffValidator()
    report: Optional[ValidationReport] = None

    if args.check:
        report = validator.validate_handoff(args.check)
    elif args.pre_check:
        report = validator.pre_handoff_check(args.phase)
    elif args.post_check:
        report = validator.post_handoff_check(args.post_check)
    elif args.chain_check:
        report = validator.chain_validation()
    elif args.retry:
        success, message = validator.mark_failed_for_retry(args.retry)
        print(f"{'✅' if success else '❌'} {message}")
        return
    else:
        parser.print_help()
        return

    if report:
        output = json.dumps(report.to_dict(), indent=2) if args.json else report.to_markdown()

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Report saved: {args.output}")
        else:
            print(output)

        # Exit with appropriate code
        if not report.is_valid:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
