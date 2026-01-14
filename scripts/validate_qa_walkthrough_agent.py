#!/usr/bin/env python3
"""
Validation script for Codebase QA Walkthrough Agent setup.

This script validates that all components of the QA Walkthrough Agent are properly
configured and ready for use. It checks:
- Agent definition files
- Workflow configuration
- Documentation completeness
- Integration points
- Tool availability

Usage:
    python scripts/validate_qa_walkthrough_agent.py
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class QAWalkthroughValidator:
    """Validator for QA Walkthrough Agent setup."""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
    
    def validate_agent_definition(self) -> bool:
        """Validate agent definition file."""
        agent_file = self.repo_root / ".github/agents/codebase-qa-walkthrough-agent.agent.yml"
        
        if not agent_file.exists():
            self.errors.append(f"Agent definition file not found: {agent_file}")
            return False
        
        try:
            with open(agent_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ['name', 'description', 'version', 'agent_type', 'capabilities']
            for field in required_fields:
                if field not in config:
                    self.errors.append(f"Missing required field in agent definition: {field}")
                    return False
            
            # Validate triggers
            if 'triggers' not in config or 'commands' not in config['triggers']:
                self.errors.append("Agent definition missing trigger commands")
                return False
            
            commands = config['triggers']['commands']
            if '@copilot qa walkthrough' not in commands:
                self.warnings.append("Primary trigger '@copilot qa walkthrough' not found in commands")
            
            self.successes.append("Agent definition validated successfully")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to parse agent definition: {e}")
            return False
    
    def validate_workflow(self) -> bool:
        """Validate GitHub Actions workflow."""
        workflow_file = self.repo_root / ".github/workflows/codebase-qa-walkthrough.yml"
        
        if not workflow_file.exists():
            self.errors.append(f"Workflow file not found: {workflow_file}")
            return False
        
        try:
            with open(workflow_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check workflow triggers (note: 'on' might be parsed as True in YAML)
            triggers = config.get('on') or config.get(True)
            if not triggers:
                self.errors.append("Workflow missing 'on' triggers")
                return False
            
            # Validate workflow_dispatch
            if 'workflow_dispatch' not in triggers:
                self.errors.append("Workflow missing 'workflow_dispatch' trigger")
                return False
            
            # Validate PR trigger
            if 'pull_request' not in triggers and 'pull_request_target' not in triggers:
                self.warnings.append("Workflow missing PR trigger (pull_request or pull_request_target)")
            
            # Validate issue_comment trigger for @copilot commands
            if 'issue_comment' not in triggers:
                self.warnings.append("Workflow missing 'issue_comment' trigger for @copilot commands")
            
            # Check jobs
            if 'jobs' not in config:
                self.errors.append("Workflow has no jobs defined")
                return False
            
            self.successes.append("Workflow configuration validated successfully")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to parse workflow file: {e}")
            return False
    
    def validate_documentation(self) -> bool:
        """Validate documentation files."""
        docs = [
            self.repo_root / ".github/agents/codebase-qa-walkthrough-agent/README.md",
            self.repo_root / ".github/workflows/CODEBASE_QA_WALKTHROUGH_USAGE.md"
        ]
        
        all_exist = True
        for doc in docs:
            if not doc.exists():
                self.errors.append(f"Documentation file not found: {doc}")
                all_exist = False
            else:
                # Check if file has content
                if doc.stat().st_size < 100:
                    self.warnings.append(f"Documentation file seems too small: {doc}")
        
        if all_exist:
            self.successes.append("Documentation files validated successfully")
        
        return all_exist
    
    def validate_tools(self) -> bool:
        """Validate availability of required tools."""
        required_tools = [
            ('python3', '--version'),
            ('pytest', '--version'),
            ('pylint', '--version'),
            ('mypy', '--version'),
        ]
        
        optional_tools = [
            ('bandit', '--version'),
            ('safety', '--version'),
            ('ruff', '--version'),
        ]
        
        all_required = True
        for tool, arg in required_tools:
            try:
                result = subprocess.run(
                    [tool, arg],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    self.errors.append(f"Required tool not available: {tool}")
                    all_required = False
                else:
                    self.successes.append(f"Tool available: {tool}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.errors.append(f"Required tool not available: {tool}")
                all_required = False
        
        for tool, arg in optional_tools:
            try:
                result = subprocess.run(
                    [tool, arg],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    self.warnings.append(f"Optional tool not available: {tool}")
                else:
                    self.successes.append(f"Optional tool available: {tool}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.warnings.append(f"Optional tool not available: {tool}")
        
        return all_required
    
    def validate_examples(self) -> bool:
        """Validate example files."""
        examples_dir = self.repo_root / ".github/agents/codebase-qa-walkthrough-agent/examples"
        
        if not examples_dir.exists():
            self.warnings.append(f"Examples directory not found: {examples_dir}")
            return False
        
        examples = list(examples_dir.glob("*.md"))
        if not examples:
            self.warnings.append("No example files found in examples directory")
            return False
        
        self.successes.append(f"Found {len(examples)} example file(s)")
        return True
    
    def print_results(self):
        """Print validation results."""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}QA Walkthrough Agent Validation Results{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        if self.successes:
            print(f"{GREEN}✅ Successes ({len(self.successes)}):{RESET}")
            for success in self.successes:
                print(f"  {GREEN}✓{RESET} {success}")
            print()
        
        if self.warnings:
            print(f"{YELLOW}⚠️  Warnings ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {warning}")
            print()
        
        if self.errors:
            print(f"{RED}❌ Errors ({len(self.errors)}):{RESET}")
            for error in self.errors:
                print(f"  {RED}✗{RESET} {error}")
            print()
        
        # Summary
        total_checks = len(self.successes) + len(self.warnings) + len(self.errors)
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"Total checks: {total_checks}")
        print(f"{GREEN}Passed: {len(self.successes)}{RESET}")
        print(f"{YELLOW}Warnings: {len(self.warnings)}{RESET}")
        print(f"{RED}Failed: {len(self.errors)}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        if self.errors:
            print(f"{RED}❌ Validation FAILED{RESET}")
            print(f"Please fix the errors above before using the QA Walkthrough Agent.\n")
            return False
        elif self.warnings:
            print(f"{YELLOW}⚠️  Validation PASSED with warnings{RESET}")
            print(f"The agent should work, but consider addressing the warnings.\n")
            return True
        else:
            print(f"{GREEN}✅ Validation PASSED{RESET}")
            print(f"QA Walkthrough Agent is ready to use!\n")
            return True
    
    def print_usage_instructions(self):
        """Print usage instructions."""
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}How to Use the QA Walkthrough Agent{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        print(f"{GREEN}1. Trigger via PR Comment:{RESET}")
        print(f"   Post a comment on any PR: {YELLOW}@copilot qa walkthrough{RESET}\n")
        
        print(f"{GREEN}2. Manual Workflow Trigger:{RESET}")
        print(f"   gh workflow run codebase-qa-walkthrough.yml \\")
        print(f"     --ref YOUR_BRANCH \\")
        print(f"     -f review_depth=comprehensive \\")
        print(f"     -f pr_number=YOUR_PR_NUMBER \\")
        print(f"     -f post_comment=true\n")
        
        print(f"{GREEN}3. Via GitHub Actions UI:{RESET}")
        print(f"   - Go to Actions tab")
        print(f"   - Select 'Codebase QA Walkthrough' workflow")
        print(f"   - Click 'Run workflow'")
        print(f"   - Fill in parameters and run\n")
        
        print(f"{GREEN}4. Automatic PR Trigger:{RESET}")
        print(f"   The workflow can be configured to run automatically on PRs")
        print(f"   by enabling the pull_request trigger in the workflow file.\n")
        
        print(f"{BLUE}{'='*60}{RESET}\n")
    
    def run_validation(self) -> bool:
        """Run all validation checks."""
        print(f"\n{BLUE}Starting QA Walkthrough Agent Validation...{RESET}\n")
        
        checks = [
            ("Agent Definition", self.validate_agent_definition),
            ("Workflow Configuration", self.validate_workflow),
            ("Documentation", self.validate_documentation),
            ("Required Tools", self.validate_tools),
            ("Example Files", self.validate_examples),
        ]
        
        for check_name, check_func in checks:
            print(f"Checking {check_name}...", end=" ")
            result = check_func()
            if result:
                print(f"{GREEN}✓{RESET}")
            else:
                print(f"{RED}✗{RESET}")
        
        results_ok = self.print_results()
        
        if results_ok:
            self.print_usage_instructions()
        
        return results_ok


def main():
    """Main entry point."""
    validator = QAWalkthroughValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
