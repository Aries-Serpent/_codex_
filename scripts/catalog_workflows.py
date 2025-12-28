#!/usr/bin/env python3
"""
Workflow Catalog Generator

Creates comprehensive inventory of all GitHub Actions workflows with metadata.
Stores data in .github/workflow-archive/WORKFLOW_INVENTORY.yaml

SECURITY NOTE: This script extracts secret names (not values) from workflow files.
Secret names are tokenized using SHA256 hashing and stored with base64 encoding
for additional obfuscation. This prevents direct exposure of secret names in the
inventory file while maintaining utility for internal tooling.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of workflow file."""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def tokenize_secret_name(secret_name: str) -> dict[str, str]:
    """
    Tokenize a secret name for secure storage.
    
    Uses SHA256 hashing with base64 encoding to obfuscate secret names
    while maintaining the ability to match and analyze secret usage.
    
    Args:
        secret_name: The plain-text secret name (e.g., "GITHUB_TOKEN")
    
    Returns:
        Dictionary with tokenized representation:
        - token: SHA256 hash of the secret name (for matching)
        - encoded: Base64-encoded secret name (for decoding if authorized)
        - hint: First 3 characters + length (for human reference)
    """
    # Create SHA256 token for matching/deduplication
    token = hashlib.sha256(secret_name.encode()).hexdigest()
    
    # Base64 encode the secret name for reversible obfuscation
    encoded = base64.b64encode(secret_name.encode()).decode('ascii')
    
    # Create a human-readable hint (first 3 chars + length)
    hint = f"{secret_name[:3]}***({len(secret_name)} chars)" if len(secret_name) > 3 else "***"
    
    return {
        "token": token,
        "encoded": encoded,
        "hint": hint
    }


def decode_secret_name(encoded: str) -> str:
    """
    Decode a base64-encoded secret name.
    
    WARNING: Only use this function in authorized contexts.
    
    Args:
        encoded: Base64-encoded secret name
    
    Returns:
        Decoded secret name
    """
    return base64.b64decode(encoded.encode('ascii')).decode('utf-8')


def extract_workflow_metadata(workflow_path: Path) -> dict[str, Any]:
    """Extract metadata from workflow YAML file."""
    try:
        with open(workflow_path) as f:
            workflow_data = yaml.safe_load(f)
        
        if not workflow_data:
            return {"error": "Empty workflow file"}
        
        # Extract key metadata
        metadata = {
            "name": workflow_data.get("name", workflow_path.stem),
            "filename": workflow_path.name,
            "path": str(workflow_path.relative_to(Path.cwd())),
            "triggers": list(workflow_data.get("on", {}).keys()) if isinstance(workflow_data.get("on"), dict) else [str(workflow_data.get("on"))],
            "jobs": list(workflow_data.get("jobs", {}).keys()),
            "job_count": len(workflow_data.get("jobs", {})),
            "permissions": workflow_data.get("permissions", {}),
            "env_vars": list(workflow_data.get("env", {}).keys()),
            "secrets_used": extract_secrets(workflow_data),
            "file_size_bytes": workflow_path.stat().st_size,
            "file_hash": calculate_file_hash(workflow_path),
            "last_modified": datetime.fromtimestamp(workflow_path.stat().st_mtime).isoformat(),
            "category": categorize_workflow(workflow_data, workflow_path.name),
            "consolidation_candidate": False,  # Will be set by analysis
            "status": "active",
        }
        
        return metadata
        
    except Exception as e:
        return {
            "filename": workflow_path.name,
            "error": str(e),
            "status": "error",
        }


