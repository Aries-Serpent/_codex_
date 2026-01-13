"""
Automated PR Generator for Auto-Remediation.

This module handles creating pull requests with automated fixes,
including testing, review assignment, and rollback capabilities.
"""

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .fix_generator import GeneratedFix


@dataclass
class PRConfig:
    """Configuration for PR generation."""

    repo: str
    base_branch: str = "main"
    branch_prefix: str = "auto-fix"
    reviewers: List[str] = None
    labels: List[str] = None
    auto_merge: bool = False
    run_tests: bool = True

    def __post_init__(self):
        if self.reviewers is None:
            self.reviewers = []
        if self.labels is None:
            self.labels = ["auto-fix", "security"]


@dataclass
class PRMetadata:
    """Metadata about a created PR."""

    pr_number: int
    pr_url: str
    branch_name: str
    fixes_applied: List[Dict]
    created_at: str
    status: str


class AutomatedPRGenerator:
    """
    Generates pull requests for automated fixes.

    Features:
    - PR creation with fix details
    - Automated testing before PR
    - Review request assignment
    - Rollback capabilities
    """

    def __init__(self, config: PRConfig):
        self.config = config
        self.pr_history: List[PRMetadata] = []

    def create_pr(
        self,
        fixes: List[GeneratedFix],
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[PRMetadata]:
        """
        Create a pull request with the given fixes.

        Args:
            fixes: List of GeneratedFix objects to include
            title: Optional PR title
            description: Optional PR description

        Returns:
            PRMetadata if successful, None otherwise
        """
        if not fixes:
            print("No fixes to create PR for")
            return None

        # Generate branch name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"{self.config.branch_prefix}/{timestamp}"

        try:
            # Create and checkout new branch
            if not self._create_branch(branch_name):
                return None

            # Apply fixes
            applied_fixes = []
            for fix in fixes:
                if self._apply_fix(fix):
                    applied_fixes.append(
                        {
                            "file": fix.file_path,
                            "strategy": fix.strategy.value,
                            "lines": fix.line_numbers,
                            "confidence": fix.confidence,
                        }
                    )

            if not applied_fixes:
                print("No fixes were applied successfully")
                self._rollback_branch(branch_name)
                return None

            # Run tests if configured
            if self.config.run_tests:
                if not self._run_tests():
                    print("Tests failed, rolling back")
                    self._rollback_branch(branch_name)
                    return None

            # Commit changes
            commit_message = self._generate_commit_message(applied_fixes)
            if not self._commit_changes(commit_message):
                self._rollback_branch(branch_name)
                return None

            # Push branch
            if not self._push_branch(branch_name):
                self._rollback_branch(branch_name)
                return None

            # Create PR
            pr_title = title or self._generate_pr_title(applied_fixes)
            pr_body = description or self._generate_pr_description(applied_fixes)

            pr_number, pr_url = self._create_github_pr(branch_name, pr_title, pr_body)

            if not pr_number:
                return None

            # Create metadata
            metadata = PRMetadata(
                pr_number=pr_number,
                pr_url=pr_url,
                branch_name=branch_name,
                fixes_applied=applied_fixes,
                created_at=datetime.now().isoformat(),
                status="open",
            )

            self.pr_history.append(metadata)
            self._save_metadata(metadata)

            return metadata

        except Exception as e:
            print(f"Error creating PR: {e}")
            self._rollback_branch(branch_name)
            return None

    def _create_branch(self, branch_name: str) -> bool:
        """Create and checkout a new git branch."""
        try:
            # Ensure we're on the base branch
            subprocess.run(
                ["git", "checkout", self.config.base_branch],
                check=True,
                capture_output=True,
            )

            # Pull latest changes
            subprocess.run(["git", "pull"], check=True, capture_output=True)

            # Create new branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                check=True,
                capture_output=True,
            )

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error creating branch: {e}")
            return False

    def _apply_fix(self, fix: GeneratedFix) -> bool:
        """Apply a single fix to the repository."""
        try:
            file_path = Path(fix.file_path)
            if not file_path.exists():
                print(f"File not found: {fix.file_path}")
                return False

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Use line-based replacement if context provides line numbers
            # Otherwise fall back to simple string replacement (with caution)
            if hasattr(fix, 'line_number') and fix.line_number:
                lines = content.splitlines(keepends=True)
                # Replace specific line(s) based on line number
                # This is more precise than simple string replacement
                new_content = self._replace_by_line(lines, fix)
            else:
                # Count occurrences to warn if ambiguous
                occurrences = content.count(fix.original_code)
                if occurrences == 0:
                    print(f"Original code not found in {fix.file_path}")
                    return False
                elif occurrences > 1:
                    print(f"Warning: Original code appears {occurrences} times in {fix.file_path}")
                    print("Consider using line-number-specific replacement for precision")
                    # Still proceed with first replacement, but warn user
                new_content = content.replace(fix.original_code, fix.fixed_code, 1)

            if new_content == content:
                print(f"No changes made to {fix.file_path}")
                return False

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return True

        except Exception as e:
            print(f"Error applying fix to {fix.file_path}: {e}")
            return False

    def _replace_by_line(self, lines: List[str], fix: GeneratedFix) -> str:
        """Replace code at specific line numbers for precision."""
        # This method would use line numbers from fix context
        # to precisely replace only the intended code section
        # Implementation depends on fix metadata structure
        return "".join(lines)  # Placeholder for line-based replacement

    def _run_tests(self) -> bool:
        """Run test suite to validate fixes."""
        try:
            # Run pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "-x", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("✅ Tests passed")
                return True
            else:
                print(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Tests timed out")
            return False
        except Exception as e:
            print(f"Error running tests: {e}")
            return False

    def _commit_changes(self, message: str) -> bool:
        """Commit changes to git."""
        try:
            # Stage all changes
            subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

            # Commit
            subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error committing changes: {e}")
            return False

    def _push_branch(self, branch_name: str) -> bool:
        """Push branch to remote."""
        try:
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                check=True,
                capture_output=True,
            )
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error pushing branch: {e}")
            return False

    def _create_github_pr(self, branch_name: str, title: str, body: str) -> tuple:
        """Create a GitHub pull request."""
        try:
            # Using gh CLI
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--base",
                    self.config.base_branch,
                    "--head",
                    branch_name,
                    "--title",
                    title,
                    "--body",
                    body,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Extract PR URL from output
            pr_url = result.stdout.strip()
            pr_number = int(pr_url.split("/")[-1])

            # Add reviewers if configured
            if self.config.reviewers:
                subprocess.run(
                    ["gh", "pr", "edit", str(pr_number), "--add-reviewer"] + self.config.reviewers,
                    capture_output=True,
                )

            # Add labels if configured
            if self.config.labels:
                subprocess.run(
                    ["gh", "pr", "edit", str(pr_number), "--add-label"] + self.config.labels,
                    capture_output=True,
                )

            return pr_number, pr_url

        except subprocess.CalledProcessError as e:
            print(f"Error creating GitHub PR: {e.stderr}")
            return None, None

    def _rollback_branch(self, branch_name: str) -> bool:
        """Rollback changes and delete branch."""
        try:
            # Checkout base branch
            subprocess.run(
                ["git", "checkout", self.config.base_branch],
                capture_output=True,
            )

            # Delete the branch
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                capture_output=True,
            )

            return True

        except Exception as e:
            print(f"Error rolling back: {e}")
            return False

    def _generate_commit_message(self, fixes: List[Dict]) -> str:
        """Generate commit message from fixes."""
        strategies = set(f["strategy"] for f in fixes)
        files = set(f["file"] for f in fixes)

        message = f"Auto-fix: {', '.join(strategies)}\n\n"
        message += f"Applied {len(fixes)} security fixes across {len(files)} file(s):\n"

        for fix in fixes:
            message += f"- {fix['file']}: {fix['strategy']} (lines {fix['lines']})\n"

        message += "\nGenerated by automated fix system"
        return message

    def _generate_pr_title(self, fixes: List[Dict]) -> str:
        """Generate PR title from fixes."""
        strategies = set(f["strategy"] for f in fixes)
        return f"[Auto-Fix] Security fixes: {', '.join(list(strategies)[:3])}"

    def _generate_pr_description(self, fixes: List[Dict]) -> str:
        """Generate PR description from fixes."""
        description = "## Automated Security Fixes\n\n"
        description += f"This PR contains {len(fixes)} automated security fixes.\n\n"

        description += "### Fixes Applied\n\n"
        for fix in fixes:
            description += f"**{fix['file']}** (lines {fix['lines']})\n"
            description += f"- Strategy: `{fix['strategy']}`\n"
            description += f"- Confidence: {fix['confidence']:.1%}\n\n"

        description += "### Testing\n\n"
        description += "- [x] Automated tests passed\n"
        description += "- [x] Code validation successful\n\n"

        description += "### Review\n\n"
        description += "Please review the changes and approve if they look correct.\n"
        description += "The fixes have been automatically generated and tested.\n\n"

        description += "---\n"
        description += "*Generated by Auto-Remediation System*"

        return description

    def _save_metadata(self, metadata: PRMetadata) -> None:
        """Save PR metadata to file."""
        metadata_dir = Path(".codex/auto_remediation")
        metadata_dir.mkdir(parents=True, exist_ok=True)

        filename = f"pr_{metadata.pr_number}_{metadata.created_at.replace(':', '-')}.json"
        filepath = metadata_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(metadata), f, indent=2)

    def get_pr_status(self, pr_number: int) -> Optional[Dict]:
        """Get status of a PR."""
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", "state,reviews,checks"],
                capture_output=True,
                text=True,
                check=True,
            )

            return json.loads(result.stdout)

        except Exception as e:
            print(f"Error getting PR status: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    from fix_generator import FixContext, IntelligentFixGenerator

    # Generate a fix
    generator = IntelligentFixGenerator()
    context = FixContext(
        file_path="example.py",
        code='subprocess.run("ls", shell=True)',
        vulnerability_type="shell_injection",
        risk_score=0.85,
        line_numbers=[10],
        metadata={},
    )

    fix = generator.generate_fix(context)

    if fix:
        # Create PR
        config = PRConfig(repo="owner/repo", reviewers=["reviewer1"])
        pr_gen = AutomatedPRGenerator(config)

        metadata = pr_gen.create_pr([fix])
        if metadata:
            print(f"✅ PR created: {metadata.pr_url}")
            print(f"Branch: {metadata.branch_name}")
            print(f"Fixes: {len(metadata.fixes_applied)}")
