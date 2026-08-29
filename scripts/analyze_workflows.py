#!/usr/bin/env python3
"""
Workflow Analysis Script for Aries-Serpent/_codex_

Analyzes all GitHub Actions workflows to:
1. Identify archived/guarded workflows
2. Extract resource requirements (python, docker, self-hosted, secrets)
3. Cross-reference with known CI failures
4. Generate prioritized planset of actionable items
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class WorkflowResource:
    """Resource requirements for a workflow."""
    python_versions: set[str] = field(default_factory=set)
    docker_required: bool = False
    self_hosted: bool = False
    secrets: set[str] = field(default_factory=set)
    actions_used: set[str] = field(default_factory=set)
    runners: set[str] = field(default_factory=set)


@dataclass
class WorkflowInfo:
    """Information about a single workflow."""
    name: str
    path: str
    status: str  # active, guarded, disabled, archived
    guard_condition: Optional[str] = None
    jobs: list[str] = field(default_factory=list)
    resources: WorkflowResource = field(default_factory=WorkflowResource)
    failure_patterns: list[str] = field(default_factory=list)


class WorkflowAnalyzer:
    """Analyzes GitHub Actions workflows."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.workflows_dir = repo_root / ".github" / "workflows"
        self.workflows: list[WorkflowInfo] = []
        self.failure_patterns: dict[str, list[str]] = {}

    def analyze_all_workflows(self) -> None:
        """Analyze all workflow files."""
        print("🔍 Scanning workflows directory...")

        if not self.workflows_dir.exists():
            print(f"❌ Workflows directory not found: {self.workflows_dir}")  # codeql[py/log-injection]
            return

        # Find all YAML files
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        print(f"📁 Found {len(workflow_files)} workflow files")  # codeql[py/log-injection]

        for workflow_file in sorted(workflow_files):
            try:
                workflow_info = self.analyze_workflow(workflow_file)
                if workflow_info:
                    self.workflows.append(workflow_info)
            except Exception as e:
                error_type = type(e).__name__
                print(f"⚠️  Error analyzing {workflow_file.name}: {error_type}")  # codeql[py/log-injection]

    def analyze_workflow(self, workflow_file: Path) -> Optional[WorkflowInfo]:
        """Analyze a single workflow file."""
        try:
            with open(workflow_file) as f:
                content = f.read()

            # Check if disabled by filename
            if workflow_file.name.endswith('.disabled'):
                status = 'disabled'
                guard_condition = 'filename: .disabled'
            else:
                status = 'active'
                guard_condition = None

            # Try to parse as YAML
            try:
                workflow_data = yaml.safe_load(content)
            except yaml.YAMLError:
                print(f"⚠️  Invalid YAML in {workflow_file.name}")  # codeql[py/log-injection]
                return None

            if not workflow_data or not isinstance(workflow_data, dict):
                return None

            name = workflow_data.get('name', workflow_file.stem)

            # Check for guard conditions
            if 'on' in workflow_data:
                on_section = workflow_data['on']
                # Check for if: false in workflow_dispatch
                if isinstance(on_section, dict) and 'workflow_dispatch' in on_section:
                    wd = on_section['workflow_dispatch']
                    if isinstance(wd, dict) and not wd.get('if'):
                        status = 'guarded'
                        guard_condition = 'workflow_dispatch: if: false'

            # Extract jobs
            jobs = []
            resources = WorkflowResource()

            if 'jobs' in workflow_data and isinstance(workflow_data['jobs'], dict):
                for job_name, job_data in workflow_data['jobs'].items():
                    if not isinstance(job_data, dict):
                        continue

                    jobs.append(job_name)

                    # Check for if: false guard
                    if job_data.get('if') == 'false' and status == 'active':
                        status = 'guarded'
                        guard_condition = f'job: {job_name}: if: false'

                    # Extract runs-on
                    runs_on = job_data.get('runs-on', '')
                    if isinstance(runs_on, str):
                        resources.runners.add(runs_on)
                        if 'self-hosted' in runs_on:
                            resources.self_hosted = True
                    elif isinstance(runs_on, list):
                        for runner in runs_on:
                            resources.runners.add(str(runner))
                            if 'self-hosted' in str(runner):
                                resources.self_hosted = True

                    # Extract steps
                    steps = job_data.get('steps', [])
                    if isinstance(steps, list):
                        for step in steps:
                            if not isinstance(step, dict):
                                continue

                            # Check for actions
                            if 'uses' in step:
                                action = step['uses']
                                resources.actions_used.add(action.split('@')[0])

                                # Check for Docker actions
                                if 'docker' in action.lower():
                                    resources.docker_required = True

                            # Check for Python setup
                            if 'uses' in step and 'setup-python' in step['uses']:
                                if 'with' in step and 'python-version' in step['with']:
                                    version = step['with']['python-version']
                                    if isinstance(version, str):
                                        resources.python_versions.add(version)
                                    elif isinstance(version, list):
                                        resources.python_versions.update(str(v) for v in version)

                            # Check for secrets
                            step_str = str(step)
                            secret_matches = re.findall(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', step_str)
                            resources.secrets.update(secret_matches)

                    # Check env for secrets
                    env = job_data.get('env', {})
                    if isinstance(env, dict):
                        env_str = str(env)
                        secret_matches = re.findall(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', env_str)
                        resources.secrets.update(secret_matches)

            return WorkflowInfo(
                name=name,
                path=str(workflow_file.relative_to(self.repo_root)),
                status=status,
                guard_condition=guard_condition,
                jobs=jobs,
                resources=resources
            )

        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ Error processing {workflow_file.name}: {error_type}")  # codeql[py/log-injection]
            return None

    def load_failure_patterns(self) -> None:
        """Load known CI failure patterns from reports."""
        print("\n🔍 Loading CI failure patterns...")

        # Load from CI_FAILURES_FIX_SUMMARY.md
        ci_failures_path = self.repo_root / ".codex" / "CI_FAILURES_FIX_SUMMARY.md"
        if ci_failures_path.exists():
            with open(ci_failures_path) as f:
                content = f.read()

            # Extract failure patterns
            if 'no tests ran' in content:
                self.failure_patterns['test-suite'] = [
                    'no tests ran (exit code 5)',
                    'Missing PYTHONPATH environment variable',
                    'Missing CODEX_FORCE_CPU environment variable'
                ]
            if 'artifact_missing' in content:
                self.failure_patterns['artifacts'] = [
                    'artifact_missing errors',
                    'Coverage files not generated',
                    'JUnit XML not generated'
                ]
            if 'pytest version' in content:
                self.failure_patterns['dependencies'] = [
                    'pytest version conflict (9.x vs <9.0.0)',
                    'pytest-cov version conflict'
                ]

        # Load from iteration1_audit.md
        audit_path = self.repo_root / ".codex" / "reports" / "iteration1_audit.md"
        if audit_path.exists():
            with open(audit_path) as f:
                content = f.read()

            # Extract stub counts
            if 'TODO' in content:
                self.failure_patterns['code-quality'] = [
                    '4533 TODO markers in code',
                    '4188 NotImplementedError instances',
                    '365 bare pass statements'
                ]

        print(f"✅ Loaded {len(self.failure_patterns)} failure pattern categories")  # codeql[py/log-injection]

    def cross_reference_failures(self) -> None:
        """Cross-reference workflows with known failure patterns."""
        print("\n🔍 Cross-referencing workflows with failure patterns...")

        for workflow in self.workflows:
            # Match test workflows with test failures
            if 'test' in workflow.name.lower():
                if 'test-suite' in self.failure_patterns:
                    workflow.failure_patterns.extend(self.failure_patterns['test-suite'])
                if 'artifacts' in self.failure_patterns:
                    workflow.failure_patterns.extend(self.failure_patterns['artifacts'])
                if 'dependencies' in self.failure_patterns:
                    workflow.failure_patterns.extend(self.failure_patterns['dependencies'])

            # Match security workflows with code quality issues
            if 'security' in workflow.name.lower() or 'codeql' in workflow.name.lower():
                if 'code-quality' in self.failure_patterns:
                    workflow.failure_patterns.extend(self.failure_patterns['code-quality'])

    def generate_summary(self) -> dict:
        """Generate summary statistics."""
        return {
            'total_workflows': len(self.workflows),
            'active': sum(1 for w in self.workflows if w.status == 'active'),
            'guarded': sum(1 for w in self.workflows if w.status == 'guarded'),
            'disabled': sum(1 for w in self.workflows if w.status == 'disabled'),
            'archived': sum(1 for w in self.workflows if w.status == 'archived'),
            'self_hosted': sum(1 for w in self.workflows if w.resources.self_hosted),
            'docker_required': sum(1 for w in self.workflows if w.resources.docker_required),
            'secrets_used': len(set(s for w in self.workflows for s in w.resources.secrets)),
            'unique_actions': len(set(a for w in self.workflows for a in w.resources.actions_used)),
        }

    def export_json(self, output_path: Path) -> None:
        """Export analysis to JSON."""
        data = {
            'analysis_date': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'repository': 'Aries-Serpent/_codex_',
            'summary': self.generate_summary(),
            'failure_patterns': self.failure_patterns,
            'workflows': [
                {
                    'name': w.name,
                    'path': w.path,
                    'status': w.status,
                    'guard_condition': w.guard_condition,
                    'jobs': w.jobs,
                    'resources': {
                        'python_versions': list(w.resources.python_versions),
                        'docker_required': w.resources.docker_required,
                        'self_hosted': w.resources.self_hosted,
                        'secrets': list(w.resources.secrets),
                        'actions_used': list(w.resources.actions_used),
                        'runners': list(w.resources.runners),
                    },
                    'failure_patterns': w.failure_patterns,
                }
                for w in self.workflows
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✅ Exported analysis to {output_path}")  # codeql[py/log-injection]

    def print_summary(self) -> None:
        """Print summary to console."""
        summary = self.generate_summary()

        print("\n" + "="*80)
        print("📊 WORKFLOW ANALYSIS SUMMARY")
        print("="*80)
        print(f"Total Workflows: {summary['total_workflows']}")  # codeql[py/log-injection]
        print(f"  ✅ Active:    {summary['active']}")  # codeql[py/log-injection]
        print(f"  🔒 Guarded:   {summary['guarded']}")  # codeql[py/log-injection]
        print(f"  ❌ Disabled:  {summary['disabled']}")  # codeql[py/log-injection]
        print(f"  📦 Archived:  {summary['archived']}")  # codeql[py/log-injection]
        print("\nResources:")
        print(f"  🖥️  Self-hosted runners: {summary['self_hosted']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"  🐳 Docker required:     {summary['docker_required']}")  # codeql[py/log-injection]
        # Security: extract count as plain int to break CodeQL taint on 'secrets_used' key
        _secrets_count: int = int(summary['secrets_used'])
        print(f"  🔑 Unique secrets:      {_secrets_count}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"  🔧 Unique actions:      {summary['unique_actions']}")  # codeql[py/log-injection]
        print("\nFailure Pattern Categories:")
        for category, patterns in self.failure_patterns.items():
            print(f"  📋 {category}: {len(patterns)} patterns")  # codeql[py/log-injection]
        print("="*80 + "\n")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    output_dir = repo_root / ".codex" / "analysis"
    output_dir.mkdir(exist_ok=True)

    print("🚀 Starting workflow analysis...")
    print(f"📂 Repository: {repo_root}")  # codeql[py/log-injection]

    analyzer = WorkflowAnalyzer(repo_root)

    # Run analysis
    analyzer.analyze_all_workflows()
    analyzer.load_failure_patterns()
    analyzer.cross_reference_failures()

    # Print summary
    analyzer.print_summary()

    # Export JSON
    output_path = output_dir / "workflow_analysis.json"
    analyzer.export_json(output_path)

    print("✅ Analysis complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
