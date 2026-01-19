#!/usr/bin/env python3
"""
Comprehensive Documentation Quality Audit Script
Analyzes Python source code for documentation coverage and quality.
"""

import ast
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ModuleStats:
    """Statistics for a single module."""
    path: str
    has_module_docstring: bool = False
    total_functions: int = 0
    documented_functions: int = 0
    total_classes: int = 0
    documented_classes: int = 0
    total_methods: int = 0
    documented_methods: int = 0
    public_items: int = 0
    documented_public_items: int = 0
    lines_of_code: int = 0
    
    @property
    def function_coverage(self) -> float:
        if self.total_functions == 0:
            return 100.0
        return (self.documented_functions / self.total_functions) * 100
    
    @property
    def class_coverage(self) -> float:
        if self.total_classes == 0:
            return 100.0
        return (self.documented_classes / self.total_classes) * 100
    
    @property
    def method_coverage(self) -> float:
        if self.total_methods == 0:
            return 100.0
        return (self.documented_methods / self.total_methods) * 100
    
    @property
    def public_coverage(self) -> float:
        if self.public_items == 0:
            return 100.0
        return (self.documented_public_items / self.public_items) * 100
    
    @property
    def overall_coverage(self) -> float:
        total = (self.total_functions + self.total_classes + self.total_methods)
        if total == 0:
            return 100.0 if self.has_module_docstring else 0.0
        documented = (self.documented_functions + self.documented_classes + self.documented_methods)
        base_score = (documented / total) * 100
        # Bonus for module docstring
        if self.has_module_docstring:
            base_score = min(100.0, base_score + 5.0)
        return base_score


@dataclass
class AuditResults:
    """Overall audit results."""
    modules: Dict[str, ModuleStats] = field(default_factory=dict)
    total_files: int = 0
    total_lines: int = 0
    
    @property
    def module_docstring_coverage(self) -> float:
        if not self.modules:
            return 0.0
        documented = sum(1 for m in self.modules.values() if m.has_module_docstring)
        return (documented / len(self.modules)) * 100
    
    @property
    def function_coverage(self) -> float:
        total = sum(m.total_functions for m in self.modules.values())
        if total == 0:
            return 100.0
        documented = sum(m.documented_functions for m in self.modules.values())
        return (documented / total) * 100
    
    @property
    def class_coverage(self) -> float:
        total = sum(m.total_classes for m in self.modules.values())
        if total == 0:
            return 100.0
        documented = sum(m.documented_classes for m in self.modules.values())
        return (documented / total) * 100
    
    @property
    def method_coverage(self) -> float:
        total = sum(m.total_methods for m in self.modules.values())
        if total == 0:
            return 100.0
        documented = sum(m.documented_methods for m in self.modules.values())
        return (documented / total) * 100
    
    @property
    def public_api_coverage(self) -> float:
        total = sum(m.public_items for m in self.modules.values())
        if total == 0:
            return 100.0
        documented = sum(m.documented_public_items for m in self.modules.values())
        return (documented / total) * 100
    
    @property
    def overall_docstring_score(self) -> float:
        """Calculate weighted overall documentation score."""
        weights = {
            'module': 0.15,
            'function': 0.25,
            'class': 0.25,
            'method': 0.20,
            'public': 0.15
        }
        
        return (
            weights['module'] * self.module_docstring_coverage +
            weights['function'] * self.function_coverage +
            weights['class'] * self.class_coverage +
            weights['method'] * self.method_coverage +
            weights['public'] * self.public_api_coverage
        )


class DocstringAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze docstring coverage."""
    
    def __init__(self, module_path: str):
        self.module_path = module_path
        self.stats = ModuleStats(path=module_path)
        self.current_class = None
        
    def has_docstring(self, node) -> bool:
        """Check if a node has a docstring."""
        if not node.body:
            return False
        first = node.body[0]
        return (isinstance(first, ast.Expr) and 
                isinstance(first.value, (ast.Str, ast.Constant)))
    
    def is_public(self, name: str) -> bool:
        """Check if a name is public (doesn't start with _)."""
        return not name.startswith('_')
    
    def visit_Module(self, node):
        """Visit module to check module-level docstring."""
        self.stats.has_module_docstring = self.has_docstring(node)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        # Skip nested functions and lambda
        if self.current_class is None:
            self.stats.total_functions += 1
            if self.has_docstring(node):
                self.stats.documented_functions += 1
            
            if self.is_public(node.name):
                self.stats.public_items += 1
                if self.has_docstring(node):
                    self.stats.documented_public_items += 1
        else:
            # It's a method
            self.stats.total_methods += 1
            if self.has_docstring(node):
                self.stats.documented_methods += 1
            
            if self.is_public(node.name):
                self.stats.public_items += 1
                if self.has_docstring(node):
                    self.stats.documented_public_items += 1
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions."""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.stats.total_classes += 1
        if self.has_docstring(node):
            self.stats.documented_classes += 1
        
        if self.is_public(node.name):
            self.stats.public_items += 1
            if self.has_docstring(node):
                self.stats.documented_public_items += 1
        
        # Process methods
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class


def analyze_python_file(filepath: Path) -> Optional[ModuleStats]:
    """Analyze a single Python file for documentation coverage."""
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(filepath))
        
        analyzer = DocstringAnalyzer(str(filepath))
        analyzer.visit(tree)
        analyzer.stats.lines_of_code = len(content.splitlines())
        
        return analyzer.stats
    except Exception as e:
        print(f"Warning: Could not analyze {filepath}: {e}")
        return None


def find_python_files(root_dir: Path, exclude_patterns: List[str] = None) -> List[Path]:
    """Find all Python files in the directory tree."""
    if exclude_patterns is None:
        exclude_patterns = [
            '*/tests/*',
            '*/test_*',
            '*/__pycache__/*',
            '*/.*',
            '*/venv/*',
            '*/env/*',
            '*/.venv/*',
            '*/build/*',
            '*/dist/*',
        ]
    
    python_files = []
    for py_file in root_dir.rglob('*.py'):
        # Check if file matches any exclude pattern
        if any(py_file.match(pattern) for pattern in exclude_patterns):
            continue
        python_files.append(py_file)
    
    return python_files


def analyze_markdown_docs(root_dir: Path) -> Dict[str, any]:
    """Analyze markdown documentation files."""
    docs_dir = root_dir / 'docs'
    
    stats = {
        'total_md_files': 0,
        'total_md_lines': 0,
        'files_with_links': 0,
        'total_internal_links': 0,
        'api_reference_files': 0,
        'tutorial_files': 0,
        'guide_files': 0,
        'architecture_files': 0,
    }
    
    if not docs_dir.exists():
        return stats
    
    for md_file in docs_dir.rglob('*.md'):
        stats['total_md_files'] += 1
        try:
            content = md_file.read_text(encoding='utf-8')
            stats['total_md_lines'] += len(content.splitlines())
            
            # Count internal links
            internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            if internal_links:
                stats['files_with_links'] += 1
                stats['total_internal_links'] += len(internal_links)
            
            # Categorize files
            name_lower = md_file.name.lower()
            if 'api' in name_lower or 'reference' in name_lower:
                stats['api_reference_files'] += 1
            if 'tutorial' in name_lower or 'getting' in name_lower:
                stats['tutorial_files'] += 1
            if 'guide' in name_lower or 'how' in name_lower:
                stats['guide_files'] += 1
            if 'architecture' in name_lower or 'design' in name_lower:
                stats['architecture_files'] += 1
                
        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}")
    
    return stats


def check_cli_documentation(root_dir: Path) -> Dict[str, any]:
    """Check CLI command documentation."""
    cli_stats = {
        'cli_files_found': 0,
        'cli_commands_with_help': 0,
        'cli_commands_without_help': 0,
    }
    
    # Search for CLI-related files
    cli_patterns = ['**/cli.py', '**/cli/*.py', '**/*_cli.py']
    cli_files = []
    
    for pattern in cli_patterns:
        cli_files.extend(root_dir.glob(pattern))
    
    cli_stats['cli_files_found'] = len(set(cli_files))
    
    # Simple heuristic: look for @click.command or @typer decorators
    for cli_file in cli_files:
        try:
            content = cli_file.read_text(encoding='utf-8')
            # Count decorated functions (likely CLI commands)
            commands = re.findall(r'@(?:click|typer|app)\.command', content)
            # Count help strings
            help_strings = re.findall(r'help\s*=\s*["\']', content)
            
            if commands:
                cli_stats['cli_commands_with_help'] += len(help_strings)
                cli_stats['cli_commands_without_help'] += max(0, len(commands) - len(help_strings))
        except Exception as e:
            print(f"Warning: Could not analyze CLI file {cli_file}: {e}")
    
    return cli_stats


def generate_report(results: AuditResults, md_stats: Dict, cli_stats: Dict, root_dir: Path) -> str:
    """Generate comprehensive documentation quality report."""
    
    report = []
    report.append("=" * 80)
    report.append("COMPREHENSIVE DOCUMENTATION QUALITY AUDIT REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Executive Summary
    report.append("## EXECUTIVE SUMMARY")
    report.append("-" * 80)
    report.append(f"Repository Root: {root_dir}")
    report.append(f"Total Python Files Analyzed: {results.total_files}")
    report.append(f"Total Lines of Code: {results.total_lines:,}")
    report.append(f"Total Markdown Files: {md_stats['total_md_files']}")
    report.append("")
    
    # Overall Quality Score
    overall_score = results.overall_docstring_score
    report.append(f"**OVERALL DOCUMENTATION QUALITY SCORE: {overall_score:.1f}/100**")
    
    if overall_score >= 90:
        grade = "A (Excellent)"
    elif overall_score >= 80:
        grade = "B (Good)"
    elif overall_score >= 70:
        grade = "C (Satisfactory)"
    elif overall_score >= 60:
        grade = "D (Needs Improvement)"
    else:
        grade = "F (Critical)"
    
    report.append(f"Grade: {grade}")
    report.append("")
    
    # Docstring Coverage by Category
    report.append("## DOCSTRING COVERAGE BY CATEGORY")
    report.append("-" * 80)
    report.append(f"Module Docstrings:     {results.module_docstring_coverage:6.1f}%")
    report.append(f"Function Docstrings:   {results.function_coverage:6.1f}%")
    report.append(f"Class Docstrings:      {results.class_coverage:6.1f}%")
    report.append(f"Method Docstrings:     {results.method_coverage:6.1f}%")
    report.append(f"Public API Coverage:   {results.public_api_coverage:6.1f}%")
    report.append("")
    
    # Detailed Statistics
    report.append("## DETAILED STATISTICS")
    report.append("-" * 80)
    
    total_funcs = sum(m.total_functions for m in results.modules.values())
    doc_funcs = sum(m.documented_functions for m in results.modules.values())
    total_classes = sum(m.total_classes for m in results.modules.values())
    doc_classes = sum(m.documented_classes for m in results.modules.values())
    total_methods = sum(m.total_methods for m in results.modules.values())
    doc_methods = sum(m.documented_methods for m in results.modules.values())
    total_public = sum(m.public_items for m in results.modules.values())
    doc_public = sum(m.documented_public_items for m in results.modules.values())
    
    report.append(f"Functions:     {doc_funcs:4d} / {total_funcs:4d} documented ({results.function_coverage:.1f}%)")
    report.append(f"Classes:       {doc_classes:4d} / {total_classes:4d} documented ({results.class_coverage:.1f}%)")
    report.append(f"Methods:       {doc_methods:4d} / {total_methods:4d} documented ({results.method_coverage:.1f}%)")
    report.append(f"Public APIs:   {doc_public:4d} / {total_public:4d} documented ({results.public_api_coverage:.1f}%)")
    report.append("")
    
    # User Documentation
    report.append("## USER DOCUMENTATION")
    report.append("-" * 80)
    report.append(f"Total Documentation Files: {md_stats['total_md_files']}")
    report.append(f"Total Documentation Lines: {md_stats['total_md_lines']:,}")
    report.append(f"API Reference Files:       {md_stats['api_reference_files']}")
    report.append(f"Tutorial Files:            {md_stats['tutorial_files']}")
    report.append(f"Guide Files:               {md_stats['guide_files']}")
    report.append(f"Architecture Files:        {md_stats['architecture_files']}")
    report.append(f"Files with Links:          {md_stats['files_with_links']}")
    report.append(f"Total Internal Links:      {md_stats['total_internal_links']}")
    report.append("")
    
    # User Documentation Score
    user_doc_score = min(100, (
        (md_stats['api_reference_files'] * 10) +
        (md_stats['tutorial_files'] * 8) +
        (md_stats['guide_files'] * 6) +
        (md_stats['architecture_files'] * 5)
    ))
    report.append(f"User Documentation Score: {user_doc_score:.1f}/100")
    report.append("")
    
    # CLI Documentation
    report.append("## CLI DOCUMENTATION")
    report.append("-" * 80)
    report.append(f"CLI Files Found:                {cli_stats['cli_files_found']}")
    report.append(f"CLI Commands with Help Text:    {cli_stats['cli_commands_with_help']}")
    report.append(f"CLI Commands without Help Text: {cli_stats['cli_commands_without_help']}")
    
    total_cli = cli_stats['cli_commands_with_help'] + cli_stats['cli_commands_without_help']
    if total_cli > 0:
        cli_coverage = (cli_stats['cli_commands_with_help'] / total_cli) * 100
        report.append(f"CLI Documentation Coverage:     {cli_coverage:.1f}%")
    report.append("")
    
    # Top 20 Modules Missing Documentation
    report.append("## TOP 20 MODULES MISSING DOCUMENTATION")
    report.append("-" * 80)
    
    # Sort modules by overall coverage (ascending)
    sorted_modules = sorted(
        results.modules.items(),
        key=lambda x: (x[1].overall_coverage, x[1].lines_of_code),
    )
    
    report.append(f"{'Rank':<5} {'Coverage':<10} {'LOC':<8} {'Module Path'}")
    report.append("-" * 80)
    
    for i, (path, stats) in enumerate(sorted_modules[:20], 1):
        # Shorten path for readability
        short_path = str(Path(path).relative_to(root_dir)) if root_dir in Path(path).parents else path
        report.append(f"{i:<5} {stats.overall_coverage:>6.1f}%   {stats.lines_of_code:>6}  {short_path}")
    
    report.append("")
    
    # Modules with Zero Documentation
    zero_doc_modules = [
        (path, stats) for path, stats in results.modules.items()
        if stats.overall_coverage == 0.0 and stats.lines_of_code > 10
    ]
    
    report.append(f"## MODULES WITH ZERO DOCUMENTATION (LOC > 10)")
    report.append("-" * 80)
    report.append(f"Total: {len(zero_doc_modules)} modules")
    report.append("")
    
    for path, stats in sorted(zero_doc_modules, key=lambda x: x[1].lines_of_code, reverse=True)[:10]:
        short_path = str(Path(path).relative_to(root_dir)) if root_dir in Path(path).parents else path
        report.append(f"  {stats.lines_of_code:>6} LOC  {short_path}")
    
    report.append("")
    
    # Calculate Overall Final Score
    report.append("## OVERALL QUALITY SCORE CALCULATION")
    report.append("-" * 80)
    
    api_doc_score = results.overall_docstring_score
    
    # Weighted score
    weights = {
        'api_docstrings': 0.50,
        'user_docs': 0.30,
        'cli_docs': 0.20,
    }
    
    cli_doc_score = (cli_stats['cli_commands_with_help'] / max(1, total_cli)) * 100 if total_cli > 0 else 70
    
    final_score = (
        weights['api_docstrings'] * api_doc_score +
        weights['user_docs'] * user_doc_score +
        weights['cli_docs'] * cli_doc_score
    )
    
    report.append(f"API Documentation (50%):  {api_doc_score:6.1f}%")
    report.append(f"User Documentation (30%): {user_doc_score:6.1f}%")
    report.append(f"CLI Documentation (20%):  {cli_doc_score:6.1f}%")
    report.append("")
    report.append(f"**FINAL OVERALL DOCUMENTATION QUALITY SCORE: {final_score:.1f}/100**")
    report.append("")
    
    # Recommendations
    report.append("## PRIORITIZED REMEDIATION PLAN")
    report.append("-" * 80)
    report.append("")
    
    recommendations = []
    
    if results.module_docstring_coverage < 70:
        recommendations.append({
            'priority': 'P0',
            'area': 'Module Docstrings',
            'action': 'Add module-level docstrings to all public modules',
            'impact': 'High',
            'effort': 'Low',
        })
    
    if results.public_api_coverage < 80:
        recommendations.append({
            'priority': 'P0',
            'area': 'Public API Documentation',
            'action': 'Document all public functions, classes, and methods',
            'impact': 'High',
            'effort': 'Medium',
        })
    
    if md_stats['api_reference_files'] < 10:
        recommendations.append({
            'priority': 'P1',
            'area': 'API Reference',
            'action': 'Create comprehensive API reference documentation',
            'impact': 'High',
            'effort': 'High',
        })
    
    if md_stats['tutorial_files'] < 5:
        recommendations.append({
            'priority': 'P1',
            'area': 'Tutorials',
            'action': 'Create getting-started tutorials and examples',
            'impact': 'Medium',
            'effort': 'Medium',
        })
    
    if cli_stats['cli_commands_without_help'] > 5:
        recommendations.append({
            'priority': 'P2',
            'area': 'CLI Help Text',
            'action': 'Add help text to all CLI commands',
            'impact': 'Medium',
            'effort': 'Low',
        })
    
    if results.function_coverage < 70:
        recommendations.append({
            'priority': 'P1',
            'area': 'Function Docstrings',
            'action': 'Add docstrings to undocumented functions',
            'impact': 'Medium',
            'effort': 'Medium',
        })
    
    if results.class_coverage < 70:
        recommendations.append({
            'priority': 'P1',
            'area': 'Class Docstrings',
            'action': 'Add docstrings to undocumented classes',
            'impact': 'Medium',
            'effort': 'Medium',
        })
    
    # Sort by priority
    recommendations.sort(key=lambda x: x['priority'])
    
    for i, rec in enumerate(recommendations, 1):
        report.append(f"{i}. [{rec['priority']}] {rec['area']}")
        report.append(f"   Action: {rec['action']}")
        report.append(f"   Impact: {rec['impact']} | Effort: {rec['effort']}")
        report.append("")
    
    # Quick Wins
    report.append("## QUICK WINS (Low Effort, High Impact)")
    report.append("-" * 80)
    
    quick_wins = []
    
    # Module docstrings are quick wins
    if results.module_docstring_coverage < 80:
        modules_needing_docstrings = sum(1 for m in results.modules.values() if not m.has_module_docstring)
        quick_wins.append(f"Add module docstrings to {modules_needing_docstrings} modules (~2-5 minutes each)")
    
    # CLI help text
    if cli_stats['cli_commands_without_help'] > 0:
        quick_wins.append(f"Add help text to {cli_stats['cli_commands_without_help']} CLI commands (~2 minutes each)")
    
    # Small files with zero documentation
    small_zero_doc = [
        s for s in results.modules.values()
        if s.overall_coverage == 0.0 and 10 < s.lines_of_code < 100
    ]
    if small_zero_doc:
        quick_wins.append(f"Document {len(small_zero_doc)} small modules (< 100 LOC) with zero documentation")
    
    for i, win in enumerate(quick_wins, 1):
        report.append(f"{i}. {win}")
    
    report.append("")
    
    # Phase 5 Effort Estimation
    report.append("## PHASE 5 EFFORT ESTIMATION (8 WEEKS)")
    report.append("-" * 80)
    
    undocumented_count = (
        (total_funcs - doc_funcs) +
        (total_classes - doc_classes) +
        (total_methods - doc_methods)
    )
    
    # Estimate time per item
    time_per_docstring = 5  # minutes
    time_per_api_ref = 60  # minutes
    time_per_tutorial = 180  # minutes
    
    docstring_hours = (undocumented_count * time_per_docstring) / 60
    api_ref_hours = max(0, 20 - md_stats['api_reference_files']) * time_per_api_ref / 60
    tutorial_hours = max(0, 10 - md_stats['tutorial_files']) * time_per_tutorial / 60
    
    total_hours = docstring_hours + api_ref_hours + tutorial_hours
    weeks_at_20hrs = total_hours / 20
    
    report.append(f"Undocumented Items: {undocumented_count}")
    report.append(f"  - Docstring Writing:       {docstring_hours:>6.1f} hours")
    report.append(f"  - API Reference Creation:  {api_ref_hours:>6.1f} hours")
    report.append(f"  - Tutorial Creation:       {tutorial_hours:>6.1f} hours")
    report.append(f"")
    report.append(f"Total Estimated Effort:      {total_hours:>6.1f} hours")
    report.append(f"Weeks at 20hrs/week:         {weeks_at_20hrs:>6.1f} weeks")
    report.append(f"")
    
    if weeks_at_20hrs <= 8:
        report.append("✅ Phase 5 (8 weeks) is FEASIBLE for complete documentation")
    else:
        report.append(f"⚠️  Phase 5 (8 weeks) may be tight. Consider {weeks_at_20hrs:.0f} weeks or prioritization.")
    
    report.append("")
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main execution function."""
    root_dir = Path.cwd()
    src_dir = root_dir / 'src'
    
    print("Starting Comprehensive Documentation Quality Audit...")
    print(f"Root Directory: {root_dir}")
    print(f"Source Directory: {src_dir}")
    print()
    
    # Find and analyze Python files
    print("Finding Python files...")
    python_files = find_python_files(src_dir)
    print(f"Found {len(python_files)} Python files in src/")
    print()
    
    print("Analyzing Python files for docstring coverage...")
    results = AuditResults()
    results.total_files = len(python_files)
    
    for i, py_file in enumerate(python_files, 1):
        if i % 50 == 0:
            print(f"  Analyzed {i}/{len(python_files)} files...")
        
        stats = analyze_python_file(py_file)
        if stats:
            results.modules[str(py_file)] = stats
            results.total_lines += stats.lines_of_code
    
    print(f"✓ Analyzed {len(results.modules)} modules successfully")
    print()
    
    # Analyze markdown documentation
    print("Analyzing markdown documentation...")
    md_stats = analyze_markdown_docs(root_dir)
    print(f"✓ Found {md_stats['total_md_files']} documentation files")
    print()
    
    # Analyze CLI documentation
    print("Analyzing CLI documentation...")
    cli_stats = check_cli_documentation(root_dir)
    print(f"✓ Found {cli_stats['cli_files_found']} CLI files")
    print()
    
    # Generate report
    print("Generating comprehensive report...")
    report = generate_report(results, md_stats, cli_stats, root_dir)
    
    # Save report
    report_path = root_dir / 'DOCUMENTATION_QUALITY_AUDIT_REPORT.md'
    report_path.write_text(report)
    print(f"✓ Report saved to: {report_path}")
    print()
    
    # Also save JSON data for programmatic access
    json_data = {
        'overall_score': results.overall_docstring_score,
        'module_coverage': results.module_docstring_coverage,
        'function_coverage': results.function_coverage,
        'class_coverage': results.class_coverage,
        'method_coverage': results.method_coverage,
        'public_api_coverage': results.public_api_coverage,
        'total_files': results.total_files,
        'total_lines': results.total_lines,
        'markdown_stats': md_stats,
        'cli_stats': cli_stats,
    }
    
    json_path = root_dir / 'documentation_quality_audit.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"✓ JSON data saved to: {json_path}")
    print()
    
    # Print summary to console
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Overall Documentation Quality Score: {results.overall_docstring_score:.1f}/100")
    print(f"Module Docstrings:     {results.module_docstring_coverage:6.1f}%")
    print(f"Function Docstrings:   {results.function_coverage:6.1f}%")
    print(f"Class Docstrings:      {results.class_coverage:6.1f}%")
    print(f"Method Docstrings:     {results.method_coverage:6.1f}%")
    print(f"Public API Coverage:   {results.public_api_coverage:6.1f}%")
    print()
    print(f"See full report at: {report_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()
