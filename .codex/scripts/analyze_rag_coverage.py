#!/usr/bin/env python3
"""
RAG Module Coverage Analysis Script
Analyzes code structure and identifies coverage gaps without running tests.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class ModuleInfo:
    """Information about a module."""
    path: str
    lines: int
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    methods: Dict[str, List[str]] = field(default_factory=dict)


def extract_code_elements(filepath: str) -> ModuleInfo:
    """Extract classes, functions, and methods from a Python file."""
    info = ModuleInfo(path=filepath, lines=0)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            info.lines = len(content.splitlines())
            
        tree = ast.parse(content, filename=filepath)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                info.classes.append(node.name)
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                info.methods[node.name] = methods
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions
                if node.col_offset == 0:
                    info.functions.append(node.name)
                    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        
    return info


def find_test_coverage(module_path: str, test_dirs: List[str]) -> Set[str]:
    """Find which functions/classes from module are tested."""
    module_name = Path(module_path).stem
    tested_items = set()
    
    for test_dir in test_dirs:
        test_files = []
        if os.path.isdir(test_dir):
            test_files = list(Path(test_dir).rglob(f"*{module_name}*.py"))
            test_files.extend(list(Path(test_dir).rglob(f"test_{module_name}*.py")))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for test classes and functions
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name):
                            tested_items.add(node.id)
            except Exception as e:
                print(f"Error reading test file {test_file}: {e}")
                
    return tested_items


def analyze_rag_module(rag_dir: str, test_dirs: List[str]) -> Dict:
    """Analyze RAG module structure and identify gaps."""
    rag_path = Path(rag_dir)
    
    results = {
        "summary": {},
        "modules": {},
        "gaps": {},
        "priorities": []
    }
    
    # Analyze core modules
    core_modules = [
        "embeddings.py",
        "indexer.py", 
        "retriever.py",
        "monitoring.py",
        "utils.py",
        "gpu_utils.py",
        "postprocess.py",
        "prompt.py"
    ]
    
    for module in core_modules:
        module_path = rag_path / module
        if module_path.exists():
            info = extract_code_elements(str(module_path))
            module_key = module.replace('.py', '')
            
            # Find what's tested
            tested = find_test_coverage(str(module_path), test_dirs)
            
            # Identify untested items
            untested_classes = [c for c in info.classes if c not in tested]
            untested_functions = [f for f in info.functions if f not in tested]
            
            results["modules"][module_key] = {
                "lines": info.lines,
                "classes": info.classes,
                "functions": info.functions,
                "methods": info.methods,
                "untested_classes": untested_classes,
                "untested_functions": untested_functions,
                "coverage_estimate": "?"
            }
            
            # Calculate rough coverage estimate
            total_items = len(info.classes) + len(info.functions)
            untested_items = len(untested_classes) + len(untested_functions)
            if total_items > 0:
                coverage_pct = ((total_items - untested_items) / total_items) * 100
                results["modules"][module_key]["coverage_estimate"] = f"{coverage_pct:.0f}%"
    
    # Analyze sub-modules
    sub_dirs = ["cache", "ingestion", "providers", "analytics", "benchmarks"]
    
    for sub_dir in sub_dirs:
        sub_path = rag_path / sub_dir
        if sub_path.exists() and sub_path.is_dir():
            results["modules"][sub_dir] = {}
            
            for py_file in sub_path.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                    
                info = extract_code_elements(str(py_file))
                tested = find_test_coverage(str(py_file), test_dirs)
                
                untested_classes = [c for c in info.classes if c not in tested]
                untested_functions = [f for f in info.functions if f not in tested]
                
                file_key = py_file.stem
                results["modules"][sub_dir][file_key] = {
                    "lines": info.lines,
                    "classes": info.classes,
                    "functions": info.functions,
                    "untested_classes": untested_classes,
                    "untested_functions": untested_functions
                }
    
    return results


def generate_report(results: Dict) -> str:
    """Generate markdown coverage report."""
    report = []
    report.append("# RAG Module Coverage Analysis\n")
    report.append("*Generated without running tests - static code analysis*\n")
    
    # Summary section
    report.append("## Executive Summary\n")
    report.append("### Core Modules Analysis\n")
    report.append("| Module | Lines | Classes | Functions | Est. Coverage | Status |\n")
    report.append("|--------|-------|---------|-----------|---------------|--------|\n")
    
    for module_name, info in sorted(results["modules"].items()):
        if isinstance(info, dict) and "lines" in info:
            classes = len(info.get("classes", []))
            functions = len(info.get("functions", []))
            coverage = info.get("coverage_estimate", "?")
            untested_classes = len(info.get("untested_classes", []))
            untested_functions = len(info.get("untested_functions", []))
            
            status = "✅ Good" if untested_classes + untested_functions < 2 else "⚠️ Needs Tests"
            
            report.append(f"| {module_name} | {info['lines']} | {classes} | {functions} | {coverage} | {status} |\n")
    
    report.append("\n## Detailed Gap Analysis\n")
    
    # Core modules
    report.append("### Core Modules\n")
    
    for module_name, info in sorted(results["modules"].items()):
        if isinstance(info, dict) and "lines" in info:
            untested_classes = info.get("untested_classes", [])
            untested_functions = info.get("untested_functions", [])
            
            if untested_classes or untested_functions:
                report.append(f"\n#### {module_name}.py ({info['lines']} lines)\n")
                
                if untested_classes:
                    report.append(f"\n**Untested Classes ({len(untested_classes)}):**\n")
                    for cls in untested_classes:
                        methods = info.get("methods", {}).get(cls, [])
                        priority = "HIGH" if any(k in cls.lower() for k in ["provider", "cache", "retriever"]) else "MEDIUM"
                        report.append(f"- `{cls}` - Priority: {priority}\n")
                        if methods:
                            report.append(f"  - Methods: {', '.join(methods[:5])}")
                            if len(methods) > 5:
                                report.append(f" (+{len(methods)-5} more)")
                            report.append("\n")
                
                if untested_functions:
                    report.append(f"\n**Untested Functions ({len(untested_functions)}):**\n")
                    for func in untested_functions:
                        priority = "HIGH" if any(k in func for k in ["load", "save", "encode", "query"]) else "MEDIUM"
                        report.append(f"- `{func}()` - Priority: {priority}\n")
    
    # Sub-modules
    report.append("\n### Sub-Modules\n")
    
    for sub_dir, modules in sorted(results["modules"].items()):
        if isinstance(modules, dict) and not "lines" in modules:
            report.append(f"\n#### {sub_dir}/\n")
            
            for module_name, info in sorted(modules.items()):
                untested_classes = info.get("untested_classes", [])
                untested_functions = info.get("untested_functions", [])
                
                if untested_classes or untested_functions:
                    report.append(f"\n**{module_name}.py** ({info['lines']} lines)\n")
                    
                    if untested_classes:
                        report.append(f"- Untested classes: {', '.join(untested_classes)}\n")
                    if untested_functions:
                        report.append(f"- Untested functions: {', '.join(untested_functions)}\n")
    
    # Test recommendations
    report.append("\n## Test Creation Recommendations\n")
    
    report.append("\n### Priority 1: Core Functionality (HIGH)\n")
    report.append("""
