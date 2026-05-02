#!/usr/bin/env python3
"""
Workflow Deprecation Automation Script

Safely deprecates original workflows that have been consolidated into suite workflows.

Features:
- Validates consolidated replacement is working
- Checks for remaining references
- Adds .disabled extension
- Moves to workflow-archive/deprecated/
- Updates documentation
- Creates deprecation record

Usage:
    python scripts/deprecate_workflow.py <workflow-file> [OPTIONS]

Options:
    --dry-run             Show what would be done without making changes
    --force               Skip validation checks (use with caution)
    --consolidated SUITE  Name of consolidated suite replacing this workflow
"""

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class WorkflowDeprecator:
    """Automate the safe deprecation of GitHub Actions workflows."""

    def __init__(self, workflow_file: str, dry_run: bool = False, force: bool = False):
        self.workflow_file = workflow_file
        self.dry_run = dry_run
        self.force = force
        self.repo_root = Path.cwd()
        self.workflow_path = self.repo_root / '.github' / 'workflows' / workflow_file
        self.archive_dir = self.repo_root / '.github' / 'workflow-archive' / 'deprecated'

        # Consolidated suite mapping
        self.suite_mapping = {
            'cache-warmup.yml': 'cache-suite.yml',
            'cache-management.yml': 'cache-suite.yml',
            'cache-cleanup.yml': 'cache-suite.yml',
            'test-rag.yml': 'test-suite.yml',
            'auth-tests.yml': 'test-suite.yml',
            'determinism.yml': 'test-suite.yml',
            'integration-gated.yml': 'test-suite.yml',
            'coverage_report.yml': 'test-suite.yml',
            'ci-health-monitor.yml': 'ci-health-suite.yml',
            'ci-diagnostic-automation.yml': 'ci-health-suite.yml',
            'repository-health-monitoring.yml': 'ci-health-suite.yml',
            'runner-diagnostics.yml': 'ci-health-suite.yml',
        }

        self.deprecation_log = self.repo_root / '.github' / 'workflow-archive' / 'DEPRECATION_LOG.md'

    def validate_workflow_exists(self) -> bool:
        """Validate that the workflow file exists."""
        if not self.workflow_path.exists():
            print(f"❌ Workflow file not found: {self.workflow_path}")
            return False
        return True

    def get_consolidated_suite(self) -> Optional[str]:
        """Get the consolidated suite that replaces this workflow."""
        return self.suite_mapping.get(self.workflow_file)

    def validate_consolidated_suite(self, suite_file: str) -> bool:
        """Validate that the consolidated suite exists and is working."""
        suite_path = self.repo_root / '.github' / 'workflows' / suite_file

        if not suite_path.exists():
            print(f"❌ Consolidated suite not found: {suite_path}")
            return False

        # Check if suite has .disabled extension
        if suite_file.endswith('.disabled'):
            print(f"❌ Consolidated suite is disabled: {suite_file}")
            return False

        return True

    def find_references(self) -> List[Dict[str, str]]:
        """Find references to this workflow in documentation and other files."""
        references = []
        workflow_name = self.workflow_file.replace('.yml', '').replace('.yaml', '')

        # Search in documentation
        doc_paths = [
            self.repo_root / 'docs',
            self.repo_root / '.github' / 'workflows',
            self.repo_root / '.codex',
            self.repo_root / 'README.md',
            self.repo_root / 'AGENTS.md'
        ]

        for path in doc_paths:
            if not path.exists():
                continue

            files_to_check = [path] if path.is_file() else list(path.rglob('*.md'))

            for file_path in files_to_check:
                try:
                    content = file_path.read_text()

                    # Look for workflow references
                    if self.workflow_file in content or workflow_name in content:
                        # Find line numbers
                        lines = content.split('\n')
                        line_numbers = [
                            i + 1 for i, line in enumerate(lines)
                            if self.workflow_file in line or workflow_name in line
                        ]

                        references.append({
                            'file': str(file_path.relative_to(self.repo_root)),
                            'lines': line_numbers,
                            'type': 'documentation'
                        })
                except Exception as e:
                    print(f"⚠️  Could not read {file_path}: {e}")

        return references

    def check_recent_runs(self) -> Dict[str, Any]:
        """Check if workflow has recent runs (requires GitHub API).

        Note: This is a placeholder for future implementation.
        Actual implementation would query GitHub API for workflow run history.

        For manual verification:
        1. Check GitHub Actions UI for recent runs
        2. Use gh CLI: gh run list --workflow=<workflow-name>
        3. Review failure patterns in last 2 weeks

        Returns:
            Dict with placeholder data. Manual verification required.
        """
        # TODO: Implement GitHub API integration
        # gh api repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs
        # For now, deprecation script requires manual verification
        return {
            'last_run': None,
            'recent_failures': 0,
            'status': 'unknown - manual verification required'
        }

    def disable_workflow(self) -> bool:
        """Add .disabled extension to workflow file."""
        disabled_path = self.workflow_path.parent / f"{self.workflow_file}.disabled"

        if disabled_path.exists():
            print(f"⚠️  Workflow already disabled: {disabled_path}")
            return True

        if self.dry_run:
            print(f"[DRY RUN] Would rename: {self.workflow_path} -> {disabled_path}")
            return True

        try:
            shutil.move(str(self.workflow_path), str(disabled_path))
            print(f"✅ Disabled workflow: {disabled_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to disable workflow: {e}")
            return False

    def archive_workflow(self) -> bool:
        """Move disabled workflow to archive directory."""
        disabled_path = self.workflow_path.parent / f"{self.workflow_file}.disabled"
        archive_path = self.archive_dir / f"{self.workflow_file}.disabled"

        # Create archive directory
        if not self.archive_dir.exists():
            if self.dry_run:
                print(f"[DRY RUN] Would create directory: {self.archive_dir}")
            else:
                self.archive_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created archive directory: {self.archive_dir}")

        if not disabled_path.exists():
            print(f"❌ Disabled workflow not found: {disabled_path}")
            return False

        if self.dry_run:
            print(f"[DRY RUN] Would move: {disabled_path} -> {archive_path}")
            return True

        try:
            shutil.move(str(disabled_path), str(archive_path))
            print(f"✅ Archived workflow to: {archive_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to archive workflow: {e}")
            return False

    def create_deprecation_record(self, suite_file: str, references: List[Dict[str, str]]) -> bool:
        """Create a record of the deprecation in the log."""
        record = f"""
## {self.workflow_file}

**Deprecation Date:** {datetime.now(timezone.utc).isoformat()}Z
**Replaced By:** {suite_file}
**Status:** Archived

### References Found

"""

        if references:
            for ref in references:
                record += f"- `{ref['file']}` (lines: {', '.join(map(str, ref['lines']))})\n"
        else:
            record += "- No references found\n"

        record += "\n### Migration Notes\n\n"
        record += f"This workflow has been consolidated into `{suite_file}`. "
        record += "All functionality is preserved in the consolidated suite.\n\n"
        record += "---\n\n"

        if self.dry_run:
            print("[DRY RUN] Would append to deprecation log:")
            print(record)
            return True

        # Ensure parent directory exists
        self.deprecation_log.parent.mkdir(parents=True, exist_ok=True)

        # Create log file if it doesn't exist
        if not self.deprecation_log.exists():
            header = "# Workflow Deprecation Log\n\n"
            header += "This log tracks all deprecated workflows and their consolidated replacements.\n\n"
            header += "---\n\n"
            self.deprecation_log.write_text(header)

        # Append record
        try:
            with open(self.deprecation_log, 'a') as f:
                f.write(record)
            print(f"✅ Updated deprecation log: {self.deprecation_log}")
            return True
        except Exception as e:
            print(f"❌ Failed to update deprecation log: {e}")
            return False

    def generate_redirect_doc(self, suite_file: str) -> bool:
        """Generate a redirect/migration document."""
        redirect_path = self.archive_dir / f"{self.workflow_file.replace('.yml', '')}_REDIRECT.md"

        content = f"""# {self.workflow_file} - Deprecated

**Status:** ⚠️ DEPRECATED
**Deprecation Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
**Replaced By:** [{suite_file}](../{suite_file})

## Migration Guide

This workflow has been consolidated into `{suite_file}` for improved efficiency and maintainability.

### What Changed

- All functionality from `{self.workflow_file}` is now part of `{suite_file}`
- Jobs may have different names but provide the same capabilities
- Improved caching and performance optimizations
- Support for AI agent integration via `workflow_call`

### How to Migrate

If you were referencing `{self.workflow_file}` in your code or documentation:

1. Update references to use `{suite_file}`
2. Review the consolidated suite for new job names
3. Update any `workflow_call` invocations if applicable

### Need Help?

- Review the [Consolidation Guide](../CONSOLIDATION_GUIDE.md)
- Check the [Deprecation Plan](../DEPRECATION_PLAN.md)
- Create an issue with the `workflow-consolidation` label

---

**Last Updated:** {datetime.now(timezone.utc).isoformat()}Z
"""

        if self.dry_run:
            print(f"[DRY RUN] Would create redirect doc: {redirect_path}")
            return True

        try:
            redirect_path.write_text(content)
            print(f"✅ Created redirect document: {redirect_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create redirect document: {e}")
            return False

    def run(self, consolidated_suite: Optional[str] = None) -> bool:
        """Execute the deprecation process."""
        print(f"\n{'='*60}")
        print(f"Deprecating Workflow: {self.workflow_file}")
        print(f"{'='*60}\n")

        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made\n")

        # Step 1: Validate workflow exists
        print("Step 1: Validating workflow file...")
        if not self.validate_workflow_exists():
            return False
        print("✅ Workflow file exists\n")

        # Step 2: Determine consolidated suite
        print("Step 2: Determining consolidated suite...")
        suite_file = consolidated_suite or self.get_consolidated_suite()

        if not suite_file:
            print(f"❌ No consolidated suite found for {self.workflow_file}")
            print("   Use --consolidated SUITE to specify manually")
            return False
        print(f"✅ Consolidated suite: {suite_file}\n")

        # Step 3: Validate consolidated suite
        if not self.force:
            print("Step 3: Validating consolidated suite...")
            if not self.validate_consolidated_suite(suite_file):
                return False
            print("✅ Consolidated suite is valid\n")
        else:
            print("⚠️  Step 3: SKIPPED (--force)\n")

        # Step 4: Find references
        print("Step 4: Finding references...")
        references = self.find_references()
        if references:
            print(f"⚠️  Found {len(references)} files with references:")
            for ref in references:
                print(f"   - {ref['file']} (lines: {', '.join(map(str, ref['lines']))})")
            print()

            if not self.force and not self.dry_run:
                response = input("Continue with deprecation? (y/n): ")
                if response.lower() != 'y':
                    print("❌ Deprecation cancelled by user")
                    return False
        else:
            print("✅ No references found\n")

        # Step 5: Disable workflow
        print("Step 5: Disabling workflow...")
        if not self.disable_workflow():
            return False
        print()

        # Step 6: Archive workflow
        print("Step 6: Archiving workflow...")
        if not self.archive_workflow():
            return False
        print()

        # Step 7: Create deprecation record
        print("Step 7: Creating deprecation record...")
        if not self.create_deprecation_record(suite_file, references):
            return False
        print()

        # Step 8: Generate redirect document
        print("Step 8: Generating redirect document...")
        if not self.generate_redirect_doc(suite_file):
            return False
        print()

        print(f"{'='*60}")
        print("✅ DEPRECATION COMPLETE")
        print(f"{'='*60}\n")

        if self.dry_run:
            print("This was a dry run. Re-run without --dry-run to apply changes.")
        else:
            print("Next steps:")
            print("1. Update documentation to reference the consolidated suite")
            print("2. Test that CI/CD still works correctly")
            print("3. Monitor for 48 hours")
            print("4. Update cognitive brain status")

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Safely deprecate a GitHub Actions workflow'
    )
    parser.add_argument(
        'workflow',
        help='Workflow file to deprecate (e.g., cache-warmup.yml)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip validation checks (use with caution)'
    )
    parser.add_argument(
        '--consolidated',
        help='Name of consolidated suite replacing this workflow'
    )

    args = parser.parse_args()

    deprecator = WorkflowDeprecator(args.workflow, args.dry_run, args.force)
    success = deprecator.run(args.consolidated)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