def extract_secrets(workflow_data: dict) -> list[dict[str, str]]:
    """
    Extract and tokenize all secret references from workflow.
    
    Returns list of tokenized secret representations (not plain-text names).
    Each entry contains: token (hash), encoded (base64), hint (redacted preview).
    """
    secrets = set()
    workflow_str = json.dumps(workflow_data)
    
    # Find ${{ secrets.SECRET_NAME }} patterns
    secret_pattern = re.compile(r'\$\{\{\s*secrets\.(\w+)\s*\}\}')
    secret_names = secret_pattern.findall(workflow_str)
    
    # Tokenize each secret name
    tokenized_secrets = []
    for secret_name in sorted(set(secret_names)):
        tokenized = tokenize_secret_name(secret_name)
        tokenized_secrets.append(tokenized)
    
    return tokenized_secrets


def categorize_workflow(workflow_data: dict, filename: str) -> str:
    """Categorize workflow by purpose."""
    name = workflow_data.get("name", "").lower()
    filename_lower = filename.lower()
    
    categories = {
        "testing": ["test", "pytest", "coverage", "integration"],
        "ci": ["ci", "build", "compile"],
        "security": ["security", "scan", "codeql", "semgrep", "dependabot"],
        "documentation": ["docs", "documentation", "pages", "mkdocs"],
        "deployment": ["deploy", "release", "publish", "docker"],
        "automation": ["automation", "autonomous", "agent", "copilot"],
        "validation": ["validate", "lint", "check", "verify"],
        "monitoring": ["status", "report", "dashboard", "metrics"],
        "maintenance": ["cleanup", "cache", "archive"],
    }
    
    for category, keywords in categories.items():
        if any(keyword in name or keyword in filename_lower for keyword in keywords):
            return category
    
    return "other"


def identify_consolidation_candidates(inventory: dict) -> dict:
    """Identify workflows that can be consolidated."""
    # Group workflows by category
    by_category = defaultdict(list)
    
    for workflow in inventory["workflows"]:
        if workflow.get("status") == "active":
            by_category[workflow["category"]].append(workflow)
    
    consolidation_plan = {
        "testing": {
            "keep": ["optimized-ci.yml", "integration-gated.yml"],
            "remove": ["test-suite.yml", "mcp-ci.yml"],
            "reason": "Consolidated into optimized-ci.yml with MCP tests as additional job",
        },
        "documentation": {
            "keep": ["pages-mkdocs.yml", "documentation-link-checker.yml"],
            "remove": ["docs.yml", "validate-docs.yml", "validate-docs-enhanced.yml"],
            "reason": "pages-mkdocs.yml handles all doc building and deployment",
        },
        "deployment": {
            "keep": ["docker-build-push.yml"],
            "remove": ["container-build.yml", "build-container-cache.yml"],
            "reason": "Unified container build with matrix strategy for CPU/GPU variants",
        },
        "validation": {
            "keep": ["workflow-validation.yml"],
            "remove": ["workflow-lint.yml", "workflow-validator.yml", "template-validation.yml"],
            "reason": "Single validation pipeline with sequential jobs",
        },
        "monitoring": {
            "keep": ["daily-status-pipeline.yml", "publish_dashboard_release.yml"],
            "remove": ["daily_status_cron.yml", "daily_status_enrich.yml", "automation_ingest.yml", "produce-trend.yml", "report_publish.yml"],
            "reason": "Consolidated into single pipeline with job dependencies",
        },
        "maintenance": {
            "keep": ["cache-management.yml"],
            "remove": ["cache-cleanup.yml", "cache-warmer.yml"],
            "reason": "Unified cache operations with scheduled jobs",
        },
    }
    
    # Mark consolidation candidates
    for workflow in inventory["workflows"]:
        for category, plan in consolidation_plan.items():
            if workflow["filename"] in plan.get("remove", []):
                workflow["consolidation_candidate"] = True
                workflow["consolidation_plan"] = plan["reason"]
                workflow["consolidation_keep"] = plan["keep"]
    
    return consolidation_plan


