"""
Codemod: Fix unsafe subprocess usage

Transforms:
  subprocess.call(..., shell=False) → subprocess.run(..., shell=False, check=True)
  os.system(...) → subprocess.run([...], check=True)

Author: mbaetiong
Generated: 2025-12-17
Updated: 2025-12-21 - Now uses libcst for AST-based transformations

This module now uses libcst for robust AST-based transformations that preserve
formatting and handle edge cases correctly. The regex-based implementation has
been replaced with proper AST manipulation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple

# Import from the libcst-based implementation
try:
    from .fix_subprocess_libcst import transform_file as _transform_file_libcst
    HAS_LIBCST = True
except ImportError:
    HAS_LIBCST = False
    _transform_file_libcst = None

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def transform_file(file_path: str) -> Tuple[str, List[str]]:
    """
    Transform a single file to fix unsafe subprocess usage.

    Args:
        file_path: Path to the file to transform

    Returns:
        Tuple of (new_content, list_of_changes)
    """
    # Use libcst-based implementation if available
    if HAS_LIBCST and _transform_file_libcst:
        return _transform_file_libcst(file_path)
    
    # Fallback message - libcst should always be available
    logger.warning(
        "libcst not available for AST-based transformations. "
        "Install with: pip install 'codex[analysis]'"
    )
    return "", ["ERROR: libcst not available - cannot perform transformations"]


def main() -> None:
    """Main entry point for CLI usage."""
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python fix_subprocess.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    new_code, changes = transform_file(file_path)

    if changes and not changes[0].startswith("ERROR"):
        logger.info(f"✅ Made {len(changes)} changes:")
        for change in changes:
            logger.info(f"  - {change}")

        # Write back
        with open(file_path, "w") as f:
            f.write(new_code)
        logger.info(f"💾 Updated {file_path}")
    elif changes and changes[0].startswith("ERROR"):
        logger.error(changes[0])
        sys.exit(1)
    else:
        logger.info("No changes needed")


if __name__ == "__main__":
    main()
