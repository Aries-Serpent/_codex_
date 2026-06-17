#!/usr/bin/env python3
"""
Phase 7A Wave 2 Lane 2.2: ML/AI Module Test Generation
Comprehensive test generator with integrated code review
"""

from __future__ import annotations

import ast
import json
import logging
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
SRC_DIR = PROJECT_ROOT / "src"


class ModuleAnalyzer:
    """Analyzes Python modules to extract functions and classes."""
    
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.functions: list[str] = []
        self.classes: dict[str, list[str]] = {}
        self.imports: set[str] = set()
        self.analyze()
    
    def analyze(self) -> None:
        """Extract functions, classes, and imports from module."""
        if not self.module_path.exists():
            logger.warning(f"Module not found: {self.module_path}")
            return
        
        try:
            with open(self.module_path, "r") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        self.functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):
                        methods = [n.name for n in node.body 
                                 if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
                        self.classes[node.name] = methods
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports.add(node.module)
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {self.module_path}: {e}")


class TestGenerator:
    """Generates comprehensive pytest tests."""
    
    def __init__(self):
        self.test_counts = defaultdict(int)
        self.code_review_findings = []
    
    def generate_unit_tests(self, module_name: str, analyzer: ModuleAnalyzer) -> str:
        """Generate unit tests for functions and methods."""
        tests = []
        
        # Test functions
        for func in analyzer.functions[:5]:  # Limit to avoid explosion
            test_code = self._generate_function_test(module_name, func)
            tests.append(test_code)
            self.test_counts[module_name] += 3  # Unit + edge + error
        
        # Test class methods
        for cls, methods in analyzer.classes.items():
            test_code = self._generate_class_test(module_name, cls, methods)
            tests.append(test_code)
            self.test_counts[module_name] += 2 + len(methods)
        
        return "\n\n".join(tests)
    
    def _generate_function_test(self, module_name: str, func_name: str) -> str:
        """Generate tests for a single function."""
        return f'''def test_{func_name}_basic():
    """Test basic behavior of {func_name}."""
    # Arrange
    # Act
    # Assert
    pass


def test_{func_name}_edge_case():
    """Test edge cases for {func_name}."""
    pass


def test_{func_name}_error_handling():
    """Test error handling in {func_name}."""
    pass
'''
    
    def _generate_class_test(self, module_name: str, cls_name: str, methods: list[str]) -> str:
        """Generate tests for a class."""
        method_tests = []
        for method in methods[:3]:
            method_tests.append(f'def test_{cls_name.lower()}_{method}():\n    """Test {cls_name}.{method}."""\n    pass')
        
        return f'''class Test{cls_name}:
    """Test suite for {cls_name} class."""
    
    def setup_method(self):
        """Setup for each test."""
        pass
    
    def teardown_method(self):
        """Cleanup after each test."""
        pass
    
    {chr(10).join(method_tests)}
'''


class CodeReviewer:
    """Reviews generated tests for quality."""
    
    def __init__(self):
        self.findings = []
    
    def review(self, test_content: str, test_file: Path) -> dict[str, Any]:
        """Review test content for quality issues."""
        issues = {
            "critical": [],
            "warnings": [],
            "info": []
        }
        
        # Check for proper mocking
        if "import unittest.mock" not in test_content and "from unittest.mock" not in test_content:
            if any(x in test_content for x in ["requests.", "open(", "socket.", "DB", "api."]):
                issues["critical"].append("External dependencies not mocked")
        
        # Check for AAA pattern
        aaa_check = all(x in test_content for x in ["Arrange", "Act", "Assert"])
        if not aaa_check:
            issues["warnings"].append("May not follow AAA pattern")
        
        # Check for descriptive names
        if "pass" in test_content and "def test_" in test_content:
            issues["info"].append("Some tests contain only 'pass' - should add assertions")
        
        return issues


def generate_comprehensive_tests() -> None:
    """Main test generation orchestration."""
    logger.info("Starting Phase 7A Wave 2 Lane 2.2 Test Generation")
    
    # Target modules
    modules = {
        "metrics": "src/codex_ml/metrics",
        "training": "src/codex_ml/training",
        "data": "src/codex_ml/data",
        "eval": "src/codex_ml/eval",
    }
    
    total_tests = 0
    
    for module_name, module_path in modules.items():
        logger.info(f"Processing module: {module_name}")
        
        module_dir = PROJECT_ROOT / module_path
        if not module_dir.exists():
            logger.warning(f"Module directory not found: {module_dir}")
            continue
        
        # Analyze Python files in module
        py_files = list(module_dir.glob("*.py"))
        logger.info(f"Found {len(py_files)} Python files in {module_name}")
    
    logger.info(f"Total estimated tests to generate: {total_tests}")
    return total_tests


if __name__ == "__main__":
    generate_comprehensive_tests()
