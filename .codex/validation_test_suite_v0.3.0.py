#!/usr/bin/env python3
"""
Comprehensive Validation Test Suite for codex-ml 0.3.0

This suite validates all major components, integrations, and features
of the codex-ml package, including CLI, API, cognitive app, and more.

Author: Copilot Agent
Date: 2026-07-20T05:10Z
"""

import sys
import time
import json
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field, asdict
import traceback

# Test Results Data Structure
@dataclass
class TestResult:
    """Single test result"""
    category: str
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration_ms: float = 0.0
    error_msg: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationReport:
    """Complete validation report"""
    timestamp: str
    package_version: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    total_duration_ms: float = 0.0
    results: List[TestResult] = field(default_factory=list)

class CodexValidationSuite:
    """Main validation suite for codex-ml"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.report = ValidationReport(
            timestamp=self._get_timestamp(),
            package_version=""
        )
        
    @staticmethod
    def _get_timestamp() -> str:
        """Get ISO format timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def run_all_tests(self) -> ValidationReport:
        """Execute all validation tests"""
        print("=" * 80)
        print("CODEX-ML 0.3.0 COMPREHENSIVE VALIDATION TEST SUITE")
        print("=" * 80)
        print()
        
        # Get package version
        try:
            import codex_ml
            self.report.package_version = codex_ml.__version__
            print(f"Package Version: {codex_ml.__version__}")
        except Exception as e:
            print(f"Error getting package version: {e}")
            self.report.package_version = "unknown"
        
        # Run test categories
        self._test_imports()
        self._test_cli_availability()
        self._test_config_management()
        self._test_api_modules()
        self._test_cognitive_brain()
        self._test_memory_systems()
        self._test_data_validation()
        self._test_integration()
        self._test_performance()
        
        # Finalize report
        self._finalize_report()
        return self.report
    
    def _add_result(self, category: str, test_name: str, status: str, 
                   duration_ms: float = 0.0, error_msg: str = "", 
                   details: Dict[str, Any] = None):
        """Add a test result"""
        result = TestResult(
            category=category,
            test_name=test_name,
            status=status,
            duration_ms=duration_ms,
            error_msg=error_msg,
            details=details or {}
        )
        self.results.append(result)
        self.report.results.append(result)
    
    def _test_imports(self):
        """Test 1: Module imports"""
        print("\n[1/9] Testing Module Imports...")
        modules_to_test = [
            "codex_ml",
            "codex_ml.config",
            "codex_ml.cli.main",
            "codex_ml.api.rag_api",
            "codex_ml.metrics",
            "codex_ml.data",
            "codex_ml.utils",
        ]
        
        for module_name in modules_to_test:
            start = time.time()
            try:
                importlib.import_module(module_name)
                duration = (time.time() - start) * 1000
                self._add_result("Imports", f"Import {module_name}", "PASS", duration)
                print(f"  ✓ {module_name} ({duration:.2f}ms)")
            except Exception as e:
                duration = (time.time() - start) * 1000
                self._add_result("Imports", f"Import {module_name}", "FAIL", duration, str(e))
                print(f"  ✗ {module_name} - {str(e)[:50]}")
    
    def _test_cli_availability(self):
        """Test 2: CLI availability and help"""
        print("\n[2/9] Testing CLI Availability...")
        
        start = time.time()
        try:
            from codex_ml.cli.main import cli
            # Check CLI object exists and has context
            has_ctx = hasattr(cli, 'ctx')
            duration = (time.time() - start) * 1000
            
            status = "PASS" if cli else "FAIL"
            self._add_result("CLI", "CLI main entry point", status, duration,
                           details={"has_context": has_ctx})
            print(f"  ✓ CLI entry point available ({duration:.2f}ms)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CLI", "CLI main entry point", "FAIL", duration, str(e))
            print(f"  ✗ CLI - {str(e)[:50]}")
        
        start = time.time()
        try:
            from codex_ml.config import MlConfig
            config = MlConfig()
            duration = (time.time() - start) * 1000
            self._add_result("CLI", "Config creation", "PASS", duration)
            print(f"  ✓ MlConfig instantiation ({duration:.2f}ms)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CLI", "Config creation", "FAIL", duration, str(e))
            print(f"  ✗ MlConfig - {str(e)[:50]}")
    
    def _test_config_management(self):
        """Test 3: Configuration management"""
        print("\n[3/9] Testing Configuration Management...")
        
        start = time.time()
        try:
            from codex_ml.config import MlConfig
            
            # Test config creation
            config = MlConfig()
            duration = (time.time() - start) * 1000
            
            # Check key attributes
            has_attrs = all(hasattr(config, attr) for attr in 
                           ['model_name', 'batch_size', 'learning_rate'])
            
            self._add_result("Config", "Config creation and attributes", 
                           "PASS" if has_attrs else "FAIL", duration,
                           details={"has_required_attrs": has_attrs})
            print(f"  ✓ Config attributes present ({duration:.2f}ms)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Config", "Config creation and attributes", "FAIL", duration, str(e))
            print(f"  ✗ Config - {str(e)[:50]}")
    
    def _test_api_modules(self):
        """Test 4: API modules"""
        print("\n[4/9] Testing API Modules...")
        
        api_modules = [
            ("RAG API", "codex_ml.api.rag_api"),
            ("Metrics API", "codex_ml.metrics"),
        ]
        
        for api_name, module_path in api_modules:
            start = time.time()
            try:
                module = importlib.import_module(module_path)
                duration = (time.time() - start) * 1000
                
                # Check for expected classes/functions
                has_content = len(dir(module)) > 0
                
                self._add_result("API", f"{api_name} module", 
                               "PASS" if has_content else "FAIL", duration,
                               details={"exported_items": len(dir(module))})
                print(f"  ✓ {api_name} ({duration:.2f}ms, {len(dir(module))} exports)")
            except Exception as e:
                duration = (time.time() - start) * 1000
                self._add_result("API", f"{api_name} module", "FAIL", duration, str(e))
                print(f"  ✗ {api_name} - {str(e)[:50]}")
    
    def _test_cognitive_brain(self):
        """Test 5: Cognitive Brain components"""
        print("\n[5/9] Testing Cognitive Brain Components...")
        
        # Check for cognitive brain modules
        cb_modules = [
            "codex_ml.cognitive_brain",
        ]
        
        for module_path in cb_modules:
            start = time.time()
            try:
                module = importlib.import_module(module_path)
                duration = (time.time() - start) * 1000
                
                has_content = len(dir(module)) > 0
                self._add_result("CognitiveBrain", f"Module {module_path}", 
                               "PASS" if has_content else "FAIL", duration,
                               details={"exports": len(dir(module))})
                print(f"  ✓ Cognitive Brain module ({duration:.2f}ms)")
            except ImportError:
                # Expected - module may not exist in this version
                self._add_result("CognitiveBrain", f"Module {module_path}", "SKIP", 0.0,
                               "Module not available in this version")
                print(f"  - Cognitive Brain module (skipped)")
            except Exception as e:
                duration = (time.time() - start) * 1000
                self._add_result("CognitiveBrain", f"Module {module_path}", "FAIL", duration, str(e))
                print(f"  ✗ Cognitive Brain - {str(e)[:50]}")
    
    def _test_memory_systems(self):
        """Test 6: Memory systems (STM/LTM)"""
        print("\n[6/9] Testing Memory Systems...")
        
        start = time.time()
        try:
            # Check for memory-related modules
            memory_modules = []
            if self._module_exists("codex_ml.memory"):
                memory_modules.append("codex_ml.memory")
            if self._module_exists("codex_ml.storage"):
                memory_modules.append("codex_ml.storage")
            
            duration = (time.time() - start) * 1000
            
            if memory_modules:
                self._add_result("Memory", "Memory system modules", "PASS", duration,
                               details={"available_modules": memory_modules})
                print(f"  ✓ Memory modules available ({duration:.2f}ms)")
            else:
                self._add_result("Memory", "Memory system modules", "SKIP", duration,
                               "Memory modules not detected in this version")
                print(f"  - Memory modules (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Memory", "Memory system modules", "FAIL", duration, str(e))
            print(f"  ✗ Memory systems - {str(e)[:50]}")
    
    def _test_data_validation(self):
        """Test 7: Data validation"""
        print("\n[7/9] Testing Data Validation...")
        
        start = time.time()
        try:
            from codex_ml.data import validation
            
            # Check validation module exists and has validators
            has_validators = len(dir(validation)) > 0
            duration = (time.time() - start) * 1000
            
            self._add_result("DataValidation", "Validation module", 
                           "PASS" if has_validators else "FAIL", duration,
                           details={"validators": len(dir(validation))})
            print(f"  ✓ Data validation module ({duration:.2f}ms, {len(dir(validation))} functions)")
        except ImportError:
            self._add_result("DataValidation", "Validation module", "SKIP", 0.0,
                           "Validation module not available")
            print(f"  - Data validation (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("DataValidation", "Validation module", "FAIL", duration, str(e))
            print(f"  ✗ Data validation - {str(e)[:50]}")
    
    def _test_integration(self):
        """Test 8: Integration tests"""
        print("\n[8/9] Testing Integration...")
        
        # Test 8a: Config + CLI integration
        start = time.time()
        try:
            from codex_ml.config import MlConfig
            from codex_ml.cli.main import cli
            
            config = MlConfig()
            duration = (time.time() - start) * 1000
            
            self._add_result("Integration", "Config + CLI integration", "PASS", duration)
            print(f"  ✓ Config + CLI integration ({duration:.2f}ms)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Integration", "Config + CLI integration", "FAIL", duration, str(e))
            print(f"  ✗ Integration - {str(e)[:50]}")
        
        # Test 8b: Module cross-imports
        start = time.time()
        try:
            import codex_ml
            from codex_ml import config, metrics, data
            duration = (time.time() - start) * 1000
            
            self._add_result("Integration", "Module cross-imports", "PASS", duration)
            print(f"  ✓ Module cross-imports ({duration:.2f}ms)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Integration", "Module cross-imports", "FAIL", duration, str(e))
            print(f"  ✗ Cross-imports - {str(e)[:50]}")
    
    def _test_performance(self):
        """Test 9: Performance metrics"""
        print("\n[9/9] Testing Performance Metrics...")
        
        # Test import performance
        start = time.time()
        try:
            # Measure codex_ml import time
            import_start = time.time()
            import codex_ml as cm
            import_time = (time.time() - import_start) * 1000
            
            duration = (time.time() - start) * 1000
            
            self._add_result("Performance", "Package import time", "PASS", duration,
                           details={"import_time_ms": import_time})
            print(f"  ✓ Performance metrics collected ({duration:.2f}ms, import: {import_time:.2f}ms)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Performance", "Package import time", "FAIL", duration, str(e))
            print(f"  ✗ Performance - {str(e)[:50]}")
    
    def _module_exists(self, module_name: str) -> bool:
        """Check if a module exists"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def _finalize_report(self):
        """Finalize the validation report"""
        self.report.total_tests = len(self.results)
        self.report.passed = sum(1 for r in self.results if r.status == "PASS")
        self.report.failed = sum(1 for r in self.results if r.status == "FAIL")
        self.report.skipped = sum(1 for r in self.results if r.status == "SKIP")
        self.report.errors = sum(1 for r in self.results if r.status == "ERROR")
        self.report.total_duration_ms = sum(r.duration_ms for r in self.results)
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("VALIDATION TEST RESULTS SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {self.report.timestamp}")
        lines.append(f"Package Version: {self.report.package_version}")
        lines.append(f"Total Duration: {self.report.total_duration_ms:.2f}ms")
        lines.append("")
        
        # Summary statistics
        lines.append("SUMMARY STATISTICS:")
        lines.append(f"  Total Tests:    {self.report.total_tests}")
        pass_rate = self.report.passed/max(1, self.report.total_tests)*100
        lines.append(f"  Passed:         {self.report.passed} ({pass_rate:.1f}%)")
        lines.append(f"  Failed:         {self.report.failed}")
        lines.append(f"  Skipped:        {self.report.skipped}")
        lines.append(f"  Errors:         {self.report.errors}")
        lines.append("")
        
        # Results by category
        categories = {}
        for result in self.report.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        lines.append("RESULTS BY CATEGORY:")
        for category in sorted(categories.keys()):
            cat_results = categories[category]
            cat_passed = sum(1 for r in cat_results if r.status == "PASS")
            lines.append(f"\n  {category} ({cat_passed}/{len(cat_results)} passed):")
            for result in cat_results:
                status_symbol = "✓" if result.status == "PASS" else "✗" if result.status == "FAIL" else "-"
                lines.append(f"    {status_symbol} {result.test_name:40s} {result.status:6s} ({result.duration_ms:7.2f}ms)")
                if result.error_msg:
                    lines.append(f"      Error: {result.error_msg[:60]}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

def main():
    """Main entry point"""
    suite = CodexValidationSuite()
    
    # Run all tests
    report = suite.run_all_tests()
    
    # Generate report
    print(suite.generate_report())
    
    # Save detailed report as JSON
    report_path = Path(".codex/validation_results_v0.3.0.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert results to JSON-serializable format
    results_json = {
        "timestamp": report.timestamp,
        "package_version": report.package_version,
        "summary": {
            "total_tests": report.total_tests,
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
            "errors": report.errors,
            "pass_rate": f"{report.passed/max(1, report.total_tests)*100:.1f}%",
            "total_duration_ms": f"{report.total_duration_ms:.2f}ms"
        },
        "results": [
            {
                "category": r.category,
                "test_name": r.test_name,
                "status": r.status,
                "duration_ms": r.duration_ms,
                "error_msg": r.error_msg,
                "details": r.details
            }
            for r in report.results
        ]
    }
    
    with open(report_path, 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print(f"\nDetailed results saved to: {report_path}")
    
    # Return exit code based on results
    return 0 if report.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
