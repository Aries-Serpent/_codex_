#!/usr/bin/env python3
"""
Automated Script Documentation Header Generator

Purpose:
    Adds comprehensive documentation headers to Python scripts
    that currently lack them.

Usage:
    python scripts/add_script_headers.py [script_path|--all]
    
    Examples:
    $ python scripts/add_script_headers.py scripts/some_script.py
    $ python scripts/add_script_headers.py --all

Author: Codex Automation
Last Updated: 2026-01-16
"""

import sys
import re
from pathlib import Path
from typing import Optional

HEADER_TEMPLATE = '''"""
{title}

Purpose:
    {purpose}

Usage:
    python {script_path} [options]
    
    Examples:
    $ python {script_path} --help

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

'''

def infer_purpose(script_path: Path, content: str) -> str:
    """
    Infer the purpose of a script from its name and content.
    
    Args:
        script_path: Path to the script
        content: Script content
        
    Returns:
        Inferred purpose description
    """
    name = script_path.stem
    
    # Common patterns
    if 'test' in name:
        return f"Test script for {name.replace('test_', '')}"
    elif 'generate' in name:
        return f"Generates {name.replace('generate_', '')}"
    elif 'analyze' in name or 'analyse' in name:
        return f"Analyzes {name.replace('analyze_', '').replace('analyse_', '')}"
    elif 'validate' in name:
        return f"Validates {name.replace('validate_', '')}"
    elif 'migrate' in name:
        return f"Migration script for {name.replace('migrate_', '')}"
    elif 'setup' in name:
        return f"Setup script for {name.replace('setup_', '')}"
    elif 'run' in name:
        return f"Runs {name.replace('run_', '')}"
    elif 'build' in name:
        return f"Builds {name.replace('build_', '')}"
    elif 'deploy' in name:
        return f"Deploys {name.replace('deploy_', '')}"
    elif 'sync' in name:
        return f"Synchronizes {name.replace('sync_', '')}"
    elif 'update' in name:
        return f"Updates {name.replace('update_', '')}"
    elif 'init' in name:
        return f"Initializes {name.replace('init_', '')}"
    
    # Check content for clues
    if 'if __name__' in content:
        # Look for argparse
        if 'argparse' in content:
            return "Command-line utility (see argument parser for details)"
        # Look for main function
        if 'def main(' in content:
            return "Main execution script"
    
    # Default
    return f"[To be documented - {name.replace('_', ' ').title()}]"

def generate_script_header(script_path: Path) -> Optional[str]:
    """
    Generate documentation header for a script.
    
    Args:
        script_path: Path to the script
        
    Returns:
        Generated header or None if script already has one
    """
    try:
        with open(script_path) as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Error reading {script_path}: {e}")
        return None
    
    # Skip if already has docstring
    stripped = content.strip()
    if stripped.startswith('"""') or stripped.startswith("'''"):
        return None
    
    # Skip if it's just imports/comments
    if len(content.strip()) < 50:
        return None
    
    title = script_path.stem.replace('_', ' ').title()
    purpose = infer_purpose(script_path, content)
    
    header = HEADER_TEMPLATE.format(
        title=title,
        purpose=purpose,
        script_path=script_path
    )
    
    return header

def add_header_to_script(script_path: Path) -> bool:
    """
    Add documentation header to a script file.
    
    Args:
        script_path: Path to the script
        
    Returns:
        True if header was added, False otherwise
    """
    header = generate_script_header(script_path)
    if not header:
        return False
    
    try:
        with open(script_path) as f:
            content = f.read()
        
        lines = content.split('\n')
        insert_idx = 0
        
        # Skip shebang
        if lines and lines[0].startswith('#!'):
            insert_idx = 1
        
        # Skip encoding declarations
        if insert_idx < len(lines) and ('coding' in lines[insert_idx] or 'encoding' in lines[insert_idx]):
            insert_idx += 1
        
        # Insert header
        lines.insert(insert_idx, header)
        
        with open(script_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return True
    except Exception as e:
        print(f"❌ Error processing {script_path}: {e}")
        return False

def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_script_headers.py [script_path|--all]")
        sys.exit(1)
    
    scripts_dir = Path('scripts')
    
    if sys.argv[1] == '--all':
        scripts = list(scripts_dir.rglob('*.py'))
        # Filter out this script itself and __init__ files
        scripts = [s for s in scripts if s.name != 'add_script_headers.py' and s.name != '__init__.py']
    else:
        scripts = [Path(sys.argv[1])]
    
    print(f"📚 Processing {len(scripts)} scripts")
    print("="*60)
    
    documented = 0
    skipped = 0
    errors = 0
    
    for script in scripts:
        if not script.exists():
            print(f"❌ Not found: {script}")
            errors += 1
            continue
        
        if add_header_to_script(script):
            documented += 1
            print(f"✅ Added header to {script.name}")
        else:
            skipped += 1
            print(f"✓  {script.name} (already has header or too small)")
    
    print("\n" + "="*60)
    print(f"📊 Documentation Statistics:")
    print(f"   Documented: {documented} scripts")
    print(f"   Skipped: {skipped} (already have headers)")
    print(f"   Errors: {errors}")
    print(f"   Total Scripts: {len(scripts)}")
    print(f"   Success Rate: {(documented / max(len(scripts), 1)) * 100:.1f}%")

if __name__ == '__main__':
    main()
