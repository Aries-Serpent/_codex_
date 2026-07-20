#!/usr/bin/env python3
"""
CI/CD Cache Optimization Script
Automatically adds intelligent caching to Python workflows lacking cache configuration.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

class WorkflowOptimizer:
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = workflows_dir
        self.optimized_workflows = []
        self.failed_workflows = []
        
    def needs_cache_optimization(self, content: str) -> bool:
        """Check if workflow needs cache optimization."""
        has_pip = 'pip install' in content
        has_poetry = 'poetry' in content
        has_setup_python_non_cached = 'uses: actions/setup-python@' in content
        has_cache = 'uses: ./.github/actions/setup-python-cached' in content or 'uses: actions/cache' in content
        
        return (has_pip or has_poetry) and has_setup_python_non_cached and not has_cache
    
    def extract_workflow_name(self, filename: str) -> str:
        """Extract friendly workflow name from filename."""
        return filename.replace('-', '_').replace('.yml', '').replace('.yaml', '')
    
    def optimize_setup_python(self, content: str) -> Tuple[str, bool]:
        """Replace actions/setup-python@v5 with setup-python-cached."""
        original = content
        
        # Pattern 1: setup-python with inline python-version
        pattern = r"(\s+)-\s*name:\s*['\"]?Set\s+up\s+Python['\"]?\n\s+uses:\s+actions/setup-python@v\d+\n\s+with:\n\s+python-version:\s*['\"]?([^'\"]\n[^\n]*?)['\"]?\n"
        
        def replace_func(match):
            indent = match.group(1)
            py_version = match.group(2).strip()
            return f"""{indent}- name: Set up Python with caching
{indent}  uses: ./.github/actions/setup-python-cached
{indent}  with:
{indent}    python-version: '{py_version}'
{indent}    cache-tier: common
{indent}    cache-version: ${{{{ vars.CODEX_CACHE_VERSION || 'v2' }}}}
"""
        
        content = re.sub(pattern, replace_func, content)
        
        return content, content != original
    
    def add_pip_cache(self, content: str, workflow_name: str) -> Tuple[str, bool]:
        """Add pip cache action after setup-python-cached."""
        original = content
        
        # Find setup-python-cached block
        pattern = r"((\s+)-\s*name:\s*Set\s+up\s+Python\s+with\s+caching\n(?:.*?\n){0,10}?cache-version:.*?\n)"
        
        if not re.search(pattern, content):
            return content, False
        
        cache_step = f"""{match.group(1) if (match := re.search(pattern, content)) else ''}    - name: Cache pip dependencies
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{{{ runner.os }}}}-pip-{workflow_name}-${{{{ hashFiles('**/requirements*.txt', '**/pyproject.toml', '**/uv.lock') }}}}
        restore-keys: |
          ${{{{ runner.os }}}}-pip-{workflow_name}-
          ${{{{ runner.os }}}}-pip-
"""
        
        content = re.sub(pattern, cache_step, content, count=1)
        
        return content, content != original
    
    def add_pytest_cache(self, content: str) -> Tuple[str, bool]:
        """Add pytest cache if tests are present."""
        if 'pytest' not in content and '-m test' not in content:
            return content, False
        
        original = content
        
        # Add pytest cache before first run/test step
        pattern = r"(\s+)-\s*name:.*?[Rr]un.*?[Tt]est"
        
        pytest_cache = """      - name: Cache pytest artifacts
        uses: actions/cache@v4
        with:
          path: .pytest_cache
          key: ${{ runner.os }}-pytest-${{ hashFiles('**/pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pytest-
      """
        
        if re.search(pattern, content):
            content = re.sub(pattern, pytest_cache + r"\g<0>", content, count=1)
        
        return content, content != original
    
    def optimize_workflow(self, filepath: str) -> bool:
        """Optimize a single workflow file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            if not self.needs_cache_optimization(content):
                return False
            
            original_content = content
            workflow_name = self.extract_workflow_name(os.path.basename(filepath))
            
            # Optimize setup-python
            content, setup_changed = self.optimize_setup_python(content)
            
            # Add pip cache
            content, pip_changed = self.add_pip_cache(content, workflow_name)
            
            # Add pytest cache if needed
            content, pytest_changed = self.add_pytest_cache(content)
            
            if content == original_content:
                return False
            
            # Write optimized workflow back
            with open(filepath, 'w') as f:
                f.write(content)
            
            self.optimized_workflows.append({
                'file': os.path.basename(filepath),
                'setup_changed': setup_changed,
                'pip_cache_added': pip_changed,
                'pytest_cache_added': pytest_changed
            })
            
            return True
            
        except Exception as e:
            self.failed_workflows.append({
                'file': os.path.basename(filepath),
                'error': str(e)
            })
            return False
    
    def optimize_all(self) -> Dict:
        """Optimize all workflows in directory."""
        for filename in sorted(os.listdir(self.workflows_dir)):
            if not filename.endswith(('.yml', '.yaml')):
                continue
            
            filepath = os.path.join(self.workflows_dir, filename)
            self.optimize_workflow(filepath)
        
        return {
            'total_optimized': len(self.optimized_workflows),
            'total_failed': len(self.failed_workflows),
            'optimized': self.optimized_workflows,
            'failed': self.failed_workflows
        }
    
    def print_report(self, results: Dict):
        """Print optimization report."""
        print("\n" + "=" * 80)
        print("CI/CD CACHE OPTIMIZATION REPORT")
        print("=" * 80)
        print(f"\n✅ Workflows Optimized: {results['total_optimized']}")
        print(f"❌ Workflows Failed: {results['total_failed']}")
        
        if results['optimized']:
            print("\nOPTIMIZED WORKFLOWS:")
            for w in results['optimized'][:20]:
                changes = []
                if w['setup_changed']:
                    changes.append("setup-python")
                if w['pip_cache_added']:
                    changes.append("pip-cache")
                if w['pytest_cache_added']:
                    changes.append("pytest-cache")
                print(f"  ✓ {w['file']:<40} ({', '.join(changes)})")
        
        if results['failed']:
            print("\nFAILED WORKFLOWS:")
            for w in results['failed']:
                print(f"  ✗ {w['file']:<40} ({w['error']})")
        
        print("\n" + "=" * 80)

def main():
    optimizer = WorkflowOptimizer()
    results = optimizer.optimize_all()
    optimizer.print_report(results)
    
    # Write results to JSON for tracking
    with open('.codex/cache_optimization_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if results['total_failed'] == 0 else 1

if __name__ == '__main__':
    exit(main())
