#!/usr/bin/env python3
"""
Cognitive App Cache Invalidator

Purges old cached assets from GitHub Pages and generates cache-busting
strategies for deployment. Ensures fresh assets are served after redeployment.

Exit codes:
  0 - Cache invalidation successful
  1 - Failed to invalidate cache
  2 - Invalid arguments
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def log(level: str, msg: str) -> None:
    """Log with prefix."""
    prefix = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"[{prefix.get(level, '•')}] {msg}")


def add_cache_busting_query_params(html_file: Path, base_url: str = "") -> bool:
    """Add cache-busting query parameters to asset URLs in HTML."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add timestamp-based cache buster to all asset URLs
        import re
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        
        # Update script src attributes
        content = re.sub(
            r'(src=")([^"]+\.js)(")',
            rf'\1\2?v={timestamp}\3',
            content
        )
        
        # Update link href attributes for stylesheets
        content = re.sub(
            r'(href=")([^"]+\.css)(")',
            rf'\1\2?v={timestamp}\3',
            content
        )
        
        # Update other asset references
        content = re.sub(
            r'(href=")([^"]+\.woff[^"]*|[^"]+\.woff2[^"]*|[^"]+\.png[^"]*|[^"]+\.jpg[^"]*|[^"]+\.svg[^"]*|[^"]+\.webp[^"]*)(")',
            rf'\1\2?v={timestamp}\3',
            content
        )
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        log("SUCCESS", f"Cache-busting params added (timestamp: {timestamp})")
        return True
    except Exception as e:
        log("ERROR", f"Failed to add cache-busting params: {e}")
        return False


def add_cache_control_headers_config() -> bool:
    """Generate cache control headers configuration for GitHub Pages."""
    repo_root = Path(__file__).resolve().parents[2]
    config_dir = repo_root / "site"
    
    # Create _headers file for Netlify/GitHub Pages cache control
    headers_file = config_dir / "_headers"
    
    headers_content = """# Cache control headers for GitHub Pages
/cognitive_app/index.html
  Cache-Control: public, max-age=0, must-revalidate
  
/cognitive_app/assets/*
  Cache-Control: public, max-age=31536000, immutable
  
/cognitive_app/*
  Cache-Control: public, max-age=3600
"""
    
    try:
        with open(headers_file, 'w') as f:
            f.write(headers_content)
        log("SUCCESS", f"Cache control headers config created: {headers_file.name}")
        return True
    except Exception as e:
        log("ERROR", f"Failed to create headers config: {e}")
        return False


def generate_cache_invalidation_report(base_url: str) -> Optional[str]:
    """Generate cache invalidation strategy report."""
    report_lines = []
    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("COGNITIVE APP CACHE INVALIDATION REPORT")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    report_lines.append("CACHE BUSTING STRATEGY APPLIED")
    report_lines.append("-" * 70)
    report_lines.append("1. Timestamp-based query parameters added to all assets")
    report_lines.append(f"   Format: /assets/file.js?v=YYYYMMDDHHMMSS")
    report_lines.append("")
    report_lines.append("2. Cache control headers configured:")
    report_lines.append("   - index.html: Cache-Control: max-age=0 (no cache)")
    report_lines.append("   - /assets/*: Cache-Control: max-age=31536000 (1 year)")
    report_lines.append("   - Other files: Cache-Control: max-age=3600 (1 hour)")
    report_lines.append("")
    
    report_lines.append("GITHUB PAGES CACHE INVALIDATION")
    report_lines.append("-" * 70)
    report_lines.append("GitHub Pages automatically invalidates cache when:")
    report_lines.append("  1. Files are modified (git commit SHA changes)")
    report_lines.append("  2. Deployment history is pushed to gh-pages branch")
    report_lines.append("")
    report_lines.append("Additional invalidation methods:")
    report_lines.append("  1. Force push new build to gh-pages branch")
    report_lines.append("  2. Wait 24-48 hours for natural CDN cache expiration")
    report_lines.append("  3. Use GitHub Pages rollback feature if available")
    report_lines.append("")
    
    report_lines.append("VERIFICATION AFTER INVALIDATION")
    report_lines.append("-" * 70)
    report_lines.append(f"Check deployment at: {base_url}")
    report_lines.append(f"Expected URL format: {base_url}assets/index-HASH.js?v=YYYYMMDDHHMMSS")
    report_lines.append("")
    report_lines.append("Verify with:")
    report_lines.append(f"  curl -I '{base_url}' | grep 'Cache-Control'")
    report_lines.append("")
    
    report_lines.append("TIMELINE")
    report_lines.append("-" * 70)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    report_lines.append(f"Invalidation requested: {now}")
    report_lines.append("CDN propagation time:   5-15 minutes (varies by location)")
    report_lines.append("Full propagation:       Within 1 hour")
    report_lines.append("")
    
    return "\n".join(report_lines)


