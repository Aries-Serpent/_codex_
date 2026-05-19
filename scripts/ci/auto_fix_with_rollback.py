#!/usr/bin/env python3
"""
Enhanced Auto-Fix Script with Rollback Support

Safely applies fixes to code with automatic rollback on failure.
Includes pre-flight checks, per-fix isolation, and comprehensive logging.

Usage:
    python scripts/ci/auto_fix_with_rollback.py [options]

Options:
    --pre-flight      Run pre-flight checks only
    --apply           Apply fixes with rollback support
    --pattern N       Only apply specific pattern (1-8)
    --verbose         Enable verbose logging
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class PreFlightError(Exception):
    """Raised when pre-flight checks fail."""



class FixApplicationError(Exception):
    """Raised when fix application fails."""



class AutoFixWithRollback:
    """Enhanced auto-fix with rollback support and safety checks."""

    def __init__(
        self, repo_root: Path, verbose: bool = False, max_retries: int = 3
    ):
        self.repo_root = repo_root
        self.max_retries = max_retries
        self.logger = self._setup_logging(verbose)
        self.metrics = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "pre_flight_passed": False,
            "fixes_attempted": 0,
            "fixes_succeeded": 0,
            "fixes_failed": 0,
            "rollbacks_performed": 0,
        }

    def _setup_logging(self, verbose: bool) -> logging.Logger:
        """Set up logging configuration."""
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("auto_fix_rollback.log"),
            ],
        )
        return logging.getLogger(__name__)

    def run_pre_flight_checks(self) -> bool:
        """Run comprehensive pre-flight checks.

        Returns:
            True if all checks pass

        Raises:
            PreFlightError if any check fails
        """
        self.logger.info("Running pre-flight checks...")

        checks = {
            "git_repository": self._check_git_repository,
            "git_clean": self._check_git_clean,
            "files_writable": self._check_files_writable,
            "branch_valid": self._check_branch_valid,
            "python_available": self._check_python_available,
            "tools_available": self._check_tools_available,
        }

        results = {}
        for name, check_func in checks.items():
            try:
                result = check_func()
                results[name] = result
                status = "✓" if result else "✗"
                self.logger.info(f"  {status} {name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                results[name] = False
                self.logger.error(f"  ✗ {name}: ERROR - {e}")

        all_passed = all(results.values())
        self.metrics["pre_flight_passed"] = all_passed

        if not all_passed:
            failed = [name for name, passed in results.items() if not passed]
            raise PreFlightError(f"Pre-flight checks failed: {', '.join(failed)}")

        self.logger.info("✓ All pre-flight checks passed")
        return True

    def _check_git_repository(self) -> bool:
        """Check if we're in a git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _check_git_clean(self) -> bool:
        """Check if git working directory is clean."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            # Allow untracked files, but no modifications
            lines = result.stdout.strip().split("\n")
            has_modifications = any(
                line and not line.startswith("??") for line in lines
            )
            return not has_modifications
        except subprocess.CalledProcessError:
            return False

    def _check_files_writable(self) -> bool:
        """Check if key directories are writable."""
        test_dirs = [self.repo_root / "src", self.repo_root / "tests"]
        for test_dir in test_dirs:
            if test_dir.exists():
                test_file = test_dir / ".write_test"
                try:
                    test_file.touch()
                    test_file.unlink()
                except (OSError, PermissionError):
                    self.logger.error(f"Directory not writable: {test_dir}")
                    return False
        return True

    def _check_branch_valid(self) -> bool:
        """Check if current branch is valid (not detached HEAD)."""
        try:
            subprocess.run(
                ["git", "symbolic-ref", "-q", "HEAD"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            self.logger.warning("Detached HEAD state detected")
            return False

    def _check_python_available(self) -> bool:
        """Check if Python is available."""
        try:
            subprocess.run(
                [sys.executable, "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_tools_available(self) -> bool:
        """Check if required tools are available."""
        tools = ["ruff", "black", "isort"]
        for tool in tools:
            try:
                subprocess.run(
                    ["python", "-m", tool, "--version"],
                    check=True,
                    capture_output=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.warning(f"Tool not available: {tool}")
                return False
        return True

    @contextmanager
    def rollback_context(self, file_path: Path):
        """Context manager for automatic rollback on failure.

        Args:
            file_path: Path to file being modified

        Yields:
            Path to the file

        Raises:
            FixApplicationError if rollback needed
        """
        backup_path = None
        try:
            # Create backup
            if file_path.exists():
                # FIX: Use secure tempfile.mkstemp instead of insecure mktemp
                fd, backup_path_str = tempfile.mkstemp(suffix=".backup")
                backup_path = Path(backup_path_str)
                import os
                os.close(fd)  # Close the file descriptor immediately
                shutil.copy2(file_path, backup_path)
                self.logger.debug(f"Created backup: {backup_path}")

            yield file_path

            # Validate after modification
            if file_path.suffix == ".py":
                self._validate_python_syntax(file_path)

            # Clean up backup on success
            if backup_path and backup_path.exists():
                backup_path.unlink()
                self.logger.debug(f"Removed backup: {backup_path}")

        except Exception as e:
            # Rollback on any error
            if backup_path and backup_path.exists():
                self.logger.warning(f"Rolling back {file_path}: {e}")
                shutil.copy2(backup_path, file_path)
                backup_path.unlink()
                self.metrics["rollbacks_performed"] += 1
            raise FixApplicationError(f"Fix failed for {file_path}: {e}") from e

    def _validate_python_syntax(self, file_path: Path) -> bool:
        """Validate Python syntax after fix.

        Args:
            file_path: Path to Python file

        Returns:
            True if syntax is valid

        Raises:
            FixApplicationError if syntax is invalid
        """
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise FixApplicationError(f"Invalid Python syntax: {e.stderr.decode()}")

    def apply_fix_with_retry(
        self, fix_name: str, fix_func, *args, **kwargs
    ) -> bool:
        """Apply fix with exponential backoff retry logic.

        Args:
            fix_name: Human-readable name for the fix
            fix_func: Function to apply the fix
            *args, **kwargs: Arguments for fix function

        Returns:
            True if fix succeeded
        """
        self.metrics["fixes_attempted"] += 1

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(
                    f"Applying fix: {fix_name} (attempt {attempt}/{self.max_retries})"
                )
                result = fix_func(*args, **kwargs)

                if result:
                    self.metrics["fixes_succeeded"] += 1
                    self.logger.info(f"✓ Fix succeeded: {fix_name}")
                    return True

            except Exception as e:
                self.logger.warning(
                    f"Fix attempt {attempt} failed for {fix_name}: {e}"
                )

                if attempt < self.max_retries:
                    wait_time = 2**attempt  # Exponential backoff
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"✗ All attempts failed for {fix_name}")
                    self.metrics["fixes_failed"] += 1

        return False

    def fix_unused_imports(self) -> bool:
        """Fix unused imports using ruff with rollback support."""

        def _fix():
            # Get list of files with unused imports
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "ruff",
                    "check",
                    "--select",
                    "F401",
                    "src/",
                    "tests/",
                    "--output-format=json",
                ],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
            )

            if not result.stdout.strip():
                return True  # No issues

            issues = json.loads(result.stdout)
            affected_files = set(issue["filename"] for issue in issues)

            for file_path_str in affected_files:
                file_path = Path(file_path_str)
                with self.rollback_context(file_path):
                    # Apply fix
                    subprocess.run(
                        [
                            "python",
                            "-m",
                            "ruff",
                            "check",
                            "--select",
                            "F401",
                            "--fix",
                            str(file_path),
                        ],
                        cwd=self.repo_root,
                        check=True,
                        capture_output=True,
                    )

            return True

        return self.apply_fix_with_retry("unused imports", _fix)

    def commit_and_push_fixes(self, changed_files: list[Path]) -> bool:
        """Commit and push fixes with retry logic.

        Args:
            changed_files: List of files that were modified

        Returns:
            True if commit/push succeeded
        """
        if not changed_files:
            self.logger.info("No changes to commit")
            return True

        self.logger.info(f"Committing {len(changed_files)} changed files")

        try:
            # Stage files
            subprocess.run(
                ["git", "add"] + [str(f) for f in changed_files],
                cwd=self.repo_root,
                check=True,
            )

            # Create commit message
            commit_msg = (
                f"auto-fix: Applied fixes to {len(changed_files)} files\n\n"
                + "\n".join(f"- {f}" for f in changed_files)
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.repo_root,
                check=True,
            )

            # Push with retry
            for attempt in range(1, self.max_retries + 1):
                try:
                    subprocess.run(
                        ["git", "push"], cwd=self.repo_root, check=True, timeout=30
                    )
                    self.logger.info("✓ Changes pushed successfully")
                    return True
                except subprocess.CalledProcessError:
                    if attempt < self.max_retries:
                        wait_time = 2**attempt
                        self.logger.warning(
                            f"Push failed, retrying in {wait_time} seconds..."
                        )
                        time.sleep(wait_time)
                    else:
                        raise

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Commit/push failed: {e}")
            return False

        return False

    def save_metrics(self, output_path: str = "auto_fix_metrics.json"):
        """Save metrics to file.

        Args:
            output_path: Path to save metrics JSON
        """
        self.metrics["end_time"] = datetime.now(timezone.utc).isoformat()
        with open(output_path, "w") as f:
            json.dump(self.metrics, f, indent=2)
        self.logger.info(f"Metrics saved to {output_path}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Enhanced auto-fix with rollback support"
    )
    parser.add_argument(
        "--pre-flight", action="store_true", help="Run pre-flight checks only"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply fixes with rollback support"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--pattern", type=int, help="Only apply specific pattern (1-8)"
    )

    args = parser.parse_args()

    repo_root = Path.cwd()
    fixer = AutoFixWithRollback(repo_root, verbose=args.verbose)

    try:
        if args.pre_flight or not args.apply:
            # Run pre-flight checks
            fixer.run_pre_flight_checks()
            print("\n✓ Pre-flight checks passed - ready to apply fixes")
            sys.exit(0)

        if args.apply:
            # Run pre-flight first
            fixer.run_pre_flight_checks()

            # Apply fixes
            print("\nApplying fixes with rollback support...")
            success = fixer.fix_unused_imports()

            # Save metrics
            fixer.save_metrics()

            if success:
                print("\n✓ Fixes applied successfully")
                sys.exit(0)
            else:
                print("\n✗ Some fixes failed")
                sys.exit(1)

    except PreFlightError as e:
        print(f"\n✗ Pre-flight checks failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        fixer.logger.exception("Unexpected error")
        sys.exit(1)


if __name__ == "__main__":
    main()
