#!/usr/bin/env python3
"""
Comprehensive deployment validation script for codex-ml v0.3.0
Tests GitHub Pages deployment, cognitive app functionality, and package functionality
"""

import subprocess
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple

class DeploymentValidator:
    def __init__(self):
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {}
        self.repo_root = Path(__file__).parent.parent
        
    def log_test(self, phase: str, test_name: str, passed: bool, message: str = ""):
        """Log a test result"""
        if phase not in self.results:
            self.results[phase] = []
        self.results[phase].append((test_name, passed, message))
        status = "✅" if passed else "❌"
        print(f"{status} {phase}: {test_name}")
        if message:
            print(f"   {message}")
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*80)
        print("DEPLOYMENT VALIDATION SUMMARY FOR v0.3.0")
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
                if message and not passed:
                    print(f"      {message}")
        
        print("\n" + "-"*80)
        print(f"TOTAL: {total_passed}/{total_tests} tests passed ({100*total_passed//total_tests if total_tests else 0}%)")
        print("="*80)
        
        return total_passed == total_tests

    def test_pages_deployment(self):
        """Phase 1: Validate GitHub Pages deployment"""
        print("\n" + "="*80)
        print("PHASE 1: VALIDATE GITHUB PAGES DEPLOYMENT")
        print("="*80)
        
        # Test 1: Main documentation site
        try:
            req = urllib.request.Request(
                "https://aries-serpent.github.io/_codex_/",
                headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read(2000).decode('utf-8', errors='ignore')
                has_mkdocs = 'site_name' in content or 'mkdocs' in content.lower()
                self.log_test("Phase 1", "Main docs site accessible", response.status == 200, 
                            f"HTTP {response.status}")
                self.log_test("Phase 1", "MkDocs site detected", has_mkdocs, "")
        except Exception as e:
            self.log_test("Phase 1", "Main docs site accessible", False, str(e)[:50])

        # Test 2: Cognitive app accessible
        try:
            req = urllib.request.Request(
                "https://aries-serpent.github.io/_codex_/cognitive_app/",
                headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read(5000).decode('utf-8', errors='ignore')
                self.log_test("Phase 1", "Cognitive app accessible", response.status == 200,
                            f"HTTP {response.status}")
                
                # Test 3: React app indicators
                has_root = '<div id="root">' in content
                self.log_test("Phase 1", "React root div present", has_root, "")
                
                has_module = 'type="module"' in content
                self.log_test("Phase 1", "Module script present", has_module, "")
                
                has_css = '<link rel="stylesheet"' in content
                self.log_test("Phase 1", "CSS link present", has_css, "")
                
                correct_assets = '/_codex_/cognitive_app/assets' in content
                self.log_test("Phase 1", "Asset path correct", correct_assets,
                            "Paths should include /_codex_/cognitive_app/assets")
        except Exception as e:
            self.log_test("Phase 1", "Cognitive app accessible", False, str(e)[:50])

    def test_local_deployment(self):
        """Phase 2: Test local deployment files"""
        print("\n" + "="*80)
        print("PHASE 2: TEST LOCAL DEPLOYMENT FILES")
        print("="*80)
        
        # Test 1: site/cognitive_app exists
        site_app_path = self.repo_root / "site" / "cognitive_app"
        self.log_test("Phase 2", "site/cognitive_app directory exists", site_app_path.exists(),
                    f"Path: {site_app_path}")
        
        # Test 2: index.html exists and has correct structure
        if site_app_path.exists():
            index_path = site_app_path / "index.html"
            self.log_test("Phase 2", "index.html exists", index_path.exists(),
                        f"Path: {index_path}")
            
            if index_path.exists():
                content = index_path.read_text(encoding='utf-8')
                has_root = '<div id="root">' in content
                self.log_test("Phase 2", "index.html has root div", has_root, "")
                
                has_script = 'type="module"' in content
                self.log_test("Phase 2", "index.html has module script", has_script, "")

        # Test 3: assets directory exists
        assets_path = site_app_path / "assets"
        if site_app_path.exists():
            self.log_test("Phase 2", "assets directory exists", assets_path.exists(),
                        f"Path: {assets_path}")
            
            if assets_path.exists():
                js_files = list(assets_path.glob("*.js"))
                css_files = list(assets_path.glob("*.css"))
                has_js = len(js_files) > 0
                has_css = len(css_files) > 0
                
                self.log_test("Phase 2", "JavaScript assets deployed", has_js,
                            f"Found {len(js_files)} .js files")
                self.log_test("Phase 2", "CSS assets deployed", has_css,
                            f"Found {len(css_files)} .css files")

    def test_package_installation(self):
        """Phase 3: Test codex-ml package installation and basic functionality"""
        print("\n" + "="*80)
        print("PHASE 3: TEST CODEX-ML PACKAGE INSTALLATION")
        print("="*80)
        
        # Test 1: Check PyPI package info
        try:
            url = "https://pypi.org/pypi/codex-ml/0.3.0/json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                version = data['info']['version']
                self.log_test("Phase 3", "Package available on PyPI", version == "0.3.0",
                            f"Version: {version}")
        except Exception as e:
            self.log_test("Phase 3", "Package available on PyPI", False, str(e)[:50])

        # Test 2: Import package (editable install)
        try:
            import codex_ml
            version = codex_ml.__version__
            self.log_test("Phase 3", "Package imports successfully", True,
                        f"Version: {version}")
            self.log_test("Phase 3", "Correct version installed", version == "0.3.0",
                        f"Version: {version}")
        except Exception as e:
            self.log_test("Phase 3", "Package imports successfully", False, str(e)[:50])

        # Test 3: Test CLI entry point
        try:
            result = subprocess.run(["codex", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            self.log_test("Phase 3", "CLI entry point works", result.returncode == 0,
                        result.stdout.strip() if result.stdout else result.stderr[:50])
        except FileNotFoundError:
            self.log_test("Phase 3", "CLI entry point works", False, "Command not found")
        except Exception as e:
            self.log_test("Phase 3", "CLI entry point works", False, str(e)[:50])

    def test_module_imports(self):
        """Phase 4: Test module imports"""
        print("\n" + "="*80)
        print("PHASE 4: TEST MODULE IMPORTS")
        print("="*80)
        
        modules_to_test = [
            ("codex_ml", "Main package"),
            ("codex_ml.api", "API module"),
            ("codex_ml.cognitive_brain", "Cognitive Brain module"),
            ("codex_ml.memory", "Memory module"),
            ("codex_ml.config", "Config module"),
            ("codex_ml.cli", "CLI module"),
        ]
        
        for module_name, description in modules_to_test:
            try:
                __import__(module_name)
                self.log_test("Phase 4", f"Import {description}", True, f"Module: {module_name}")
            except ImportError as e:
                self.log_test("Phase 4", f"Import {description}", False,
                            f"Module: {module_name}, Error: {str(e)[:40]}")
            except Exception as e:
                self.log_test("Phase 4", f"Import {description}", False,
                            f"Module: {module_name}, Error: {str(e)[:40]}")

    def test_workflow_configuration(self):
        """Phase 5: Test workflow configuration"""
        print("\n" + "="*80)
        print("PHASE 5: TEST WORKFLOW CONFIGURATION")
        print("="*80)
        
        workflow_files = [
            ("pages-mkdocs.yml", "MkDocs deployment"),
            ("pages-scheduled-validation.yml", "Pages validation"),
            ("pages-health-guard.yml", "Pages health check"),
        ]
        
        workflows_path = self.repo_root / ".github" / "workflows"
        
        for filename, description in workflow_files:
            path = workflows_path / filename
            self.log_test("Phase 5", f"{description} workflow exists", path.exists(),
                        f"Path: {path}")
            
            if path.exists():
                content = path.read_text(encoding='utf-8')
                
                # Check for cognitive_app build
                if "cognitive_app" in filename or filename == "pages-mkdocs.yml":
                    has_app_build = "npm run build" in content and "cognitive_app" in content
                    self.log_test("Phase 5", f"{description}: cognitive_app build configured",
                                has_app_build, "")
                    
                    if has_app_build:
                        has_deploy = "site/cognitive_app" in content
                        self.log_test("Phase 5", f"{description}: app deployment configured",
                                    has_deploy, "")

    def run_all_validations(self):
        """Run all validation phases"""
        self.test_pages_deployment()
        self.test_local_deployment()
        self.test_package_installation()
        self.test_module_imports()
        self.test_workflow_configuration()
        
        return self.print_summary()

if __name__ == "__main__":
    validator = DeploymentValidator()
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)
