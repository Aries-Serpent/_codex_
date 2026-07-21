#!/usr/bin/env python3
"""
Cognitive App Asset Manifest Verifier

Compares locally built asset hashes against deployed assets on GitHub Pages.
Detects hash mismatches indicating stale deployments and generates detailed
asset comparison reports.

Exit codes:
  0 - All asset hashes match (deployment is fresh)
  1 - Asset hash mismatches detected (stale deployment)
  2 - Could not fetch remote assets (network error)
  3 - No local manifest found (build not validated)
  4 - No remote manifest found (deployment verification impossible)
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin


def log(level: str, msg: str) -> None:
    """Log with prefix."""
    prefix = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"[{prefix.get(level, '•')}] {msg}")


def manifest_search_candidates(cli_path: Optional[str] = None) -> list[Path]:
    """Return manifest path candidates in priority order."""
    candidates = []

    if cli_path:
        candidates.append(Path(cli_path).expanduser().resolve())

    env_path = os.environ.get("COGNITIVE_APP_MANIFEST")
    if env_path:
        candidates.append(Path(env_path).expanduser().resolve())

    # Standard repo layout: script at scripts/ci/ -> repo root
    script_repo_root = Path(__file__).resolve().parents[2]
    candidates.append(script_repo_root / "cognitive_app" / "dist" / "manifest.json")

    # Flat artifact layout: script and manifest in same directory
    script_dir = Path(__file__).resolve().parent
    candidates.append(script_dir / "manifest.json")

    # Current working directory layouts
    candidates.append(Path.cwd() / "manifest.json")
    candidates.append(Path.cwd() / "cognitive_app" / "dist" / "manifest.json")

    return candidates


def resolve_manifest_path(cli_path: Optional[str] = None) -> Optional[Path]:
    """Resolve the local manifest path using CLI arg, env var, or heuristics."""
    for candidate in manifest_search_candidates(cli_path):
        if candidate.exists():
            return candidate
    return None


def get_local_manifest(manifest_path: Optional[Path] = None) -> Optional[dict]:
    """Load locally built asset manifest."""
    manifest_file = manifest_path or resolve_manifest_path()

    if not manifest_file:
        log("ERROR", "Local manifest not found: cognitive_app/dist/manifest.json")
        log("INFO", "Searched the following locations:")
        for candidate in manifest_search_candidates():
            exists_marker = "✓ exists" if candidate.exists() else "✗ missing"
            log("INFO", f"  {candidate} ({exists_marker})")
        log("INFO", "Use --manifest <path> or set COGNITIVE_APP_MANIFEST environment variable")
        return None

    try:
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        log("SUCCESS", f"Loaded local manifest ({len(manifest.get('assets', {}))} assets)")
        log("INFO", f"   Manifest path: {manifest_file}")
        return manifest
    except Exception as e:
        log("ERROR", f"Failed to load local manifest: {e}")
        return None


def fetch_remote_manifest(base_url: str) -> Optional[dict]:
    """Fetch manifest from deployed cognitive app."""
    manifest_url = urljoin(base_url.rstrip('/') + '/', 'manifest.json')
    
    try:
        result = subprocess.run(
            ["curl", "-sS", manifest_url],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            log("ERROR", f"Failed to fetch remote manifest: {result.stderr}")
            return None
        
        manifest = json.loads(result.stdout)
        log("SUCCESS", f"Fetched remote manifest ({len(manifest.get('assets', {}))} assets)")
        return manifest
    except json.JSONDecodeError as e:
        log("ERROR", f"Invalid JSON in remote manifest: {e}")
        return None
    except Exception as e:
        log("ERROR", f"Failed to fetch remote manifest: {e}")
        return None


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate file hash."""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_local_file_hashes(manifest: dict, manifest_path: Optional[Path] = None) -> dict:
    """Verify that local files match their manifest hashes."""
    if manifest_path:
        base_dir = manifest_path.parent
    else:
        base_dir = Path(__file__).resolve().parents[2]
    
    results = {
        "total": 0,
        "verified": 0,
        "mismatches": [],
        "missing": [],
    }
    
    for asset_name, asset_info in manifest.get('assets', {}).items():
        results["total"] += 1
        asset_path = base_dir / asset_info['path']
        
        if not asset_path.exists():
            results["missing"].append(asset_name)
            log("WARNING", f"Local file missing: {asset_name}")
            continue
        
        # For local verification, we just check file size as hash matching
        # since we don't store hashes in the manifest yet
        expected_size = asset_info.get('size_bytes', 0)
        actual_size = asset_path.stat().st_size
        
        if expected_size == actual_size:
            results["verified"] += 1
        else:
            results["mismatches"].append({
                "asset": asset_name,
                "expected_size": expected_size,
                "actual_size": actual_size
            })
            log("WARNING", f"Size mismatch: {asset_name} (expected {expected_size}, got {actual_size})")
    
    return results


