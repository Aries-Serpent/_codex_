#!/usr/bin/env python3
"""Batch-migrate all GitHub Actions workflows to use the unified
rescue-comment upsert pattern (S294).

What this script does
---------------------
For every .github/workflows/*.yml that contains a ``rescue-comment`` job:

1.  Replaces the inline Python / JavaScript rescue-comment step with a
    standardised two-step block:
      a. ``actions/checkout@v5``  (to make ``scripts/ci/post_rescue_comment.py``
         available on the runner)
      b. ``python scripts/ci/post_rescue_comment.py``  (canonical upsert logic)

2.  Standardises the ``env:`` block so every rescue-comment step exports
    exactly the vars required by the canonical script.

3.  Preserves the ``WORKFLOW_NAME`` value extracted from the original file.

4.  Preserves the ``if:`` guard, ``needs:``, ``permissions:``, and
    ``timeout-minutes:`` of the rescue-comment job — only the *steps* change.

After running this script all 67 workflows share the same upsert logic and
the same SHA-scoped marker, so multiple workflows failing on the same commit
all append into one comment thread instead of spamming separate threads.

Usage
-----
    python scripts/ci/migrate_rescue_comments.py [--dry-run] [--workflow FILE]

Options
-------
--dry-run       Print diffs without writing files.
--workflow FILE Only process a single workflow file (for testing).
--verbose       Show each file processed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent.parent / ".github" / "workflows"

# ── Canonical step template (inserted verbatim) ──────────────────────────────

_STEP_TEMPLATE_PR = """\
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.CODEX_MASTER_KEY || secrets.GITHUB_TOKEN }}}}
          fetch-depth: 1

      - name: Post or update rescue comment
        env:
          GH_TOKEN: ${{{{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}}}
          PR_NUMBER: ${{{{ github.event.pull_request.number }}}}
          REPO: ${{{{ github.repository }}}}
          COMMIT_SHA: ${{{{ github.event.pull_request.head.sha }}}}
          RUN_ID: ${{{{ github.run_id }}}}
          WORKFLOW_NAME: {workflow_name}
          RUN_URL: ${{{{ github.server_url }}}}/${{{{ github.repository }}}}/actions/runs/${{{{ github.run_id }}}}
          BRANCH: ${{{{ github.head_ref }}}}
        run: python scripts/ci/post_rescue_comment.py
"""

# Push-triggered variant — PR_NUMBER is omitted so the script looks it up.
_STEP_TEMPLATE_PUSH = """\
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.CODEX_MASTER_KEY || secrets.GITHUB_TOKEN }}}}
          fetch-depth: 1

      - name: Post or update rescue comment
        env:
          GH_TOKEN: ${{{{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}}}
          REPO: ${{{{ github.repository }}}}
          COMMIT_SHA: ${{{{ github.sha }}}}
          RUN_ID: ${{{{ github.run_id }}}}
          WORKFLOW_NAME: {workflow_name}
          RUN_URL: ${{{{ github.server_url }}}}/${{{{ github.repository }}}}/actions/runs/${{{{ github.run_id }}}}
          BRANCH: ${{{{ github.ref_name }}}}
        run: python scripts/ci/post_rescue_comment.py
"""

# Fallback workflow name when we can't extract one.
_DEFAULT_NAME = '"CI Workflow"'

def _extract_workflow_name(content: str) -> str:
    """Return the quoted WORKFLOW_NAME value, e.g. '"Test RAG"'."""
    # Try explicit env-block WORKFLOW_NAME first (most workflows)
    m = re.search(
        r'WORKFLOW_NAME\s*:\s*("(?:[^"\\]|\\.)*"'  # double-quoted
        r"|'(?:[^'\\]|\\.)*'"  # single-quoted
        r"|[^\n]+)",            # unquoted / expression
        content,
    )
    if m:
        val = m.group(1).strip()
        if val.startswith(('"', "'")):
            return val
        return f'"{val}"'
    # Inline Python assignment:  workflow  = "Branch Divergence Monitor"
    m2 = re.search(
        r"""(?:^|\n)\s*workflow\s*=\s*['"]([^'"]+)['"]""",
        content,
    )
    if m2:
        return f'"{m2.group(1)}"'
    # JS pattern:  workflowName = 'Test RAG';  or  const workflow = "…"
    m3 = re.search(
        r"""(?:workflowName|workflow_?[Nn]ame)\s*[=:]\s*['"]([^'"]+)['"]""",
        content,
    )
    if m3:
        return f'"{m3.group(1)}"'
    return _DEFAULT_NAME


def _has_rescue_comment_job(content: str) -> bool:
    return bool(
        re.search(r"^\s{2}rescue-comment(-push)?\s*:", content, re.MULTILINE)
    )


def _find_rescue_comment_job_bounds(lines: list[str]) -> tuple[int, int, bool]:
    """Return (start, end, is_push) line indices for the rescue-comment(-push) job."""
    start = -1
    is_push = False
    for i, line in enumerate(lines):
        if re.match(r"^  rescue-comment(-push)?\s*:", line):
            start = i
            is_push = bool(re.match(r"^  rescue-comment-push\s*:", line))
            break
    if start == -1:
        return -1, -1, False

    # The job ends at the next top-level job definition (2-space indent) or EOF.
    end = len(lines) - 1
    for i in range(start + 1, len(lines)):
        if re.match(r"^  [a-zA-Z]", lines[i]) and not re.match(r"^  #", lines[i]):
            end = i - 1
            break
    return start, end, is_push


def _build_replacement_job(
    original_lines: list[str],
    workflow_name: str,
    is_push: bool = False,
) -> list[str]:
    """Rebuild the rescue-comment job keeping metadata, replacing only steps."""
    template = _STEP_TEMPLATE_PUSH if is_push else _STEP_TEMPLATE_PR
    header: list[str] = []
    steps_start = -1
    for i, line in enumerate(original_lines):
        if re.match(r"^\s{4}steps\s*:", line):
            steps_start = i
            break
        header.append(line)

    if steps_start == -1:
        # Malformed job — return unchanged
        return original_lines

    # Ensure `    steps:` itself is in the header
    header.append(original_lines[steps_start])

    # Build the canonical steps block
    step_block = template.format(workflow_name=workflow_name)
    new_step_lines = [ln + "\n" for ln in step_block.splitlines()]

    return header + new_step_lines


def migrate_file(path: Path, dry_run: bool = False, verbose: bool = False) -> bool:
    """Migrate one workflow file.  Returns True if file was (would be) changed."""
    original = path.read_text(encoding="utf-8")

    if not _has_rescue_comment_job(original):
        return False

    workflow_name = _extract_workflow_name(original)
    lines = original.splitlines(keepends=True)

    start, end, is_push = _find_rescue_comment_job_bounds(lines)
    if start == -1:
        if verbose:
            print(f"  ⚠  Could not find rescue-comment job bounds in {path.name}")
        return False

    job_lines = lines[start : end + 1]
    new_job_lines = _build_replacement_job(job_lines, workflow_name, is_push=is_push)

    if job_lines == new_job_lines:
        if verbose:
            print(f"  ✓  {path.name} — already up-to-date")
        return False

    new_lines = lines[:start] + new_job_lines + lines[end + 1 :]
    new_content = "".join(new_lines)

    if dry_run:
        print(f"\n{'='*70}\nDRY-RUN: {path.name}  (workflow_name={workflow_name})")
        # Show a simple diff summary
        old_job = "".join(job_lines)
        new_job = "".join(new_job_lines)
        print(f"  OLD rescue-comment job: {len(old_job)} chars")
        print(f"  NEW rescue-comment job: {len(new_job)} chars")
        return True

    path.write_text(new_content, encoding="utf-8")
    if verbose:
        print(f"  ✅  {path.name}  (workflow_name={workflow_name})")
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workflow", metavar="FILE", help="Process single file only")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    files = [Path(args.workflow)] if args.workflow else sorted(WORKFLOWS_DIR.glob("*.yml"))

    changed = 0
    skipped = 0
    for f in files:
        try:
            was_changed = migrate_file(f, dry_run=args.dry_run, verbose=args.verbose)
        except (OSError, ValueError, KeyError) as exc:
            print(f"  ❌  {f.name}: {exc}", file=sys.stderr)
            skipped += 1
            continue
        except Exception as exc:  # noqa: BLE001 — unexpected error; log and skip
            print(f"  ❌  {f.name} (unexpected): {exc}", file=sys.stderr)
            skipped += 1
            continue
        if was_changed:
            changed += 1
        else:
            skipped += 1

    verb = "Would change" if args.dry_run else "Changed"
    print(
        f"\n{verb} {changed} workflow(s); {skipped} already up-to-date or skipped."
    )


if __name__ == "__main__":
    main()