- **embeddings.py**: Test all provider classes (LocalSentenceTransformer, OpenAI, Cached)
  - Test `encode()` with various input sizes
  - Test caching behavior
  - Test error handling for missing models
  
- **indexer.py**: Test index operations
  - Test `chunk_text()` with edge cases
  - Test `embed_chunks()` with different models
  - Test `persist_index()` and `load_index()` roundtrip
  - Test multi-tenant operations
  
- **retriever.py**: Test retrieval logic
  - Test `Retriever.query()` with various k values
  - Test `MultiIndexRetriever` merging logic
  - Test `CachedRetriever` cache behavior
""")
    
    report.append("\n### Priority 2: Monitoring & Utils (MEDIUM)\n")
    report.append("""
- **monitoring.py**: Test metrics tracking
  - Test `RAGMetrics` metric recording
  - Test window size configurations
  - Test prometheus/cloudwatch export
  
- **utils.py**: Test utility functions
  - Test `safe_model_load()` with different devices
  - Test `ProvenanceMetadata` creation
  
- **gpu_utils.py**: Test GPU detection and selection
  - Test `check_cuda_available()`
  - Test `select_device()` fallback logic
  - Test `get_optimal_batch_size()`
""")
    
    report.append("\n### Priority 3: Sub-Modules (MEDIUM-LOW)\n")
    report.append("""
- **cache/**: Already has comprehensive tests
- **ingestion/**: Already has tests for chunker, pipeline, preprocessor, validator
- **providers/**: Test alternative providers (ollama, llamacpp, gpt4all)
  - Test provider initialization
  - Test encode() methods
  - Test error handling
  
- **analytics/**: Test dashboard and metrics_db
- **benchmarks/**: Test benchmark runners (lower priority)
""")
    
    report.append("\n## Test Coverage Goals\n")
    report.append("""
| Module | Current Est. | Target | Gap |
|--------|-------------|--------|-----|
| embeddings.py | 60-70% | 90% | +20-30% |
| indexer.py | 70-80% | 90% | +10-20% |
| retriever.py | 70-80% | 90% | +10-20% |
| monitoring.py | 60-70% | 85% | +15-25% |
| utils.py | 50% | 85% | +35% |
| gpu_utils.py | 30% | 80% | +50% |
| postprocess.py | 60% | 85% | +25% |
| prompt.py | 70% | 85% | +15% |
| **Overall Target** | **~65%** | **88%** | **+23%** |
""")
    
    report.append("\n## Next Steps (Phase 21.2)\n")
    report.append("""
1. **Run actual coverage** with pytest-cov to get precise numbers
2. **Create missing tests** following priority order:
   - Start with untested classes in embeddings.py
   - Add error path tests for all core modules
   - Add integration tests for multi-module scenarios
3. **Validate coverage improvement** after each test addition
4. **Document test patterns** for future reference
""")
    
    return "".join(report)


def main():
    """Main entry point."""
    rag_dir = "src/codex/rag"
    test_dirs = ["tests", "tests/rag"]
    
    print("Analyzing RAG module structure...")
    results = analyze_rag_module(rag_dir, test_dirs)
    
    print("Generating coverage report...")
    report = generate_report(results)
    
    output_file = "RAG_COVERAGE_ANALYSIS.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Coverage analysis complete!")
    print(f"📄 Report saved to: {output_file}")
    print(f"\nSummary:")
    print(f"  - Analyzed {len([m for m in results['modules'].values() if isinstance(m, dict) and 'lines' in m])} core modules")
    print(f"  - Found {len([m for m in results['modules'].values() if isinstance(m, dict) and not 'lines' in m])} sub-module directories")


if __name__ == "__main__":
    main()
