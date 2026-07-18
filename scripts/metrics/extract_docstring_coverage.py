#!/usr/bin/env python3
"""
Extract docstring coverage metrics.

Counts functions and classes with/without docstrings.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from ast import parse, walk, FunctionDef, ClassDef, AsyncFunctionDef


def extract_docstring_coverage(src_path: str, output_path: str) -> None:
    """Extract docstring coverage metrics from Python source files."""
    
    src_dir = Path(src_path)
    if not src_dir.exists():
        print(f"Source directory not found: {src_path}")
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metric_id": "docstring_coverage",
            "coverage_percent": 0,
            "total_items": 0,
            "documented_items": 0,
            "status": "no_data",
        }
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        return
    
    total_items = 0
    documented_items = 0
    undocumented = []
    
    # Walk all Python files
    for py_file in src_dir.rglob("*.py"):
        try:
            with open(py_file) as f:
                content = f.read()
            
            tree = parse(content)
            
            # Count functions and classes
            for node in walk(tree):
                if isinstance(node, (FunctionDef, AsyncFunctionDef, ClassDef)):
                    # Skip private/special methods unless they're classes
                    if isinstance(node, ClassDef) or not node.name.startswith('_'):
                        total_items += 1
                        
                        # Check for docstring
                        if node.body and isinstance(node.body[0], type(parse("").body[0])):
                            has_docstring = False
                        else:
                            has_docstring = bool(__doc__ in str(node.body[0]) if node.body else False)
                        
                        # Simpler: check if first statement is string
                        has_docstring = (
                            node.body and
                            hasattr(node.body[0], 'value') and
                            isinstance(node.body[0].value, type(''))
                        )
                        
                        if has_docstring:
                            documented_items += 1
                        else:
                            undocumented.append({
                                'file': str(py_file.relative_to(src_dir)),
                                'name': node.name,
                                'type': 'function' if isinstance(node, (FunctionDef, AsyncFunctionDef)) else 'class',
                            })
        
        except SyntaxError as e:
            print(f"⚠️ Syntax error in {py_file}: {e}")
            continue
    
    # Calculate percentage
    coverage_percent = (documented_items / total_items * 100) if total_items > 0 else 0
    
    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "docstring_coverage",
        "coverage_percent": round(coverage_percent, 2),
        "total_items": total_items,
        "documented_items": documented_items,
        "undocumented_items": total_items - documented_items,
        "undocumented_examples": undocumented[:20],  # Top 20
        "target": 85.0,
        "source": "ast-analysis",
    }
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Docstring coverage metrics written to {output_path}")
    print(f"   Coverage: {coverage_percent:.2f}% ({documented_items}/{total_items})")
    print(f"   Undocumented items: {total_items - documented_items}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_docstring_coverage.py <src_path> <output.json>")
        sys.exit(1)
    
    extract_docstring_coverage(sys.argv[1], sys.argv[2])
