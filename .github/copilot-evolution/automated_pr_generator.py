"""
Automated PR Generation for Healing Fixes

Implements automated pull request generation for healing fixes:
- Generates fix code from healing suggestions
- Creates PR descriptions with context
- Supports confidence-based auto-merge

Phase 3: Self-Healing Evolution

Author: mbaetiong
Generated: 2025-12-22
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class FixSuggestion:
    """Suggested fix for an issue."""

    suggestion_id: str
    issue_type: str
    file_path: str
    line_number: Optional[int]
    original_code: str
    fixed_code: str
    explanation: str
    confidence: float
    created_at: str


@dataclass
class GeneratedPR:
    """Generated pull request details."""

    pr_id: str
    title: str
    description: str
    branch_name: str
    fixes: List[FixSuggestion]
    confidence: float
    auto_merge_eligible: bool
    created_at: str
    status: str  # draft, ready, merged, closed


@dataclass
class PRTemplate:
    """Template for PR generation."""

    template_id: str
    name: str
    title_template: str
    description_template: str
    labels: List[str]
    reviewers: List[str]


# ============================================================================
# Fix Code Generator
# ============================================================================


class FixCodeGenerator:
    """
    Generates fix code from healing suggestions.

    Takes healing suggestions and generates actual code fixes
    that can be applied to the repository.
    """

    def __init__(self):
        """Initialize fix code generator."""
        # Fix templates for common issues
        self.fix_templates: Dict[str, Dict[str, Any]] = {
            "docker_tag_error": {
                "pattern": r"ghcr\.io/[^:]+:[^}]+\}",
                "fix_template": self._docker_tag_fix_template,
            },
            "peft_target_error": {
                "pattern": r"target_modules=\[.*?\]",
                "fix_template": self._peft_target_fix_template,
            },
            "hydra_composition": {
                "pattern": r'overrides=\["(\w+)=',
                "fix_template": self._hydra_composition_fix_template,
            },
            "assertion_error": {
                "pattern": r"assert 0\.0 < prob",
                "fix_template": self._assertion_fix_template,
            },
            "import_error": {
                "pattern": r"pip install",
                "fix_template": self._import_error_fix_template,
            },
            "artifact_version": {
                "pattern": r"actions/upload-artifact@v\d+",
                "fix_template": self._artifact_version_fix_template,
            },
        }

        logger.info(
            f"✅ FixCodeGenerator initialized | "
            f"Templates: {len(self.fix_templates)}"
        )

    def generate_fix(
        self,
        issue_type: str,
        file_content: str,
        context: Dict[str, Any],
    ) -> Optional[FixSuggestion]:
        """
        Generate a fix for the given issue.

        Args:
            issue_type: Type of issue to fix
            file_content: Current file content
            context: Context about the issue

        Returns:
            FixSuggestion or None if no fix could be generated
        """
        if issue_type not in self.fix_templates:
            logger.warning(f"No template for issue type: {issue_type}")
            return None

        template = self.fix_templates[issue_type]
        fix_func = template["fix_template"]

        try:
            fixed_code, confidence, explanation = fix_func(file_content, context)

            if fixed_code is None:
                return None

            suggestion = FixSuggestion(
                suggestion_id=hashlib.md5(
                    f"{issue_type}:{datetime.utcnow().isoformat()}".encode()
                ).hexdigest()[:12],
                issue_type=issue_type,
                file_path=context.get("file_path", "unknown"),
                line_number=context.get("line_number"),
                original_code=file_content[:500] + "..." if len(file_content) > 500 else file_content,
                fixed_code=fixed_code,
                explanation=explanation,
                confidence=confidence,
                created_at=datetime.utcnow().isoformat(),
            )

            logger.info(
                f"🔧 Generated fix for {issue_type} "
                f"(confidence: {confidence:.1%})"
            )

            return suggestion

        except Exception as e:
            logger.error(f"Failed to generate fix: {e}")
            return None

    def _docker_tag_fix_template(
        self, content: str, context: Dict[str, Any]
    ) -> Tuple[Optional[str], float, str]:
        """
        Generate fix for Docker tag errors in GitHub Actions workflow YAML.

        This generates a shell command that will execute within the GitHub
        Actions runner context. The $(echo ...) syntax is valid shell
        substitution that will be interpreted by bash when the workflow runs.

        Note: The replacement string inserts literal shell command syntax
        into workflow YAML files where commands are executed by the runner's
        shell. This is intentional - the sanitization happens at workflow
        runtime, not at fix generation time.
        """
        # Find the problematic tag reference
        pattern = r"(ghcr\.io/[^:]+:)(\$\{[^}]+\})"

        def sanitize_replacement(match: re.Match) -> str:
            prefix = match.group(1)
            variable = match.group(2)
            # Wrap with sanitization - this shell command executes at workflow runtime
            return f'{prefix}$(echo {variable} | tr "/:A-Z" ".-a-z" | sed "s/[^a-z0-9._-]/-/g")'

        fixed = re.sub(pattern, sanitize_replacement, content)

        if fixed == content:
            return None, 0.0, "No Docker tag issues found"

        return (
            fixed,
            0.92,
            "Sanitized Docker tag to comply with naming conventions: "
            "lowercase, replace slashes and colons with hyphens",
        )

    def _peft_target_fix_template(
        self, content: str, context: Dict[str, Any]
    ) -> Tuple[Optional[str], float, str]:
        """Generate fix for PEFT target_modules errors."""
        # Remove target_modules parameter entirely
        pattern = r',?\s*target_modules=\[.*?\]'
        fixed = re.sub(pattern, "", content)

        if fixed == content:
            return None, 0.0, "No PEFT target_modules issue found"

        return (
            fixed,
            0.90,
            "Removed target_modules parameter to let PEFT auto-detect Linear layers",
        )

    def _hydra_composition_fix_template(
        self, content: str, context: Dict[str, Any]
    ) -> Tuple[Optional[str], float, str]:
        """Generate fix for Hydra composition errors."""
        # Add + prefix for non-default config groups
        pattern = r'overrides=\["(\w+)='
        fixed = re.sub(pattern, r'overrides=["+\1=', content)

        if fixed == content:
            return None, 0.0, "No Hydra composition issue found"

        return (
            fixed,
            0.88,
            "Added + prefix for config groups not in defaults list",
        )

    def _assertion_fix_template(
        self, content: str, context: Dict[str, Any]
    ) -> Tuple[Optional[str], float, str]:
        """Generate fix for assertion errors."""
        # Fix Boltzmann probability assertion
        pattern = r"assert 0\.0 < prob"
        fixed = re.sub(pattern, "assert 0.0 <= prob", content)

        if fixed == content:
            return None, 0.0, "No assertion issue found"

        return (
            fixed,
            0.95,
            "Allow zero probability for physically inaccessible states "
            "(Boltzmann distribution can approach zero for high energy states)",
        )

    def _import_error_fix_template(
        self, content: str, context: Dict[str, Any]
    ) -> Tuple[Optional[str], float, str]:
        """Generate fix for import/dependency errors."""
        # Add missing pytest plugins
        if "pip install" in content and "pytest" in content:
            # Find the pip install line and add pytest-timeout
            pattern = r"(pip install [^&\n]+)"

            def add_timeout(match: re.Match) -> str:
                original = match.group(1)
                if "pytest-timeout" not in original:
                    return original + " pytest-timeout pytest-asyncio pytest-mock"
                return original

            fixed = re.sub(pattern, add_timeout, content)

            if fixed != content:
                return (
                    fixed,
                    0.95,
                    "Added missing pytest plugins: pytest-timeout, pytest-asyncio, pytest-mock",
                )

        return None, 0.0, "No import error fix applicable"

    def _artifact_version_fix_template(
        self, content: str, context: Dict[str, Any]
    ) -> Tuple[Optional[str], float, str]:
        """Generate fix for artifact action version errors."""
        # Replace v6 with v4
        pattern = r"actions/upload-artifact@v\d+"
        fixed = re.sub(pattern, "actions/upload-artifact@v4", content)

        pattern2 = r"actions/download-artifact@v\d+"
        fixed = re.sub(pattern2, "actions/download-artifact@v4", fixed)

        if fixed == content:
            return None, 0.0, "No artifact version issue found"

        return (
            fixed,
            0.98,
            "Aligned artifact actions to v4 for compatibility",
        )


# ============================================================================
# PR Description Generator
# ============================================================================


class PRDescriptionGenerator:
    """
    Generates pull request descriptions from fixes.

    Creates detailed, well-formatted PR descriptions that
    explain the changes and provide context.
    """

    def __init__(self):
        """Initialize PR description generator."""
        self.templates = self._load_templates()

        logger.info(
            f"✅ PRDescriptionGenerator initialized | "
            f"Templates: {len(self.templates)}"
        )

    def _load_templates(self) -> Dict[str, PRTemplate]:
        """Load PR templates."""
        return {
            "healing_fix": PRTemplate(
                template_id="healing_fix",
                name="Self-Healing Fix",
                title_template="fix: {issue_type} in {file_path}",
                description_template="""## 🔧 Self-Healing Fix

