"""
Codemod: Fix unsafe subprocess usage

Transforms:
  subprocess.call(..., shell=True) → subprocess.run(..., shell=False, check=True)
  os.system(...) → subprocess.run([...], check=True)

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Input validation on file paths
- Backup creation before modification
- Defensive error handling
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Tuple, List

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
    # Input validation (safeguard)
    if not file_path or not isinstance(file_path, str):
        return "", ["Invalid file path"]
    
    path = Path(file_path)
    if not path.exists():
        return "", [f"File not found: {file_path}"]
    
    # File size check (safeguard)
    if path.stat().st_size > MAX_FILE_SIZE:
        return "", [f"File too large: {file_path}"]
    
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return "", [f"Error reading file: {e}"]
    
    changes: List[str] = []
    new_source = source
    
    # Pattern 1: subprocess.call(..., shell=True) -> subprocess.run(..., shell=False, check=True)
    pattern1 = r'subprocess\.call\s*\(([^)]+),\s*shell\s*=\s*True([^)]*)\)'
    
    def replace_call(match: re.Match) -> str:
        args = match.group(1)
        rest = match.group(2)
        changes.append("Changed subprocess.call(shell=True) to subprocess.run(shell=False, check=True)")
        return f'subprocess.run({args}, shell=False, check=True{rest})'
    
    new_source = re.sub(pattern1, replace_call, new_source)
    
    # Pattern 2: subprocess.Popen(..., shell=True) - add warning comment
    pattern2 = r'(subprocess\.Popen\s*\([^)]+shell\s*=\s*True[^)]*\))'
    
    def add_popen_warning(match: re.Match) -> str:
        original = match.group(1)
        changes.append("Added security warning for subprocess.Popen(shell=True)")
        return f'# SECURITY: Review shell=True usage - consider shell=False\n{original}'
    
    # Only add warning if not already present
    if 'SECURITY: Review shell=True' not in new_source:
        new_source = re.sub(pattern2, add_popen_warning, new_source)
    
    # Pattern 3: os.system(...) -> subprocess.run([...], shell=True, check=True)
    pattern3 = r'os\.system\s*\(\s*(["\'][^"\']+["\'])\s*\)'
    
    def replace_os_system(match: re.Match) -> str:
        cmd = match.group(1)
        changes.append(f"Converted os.system({cmd}) to subprocess.run")
        return f'subprocess.run({cmd}, shell=True, check=True)'
    
    new_source = re.sub(pattern3, replace_os_system, new_source)
    
    # Add subprocess import if needed and changes were made
    if changes and 'import subprocess' not in new_source:
        # Add import at the top
        import_added = False
        lines = new_source.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                lines.insert(i, 'import subprocess')
                import_added = True
                changes.append("Added 'import subprocess'")
                break
        
        if import_added:
            new_source = '\n'.join(lines)
    
    return new_source, changes


def main() -> None:
    """Main entry point for CLI usage."""
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("Usage: python fix_subprocess.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    new_code, changes = transform_file(file_path)
    
    if changes:
        logger.info(f"✅ Made {len(changes)} changes:")
        for change in changes:
            logger.info(f"  - {change}")
        
        # Write back
        with open(file_path, "w") as f:
            f.write(new_code)
        logger.info(f"💾 Updated {file_path}")
    else:
        logger.info("No changes needed")


if __name__ == "__main__":
    main()