def generate_inventory():
    """Generate comprehensive workflow inventory."""
    workflows_dir = Path(".github/workflows")
    
    if not workflows_dir.exists():
        print(f"❌ Workflows directory not found: {workflows_dir}")
        return
    
    # Scan all workflow files
    workflow_files = sorted(workflows_dir.glob("*.yml")) + sorted(workflows_dir.glob("*.yaml"))
    
    inventory = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_workflows": len(workflow_files),
            "active_count": 0,
            "disabled_count": 0,
            "archived_count": 0,
            "consolidation_target": 48,
        },
        "workflows": [],
    }
    
    print(f"📊 Cataloging {len(workflow_files)} workflows...")
    
    for workflow_file in workflow_files:
        print(f"  Processing: {workflow_file.name}")
        metadata = extract_workflow_metadata(workflow_file)
        inventory["workflows"].append(metadata)
        
        if metadata.get("status") == "active":
            inventory["metadata"]["active_count"] += 1
    
    # Identify consolidation candidates
    consolidation_plan = identify_consolidation_candidates(inventory)
    inventory["consolidation_plan"] = consolidation_plan
    
    # Save inventory
    inventory_path = Path(".github/workflow-archive/WORKFLOW_INVENTORY.yaml")
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(inventory_path, "w") as f:
        yaml.dump(inventory, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Inventory saved to: {inventory_path}")
    print(f"   Total workflows: {inventory['metadata']['total_workflows']}")
    print(f"   Active: {inventory['metadata']['active_count']}")
    print(f"   Consolidation candidates: {sum(1 for w in inventory['workflows'] if w.get('consolidation_candidate'))}")
    
    # Security note: Secret names are stored in inventory file but NOT logged to console
    # to prevent information disclosure in CI logs
    
    # Generate summary report
    generate_summary_report(inventory)


def generate_summary_report(inventory: dict):
    """Generate human-readable summary report."""
    report_path = Path(".github/workflow-archive/INVENTORY_SUMMARY.md")
    
    with open(report_path, "w") as f:
        f.write("# Workflow Inventory Summary\n\n")
        f.write(f"**Generated**: {inventory['metadata']['generated_at']}\n\n")
        f.write(f"**Total Workflows**: {inventory['metadata']['total_workflows']}\n\n")
        
        # Category breakdown
        f.write("## Workflows by Category\n\n")
        by_category = defaultdict(list)
        for workflow in inventory["workflows"]:
            by_category[workflow.get("category", "other")].append(workflow)
        
        for category, workflows in sorted(by_category.items()):
            f.write(f"### {category.title()} ({len(workflows)} workflows)\n\n")
            for workflow in workflows:
                status_icon = "🟢" if workflow.get("status") == "active" else "🔴"
                consolidation_icon = "⚠️" if workflow.get("consolidation_candidate") else ""
                f.write(f"- {status_icon} {consolidation_icon} `{workflow['filename']}` - {workflow.get('name', 'N/A')}\n")
            f.write("\n")
        
        # Consolidation candidates
        candidates = [w for w in inventory["workflows"] if w.get("consolidation_candidate")]
        if candidates:
            f.write(f"## Consolidation Candidates ({len(candidates)} workflows)\n\n")
            for workflow in candidates:
                f.write(f"### `{workflow['filename']}`\n\n")
                f.write(f"**Reason**: {workflow.get('consolidation_plan', 'N/A')}\n\n")
                f.write(f"**Will be replaced by**: {', '.join(workflow.get('consolidation_keep', []))}\n\n")
        
        # Secrets usage - SECURITY NOTE: Removed to prevent information disclosure
        # Secret names are stored in WORKFLOW_INVENTORY.yaml for internal tooling only
        # but should not be exposed in human-readable markdown reports
        f.write("## Secrets Usage\n\n")
        f.write("_Secret usage information has been omitted from this report for security reasons._\n\n")
        f.write("_Secret names are available in `WORKFLOW_INVENTORY.yaml` for authorized tooling use only._\n\n")
    
    print(f"✅ Summary report saved to: {report_path}")


if __name__ == "__main__":
    generate_inventory()
