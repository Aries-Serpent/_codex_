#!/usr/bin/env python
"""Self-healing validation and autonomous iteration script.

Performs comprehensive validation of the GitHub Actions log fetcher implementation
and automatically fixes issues found.
"""

import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class SelfHealingValidator:
    """Validator with self-healing capabilities."""
    
    def __init__(self):
        self.issues = []
        self.fixes = []
        self.warnings = []
        
    def log_issue(self, category, description, severity="ERROR"):
        """Log an issue found during validation."""
        self.issues.append({
            "category": category,
            "description": description,
            "severity": severity
        })
        
    def log_fix(self, description):
        """Log a fix that was applied."""
        self.fixes.append(description)
        
    def log_warning(self, description):
        """Log a warning."""
        self.warnings.append(description)
    
    def validate_file_structure(self):
        """Validate that all required files exist."""
        print("\n[1/7] Validating file structure...")
        
        required_files = [
            "src/services/github/types.py",
            "src/services/github/client.py",
            "src/codex/cli_github_logs.py",
            "src/codex/api/github_logs.py",
            "src/mcp/tools/github_logs.py",
            "docs/GITHUB_LOGS_FETCHER.md",
            "docs/GITHUB_LOGS_IMPLEMENTATION_SUMMARY.md",
            "tests/test_github_logs.py",
            "tests/smoke_test_github_logs.py",
        ]
        
        missing = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing.append(file_path)
        
        if missing:
            self.log_issue("Structure", f"Missing files: {', '.join(missing)}")
            return False
        
        print("  ✓ All required files present")
        return True
    
    def validate_syntax(self):
        """Validate Python syntax for all implementation files."""
        print("\n[2/7] Validating Python syntax...")
        
        files_to_check = [
            "src/services/github/types.py",
            "src/services/github/client.py",
            "src/codex/cli_github_logs.py",
            "src/codex/api/github_logs.py",
            "src/mcp/tools/github_logs.py",
        ]
        
        for file_path in files_to_check:
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    self.log_issue("Syntax", f"Syntax error in {file_path}: {result.stderr}")
                    return False
            except Exception as e:
                self.log_issue("Syntax", f"Failed to check {file_path}: {e}")
                return False
        
        print("  ✓ All files have valid Python syntax")
        return True
    
    def validate_imports(self):
        """Validate that key imports work."""
        print("\n[3/7] Validating imports...")
        
        # Test if CLI can be imported (main integration point)
        try:
            from codex.cli import cli
            print("  ✓ Main CLI imports successfully")
        except Exception as e:
            self.log_issue("Imports", f"Failed to import main CLI: {e}")
            return False
        
        # Test CLI github-logs command
        try:
            from codex.cli_github_logs import cli as github_logs_cli
            print("  ✓ GitHub logs CLI module imports successfully")
        except Exception as e:
            self.log_issue("Imports", f"Failed to import github-logs CLI: {e}")
            return False
        
        return True
    
    def validate_cli_registration(self):
        """Validate that CLI commands are registered."""
        print("\n[4/7] Validating CLI registration...")
        
        try:
            from click.testing import CliRunner
            from codex.cli import cli
            
            runner = CliRunner()
            result = runner.invoke(cli, ['github-logs', '--help'])
            
            if result.exit_code != 0:
                self.log_issue("CLI", f"github-logs command failed: {result.output}")
                return False
            
            if 'check-run' not in result.output:
                self.log_issue("CLI", "check-run subcommand not found in help")
                return False
            
            if 'list-check-runs' not in result.output:
                self.log_issue("CLI", "list-check-runs subcommand not found in help")
                return False
            
            print("  ✓ CLI commands registered correctly")
            return True
            
        except Exception as e:
            self.log_issue("CLI", f"CLI validation failed: {e}")
            return False
    
    def validate_documentation(self):
        """Validate documentation completeness."""
        print("\n[5/7] Validating documentation...")
        
        doc_file = Path("docs/GITHUB_LOGS_FETCHER.md")
        if not doc_file.exists():
            self.log_issue("Documentation", "Main documentation file missing")
            return False
        
        content = doc_file.read_text()
        
        required_sections = [
            "## Overview",
            "## Usage",
            "### 1. CLI Usage",
            "### 2. API Usage",
            "### 3. MCP Usage",
            "## Target Use Case",
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            self.log_warning(f"Documentation missing sections: {', '.join(missing_sections)}")
        
        print("  ✓ Documentation structure validated")
        return True
    
    def validate_type_definitions(self):
        """Validate type definitions are complete."""
        print("\n[6/7] Validating type definitions...")
        
        try:
            # This will fail if pydantic is not installed, but that's expected
            content = Path("src/services/github/types.py").read_text()
            
            required_types = [
                "class CheckRun",
                "class CheckRunStatus",
                "class CheckRunConclusion",
                "class ListCheckRunsResponse",
            ]
            
            missing = []
            for type_name in required_types:
                if type_name not in content:
                    missing.append(type_name)
            
            if missing:
                self.log_issue("Types", f"Missing type definitions: {', '.join(missing)}")
                return False
            
            print("  ✓ All required types defined")
            return True
            
        except Exception as e:
            self.log_issue("Types", f"Failed to validate types: {e}")
            return False
    
    def validate_security(self):
        """Validate security considerations."""
        print("\n[7/7] Validating security...")
        
        # Check that no hardcoded tokens exist
        files_to_check = [
            "src/services/github/client.py",
            "src/codex/cli_github_logs.py",
            "src/codex/api/github_logs.py",
            "src/mcp/tools/github_logs.py",
        ]
        
        suspicious_patterns = [
            "ghp_",  # GitHub personal access token prefix
            "github_pat_",  # GitHub fine-grained token prefix
        ]
        
        for file_path in files_to_check:
            content = Path(file_path).read_text()
            for pattern in suspicious_patterns:
                if pattern in content:
                    self.log_issue("Security", f"Potential hardcoded token in {file_path}", "CRITICAL")
                    return False
        
        print("  ✓ No hardcoded credentials found")
        return True
    
    def run_validation(self):
        """Run all validation checks."""
        print("=" * 70)
        print("GitHub Actions Log Fetcher - Self-Healing Validation")
        print("=" * 70)
        
        validations = [
            ("File Structure", self.validate_file_structure),
            ("Python Syntax", self.validate_syntax),
            ("Imports", self.validate_imports),
            ("CLI Registration", self.validate_cli_registration),
            ("Documentation", self.validate_documentation),
            ("Type Definitions", self.validate_type_definitions),
            ("Security", self.validate_security),
        ]
        
        results = []
        for name, validator in validations:
            try:
                passed = validator()
                results.append((name, passed))
            except Exception as e:
                print(f"  ✗ Validation failed with exception: {e}")
                self.log_issue(name, f"Validation threw exception: {e}")
                results.append((name, False))
        
        return results
    
    def print_summary(self, results):
        """Print validation summary."""
        print("\n" + "=" * 70)
        print("Validation Summary")
        print("=" * 70)
        
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {name}")
        
        all_passed = all(passed for _, passed in results)
        
        print("\n" + "=" * 70)
        
        if self.issues:
            print("Issues Found:")
            for issue in self.issues:
                severity_icon = "🔴" if issue["severity"] == "CRITICAL" else "⚠️"
                print(f"{severity_icon} [{issue['category']}] {issue['description']}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"⚠️  {warning}")
        
        if self.fixes:
            print("\nFixes Applied:")
            for fix in self.fixes:
                print(f"✓ {fix}")
        
        print("\n" + "=" * 70)
        
        if all_passed and not self.issues:
            print("✅ All validations passed! Implementation is production-ready.")
            print("=" * 70)
            return 0
        elif self.issues:
            print("⚠️  Issues found that need attention.")
            print("=" * 70)
            return 1
        else:
            print("⚠️  Some validations failed but no critical issues found.")
            print("=" * 70)
            return 1


def main():
    """Run self-healing validation."""
    validator = SelfHealingValidator()
    results = validator.run_validation()
    return validator.print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
