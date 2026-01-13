#!/usr/bin/env python3
"""
IMMEDIATE EXECUTION: Automated Phase 10 Secrets Injection
Copilot Agent can run this NOW with GITHUB_ACTIONS token

User Authorization: mbaetiong granted FULL ACCESS (comment #3745423798)
Capabilities: GitHub API, CLI, MCP access enabled
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_environment():
    """Check if we have the necessary tokens and tools."""
    print("🔍 Checking environment...")
    print("=" * 60)
    
    # Check for GitHub token
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        print(f"✅ GitHub token found (length: {len(token)})")
    else:
        print("❌ No GitHub token found")
        return False
    
    # Check for gh CLI
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            check=True
        )
        print(f"✅ gh CLI available: {result.stdout.decode().split()[2]}")
    except Exception:
        print("⚠️  gh CLI not available (will use API)")
    
    # Check repository context
    repo = os.getenv("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
    print(f"📦 Repository: {repo}")
    
    return True

def inject_secret_via_cli(name, value):
    """Inject secret using gh CLI (simplest method)."""
    try:
        process = subprocess.Popen(
            [
                "gh", "secret", "set", name,
                "--repo", "Aries-Serpent/_codex_"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )
        
        stdout, stderr = process.communicate(input=value)
        
        if process.returncode == 0:
            print(f"✅ {name} injected successfully via gh CLI")
            return True
        else:
            print(f"❌ {name} failed: {stderr}")
            return False
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return False

def generate_codex_master_key():
    """Generate CODEX_MASTER_KEY using openssl."""
    try:
        result = subprocess.run(
            ["openssl", "rand", "-base64", "32"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Failed to generate key: {e}")
        return None

def verify_secret_exists(name):
    """Check if secret already exists."""
    try:
        result = subprocess.run(
            ["gh", "secret", "list", "--repo", "Aries-Serpent/_codex_"],
            capture_output=True,
            text=True,
            check=True
        )
        return name in result.stdout
    except Exception:
        return False

def main():
    """Execute immediate automated secrets injection."""
    print("\n🚀 Phase 10 Automated Secrets Injection")
    print("========================================")
    print("User Authorization: FULL ACCESS granted by mbaetiong")
    print("Comment: #3745423798 + new_requirement")
    print("")
    
    if not check_environment():
        print("\n❌ Environment check failed")
        print("Required: GITHUB_TOKEN or GH_TOKEN + gh CLI")
        return 1
    
    print("\n📋 Phase 10 Secrets Setup Plan")
    print("=" * 60)
    print("1. ✅ CODEX_MASTER_KEY - AUTO-GENERATE (if not exists)")
    print("2. ⏸️  GDRIVE_SERVICE_ACCOUNT_JSON - REQUIRES GOOGLE CLOUD SETUP")
    print("3. ⏸️  GOOGLE_CLIENT_ID - REQUIRES GOOGLE CLOUD SETUP")
    print("4. ⏸️  GOOGLE_CLIENT_SECRET - REQUIRES GOOGLE CLOUD SETUP")
    print("")
    
    # Step 1: CODEX_MASTER_KEY (can auto-generate)
    print("\n🔑 Step 1: CODEX_MASTER_KEY")
    print("-" * 60)
    
    if verify_secret_exists("CODEX_MASTER_KEY"):
        print("✅ CODEX_MASTER_KEY already exists")
        print("   (Use --force flag in workflow to regenerate)")
    else:
        print("Generating new CODEX_MASTER_KEY...")
        key = generate_codex_master_key()
        if key:
            print(f"🔑 Generated 256-bit key: {key[:8]}...{key[-8:]}")
            if inject_secret_via_cli("CODEX_MASTER_KEY", key):
                print("✅ CODEX_MASTER_KEY configured successfully")
            else:
                print("❌ Failed to inject CODEX_MASTER_KEY")
                return 1
        else:
            print("❌ Failed to generate CODEX_MASTER_KEY")
            return 1
    
    # Steps 2-4: Google Cloud secrets (require user input)
    print("\n🔐 Steps 2-4: Google Cloud Secrets")
    print("-" * 60)
    print("⚠️  Google Cloud secrets require manual configuration:")
    print("")
    print("Option A: Via Workflow (RECOMMENDED for Copilot Agent)")
    print("  1. Complete Google Cloud setup (HA-GC-001)")
    print("  2. Obtain service account JSON + OAuth credentials")
    print("  3. Trigger: phase10-automated-secrets-setup.yml")
    print("  4. Provide values via workflow inputs")
    print("")
    print("Option B: Via Script (requires JSON files locally)")
    print("  1. Save service-account.json locally")
    print("  2. Run: scripts/phase10/inject_google_secrets.sh")
    print("")
    print("Option C: Via GitHub UI (manual, slowest)")
    print("  1. Navigate to repository Settings → Secrets")
    print("  2. Add each secret manually")
    print("")
    
    # Check current status
    print("\n📊 Current Secrets Status")
    print("=" * 60)
    
    secrets_to_check = [
        "CODEX_MASTER_KEY",
        "GDRIVE_SERVICE_ACCOUNT_JSON",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "NOTEBOOKLM_WEBHOOK_URL"
    ]
    
    configured_count = 0
    for secret in secrets_to_check:
        if verify_secret_exists(secret):
            print(f"✅ {secret}")
            configured_count += 1
        else:
            print(f"⏸️  {secret} - Not configured")
    
    print("")
    print(f"Progress: {configured_count}/{len(secrets_to_check)} secrets configured")
    
    if configured_count == len(secrets_to_check):
        print("\n🎉 All Phase 10 secrets configured!")
        print("Ready to proceed with:")
        print("  - HA-WF-001: First workflow trigger")
        print("  - HA-NB-001: NotebookLM setup")
    elif configured_count >= 1:
        print("\n✅ Partial success - CODEX_MASTER_KEY ready")
        print("⏸️  Complete Google Cloud setup for remaining secrets")
        print("   See: HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md (HA-GC-001)")
    
    print("\n📚 Documentation References")
    print("=" * 60)
    print("  • Full tracker: HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md")
    print("  • Automation analysis: AUTOMATION_CAPABILITY_ANALYSIS_PHASE10.md")
    print("  • Python API tool: scripts/phase10/automated_secrets_manager.py")
    print("  • Workflow: .github/workflows/phase10-automated-secrets-setup.yml")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
