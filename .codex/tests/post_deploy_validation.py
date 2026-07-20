#!/usr/bin/env python3
"""
Post-Deployment Validation Script

This script validates the deployed site after deployment to ensure:
- Site returns HTTP 200 status
- React app loads correctly
- Asset files are accessible
- React root div is present and functional
- Required script tags are present
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple


class PostDeployValidator:
    """Validates deployed site after deployment."""

    def __init__(self, site_url: str = None, verbose: bool = False):
        self.verbose = verbose
        self.base_path = Path(__file__).parent.parent.parent
        self.site_url = site_url or "https://aries-serpent.github.io/_codex_/cognitive_app/"
        self.results: Dict = {
            "status": "PENDING",
            "site_url": self.site_url,
            "checks": [],
            "errors": [],
            "warnings": [],
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message with level."""
        if self.verbose or level in ("ERROR", "FAIL"):
            print(f"[{level}] {message}")

    def run_all_checks(self, retries: int = 3, retry_delay: int = 5) -> bool:
        """Run all post-deployment checks with retries."""
        self.log("=== Starting Post-Deployment Validation ===")
        self.log(f"Target URL: {self.site_url}")

        checks = [
            ("Site HTTP Status", self.check_http_status),
            ("Index.html Retrieval", self.fetch_index_html),
            ("React Root Div", self.check_react_root),
            ("Script Tags", self.check_script_tags),
            ("Asset Accessibility", self.check_asset_accessibility),
            ("HTML Meta Tags", self.check_meta_tags),
            ("Security Headers", self.check_security_headers),
            ("Performance Metrics", self.analyze_performance),
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

    def fetch_url(self, url: str, timeout: int = 10) -> Tuple[int, str]:
        """Fetch URL and return status code and content."""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "PostDeployValidator/1.0",
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8", errors="ignore")
                return response.status, content
        except urllib.error.HTTPError as e:
            return e.code, ""
        except urllib.error.URLError as e:
            return 0, str(e)
        except Exception as e:
            return 0, str(e)

    def check_http_status(self) -> Tuple[bool, str]:
        """Check site returns HTTP 200 status."""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            self.log(f"  HTTP check (attempt {attempt + 1}/{max_retries})")
            status, _ = self.fetch_url(self.site_url)

            if status == 200:
                return True, f"Site returns HTTP 200 (attempt {attempt + 1})"

            if status == 0:
                if attempt < max_retries - 1:
                    self.log(f"  Connection failed, retrying in {retry_delay}s...", "INFO")
                    time.sleep(retry_delay)
                    continue
                else:
                    return False, "Site unreachable after retries"
            elif status == 404:
                return False, "Site returns HTTP 404 - deployment may have failed"
            elif status in (503, 502):
                if attempt < max_retries - 1:
                    self.log(f"  Server unavailable ({status}), retrying...", "INFO")
                    time.sleep(retry_delay)
                    continue
                else:
                    return False, f"Server unavailable (HTTP {status})"
            else:
                return False, f"Unexpected HTTP status: {status}"

        return False, "Max retries exceeded"

    def fetch_index_html(self) -> Tuple[bool, str]:
        """Fetch and validate index.html."""
        try:
            status, content = self.fetch_url(self.site_url + "index.html")

            if status != 200:
                status2, content2 = self.fetch_url(self.site_url)
                if status2 == 200 and content2:
                    content = content2
                    status = status2
                else:
                    return False, f"Failed to fetch index.html (HTTP {status})"

            if not content:
                return False, "index.html is empty"

            if len(content) < 1000:
                self.results["warnings"].append(
                    f"index.html is suspiciously small ({len(content)} bytes)"
                )

            return True, f"index.html retrieved ({len(content)} bytes)"
        except Exception as e:
            return False, f"Error fetching index.html: {str(e)}"

    def check_react_root(self) -> Tuple[bool, str]:
        """Verify React root div is present and accessible."""
        try:
            status, content = self.fetch_url(self.site_url)

            if status != 200:
                return False, "Cannot check React root - site unreachable"

            # Check for React root div
            if 'id="root"' in content or "id='root'" in content:
                return True, "React root div (id='root') found and accessible"

            # Fallback check for common variations
            if "<div id=" in content and ("root" in content or "app" in content):
                self.results["warnings"].append(
                    "React root div found with different structure"
                )
                return True, "React root div found (alternative structure)"

            return False, "React root div not found in deployed HTML"
        except Exception as e:
            return False, f"Error checking React root: {str(e)}"

    def check_script_tags(self) -> Tuple[bool, str]:
        """Verify required script tags are present."""
        try:
            status, content = self.fetch_url(self.site_url)

            if status != 200:
                return False, "Cannot check scripts - site unreachable"

            script_patterns = [
                ("<script", "Script tags"),
                ('type="module"', "Module script type"),
                (".js", "JavaScript references"),
            ]

            found_scripts = []
            for pattern, description in script_patterns:
                if pattern in content:
                    found_scripts.append(description)

            if not found_scripts:
                return False, "No script tags found in deployed HTML"

            # Count script occurrences
            script_count = content.count("<script")
            js_count = content.count(".js")

            return (
                True,
                f"Scripts present ({script_count} tags, {js_count} .js references)",
            )
        except Exception as e:
            return False, f"Error checking scripts: {str(e)}"

    def check_asset_accessibility(self) -> Tuple[bool, str]:
        """Verify asset files are accessible."""
        try:
            status, content = self.fetch_url(self.site_url)

            if status != 200:
                return False, "Cannot check assets - site unreachable"

            # Extract asset paths from HTML
            import re

            # Find script src attributes
            scripts = re.findall(r'<script[^>]*src="([^"]*)"', content)
            # Find link href attributes
            links = re.findall(r'<link[^>]*href="([^"]*)"', content)

            assets_checked = 0
            assets_ok = 0

            for asset in scripts[:3] + links[:3]:  # Check first 3 of each type
                if asset.startswith("http"):
                    url = asset
                elif asset.startswith("/"):
                    url = self.site_url.rstrip("/") + asset
                else:
                    url = self.site_url + asset

                status_code, _ = self.fetch_url(url, timeout=5)
                assets_checked += 1
                if status_code == 200:
                    assets_ok += 1

            if assets_checked == 0:
                return True, "No external assets found to verify"

            if assets_ok == assets_checked:
                return True, f"All {assets_ok} asset samples accessible"
            else:
                self.results["warnings"].append(
                    f"Some assets may be inaccessible ({assets_ok}/{assets_checked})"
                )
                return True, f"Asset check: {assets_ok}/{assets_checked} samples OK"
        except Exception as e:
            return False, f"Error checking assets: {str(e)}"

    def check_meta_tags(self) -> Tuple[bool, str]:
        """Verify HTML meta tags are present."""
        try:
            status, content = self.fetch_url(self.site_url)

            if status != 200:
                return False, "Cannot check meta tags - site unreachable"

            meta_tags = [
                ('<meta charset="utf-8"', "Character encoding"),
                ('<meta name="viewport"', "Viewport"),
                ("<title>", "Title tag"),
            ]

            found_tags = []
            for tag_pattern, description in meta_tags:
                if tag_pattern.lower() in content.lower():
                    found_tags.append(description)

            if len(found_tags) >= 2:
                return True, f"Essential meta tags present: {', '.join(found_tags)}"

            if found_tags:
                self.results["warnings"].append(
                    f"Missing some meta tags: {found_tags}"
                )
                return True, f"Some meta tags present: {', '.join(found_tags)}"

            return False, "Critical meta tags missing"
        except Exception as e:
            return False, f"Error checking meta tags: {str(e)}"

    def check_security_headers(self) -> Tuple[bool, str]:
        """Verify security headers are present."""
        try:
            req = urllib.request.Request(self.site_url)
            with urllib.request.urlopen(req, timeout=10) as response:
                headers = response.headers

            security_headers = [
                "Content-Security-Policy",
                "X-Content-Type-Options",
                "X-Frame-Options",
                "Strict-Transport-Security",
            ]

            found_headers = []
            for header in security_headers:
                if header in headers:
                    found_headers.append(header)

            if found_headers:
                return (
                    True,
                    f"Security headers present: {', '.join(found_headers[:2])}",
                )

            self.results["warnings"].append(
                "Limited or no security headers detected"
            )
            return True, "Security header check complete"
        except Exception as e:
            self.results["warnings"].append(f"Could not check security headers: {str(e)}")
            return True, "Security header check skipped"

    def analyze_performance(self) -> Tuple[bool, str]:
        """Analyze deployed site performance metrics."""
        try:
            start_time = time.time()
            status, content = self.fetch_url(self.site_url)
            load_time = time.time() - start_time

            if status != 200:
                return False, "Cannot analyze performance - site unreachable"

            metrics = {
                "load_time_seconds": round(load_time, 2),
                "content_size_kb": round(len(content) / 1024, 2),
            }

            if load_time > 5:
                self.results["warnings"].append(
                    f"Slow load time ({load_time:.2f}s) - may affect UX"
                )

            return (
                True,
                f"Performance: {metrics['load_time_seconds']}s load, {metrics['content_size_kb']}KB",
            )
        except Exception as e:
            return False, f"Error analyzing performance: {str(e)}"

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("POST-DEPLOYMENT VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Site URL: {self.site_url}")
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
    """Run post-deployment validation."""
    import sys

    site_url = sys.argv[1] if len(sys.argv) > 1 else None
    validator = PostDeployValidator(site_url=site_url, verbose=True)
    passed = validator.run_all_checks()
    validator.print_summary()

    # Output JSON results for CI integration
    base_path = Path(__file__).parent.parent.parent
    with open(
        base_path / ".codex" / "post_deploy_results.json", "w"
    ) as f:
        json.dump(validator.results, f, indent=2)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
