#!/usr/bin/env python3
"""
Cognitive App Deployment History Tracker

Records and tracks every cognitive app deployment with:
- Timestamp
- Version/commit SHA
- Asset hashes
- Deployment status
- Operator/trigger source

Used for audit trail and debugging stale deployments.
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


def get_git_info() -> dict:
    """Get current git information."""
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10
        ).stdout.strip()
        
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10
        ).stdout.strip()
        
        tag = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True,
            timeout=10
        ).stdout.strip() or None
        
        message = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            timeout=10
        ).stdout.strip()
        
        author = subprocess.run(
            ["git", "log", "-1", "--pretty=%an"],
            capture_output=True,
            text=True,
            timeout=10
        ).stdout.strip()
        
        return {
            "sha": sha,
            "branch": branch,
            "tag": tag,
            "message": message[:100],  # First 100 chars
            "author": author,
        }
    except Exception as e:
        log("WARNING", f"Failed to get git info: {e}")
        return {}


def calculate_asset_hashes() -> dict:
    """Calculate hashes of built assets."""
    repo_root = Path(__file__).resolve().parents[2]
    manifest_file = repo_root / "cognitive_app" / "dist" / "manifest.json"
    
    if not manifest_file.exists():
        return {}
    
    try:
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        return {
            "asset_count": len(manifest.get('assets', {})),
            "generated_at": manifest.get('generated_at'),
            "total_size_bytes": sum(
                a.get('size_bytes', 0) for a in manifest.get('assets', {}).values()
            ),
        }
    except Exception as e:
        log("WARNING", f"Failed to read manifest: {e}")
        return {}


def get_deployment_status(base_url: str) -> dict:
    """Check deployment status."""
    status = {
        "accessible": False,
        "http_code": None,
        "has_root_element": False,
        "error": None,
    }
    
    try:
        result = subprocess.run(
            ["curl", "-sS", "-w", "\n%{http_code}", base_url],
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
        
        status["http_code"] = int(http_code.strip())
        status["accessible"] = status["http_code"] == 200
        
        if 'id="root"' in content:
            status["has_root_element"] = True
        
        return status
    except Exception as e:
        status["error"] = str(e)
        return status


def record_deployment(
    deployment_type: str,
    status: str,
    base_url: str = "",
    version: Optional[str] = None,
    reason: str = "",
) -> bool:
    """Record a deployment event."""
    repo_root = Path(__file__).resolve().parents[2]
    history_file = repo_root / ".codex" / "cognitive_app_deployment_history.jsonl"
    
    git_info = get_git_info()
    asset_info = calculate_asset_hashes()
    deploy_status = get_deployment_status(base_url) if base_url else {}
    
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "type": deployment_type,
        "status": status,
        "version": version or git_info.get("sha", "unknown")[:8],
        "base_url": base_url,
        "reason": reason,
        "git": git_info,
        "assets": asset_info,
        "deployment": deploy_status,
    }
    
    try:
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, 'a') as f:
            f.write(json.dumps(event) + "\n")
        log("SUCCESS", f"Deployment recorded: {deployment_type} / {status}")
        return True
    except Exception as e:
        log("ERROR", f"Failed to record deployment: {e}")
        return False


def generate_deployment_history_report(limit: int = 20) -> Optional[str]:
    """Generate a report of recent deployments."""
    repo_root = Path(__file__).resolve().parents[2]
    history_file = repo_root / ".codex" / "cognitive_app_deployment_history.jsonl"
    
    if not history_file.exists():
        return None
    
    try:
        events = []
        with open(history_file, 'r') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        # Sort by timestamp descending
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        events = events[:limit]
        
        report_lines = []
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("COGNITIVE APP DEPLOYMENT HISTORY")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        for i, event in enumerate(events, 1):
            report_lines.append(f"{i}. {event.get('timestamp', 'N/A')}")
            report_lines.append(f"   Type:    {event.get('type', 'unknown')}")
            report_lines.append(f"   Status:  {event.get('status', 'unknown')}")
            report_lines.append(f"   Version: {event.get('version', 'unknown')}")
            
            git = event.get('git', {})
            if git:
                report_lines.append(f"   SHA:     {git.get('sha', 'N/A')[:8]}")
                if git.get('tag'):
                    report_lines.append(f"   Tag:     {git.get('tag')}")
            
            assets = event.get('assets', {})
            if assets:
                report_lines.append(f"   Assets:  {assets.get('asset_count', 0)} files, "
                                  f"{assets.get('total_size_bytes', 0) / (1024 * 1024):.1f}MB")
            
            deploy = event.get('deployment', {})
            if deploy:
                report_lines.append(f"   HTTP:    {deploy.get('http_code', 'N/A')}")
                report_lines.append(f"   React:   {'✓' if deploy.get('has_root_element') else '✗'}")
            
            if event.get('reason'):
                report_lines.append(f"   Reason:  {event.get('reason')}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    except Exception as e:
        log("ERROR", f"Failed to generate report: {e}")
        return None


def main() -> int:
    """Main tracking flow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track Cognitive App Deployments")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # record command
    record_parser = subparsers.add_parser("record", help="Record a deployment event")
    record_parser.add_argument("--type", required=True, help="Deployment type (auto/manual/rollback)")
    record_parser.add_argument("--status", required=True, help="Status (started/success/failed)")
    record_parser.add_argument("--url", help="Deployment base URL")
    record_parser.add_argument("--version", help="Version/tag deployed")
    record_parser.add_argument("--reason", help="Reason for deployment")
    
    # report command
    report_parser = subparsers.add_parser("report", help="Generate deployment history report")
    report_parser.add_argument("--limit", type=int, default=20, help="Number of recent deployments to show")
    report_parser.add_argument("--output", help="Save report to file")
    
    args = parser.parse_args()
    
    if args.command == "record":
        return 0 if record_deployment(
            deployment_type=args.type,
            status=args.status,
            base_url=args.url or "",
            version=args.version,
            reason=args.reason or "",
        ) else 1
    
    elif args.command == "report":
        report = generate_deployment_history_report(args.limit)
        if report:
            print(report)
            if args.output:
                try:
                    with open(args.output, 'w') as f:
                        f.write(report)
                    log("SUCCESS", f"Report saved to {args.output}")
                except Exception as e:
                    log("ERROR", f"Failed to save report: {e}")
                    return 1
            return 0
        else:
            log("INFO", "No deployment history found")
            return 0
    
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
