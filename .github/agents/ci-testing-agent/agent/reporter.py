"""
Artifact Uploader and PR/Commit Helpers
Reports results and manages GitHub integration.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ArtifactReporter:
    """Reports test results and uploads artifacts."""

    def __init__(self, workspace: Path):
        """
        Initialize ArtifactReporter.

        Args:
            workspace: Path to repository workspace
        """
        self.workspace = workspace
        self.reports_dir = workspace / ".reports"
        self.reports_dir.mkdir(exist_ok=True)

    def report(self, result: dict[str, Any]) -> None:
        """
        Generate and save test report.

        Args:
            result: Result dictionary from agent execution
        """
        # Add timestamp if not present
        if "timestamp" not in result:
            result["timestamp"] = datetime.utcnow().isoformat()

        # Generate JSON report
        timestamp = result.get("timestamp", "latest").replace(":", "-").replace(".", "-")
        report_file = self.reports_dir / f"report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(result, f, indent=2)

        print(f"📄 Report saved: {report_file}")

        # Generate markdown summary
        summary = self._generate_summary(result)
        summary_file = self.reports_dir / f"summary_{timestamp}.md"

        with open(summary_file, "w") as f:
            f.write(summary)

        print(f"📝 Summary saved: {summary_file}")

        # Also save as latest
        latest_summary = self.reports_dir / "summary_latest.md"
        with open(latest_summary, "w") as f:
            f.write(summary)

    def _generate_summary(self, result: dict[str, Any]) -> str:
        """
        Generate markdown summary of results.

        Args:
            result: Result dictionary

        Returns:
            Markdown summary string
        """
        status = result.get("status", "unknown")
        emoji = self._status_emoji(status)
        timestamp = result.get("timestamp", "N/A")

        summary = f"""# CI Testing Agent Report

## Status: {emoji} {status.upper()}

**Timestamp**: {timestamp}

---

"""

        # Task-specific sections
        task_type = result.get("task_type", result.get("type", "unknown"))

        if task_type == "generate_tests":
            summary += self._summary_generate_tests(result)
        elif task_type == "validate_coverage":
            summary += self._summary_validate_coverage(result)
        elif task_type == "execute_tests":
            summary += self._summary_execute_tests(result)
        elif task_type == "debug_ci_failure":
            summary += self._summary_debug_ci(result)
        else:
            summary += self._summary_generic(result)

        # Error section
        if "error" in result:
            summary += f"\n## ⚠️ Error\n\n```\n{result['error']}\n```\n"

        return summary

    def _summary_generate_tests(self, result: dict[str, Any]) -> str:
        """Generate summary for test generation task."""
        summary = "## Test Generation Results\n\n"

        files_generated = result.get("files_generated", 0)
        summary += f"- **Files Generated**: {files_generated}\n"
        summary += f"- **Target Module**: {result.get('module', 'N/A')}\n"
        summary += f"- **Coverage Threshold**: {result.get('threshold', 'N/A')}%\n\n"

        if files_generated > 0 and "test_files" in result:
            summary += "### Generated Test Files\n\n"
            for test_file in result["test_files"]:
                summary += f"- `{test_file['path']}` (function: `{test_file['function']}`)\n"

        return summary

    def _summary_validate_coverage(self, result: dict[str, Any]) -> str:
        """Generate summary for coverage validation task."""
        summary = "## Coverage Validation Results\n\n"

        current = result.get("current_coverage", 0.0)
        baseline = result.get("baseline_coverage", 0.0)
        delta = result.get("delta", 0.0)
        threshold = result.get("threshold", 85)
        meets_threshold = result.get("meets_threshold", False)

        summary += f"- **Current Coverage**: {current:.2f}%\n"
        summary += f"- **Baseline Coverage**: {baseline:.2f}%\n"
        summary += f"- **Delta**: {delta:+.2f}%\n"
        summary += f"- **Target Threshold**: {threshold}%\n"
        summary += f"- **Meets Threshold**: {'✅ Yes' if meets_threshold else '❌ No'}\n\n"

        # Coverage gaps
        gaps = result.get("gaps", [])
        if gaps:
            summary += "### Coverage Gaps\n\n"
            for gap in gaps:
                summary += f"- {gap}\n"

        # Module coverage
        module_coverage = result.get("module_coverage", {})
        if module_coverage:
            summary += "\n### Module Coverage\n\n"
            for module, coverage in sorted(
                module_coverage.items(), key=lambda x: x[1]
            ):
                summary += f"- `{module}`: {coverage:.2f}%\n"

        return summary

    def _summary_execute_tests(self, result: dict[str, Any]) -> str:
        """Generate summary for test execution task."""
        summary = "## Test Execution Results\n\n"

        returncode = result.get("returncode", -1)
        command = result.get("command", "N/A")

        summary += f"- **Command**: `{command}`\n"
        summary += f"- **Exit Code**: {returncode}\n\n"

        # stdout
        if "stdout" in result and result["stdout"]:
            summary += "### Standard Output\n\n```\n"
            summary += result["stdout"][:1000]  # Truncate long output
            if len(result["stdout"]) > 1000:
                summary += "\n... (truncated)"
            summary += "\n```\n\n"

        # stderr
        if "stderr" in result and result["stderr"]:
            summary += "### Standard Error\n\n```\n"
            summary += result["stderr"][:1000]
            if len(result["stderr"]) > 1000:
                summary += "\n... (truncated)"
            summary += "\n```\n\n"

        return summary

    def _summary_debug_ci(self, result: dict[str, Any]) -> str:
        """Generate summary for CI debugging task."""
        summary = "## CI Debugging Results\n\n"
        summary += self._summary_execute_tests(result)
        return summary

    def _summary_generic(self, result: dict[str, Any]) -> str:
        """Generate generic summary for unknown task types."""
        summary = "## Results\n\n"

        for key, value in result.items():
            if key not in ["timestamp", "status", "task_type", "type"]:
                summary += f"- **{key}**: {value}\n"

        return summary

    def _status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        emoji_map = {
            "success": "✅",
            "failure": "❌",
            "error": "🔥",
            "timeout": "⏱️",
            "below_threshold": "⚠️",
        }
        return emoji_map.get(status, "❓")

    def upload_artifact(self, file_path: Path, artifact_name: str) -> bool:
        """
        Upload artifact to GitHub Actions.

        Args:
            file_path: Path to file to upload
            artifact_name: Name for artifact

        Returns:
            True if upload would succeed (placeholder for actual GitHub integration)
        """
        print(f"📦 Artifact ready for upload: {artifact_name}")
        print(f"   File: {file_path}")
        # Would integrate with GitHub Actions artifact API
        return True

    def create_pr_comment(self, pr_number: int, comment: str) -> bool:
        """
        Create comment on pull request.

        Args:
            pr_number: Pull request number
            comment: Comment text

        Returns:
            True if comment would be created (placeholder for actual GitHub integration)
        """
        print(f"💬 PR comment ready for #{pr_number}")
        # Would integrate with GitHub API
        return True

    def update_commit_status(
        self, commit_sha: str, state: str, description: str, context: str = "ci-testing-agent"
    ) -> bool:
        """
        Update commit status.

        Args:
            commit_sha: Commit SHA
            state: Status state ('pending', 'success', 'failure', 'error')
            description: Status description
            context: Status context

        Returns:
            True if status would be updated (placeholder for actual GitHub integration)
        """
        print("📊 Commit status update ready")
        print(f"   SHA: {commit_sha}")
        print(f"   State: {state}")
        print(f"   Description: {description}")
        # Would integrate with GitHub API
        return True
