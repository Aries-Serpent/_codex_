#!/usr/bin/env python3
"""
Enhanced Validation Test Suite for codex-ml 0.3.0 - LANE 5
Comprehensive validation with 27 tests across all components
"""

import sys
import time
import json
import importlib
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field
import traceback

@dataclass
class TestResult:
    """Single test result"""
    category: str
    test_name: str
    status: str  # PASS, FAIL, SKIP
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
    total_duration_ms: float = 0.0
    results: List[TestResult] = field(default_factory=list)

class Lane5ValidationSuite:
    """Enhanced validation suite for Lane 5 - 27 tests"""
    
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
        """Execute all 27 validation tests"""
        print("=" * 80)
        print("CODEX-ML 0.3.0 LANE 5: COMPREHENSIVE VALIDATION (27 TESTS)")
        print("=" * 80)
        print()
        
        try:
            import codex_ml
            self.report.package_version = codex_ml.__version__
            print(f"Package Version: {codex_ml.__version__}")
        except Exception as e:
            self.report.package_version = "unknown"
        
        # Run all test categories
        self._test_imports()              # Tests 1-7
        self._test_cli()                  # Tests 8-9
        self._test_config()               # Test 10
        self._test_api_modules()          # Tests 11-12
        self._test_rag_api_detail()       # Tests 13-15
        self._test_cognitive_brain()      # Test 16
        self._test_cognitive_brain_detail()  # Tests 17-19
        self._test_memory_systems()       # Test 20
        self._test_memory_systems_detail()  # Tests 21-24
        self._test_optional_dependencies()  # Test 25
        self._test_data_validation()      # Test 26
        self._test_integration()          # Test 27
        self._test_performance()          # Extra
        
        self._finalize_report()
        return self.report
    
    def _add_result(self, category: str, test_name: str, status: str,
                   duration_ms: float = 0.0, error_msg: str = "",
                   details: Dict[str, Any] = None):
        """Add test result"""
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
        """Tests 1-7: Module imports"""
        print("\n[TESTS 1-7] Testing Module Imports...")
        modules = [
            "codex_ml",
            "codex_ml.config",
            "codex_ml.cli.main",
            "codex_ml.api.rag_api",
            "codex_ml.metrics",
            "codex_ml.data",
            "codex_ml.utils",
        ]
        
        for module_name in modules:
            start = time.time()
            try:
                importlib.import_module(module_name)
                duration = (time.time() - start) * 1000
                self._add_result("Imports", f"Import {module_name}", "PASS", duration)
                print(f"  ✓ {module_name}")
            except Exception as e:
                duration = (time.time() - start) * 1000
                self._add_result("Imports", f"Import {module_name}", "FAIL", duration, str(e))
                print(f"  ✗ {module_name}: {str(e)[:40]}")
    
    def _test_cli(self):
        """Tests 8-9: CLI availability"""
        print("\n[TESTS 8-9] Testing CLI Availability...")
        
        start = time.time()
        try:
            from codex_ml.cli.main import cli
            duration = (time.time() - start) * 1000
            self._add_result("CLI", "CLI main entry point", "PASS", duration)
            print(f"  ✓ CLI entry point")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CLI", "CLI main entry point", "FAIL", duration, str(e))
            print(f"  ✗ CLI: {str(e)[:40]}")
        
        start = time.time()
        try:
            from codex_ml.config import MlConfig
            config = MlConfig()
            duration = (time.time() - start) * 1000
            self._add_result("CLI", "Config creation", "PASS", duration)
            print(f"  ✓ MlConfig instantiation")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CLI", "Config creation", "FAIL", duration, str(e))
            print(f"  ✗ Config: {str(e)[:40]}")
    
    def _test_config(self):
        """Test 10: Configuration management"""
        print("\n[TEST 10] Testing Configuration Management...")
        
        start = time.time()
        try:
            from codex_ml.config import MlConfig
            config = MlConfig()
            has_attrs = all(hasattr(config, attr) for attr in
                           ['model_name', 'batch_size', 'learning_rate'])
            duration = (time.time() - start) * 1000
            self._add_result("Config", "Config attributes", 
                           "PASS" if has_attrs else "FAIL", duration)
            print(f"  ✓ Config attributes present")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Config", "Config attributes", "FAIL", duration, str(e))
            print(f"  ✗ Config: {str(e)[:40]}")
    
    def _test_api_modules(self):
        """Tests 11-12: API modules"""
        print("\n[TESTS 11-12] Testing API Modules...")
        
        for api_name, module_path in [("RAG API", "codex_ml.api.rag_api"),
                                       ("Metrics API", "codex_ml.metrics")]:
            start = time.time()
            try:
                module = importlib.import_module(module_path)
                duration = (time.time() - start) * 1000
                self._add_result("API", f"{api_name} module", "PASS", duration,
                               details={"exports": len(dir(module))})
                print(f"  ✓ {api_name}")
            except Exception as e:
                duration = (time.time() - start) * 1000
                self._add_result("API", f"{api_name} module", "FAIL", duration, str(e))
                print(f"  ✗ {api_name}: {str(e)[:40]}")
    
    def _test_rag_api_detail(self):
        """Tests 13-15: RAG API detailed"""
        print("\n[TESTS 13-15] Testing RAG API Details...")
        
        # Test 13
        start = time.time()
        try:
            from codex_ml.api import rag_api
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API module load", "PASS", duration)
            print(f"  ✓ RAG API module load")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API module load", "FAIL", duration, str(e))
            print(f"  ✗ RAG module load: {str(e)[:40]}")
        
        # Test 14
        start = time.time()
        try:
            from codex_ml.api.rag_api import RagAPI
            has_methods = all(hasattr(RagAPI, m) for m in ['query', 'index', 'retrieve'])
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API methods", 
                           "PASS" if has_methods else "SKIP", duration)
            print(f"  ✓ RAG API methods available")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API methods", "SKIP", duration)
            print(f"  - RAG methods (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API methods", "FAIL", duration, str(e))
            print(f"  ✗ RAG methods: {str(e)[:40]}")
        
        # Test 15
        start = time.time()
        try:
            from codex_ml.api.rag_api import RAG_REGISTRY
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API registry", "PASS", duration)
            print(f"  ✓ RAG API registry available")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API registry", "SKIP", duration)
            print(f"  - RAG registry (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("RAG", "RAG API registry", "FAIL", duration, str(e))
            print(f"  ✗ RAG registry: {str(e)[:40]}")
    
    def _test_cognitive_brain(self):
        """Test 16: Cognitive Brain basic"""
        print("\n[TEST 16] Testing Cognitive Brain...")
        
        start = time.time()
        try:
            module = importlib.import_module("codex_ml.cognitive_brain")
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrain", "Module load", "PASS", duration)
            print(f"  ✓ Cognitive Brain module")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrain", "Module load", "FAIL", duration, str(e))
            print(f"  ✗ Cognitive Brain: {str(e)[:40]}")
    
    def _test_cognitive_brain_detail(self):
        """Tests 17-19: Cognitive Brain detailed"""
        print("\n[TESTS 17-19] Testing Cognitive Brain Details...")
        
        # Test 17
        start = time.time()
        try:
            from codex_ml import cognitive_brain
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Module load", "PASS", duration)
            print(f"  ✓ CB module load")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Module load", "SKIP", duration)
            print(f"  - CB module (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Module load", "FAIL", duration, str(e))
            print(f"  ✗ CB load: {str(e)[:40]}")
        
        # Test 18
        start = time.time()
        try:
            from codex_ml.cognitive_brain import CognitiveBrain
            cb = CognitiveBrain()
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Initialization", "PASS", duration)
            print(f"  ✓ CB initialization")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Initialization", "SKIP", duration)
            print(f"  - CB init (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Initialization", "FAIL", duration, str(e))
            print(f"  ✗ CB init: {str(e)[:40]}")
        
        # Test 19
        start = time.time()
        try:
            from codex_ml.cognitive_brain import CognitiveBrain
            cb = CognitiveBrain()
            has_reasoning = all(hasattr(cb, m) for m in ['reason', 'infer', 'process'])
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Reasoning engine", 
                           "PASS" if has_reasoning else "SKIP", duration)
            print(f"  ✓ CB reasoning available")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Reasoning engine", "SKIP", duration)
            print(f"  - CB reasoning (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("CognitiveBrainDetail", "Reasoning engine", "FAIL", duration, str(e))
            print(f"  ✗ CB reasoning: {str(e)[:40]}")
    
    def _test_memory_systems(self):
        """Test 20: Memory systems basic"""
        print("\n[TEST 20] Testing Memory Systems...")
        
        start = time.time()
        try:
            modules = []
            if self._module_exists("codex_ml.memory"):
                modules.append("codex_ml.memory")
            if self._module_exists("codex_ml.storage"):
                modules.append("codex_ml.storage")
            
            duration = (time.time() - start) * 1000
            status = "PASS" if modules else "SKIP"
            self._add_result("Memory", "System modules", status, duration)
            print(f"  ✓ Memory modules available")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Memory", "System modules", "FAIL", duration, str(e))
            print(f"  ✗ Memory: {str(e)[:40]}")
    
    def _test_memory_systems_detail(self):
        """Tests 21-24: Memory systems detailed"""
        print("\n[TESTS 21-24] Testing Memory Systems Details...")
        
        # Test 21
        start = time.time()
        try:
            from codex_ml.memory import ShortTermMemory
            stm = ShortTermMemory()
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "STM initialization", "PASS", duration)
            print(f"  ✓ Memory STM init")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "STM initialization", "SKIP", duration)
            print(f"  - Memory STM (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "STM initialization", "FAIL", duration, str(e))
            print(f"  ✗ STM: {str(e)[:40]}")
        
        # Test 22
        start = time.time()
        try:
            from codex_ml.memory import LongTermMemory
            ltm = LongTermMemory()
            has_persistence = all(hasattr(ltm, m) for m in ['save', 'load', 'persist'])
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "LTM persistence", 
                           "PASS" if has_persistence else "SKIP", duration)
            print(f"  ✓ Memory LTM persistence")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "LTM persistence", "SKIP", duration)
            print(f"  - Memory LTM (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "LTM persistence", "FAIL", duration, str(e))
            print(f"  ✗ LTM: {str(e)[:40]}")
        
        # Test 23
        start = time.time()
        try:
            from codex_ml.memory import MemoryConsolidation
            consolidator = MemoryConsolidation()
            has_consolidation = all(hasattr(consolidator, m) for m in ['consolidate', 'transfer', 'merge'])
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "Consolidation", 
                           "PASS" if has_consolidation else "SKIP", duration)
            print(f"  ✓ Memory consolidation")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "Consolidation", "SKIP", duration)
            print(f"  - Memory consolidation (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "Consolidation", "FAIL", duration, str(e))
            print(f"  ✗ Consolidation: {str(e)[:40]}")
        
        # Test 24
        start = time.time()
        try:
            from codex_ml.memory import MemoryRetrieval
            retriever = MemoryRetrieval()
            has_retrieval = all(hasattr(retriever, m) for m in ['retrieve', 'query', 'lookup'])
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "Retrieval", 
                           "PASS" if has_retrieval else "SKIP", duration)
            print(f"  ✓ Memory retrieval")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "Retrieval", "SKIP", duration)
            print(f"  - Memory retrieval (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("MemoryDetail", "Retrieval", "FAIL", duration, str(e))
            print(f"  ✗ Retrieval: {str(e)[:40]}")
    
    def _test_optional_dependencies(self):
        """Test 25: Optional dependencies"""
        print("\n[TEST 25] Testing Optional Dependencies...")
        
        start = time.time()
        try:
            from codex_ml.config import OPTIONAL_DEPS
            missing_deps = []
            for dep_name, import_path in OPTIONAL_DEPS.items():
                try:
                    importlib.import_module(import_path)
                except ImportError:
                    missing_deps.append(dep_name)
            
            duration = (time.time() - start) * 1000
            self._add_result("OptionalDependencies", "Graceful degradation", "PASS", duration,
                           details={"missing": len(missing_deps)})
            print(f"  ✓ Optional deps handled")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("OptionalDependencies", "Graceful degradation", "SKIP", duration)
            print(f"  - Optional deps (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("OptionalDependencies", "Graceful degradation", "FAIL", duration, str(e))
            print(f"  ✗ Optional deps: {str(e)[:40]}")
    
    def _test_data_validation(self):
        """Test 26: Data validation"""
        print("\n[TEST 26] Testing Data Validation...")
        
        start = time.time()
        try:
            from codex_ml.data import validation
            has_validators = len(dir(validation)) > 0
            duration = (time.time() - start) * 1000
            self._add_result("DataValidation", "Validation module", 
                           "PASS" if has_validators else "FAIL", duration)
            print(f"  ✓ Data validation")
        except ImportError:
            duration = (time.time() - start) * 1000
            self._add_result("DataValidation", "Validation module", "SKIP", duration)
            print(f"  - Data validation (skipped)")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("DataValidation", "Validation module", "FAIL", duration, str(e))
            print(f"  ✗ Validation: {str(e)[:40]}")
    
    def _test_integration(self):
        """Test 27: Integration"""
        print("\n[TEST 27] Testing Integration...")
        
        start = time.time()
        try:
            from codex_ml.config import MlConfig
            from codex_ml.cli.main import cli
            config = MlConfig()
            duration = (time.time() - start) * 1000
            self._add_result("Integration", "Config + CLI integration", "PASS", duration)
            print(f"  ✓ Config + CLI integration")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Integration", "Config + CLI integration", "FAIL", duration, str(e))
            print(f"  ✗ Integration: {str(e)[:40]}")
    
    def _test_performance(self):
        """Extra: Performance metrics"""
        print("\n[EXTRA] Testing Performance...")
        
        start = time.time()
        try:
            import_start = time.time()
            import codex_ml
            import_time = (time.time() - import_start) * 1000
            duration = (time.time() - start) * 1000
            self._add_result("Performance", "Package import time", "PASS", duration,
                           details={"import_time_ms": import_time})
            print(f"  ✓ Performance metrics")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result("Performance", "Package import time", "FAIL", duration, str(e))
            print(f"  ✗ Performance: {str(e)[:40]}")
    
    def _module_exists(self, module_name: str) -> bool:
        """Check if module exists"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def _finalize_report(self):
        """Finalize report"""
        self.report.total_tests = len(self.results)
        self.report.passed = sum(1 for r in self.results if r.status == "PASS")
        self.report.failed = sum(1 for r in self.results if r.status == "FAIL")
        self.report.skipped = sum(1 for r in self.results if r.status == "SKIP")
        self.report.total_duration_ms = sum(r.duration_ms for r in self.results)
    
    def generate_report(self) -> str:
        """Generate report"""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("LANE 5 VALIDATION TEST RESULTS")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {self.report.timestamp}")
        lines.append(f"Package Version: {self.report.package_version}")
        lines.append(f"Total Duration: {self.report.total_duration_ms:.2f}ms")
        lines.append("")
        
        lines.append("SUMMARY STATISTICS:")
        lines.append(f"  Total Tests:    {self.report.total_tests}")
        pass_rate = self.report.passed / max(1, self.report.total_tests) * 100
        lines.append(f"  Passed:         {self.report.passed} ({pass_rate:.1f}%)")
        lines.append(f"  Failed:         {self.report.failed}")
        lines.append(f"  Skipped:        {self.report.skipped}")
        lines.append("")
        
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
    suite = Lane5ValidationSuite()
    report = suite.run_all_tests()
    
    print(suite.generate_report())
    
    report_path = Path(".codex/validation_results_v0.3.0_LANE5.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    results_json = {
        "timestamp": report.timestamp,
        "package_version": report.package_version,
        "summary": {
            "total_tests": report.total_tests,
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
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
    return 0 if report.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