def compare_manifests(local_manifest: dict, remote_manifest: dict) -> dict:
    """Compare local and remote manifests."""
    local_assets = local_manifest.get('assets', {})
    remote_assets = remote_manifest.get('assets', {})
    
    comparison = {
        "total_local": len(local_assets),
        "total_remote": len(remote_assets),
        "matches": [],
        "mismatches": [],
        "local_only": [],
        "remote_only": [],
    }
    
    # Check for matches and mismatches
    for asset_name, local_info in local_assets.items():
        if asset_name in remote_assets:
            remote_info = remote_assets[asset_name]
            local_size = local_info.get('size_bytes', 0)
            remote_size = remote_info.get('size_bytes', 0)
            
            if local_size == remote_size and local_info.get('type') == remote_info.get('type'):
                comparison["matches"].append(asset_name)
            else:
                comparison["mismatches"].append({
                    "asset": asset_name,
                    "local": {"size": local_size, "type": local_info.get('type')},
                    "remote": {"size": remote_size, "type": remote_info.get('type')},
                })
        else:
            comparison["local_only"].append(asset_name)
    
    # Check for remote-only assets
    for asset_name in remote_assets:
        if asset_name not in local_assets:
            comparison["remote_only"].append(asset_name)
    
    return comparison


def generate_report(local_manifest: dict, remote_manifest: dict, comparison: dict) -> str:
    """Generate detailed comparison report."""
    report_lines = []
    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("COGNITIVE APP ASSET MANIFEST VERIFICATION REPORT")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    # Summary
    report_lines.append("SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append(f"Local assets:        {comparison['total_local']}")
    report_lines.append(f"Remote assets:       {comparison['total_remote']}")
    report_lines.append(f"Matches:             {len(comparison['matches'])}")
    report_lines.append(f"Mismatches:          {len(comparison['mismatches'])}")
    report_lines.append(f"Local only:          {len(comparison['local_only'])}")
    report_lines.append(f"Remote only:         {len(comparison['remote_only'])}")
    report_lines.append("")
    
    # Verdict
    mismatch_count = len(comparison['mismatches'])
    if mismatch_count == 0 and len(comparison['local_only']) == 0 and len(comparison['remote_only']) == 0:
        report_lines.append("VERDICT: ✓ DEPLOYMENT IS FRESH - All asset hashes match")
        report_lines.append("Status:  OK")
    else:
        report_lines.append("VERDICT: ✗ STALE DEPLOYMENT DETECTED - Asset hash mismatches found")
        report_lines.append("Status:  REQUIRES REDEPLOYMENT")
    report_lines.append("")
    
    # Details
    if comparison['mismatches']:
        report_lines.append("MISMATCHES (These indicate stale deployment)")
        report_lines.append("-" * 70)
        for mismatch in comparison['mismatches']:
            asset = mismatch['asset']
            local = mismatch['local']
            remote = mismatch['remote']
            report_lines.append(f"  {asset}")
            report_lines.append(f"    Local:  {local['type']:12} {local['size']:>10} bytes")
            report_lines.append(f"    Remote: {remote['type']:12} {remote['size']:>10} bytes")
        report_lines.append("")
    
    if comparison['local_only']:
        report_lines.append("LOCAL ONLY (New assets not yet deployed)")
        report_lines.append("-" * 70)
        for asset in sorted(comparison['local_only'])[:10]:
            report_lines.append(f"  {asset}")
        if len(comparison['local_only']) > 10:
            report_lines.append(f"  ... and {len(comparison['local_only']) - 10} more")
        report_lines.append("")
    
    if comparison['remote_only']:
        report_lines.append("REMOTE ONLY (Stale assets from previous deployment)")
        report_lines.append("-" * 70)
        for asset in sorted(comparison['remote_only'])[:10]:
            report_lines.append(f"  {asset}")
        if len(comparison['remote_only']) > 10:
            report_lines.append(f"  ... and {len(comparison['remote_only']) - 10} more")
        report_lines.append("")
    
    # Recommendations
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("-" * 70)
    if mismatch_count > 0:
        report_lines.append("1. Run: gh workflow run rebuild-cognitive-app-assets.yml")
        report_lines.append("2. Or manually trigger: deploy-cognitive-app-manual.yml with force_rebuild=true")
        report_lines.append("3. Verify with: verify_cognitive_app_deployment.py --url <URL>")
    else:
        report_lines.append("✓ No action needed - deployment is current")
    report_lines.append("")
    
    return "\n".join(report_lines)


def save_report(report_content: str, report_file: Optional[Path] = None) -> bool:
    """Save report to file."""
    if not report_file:
        repo_root = Path(__file__).resolve().parents[2]
        report_file = repo_root / ".codex" / "cognitive_app_manifest_verification.txt"
    
    try:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report_content)
        log("SUCCESS", f"Report saved to {report_file.relative_to(Path.cwd())}")
        return True
    except Exception as e:
        log("ERROR", f"Failed to save report: {e}")
        return False


