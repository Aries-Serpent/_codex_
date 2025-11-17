#!/usr/bin/env python3
"""Auto-fixer for markdown code fences.

Scans all markdown files and:
- Adds language tags to bare code fences
- Detects language from content heuristics
- Normalizes fence formatting
"""

import re
import sys
from pathlib import Path

# Language detection patterns (ordered by specificity)
LANG_HINT = {
    r"^\s*{[\s\n]*[\"']": "json",
    r"^\s*\[": "json",
    r"^\s*<\?xml": "xml",
    r"^\s*<!DOCTYPE html": "html",
    r"^\s*<[a-z]+[\s>]": "html",
    r"^\s*from\s+\w+\s+import": "python",
    r"^\s*import\s+\w+": "python",
    r"^\s*def\s+\w+\(": "python",
    r"^\s*class\s+\w+": "python",
    r"^\s*#\s*!/usr/bin/(env\s+)?python": "python",
    r"^\s*SELECT\s+": "sql",
    r"^\s*INSERT\s+INTO": "sql",
    r"^\s*CREATE\s+TABLE": "sql",
    r"^\s*\$\s+": "bash",
    r"^\s*sudo\s+": "bash",
    r"^\s*apt-get\s+": "bash",
    r"^\s*pip\s+install": "bash",
    r"^\s*npm\s+(install|run)": "bash",
    r"^\s*function\s+\w+\(": "javascript",
    r"^\s*const\s+\w+\s*=": "javascript",
    r"^\s*let\s+\w+\s*=": "javascript",
    r"^\s*var\s+\w+\s*=": "javascript",
    r"^\s*package\s+\w+": "go",
    r"^\s*func\s+\w+\(": "go",
    r"^\s*#\s*include\s+<": "c",
    r"^\s*\[tool\.": "toml",
    r"^\s*\[\w+\]": "ini",
    r"^\s*---\s*$": "yaml",
    r"^\s*\w+:\s*$": "yaml",
    r"^\s*-\s+\w+:": "yaml",
}


def detect_lang(block: str) -> str:
    """Detect language from code block content."""
    # Get first few non-empty lines
    lines = [line for line in block.splitlines()[:5] if line.strip()]
    head = "\n".join(lines)

    # Try pattern matching
    for pattern, lang in LANG_HINT.items():
        if re.search(pattern, head, re.I | re.M):
            return lang

    # Default to text for unknown
    return "text"


def fix_fence_in_file(filepath: Path, dry_run: bool = False) -> tuple[bool, int]:
    """Fix fences in a single markdown file.

    Returns:
        (changed, num_fixes) tuple
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, IOError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return False, 0

    original = content
    fixes = 0

    # Fix bare triple-backtick fences (no language tag)
    def replace_bare_fence(match):
        nonlocal fixes
        fence_marker = match.group(1)  # ``` or ~~~
        body = match.group(2)

        # Detect language from content
        lang = detect_lang(body)
        fixes += 1

        return f"{fence_marker}{lang}\n{body}\n{fence_marker}"

    # Match fences with optional language tag
    # This handles both ``` and ~~~ style fences
    fence_pattern = r"^(```|~~~)(\w*)\n(.*?)\n\1\s*$"

    def process_fence(match):
        fence_marker = match.group(1)
        existing_lang = match.group(2)
        body = match.group(3)

        if not existing_lang:  # No language tag
            nonlocal fixes
            lang = detect_lang(body)
            fixes += 1
            return f"{fence_marker}{lang}\n{body}\n{fence_marker}"

        # Has language tag, keep as is
        return match.group(0)

    content = re.sub(fence_pattern, process_fence, content, flags=re.MULTILINE | re.DOTALL)

    # Write back if changed
    if content != original and not dry_run:
        filepath.write_text(content, encoding="utf-8")
        return True, fixes

    return content != original, fixes


def main(root: str = ".", dry_run: bool = False, verbose: bool = False):
    """Scan and fix all markdown files under root directory."""
    root_path = Path(root).resolve()

    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist", file=sys.stderr)
        return 1

    total_files = 0
    total_changed = 0
    total_fixes = 0

    # Find all markdown files
    for md_file in root_path.rglob("*.md"):
        # Skip hidden directories and common exclude patterns
        if any(part.startswith(".") for part in md_file.parts):
            continue
        if "node_modules" in md_file.parts or "venv" in md_file.parts:
            continue

        total_files += 1
        changed, fixes = fix_fence_in_file(md_file, dry_run=dry_run)

        if changed:
            total_changed += 1
            total_fixes += fixes
            status = "Would fix" if dry_run else "Fixed"
            if verbose or dry_run:
                print(f"{status} {fixes} fence(s) in {md_file.relative_to(root_path)}")

    # Summary
    mode = "dry-run" if dry_run else "fixed"
    print(f"\nSummary ({mode}):")
    print(f"  Files scanned: {total_files}")
    print(f"  Files changed: {total_changed}")
    print(f"  Total fixes: {total_fixes}")

    return 0 if not dry_run or total_changed == 0 else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix markdown code fence language tags")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to scan (default: .)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without modifying files"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    sys.exit(main(args.root, dry_run=args.dry_run, verbose=args.verbose))
