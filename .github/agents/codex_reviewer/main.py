"""
Codex Quantum Reviewer - Main Agent Implementation

This module contains the core implementation of the CodexQuantumReviewer agent,
including data structures for review context and results, and the main event
handling logic.
"""

import asyncio
import json
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ReviewContext:
    """
    Context information for PR review.

    Contains all necessary information about the pull request being reviewed,
    including files changed, diff content, branch information, and metadata.
    """

    pr_number: int
    repo: str
    files_changed: list[str]
    diff: str
    base_branch: str
    head_branch: str
    author: str
    description: str
    head_sha: str = ""
    labels: list[str] = field(default_factory=list)
    reviewers: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())


@dataclass
class ReviewResult:
    """
    Result of PR review analysis.

    Contains the outcome of the review including suggestions, confidence level,
    orchestration plan, and identified knowledge gaps.
    """

    status: str  # approved, changes_requested, commented
    confidence: float  # 0.0 to 1.0
    suggestions: list[dict[str, Any]]
    orchestration_plan: dict[str, Any]
    next_steps: list[str]
    knowledge_gaps: list[str]
    review_time_seconds: float = 0.0
    analysis_summary: dict[str, Any] = field(default_factory=dict)


class CodexQuantumReviewer:
    """
    Main reviewer agent implementation.

    Orchestrates the entire review process including code quality analysis,
    security scanning, quantum pattern detection, workflow orchestration,
    and learning from feedback.
    """

    def __init__(
        self,
        github_config: Optional[dict[str, str]] = None,
        head_verifier: Optional[Callable[[ReviewContext], bool]] = None,
    ):
        """
        Initialize the reviewer with all analysis components.

        Args:
            github_config: Optional GitHub API configuration dict
            head_verifier: Optional current-head check executed immediately before publication
        """
        # Import components here to avoid circular dependencies
        from .analyzers import QuantumPatternAnalyzer
        from .github_client import GitHubAPIClient, GitHubConfig
        from .knowledge import KnowledgeGapDetector
        from .learning import SelfEvolutionSystem
        from .orchestration import WorkflowOrchestrator
        from .security import SecurityValidator

        self.pattern_analyzer = QuantumPatternAnalyzer()
        self.security_scanner = SecurityValidator()
        self.orchestrator = WorkflowOrchestrator()
        self.knowledge_engine = KnowledgeGapDetector()
        self.learning_system = SelfEvolutionSystem()
        self.head_verifier = head_verifier

        # Initialize GitHub client with config
        if github_config:
            self.github_client = GitHubAPIClient(GitHubConfig(**github_config))
        else:
            self.github_client = GitHubAPIClient()

        logger.info(
            "CodexQuantumReviewer initialized successfully"
        )  # codeql[py/clear-text-logging-sensitive-data]

    async def handle_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Main event handler for all triggers.

        Routes incoming events to appropriate handlers based on event type.

        Args:
            event: Event data from GitHub webhook or Copilot platform

        Returns:
            Dictionary containing handling result and metadata
        """
        event_type = event.get("action")

        logger.info(
            f"Handling event type: {event_type}"
        )  # codeql[py/clear-text-logging-sensitive-data]

        if event_type == "initial_review":
            return await self.perform_initial_review(event)
        if event_type == "incremental_review":
            return await self.perform_incremental_review(event)
        if event_type == "analyze_human_feedback":
            return await self.integrate_feedback(event)
        if event_type == "respond_to_mention":
            return await self.respond_to_mention(event)
        logger.warning(
            f"Unhandled event type: {event_type}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return {"status": "unhandled_event", "event": event_type}

    async def perform_initial_review(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Perform comprehensive initial PR review.

        Executes all analysis tasks in parallel, aggregates results, generates
        orchestration plan, and posts review to GitHub.

        Args:
            event: Event data containing review context

        Returns:
            Dictionary with review completion status and metadata
        """
        start_time = datetime.utcnow()

        # Extract context
        context = self._extract_review_context(event)
        logger.info(
            f"Starting initial review for PR #{context.pr_number}"
        )  # codeql[py/clear-text-logging-sensitive-data]

        # Parallel analysis tasks
        tasks = [
            self._analyze_code_quality(context),
            self._analyze_security(context),
            self._analyze_performance(context),
            self._analyze_documentation(context),
            self._analyze_quantum_patterns(context),
            self._detect_knowledge_gaps(context),
        ]

        # Execute all analysis tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out any exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Analysis task {i} failed: {result}"
                )  # codeql[py/clear-text-logging-sensitive-data]
            else:
                valid_results.append(result)

        # Aggregate results
        review_result = self._aggregate_results(valid_results)

        # Generate orchestration plan
        orchestration = await self.orchestrator.create_plan(context, review_result)
        review_result.orchestration_plan = orchestration

        # Generate next steps
        next_steps = self._generate_next_steps(review_result, context)
        review_result.next_steps = next_steps

        # Calculate review time
        end_time = datetime.utcnow()
        review_result.review_time_seconds = (end_time - start_time).total_seconds()

        # Post review
        try:
            await self._post_review(context, review_result)
        except Exception as exc:
            logger.error(f"Review posting failed for PR #{context.pr_number}: {exc}")
            return {
                "status": "review_failed",
                "pr_number": context.pr_number,
                "review_status": review_result.status,
                "suggestions_count": len(review_result.suggestions),
                "confidence": review_result.confidence,
                "review_time_seconds": review_result.review_time_seconds,
                "error": str(exc),
            }

        # Learn from review
        await self.learning_system.learn_from_review(context, review_result)

        logger.info(
            f"Completed review for PR #{context.pr_number} "
            f"in {review_result.review_time_seconds:.2f}s with "
            f"confidence {review_result.confidence:.2%}"
        )

        return {
            "status": "review_complete",
            "pr_number": context.pr_number,
            "review_status": review_result.status,
            "suggestions_count": len(review_result.suggestions),
            "confidence": review_result.confidence,
            "review_time_seconds": review_result.review_time_seconds,
        }

    async def perform_incremental_review(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Perform incremental review for PR updates.

        Focuses on changed files since last review, providing faster feedback
        for iterative development.

        Args:
            event: Event data with incremental changes

        Returns:
            Dictionary with incremental review results
        """
        logger.info("Performing incremental review")  # codeql[py/clear-text-logging-sensitive-data]
        # TODO: Implement incremental review logic
        # For now, delegate to full review
        return await self.perform_initial_review(event)

    async def integrate_feedback(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Integrate human feedback into learning system.

        Analyzes reviewer comments and decisions to improve future reviews.

        Args:
            event: Event data containing human review feedback

        Returns:
            Dictionary with feedback integration status
        """
        logger.info("Integrating human feedback")  # codeql[py/clear-text-logging-sensitive-data]

        feedback = event.get("feedback", {})
        if isinstance(feedback, str):
            try:
                parsed = json.loads(feedback)
            except json.JSONDecodeError:
                parsed = {"comments": [feedback]}
            if isinstance(parsed, dict):
                feedback = parsed
            elif isinstance(parsed, list):
                feedback = {"comments": parsed}
            elif parsed is None:
                feedback = {}
            else:
                feedback = {"comments": [str(parsed)]}
        elif not isinstance(feedback, dict):
            feedback = {"comments": [feedback] if not isinstance(feedback, list) else feedback}

        comments = feedback.get("comments", [])
        if isinstance(comments, str):
            comments = [comments]
        elif comments is None:
            comments = []

        await self.learning_system.integrate_feedback(feedback)

        return {"status": "feedback_integrated", "feedback_items": len(comments)}

    async def respond_to_mention(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Respond to @codex-reviewer mentions in comments.

        Handles explicit requests for re-review, specific analysis,
        or teaching new patterns.

        Args:
            event: Event data containing mention and context

        Returns:
            Dictionary with response status
        """
        comment = event.get("comment", {})
        if isinstance(comment, str):
            body = comment
        elif isinstance(comment, dict):
            body = comment.get("body", "")
        else:
            body = str(comment)

        logger.info(
            f"Responding to mention: {body[:100]}..."
        )  # codeql[py/clear-text-logging-sensitive-data]

        # Parse mention commands
        if "learn:" in body.lower():
            # Extract learning content
            learning_content = body.split("learn:", 1)[1].strip()
            await self.learning_system.learn_from_user_input(learning_content)
            return {"status": "learned", "content": learning_content}

        if "analyze" in body.lower():
            # Trigger specific analysis
            return await self.perform_initial_review(event)

        # Generic re-review request
        return await self.perform_initial_review(event)

    def _extract_review_context(self, event: dict[str, Any]) -> ReviewContext:
        """
        Extract ReviewContext from event data.

        Args:
            event: Raw event data

        Returns:
            ReviewContext object with extracted information
        """
        # Handle different event formats
        if "context" in event:
            # Pre-formatted context
            return event["context"]

        # Extract from raw GitHub webhook
        pr = event.get("pull_request", {})
        return ReviewContext(
            pr_number=pr.get("number", 0),
            repo=event.get("repository", {}).get("full_name", ""),
            files_changed=event.get("files_changed", []),
            diff=event.get("diff", ""),
            base_branch=pr.get("base", {}).get("ref", "main"),
            head_branch=pr.get("head", {}).get("ref", ""),
            author=pr.get("user", {}).get("login", ""),
            description=pr.get("body", ""),
            head_sha=pr.get("head", {}).get("sha", ""),
            labels=[label.get("name", "") for label in pr.get("labels", [])],
            reviewers=[r.get("login", "") for r in pr.get("requested_reviewers", [])],
        )

    async def _analyze_code_quality(self, context: ReviewContext) -> dict[str, Any]:
        """
        Analyze code quality aspects.

        Examines style, complexity, maintainability, and adherence to best practices.

        Args:
            context: Review context with PR information

        Returns:
            Dictionary with quality analysis results
        """
        logger.debug("Analyzing code quality")  # codeql[py/clear-text-logging-sensitive-data]

        quality_issues = []

        for file_path in context.files_changed:
            if file_path.endswith(".py"):
                # Analyze Python files
                issues = await self._analyze_python_quality(file_path, context.diff)
                quality_issues.extend(issues)
            elif file_path.endswith((".yml", ".yaml")):
                # Analyze YAML files
                issues = await self._analyze_yaml_quality(file_path, context.diff)
                quality_issues.extend(issues)

        return {
            "category": "code_quality",
            "issues": quality_issues,
            "score": self._calculate_quality_score(quality_issues),
            "file_count": len(context.files_changed),
            "substantive": True,
        }

    @staticmethod
    def _added_source_lines(diff: str, file_path: str) -> list[str]:
        """Return added source lines belonging to one file in a unified diff."""
        current_file = ""
        lines: list[str] = []
        for raw_line in diff.splitlines():
            if raw_line.startswith("+++ b/"):
                current_file = raw_line[6:]
                continue
            if raw_line.startswith("+") and not raw_line.startswith("+++"):
                if not file_path or current_file == file_path:
                    lines.append(raw_line[1:])
        return lines

    async def _analyze_python_quality(self, file_path: str, diff: str) -> list[dict[str, Any]]:
        """Run bounded Python style checks on added lines for the changed file."""
        issues: list[dict[str, Any]] = []
        for line_number, line in enumerate(self._added_source_lines(diff, file_path), 1):
            if line.rstrip() != line:
                issues.append(
                    {
                        "category": "code_quality",
                        "type": "trailing_whitespace",
                        "severity": "low",
                        "line": line_number,
                        "file": file_path,
                    }
                )
            if re.match(r"^\s*except\s*:\s*(?:#.*)?$", line):
                issues.append(
                    {
                        "category": "code_quality",
                        "type": "bare_except",
                        "severity": "low",
                        "line": line_number,
                        "file": file_path,
                    }
                )
            if len(line) > 120:
                issues.append(
                    {
                        "category": "code_quality",
                        "type": "long_line",
                        "severity": "low",
                        "line": line_number,
                        "file": file_path,
                    }
                )
        return issues

    async def _analyze_yaml_quality(self, file_path: str, diff: str) -> list[dict[str, Any]]:
        """Run bounded YAML hygiene checks on added lines for the changed file."""
        issues: list[dict[str, Any]] = []
        for line_number, line in enumerate(self._added_source_lines(diff, file_path), 1):
            if "\t" in line:
                issues.append(
                    {
                        "category": "code_quality",
                        "type": "yaml_tab",
                        "severity": "low",
                        "line": line_number,
                        "file": file_path,
                    }
                )
            uses = re.search(r"\buses:\s*([^\s#]+)", line)
            if uses and not uses.group(1).startswith("./") and "@" not in uses.group(1):
                issues.append(
                    {
                        "category": "code_quality",
                        "type": "unpinned_action",
                        "severity": "low",
                        "line": line_number,
                        "file": file_path,
                    }
                )
        return issues

    def _calculate_quality_score(self, issues: list[dict[str, Any]]) -> float:
        """Calculate overall quality score from issues."""
        if not issues:
            return 1.0

        # Weight by severity
        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}
        total_weight = sum(
            severity_weights.get(issue.get("severity", "medium"), 0.3) for issue in issues
        )

        # Normalize to 0-1 range (assuming 10 issues = 0 score)
        return max(0.0, 1.0 - (total_weight / 10.0))

    async def _analyze_security(self, context: ReviewContext) -> dict[str, Any]:
        """Analyze security vulnerabilities."""
        logger.debug("Analyzing security")  # codeql[py/clear-text-logging-sensitive-data]

        vulnerabilities = await self.security_scanner.scan(context)

        return {
            "category": "security",
            "vulnerabilities": vulnerabilities,
            "severity_counts": self._count_by_severity(vulnerabilities),
        }

    async def _analyze_performance(self, context: ReviewContext) -> dict[str, Any]:
        """Detect bounded performance anti-patterns in added Python lines."""
        logger.debug("Analyzing performance")  # codeql[py/clear-text-logging-sensitive-data]
        issues: list[dict[str, Any]] = []
        for file_path in context.files_changed:
            if not file_path.endswith(".py"):
                continue
            lines = self._added_source_lines(context.diff, file_path)
            loop_depth = 0
            for line_number, line in enumerate(lines, 1):
                stripped = line.lstrip()
                indent = len(line) - len(stripped)
                if stripped.startswith("for ") or stripped.startswith("while "):
                    loop_depth += 1
                    if loop_depth > 1 or (
                        indent > 0 and any(marker in line for marker in (".append(", "+="))
                    ):
                        issues.append(
                            {
                                "category": "performance",
                                "type": "nested_or_repeated_work",
                                "severity": "low",
                                "file": file_path,
                                "line": line_number,
                            }
                        )
                elif indent == 0:
                    loop_depth = 0
        return {
            "category": "performance",
            "issues": issues,
            "impact_score": max(0.0, 1.0 - len(issues) * 0.05),
            "substantive": True,
        }

    async def _analyze_documentation(self, context: ReviewContext) -> dict[str, Any]:
        """Detect added production definitions without nearby docstrings."""
        logger.debug("Analyzing documentation")  # codeql[py/clear-text-logging-sensitive-data]
        missing_docs: list[dict[str, Any]] = []
        for file_path in context.files_changed:
            if (
                not file_path.endswith(".py")
                or "/tests/" in f"/{file_path}"
                or file_path.startswith("tests/")
            ):
                continue
            lines = self._added_source_lines(context.diff, file_path)
            for index, line in enumerate(lines):
                match = re.match(r"\s*(?:async\s+def|def|class)\s+(_?[A-Za-z][A-Za-z0-9_]*)", line)
                if not match or match.group(1).startswith("_"):
                    continue
                next_lines = "\n".join(lines[index + 1 : index + 4])
                if '"""' not in next_lines:
                    missing_docs.append(
                        {
                            "category": "documentation",
                            "type": "missing_docstring",
                            "severity": "low",
                            "file": file_path,
                            "line": index + 1,
                        }
                    )
        completeness = 1.0 if not missing_docs else max(0.5, 1.0 - len(missing_docs) * 0.05)
        return {
            "category": "documentation",
            "missing_docs": missing_docs,
            "completeness_score": completeness,
            "substantive": True,
        }

    async def _analyze_quantum_patterns(self, context: ReviewContext) -> dict[str, Any]:
        """Analyze quantum-inspired patterns."""
        logger.debug("Analyzing quantum patterns")  # codeql[py/clear-text-logging-sensitive-data]

        patterns = await self.pattern_analyzer.analyze(context)

        return {
            "category": "quantum_patterns",
            "patterns": patterns,
            "opportunities_count": len(patterns),
        }

    async def _detect_knowledge_gaps(self, context: ReviewContext) -> dict[str, Any]:
        """Detect knowledge gaps."""
        logger.debug("Detecting knowledge gaps")  # codeql[py/clear-text-logging-sensitive-data]

        gaps = await self.knowledge_engine.detect_gaps(context)

        return {"category": "knowledge_gaps", "gaps": gaps, "gap_count": len(gaps)}

    def _aggregate_results(self, results: list[dict[str, Any]]) -> ReviewResult:
        """
        Aggregate analysis results into ReviewResult.

        Args:
            results: List of analysis results from different components

        Returns:
            Aggregated ReviewResult object
        """
        all_suggestions = []
        knowledge_gaps = []
        analysis_summary = {}

        # Extract data from each result
        for result in results:
            category = result.get("category", "unknown")
            analysis_summary[category] = result

            # Collect suggestions
            if "issues" in result:
                all_suggestions.extend(result["issues"])
            if "vulnerabilities" in result:
                all_suggestions.extend(result["vulnerabilities"])
            if "patterns" in result:
                # Convert patterns to suggestions
                for pattern in result["patterns"]:
                    if pattern.get("type") == "superposition_opportunity":
                        all_suggestions.append(
                            {
                                "category": "quantum_patterns",
                                "type": "enhancement",
                                "description": pattern.get("description", ""),
                                "severity": "low",
                            }
                        )

            # Collect knowledge gaps
            if "gaps" in result:
                knowledge_gaps.extend(result["gaps"])

        # Calculate overall confidence
        confidence = self._calculate_confidence(all_suggestions, analysis_summary)

        # Determine status. Low-severity opportunities are included in the
        # review body but do not prevent a substantive clean approval.
        blocking = [
            suggestion
            for suggestion in all_suggestions
            if suggestion.get("severity") in {"medium", "high", "critical"}
        ]
        if confidence > 0.95 and not blocking:
            status = "approved"
        elif any(s.get("severity") == "critical" for s in all_suggestions):
            status = "changes_requested"
        else:
            status = "commented"

        return ReviewResult(
            status=status,
            confidence=confidence,
            suggestions=all_suggestions,
            orchestration_plan={},
            next_steps=[],
            knowledge_gaps=knowledge_gaps,
            analysis_summary=analysis_summary,
        )

    def _calculate_confidence(
        self, suggestions: list[dict[str, Any]], summary: dict[str, Any]
    ) -> float:
        """Calculate overall confidence in review."""
        # Base confidence
        confidence = 0.85

        # Adjust based on knowledge gaps
        gaps = sum(len(s.get("gaps", [])) for s in summary.values())
        confidence -= gaps * 0.05

        # Adjust based on analysis completeness. Low-severity enhancement
        # opportunities and knowledge gaps are advisory, not approval blockers.
        expected_categories = {"code_quality", "security", "performance", "documentation"}
        completed_categories = expected_categories & summary.keys()
        completed = sum(
            1 for category in completed_categories if summary[category].get("substantive", True)
        )
        confidence *= completed / len(expected_categories)
        blocking = [
            suggestion
            for suggestion in suggestions
            if suggestion.get("severity") in {"medium", "high", "critical"}
        ]
        if completed == len(expected_categories) and not blocking:
            confidence = max(confidence, 0.99)

        return max(0.0, min(1.0, confidence))

    def _count_by_severity(self, items: list[dict[str, Any]]) -> dict[str, int]:
        """Count items by severity level."""
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for item in items:
            severity = item.get("severity", "medium")
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _generate_next_steps(self, result: ReviewResult, context: ReviewContext) -> list[str]:
        """Generate actionable next steps."""
        steps = []

        # Add steps based on suggestions
        critical_issues = [s for s in result.suggestions if s.get("severity") == "critical"]
        if critical_issues:
            steps.append(f"Address {len(critical_issues)} critical security issue(s)")

        high_issues = [s for s in result.suggestions if s.get("severity") == "high"]
        if high_issues:
            steps.append(f"Fix {len(high_issues)} high-priority issue(s)")

        # Add documentation steps
        if any(s.get("category") == "documentation" for s in result.suggestions):
            steps.append("Update documentation for new/modified code")

        # Add test steps
        if "test" in context.description.lower() or any("test" in f for f in context.files_changed):
            steps.append("Verify all tests pass")

        return steps

    async def _post_review(self, context: ReviewContext, result: ReviewResult):
        """
        Post review results to PR.

        Formats results as markdown and posts via GitHub API.

        Args:
            context: Review context
            result: Review result to post
        """
        logger.info(
            f"Posting review for PR #{context.pr_number}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        if self.head_verifier is not None and not self.head_verifier(context):
            raise RuntimeError("Pull request head changed during review analysis")

        # Format review comment
        review_body = self._format_review_body(result)

        # Determine review action
        if result.status == "approved":
            action = "APPROVE"
        elif any(s.get("severity") == "critical" for s in result.suggestions):
            action = "REQUEST_CHANGES"
        else:
            action = "COMMENT"

        # Post via GitHub API (delegated to GitHub integration module)
        try:
            await self._github_api_post_review(
                context.repo,
                context.pr_number,
                review_body,
                action,
                result.suggestions,
                context.head_sha,
            )
            logger.info(
                f"Successfully posted {action} review"
            )  # codeql[py/clear-text-logging-sensitive-data]
        except Exception as e:
            logger.error(
                f"Failed to post review: {e}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise RuntimeError(f"Failed to post review for PR #{context.pr_number}: {e}") from e

    def _format_review_body(self, result: ReviewResult) -> str:
        """
        Format review results as markdown.

        Args:
            result: Review result to format

        Returns:
            Markdown-formatted review body
        """
        body = []

        # Header
        body.append("## 🤖 Codex Quantum Review\n")
        body.append(f"**Confidence**: {result.confidence:.1%}")
        body.append(f"**Status**: {result.status}")
        body.append(f"**Review Time**: {result.review_time_seconds:.1f}s\n")

        # Summary
        if result.suggestions:
            body.append("### 📊 Review Summary")
            body.append(f"Found **{len(result.suggestions)}** suggestions across:")

            categories = {}
            for s in result.suggestions:
                cat = s.get("category", "general")
                categories[cat] = categories.get(cat, 0) + 1

            for cat, count in sorted(categories.items()):
                body.append(f"- {cat}: {count} items")
            body.append("")

        # Orchestration Plan
        if result.orchestration_plan and result.orchestration_plan.get("steps"):
            body.append("### 🎯 Orchestration Plan")
            for i, step in enumerate(result.orchestration_plan.get("steps", []), 1):
                body.append(f"{i}. {step.get('description', 'N/A')}")
                if "command" in step:
                    body.append(f"   ```bash\n   {step['command']}\n   ```")

            total_time = result.orchestration_plan.get("estimated_time", 0)
            body.append(f"\n**Estimated time**: {total_time} minutes\n")

        # Next Steps
        if result.next_steps:
            body.append("### 🔄 Next Steps")
            for step in result.next_steps:
                body.append(f"- [ ] {step}")
            body.append("")

        # Knowledge Gaps
        if result.knowledge_gaps:
            body.append("### 🧠 Knowledge Gaps Detected")
            body.append("*I could provide better review with knowledge about:*")
            for gap in result.knowledge_gaps:
                body.append(f"- {gap}")
            body.append(
                "\n**Feed me knowledge**: Reply with `@codex-reviewer learn: <information>`"
            )

        # Footer
        body.append("\n---")
        body.append("*Generated by Codex Quantum Reviewer v1.0.0*")
        body.append("*Self-evolving with each review • Quantum-pattern aware*")

        return "\n".join(body)

    async def _github_api_post_review(
        self,
        repo: str,
        pr_number: int,
        body: str,
        action: str,
        suggestions: list[dict[str, Any]],
        commit_id: str = "",
    ):
        """
        Post review via GitHub API client.

        Uses the integrated GitHubAPIClient to post reviews with proper
        authentication, retry logic, and error handling.

        Args:
            repo: Repository full name (owner/repo)
            pr_number: PR number
            body: Review comment body (markdown)
            action: Review action (APPROVE, REQUEST_CHANGES, COMMENT)
            suggestions: List of inline suggestions (future: inline comments)
        """
        try:
            result = await self.github_client.post_review(
                repo=repo,
                pr_number=pr_number,
                body=body,
                event=action,
                commit_id=commit_id or None,
            )

            logger.info(
                f"Successfully posted {action} review to {repo}#{pr_number}, "
                f"review_id={result.get('id')}"
            )

        except Exception as e:
            logger.error(f"Failed to post review to {repo}#{pr_number}: {e}", exc_info=True)
            raise
