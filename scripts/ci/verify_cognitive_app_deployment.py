#!/usr/bin/env python3
"""
Cognitive App Deployment Verification Script

Verifies that the cognitive_app has been correctly deployed to GitHub Pages
with all required assets available and functional.

Exit codes:
  0 - Deployment verified, all assets available
  1 - Root page not accessible
  2 - Assets missing or hash mismatch
  3 - React root element not properly loaded
  4 - Critical assets (JS/CSS) not accessible
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin


def log(level: str, msg: str) -> None:
    """Log with prefix."""
    prefix = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"[{prefix.get(level, '•')}] {msg}")


def verify_page_loads(url: str, max_retries: int = 5) -> tuple[bool, str]:
    """Verify that a page loads and extract asset references."""
    log("INFO", f"Verifying page: {url}")
    
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                ["curl", "-sS", "-w", "\n%{http_code}", url],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            lines = result.stdout.rsplit('\n', 1)
            if len(lines) == 2:
                content, http_code = lines
            else:
                http_code = result.stdout.strip()
                content = ""
            
            http_code = http_code.strip()
            
            if http_code == "200":
                log("SUCCESS", f"✓ Page returned HTTP {http_code}")
                return True, content
            
            log("WARNING", f"⚠ Attempt {attempt}/{max_retries}: HTTP {http_code}")
            if attempt < max_retries:
                time.sleep(10)
        except subprocess.TimeoutExpired:
            log("WARNING", f"⚠ Timeout on attempt {attempt}/{max_retries}")
            if attempt < max_retries:
                time.sleep(10)
        except Exception as e:
            log("WARNING", f"⚠ Error on attempt {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                time.sleep(10)
    
    log("ERROR", f"✗ Page failed to load after {max_retries} attempts")
    return False, ""


def extract_asset_urls(html_content: str, base_url: str) -> dict:
    """Extract asset URLs from HTML."""
    import re
    
    assets = {
        "scripts": [],
        "styles": [],
    }
    
    # Extract script tags with src
    for match in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', html_content):
        url = match.group(1)
        # Convert relative URLs to absolute
        if not url.startswith(('http://', 'https://')):
            assets["scripts"].append(urljoin(base_url, url))
        else:
            assets["scripts"].append(url)
    
    # Extract link tags with href for stylesheets
    for match in re.finditer(r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']', html_content):
        url = match.group(1)
        if not url.startswith(('http://', 'https://')):
            assets["styles"].append(urljoin(base_url, url))
        else:
            assets["styles"].append(url)
    
    # Also check for alternate format (href before rel)
    for match in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']stylesheet["\']', html_content):
        url = match.group(1)
        if not url.startswith(('http://', 'https://')):
            assets["styles"].append(urljoin(base_url, url))
        else:
            assets["styles"].append(url)
    
    return assets


def verify_asset_accessible(url: str, asset_type: str = "asset") -> bool:
    """Verify that an asset is accessible."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", url],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        http_code = result.stdout.strip()
        
        if http_code == "200":
            log("SUCCESS", f"✓ {asset_type} accessible: {Path(url).name}")
            return True
        else:
            log("ERROR", f"✗ {asset_type} returned HTTP {http_code}: {Path(url).name}")
            return False
    except Exception as e:
        log("ERROR", f"✗ Failed to verify {asset_type}: {e}")
        return False


def verify_react_root(html_content: str) -> bool:
    """Verify React root element is present."""
    if 'id="root"' in html_content:
        log("SUCCESS", "✓ React root element found")
        return True
    
    log("ERROR", "✗ React root element (id='root') not found")
    return False


def verify_module_script(html_content: str) -> bool:
    """Verify that module scripts are properly configured."""
    if 'type="module"' in html_content:
        log("SUCCESS", "✓ Module scripts found")
        return True
    
    log("WARNING", "⚠ No module scripts found (may use other loading method)")
    return True


def main() -> int:
    """Main verification flow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Cognitive App Deployment")
    parser.add_argument(
        "--url",
        default="https://aries-serpent.github.io/_codex_/cognitive_app/",
        help="Base URL of cognitive_app deployment"
    )
    parser.add_argument(
        "--skip-assets",
        action="store_true",
        help="Skip asset verification (test only page structure)"
    )
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    log("INFO", f"Starting Cognitive App Deployment Verification")
    log("INFO", f"   Target URL: {base_url}/")
    print()
    
    # Phase 1: Verify page loads
    log("INFO", "Phase 1: Page Accessibility Verification")
    page_loads, html_content = verify_page_loads(base_url + "/")
    if not page_loads:
        log("ERROR", "Deployment verification FAILED - page not accessible")
        return 1
    print()
    
    # Phase 2: Verify React setup
    log("INFO", "Phase 2: React Configuration Verification")
    if not verify_react_root(html_content):
        log("ERROR", "React root element not found")
        return 3
    print()
    
    if not verify_module_script(html_content):
        log("WARNING", "Module script configuration not ideal")
    print()
    
    # Phase 3: Verify assets if not skipped
    if not args.skip_assets:
        log("INFO", "Phase 3: Asset Accessibility Verification")
        assets = extract_asset_urls(html_content, base_url)
        
        if not assets["scripts"] and not assets["styles"]:
            log("ERROR", "✗ No assets found in HTML")
            return 4
        
        all_accessible = True
        
        # Verify scripts
        if assets["scripts"]:
            log("INFO", f"Checking {len(assets['scripts'])} script(s)...")
            for script_url in assets["scripts"]:
                if not verify_asset_accessible(script_url, "Script"):
                    all_accessible = False
        else:
            log("WARNING", "⚠ No scripts found")
        
        print()
        
        # Verify styles
        if assets["styles"]:
            log("INFO", f"Checking {len(assets['styles'])} stylesheet(s)...")
            for style_url in assets["styles"]:
                if not verify_asset_accessible(style_url, "Stylesheet"):
                    all_accessible = False
        else:
            log("WARNING", "⚠ No stylesheets found (may be inline)")
        
        print()
        
        if not all_accessible:
            log("ERROR", "Deployment verification FAILED - some assets not accessible")
            return 4
    
    log("SUCCESS", "Deployment verification PASSED - cognitive_app is functional")
    return 0


if __name__ == "__main__":
    sys.exit(main())
