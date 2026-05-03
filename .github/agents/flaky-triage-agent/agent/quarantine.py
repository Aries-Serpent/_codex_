"""
Flaky Test Quarantine Manager - ACT Phase

Executes remediation actions for flaky tests.

#AFTERMATH_PATTERN_IDENTIFIED: flaky_remediation
#AFTERMATH_METRIC: tests_quarantined

PDA Loop: ACT Phase
- Generate flake index file
- Create quarantine lists
- Apply pytest decorators
- Create GitHub issues
- Update test configurations
"""

import json

# Import from classifier
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from classifier import FlakyTestClassification, RemediationAction


@dataclass
class QuarantineEntry:
    """Entry in quarantine list."""
    test_name: str
    quarantined_at: str
    severity: str
    pass_rate: float
    reason: str
    issue_url: Optional[str] = None


class FlakyTestQuarantine:
    """
    Quarantine manager for flaky tests - ACT Phase.

    #AFTERMATH_PATTERN_IDENTIFIED: quarantine_management

    Responsibilities:
    - Create flake index (JSON)
    - Generate quarantine lists (Markdown)
    - Apply @pytest.mark.flaky decorators
    - Create GitHub issues for investigation
    - Update test skip lists
    """

    def __init__(self, repo_path: Path):
        """
        Initialize quarantine manager.

        Args:
            repo_path: Path to repository
        """
        self.repo_path = repo_path
        self.flake_index_path = repo_path / ".codex" / "flake_index.json"
        self.quarantine_list_path = repo_path / ".codex" / "quarantine_list.md"

        #AFTERMATH_METRIC: quarantine_initialized

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        ACT phase - execute remediation actions.

        #AFTERMATH_PATTERN_IDENTIFIED: action_phase

        Args:
            decision: Decision from DECIDE phase (classifier)

        Returns:
            Result dictionary with executed actions
        """
        result = {
            "flake_index_created": False,
            "quarantine_list_created": False,
            "decorators_applied": [],
            "issues_created": [],
            "tests_quarantined": 0,
            "tests_marked_flaky": 0
        }

        classifications = decision.get("classifications", [])
        actions = decision.get("actions", {})

        # Create flake index
        result["flake_index_created"] = self._create_flake_index(classifications)

        # Create quarantine list
        result["quarantine_list_created"] = self._create_quarantine_list(
            classifications, actions
        )

        # Execute actions for each test
        for classification in classifications:
            test_name = classification.test_name
            action = actions.get(test_name, {})

            if action.get("type") == RemediationAction.QUARANTINE.value:
                self._quarantine_test(classification, result)
                result["tests_quarantined"] += 1

            elif action.get("type") == RemediationAction.MARK_FLAKY.value:
                self._mark_test_flaky(classification, result)
                result["tests_marked_flaky"] += 1

            elif action.get("type") == RemediationAction.INVESTIGATE.value:
                self._create_investigation_issue(classification, result)

        #AFTERMATH_METRIC: actions_executed = len(result["decorators_applied"]) + len(result["issues_created"])
        #AFTERMATH_METRIC: tests_quarantined = result["tests_quarantined"]

        return result

    def _create_flake_index(self, classifications: list[FlakyTestClassification]) -> bool:
        """
        Create flake index JSON file.

        #AFTERMATH_PATTERN_IDENTIFIED: index_creation
        """
        try:
            # Ensure directory exists
            self.flake_index_path.parent.mkdir(parents=True, exist_ok=True)

            # Build index
            index = {
                "generated_at": datetime.now().isoformat(),
                "total_flaky_tests": len(classifications),
                "tests": []
            }

            for classification in classifications:
                index["tests"].append({
                    "name": classification.test_name,
                    "severity": classification.severity.value,
                    "confidence": classification.confidence,
                    "pass_rate": classification.pass_rate,
                    "recommended_action": classification.recommended_action.value,
                    "reasons": classification.reasons,
                    "impact_score": classification.impact_score,
                    "metadata": classification.metadata
                })

            # Write to file
            with open(self.flake_index_path, 'w') as f:
                json.dump(index, f, indent=2)

            #AFTERMATH_METRIC: flake_index_size = len(index["tests"])
            return True

        except Exception as e:
            #AFTERMATH_PATTERN_IDENTIFIED: index_creation_failed
            print(f"Failed to create flake index: {e}")
            return False

    def _create_quarantine_list(self, classifications: list[FlakyTestClassification],
                                actions: dict[str, Any]) -> bool:
        """
        Create quarantine list Markdown file.

        #AFTERMATH_PATTERN_IDENTIFIED: quarantine_list_creation
        """
        try:
            # Ensure directory exists
            self.quarantine_list_path.parent.mkdir(parents=True, exist_ok=True)

            # Filter for quarantined tests
            quarantined = [
                c for c in classifications
                if c.recommended_action == RemediationAction.QUARANTINE
            ]

            # Build markdown content
            content = f"""# Flaky Test Quarantine List

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Quarantined**: {len(quarantined)}

## Overview

This list contains tests that have been quarantined due to flakiness. These tests are temporarily excluded from CI runs until they can be fixed.

## Quarantined Tests

