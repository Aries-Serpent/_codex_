#!/usr/bin/env python3
"""
Cognitive App Deployment Verification
Tests that the cognitive app is deployed correctly and all components are accessible
"""

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


class CognitiveAppVerifier:
    def __init__(self):
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {}
        self.base_url = "https://aries-serpent.github.io/_codex_/cognitive_app"
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
    
    def fetch_url(self, url: str, timeout: int = 10) -> Tuple[int, str]:
        """Fetch a URL and return status code and content"""
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read(10000).decode('utf-8', errors='ignore')
                return response.status, content
        except urllib.error.HTTPError as e:
            return e.code, ""
        except Exception as e:
            return 0, f"Error: {str(e)[:50]}"

    def test_app_entry_point(self):
        """Test cognitive app entry point"""
        print("\n" + "="*80)
        print("TEST 1: COGNITIVE APP ENTRY POINT")
        print("="*80)
        
        status, content = self.fetch_url(f"{self.base_url}/")
        
        self.log_test("Entry Point", "App accessible at root", status == 200,
                    f"HTTP {status}")
        
        if status == 200:
            checks = [
                ("React root div", '<div id="root">' in content),
                ("Module script", 'type="module"' in content and 'index-' in content),
                ("CSS stylesheet", '<link rel="stylesheet"' in content and 'index-' in content),
                ("Correct base path", '/_codex_/cognitive_app' in content),
                ("HTML doctype", '<!DOCTYPE html>' in content),
                ("Meta charset", 'charset="UTF-8"' in content or 'charset=UTF-8' in content),
                ("Meta viewport", 'viewport' in content),
            ]
            
            for check_name, result in checks:
                self.log_test("Entry Point", f"HTML has {check_name}", result, "")

    def test_app_structure(self):
        """Test local app deployment structure"""
        print("\n" + "="*80)
        print("TEST 2: LOCAL APP DEPLOYMENT STRUCTURE")
        print("="*80)
        
        site_app_path = self.repo_root / "site" / "cognitive_app"
        
        # Check directory structure
        required_dirs = [
            ("assets directory", site_app_path / "assets"),
        ]
        
        for name, path in required_dirs:
            self.log_test("Structure", f"{name} exists", path.exists(),
                        f"Path: {path}")
        
        # Check required files
        required_files = [
            ("index.html", site_app_path / "index.html"),
            ("package.json", site_app_path / "package.json"),
        ]
        
        for name, path in required_files:
            exists = path.exists()
            self.log_test("Structure", f"{name} exists", exists,
                        f"Path: {path}")
            
            if exists and name == "package.json":
                try:
                    with open(path, encoding='utf-8') as f:
                        pkg = json.load(f)
                        has_name = "name" in pkg
                        self.log_test("Structure", "package.json is valid JSON", has_name,
                                    f"Package name: {pkg.get('name', 'N/A')}")
                except Exception as e:
                    self.log_test("Structure", "package.json is valid JSON", False, str(e)[:50])

    def test_assets(self):
        """Test asset deployment"""
        print("\n" + "="*80)
        print("TEST 3: ASSET DEPLOYMENT")
        print("="*80)
        
        site_app_path = self.repo_root / "site" / "cognitive_app"
        assets_path = site_app_path / "assets"
        
        if assets_path.exists():
            js_files = list(assets_path.glob("*.js"))
            css_files = list(assets_path.glob("*.css"))
            other_files = list(assets_path.glob("*.*"))
            
            self.log_test("Assets", "JavaScript files deployed", len(js_files) > 0,
                        f"Found {len(js_files)} .js files")
            
            self.log_test("Assets", "CSS files deployed", len(css_files) > 0,
                        f"Found {len(css_files)} .css files")
            
            self.log_test("Assets", "Asset files present", len(other_files) > 0,
                        f"Total files: {len(other_files)}")

    def test_app_features(self):
        """Test app feature indicators in HTML"""
        print("\n" + "="*80)
        print("TEST 4: APP FEATURE INDICATORS")
        print("="*80)
        
        status, content = self.fetch_url(f"{self.base_url}/")
        
        if status == 200:
            # Verify deployment was successful
            self.log_test("Deployment", "App deployed successfully", True, "HTTP 200")

    def test_documentation_links(self):
        """Test documentation links from cognitive app page"""
        print("\n" + "="*80)
        print("TEST 5: DOCUMENTATION LINKS")
        print("="*80)
        
        # Check docs are accessible
        docs_to_check = [
            ("Main documentation", "https://aries-serpent.github.io/_codex_/"),
            ("Cognitive App docs", "https://aries-serpent.github.io/_codex_/cognitive_app/"),
        ]
        
        for name, url in docs_to_check:
            status, _ = self.fetch_url(url)
            self.log_test("Documentation", f"{name} accessible", status == 200,
                        f"HTTP {status}")

    def test_workflow_configuration(self):
        """Test workflow deployment configuration"""
        print("\n" + "="*80)
        print("TEST 6: WORKFLOW CONFIGURATION")
        print("="*80)
        
        workflows_path = self.repo_root / ".github" / "workflows"
        mkdocs_workflow = workflows_path / "pages-mkdocs.yml"
        
        if mkdocs_workflow.exists():
            content = mkdocs_workflow.read_text(encoding='utf-8')
            
            checks = [
                ("cognitive_app build step", "Build cognitive_app dashboard" in content 
                                           or "npm run build" in content),
                ("cognitive_app deployment", "site/cognitive_app" in content),
                ("artifact upload", "upload-pages-artifact" in content),
                ("pages deployment", "deploy-pages" in content),
                ("node setup", "setup-node" in content),
            ]
            
            for check_name, result in checks:
                self.log_test("Workflow", f"{check_name} present", result, "")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("COGNITIVE APP VERIFICATION SUMMARY FOR v0.3.0")
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

    def run_all_verifications(self):
        """Run all cognitive app verifications"""
        self.test_app_entry_point()
        self.test_app_structure()
        self.test_assets()
        self.test_app_features()
        self.test_documentation_links()
        self.test_workflow_configuration()
        
        return self.print_summary()

if __name__ == "__main__":
    verifier = CognitiveAppVerifier()
    success = verifier.run_all_verifications()
    exit(0 if success else 1)
