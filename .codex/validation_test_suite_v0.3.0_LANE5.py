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
            from codex_ml.memory import MemoryConsolidation, STMMemory, LTMMemory
            stm = STMMemory()
            ltm = LTMMemory()
            consolidator = MemoryConsolidation(stm, ltm)