| Test Name | Severity | Pass Rate | Reason | Status |
|-----------|----------|-----------|--------|--------|
"""

            for classification in quarantined:
                content += f"| `{classification.test_name}` | {classification.severity.value} | {classification.pass_rate:.1%} | {', '.join(classification.reasons[:2])} | 🔴 Quarantined |\n"

            content += """

## Actions Required

1. **Review quarantined tests** - Check GitHub issues for investigation status
2. **Fix root causes** - Address timing issues, race conditions, or flaky dependencies
3. **Verify fixes** - Run tests locally multiple times before removing from quarantine
4. **Update list** - Remove from quarantine once stable (>99% pass rate for 30 days)

## Legend

- 🔴 Quarantined - Test excluded from CI
- 🟡 Monitoring - Test under observation
- 🟢 Fixed - Test restored to CI

---

*Generated by flaky-triage-agent.v1*
"""

            # Write to file
            with open(self.quarantine_list_path, 'w') as f:
                f.write(content)

            #AFTERMATH_METRIC: quarantined_count = len(quarantined)
            return True

        except Exception as e:
            #AFTERMATH_PATTERN_IDENTIFIED: quarantine_list_creation_failed
            print(f"Failed to create quarantine list: {e}")
            return False

    def _quarantine_test(self, classification: FlakyTestClassification,
                        result: dict[str, Any]) -> None:
        """
        Quarantine a test by adding skip marker.

        #AFTERMATH_PATTERN_IDENTIFIED: test_quarantine
        """
        # In production, would modify test file to add @pytest.mark.skip
        # For now, just record the action
        result["decorators_applied"].append({
            "test": classification.test_name,
            "decorator": "@pytest.mark.skip(reason='Quarantined due to flakiness')",
            "applied": False  # Would be True if actually modified file
        })

        #AFTERMATH_METRIC: test_quarantined

    def _mark_test_flaky(self, classification: FlakyTestClassification,
                        result: dict[str, Any]) -> None:
        """
        Mark test as flaky with rerun decorator.

        #AFTERMATH_PATTERN_IDENTIFIED: test_marking
        """
        # In production, would modify test file to add @pytest.mark.flaky
        # For now, just record the action
        result["decorators_applied"].append({
            "test": classification.test_name,
            "decorator": "@pytest.mark.flaky(reruns=3, reruns_delay=2)",
            "applied": False  # Would be True if actually modified file
        })

        #AFTERMATH_METRIC: test_marked_flaky

    def _create_investigation_issue(self, classification: FlakyTestClassification,
                                   result: dict[str, Any]) -> None:
        """
        Create GitHub issue for test investigation.

        #AFTERMATH_PATTERN_IDENTIFIED: issue_creation
        """
        # In production, would create actual GitHub issue
        # For now, just record the intent
        issue = {
            "title": f"[Flaky Test] {classification.test_name}",
            "body": self._generate_issue_body(classification),
            "labels": ["flaky-test", f"severity-{classification.severity.value}"],
            "created": False  # Would be True if actually created
        }

        result["issues_created"].append(issue)

        #AFTERMATH_METRIC: issue_created

    def _generate_issue_body(self, classification: FlakyTestClassification) -> str:
        """Generate GitHub issue body."""
        body = f"""## Flaky Test Detected

**Test Name**: `{classification.test_name}`
**Severity**: {classification.severity.value}
**Pass Rate**: {classification.pass_rate:.1%}
**Confidence**: {classification.confidence:.1%}
**Impact Score**: {classification.impact_score:.2f}

### Reasons for Flakiness

"""
        for i, reason in enumerate(classification.reasons, 1):
            body += f"{i}. {reason}\n"

        body += f"""

### Metadata

- **Total Runs**: {classification.metadata.get('total_runs', 'N/A')}
- **Failed Count**: {classification.metadata.get('failed_count', 'N/A')}
- **Avg Duration**: {classification.metadata.get('avg_duration', 0):.2f}s
- **Std Duration**: {classification.metadata.get('std_duration', 0):.2f}s

### Recommended Action

{classification.recommended_action.value}

### Next Steps

1. Review test code for timing issues or race conditions
2. Check for external dependencies (network, database, etc.)
3. Run test locally multiple times to reproduce
4. Fix root cause
5. Verify stability (>99% pass rate) before removing from quarantine

---

*Auto-generated by flaky-triage-agent.v1*
"""
        return body

    def get_summary(self) -> dict[str, Any]:
        """
        Generate quarantine summary.

        #AFTERMATH_METRIC: quarantine_summary_generated

        Returns:
            Summary dictionary
        """
        summary = {
            "flake_index_path": str(self.flake_index_path),
            "quarantine_list_path": str(self.quarantine_list_path)
        }

        # Load existing index if available
        if self.flake_index_path.exists():
            try:
                with open(self.flake_index_path) as f:
                    index = json.load(f)
                    summary["total_in_index"] = index.get("total_flaky_tests", 0)
            except (OSError, json.JSONDecodeError):
                # Best-effort: if flake index is missing or malformed,
                # continue with empty index. Will be regenerated on next run.
                pass

        #AFTERMATH_LESSON_LEARNED: quarantine_patterns_identified
        return summary
