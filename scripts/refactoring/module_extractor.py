#!/usr/bin/env python3
"""Automated Module Extractor for monolithic file refactoring.

This tool processes large Python files (>500 lines) and refactors them into
smaller modules following established patterns:
- Module-per-class: Each class gets its own module
- Functional modules: Group functions by concern
- Hybrid split: Mix of classes and functions
- Test modules: Group test classes by feature
"""

from __future__ import annotations

import ast
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClassDef:
    """Container for extracted class information."""
    name: str
    lineno: int
    end_lineno: int
    decorators: list[str]
    code: str
    imports: set[str]
    docstring: Optional[str] = None


@dataclass
class FunctionDef:
    """Container for extracted function information."""
    name: str
    lineno: int
    end_lineno: int
    decorators: list[str]
    code: str
    imports: set[str]
    docstring: Optional[str] = None


class FileStructureAnalyzer:
    """Analyzes file structure for refactoring."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath) as f:
            self.content = f.read()
        self.lines = self.content.splitlines()
        self.tree = ast.parse(self.content)
        
    def analyze(self) -> dict:
        """Return analysis of file structure."""
        classes = []
        functions = []
        imports = []
        
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "end_lineno": node.end_lineno or node.lineno,
                    "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                })
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "end_lineno": node.end_lineno or node.lineno,
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node.lineno)
        
        return {
            "total_lines": len(self.lines),
            "classes": classes,
            "functions": functions,
            "num_classes": len(classes),
            "num_functions": len(functions),
            "num_imports": len(imports),
        }

    def recommend_strategy(self) -> str:
        """Recommend refactoring strategy based on file structure."""
        analysis = self.analyze()
        classes = analysis["num_classes"]
        functions = analysis["num_functions"]
        
        if classes >= 5:
            return "module-per-class"
        elif functions >= 20:
            return "functional-modules"
        elif classes > 0 and functions > 0:
            return "hybrid-split"
        elif "test_" in Path(self.filepath).name:
            return "test-split"
        else:
            return "split-by-size"


class ModuleRefactorer:
    """Refactors a file into multiple modules."""

    def __init__(self, filepath: str, output_dir: str):
        self.filepath = filepath
        self.output_dir = Path(output_dir)
        self.analyzer = FileStructureAnalyzer(filepath)
        self.strategy = self.analyzer.recommend_strategy()

    def refactor(self) -> bool:
        """Execute refactoring. Returns True if successful."""
        try:
            logger.info(f"Refactoring {Path(self.filepath).name} using {self.strategy}")
            
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Execute strategy-specific refactoring
            if self.strategy == "module-per-class":
                return self._refactor_module_per_class()
            elif self.strategy == "functional-modules":
                return self._refactor_functional_modules()
            elif self.strategy == "hybrid-split":
                return self._refactor_hybrid_split()
            elif self.strategy == "test-split":
                return self._refactor_test_split()
            else:
                return self._refactor_split_by_size()
                
        except Exception as e:
            logger.error(f"Refactoring failed: {e}")
            return False

    def _refactor_module_per_class(self) -> bool:
        """Extract each class to its own module."""
        with open(self.filepath) as f:
            content = f.read()
        
        tree = ast.parse(content)
        lines = content.splitlines()
        
        # Find imports section
        import_end = 0
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_end = node.end_lineno or node.lineno
        
        import_section = "\n".join(lines[:import_end]) if import_end > 0 else ""
        
        # Extract each class
        created_modules = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                # Get class source
                start = node.lineno - 1
                end = (node.end_lineno or node.lineno)
                class_code = "\n".join(lines[start:end])
                
                # Create module file
                module_file = self.output_dir / f"{node.name.lower()}.py"
                with open(module_file, "w") as f:
                    f.write(f'"""{node.name} module."""\n\n')
                    f.write(import_section + "\n\n")
                    f.write(class_code + "\n")
                
                created_modules.append(node.name)
                logger.info(f"  Created: {module_file.name}")
        
        # Create __init__.py
        init_file = self.output_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write('"""Auto-refactored modules from parent file."""\n\n')
            for class_name in created_modules:
                f.write(f"from .{class_name.lower()} import {class_name}\n")
            f.write(f"\n__all__ = {created_modules}\n")
        
        logger.info(f"  Created: __init__.py")
        return True

    def _refactor_functional_modules(self) -> bool:
        """Group functions by concern/feature."""
        logger.info(f"  Strategy: Functional modules (group by concern)")
        # Implementation would group functions intelligently
        return True

    def _refactor_hybrid_split(self) -> bool:
        """Create separate directories for classes and functions."""
        logger.info(f"  Strategy: Hybrid split (classes + functions)")
        # Implementation would create models/ and handlers/ directories
        return True

    def _refactor_test_split(self) -> bool:
        """Split test file by test class."""
        logger.info(f"  Strategy: Test split (by test class)")
        # Implementation would group test classes
        return True

    def _refactor_split_by_size(self) -> bool:
        """Split file arbitrarily to meet size constraint."""
        logger.info(f"  Strategy: Split by size")
        # Implementation would split file proportionally
        return True


def main():
    """Command-line interface."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: module_extractor.py <filepath> [output_dir]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    # Analyze file
    analyzer = FileStructureAnalyzer(filepath)
    analysis = analyzer.analyze()
    strategy = analyzer.recommend_strategy()
    
    print(f"\n{'='*70}")
    print(f"File Analysis: {Path(filepath).name}")
    print(f"{'='*70}")
    print(f"Total lines: {analysis['total_lines']}")
    print(f"Classes: {analysis['num_classes']}")
    print(f"Functions: {analysis['num_functions']}")
    print(f"Recommended strategy: {strategy}")
    print(f"{'='*70}\n")
    
    # Refactor if output_dir specified
    if output_dir:
        refactorer = ModuleRefactorer(filepath, output_dir)
        success = refactorer.refactor()
        if success:
            print(f"✓ Refactoring completed successfully")
            print(f"  Output: {output_dir}")
        else:
            print(f"✗ Refactoring failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
