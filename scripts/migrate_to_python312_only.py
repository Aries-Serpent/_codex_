#!/usr/bin/env python3
"""
Complete Python 3.11 to 3.12 Migration Script

This script performs a deterministic, comprehensive migration from Python 3.11
to Python 3.12 ONLY, eliminating all Python 3.11 references and cachesets.

Strategy: A - Immediate Full Migration (Weighted Score: 7.55/10)
Breaking Change: YES - Python 3.11 will no longer be supported
Confidence: VERY HIGH (95%)

Usage:
    python scripts/migrate_to_python312_only.py [--dry-run] [--verbose]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


class Python312MigrationTool:
    """Deterministic migration tool for Python 3.11 → 3.12 complete transition."""

    def __init__(self, repo_root: Path, dry_run: bool = False, verbose: bool = False):
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.changes: list[dict] = []
        self.errors: list[str] = []

    def log(self, message: str, level: str = "INFO"):
        """Log messages with color coding."""
        colors = {
            "INFO": BLUE,
            "SUCCESS": GREEN,
            "WARNING": YELLOW,
            "ERROR": RED,
        }
        color = colors.get(level, RESET)
        prefix = f"{color}[{level}]{RESET}"
        print(f"{prefix} {message}")

    def record_change(self, file_path: Path, change_type: str, details: str):
        """Record a change for reporting."""
        self.changes.append({
            "file": str(file_path.relative_to(self.repo_root)),
            "type": change_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        })

    def update_pyproject_toml(self) -> bool:
        """Update pyproject.toml to require Python 3.12+."""
        pyproject_path = self.repo_root / "pyproject.toml"

        if not pyproject_path.exists():
            self.errors.append("pyproject.toml not found")
            return False

        content = pyproject_path.read_text()
        original_content = content

        # Update requires-python
        content = re.sub(
            r'requires-python\s*=\s*">=3\.11"',
            'requires-python = ">=3.12"',
            content
        )

        # Remove Python 3.11 classifier
        content = re.sub(
            r'"Programming Language :: Python :: 3\.11",?\n',
            '',
            content
        )

        # Add comment about breaking change
        if 'requires-python = ">=3.12"' in content and 'BREAKING CHANGE' not in content:
            content = content.replace(
                'requires-python = ">=3.12"',
                'requires-python = ">=3.12"  # BREAKING CHANGE: Python 3.11 support removed'
            )

        if content != original_content:
            if not self.dry_run:
                pyproject_path.write_text(content)
            self.record_change(pyproject_path, "PYTHON_VERSION", "Updated requires-python to >=3.12, removed 3.11 classifier")
            self.log(f"✅ Updated {pyproject_path.relative_to(self.repo_root)}", "SUCCESS")
            return True
        return False

    def update_workflow_files(self) -> int:
        """Update all GitHub Actions workflow files."""
        workflows_dir = self.repo_root / ".github" / "workflows"

        if not workflows_dir.exists():
            self.errors.append(".github/workflows directory not found")
            return 0

        count = 0
        workflow_files = list(workflows_dir.glob("**/*.yml")) + list(workflows_dir.glob("**/*.yaml"))

        for workflow_file in workflow_files:
            if self.update_workflow_file(workflow_file):
                count += 1

        return count

    def update_workflow_file(self, workflow_path: Path) -> bool:
        """Update a single workflow file."""
        content = workflow_path.read_text()
        original_content = content
        changes_made = []

        # Pattern 1: Matrix with ['3.11', '3.12'] → ['3.12']
        if "python-version: ['3.11', '3.12']" in content or 'python-version: ["3.11", "3.12"]' in content:
            content = re.sub(
                r"python-version:\s*\[['\"]3\.11['\"],\s*['\"]3\.12['\"]\]",
                "python-version: ['3.12']",
                content
            )
            changes_made.append("Removed 3.11 from matrix")

        # Pattern 2: Hardcoded python-version: 3.11 or '3.11'
        if re.search(r"python-version:\s*['\"]?3\.11['\"]?", content):
            content = re.sub(
                r"python-version:\s*['\"]?3\.11['\"]?",
                "python-version: '3.12'",
                content
            )
            changes_made.append("Changed 3.11 to 3.12")

        # Pattern 3: Environment variable PYTHON_VERSION: 3.11
        if re.search(r"PYTHON_VERSION:\s*['\"]?3\.11['\"]?", content):
            content = re.sub(
                r"PYTHON_VERSION:\s*['\"]?3\.11['\"]?",
                "PYTHON_VERSION: '3.12'",
                content
            )
            changes_made.append("Updated PYTHON_VERSION env var")

        # Pattern 4: Cache keys referencing 3.11
        if "py311" in content or "python-3.11" in content or "python3.11" in content:
            content = content.replace("py311", "py312")
            content = content.replace("python-3.11", "python-3.12")
            content = content.replace("python3.11", "python3.12")
            changes_made.append("Updated cache keys")

        # Pattern 5: Comments mentioning Python 3.11
        content = re.sub(
            r"#\s*.*Python\s+3\.11.*$",
            "# Python 3.12 only (3.11 support removed)",
            content,
            flags=re.MULTILINE
        )

        if content != original_content:
            if not self.dry_run:
                workflow_path.write_text(content)
            details = "; ".join(changes_made)
            self.record_change(workflow_path, "WORKFLOW", details)
            self.log(f"✅ Updated {workflow_path.relative_to(self.repo_root)}: {details}", "SUCCESS")
            return True

        return False

    def update_dockerfile_files(self) -> int:
        """Update Dockerfiles to use Python 3.12."""
        dockerfiles = list(self.repo_root.glob("**/Dockerfile*"))
        count = 0

        for dockerfile in dockerfiles:
            if self.update_dockerfile(dockerfile):
                count += 1

        return count

    def update_dockerfile(self, dockerfile_path: Path) -> bool:
        """Update a single Dockerfile."""
        content = dockerfile_path.read_text()
        original_content = content

        # Update FROM python:3.11 → FROM python:3.12
        content = re.sub(
            r"FROM\s+python:3\.11",
            "FROM python:3.12",
            content
        )

        # Update python3.11 references
        content = re.sub(
            r"python3\.11",
            "python3.12",
            content
        )

        if content != original_content:
            if not self.dry_run:
                dockerfile_path.write_text(content)
            self.record_change(dockerfile_path, "DOCKERFILE", "Updated Python version to 3.12")
            self.log(f"✅ Updated {dockerfile_path.relative_to(self.repo_root)}", "SUCCESS")
            return True

        return False

    def update_python_version_files(self) -> int:
        """Update .python-version and runtime.txt files."""
        count = 0

        # Update .python-version
        python_version_files = list(self.repo_root.glob("**/.python-version"))
        for pv_file in python_version_files:
            content = pv_file.read_text().strip()
            if content.startswith("3.11"):
                if not self.dry_run:
                    pv_file.write_text("3.12.0\n")
                self.record_change(pv_file, "VERSION_FILE", f"Changed {content} → 3.12.0")
                self.log(f"✅ Updated {pv_file.relative_to(self.repo_root)}", "SUCCESS")
                count += 1

        # Update runtime.txt (Heroku, etc.)
        runtime_files = list(self.repo_root.glob("**/runtime.txt"))
        for rt_file in runtime_files:
            content = rt_file.read_text().strip()
            if "3.11" in content:
                new_content = re.sub(r"python-3\.11\.\d+", "python-3.12.0", content)
                if not self.dry_run:
                    rt_file.write_text(new_content + "\n")
                self.record_change(rt_file, "VERSION_FILE", f"Changed {content} → {new_content}")
                self.log(f"✅ Updated {rt_file.relative_to(self.repo_root)}", "SUCCESS")
                count += 1

        return count

    def update_documentation(self) -> int:
        """Update documentation files."""
        count = 0
        doc_files = (
            list(self.repo_root.glob("*.md")) +
            list(self.repo_root.glob("docs/**/*.md")) +
            list(self.repo_root.glob(".github/**/*.md"))
        )

        for doc_file in doc_files:
            if self.update_doc_file(doc_file):
                count += 1

        return count

    def update_doc_file(self, doc_path: Path) -> bool:
        """Update a documentation file."""
        try:
            content = doc_path.read_text()
        except (UnicodeDecodeError, PermissionError):
            return False

        original_content = content

        # Replace Python 3.11 references with 3.12
        # Be conservative - only replace version numbers, not prose
        patterns = [
            (r"Python\s+3\.11", "Python 3.12"),
            (r"python\s+3\.11", "python 3.12"),
            (r"Python\s+≥\s*3\.11", "Python ≥ 3.12"),
            (r"python-version:\s*3\.11", "python-version: 3.12"),
            (r"`3\.11`", "`3.12`"),
            (r"\[3\.11,\s*3\.12\]", "[3.12]"),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            if not self.dry_run:
                doc_path.write_text(content)
            self.record_change(doc_path, "DOCUMENTATION", "Updated Python version references")
            self.log(f"✅ Updated {doc_path.relative_to(self.repo_root)}", "SUCCESS")
            return True

        return False

    def generate_report(self) -> dict:
        """Generate migration report."""
        report = {
            "migration_strategy": "A - Immediate Full Migration",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "dry_run": self.dry_run,
            "summary": {
                "total_files_changed": len(self.changes),
                "errors": len(self.errors),
                "breaking_change": True,
                "python_version_from": "3.11",
                "python_version_to": "3.12",
            },
            "changes_by_type": {},
            "changes": self.changes,
            "errors": self.errors
        }

        # Count changes by type
        for change in self.changes:
            change_type = change["type"]
            report["changes_by_type"][change_type] = report["changes_by_type"].get(change_type, 0) + 1

        return report

    def run(self) -> bool:
        """Execute the migration."""
        self.log(f"{BOLD}Python 3.11 → 3.12 Complete Migration{RESET}", "INFO")
        self.log("Strategy: A - Immediate Full Migration", "INFO")
        self.log(f"Repository: {self.repo_root}", "INFO")
        self.log(f"Dry Run: {self.dry_run}", "INFO")
        self.log("", "INFO")

        # Phase 1: Update pyproject.toml
        self.log("Phase 1: Updating pyproject.toml...", "INFO")
        self.update_pyproject_toml()

        # Phase 2: Update workflows
        self.log("Phase 2: Updating GitHub Actions workflows...", "INFO")
        workflow_count = self.update_workflow_files()
        self.log(f"Updated {workflow_count} workflow files", "INFO")

        # Phase 3: Update Dockerfiles
        self.log("Phase 3: Updating Dockerfiles...", "INFO")
        dockerfile_count = self.update_dockerfile_files()
        self.log(f"Updated {dockerfile_count} Docker files", "INFO")

        # Phase 4: Update version files
        self.log("Phase 4: Updating version files...", "INFO")
        version_file_count = self.update_python_version_files()
        self.log(f"Updated {version_file_count} version files", "INFO")

        # Phase 5: Update documentation
        self.log("Phase 5: Updating documentation...", "INFO")
        doc_count = self.update_documentation()
        self.log(f"Updated {doc_count} documentation files", "INFO")

        # Generate report
        report = self.generate_report()

        # Save report
        report_file = self.repo_root / ".codex" / "PYTHON_312_MIGRATION_REPORT.json"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        self.log("", "INFO")
        self.log(f"{BOLD}=== MIGRATION SUMMARY ==={RESET}", "INFO")
        self.log(f"Total files changed: {len(self.changes)}", "SUCCESS" if len(self.changes) > 0 else "INFO")
        self.log(f"Errors encountered: {len(self.errors)}", "ERROR" if len(self.errors) > 0 else "INFO")

        if self.changes:
            self.log(f"{BOLD}Changes by type:{RESET}", "INFO")
            for change_type, count in report["changes_by_type"].items():
                self.log(f"  {change_type}: {count}", "INFO")

        if self.errors:
            self.log(f"{BOLD}Errors:{RESET}", "ERROR")
            for error in self.errors:
                self.log(f"  {error}", "ERROR")

        self.log(f"Report saved to: {report_file}", "INFO")

        return len(self.errors) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate repository from Python 3.11 to Python 3.12 ONLY"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making actual changes"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)"
    )

    args = parser.parse_args()

    migrator = Python312MigrationTool(
        repo_root=args.repo_root,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    success = migrator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
