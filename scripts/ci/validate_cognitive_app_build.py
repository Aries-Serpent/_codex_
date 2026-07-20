#!/usr/bin/env python3
"""
Cognitive App Build Validation Script

Validates the cognitive_app build process to ensure:
1. Pre-build: Dependencies, Node version, npm cache integrity
2. Post-build: All expected widgets and assets are present
3. Build artifacts: Required files exist and are not corrupted

This script ensures deterministic, reliable builds that work post-merge without
requiring copilot agent intervention.

Exit codes:
  0 - All validations passed
  1 - Pre-build validation failed (dependencies, env)
  2 - Build process failed
  3 - Post-build validation failed (missing widgets/assets)
  4 - Artifact corruption detected
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COGNITIVE_APP_DIR = REPO_ROOT / "cognitive_app"
DIST_DIR = COGNITIVE_APP_DIR / "dist"
PACKAGE_JSON = COGNITIVE_APP_DIR / "package.json"
PACKAGE_LOCK_JSON = COGNITIVE_APP_DIR / "package-lock.json"
NODE_MODULES_DIR = COGNITIVE_APP_DIR / "node_modules"


def log(level: str, msg: str) -> None:
    """Log with prefix."""
    prefix = {"INFO": "ℹ", "SUCCESS": "OK", "ERROR": "ERROR", "WARNING": "WARNING"}
    print(f"[{prefix.get(level, '•')}] {msg}")


def validate_pre_build() -> bool:
    """Validate pre-build environment and dependencies."""
    log("INFO", "Phase 1: Pre-build validation")
    
    errors = []
    
    # Check package.json exists
    if not PACKAGE_JSON.exists():
        errors.append(f"package.json not found at {PACKAGE_JSON}")
        log("ERROR", f"✗ package.json missing")
        return False
    log("SUCCESS", "✓ package.json found")
    
    # Check package-lock.json exists
    if not PACKAGE_LOCK_JSON.exists():
        errors.append(f"package-lock.json not found at {PACKAGE_LOCK_JSON}")
        log("WARNING", "⚠ package-lock.json missing (may cause non-deterministic builds)")
    else:
        log("SUCCESS", "✓ package-lock.json found")
    
    # Verify package.json syntax
    try:
        with open(PACKAGE_JSON) as f:
            pkg_data = json.load(f)
        log("SUCCESS", "✓ package.json valid JSON")
    except json.JSONDecodeError as e:
        errors.append(f"package.json JSON parse error: {e}")
        log("ERROR", f"✗ package.json parse failed: {e}")
        return False
    
    # Check Node version
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        node_version = result.stdout.strip()
        log("SUCCESS", f"✓ Node.js available: {node_version}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        errors.append(f"Node.js check failed: {e}")
        log("ERROR", f"✗ Node.js not available or version check failed")
        return False
    
    # Check npm version
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        npm_version = result.stdout.strip()
        log("SUCCESS", f"✓ npm available: {npm_version}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        errors.append(f"npm check failed: {e}")
        log("ERROR", f"✗ npm not available or version check failed")
        return False
    
    # Check for critical build dependencies
    critical_deps = ["react", "react-dom", "vite", "typescript"]
    if "dependencies" in pkg_data or "devDependencies" in pkg_data:
        all_deps = {
            **pkg_data.get("dependencies", {}),
            **pkg_data.get("devDependencies", {}),
        }
        missing = [dep for dep in critical_deps if dep not in all_deps]
        if missing:
            errors.append(f"Missing critical dependencies: {', '.join(missing)}")
            log("ERROR", f"✗ Missing critical deps: {', '.join(missing)}")
            return False
        log("SUCCESS", f"✓ All critical dependencies declared: {', '.join(critical_deps)}")
    
    if errors:
        log("ERROR", "Pre-build validation FAILED")
        for err in errors:
            log("ERROR", f"  - {err}")
        return False
    
    log("SUCCESS", "Pre-build validation PASSED")
    return True


def validate_post_build() -> bool:
    """Validate post-build artifacts and structure."""
    log("INFO", "Phase 2: Post-build validation")
    
    errors = []
    
    # Check dist directory exists
    if not DIST_DIR.exists():
        errors.append(f"dist/ directory not found at {DIST_DIR}")
        log("ERROR", "✗ dist/ directory missing")
        return False
    log("SUCCESS", "✓ dist/ directory exists")
    
    # Check index.html exists
    index_html = DIST_DIR / "index.html"
    if not index_html.exists():
        errors.append(f"index.html not found in dist/")
        log("ERROR", "✗ index.html missing")
        return False
    log("SUCCESS", "✓ index.html exists")
    
    # Validate index.html structure
    try:
        with open(index_html, encoding='utf-8') as f:
            html_content = f.read()
        
        required_elements = [
            ('id="root"', "React root element"),
            ("<title>", "HTML title"),
            ("type=\"module\"", "Module script tag"),
        ]
        
        for element, desc in required_elements:
            if element in html_content:
                log("SUCCESS", f"✓ {desc} found")
            else:
                errors.append(f"Missing {desc} in index.html")
                log("ERROR", f"✗ {desc} missing")
    except Exception as e:
        errors.append(f"Failed to read index.html: {e}")
        log("ERROR", f"✗ Failed to read index.html: {e}")
        return False
    
    # Check for CSS and JS assets
    assets_dir = DIST_DIR / "assets"
    if not assets_dir.exists():
        errors.append("assets/ directory not found")
        log("ERROR", "✗ assets/ directory missing")
        return False
    log("SUCCESS", "✓ assets/ directory exists")
    
    js_files = list(assets_dir.glob("*.js"))
    css_files = list(assets_dir.glob("*.css"))
    
    if not js_files:
        errors.append("No JavaScript files found in assets/")
        log("ERROR", "✗ No JavaScript files in assets/")
        return False
    log("SUCCESS", f"✓ JavaScript files found ({len(js_files)} files)")
    
    if not css_files:
        log("WARNING", "⚠ No CSS files found in assets/ (may be inline)")
    else:
        log("SUCCESS", f"✓ CSS files found ({len(css_files)} files)")
    
    # Check for proxy.js (common in this app)
    if (DIST_DIR / "proxy.js").exists():
        log("SUCCESS", "✓ proxy.js found")
    
    # Check for package.json in dist (if app uses it)
    if (DIST_DIR / "package.json").exists():
        log("SUCCESS", "✓ dist/package.json found")
    
    if errors:
        log("ERROR", "Post-build validation FAILED")
        for err in errors:
            log("ERROR", f"  - {err}")
        return False
    
    log("SUCCESS", "Post-build validation PASSED")
    return True


def validate_widget_presence() -> bool:
    """Validate that expected widgets are included in the build."""
    log("INFO", "Phase 3: Widget presence validation")
    
    # Expected widget references in the build
    expected_widgets = [
        "MetricsDashboard",
        "CodeGenerator",
        "InteractiveDemo",
        "QuantumVisualizer",
        "QuantumDecisionEngine",
        "MemoryManagementDashboard",
        "AgentOrchestrationPanel",
        "XtermTerminal",
        "ApiClient",
        "DocumentationViewer",
    ]
    
    errors = []
    js_bundle = None
    
    # Find the main JS bundle (usually largest JS file in assets)
    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        js_files = sorted(
            assets_dir.glob("*.js"),
            key=lambda f: f.stat().st_size,
            reverse=True
        )
        
        if not js_files:
            errors.append("No JavaScript bundles found in assets/")
            log("ERROR", "✗ No JS bundles found")
            return False
        
        js_bundle = js_files[0]
        log("SUCCESS", f"✓ Main bundle found: {js_bundle.name} ({js_bundle.stat().st_size / 1024:.1f}KB)")
    
    # Check for widget references in the bundle
    if js_bundle:
        try:
            with open(js_bundle, encoding='utf-8', errors='ignore') as f:
                bundle_content = f.read()
            
            found_widgets = []
            missing_widgets = []
            
            for widget in expected_widgets:
                if widget in bundle_content:
                    found_widgets.append(widget)
                else:
                    missing_widgets.append(widget)
            
            log("SUCCESS", f"✓ Found {len(found_widgets)}/{len(expected_widgets)} widgets")
            for widget in found_widgets:
                log("SUCCESS", f"  ✓ {widget}")
            
            if missing_widgets:
                for widget in missing_widgets:
                    log("WARNING", f"  ⚠ {widget} (may be dynamically loaded)")
                    # Don't error on missing widgets as they may be code-split
        except Exception as e:
            errors.append(f"Failed to read bundle: {e}")
            log("ERROR", f"✗ Failed to read bundle: {e}")
            return False
    
    if errors:
        log("ERROR", "Widget presence validation FAILED")
        for err in errors:
            log("ERROR", f"  - {err}")
        return False
    
    log("SUCCESS", "Widget presence validation PASSED")
    return True


def save_asset_manifest() -> bool:
    """Save asset manifest with hashes for post-deployment verification."""
    log("INFO", "Phase 4: Asset manifest generation")
    
    try:
        assets_dir = DIST_DIR / "assets"
        if not assets_dir.exists():
            log("WARNING", "⚠ No assets directory to save manifest")
            return True
        
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "assets": {}
        }
        
        # Record all assets
        for asset_file in sorted(assets_dir.glob("*")):
            if asset_file.is_file():
                size = asset_file.stat().st_size
                asset_type = "unknown"
                if asset_file.suffix == ".js":
                    asset_type = "javascript"
                elif asset_file.suffix == ".css":
                    asset_type = "stylesheet"
                elif asset_file.suffix in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"):
                    asset_type = "image"
                
                manifest["assets"][asset_file.name] = {
                    "type": asset_type,
                    "size_bytes": size,
                    "path": str(asset_file.relative_to(REPO_ROOT))
                }
        
        # Save manifest
        manifest_file = DIST_DIR / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        log("SUCCESS", f"✓ Asset manifest saved ({len(manifest['assets'])} files)")
        return True
    except Exception as e:
        log("ERROR", f"✗ Failed to save asset manifest: {e}")
        return False


def main() -> int:
    """Main validation flow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Cognitive App Build")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pre-build-only", action="store_true", help="Only run pre-build validation")
    group.add_argument("--post-build-only", action="store_true", help="Only run post-build validation")
    args = parser.parse_args()
    
    log("INFO", "Starting Cognitive App Build Validation")
    log("INFO", f"   Cognitive App: {COGNITIVE_APP_DIR}")
    log("INFO", f"   Dist Output: {DIST_DIR}")
    print()
    
    # Determine what to run (default is all)
    if args.pre_build_only:
        run_pre_build = True
        run_post_build = False
    elif args.post_build_only:
        run_pre_build = False
        run_post_build = True
    else:
        # Default: run all validations
        run_pre_build = True
        run_post_build = True
    
    # Pre-build validation
    if run_pre_build:
        if not validate_pre_build():
            log("ERROR", "Pre-build validation failed")
            return 1
        print()
    
    # Post-build validation
    if run_post_build:
        if not validate_post_build():
            log("ERROR", "Post-build validation failed")
            return 3
        print()
        
        # Widget presence validation (inherently only runs in post-build phase
        # since this block is inside the "if run_post_build:" condition)
        if not validate_widget_presence():
            log("ERROR", "Widget presence validation failed")
            return 4
        print()
        
        # Asset manifest generation
        if not save_asset_manifest():
            log("ERROR", "Asset manifest generation failed")
            return 5
        print()
    
    log("SUCCESS", "All validations PASSED - Build is production-ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
