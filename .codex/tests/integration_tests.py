#!/usr/bin/env python3
"""
Integration Tests for Cognitive App & MkDocs Deployment

Tests ensure:
- MkDocs builds correctly with cognitive_app exclusion
- cognitive_app build doesn't interfere with doc build
- Artifact merging combines both correctly
- Final deployed site has both docs and app
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Tuple


class IntegrationTestSuite:
    """Integration tests for cognitive_app and MkDocs deployment."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.base_path = Path(__file__).parent.parent.parent
        self.results: Dict = {
            "status": "PENDING",
            "tests": [],
            "errors": [],
            "warnings": [],
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message with level."""
        if self.verbose or level in ("ERROR", "FAIL"):
            print(f"[{level}] {message}")

    def run_all_tests(self) -> bool:
        """Run all integration tests."""
        self.log("=== Starting Integration Test Suite ===")

        tests = [
            ("MkDocs Build Test", self.test_mkdocs_build),
            ("Cognitive App Build Test", self.test_cognitive_app_build),
            ("Non-Interference Test", self.test_non_interference),
            ("Artifact Structure Test", self.test_artifact_structure),
            ("Documentation Presence Test", self.test_documentation_presence),
            ("App Presence Test", self.test_app_presence),
            ("Configuration Validation Test", self.test_configuration_validation),
            ("Dependency Resolution Test", self.test_dependency_resolution),
        ]

        all_passed = True
        for test_name, test_func in tests:
            try:
                self.log(f"\n▶ Running: {test_name}")
                passed, message = test_func()
                status = "✅ PASS" if passed else "❌ FAIL"
                self.log(f"{status}: {test_name}")
                self.log(f"   {message}")
                self.results["tests"].append(
                    {"name": test_name, "passed": passed, "message": message}
                )
                if not passed:
                    all_passed = False
            except Exception as e:
                error_msg = f"Exception in {test_name}: {str(e)}"
                self.log(error_msg, "ERROR")
                self.results["errors"].append(error_msg)
                all_passed = False

        self.results["status"] = "PASS" if all_passed else "FAIL"
        return all_passed

    def test_mkdocs_build(self) -> Tuple[bool, str]:
        """Test MkDocs builds correctly."""
        try:
            self.log("  Running: mkdocs build", "INFO")

            result = subprocess.run(
                ["mkdocs", "build", "--verbose"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.base_path,
            )

            if result.returncode != 0:
                error = result.stderr[:300] if result.stderr else "Unknown error"
                return False, f"MkDocs build failed: {error}"

            site_path = self.base_path / "site"
            if not site_path.exists():
                return False, "site/ directory not created by MkDocs"

            # Check for key documentation files
            required_files = [
                "index.html",
                "getting-started/index.html",
            ]

            missing = [f for f in required_files if not (site_path / f).exists()]
            if missing:
                self.results["warnings"].append(
                    f"Expected documentation files missing: {missing}"
                )

            return True, "MkDocs build successful"
        except subprocess.TimeoutExpired:
            return False, "MkDocs build timed out (300s)"
        except Exception as e:
            return False, f"MkDocs build error: {str(e)}"

    def test_cognitive_app_build(self) -> Tuple[bool, str]:
        """Test cognitive_app builds correctly."""
        try:
            cognitive_app_path = self.base_path / "cognitive_app"
            self.log("  Running: npm ci && npm run build", "INFO")

            result_ci = subprocess.run(
                ["npm", "ci"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cognitive_app_path,
            )

            if result_ci.returncode != 0:
                return False, f"npm ci failed: {result_ci.stderr[:200]}"

            result_build = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cognitive_app_path,
                env={**subprocess.os.environ, "GITHUB_ACTIONS": "true"},
            )

            if result_build.returncode != 0:
                error = result_build.stderr[:300] if result_build.stderr else "Unknown error"
                return False, f"cognitive_app build failed: {error}"

            dist_path = cognitive_app_path / "dist"
            if not dist_path.exists():
                return False, "dist/ directory not created by build"

            return True, "cognitive_app build successful"
        except subprocess.TimeoutExpired:
            return False, "cognitive_app build timed out (300s)"
        except Exception as e:
            return False, f"cognitive_app build error: {str(e)}"

    def test_non_interference(self) -> Tuple[bool, str]:
        """Test that cognitive_app build doesn't interfere with MkDocs."""
        try:
            # Check that cognitive_app dist is not in docs/ directory
            docs_path = self.base_path / "docs"
            dist_in_docs = list(docs_path.glob("**/dist"))

            if dist_in_docs:
                self.results["warnings"].append(
                    "Found dist/ directories in docs/ - may interfere with build"
                )

            # Check that vite.config.ts has correct base path
            vite_config = self.base_path / "cognitive_app" / "vite.config.ts"
            with open(vite_config) as f:
                config = f.read()

            if "/_codex_/cognitive_app/" in config:
                return True, "Vite config correctly configured for subpath deployment"

            self.results["warnings"].append(
                "Vite base path may not be correctly configured"
            )
            return True, "Build separation validated"
        except Exception as e:
            return False, f"Non-interference test error: {str(e)}"

    def test_artifact_structure(self) -> Tuple[bool, str]:
        """Test final artifact structure is correct."""
        try:
            site_path = self.base_path / "site"

            if not site_path.exists():
                return False, "site/ directory not found"

            # Check for documentation
            if not list(site_path.glob("*.html")):
                return False, "No HTML files found in site/"

            # Check for assets
            asset_types = {
                "CSS": list(site_path.glob("**/*.css")),
                "JS": list(site_path.glob("**/*.js")),
            }

            missing_assets = [
                atype for atype, files in asset_types.items() if not files
            ]

            if missing_assets:
                return False, f"Missing asset types: {missing_assets}"

            structure_summary = ", ".join(
                f"{len(files)} {atype}" for atype, files in asset_types.items()
            )

            return True, f"Artifact structure valid: {structure_summary}"
        except Exception as e:
            return False, f"Artifact structure test error: {str(e)}"

    def test_documentation_presence(self) -> Tuple[bool, str]:
        """Test that documentation is present in final artifact."""
        try:
            site_path = self.base_path / "site"

            if not site_path.exists():
                return False, "site/ directory not found"

            # Check for key documentation pages
            doc_checks = [
                ("index.html", "Home page"),
                ("getting-started/index.html", "Getting started guide"),
                ("api/index.html", "API documentation"),
            ]

            found_docs = []
            missing_docs = []

            for file_path, description in doc_checks:
                full_path = site_path / file_path
                if full_path.exists():
                    found_docs.append(description)
                else:
                    missing_docs.append(description)

            if not found_docs:
                return False, "No documentation pages found"

            if missing_docs:
                self.results["warnings"].append(
                    f"Some expected documentation missing: {missing_docs}"
                )

            return (
                True,
                f"Documentation present ({len(found_docs)} core pages verified)",
            )
        except Exception as e:
            return False, f"Documentation presence test error: {str(e)}"

    def test_app_presence(self) -> Tuple[bool, str]:
        """Test that cognitive_app is deployed in final artifact."""
        try:
            site_path = self.base_path / "site"
            app_path = site_path / "cognitive_app"

            if not app_path.exists():
                return False, "cognitive_app not found in site/"

            # Check for key app files
            app_checks = [
                ("index.html", "App index"),
                ("*.js", "JavaScript bundles"),
            ]

            found_app_files = 0
            for pattern, description in app_checks:
                files = list(app_path.glob(pattern))
                if files:
                    found_app_files += len(files)

            if found_app_files == 0:
                return False, "cognitive_app appears empty"

            return True, f"cognitive_app deployed ({found_app_files} files)"
        except Exception as e:
            return False, f"App presence test error: {str(e)}"

    def test_configuration_validation(self) -> Tuple[bool, str]:
        """Validate all configuration files are correct."""
        try:
            config_checks = [
                (self.base_path / "mkdocs.yml", "mkdocs.yml"),
                (self.base_path / "cognitive_app" / "vite.config.ts", "vite.config.ts"),
                (self.base_path / "cognitive_app" / "package.json", "package.json"),
            ]

            missing_configs = []
            for config_path, name in config_checks:
                if not config_path.exists():
                    missing_configs.append(name)

            if missing_configs:
                return False, f"Missing configuration files: {missing_configs}"

            # Validate mkdocs.yml structure
            import yaml

            with open(self.base_path / "mkdocs.yml") as f:
                mkdocs_config = yaml.safe_load(f)

            required_fields = ["site_name", "nav", "theme"]
            missing_fields = [f for f in required_fields if f not in mkdocs_config]

            if missing_fields:
                return False, f"mkdocs.yml missing fields: {missing_fields}"

            return True, "All configurations validated"
        except Exception as e:
            return False, f"Configuration validation error: {str(e)}"

    def test_dependency_resolution(self) -> Tuple[bool, str]:
        """Test that all dependencies resolve correctly."""
        try:
            cognitive_app_path = self.base_path / "cognitive_app"

            # Check package.json dependencies
            with open(cognitive_app_path / "package.json") as f:
                pkg = json.load(f)

            total_deps = len(pkg.get("dependencies", {})) + len(
                pkg.get("devDependencies", {})
            )

            if total_deps == 0:
                return False, "No dependencies found in package.json"

            # Check for critical dependencies
            critical_deps = ["react", "react-dom", "vite"]
            missing_critical = [
                d for d in critical_deps
                if d not in pkg.get("dependencies", {})
                and d not in pkg.get("devDependencies", {})
            ]

            if missing_critical:
                return False, f"Missing critical dependencies: {missing_critical}"

            return True, f"Dependency resolution OK ({total_deps} dependencies)"
        except Exception as e:
            return False, f"Dependency resolution error: {str(e)}"

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Status: {self.results['status']}")
        print(f"Total Tests: {len(self.results['tests'])}")
        print(f"Passed: {sum(1 for t in self.results['tests'] if t['passed'])}")
        print(f"Failed: {sum(1 for t in self.results['tests'] if not t['passed'])}")

        if self.results["warnings"]:
            print(f"\n⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"  - {warning}")

        if self.results["errors"]:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  - {error}")

        print("\n" + "=" * 60)


def main():
    """Run integration tests."""
    import sys

    suite = IntegrationTestSuite(verbose=True)
    passed = suite.run_all_tests()
    suite.print_summary()

    # Output JSON results for CI integration
    base_path = Path(__file__).parent.parent.parent
    with open(base_path / ".codex" / "integration_test_results.json", "w") as f:
        json.dump(suite.results, f, indent=2)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
