#!/usr/bin/env python3
"""PR Follow-Up Prompt Generator - Comprehensive Edition"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class GitMetadataExtractor:
    """Extract metadata from git repository."""
    
    @staticmethod
    def get_branch() -> str:
        try:
            return subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                text=True, stderr=subprocess.PIPE
            ).strip()
        except subprocess.CalledProcessError as e:
            logger.debug(f"Failed to get branch name: {e.stderr if e.stderr else str(e)}")
            return os.environ.get('GITHUB_HEAD_REF', 'unknown-branch')
    
    @staticmethod
    def get_commit_sha() -> str:
        try:
            return subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                text=True, stderr=subprocess.PIPE
            ).strip()
        except subprocess.CalledProcessError as e:
            logger.debug(f"Failed to get commit SHA: {e.stderr if e.stderr else str(e)}")
            return os.environ.get('GITHUB_SHA', 'unknown')
    
    @staticmethod
    def get_recent_commits(count: int = 5) -> list[dict]:
        try:
            log_format = '%H|%s|%an|%ad'
            output = subprocess.check_output(
                ['git', 'log', f'-{count}', f'--format={log_format}', '--date=short'],
                text=True, stderr=subprocess.PIPE
            ).strip()
            
            commits = []
            for line in output.split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'sha': parts[0][:8],
                            'subject': parts[1],
                            'author': parts[2],
                            'date': parts[3],
                        })
            return commits
        except subprocess.CalledProcessError as e:
            logger.debug(f"Failed to get recent commits: {e.stderr if e.stderr else str(e)}")
            return []
    
    @staticmethod
    def get_modified_files() -> list[str]:
        try:
            output = subprocess.check_output(
                ['git', 'diff', '--name-only', 'origin/main...HEAD'],
                text=True, stderr=subprocess.PIPE
            ).strip()
            files = [f for f in output.split('\n') if f]
            if not files:
                output = subprocess.check_output(
                    ['git', 'diff', '--name-only', 'HEAD'],
                    text=True, stderr=subprocess.PIPE
                ).strip()
                files = [f for f in output.split('\n') if f]
            return files
        except subprocess.CalledProcessError as e:
            logger.debug(f"Failed to get modified files: {e.stderr if e.stderr else str(e)}")
            return []
    
    @staticmethod
    def get_commit_count() -> int:
        try:
            output = subprocess.check_output(
                ['git', 'rev-list', '--count', 'origin/main..HEAD'],
                text=True, stderr=subprocess.PIPE
            ).strip()
            return int(output) if output else 0
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.debug(f"Failed to get commit count: {e}")
            return 0


class PromptGenerator:
    """Generate follow-up prompts from templates."""
    
    def __init__(self, templates_dir: Path = Path('.github/copilot-prompts/templates')):
        self.templates_dir = templates_dir
        self.git = GitMetadataExtractor()
    
    def load_template(self, template_name: str) -> str:
        template_path = self.templates_dir / f'{template_name}.md'
        if not template_path.exists():
            template_path = self.templates_dir / 'pr-continuation.md'
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
        return template_path.read_text()
    
    def get_pr_metadata(self, pr_number: str) -> dict:
        return {
            'pr_number': pr_number,
            'branch': self.git.get_branch(),
            'commit_sha': self.git.get_commit_sha(),
            'pr_author': os.environ.get('GITHUB_ACTOR', 'unknown'),
            'pr_title': os.environ.get('PR_TITLE', f'PR #{pr_number}'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    
    def format_task_list(self, tasks: list[str] | None) -> str:
        if not tasks:
            return '- [ ] No tasks specified'
        return '\n'.join(f'- [ ] {task}' for task in tasks)
    
    def format_commits(self, commits: list[dict]) -> str:
        if not commits:
            return 'No recent commits'
        formatted = []
        for commit in commits:
            formatted.append(f"- [`{commit['sha']}`] {commit['subject']} ({commit['author']}, {commit['date']})")
        return '\n'.join(formatted)
    
    def format_files(self, files: list[str]) -> str:
        if not files:
            return 'No files modified'
        return '\n'.join(f'- `{file}`' for file in files)
    
    def generate(
        self,
        pr_number: str,
        template_name: str = 'pr-continuation',
        immediate_tasks: list[str] | None = None,
        validation_tasks: list[str] | None = None,
        future_tasks: list[str] | None = None,
        success_criteria: list[str] | None = None,
        commands: str = '',
        expected_outcomes: str = '',
        related_issues: str = '',
        **kwargs
    ) -> str:
        template = self.load_template(template_name)
        metadata = self.get_pr_metadata(pr_number)
        commits = self.git.get_recent_commits()
        modified_files = self.git.get_modified_files()
        commit_count = self.git.get_commit_count()
        
        immediate = self.format_task_list(immediate_tasks)
        validation = self.format_task_list(validation_tasks)
        future = self.format_task_list(future_tasks)
        
        replacements = {
            **metadata,
            'immediate_tasks': immediate,
            'validation_tasks': validation,
            'future_tasks': future,
            'checklist_items': self.format_task_list(kwargs.get('checklist', [])),
            'validation_criteria': '\n'.join(f'- {c}' for c in (success_criteria or [])),
            'commands': commands or '# No commands specified',
            'expected_outcomes': expected_outcomes or '- Outcome 1\n- Outcome 2',
            'related_issues': related_issues or 'N/A',
            'commit_count': str(commit_count),
            'completed_summary': self.format_commits(commits[:3]),
            'modified_files': self.format_files(modified_files),
            'validation_commands_p1': commands or 'echo "Add validation commands"',
            **kwargs
        }
        
        prompt = template
        for key, value in replacements.items():
            prompt = prompt.replace(f'{{{key}}}', str(value))
        
        return prompt
    
    def save(self, prompt: str, pr_number: str, output_dir: Path | None = None) -> Path:
        if output_dir is None:
            output_dir = Path('.github/copilot-prompts/active')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f'PR-{pr_number}-followup.md'
        output_file.write_text(prompt)
        return output_file


def main():
    parser = argparse.ArgumentParser(description='Generate Copilot follow-up prompt')
    parser.add_argument('pr_number', help='Pull request number')
    parser.add_argument('--template', default='pr-continuation', help='Template name')
    parser.add_argument('--immediate', nargs='+', metavar='TASK', help='Priority 1 tasks')
    parser.add_argument('--validation', nargs='+', metavar='TASK', help='Priority 2 tasks')
    parser.add_argument('--future', nargs='+', metavar='TASK', help='Priority 3 tasks')
    parser.add_argument('--criteria', nargs='+', metavar='CRITERION', help='Success criteria')
    parser.add_argument('--commands', help='Shell commands')
    parser.add_argument('--outcomes', help='Expected outcomes')
    parser.add_argument('--issues', help='Related issues')
    parser.add_argument('--phase', type=int, help='Current phase number')
    parser.add_argument('--total-phases', type=int, help='Total phases')
    parser.add_argument('--phase-name', help='Phase name')
    parser.add_argument('--output', type=Path, help='Output file path')
    parser.add_argument('--json-output', action='store_true', help='Output JSON metadata')
    
    args = parser.parse_args()
    
    try:
        generator = PromptGenerator()
        
        custom_vars = {}
        if args.phase:
            custom_vars['current_phase'] = args.phase
            custom_vars['phase_number'] = args.phase
        if args.total_phases:
            custom_vars['total_phases'] = args.total_phases
        if args.phase_name:
            custom_vars['current_phase_name'] = args.phase_name
        
        prompt = generator.generate(
            pr_number=args.pr_number,
            template_name=args.template,
            immediate_tasks=args.immediate,
            validation_tasks=args.validation,
            future_tasks=args.future,
            success_criteria=args.criteria,
            commands=args.commands,
            expected_outcomes=args.outcomes,
            related_issues=args.issues,
            **custom_vars
        )
        
        output_path = args.output or Path(f'.github/copilot-prompts/active/PR-{args.pr_number}-followup.md')
        saved_path = generator.save(prompt, args.pr_number, output_path.parent if args.output else None)
        
        print(f"✅ Follow-up prompt generated successfully")
        print(f"📄 Saved to: {saved_path}")
        print(f"PR Number: #{args.pr_number}")
        print(f"Template: {args.template}")
        print(f"Branch: {generator.git.get_branch()}")
        print(f"Commit: {generator.git.get_commit_sha()[:8]}")
        
        if args.json_output:
            metadata = generator.get_pr_metadata(args.pr_number)
            metadata['output_file'] = str(saved_path)
            metadata['template'] = args.template
            print(json.dumps(metadata, indent=2))
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
