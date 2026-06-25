"""Helper utilities for tests dealing with PR #3248 documentation refactoring.

This module provides utilities for tests to handle the documentation refactoring
introduced in PR #3248, which added intentional broken link markers:
- <!-- BROKEN ANCHOR: ... --> for invalid/missing anchors
- <!-- BROKEN: ... --> for missing files

These utilities allow tests to:
1. Detect intentionally broken links/anchors
2. Filter out broken markers before content parsing
3. Resolve old documentation paths to new locations

Usage:
    from tests.utils.doc_refactor_helpers import is_intentionally_broken_link

    if is_intentionally_broken_link(file_path, link):
        pytest.skip(f"Intentionally broken link: {link}")
"""

import re
from pathlib import Path
from typing import Optional

# Path mappings for files moved/renamed in PR #3248
# Format: {"old/path.md": "new/path.md"}
DOC_PATH_MAPPINGS: dict[str, str] = {
    # Add mappings as identified during test fixing
    # Example:
    # ".codex/OLD_NAME.md": ".codex/new/location/NEW_NAME.md"
}


def is_intentionally_broken_link(file_path: Path, link: str) -> bool:
    """Check if a link is intentionally marked as broken in the documentation.

    Args:
        file_path: Path to the file containing the link
        link: The link text/URL to check

    Returns:
        True if the link is near a <!-- BROKEN --> or <!-- BROKEN ANCHOR: --> marker

    Example:
        >>> is_intentionally_broken_link(Path("doc.md"), "[text](#missing-anchor)")
        True  # if the link is near a <!-- BROKEN ANCHOR: #missing-anchor --> comment
    """
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError) as _err:
        return False

    link_index = content.find(link)
    if link_index == -1:
        return False

    # Check surrounding 200 chars for broken markers
    context_start = max(0, link_index - 200)
    context_end = min(len(content), link_index + 200)
    context = content[context_start:context_end]

    return "<!-- BROKEN" in context or "BROKEN ANCHOR" in context


def filter_broken_markers(content: str) -> str:
    """Remove intentional broken markers from content before parsing.

    This is useful for tests that parse markdown content and would otherwise
    be confused by the HTML comments indicating broken links.

    Args:
        content: Markdown content potentially containing broken markers

    Returns:
        Content with all <!-- BROKEN ... --> comments removed

    Example:
        >>> content = "# Title\\n<!-- BROKEN ANCHOR: #missing -->\\nContent"
        >>> filter_broken_markers(content)
        '# Title\\n\\nContent'
    """
    # Remove <!-- BROKEN ANCHOR: ... --> comments
    content = re.sub(r"<!--\s*BROKEN\s+ANCHOR:.*?-->", "", content, flags=re.DOTALL | re.IGNORECASE)

    # Remove <!-- BROKEN: ... --> comments
    return re.sub(r"<!--\s*BROKEN:.*?-->", "", content, flags=re.DOTALL | re.IGNORECASE)


def resolve_doc_path(old_path: str, repo_root: Optional[Path] = None) -> Optional[Path]:
    """Resolve old documentation path to new path after PR #3248 refactoring.

    Args:
        old_path: The old path to resolve (e.g., ".codex/OLD_NAME.md")
        repo_root: Optional repository root path. If None, uses current working directory.

    Returns:
        Path object if the resolved path exists, None otherwise

    Example:
        >>> resolve_doc_path(".codex/OLD_NAME.md")
        Path(".codex/new/location/NEW_NAME.md")  # if file was moved
    """
    if repo_root is None:
        repo_root = Path.cwd()

    # Try the mapping first
    new_path_str = DOC_PATH_MAPPINGS.get(old_path, old_path)
    new_path = repo_root / new_path_str

    # Return path if it exists
    if new_path.exists():
        return new_path

    # Try the old path directly
    old_path_obj = repo_root / old_path
    if old_path_obj.exists():
        return old_path_obj

    return None


def check_for_broken_marker_in_parent(parent_dir: Path, filename: str) -> bool:
    """Check if a file is marked as broken in parent directory documentation.

    Some files may be listed as broken in parent directory README or index files.
    This function checks for such markers.

    Args:
        parent_dir: Parent directory path
        filename: Name of the file to check for broken markers

    Returns:
        True if the file is marked as broken in parent documentation

    Example:
        >>> check_for_broken_marker_in_parent(Path(".codex/"), "MISSING_FILE.md")
        True  # if .codex/README.md contains <!-- BROKEN: MISSING_FILE.md -->
    """
    # Check common parent documentation files
    for doc_file in ["README.md", "INDEX.md", "index.md"]:
        doc_path = parent_dir / doc_file
        if not doc_path.exists():
            continue

        try:
            content = doc_path.read_text(encoding="utf-8", errors="ignore")
            # Look for broken markers mentioning this filename
            if "<!-- BROKEN:" in content and filename in content:
                return True
        except (IOError, OSError) as _err:
            continue

    return False


def is_known_broken_reference(doc_ref: str) -> bool:
    """Check if doc reference is known to be intentionally broken in PR #3248.

    Maintains a list of files/paths that are known to be intentionally broken
    and documented as such.

    Args:
        doc_ref: Documentation reference path

    Returns:
        True if this is a known broken reference

    Example:
        >>> is_known_broken_reference(".codex/OLD_FILE_REMOVED.md")
        True
    """
    # List of known broken references from PR #3248
    # These are intentionally broken and documented
    known_broken = [
        # Add paths as identified during PR #3248 analysis
        # Example:
        # ".codex/OLD_FILE_REMOVED.md",
        # ".codex/archive/DEPRECATED_DOC.md",
    ]

    return any(doc_ref.endswith(broken) or broken in doc_ref for broken in known_broken)


def extract_anchor_from_link(link: str) -> Optional[str]:
    """Extract anchor ID from a markdown link.

    Args:
        link: Markdown link (e.g., "[text](#anchor)" or "[text](file.md#anchor)")

    Returns:
        Anchor ID if present, None otherwise

    Example:
        >>> extract_anchor_from_link("[text](#my-anchor)")
        'my-anchor'
        >>> extract_anchor_from_link("[text](file.md#section-1)")
        'section-1'
    """
    # Match patterns like [text](#anchor) or [text](file.md#anchor)
    match = re.search(r"\(([^)]*#([^)]+))\)", link)
    if match:
        return match.group(2)

    # Match just #anchor
    match = re.search(r"#([a-z0-9\-_]+)", link)
    if match:
        return match.group(1)

    return None
