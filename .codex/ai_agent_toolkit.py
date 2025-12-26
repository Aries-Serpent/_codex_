#!/usr/bin/env python3
"""
AI Agent Toolkit - Reusable Components for Future Agent Iterations

This module provides utility functions and components that AI agents can use
to avoid repetitive tasks and leverage lessons learned from previous iterations.

Author: AI Agent Collective
Created: 2025-12-26
Purpose: Enhance future agent capabilities and reduce redundant work
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import os


class EnvironmentValidator:
    """Validates execution environment and available tools."""
    
    @staticmethod
    def check_git_access() -> Dict[str, Any]:
        """
        Check git access and authentication status.
        
        Returns:
            Dict with status, credentials, and access details
        """
        result = {
            "git_available": False,
            "credentials_configured": False,
            "remote_access": False,
            "branches": [],
            "current_branch": None,
            "error": None
        }
        
        try:
            # Check git availability
            subprocess.run(["git", "--version"], 
                         capture_output=True, check=True)
            result["git_available"] = True
            
            # Check credential helper
            cred_result = subprocess.run(
                ["git", "config", "credential.helper"],
                capture_output=True, text=True
            )
            if cred_result.stdout.strip():
                result["credentials_configured"] = True
            
            # Check current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True
            )
            result["current_branch"] = branch_result.stdout.strip()
            
            # Check remote access
            remote_result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin"],
                capture_output=True, text=True, timeout=10
            )
            if remote_result.returncode == 0:
                result["remote_access"] = True
                branches = [
                    line.split('\t')[1].replace('refs/heads/', '')
                    for line in remote_result.stdout.strip().split('\n')
                    if line
                ]
                result["branches"] = branches
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def check_github_api_access() -> Dict[str, Any]:
        """
        Check GitHub API access via gh CLI or tokens.
        
        Returns:
            Dict with API access status and available methods
        """
        result = {
            "gh_cli_available": False,
            "gh_authenticated": False,
            "github_token_set": False,
            "gh_token_set": False,
            "actions_context": False,
            "workarounds": [],
            "error": None
        }
        
        try:
            # Check gh CLI
            gh_result = subprocess.run(
                ["gh", "--version"],
                capture_output=True, text=True
            )
            if gh_result.returncode == 0:
                result["gh_cli_available"] = True
                
                # Check authentication
                auth_result = subprocess.run(
                    ["gh", "auth", "status"],
                    capture_output=True, text=True
                )
                result["gh_authenticated"] = auth_result.returncode == 0
            
            # Check environment tokens
            result["github_token_set"] = bool(os.getenv("GITHUB_TOKEN"))
            result["gh_token_set"] = bool(os.getenv("GH_TOKEN"))
            
            # Check GitHub Actions context
            result["actions_context"] = bool(os.getenv("GITHUB_ACTIONS"))
            
            # Determine workarounds
            if not result["gh_authenticated"]:
                result["workarounds"].append("Use git commands instead of gh CLI")
            if result["actions_context"]:
                result["workarounds"].append("Use GitHub Actions context variables")
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def check_python_packages(packages: List[str]) -> Dict[str, Any]:
        """
        Check if Python packages are installed.
        
        Args:
            packages: List of package names to check
            
        Returns:
            Dict with installation status for each package
        """
        result = {
            "installed": [],
            "missing": [],
            "versions": {}
        }
        
        for package in packages:
            try:
                # Try importing the package
                __import__(package)
                result["installed"].append(package)
                
                # Try to get version
                try:
                    mod = sys.modules[package]
                    if hasattr(mod, "__version__"):
                        result["versions"][package] = mod.__version__
                except:
                    pass
                    
            except ImportError:
                result["missing"].append(package)
        
        return result


class TestRunner:
    """Utilities for running tests and collecting results."""
    
    @staticmethod
    def run_pytest_suite(
        test_path: str,
        markers: Optional[str] = None,
        verbose: bool = True,
        max_failures: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run pytest test suite and return structured results.
        
        Args:
            test_path: Path to test file or directory
            markers: Pytest marker expression (e.g., "not slow")
            verbose: Enable verbose output
            max_failures: Maximum failures before stopping
            
        Returns:
            Dict with test results, counts, and status
        """
        cmd = ["python", "-m", "pytest", test_path]
        
        if verbose:
            cmd.append("-v")
        
        if markers:
            cmd.extend(["-k", markers])
        
        if max_failures:
            cmd.extend(["--maxfail", str(max_failures)])
        
        cmd.extend(["--tb=short", "--color=yes"])
        
        result = {
            "command": " ".join(cmd),
            "success": False,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "output": "",
            "error": None
        }
        
        try:
            proc_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            result["output"] = proc_result.stdout + proc_result.stderr
            result["success"] = proc_result.returncode == 0
            
            # Parse output for counts
            for line in result["output"].split('\n'):
                if " passed" in line:
                    # Extract numbers from pytest summary
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            result["passed"] = int(parts[i-1])
                        elif part == "failed":
                            result["failed"] = int(parts[i-1])
                        elif part == "skipped":
                            result["skipped"] = int(parts[i-1])
                        elif part == "error" or part == "errors":
                            result["errors"] = int(parts[i-1])
            
        except subprocess.TimeoutExpired:
            result["error"] = "Test execution timed out after 300s"
        except Exception as e:
            result["error"] = str(e)
        
        return result