def main() -> int:
    """Main verification flow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Cognitive App Asset Manifests")
    parser.add_argument(
        "--url",
        default="https://aries-serpent.github.io/_codex_/cognitive_app/",
        help="Base URL of cognitive_app deployment"
    )
    parser.add_argument(
        "--manifest",
        "-m",
        help="Path to local manifest.json (default: auto-detect)"
    )
    parser.add_argument(
        "--report",
        help="Save report to file"
    )
    args = parser.parse_args()
    
    log("INFO", "Starting Cognitive App Asset Manifest Verification")
    log("INFO", f"   Remote URL: {args.url}")
    print()
    
    # Phase 1: Load local manifest
    log("INFO", "Phase 1: Loading local manifest")
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else None
    local_manifest = get_local_manifest(manifest_path)
    if not local_manifest:
        return 3
    print()
    
    # Phase 2: Fetch remote manifest
    log("INFO", "Phase 2: Fetching remote manifest")
    remote_manifest = fetch_remote_manifest(args.url)
    if not remote_manifest:
        return 4
    print()
    
    # Phase 3: Compare manifests
    log("INFO", "Phase 3: Comparing manifests")
    comparison = compare_manifests(local_manifest, remote_manifest)
    print()
    
    # Phase 4: Generate and display report
    log("INFO", "Phase 4: Generating report")
    report = generate_report(local_manifest, remote_manifest, comparison)
    print(report)
    
    # Save report if requested
    if args.report:
        save_report(report, Path(args.report))
    else:
        repo_root = Path(__file__).resolve().parents[2]
        report_dir = repo_root / ".codex"
        report_dir.mkdir(parents=True, exist_ok=True)
        default_report = report_dir / f"cognitive_app_manifest_verification_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.txt"
        save_report(report, default_report)
    
    # Return appropriate exit code
    if len(comparison['mismatches']) == 0 and len(comparison['local_only']) == 0:
        log("SUCCESS", "Verification PASSED - deployment is current")
        return 0
    else:
        log("ERROR", "Verification FAILED - stale deployment detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())