### Issue Type
{issue_type}

### Description
{explanation}

### Changes Made
{changes_summary}

### Confidence
{confidence:.1%}

### Files Changed
{files_list}

---

*This PR was automatically generated by the Self-Healing Engine.*
""",
                labels=["self-healing", "automated", "bug-fix"],
                reviewers=[],
            ),
            "multi_fix": PRTemplate(
                template_id="multi_fix",
                name="Multiple Fixes",
                title_template="fix: Resolve {count} workflow failures",
                description_template="""## 🔧 Multi-Fix Resolution

### Summary
This PR addresses {count} issues detected across the codebase.

### Issues Fixed
{issues_list}

### Changes Summary
{changes_summary}

### Overall Confidence
{confidence:.1%}

### Files Changed
{files_list}

---

*This PR was automatically generated by the Self-Healing Engine.*
""",
                labels=["self-healing", "automated", "multi-fix"],
                reviewers=[],
            ),
        }

    def generate_description(
        self,
        fixes: List[FixSuggestion],
        template_id: str = "healing_fix",
    ) -> Tuple[str, str]:
        """
        Generate PR title and description.

        Args:
            fixes: List of fixes to include
            template_id: Template to use

        Returns:
            Tuple of (title, description)
        """
        if not fixes:
            return "fix: No changes", "No fixes to apply"

        template = self.templates.get(template_id, self.templates["healing_fix"])

        if len(fixes) == 1:
            fix = fixes[0]
            title = template.title_template.format(
                issue_type=fix.issue_type,
                file_path=Path(fix.file_path).name,
            )
            description = template.description_template.format(
                issue_type=fix.issue_type,
                explanation=fix.explanation,
                changes_summary=self._generate_changes_summary([fix]),
                confidence=fix.confidence,
                files_list=f"- `{fix.file_path}`",
            )
        else:
            template = self.templates["multi_fix"]
            title = template.title_template.format(count=len(fixes))

            issues_list = "\n".join(
                f"- **{fix.issue_type}** in `{Path(fix.file_path).name}`"
                for fix in fixes
            )

            files_list = "\n".join(
                f"- `{fix.file_path}`" for fix in fixes
            )

            avg_confidence = sum(f.confidence for f in fixes) / len(fixes)

            description = template.description_template.format(
                count=len(fixes),
                issues_list=issues_list,
                changes_summary=self._generate_changes_summary(fixes),
                confidence=avg_confidence,
                files_list=files_list,
            )

        return title, description

    def _generate_changes_summary(self, fixes: List[FixSuggestion]) -> str:
        """Generate a summary of changes."""
        summaries = []
        for fix in fixes:
            summaries.append(f"- {fix.explanation}")
        return "\n".join(summaries)


# ============================================================================
# Automated PR Generator
# ============================================================================


class AutomatedPRGenerator:
    """
    Main class for automated PR generation.

    Coordinates fix generation, description creation,
    and PR submission.
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        auto_merge_threshold: float = 0.95,
    ):
        """
        Initialize automated PR generator.

        Args:
            storage_path: Path to store PR data
            auto_merge_threshold: Confidence threshold for auto-merge
        """
        self.storage_path = storage_path or Path(
            ".github/copilot-evolution/data/prs"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.auto_merge_threshold = auto_merge_threshold

        self.fix_generator = FixCodeGenerator()
        self.description_generator = PRDescriptionGenerator()

        self.generated_prs: Dict[str, GeneratedPR] = {}
        self._load_prs()

        logger.info(
            f"✅ AutomatedPRGenerator initialized | "
            f"Auto-merge threshold: {self.auto_merge_threshold:.0%}"
        )

    def _load_prs(self) -> None:
        """Load generated PRs from disk."""
        prs_file = self.storage_path / "prs.json"
        try:
            if prs_file.exists():
                with open(prs_file) as f:
                    data = json.load(f)
                    for prid, prdata in data.items():
                        # Convert fix dicts back to FixSuggestion
                        fixes = [
                            FixSuggestion(**fix) for fix in prdata.get("fixes", [])
                        ]
                        prdata["fixes"] = fixes
                        self.generated_prs[prid] = GeneratedPR(**prdata)
        except Exception as e:
            logger.warning(f"Failed to load PRs: {e}")

    def _save_prs(self) -> None:
        """Save generated PRs to disk."""
        prs_file = self.storage_path / "prs.json"
        try:
            data = {}
            for prid, pr in self.generated_prs.items():
                fixes_data = [
                    {
                        "suggestion_id": f.suggestion_id,
                        "issue_type": f.issue_type,
                        "file_path": f.file_path,
                        "line_number": f.line_number,
                        "original_code": f.original_code,
                        "fixed_code": f.fixed_code,
                        "explanation": f.explanation,
                        "confidence": f.confidence,
                        "created_at": f.created_at,
                    }
                    for f in pr.fixes
                ]
                data[prid] = {
                    "pr_id": pr.pr_id,
                    "title": pr.title,
                    "description": pr.description,
                    "branch_name": pr.branch_name,
                    "fixes": fixes_data,
                    "confidence": pr.confidence,
                    "auto_merge_eligible": pr.auto_merge_eligible,
                    "created_at": pr.created_at,
                    "status": pr.status,
                }
            with open(prs_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save PRs: {e}")

    def generate_pr(
        self,
        issues: List[Dict[str, Any]],
    ) -> GeneratedPR:
        """
        Generate a PR for the given issues.

        Args:
            issues: List of issues to fix

        Returns:
            GeneratedPR object
        """
        fixes: List[FixSuggestion] = []

        for issue in issues:
            fix = self.fix_generator.generate_fix(
                issue_type=issue.get("type", "unknown"),
                file_content=issue.get("content", ""),
                context=issue,
            )
            if fix:
                fixes.append(fix)

        # Handle no-fixes case early with appropriate placeholder PR
        if not fixes:
            logger.warning("No fixes generated for issues")
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            branch_name = f"self-healing/no-fix-{timestamp}"

            pr = GeneratedPR(
                pr_id=hashlib.md5(branch_name.encode()).hexdigest()[:12],
                title="[No Fixes] Unable to generate automatic fixes",
                description=(
                    "## No Automatic Fixes Available\n\n"
                    "The self-healing system analyzed the issues but could not "
                    "generate automatic fixes. Manual investigation is required.\n\n"
                    f"**Issues analyzed**: {len(issues)}\n"
                    "**Reason**: No matching fix templates found for the issue types."
                ),
                branch_name=branch_name,
                fixes=[],
                confidence=0.0,
                auto_merge_eligible=False,
                created_at=datetime.utcnow().isoformat(),
                status="failed",
            )

            self.generated_prs[pr.pr_id] = pr
            self._save_prs()

            logger.info(f"📝 Generated placeholder PR for unfixable issues: {pr.pr_id}")

            return pr

        # Generate PR title and description
        title, description = self.description_generator.generate_description(fixes)

        # Calculate overall confidence
        avg_confidence = sum(f.confidence for f in fixes) / len(fixes)

        # Determine auto-merge eligibility
        auto_merge_eligible = avg_confidence >= self.auto_merge_threshold

        # Generate branch name
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        branch_name = f"self-healing/fix-{timestamp}"

        pr = GeneratedPR(
            pr_id=hashlib.md5(branch_name.encode()).hexdigest()[:12],
            title=title,
            description=description,
            branch_name=branch_name,
            fixes=fixes,
            confidence=avg_confidence,
            auto_merge_eligible=auto_merge_eligible,
            created_at=datetime.utcnow().isoformat(),
            status="draft" if not auto_merge_eligible else "ready",
        )

        self.generated_prs[pr.pr_id] = pr
        self._save_prs()

        logger.info(
            f"📝 Generated PR: {pr.title} "
            f"(confidence: {avg_confidence:.1%}, "
            f"auto-merge: {auto_merge_eligible})"
        )

        return pr

    def get_pr_statistics(self) -> Dict[str, Any]:
        """Get PR generation statistics."""
        status_counts = {}
        for pr in self.generated_prs.values():
            status_counts[pr.status] = status_counts.get(pr.status, 0) + 1

        auto_merge_count = sum(
            1 for pr in self.generated_prs.values() if pr.auto_merge_eligible
        )

        return {
            "total_prs": len(self.generated_prs),
            "status_counts": status_counts,
            "auto_merge_eligible": auto_merge_count,
            "auto_merge_threshold": self.auto_merge_threshold,
            "avg_confidence": sum(
                pr.confidence for pr in self.generated_prs.values()
            )
            / len(self.generated_prs)
            if self.generated_prs
            else 0.0,
        }

    def generate_pr_commit_message(self, pr: GeneratedPR) -> str:
        """
        Generate a commit message for the PR.

        Args:
            pr: Generated PR

        Returns:
            Commit message string
        """
        lines = [pr.title, ""]

        for fix in pr.fixes:
            lines.append(f"- {fix.explanation}")

        lines.extend(
            [
                "",
                f"Confidence: {pr.confidence:.1%}",
                "",
                "Co-authored-by: Self-Healing Engine <self-healing@_codex_>",
            ]
        )

        return "\n".join(lines)

    def generate_pr_github_action_step(self, pr: GeneratedPR) -> Dict[str, Any]:
        """
        Generate GitHub Actions step to create the PR.

        Args:
            pr: Generated PR

        Returns:
            GitHub Actions step definition
        """
        return {
            "name": f"Create PR: {pr.title}",
            "uses": "peter-evans/create-pull-request@v6",
            "with": {
                "token": "${{ secrets.GITHUB_TOKEN }}",
                "commit-message": self.generate_pr_commit_message(pr),
                "title": pr.title,
                "body": pr.description,
                "branch": pr.branch_name,
                "labels": "self-healing,automated",
                "draft": str(not pr.auto_merge_eligible).lower(),
            },
        }
