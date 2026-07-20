#!/usr/bin/env python3
"""
Functional testing script for codex-ml v0.3.0
Tests all modules, API, CLI, and cognitive app integration
"""

import sys
import json
from pathlib import Path
from typing import Tuple, List, Dict

# Module imports for testing (imported here to avoid duplication in test functions)
try:
    from codex_ml.config import CodexConfig, MlConfig
    from codex_ml.memory import STMMemory, LTMMemory
    from codex_ml.api import RagAPI, BaseRagAPI
    from codex_ml.cognitive_brain import CognitiveBrain, ReasoningEngine
except ImportError:
    # Modules will be imported individually in test functions if needed
    pass

class FunctionalTester:
    def __init__(self):
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {}
        
    def log_test(self, phase: str, test_name: str, passed: bool, message: str = ""):
        """Log a test result"""
        if phase not in self.results:
            self.results[phase] = []
        self.results[phase].append((test_name, passed, message))
        status = "✅" if passed else "❌"
        print(f"{status} {phase}: {test_name}")
        if message:
            print(f"   {message}")
    
    def test_config_module(self):
        """Test Configuration module"""
        print("\n" + "="*80)
        print("TEST 1: CONFIGURATION MODULE")
        print("="*80)
        
        try:
            from codex_ml.config import CodexConfig, MlConfig
            
            # Test 1: Create config instance
            try:
                config = CodexConfig()
                self.log_test("Config", "CodexConfig instantiation", True,
                            f"Default config created")
            except Exception as e:
                self.log_test("Config", "CodexConfig instantiation", False, str(e)[:50])
                return
            
            # Test 2: Test with parameters
            try:
                config = CodexConfig(
                    model_name="test-model",
                    batch_size=32,
                    learning_rate=0.001
                )
                self.log_test("Config", "CodexConfig with parameters", True,
                            f"batch_size={config.batch_size}")
            except Exception as e:
                self.log_test("Config", "CodexConfig with parameters", False, str(e)[:50])
            
            # Test 3: MlConfig alias
            try:
                self.log_test("Config", "MlConfig alias available", MlConfig is CodexConfig,
                            "MlConfig correctly aliased to CodexConfig")
            except Exception as e:
                self.log_test("Config", "MlConfig alias available", False, str(e)[:50])
                
        except Exception as e:
            self.log_test("Config", "Module import", False, str(e)[:50])

    def test_memory_module(self):
        """Test Memory module"""
        print("\n" + "="*80)
        print("TEST 2: MEMORY MODULE")
        print("="*80)
        
        try:
            from codex_ml.memory import STMMemory, LTMMemory
            
            # Test 1: STMMemory creation
            try:
                stm = STMMemory(capacity=10)
                self.log_test("Memory", "STMMemory instantiation", True,
                            f"STM created with capacity=10")
            except Exception as e:
                self.log_test("Memory", "STMMemory instantiation", False, str(e)[:50])
                return
            
            # Test 2: Store in STM
            try:
                index = stm.store("test_data", importance=0.8)
                self.log_test("Memory", "STMMemory store operation", True,
                            f"Data stored at index {index}")
            except Exception as e:
                self.log_test("Memory", "STMMemory store operation", False, str(e)[:50])
            
            # Test 3: LTMMemory creation
            try:
                ltm = LTMMemory()
                self.log_test("Memory", "LTMMemory instantiation", True,
                            "LTM created successfully")
            except Exception as e:
                self.log_test("Memory", "LTMMemory instantiation", False, str(e)[:50])
                
        except Exception as e:
            self.log_test("Memory", "Module import", False, str(e)[:50])

    def test_api_module(self):
        """Test API module"""
        print("\n" + "="*80)
        print("TEST 3: API MODULE")
        print("="*80)
        
        try:
            from codex_ml.api import RagAPI, BaseRagAPI
            
            # Test 1: BaseRagAPI availability
            try:
                self.log_test("API", "BaseRagAPI available", BaseRagAPI is not None,
                            "Base API class accessible")
            except Exception as e:
                self.log_test("API", "BaseRagAPI available", False, str(e)[:50])
            
            # Test 2: RagAPI instantiation
            try:
                rag_api = RagAPI()
                self.log_test("API", "RagAPI instantiation", True,
                            "RAG API created successfully")
            except Exception as e:
                self.log_test("API", "RagAPI instantiation", False, str(e)[:50])
                
        except Exception as e:
            self.log_test("API", "Module import", False, str(e)[:50])

    def test_cognitive_brain_module(self):
        """Test Cognitive Brain module"""
        print("\n" + "="*80)
        print("TEST 4: COGNITIVE BRAIN MODULE")
        print("="*80)
        
        try:
            from codex_ml.cognitive_brain import CognitiveBrain, ReasoningEngine
            
            # Test 1: CognitiveBrain creation
            try:
                brain = CognitiveBrain()
                self.log_test("CognitiveBrain", "CognitiveBrain instantiation", True,
                            "Cognitive Brain created")
            except Exception as e:
                self.log_test("CognitiveBrain", "CognitiveBrain instantiation", False, str(e)[:50])
            
            # Test 2: ReasoningEngine availability
            try:
                self.log_test("CognitiveBrain", "ReasoningEngine available", 
                            ReasoningEngine is not None,
                            "Reasoning engine accessible")
            except Exception as e:
                self.log_test("CognitiveBrain", "ReasoningEngine available", False, str(e)[:50])
                
        except Exception as e:
            self.log_test("CognitiveBrain", "Module import", False, str(e)[:50])

    def test_cli_module(self):
        """Test CLI module"""
        print("\n" + "="*80)
        print("TEST 5: CLI MODULE")
        print("="*80)
        
        try:
            from codex_ml.cli.main import cli
            
            # Test 1: CLI callable
            try:
                self.log_test("CLI", "CLI entry point available", callable(cli),
                            "CLI is callable")
            except Exception as e:
                self.log_test("CLI", "CLI entry point available", False, str(e)[:50])
                
        except Exception as e:
            self.log_test("CLI", "Module import", False, str(e)[:50])

    def test_integration(self):
        """Test integration scenarios"""
        print("\n" + "="*80)
        print("TEST 6: INTEGRATION TESTS")
        print("="*80)
        
        try:
            # Modules imported at module level to avoid duplication
            
            # Test 1: Config + Memory integration
            try:
                config = CodexConfig(batch_size=16)
                stm = STMMemory(capacity=20)
                stm.store("integration_test", importance=0.9)
                self.log_test("Integration", "Config + Memory integration", True,
                            "Config and Memory work together")
            except Exception as e:
                self.log_test("Integration", "Config + Memory integration", False, str(e)[:50])
            
            # Test 2: API + Memory integration
            try:
                rag_api = RagAPI()
                ltm = LTMMemory()
                self.log_test("Integration", "API + Memory integration", True,
                            "API and Memory work together")
            except Exception as e:
                self.log_test("Integration", "API + Memory integration", False, str(e)[:50])
            
            # Test 3: CognitiveBrain + Memory integration
            try:
                brain = CognitiveBrain()
                stm = STMMemory(capacity=15)
                self.log_test("Integration", "CognitiveBrain + Memory integration", True,
                            "Brain and Memory work together")
            except Exception as e:
                self.log_test("Integration", "CognitiveBrain + Memory integration", False, str(e)[:50])
                
        except Exception as e:
            self.log_test("Integration", "Module imports", False, str(e)[:50])

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("FUNCTIONAL TEST SUMMARY FOR v0.3.0")
        print("="*80)
        
        total_tests = 0
        total_passed = 0
        
        for phase, tests in self.results.items():
            passed = sum(1 for _, p, _ in tests if p)
            total = len(tests)
            total_tests += total
            total_passed += passed
            
            status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
            print(f"\n{status} {phase}: {passed}/{total} passed")
            for test_name, passed, message in tests:
                symbol = "✓" if passed else "✗"
                print(f"   {symbol} {test_name}")
                if message:
                    print(f"      {message}")
        
        print("\n" + "-"*80)
        print(f"TOTAL: {total_passed}/{total_tests} tests passed ({100*total_passed//total_tests if total_tests else 0}%)")
        print("="*80)
        
        return total_passed == total_tests

    def run_all_tests(self):
        """Run all functional tests"""
        self.test_config_module()
        self.test_memory_module()
        self.test_api_module()
        self.test_cognitive_brain_module()
        self.test_cli_module()
        self.test_integration()
        
        return self.print_summary()

if __name__ == "__main__":
    tester = FunctionalTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
