#!/usr/bin/env python3
"""
Generate Pr Followup

Purpose:
    Generates pr_followup

Usage:
    python scripts/generate_pr_followup.py [options]

    Examples:
    $ python scripts/generate_pr_followup.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
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
        """Get list of modified files, handling different git configurations."""
        try:
            # Try to get upstream tracking branch
            try:
                upstream = subprocess.check_output(
                    ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
                    text=True, stderr=subprocess.PIPE
                ).strip()
            except subprocess.CalledProcessError:
                # Fallback to origin/main or GITHUB_BASE_REF if in CI
                base_ref = os.environ.get('GITHUB_BASE_REF', 'main')
                try:
                    remote = subprocess.check_output(
                        ['git', 'remote'], text=True, stderr=subprocess.PIPE
                    ).strip().split('\n')[0] or 'origin'
                except subprocess.CalledProcessError:
                    remote = 'origin'
                upstream = f"{remote}/{base_ref}"

            output = subprocess.check_output(
                ['git', 'diff', '--name-only', f'{upstream}...HEAD'],
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
        """Get commit count, handling different git configurations."""
        try:
            # Try to get upstream tracking branch
            try:
                upstream = subprocess.check_output(
                    ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
                    text=True, stderr=subprocess.PIPE
                ).strip()
            except subprocess.CalledProcessError:
                # Fallback to origin/main or GITHUB_BASE_REF if in CI
                base_ref = os.environ.get('GITHUB_BASE_REF', 'main')
                try:
                    remote = subprocess.check_output(
                        ['git', 'remote'], text=True, stderr=subprocess.PIPE
                    ).strip().split('\n')[0] or 'origin'
                except subprocess.CalledProcessError:
                    remote = 'origin'
                upstream = f"{remote}/{base_ref}"

            output = subprocess.check_output(
                ['git', 'rev-list', '--count', f'{upstream}..HEAD'],
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
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    # Sentinel strings that indicate a section has only placeholder content.
    _PLACEHOLDER_MARKERS: tuple[str, ...] = (
        '- [ ] No tasks specified',
        'echo "Add validation commands"',
        '# No commands specified',
    )

    def _section_is_placeholder(self, text: str) -> bool:
        """Return True when *text* consists entirely of placeholder content."""
        stripped = text.strip()
        return any(marker in stripped for marker in self._PLACEHOLDER_MARKERS)

    def _extract_existing_tasks(self, existing_path: Path) -> dict[str, str]:
        """
        Parse *existing_path* and return the raw text of each task section
        keyed by ``'immediate'``, ``'validation'``, ``'future'``, and
        ``'validation_commands_p1'``.

        Returns an empty dict when the file does not exist or every section is
        still at its placeholder default.
        """
        if not existing_path.exists():
            return {}

        content = existing_path.read_text()
        preserved: dict[str, str] = {}

        # ── Priority 1 (immediate tasks + inline validation block) ────────────
        p1_match = re.search(
            r'### Priority 1: Immediate Tasks.*?\n(.*?)(?=\n### Priority 2:|\Z)',
            content, re.DOTALL,
        )
        if p1_match:
            p1_body = p1_match.group(1)
            # Split off the ```bash … ``` validation sub-block
            cmd_match = re.search(r'```bash\n(.*?)```', p1_body, re.DOTALL)
            if cmd_match:
                commands = cmd_match.group(1).strip()
                tasks_only = p1_body[:p1_body.index('**Validation**')].strip() if '**Validation**' in p1_body else p1_body.strip()
                if not self._section_is_placeholder(tasks_only):
                    preserved['immediate'] = tasks_only
                if not self._section_is_placeholder(commands):
                    preserved['validation_commands_p1'] = commands
            else:
                if not self._section_is_placeholder(p1_body.strip()):
                    preserved['immediate'] = p1_body.strip()

        # ── Priority 2 ────────────────────────────────────────────────────────
        p2_match = re.search(
            r'### Priority 2: Follow-Up Validation.*?\n(.*?)(?=\n### Priority 3:|\Z)',
            content, re.DOTALL,
        )
        if p2_match:
            body = p2_match.group(1).strip()
            if not self._section_is_placeholder(body):
                preserved['validation'] = body

        # ── Priority 3 ────────────────────────────────────────────────────────
        p3_match = re.search(
            r'### Priority 3: Future Enhancements.*?\n(.*?)(?=\n---|\Z)',
            content, re.DOTALL,
        )
        if p3_match:
            body = p3_match.group(1).strip()
            if not self._section_is_placeholder(body):
                preserved['future'] = body

        return preserved

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
        output_dir: Path | None = None,
        **kwargs
    ) -> str:
        template = self.load_template(template_name)
        metadata = self.get_pr_metadata(pr_number)
        commits = self.git.get_recent_commits()
        modified_files = self.git.get_modified_files()
        commit_count = self.git.get_commit_count()

        # ── Preserve real task content written by agents/humans ──────────────
        # If the existing follow-up file already contains non-placeholder task
        # sections (Priority 1/2/3), keep them.  Only fall back to the
        # caller-supplied tasks (or the default placeholder) when the sections
        # are still at their generated default.
        resolved_dir = output_dir or Path('.github/copilot-prompts/active')
        existing_path = resolved_dir / f'PR-{pr_number}-followup.md'
        preserved = self._extract_existing_tasks(existing_path)

        immediate = preserved.get('immediate') or self.format_task_list(immediate_tasks)
        validation = preserved.get('validation') or self.format_task_list(validation_tasks)
        future = preserved.get('future') or self.format_task_list(future_tasks)
        validation_cmds = (
            preserved.get('validation_commands_p1')
            or commands
            or (
                'python -m ruff check src/ tests/ --output-format=concise\n'
                'python scripts/ci/mypy_baseline.py --require-baseline\n'
                'python scripts/ci/auto_fix_common_issues.py --check-only\n'
                'python scripts/ci/sync_tracked_files.py --fix'
            )
        )

        if preserved:
            logger.info(
                "Preserved existing task sections in PR-%s follow-up "
                "(sections: %s)", pr_number, ', '.join(preserved)
            )

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
            'validation_commands_p1': validation_cmds,
            **kwargs
        }

        prompt = template
        for key, value in replacements.items():
            prompt = prompt.replace(f'{{{key}}}', str(value))

        return prompt

    def has_real_content(self, pr_number: str, output_dir: Path | None = None) -> bool:
        """Return True if the follow-up file already contains non-placeholder content.

        Used by the workflow guard to skip regeneration when an agent/human has
        written real tasks into the file — preventing automated overwrites.
        """
        resolved_dir = output_dir or Path('.github/copilot-prompts/active')
        existing_path = resolved_dir / f'PR-{pr_number}-followup.md'
        preserved = self._extract_existing_tasks(existing_path)
        return bool(preserved)

    def save(self, prompt: str, pr_number: str, output_dir: Path | None = None) -> Path:
        if output_dir is None:
            output_dir = Path('.github/copilot-prompts/active')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f'PR-{pr_number}-followup.md'
        # Safety guard: if the file already has real (non-placeholder) content
        # that was written by an agent/human session, do NOT overwrite it.
        # The generate() method has already merged the preserved sections back
        # into `prompt`, so writing is safe — but if generate() was called with
        # only placeholder tasks we must not clobber the file.
        if output_file.exists():
            existing = self._extract_existing_tasks(output_file)
            if existing:
                # Verify the new prompt also carries the preserved sections by
                # checking that at least one preserved block is still present.
                first_preserved = next(iter(existing.values()))
                if first_preserved not in prompt:
                    logger.warning(
                        "PR-%s follow-up already has real task content — "
                        "skipping overwrite to protect agent/human changes.",
                        pr_number,
                    )
                    return output_file
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
    parser.add_argument(
        '--check-real-content', action='store_true',
        help=(
            'Exit 0 with "SKIP" message when the file already has non-placeholder content. '
            'Exit 2 when placeholder/missing (indicating regeneration is needed). '
            'Does NOT write any files. Intended for CI workflow pre-checks.'
        ),
    )

    args = parser.parse_args()

    try:
        generator = PromptGenerator()

        output_path = args.output or Path(f'.github/copilot-prompts/active/PR-{args.pr_number}-followup.md')
        resolved_output_dir = output_path.parent if args.output else None

        # --check-real-content: probe mode — no writes, used by workflow guard.
        if args.check_real_content:
            if generator.has_real_content(args.pr_number, resolved_output_dir):
                print(f"SKIP: PR-{args.pr_number}-followup.md already has real task content — workflow will NOT overwrite.")
                return 0  # 0 = skip regeneration
            print(f"REGENERATE: PR-{args.pr_number}-followup.md is missing or placeholder-only.")
            return 2  # 2 = needs regeneration

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
            output_dir=resolved_output_dir,
            **custom_vars
        )

        saved_path = generator.save(prompt, args.pr_number, resolved_output_dir)

        print("✅ Follow-up prompt generated successfully")
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
