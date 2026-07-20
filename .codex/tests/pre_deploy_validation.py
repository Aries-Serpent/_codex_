#!/usr/bin/env python3
"""
Pre-Deployment Validation Script

This script validates the cognitive_app build before deployment to ensure:
- Build completes successfully
- dist/ directory is created with required structure
- Asset files are present and valid
- HTML structure is correct
- Asset paths match vite.config.ts base path
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple


class PreDeployValidator:
    """Validates cognitive_app build before deployment."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.base_path = Path(__file__).parent.parent.parent
        self.cognitive_app_path = self.base_path / "cognitive_app"
        self.results: Dict = {
            "status": "PENDING",
            "timestamp": "",
            "checks": [],
            "errors": [],
            "warnings": [],
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message with level."""
        if self.verbose or level in ("ERROR", "FAIL"):
            print(f"[{level}] {message}")

    def run_all_checks(self) -> bool:
        """Run all pre-deployment checks."""
        self.log("=== Starting Pre-Deployment Validation ===")

        checks = [
            ("Node Version Check", self.check_node_version),
            ("Package.json Check", self.check_package_json),
            ("Package-lock.json Check", self.check_package_lock),
            ("Build Execution", self.build_cognitive_app),
            ("Dist Directory Structure", self.check_dist_structure),
            ("Required Asset Files", self.check_required_assets),
            ("HTML Structure Validation", self.check_html_structure),
            ("Vite Config Validation", self.validate_vite_config),
            ("Asset Path Validation", self.validate_asset_paths),
            ("Build Output Analysis", self.analyze_build_output),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                self.log(f"\n▶ Running: {check_name}")
                passed, message = check_func()
                status = "✅ PASS" if passed else "❌ FAIL"
                self.log(f"{status}: {check_name}")
                self.log(f"   {message}")
                self.results["checks"].append(
                    {"name": check_name, "passed": passed, "message": message}
                )
                if not passed:
                    all_passed = False
            except Exception as e:
                error_msg = f"Exception in {check_name}: {str(e)}"
                self.log(error_msg, "ERROR")
                self.results["errors"].append(error_msg)
                all_passed = False

        self.results["status"] = "PASS" if all_passed else "FAIL"
        return all_passed

    def check_node_version(self) -> Tuple[bool, str]:
        """Verify Node.js version is 22 or higher."""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=10
            )
            version_str = result.stdout.strip().lstrip("v")
            major_version = int(version_str.split(".")[0])

            if major_version >= 22:
                return True, f"Node {version_str} (required: >=22)"
            else:
                return False, f"Node {version_str} is below minimum requirement of 22"
        except Exception as e:
            return False, f"Failed to check Node version: {str(e)}"

    def check_package_json(self) -> Tuple[bool, str]:
        """Validate package.json exists and has required fields."""
        try:
            package_json = self.cognitive_app_path / "package.json"
            if not package_json.exists():
                return False, "package.json not found"

            with open(package_json) as f:
                data = json.load(f)

            required_fields = ["dependencies", "devDependencies", "scripts"]
            missing = [f for f in required_fields if f not in data]

            if missing:
                return False, f"Missing required fields: {', '.join(missing)}"

            if "build" not in data.get("scripts", {}):
                return False, "build script not defined in package.json"

            engines = data.get("engines", {})
            node_req = engines.get("node", "")
            if ">=22" not in node_req and "22" not in node_req:
                self.results["warnings"].append(
                    f"package.json engine requirement may be loose: {node_req}"
                )

            return True, f"package.json validated ({len(data.get('dependencies', {}))} dependencies)"
        except Exception as e:
            return False, f"Error parsing package.json: {str(e)}"

    def check_package_lock(self) -> Tuple[bool, str]:
        """Validate package-lock.json exists and is compatible."""
        try:
            package_lock = self.cognitive_app_path / "package-lock.json"
            if not package_lock.exists():
                return False, "package-lock.json not found"

            with open(package_lock) as f:
                data = json.load(f)

            lockfile_version = data.get("lockfileVersion")
            if lockfile_version not in (3, 4):
                self.results["warnings"].append(
                    f"Lockfile version {lockfile_version} may not be compatible with npm 11+"
                )

            return True, f"package-lock.json validated (version {lockfile_version})"
        except Exception as e:
            return False, f"Error parsing package-lock.json: {str(e)}"

    def build_cognitive_app(self) -> Tuple[bool, str]:
        """Execute npm build for cognitive_app."""
        try:
            self.log("  Running: npm ci && npm run build", "INFO")

            # Change to cognitive_app directory
            os.chdir(self.cognitive_app_path)

            # Run npm ci for clean install
            result_ci = subprocess.run(
                ["npm", "ci"],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "CI": "true"},
            )

            if result_ci.returncode != 0:
                return False, f"npm ci failed: {result_ci.stderr[:200]}"

            # Run build
            result_build = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "GITHUB_ACTIONS": "true"},
            )

            os.chdir(self.base_path)

            if result_build.returncode != 0:
                error_output = result_build.stderr[:300]
                return False, f"npm run build failed: {error_output}"

            return True, "Build completed successfully"
        except subprocess.TimeoutExpired:
            os.chdir(self.base_path)
            return False, "Build process timed out (300s)"
        except Exception as e:
            os.chdir(self.base_path)
            return False, f"Build execution error: {str(e)}"

    def check_dist_structure(self) -> Tuple[bool, str]:
        """Verify dist/ directory structure."""
        try:
            dist_path = self.cognitive_app_path / "dist"

            if not dist_path.exists():
                return False, "dist/ directory not created"

            required_files = ["index.html"]
            missing_files = [f for f in required_files if not (dist_path / f).exists()]

            if missing_files:
                return False, f"Missing required files: {', '.join(missing_files)}"

            # Check for CSS and JS bundles
            js_files = list(dist_path.glob("**/*.js"))
            css_files = list(dist_path.glob("**/*.css"))

            if not js_files:
                return False, "No JavaScript bundles found in dist/"

            return (
                True,
                f"✓ dist/ structure valid ({len(js_files)} JS, {len(css_files)} CSS bundles)",
            )
        except Exception as e:
            return False, f"Error checking dist structure: {str(e)}"

    def check_required_assets(self) -> Tuple[bool, str]:
        """Verify all required asset files exist."""
        try:
            dist_path = self.cognitive_app_path / "dist"

            required_patterns = [
                ("**/*.js", "JavaScript bundles"),
                ("**/*.css", "Stylesheet files"),
                ("**/*.woff2", "Font files (optional)"),
            ]

            assets = {}
            for pattern, description in required_patterns:
                files = list(dist_path.glob(pattern))
                assets[description] = len(files)

            if assets["JavaScript bundles"] == 0:
                return False, "No JavaScript bundles found"

            asset_summary = ", ".join(
                f"{count} {desc}" for desc, count in assets.items() if count > 0
            )
            return True, f"Asset files validated: {asset_summary}"
        except Exception as e:
            return False, f"Error checking assets: {str(e)}"

    def check_html_structure(self) -> Tuple[bool, str]:
        """Validate HTML structure and React root div."""
        try:
            index_html = self.cognitive_app_path / "dist" / "index.html"

            if not index_html.exists():
                return False, "index.html not found in dist/"

            with open(index_html) as f:
                html_content = f.read()

            # Check for React root div
            if 'id="root"' not in html_content:
                return False, "React root div (id='root') not found in index.html"

            # Check for module script
            if 'type="module"' not in html_content:
                self.results["warnings"].append(
                    "No module scripts found in index.html - app may not load"
                )

            # Basic structure checks
            checks = [
                ("<!DOCTYPE html>", "DOCTYPE declaration"),
                ("<html", "html tag"),
                ("<head>", "head tag"),
                ("<body>", "body tag"),
            ]

            missing = [desc for check, desc in checks if check.lower() not in html_content.lower()]
            if missing:
                return False, f"Missing HTML elements: {', '.join(missing)}"

            return True, "HTML structure validated with React root div present"
        except Exception as e:
            return False, f"Error validating HTML: {str(e)}"

    def validate_vite_config(self) -> Tuple[bool, str]:
        """Verify Vite configuration is correct."""
        try:
            vite_config = self.cognitive_app_path / "vite.config.ts"

            if not vite_config.exists():
                return False, "vite.config.ts not found"

            with open(vite_config) as f:
                config_content = f.read()

            # Check for base path configuration
            if "process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/'" not in config_content:
                self.results["warnings"].append(
                    "Vite base path configuration may not match deployment expectations"
                )

            required_configs = [
                ("react()", "React plugin"),
                ("tailwindcss()", "Tailwind plugin"),
                ("outDir: 'dist'", "Output directory"),
            ]

            missing = [desc for check, desc in required_configs if check not in config_content]
            if missing:
                return False, f"Missing Vite configurations: {', '.join(missing)}"

            return True, "Vite configuration validated"
        except Exception as e:
            return False, f"Error validating Vite config: {str(e)}"

    def validate_asset_paths(self) -> Tuple[bool, str]:
        """Verify asset paths match Vite base path configuration."""
        try:
            index_html = self.cognitive_app_path / "dist" / "index.html"

            if not index_html.exists():
                return False, "index.html not found - cannot validate asset paths"

            with open(index_html) as f:
                html_content = f.read()

            # Check for hardcoded root paths that should be relative
            problematic_patterns = ["/assets/", "/style/", "/js/"]
            problems = [
                p for p in problematic_patterns if p in html_content
            ]

            if problems:
                self.results["warnings"].append(
                    f"Found potentially hardcoded paths: {problems} - may break on subpath deployment"
                )

            # Vite should generate relative paths
            if 'href="/' in html_content or 'src="/' in html_content:
                self.results["warnings"].append(
                    "Detected absolute paths in HTML - relative paths are safer"
                )

            return True, "Asset path validation complete"
        except Exception as e:
            return False, f"Error validating asset paths: {str(e)}"

    def analyze_build_output(self) -> Tuple[bool, str]:
        """Analyze overall build output and generate summary."""
        try:
            dist_path = self.cognitive_app_path / "dist"

            if not dist_path.exists():
                return False, "dist/ not found"

            # Calculate total size
            total_size = sum(
                f.stat().st_size for f in dist_path.rglob("*") if f.is_file()
            )
            total_size_mb = total_size / (1024 * 1024)

            # Count files by type
            file_counts = {}
            for f in dist_path.rglob("*"):
                if f.is_file():
                    ext = f.suffix.lstrip(".") or "unknown"
                    file_counts[ext] = file_counts.get(ext, 0) + 1

            summary = f"Build output: {total_size_mb:.2f}MB, "
            summary += ", ".join(f"{count} .{ext}" for ext, count in sorted(file_counts.items()))

            if total_size_mb > 500:
                self.results["warnings"].append(
                    f"Build output size is large ({total_size_mb:.2f}MB) - may affect deployment"
                )

            return True, summary
        except Exception as e:
            return False, f"Error analyzing build output: {str(e)}"

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("PRE-DEPLOYMENT VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Status: {self.results['status']}")
        print(f"Total Checks: {len(self.results['checks'])}")
        print(f"Passed: {sum(1 for c in self.results['checks'] if c['passed'])}")
        print(f"Failed: {sum(1 for c in self.results['checks'] if not c['passed'])}")

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
    """Run pre-deployment validation."""
    validator = PreDeployValidator(verbose=True)
    passed = validator.run_all_checks()
    validator.print_summary()

    # Output JSON results for CI integration
    with open(
        validator.base_path / ".codex" / "pre_deploy_results.json", "w"
    ) as f:
        json.dump(validator.results, f, indent=2)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