class DocumentationBuilder:
    """Utilities for building documentation and reports."""
    
    @staticmethod
    def create_status_report(
        title: str,
        sections: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Create a structured status report in markdown.
        
        Args:
            title: Report title
            sections: Dict of section name to content
            output_path: Optional path to write report
            
        Returns:
            Markdown content as string
        """
        lines = [
            f"# {title}",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "---",
            ""
        ]
        
        for section_name, content in sections.items():
            lines.append(f"## {section_name}")
            lines.append("")
            
            if isinstance(content, dict):
                lines.append("```json")
                lines.append(json.dumps(content, indent=2))
                lines.append("```")
            elif isinstance(content, list):
                for item in content:
                    lines.append(f"- {item}")
            else:
                lines.append(str(content))
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        markdown = "\n".join(lines)
        
        if output_path:
            Path(output_path).write_text(markdown)
        
        return markdown
    
    @staticmethod
    def create_task_checklist(
        tasks: List[Dict[str, Any]],
        title: str = "Task Checklist"
    ) -> str:
        """
        Create a task checklist in markdown format.
        
        Args:
            tasks: List of task dicts with 'name', 'status', 'details'
            title: Checklist title
            
        Returns:
            Markdown checklist
        """
        lines = [f"## {title}", ""]
        
        for task in tasks:
            name = task.get("name", "Unnamed task")
            status = task.get("status", "pending")
            details = task.get("details", "")
            
            checkbox = "[x]" if status == "complete" else "[ ]"
            status_emoji = "✅" if status == "complete" else "⏳"
            
            lines.append(f"- {checkbox} **{name}** {status_emoji}")
            if details:
                lines.append(f"  - {details}")
        
        return "\n".join(lines)


class LessonsLearned:
    """Store and retrieve lessons learned for future agents."""
    
    def __init__(self, storage_path: str = ".codex/lessons_learned.json"):
        self.storage_path = Path(storage_path)
        self.lessons = self._load()
    
    def _load(self) -> List[Dict[str, Any]]:
        """Load existing lessons from storage."""
        if self.storage_path.exists():
            try:
                return json.loads(self.storage_path.read_text())
            except:
                return []
        return []
    
    def _save(self):
        """Save lessons to storage."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self.lessons, indent=2))
    
    def add_lesson(
        self,
        category: str,
        title: str,
        description: str,
        solution: str,
        tags: Optional[List[str]] = None
    ):
        """
        Add a new lesson learned.
        
        Args:
            category: Category (e.g., "testing", "dependencies", "ci-cd")
            title: Brief lesson title
            description: What was learned
            solution: How it was solved
            tags: Optional tags for filtering
        """
        lesson = {
            "id": len(self.lessons) + 1,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "title": title,
            "description": description,
            "solution": solution,
            "tags": tags or []
        }
        
        self.lessons.append(lesson)
        self._save()
    
    def search(self, category: Optional[str] = None, tag: Optional[str] = None) -> List[Dict]:
        """Search lessons by category or tag."""
        results = self.lessons
        
        if category:
            results = [l for l in results if l["category"] == category]
        
        if tag:
            results = [l for l in results if tag in l["tags"]]
        
        return results
    
    def export_markdown(self) -> str:
        """Export all lessons as markdown."""
        lines = [
            "# Lessons Learned - AI Agent Knowledge Base",
            "",
            f"**Total Lessons:** {len(self.lessons)}",
            f"**Last Updated:** {datetime.now().isoformat()}",
            "",
            "---",
            ""
        ]
        
        # Group by category
        categories = {}
        for lesson in self.lessons:
            cat = lesson["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(lesson)
        
        for category, lessons in sorted(categories.items()):
            lines.append(f"## {category.title()}")
            lines.append("")
            
            for lesson in lessons:
                lines.append(f"### {lesson['title']}")
                lines.append(f"*Added: {lesson['timestamp']}*")
                lines.append("")
                lines.append("**Problem:**")
                lines.append(lesson['description'])
                lines.append("")
                lines.append("**Solution:**")
                lines.append(lesson['solution'])
                lines.append("")
                if lesson['tags']:
                    lines.append(f"**Tags:** {', '.join(lesson['tags'])}")
                    lines.append("")
                lines.append("---")
                lines.append("")
        
        return "\n".join(lines)


# Convenience functions for common tasks

def quick_environment_check() -> Dict[str, Any]:
    """
    Run a quick environment check and return comprehensive status.
    
    Returns:
        Dict with all environment checks
    """
    validator = EnvironmentValidator()
    
    return {
        "git": validator.check_git_access(),
        "github_api": validator.check_github_api_access(),
        "critical_packages": validator.check_python_packages([
            "pytest", "yaml", "json"
        ])
    }


def run_core_tests() -> Dict[str, Any]:
    """
    Run core test suite that doesn't require heavy dependencies.
    
    Returns:
        Dict with test results
    """
    runner = TestRunner()
    
    tests = []
    
    # Run autonomous agent tests
    if Path("tests/test_autonomous_agent.py").exists():
        tests.append(
            runner.run_pytest_suite("tests/test_autonomous_agent.py")
        )
    
    return {
        "total_suites": len(tests),
        "results": tests
    }


# Initialize lessons learned on import
_lessons = LessonsLearned()


# Add initial lessons from current session
_lessons.add_lesson(
    category="dependency-testing",
    title="pip install hangs with large ML packages",
    description=(
        "When attempting to install packages like torch (2.6.0), "
        "transformers (4.48.0), or mlflow (2.22.4) in virtual environment, "
        "pip install -e . hangs without output for 180+ seconds"
    ),
    solution=(
        "Use incremental installation: Install packages one at a time with "
        "progress indicators. Alternative: Use existing environment or defer "
        "to CI/CD pipeline. For future: Add --progress-bar on and --verbose "
        "flags to pip commands."
    ),
    tags=["pip", "installation", "timeout", "ml-packages"]
)

_lessons.add_lesson(
    category="api-access",
    title="GitHub CLI requires explicit token in some environments",
    description=(
        "In automated environments, gh CLI commands may fail even when "
        "git operations work. Git uses credential helper but gh requires "
        "explicit GITHUB_TOKEN or GH_TOKEN environment variable."
    ),
    solution=(
        "Workaround 1: Use git commands instead of gh CLI. "
        "Workaround 2: Document operations requiring API access. "
        "Workaround 3: Request human admin to configure GITHUB_TOKEN. "
        "For workflows: Use GitHub Actions context variables."
    ),
    tags=["github-cli", "authentication", "api-access", "workaround"]
)

_lessons.add_lesson(
    category="testing",
    title="JSON serialization fails with Enum objects in dataclasses",
    description=(
        "When using asdict() from dataclasses with Enum fields, "
        "json.dump() raises TypeError: Object of type HealthStatus "
        "is not JSON serializable"
    ),
    solution=(
        "Create recursive enum_to_value helper function that converts "
        "Enum objects to their .value property before serialization. "
        "Apply to all dict/list structures before json.dump()."
    ),
    tags=["json", "enum", "serialization", "dataclass"]
)


if __name__ == "__main__":
    # CLI interface for toolkit
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Agent Toolkit - Reusable utilities"
    )
    parser.add_argument(
        "command",
        choices=["check-env", "run-tests", "lessons", "export-lessons"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "check-env":
        print("=== Environment Check ===")
        result = quick_environment_check()
        print(json.dumps(result, indent=2))
    
    elif args.command == "run-tests":
        print("=== Running Core Tests ===")
        result = run_core_tests()
        print(json.dumps(result, indent=2))
    
    elif args.command == "lessons":
        print("=== Lessons Learned ===")
        for lesson in _lessons.lessons:
            print(f"\n{lesson['id']}. {lesson['title']}")
            print(f"   Category: {lesson['category']}")
            print(f"   Tags: {', '.join(lesson['tags'])}")
    
    elif args.command == "export-lessons":
        print(_lessons.export_markdown())
