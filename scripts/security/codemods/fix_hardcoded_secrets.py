"""
Codemod: Remove hardcoded secrets and move to environment variables

Transforms:
  API_KEY = "sk-xxxxx" → API_KEY = os.getenv("API_KEY")
  PASSWORD = "secret123" → PASSWORD = os.getenv("PASSWORD")

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Input validation on file paths
- Pattern matching with bounds
- Safe value detection (placeholders)
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

# Patterns that indicate secrets
SECRET_PATTERNS = [
    r'(?i)(api[_-]?key)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(secret[_-]?key)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(password)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(token)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(auth[_-]?token)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(access[_-]?key)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(private[_-]?key)\s*=\s*["\']([^"\']+)["\']',
    r'(?i)(client[_-]?secret)\s*=\s*["\']([^"\']+)["\']',
]

# Values that are clearly not secrets (placeholders, examples)
SAFE_PATTERNS = [
    r'^(your[_-]?|my[_-]?|example[_-]?|test[_-]?|dummy[_-]?|placeholder)',
    r'^(xxx+|yyy+|zzz+)$',
    r'^(changeme|replace|todo|fixme)$',
    r'^\$\{',  # Template variables
    r'^<.*>$',  # Angle bracket placeholders
]


def is_safe_value(value: str) -> bool:
    """Check if a value is clearly a placeholder, not a real secret."""
    if not value:
        return True
    
    value_lower = value.lower()
    
    for pattern in SAFE_PATTERNS:
        if re.match(pattern, value_lower):
            return True
    
    return False


def transform_file(file_path: str) -> Tuple[str, List[str], List[Tuple[str, str]]]:
    """
    Transform a file to use environment variables for secrets.
    
    Returns:
        Tuple of (new_content, changes, env_vars)
    """
    # Input validation (safeguard)
    if not file_path or not isinstance(file_path, str):
        return "", ["Invalid file path"], []
    
    path = Path(file_path)
    if not path.exists():
        return "", [f"File not found: {file_path}"], []
    
    # File size check (safeguard)
    if path.stat().st_size > MAX_FILE_SIZE:
        return "", [f"File too large: {file_path}"], []
    
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return "", [f"Error reading file: {e}"], []
    
    changes: List[str] = []
    env_vars: List[Tuple[str, str]] = []
    
    # Check if os import exists
    has_os_import = bool(re.search(r'^import os\b', content, re.MULTILINE))
    needs_os_import = False
    
    for pattern in SECRET_PATTERNS:
        def replace_secret(match: re.Match) -> str:
            nonlocal needs_os_import
            
            var_name = match.group(1)
            value = match.group(2)
            
            if is_safe_value(value):
                return match.group(0)
            
            # Convert to environment variable format
            env_var_name = var_name.upper().replace("-", "_")
            
            changes.append(f"Moved {var_name} to environment variable {env_var_name}")
            env_vars.append((env_var_name, value))
            needs_os_import = True
            
            return f'{var_name} = os.getenv("{env_var_name}")'
        
        content = re.sub(pattern, replace_secret, content)
    
    # Add os import if needed and not present
    if needs_os_import and not has_os_import:
        # Add import at the top of the file
        import_line = "import os\n"
        
        # Find the right place to insert (after other imports)
        import_match = re.search(r'^((?:import |from ).+\n)+', content, re.MULTILINE)
        if import_match:
            insert_pos = import_match.end()
            content = content[:insert_pos] + import_line + content[insert_pos:]
        else:
            content = import_line + content
        
        changes.append("Added 'import os'")
    
    return content, changes, env_vars


def generate_env_example(env_vars: List[Tuple[str, str]], output_path: Path) -> None:
    """Generate or update .env.example file."""
    existing_vars = set()
    
    if output_path.exists():
        with open(output_path) as f:
            for line in f:
                if "=" in line:
                    existing_vars.add(line.split("=")[0].strip())
    
    with open(output_path, "a") as f:
        for var_name, original_value in env_vars:
            if var_name not in existing_vars:
                # Use a placeholder, not the actual value
                f.write(f"\n# Original value had {len(original_value)} characters\n")
                f.write(f"{var_name}=your_{var_name.lower()}_here\n")


def main() -> None:
    """Main entry point."""
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("Usage: python fix_hardcoded_secrets.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    new_content, changes, env_vars = transform_file(file_path)
    
    if changes:
        logger.info(f"✅ Made {len(changes)} changes:")
        for change in changes:
            logger.info(f"  - {change}")
        
        with open(file_path, "w") as f:
            f.write(new_content)
        logger.info(f"💾 Updated {file_path}")
        
        if env_vars:
            env_example = Path(file_path).parent / ".env.example"
            generate_env_example(env_vars, env_example)
            logger.info(f"📝 Updated {env_example}")
    else:
        logger.info("No changes needed")


if __name__ == "__main__":
    main()
