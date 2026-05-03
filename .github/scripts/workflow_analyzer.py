#!/usr/bin/env python3
"""
Comprehensive GitHub Actions Workflow Analyzer
Analyzes all workflows in .github/workflows/ and cross-references with CI failure reports.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path("/home/runner/work/_codex_/_codex_")
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

class WorkflowAnalyzer:
    def __init__(self):
        self.workflows: dict[str, dict[str, Any]] = {}
        self.disabled_workflows: list[str] = []
        self.errors: dict[str, str] = {}

    def analyze_all_workflows(self):
        """Analyze all workflow files."""
        print("🔍 Scanning workflow directory...")

        # Active workflows
        for yml_file in WORKFLOWS_DIR.glob("*.yml"):
            if yml_file.name.endswith(('.disabled', '.alt', '.tombstone')):
                continue
            self.analyze_workflow(yml_file)

        for yaml_file in WORKFLOWS_DIR.glob("*.yaml"):
            if yaml_file.name.endswith(('.disabled', '.alt', '.tombstone')):
                continue
            self.analyze_workflow(yaml_file)

        # Disabled workflows
        for disabled in WORKFLOWS_DIR.glob("*.disabled"):
            self.disabled_workflows.append(disabled.name)
        for alt in WORKFLOWS_DIR.glob("*.alt"):
            self.disabled_workflows.append(alt.name)
        for tombstone in WORKFLOWS_DIR.glob("*.tombstone"):
            self.disabled_workflows.append(tombstone.name)

    def analyze_workflow(self, workflow_path: Path):
        """Analyze a single workflow file."""
        workflow_name = workflow_path.name

        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse YAML
            try:
                workflow_data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.errors[workflow_name] = f"YAML parse error: {e}"
                return

            if not workflow_data:
                self.errors[workflow_name] = "Empty workflow file"
                return

            # Check for guards
            is_guarded = self._check_guards(content, workflow_data)

            # Extract workflow info
            info = {
                'path': str(workflow_path.relative_to(REPO_ROOT)),
                'name': workflow_data.get('name', workflow_name),
                'guarded': is_guarded,
                'triggers': self._extract_triggers(workflow_data),
                'jobs': self._extract_jobs(workflow_data),
                'secrets': self._extract_secrets(content),
                'env_vars': self._extract_env_vars(workflow_data),
                'runners': self._extract_runners(workflow_data),
                'actions_used': self._extract_actions(workflow_data),
                'python_versions': self._extract_python_versions(workflow_data),
                'dependencies': self._extract_dependencies(content),
                'line_count': len(content.splitlines()),
                'has_docker': 'docker' in content.lower(),
                'has_uv': 'astral-sh/setup-uv' in content or 'uv pip' in content,
                'has_nox': 'nox' in content.lower(),
                'has_pytest': 'pytest' in content.lower(),
            }

            self.workflows[workflow_name] = info

        except Exception as e:
            self.errors[workflow_name] = f"Analysis error: {e}"

    def _check_guards(self, content: str, data: dict) -> bool:
        """Check if workflow has guards (if: false, etc.)."""
        # Check for global if: false
        if 'on' in data:
            on_triggers = data['on']
            if isinstance(on_triggers, dict):
                for trigger_type, trigger_config in on_triggers.items():
                    if isinstance(trigger_config, dict) and not trigger_config.get('if'):
                        return True

        # Check for job-level guards
        if 'jobs' in data:
            for job_name, job_config in data['jobs'].items():
                if isinstance(job_config, dict):
                    if_condition = job_config.get('if', '')
                    if if_condition in ['false', False] or 'false' in str(if_condition).lower():
                        return True

        # Check for commented workflow-dispatch
        if 'workflow_dispatch:' in content and '#' in content.split('workflow_dispatch:')[0].split('\n')[-1]:
            return True

        return False

    def _extract_triggers(self, data: dict) -> list[str]:
        """Extract workflow triggers."""
        triggers = []
        if 'on' in data:
            on_triggers = data['on']
            if isinstance(on_triggers, str):
                triggers.append(on_triggers)
            elif isinstance(on_triggers, list):
                triggers.extend(on_triggers)
            elif isinstance(on_triggers, dict):
                triggers.extend(on_triggers.keys())
        return triggers

    def _extract_jobs(self, data: dict) -> dict[str, dict]:
        """Extract job information."""
        jobs_info = {}
        if 'jobs' in data:
            for job_name, job_config in data['jobs'].items():
                if isinstance(job_config, dict):
                    jobs_info[job_name] = {
                        'runner': job_config.get('runs-on', 'unknown'),
                        'steps': len(job_config.get('steps', [])),
                        'needs': job_config.get('needs', []),
                        'if': job_config.get('if', None),
                        'timeout': job_config.get('timeout-minutes', None),
                    }
        return jobs_info

    def _extract_secrets(self, content: str) -> list[str]:
        """Extract secret references."""
        secrets = set()
        # Pattern: secrets.SECRET_NAME or ${{ secrets.SECRET_NAME }}
        patterns = [
            r'secrets\.([A-Z_][A-Z0-9_]*)',
            r'\$\{\{\s*secrets\.([A-Z_][A-Z0-9_]*)\s*\}\}',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content)
            secrets.update(matches)
        return sorted(list(secrets))

    def _extract_env_vars(self, data: dict) -> list[str]:
        """Extract environment variables."""
        env_vars = []
        if 'env' in data:
            env_vars.extend(data['env'].keys())
        return env_vars

    def _extract_runners(self, data: dict) -> list[str]:
        """Extract runner types."""
        runners = set()
        if 'jobs' in data:
            for job_name, job_config in data['jobs'].items():
                if isinstance(job_config, dict):
                    runner = job_config.get('runs-on')
                    if runner:
                        if isinstance(runner, str):
                            runners.add(runner)
                        elif isinstance(runner, list):
                            runners.update(runner)
        return sorted(list(runners))

    def _extract_actions(self, data: dict) -> list[str]:
        """Extract GitHub Actions used."""
        actions = set()
        if 'jobs' in data:
            for job_name, job_config in data['jobs'].items():
                if isinstance(job_config, dict) and 'steps' in job_config:
                    for step in job_config['steps']:
                        if isinstance(step, dict) and 'uses' in step:
                            action = step['uses']
                            # Extract action name (owner/repo@version)
                            if '@' in action:
                                action_name = action.split('@')[0]
                                actions.add(action_name)
        return sorted(list(actions))

    def _extract_python_versions(self, data: dict) -> list[str]:
        """Extract Python versions from matrix."""
        versions = set()
        if 'jobs' in data:
            for job_name, job_config in data['jobs'].items():
                if isinstance(job_config, dict):
                    strategy = job_config.get('strategy', {})
                    if isinstance(strategy, dict):
                        matrix = strategy.get('matrix', {})
                        if isinstance(matrix, dict):
                            python_versions = matrix.get('python-version', [])
                            if isinstance(python_versions, list):
                                versions.update([str(v) for v in python_versions])
                            elif python_versions:
                                versions.add(str(python_versions))
        return sorted(list(versions))

    def _extract_dependencies(self, content: str) -> dict[str, bool]:
        """Extract dependency information."""
        return {
            'docker': bool(re.search(r'docker (build|run|push)', content, re.IGNORECASE)),
            'pip': 'pip install' in content,
            'uv': 'uv pip' in content or 'astral-sh/setup-uv' in content,
            'nox': 'nox ' in content,
            'poetry': 'poetry install' in content,
            'npm': 'npm install' in content or 'npm ci' in content,
            'yarn': 'yarn install' in content,
            'apt': 'apt-get install' in content or 'apt install' in content,
            'cargo': 'cargo build' in content or 'cargo install' in content,
        }

    def generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics."""
        active_count = len(self.workflows)
        guarded_count = sum(1 for w in self.workflows.values() if w['guarded'])
        disabled_count = len(self.disabled_workflows)

        all_runners = set()
        all_actions = set()
        all_secrets = set()

        for workflow in self.workflows.values():
            all_runners.update(workflow['runners'])
            all_actions.update(workflow['actions_used'])
            all_secrets.update(workflow['secrets'])

        return {
            'total_workflows': active_count + disabled_count,
            'active_workflows': active_count,
            'guarded_workflows': guarded_count,
            'disabled_workflows': disabled_count,
            'parse_errors': len(self.errors),
            'unique_runners': sorted(list(all_runners)),
            'unique_actions': sorted(list(all_actions)),
            'unique_secrets': sorted(list(all_secrets)),
            'secrets_count': len(all_secrets),
        }

    def generate_json_report(self) -> str:
        """Generate JSON report."""
        report = {
            'summary': self.generate_summary(),
            'workflows': self.workflows,
            'disabled': self.disabled_workflows,
            'errors': self.errors,
        }
        return json.dumps(report, indent=2)

    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report."""
        summary = self.generate_summary()

        md = []
        md.append("# GitHub Actions Workflow Analysis Report")
        md.append("")
        md.append("**Generated**: Auto-analysis of `.github/workflows/`")
        md.append("**Repository**: `Aries-Serpent/_codex_`")
        md.append("")

        # Executive Summary
        md.append("## 📊 Executive Summary")
        md.append("")
        md.append(f"- **Total Workflows**: {summary['total_workflows']}")
        md.append(f"- **Active Workflows**: {summary['active_workflows']}")
        md.append(f"- **Guarded Workflows**: {summary['guarded_workflows']} (if: false or disabled)")
        md.append(f"- **Archived Workflows**: {summary['disabled_workflows']} (.disabled, .alt, .tombstone)")
        md.append(f"- **Parse Errors**: {summary['parse_errors']}")
        md.append(f"- **Unique Secrets**: {summary['secrets_count']}")
        md.append("")

        # Runner Types
        md.append("## 🖥️ Runner Types in Use")
        md.append("")
        for runner in summary['unique_runners']:
            count = sum(1 for w in self.workflows.values() if runner in w['runners'])
            md.append(f"- `{runner}`: {count} workflows")
        md.append("")

        # Top Actions
        md.append("## 🔧 Most Used GitHub Actions")
        md.append("")
        action_counts = defaultdict(int)
        for workflow in self.workflows.values():
            for action in workflow['actions_used']:
                action_counts[action] += 1

        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            md.append(f"- `{action}`: {count} workflows")
        md.append("")

        # Detailed Workflow Table
        md.append("## 📋 Detailed Workflow Analysis")
        md.append("")
        md.append("| Workflow | Status | Jobs | Triggers | Runner | Secrets | Dependencies | Priority |")
        md.append("|----------|--------|------|----------|--------|---------|--------------|----------|")

        # Sort workflows by name
        for workflow_name in sorted(self.workflows.keys()):
            info = self.workflows[workflow_name]

            status = "🔴 Guarded" if info['guarded'] else "✅ Active"
            jobs_count = len(info['jobs'])
            triggers = ", ".join(info['triggers'][:2])
            if len(info['triggers']) > 2:
                triggers += "..."
            runner = info['runners'][0] if info['runners'] else "unknown"
            secrets_count = len(info['secrets'])

            deps = []
            if info['has_docker']:
                deps.append("Docker")
            if info['has_uv']:
                deps.append("uv")
            if info['has_nox']:
                deps.append("nox")
            if info['has_pytest']:
                deps.append("pytest")
            deps_str = ", ".join(deps[:3]) if deps else "None"

            # Determine priority (placeholder)
            priority = self._determine_priority(workflow_name, info)

            md.append(f"| {workflow_name} | {status} | {jobs_count} | {triggers} | {runner} | {secrets_count} | {deps_str} | {priority} |")

        md.append("")

        # Disabled Workflows
        md.append("## 🗄️ Archived/Disabled Workflows")
        md.append("")
        for disabled in sorted(self.disabled_workflows):
            md.append(f"- `{disabled}`")
        md.append("")

        # Errors
        if self.errors:
            md.append("## ⚠️ Parse Errors")
            md.append("")
            for workflow_name, error in self.errors.items():
                md.append(f"- **{workflow_name}**: {error}")
            md.append("")

        # Secrets Usage
        md.append("## 🔐 Secrets Usage Analysis")
        md.append("")
        secret_usage = defaultdict(list)
        for workflow_name, info in self.workflows.items():
            for secret in info['secrets']:
                secret_usage[secret].append(workflow_name)

        md.append("| Secret Name | Used In | Count |")
        md.append("|-------------|---------|-------|")
        for secret in sorted(secret_usage.keys()):
            workflows = secret_usage[secret]
            count = len(workflows)
            workflows_str = ", ".join(workflows[:3])
            if count > 3:
                workflows_str += f", ... (+{count-3} more)"
            md.append(f"| `{secret}` | {workflows_str} | {count} |")
        md.append("")

        # Resource Requirements by Category
        md.append("## 💰 Resource Requirements by Category")
        md.append("")

        categories = self._categorize_workflows()

        for category, workflows in sorted(categories.items()):
            md.append(f"### {category} ({len(workflows)} workflows)")
            md.append("")
            for wf_name in sorted(workflows):
                info = self.workflows.get(wf_name)
                if info:
                    status_emoji = "🔴" if info['guarded'] else "✅"
                    md.append(f"- {status_emoji} **{wf_name}**")
                    md.append(f"  - Runners: {', '.join(info['runners'][:3])}")
                    md.append(f"  - Jobs: {len(info['jobs'])}")
                    md.append(f"  - Triggers: {', '.join(info['triggers'])}")
            md.append("")

        return "\n".join(md)

    def _determine_priority(self, workflow_name: str, info: dict) -> str:
        """Determine workflow priority level."""
        # Critical: CI/test workflows
        if any(x in workflow_name.lower() for x in ['ci', 'test', 'pr-checks', 'security']):
            return "🔴 Critical"

        # High: Build, deploy, release
        if any(x in workflow_name.lower() for x in ['build', 'deploy', 'release', 'publish']):
            return "🟠 High"

        # Medium: Automation, monitoring
        if any(x in workflow_name.lower() for x in ['automation', 'monitor', 'audit', 'scan']):
            return "🟡 Medium"

        # Low: Documentation, cleanup
        if any(x in workflow_name.lower() for x in ['doc', 'cleanup', 'cache', 'wiki']):
            return "🟢 Low"

        return "⚪ Unknown"

    def _categorize_workflows(self) -> dict[str, list[str]]:
        """Categorize workflows by function."""
        categories = defaultdict(list)

        for workflow_name, info in self.workflows.items():
            wf_lower = workflow_name.lower()

            if any(x in wf_lower for x in ['test', 'pytest', 'ci', 'pr-check']):
                categories['Testing & CI'].append(workflow_name)
            elif any(x in wf_lower for x in ['security', 'scan', 'codeql', 'bandit', 'semgrep']):
                categories['Security'].append(workflow_name)
            elif any(x in wf_lower for x in ['build', 'docker', 'deploy', 'publish', 'release']):
                categories['Build & Deploy'].append(workflow_name)
            elif any(x in wf_lower for x in ['doc', 'wiki', 'pages', 'mkdocs']):
                categories['Documentation'].append(workflow_name)
            elif any(x in wf_lower for x in ['cache', 'cleanup', 'archiv']):
                categories['Maintenance'].append(workflow_name)
            elif any(x in wf_lower for x in ['auth', 'secret', 'token', 'mfa']):
                categories['Authentication'].append(workflow_name)
            elif any(x in wf_lower for x in ['cognitive', 'agent', 'copilot']):
                categories['AI & Automation'].append(workflow_name)
            elif any(x in wf_lower for x in ['monitor', 'health', 'diagnostic']):
                categories['Monitoring'].append(workflow_name)
            else:
                categories['Other'].append(workflow_name)

        return categories


def main():
    analyzer = WorkflowAnalyzer()

    print("🚀 Starting workflow analysis...")
    analyzer.analyze_all_workflows()

    print(f"✅ Analyzed {len(analyzer.workflows)} active workflows")
    print(f"📁 Found {len(analyzer.disabled_workflows)} disabled workflows")
    print(f"⚠️  Encountered {len(analyzer.errors)} errors")

    # Generate reports
    json_report = analyzer.generate_json_report()
    md_report = analyzer.generate_markdown_report()

    # Save reports
    json_path = REPO_ROOT / "workflow_analysis.json"
    md_path = REPO_ROOT / "workflow_analysis.md"

    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_report)
    print(f"📄 JSON report saved to: {json_path}")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_report)
    print(f"📄 Markdown report saved to: {md_path}")

    print("\n✨ Analysis complete!")


if __name__ == '__main__':
    main()