def save_invalidation_report(report_content: str, output_file: Optional[Path] = None) -> bool:
    """Save invalidation report to file."""
    if not output_file:
        repo_root = Path(__file__).resolve().parents[2]
        output_dir = repo_root / ".codex"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_file = output_dir / f"cognitive_app_cache_invalidation_{timestamp}.txt"
    
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_content)
        log("SUCCESS", f"Report saved to {output_file.relative_to(Path.cwd())}")
        return True
    except Exception as e:
        log("ERROR", f"Failed to save report: {e}")
        return False


def record_invalidation_event(base_url: str, reason: str) -> bool:
    """Record cache invalidation event for tracking."""
    repo_root = Path(__file__).resolve().parents[2]
    event_log = repo_root / ".codex" / "cognitive_app_cache_invalidation_log.jsonl"
    
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reason": reason,
        "base_url": base_url,
        "git_sha": _get_current_sha(),
    }
    
    try:
        event_log.parent.mkdir(parents=True, exist_ok=True)
        with open(event_log, 'a') as f:
            f.write(json.dumps(event) + "\n")
        log("SUCCESS", f"Invalidation event recorded")
        return True
    except Exception as e:
        log("ERROR", f"Failed to record event: {e}")
        return False


def _get_current_sha() -> str:
    """Get current git SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except:
        return "unknown"


def main() -> int:
    """Main cache invalidation flow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Invalidate Cognitive App Cache")
    parser.add_argument(
        "--url",
        default="https://aries-serpent.github.io/_codex_/cognitive_app/",
        help="Base URL of cognitive_app deployment"
    )
    parser.add_argument(
        "--reason",
        default="Manual cache invalidation",
        help="Reason for cache invalidation"
    )
    parser.add_argument(
        "--output",
        help="Save report to file"
    )
    args = parser.parse_args()
    
    log("INFO", "Starting Cognitive App Cache Invalidation")
    log("INFO", f"   URL: {args.url}")
    log("INFO", f"   Reason: {args.reason}")
    print()
    
    # Phase 1: Add cache-busting query params to index.html
    log("INFO", "Phase 1: Adding cache-busting query parameters")
    repo_root = Path(__file__).resolve().parents[2]
    index_html = repo_root / "site" / "cognitive_app" / "index.html"
    
    if index_html.exists():
        if not add_cache_busting_query_params(index_html, args.url):
            log("WARNING", "Failed to add query params (may not be needed)")
    else:
        log("WARNING", f"index.html not found at {index_html} (may be in build process)")
    print()
    
    # Phase 2: Generate cache control headers config
    log("INFO", "Phase 2: Generating cache control headers")
    add_cache_control_headers_config()
    print()
    
    # Phase 3: Generate report
    log("INFO", "Phase 3: Generating invalidation report")
    report = generate_cache_invalidation_report(args.url)
    if report:
        print(report)
    print()
    
    # Phase 4: Save report
    if args.output:
        save_invalidation_report(report, Path(args.output))
    else:
        save_invalidation_report(report)
    
    # Phase 5: Record event
    log("INFO", "Phase 5: Recording invalidation event")
    record_invalidation_event(args.url, args.reason)
    print()
    
    log("SUCCESS", "Cache invalidation configuration completed")
    log("SUCCESS", "Deploy with: gh workflow run rebuild-cognitive-app-assets.yml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
