#!/usr/bin/env python3
"""
Workflow Validation and Monitoring Script

This script validates consolidated workflows and tracks cache efficiency metrics.
Run after creating new consolidated workflows to ensure they work correctly.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml


class WorkflowValidator:
    """Validates consolidated workflows"""

    def __init__(self, workflows_dir: Path = Path(".github/workflows")):
        self.workflows_dir = workflows_dir
        self.consolidated_workflows = [
            "cache-suite.yml",
            "test-suite.yml",
            "ci-health-suite.yml",
            "security-scanning-suite.yml",
            "documentation-suite.yml",
        ]
        self.results = {}

    def validate_yaml_syntax(self) -> bool:
        """Validate YAML syntax of all consolidated workflows"""
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print("YAML SYNTAX VALIDATION")  # codeql[py/clear-text-logging-sensitive-data]
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]

        all_valid = True
        for workflow_file in self.consolidated_workflows:
            filepath = self.workflows_dir / workflow_file
            if not filepath.exists():
                print(f"⚠️  {workflow_file}: File not found")  # codeql[py/clear-text-logging-sensitive-data]
                continue

            try:
                with open(filepath) as f:
                    content = yaml.safe_load(f)

                # Validate required fields
                assert 'name' in content, "Missing 'name' field"
                assert 'on' in content, "Missing 'on' field"
                assert 'jobs' in content, "Missing 'jobs' field"

                job_count = len(content.get('jobs', {}))
                triggers = list(content['on'].keys()) if isinstance(content['on'], dict) else [str(content['on'])]

                print(f"✅ {workflow_file}")  # codeql[py/clear-text-logging-sensitive-data]
                print(f"   Name: {content['name']}")  # codeql[py/clear-text-logging-sensitive-data]
                print(f"   Jobs: {job_count}")  # codeql[py/clear-text-logging-sensitive-data]
                print(f"   Triggers: {', '.join(triggers)}")  # codeql[py/clear-text-logging-sensitive-data]

                self.results[workflow_file] = {
                    'syntax': 'valid',
                    'jobs': job_count,
                    'triggers': triggers
                }

            except Exception as e:
                print(f"❌ {workflow_file}: {e!s}")  # codeql[py/clear-text-logging-sensitive-data]
                all_valid = False
                self.results[workflow_file] = {
                    'syntax': 'invalid',
                    'error': str(e)
                }

        return all_valid

    def validate_workflow_structure(self) -> bool:
        """Validate workflow structure (jobs, steps, etc.)"""
        print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print("WORKFLOW STRUCTURE VALIDATION")  # codeql[py/clear-text-logging-sensitive-data]
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]

        all_valid = True
        for workflow_file in self.consolidated_workflows:
            filepath = self.workflows_dir / workflow_file
            if not filepath.exists():
                continue

            try:
                with open(filepath) as f:
                    content = yaml.safe_load(f)

                jobs = content.get('jobs', {})

                # Check each job structure
                for job_name, job in jobs.items():
                    if not isinstance(job, dict):
                        print(f"⚠️  {workflow_file}: Job '{job_name}' is not a dict")  # codeql[py/clear-text-logging-sensitive-data]
                        continue

                    # Validate job has steps or uses
                    if 'steps' not in job and 'uses' not in job:
                        print(f"⚠️  {workflow_file}: Job '{job_name}' has no steps or uses")  # codeql[py/clear-text-logging-sensitive-data]
                        all_valid = False

                    # Check for cached action usage
                    steps = job.get('steps', [])
                    uses_cached_action = False
                    for step in steps:
                        if isinstance(step, dict):
                            uses = step.get('uses', '')
                            if 'setup-python-cached' in uses:
                                uses_cached_action = True
                                break

                    if any('python' in str(step).lower() for step in steps) and not uses_cached_action:
                        print(f"ℹ️  {workflow_file}: Job '{job_name}' may benefit from cached Python action")  # codeql[py/clear-text-logging-sensitive-data]

                print(f"✅ {workflow_file}: Structure valid")  # codeql[py/clear-text-logging-sensitive-data]

            except Exception as e:
                print(f"❌ {workflow_file}: {e!s}")  # codeql[py/clear-text-logging-sensitive-data]
                all_valid = False

        return all_valid

    def check_workflow_call_support(self) -> bool:
        """Check if workflows support workflow_call for AI agents"""
        print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print("AI AGENT INTEGRATION CHECK (workflow_call)")  # codeql[py/clear-text-logging-sensitive-data]
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]

        all_supported = True
        for workflow_file in self.consolidated_workflows:
            filepath = self.workflows_dir / workflow_file
            if not filepath.exists():
                continue

            try:
                with open(filepath) as f:
                    content = yaml.safe_load(f)

                triggers = content.get('on', {})
                if isinstance(triggers, dict) and 'workflow_call' in triggers:
                    inputs = triggers['workflow_call'].get('inputs', {})
                    print(f"✅ {workflow_file}: workflow_call supported")  # codeql[py/clear-text-logging-sensitive-data]
                    if inputs:
                        print(f"   Inputs: {', '.join(inputs.keys())}")  # codeql[py/clear-text-logging-sensitive-data]
                else:
                    print(f"⚠️  {workflow_file}: workflow_call NOT supported")  # codeql[py/clear-text-logging-sensitive-data]
                    all_supported = False

            except Exception as e:
                print(f"❌ {workflow_file}: {e!s}")  # codeql[py/clear-text-logging-sensitive-data]
                all_supported = False

        return all_supported

    def generate_report(self, output_file: Path = Path("workflow-validation-report.json")):
        """Generate validation report"""
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'validated_workflows': len(self.consolidated_workflows),
            'results': self.results,
            'summary': {
                'total': len(self.consolidated_workflows),
                'valid': sum(1 for r in self.results.values() if r.get('syntax') == 'valid'),
                'invalid': sum(1 for r in self.results.values() if r.get('syntax') == 'invalid')
            }
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Validation report saved to {output_file}")  # codeql[py/clear-text-logging-sensitive-data]
        return report


class CacheMonitor:
    """Monitors cache efficiency metrics"""

    def __init__(self, repo: str, token: str = None):
        self.repo = repo
        self.token = token or self._get_github_token()
        self.headers = {'Authorization': f'Bearer {self.token}'}
        # nosemgrep: url-substring-check - trusted GitHub API base for workflow validation
        self.base_url = f'https://api.github.com/repos/{repo}'

    def _get_github_token(self) -> str:
        """Get GitHub token from environment"""
        token = os.environ.get('GITHUB_TOKEN', '')
        if not token:
            print(
                "⚠️  GITHUB_TOKEN is not set; GitHub API calls may fail due to lack of authentication.",
                file=sys.stderr,
            )
        return token

    def get_cache_usage(self) -> dict:
        """Get cache usage statistics"""
        print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print("CACHE USAGE ANALYSIS")  # codeql[py/clear-text-logging-sensitive-data]
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]

        try:
            # Get all caches
            response = requests.get(
                f'{self.base_url}/actions/caches',
                headers=self.headers,
                params={'per_page': 100},
                timeout=30,
            )
            response.raise_for_status()

            caches = response.json().get('actions_caches', [])

            # Analyze by tier
            tier_stats = {'live': [], 'common': [], 'ephemeral': [], 'other': []}

            for cache in caches:
                key = cache.get('key', '')
                cache.get('size_in_bytes', 0)
                cache.get('created_at', '')
                cache.get('last_accessed_at', '')

                if key.startswith('live-'):
                    tier_stats['live'].append(cache)
                elif key.startswith('common-'):
                    tier_stats['common'].append(cache)
                elif key.startswith('ephemeral-'):
                    tier_stats['ephemeral'].append(cache)
                else:
                    tier_stats['other'].append(cache)

            # Print statistics
            print(f"\n📊 Total caches: {len(caches)}")  # codeql[py/clear-text-logging-sensitive-data]
            print("\nCache Distribution by Tier:")  # codeql[py/clear-text-logging-sensitive-data]

            for tier, caches_list in tier_stats.items():
                if caches_list:
                    total_size = sum(c.get('size_in_bytes', 0) for c in caches_list)
                    size_mb = total_size / (1024 * 1024)
                    print(f"  {tier.upper()}: {len(caches_list)} caches, {size_mb:.2f} MB")  # codeql[py/clear-text-logging-sensitive-data]

            return {
                'total_caches': len(caches),
                'by_tier': {
                    tier: {
                        'count': len(caches_list),
                        'total_size_mb': sum(c.get('size_in_bytes', 0) for c in caches_list) / (1024 * 1024)
                    }
                    for tier, caches_list in tier_stats.items()
                }
            }

        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ Error fetching cache data: {error_type}")  # codeql[py/clear-text-logging-sensitive-data]
            return {}

    def analyze_workflow_performance(self, days: int = 7) -> dict:
        """Analyze workflow performance over last N days"""
        print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
        print(f"WORKFLOW PERFORMANCE (Last {days} days)")  # codeql[py/clear-text-logging-sensitive-data]
        print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]

        try:
            since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')

            response = requests.get(
                f'{self.base_url}/actions/runs',
                headers=self.headers,
                params={'created': f'>={since}', 'per_page': 100},
                timeout=30,
            )
            response.raise_for_status()

            runs = response.json().get('workflow_runs', [])

            # Analyze by workflow
            workflow_stats = {}
            for run in runs:
                workflow_name = run['name']
                status = run['conclusion']
                duration = 0

                if 'run_started_at' in run and 'updated_at' in run:
                    start = datetime.fromisoformat(run['run_started_at'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                    duration = (end - start).total_seconds()

                if workflow_name not in workflow_stats:
                    workflow_stats[workflow_name] = {
                        'total': 0,
                        'success': 0,
                        'failure': 0,
                        'durations': []
                    }

                workflow_stats[workflow_name]['total'] += 1
                if status == 'success':
                    workflow_stats[workflow_name]['success'] += 1
                elif status in ['failure', 'cancelled']:
                    workflow_stats[workflow_name]['failure'] += 1

                if duration > 0:
                    workflow_stats[workflow_name]['durations'].append(duration)

            # Print statistics for consolidated workflows
            print("\nConsolidated Workflow Performance:")  # codeql[py/clear-text-logging-sensitive-data]
            consolidated_names = [
                'Cache Management Suite',
                'Testing Suite',
                'CI/CD Health Suite',
                'Security Scanning Suite',
                'Documentation Suite'
            ]

            for workflow_name in consolidated_names:
                if workflow_name in workflow_stats:
                    stats = workflow_stats[workflow_name]
                    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0

                    print(f"\n  {workflow_name}:")  # codeql[py/clear-text-logging-sensitive-data]
                    print(f"    Runs: {stats['total']}")  # codeql[py/clear-text-logging-sensitive-data]
                    print(f"    Success Rate: {success_rate:.1f}%")  # codeql[py/clear-text-logging-sensitive-data]
                    print(f"    Avg Duration: {avg_duration/60:.1f} minutes")  # codeql[py/clear-text-logging-sensitive-data]

            return workflow_stats

        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ Error analyzing workflows: {error_type}")  # codeql[py/clear-text-logging-sensitive-data]
            return {}


def main():
    """Main validation and monitoring execution"""
    print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
    print("WORKFLOW CONSOLIDATION VALIDATION & MONITORING")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")  # codeql[py/clear-text-logging-sensitive-data]
    print("")  # codeql[py/clear-text-logging-sensitive-data]

    # Validate workflows
    validator = WorkflowValidator()

    syntax_valid = validator.validate_yaml_syntax()
    structure_valid = validator.validate_workflow_structure()
    agent_support = validator.check_workflow_call_support()

    # Generate report
    report = validator.generate_report()

    # Monitor cache (if GitHub token available)
    try:
        if os.environ.get('GITHUB_TOKEN'):
            # Determine repository to monitor:
            # 1) command-line argument (if provided)
            # 2) GITHUB_REPOSITORY environment variable (if set)
            # 3) default to the original hardcoded repository
            default_repo = 'Aries-Serpent/_codex_'
            cli_repo = sys.argv[1] if len(sys.argv) > 1 else None
            env_repo = os.environ.get('GITHUB_REPOSITORY')
            repo = cli_repo or env_repo or default_repo

            monitor = CacheMonitor(repo)
            cache_stats = monitor.get_cache_usage()
            workflow_stats = monitor.analyze_workflow_performance(days=7)

            report['cache_stats'] = cache_stats
            report['workflow_performance'] = {
                k: {
                    'total': v['total'],
                    'success_rate': (v['success'] / v['total'] * 100) if v['total'] > 0 else 0
                }
                for k, v in workflow_stats.items()
            }

            # Save updated report
            with open('workflow-validation-report.json', 'w') as f:
                json.dump(report, f, indent=2)
    except Exception as e:
        error_type = type(e).__name__
        print(f"\n⚠️  Cache monitoring skipped: {error_type}")  # codeql[py/clear-text-logging-sensitive-data]

    # Final summary
    print("\n" + "=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
    print("VALIDATION SUMMARY")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]
    print(f"✅ YAML Syntax: {'PASS' if syntax_valid else 'FAIL'}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"✅ Structure: {'PASS' if structure_valid else 'FAIL'}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"✅ AI Agent Support: {'PASS' if agent_support else 'FAIL'}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"\nTotal Workflows Validated: {report['summary']['total']}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"Valid: {report['summary']['valid']}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"Invalid: {report['summary']['invalid']}")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 70)  # codeql[py/clear-text-logging-sensitive-data]

    # Exit with appropriate code
    if not (syntax_valid and structure_valid):
        print("\n❌ Validation failed!")  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(1)
    else:
        print("\n✅ All validations passed!")  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(0)


if __name__ == '__main__':
    main()
