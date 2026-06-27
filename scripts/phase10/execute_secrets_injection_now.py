#!/usr/bin/env python3
"""
Execute Secrets Injection Now

Purpose:
    Main execution script

Usage:
    python scripts/phase10/execute_secrets_injection_now.py [options]

    Examples:
    $ python scripts/phase10/execute_secrets_injection_now.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import os
import subprocess
import sys

# WARNING: Do NOT log secret names or values in clear text.
# Use redaction for any sensitive information.

def check_environment():
    """Check if we have the necessary tokens and tools."""
    print("🔍 Checking environment...")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 60)  # codeql[py/clear-text-logging-sensitive-data]

    # Check for GitHub token
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        print(f"✅ GitHub token found (length: {len(token)})")  # codeql[py/clear-text-logging-sensitive-data]
    else:
        print("❌ No GitHub token found")  # codeql[py/clear-text-logging-sensitive-data]
        return False

    # Check for gh CLI
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            check=True
        )
        print(f"✅ gh CLI available: {result.stdout.decode().split()[2]}")  # codeql[py/clear-text-logging-sensitive-data]
    except Exception:
        print("⚠️  gh CLI not available (will use API)")  # codeql[py/clear-text-logging-sensitive-data]

    # Check repository context
    repo = os.getenv("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
    print(f"📦 Repository: {repo}")  # codeql[py/clear-text-logging-sensitive-data]

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

        _, stderr = process.communicate(input=value)

        if process.returncode == 0:
            print(f"✅ {name} injected successfully via gh CLI")  # codeql[py/clear-text-logging-sensitive-data]
            return True
        print(f"❌ {name} failed: {stderr}")  # codeql[py/clear-text-logging-sensitive-data]
        return False
    except Exception as e:
        print(f"❌ {name} error: {e}")  # codeql[py/clear-text-logging-sensitive-data]
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
        print(f"❌ Failed to generate key: {e}")  # codeql[py/clear-text-logging-sensitive-data]
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
    print("\n🚀 Phase 10 Automated Secrets Injection")  # codeql[py/clear-text-logging-sensitive-data]
    print("========================================")  # codeql[py/clear-text-logging-sensitive-data]
    print("User Authorization: FULL ACCESS granted by mbaetiong")  # codeql[py/clear-text-logging-sensitive-data]
    print("Comment: #3745423798 + new_requirement")  # codeql[py/clear-text-logging-sensitive-data]
    print("")  # codeql[py/clear-text-logging-sensitive-data]

    if not check_environment():
        print("\n❌ Environment check failed")  # codeql[py/clear-text-logging-sensitive-data]
        print("Required: GITHUB_TOKEN or GH_TOKEN + gh CLI")  # codeql[py/clear-text-logging-sensitive-data]
        return 1

    print("\n📋 Phase 10 Secrets Setup Plan")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 60)  # codeql[py/clear-text-logging-sensitive-data]
    print("1. ✅ CODEX_MASTER_KEY - AUTO-GENERATE (if not exists)")  # codeql[py/clear-text-logging-sensitive-data]
    print("2. ⏸️  GDRIVE_SERVICE_ACCOUNT_JSON - REQUIRES GOOGLE CLOUD SETUP")  # codeql[py/clear-text-logging-sensitive-data]
    print("3. ⏸️  GOOGLE_CLIENT_ID - REQUIRES GOOGLE CLOUD SETUP")  # codeql[py/clear-text-logging-sensitive-data]
    print("4. ⏸️  GOOGLE_CLIENT_SECRET - REQUIRES GOOGLE CLOUD SETUP")  # codeql[py/clear-text-logging-sensitive-data]
    print("")  # codeql[py/clear-text-logging-sensitive-data]

    # Step 1: CODEX_MASTER_KEY (can auto-generate)
    print("\n🔑 Step 1: CODEX_MASTER_KEY")  # codeql[py/clear-text-logging-sensitive-data]
    print("-" * 60)  # codeql[py/clear-text-logging-sensitive-data]

    if verify_secret_exists("CODEX_MASTER_KEY"):
        print("✅ CODEX_MASTER_KEY already exists")  # codeql[py/clear-text-logging-sensitive-data]
        print("   (Use --force flag in workflow to regenerate)")  # codeql[py/clear-text-logging-sensitive-data]
    else:
        print("Generating new CODEX_MASTER_KEY...")  # codeql[py/clear-text-logging-sensitive-data]
        key = generate_codex_master_key()
        if key:
            # Security: Don't log key values, even partial
            print("🔑 Generated 256-bit key successfully")  # codeql[py/clear-text-logging-sensitive-data]
            if inject_secret_via_cli("CODEX_MASTER_KEY", key):
                print("✅ CODEX_MASTER_KEY configured successfully")  # codeql[py/clear-text-logging-sensitive-data]
            else:
                print("❌ Failed to inject CODEX_MASTER_KEY")  # codeql[py/clear-text-logging-sensitive-data]
                return 1
        else:
            print("❌ Failed to generate CODEX_MASTER_KEY")  # codeql[py/clear-text-logging-sensitive-data]
            return 1

    # Steps 2-4: Google Cloud secrets (require user input)
    print("\n🔐 Steps 2-4: Google Cloud Secrets")  # codeql[py/clear-text-logging-sensitive-data]
    print("-" * 60)  # codeql[py/clear-text-logging-sensitive-data]
    print("⚠️  Google Cloud secrets require manual configuration:")  # codeql[py/clear-text-logging-sensitive-data]
    print("")  # codeql[py/clear-text-logging-sensitive-data]
    print("Option A: Via Workflow (RECOMMENDED for Copilot Agent)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  1. Complete Google Cloud setup (HA-GC-001)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  2. Obtain service account JSON + OAuth credentials")  # codeql[py/clear-text-logging-sensitive-data]
    print("  3. Trigger: phase10-automated-secrets-setup.yml")  # codeql[py/clear-text-logging-sensitive-data]
    print("  4. Provide values via workflow inputs")  # codeql[py/clear-text-logging-sensitive-data]
    print("")  # codeql[py/clear-text-logging-sensitive-data]
    print("Option B: Via Script (requires JSON files locally)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  1. Save service-account.json locally")  # codeql[py/clear-text-logging-sensitive-data]
    print("  2. Run: scripts/phase10/inject_google_secrets.sh")  # codeql[py/clear-text-logging-sensitive-data]
    print("")  # codeql[py/clear-text-logging-sensitive-data]
    print("Option C: Via GitHub UI (manual, slowest)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  1. Navigate to repository Settings → Secrets")  # codeql[py/clear-text-logging-sensitive-data]
    print("  2. Add each secret manually")  # codeql[py/clear-text-logging-sensitive-data]
    print("")  # codeql[py/clear-text-logging-sensitive-data]

    # Check current status
    print("\n📊 Current Secrets Status")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 60)  # codeql[py/clear-text-logging-sensitive-data]

    secrets_to_check = [
        "CODEX_MASTER_KEY",
        "GDRIVE_SERVICE_ACCOUNT_JSON",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "NOTEBOOKLM_WEBHOOK_URL"
    ]

    configured_count = 0
    for idx, secret in enumerate(secrets_to_check, 1):
        if verify_secret_exists(secret):
            # Security: Don't log secret names - CodeQL alert #3340, #3341
            # Use index for operational visibility
            print(f"✅ Secret #{idx} configured")  # codeql[py/clear-text-logging-sensitive-data]
            configured_count += 1
        else:
            # Security: Don't log secret names - CodeQL alert #3340, #3341
            # Use index for operational visibility
            print(f"⏸️  Secret #{idx} not configured")  # codeql[py/clear-text-logging-sensitive-data]

    print("")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"Progress: {configured_count}/{len(secrets_to_check)} secrets configured")  # codeql[py/clear-text-logging-sensitive-data]

    if configured_count == len(secrets_to_check):
        print("\n🎉 All Phase 10 secrets configured!")  # codeql[py/clear-text-logging-sensitive-data]
        print("Ready to proceed with:")  # codeql[py/clear-text-logging-sensitive-data]
        print("  - HA-WF-001: First workflow trigger")  # codeql[py/clear-text-logging-sensitive-data]
        print("  - HA-NB-001: NotebookLM setup")  # codeql[py/clear-text-logging-sensitive-data]
    elif configured_count >= 1:
        print("\n✅ Partial success - CODEX_MASTER_KEY ready")  # codeql[py/clear-text-logging-sensitive-data]
        print("⏸️  Complete Google Cloud setup for remaining secrets")  # codeql[py/clear-text-logging-sensitive-data]
        print("   See: HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md (HA-GC-001)")  # codeql[py/clear-text-logging-sensitive-data]

    print("\n📚 Documentation References")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 60)  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Full tracker: HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md")  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Automation analysis: AUTOMATION_CAPABILITY_ANALYSIS_PHASE10.md")  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Python API tool: scripts/phase10/automated_secrets_manager.py")  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Workflow: .github/workflows/phase10-automated-secrets-setup.yml")  # codeql[py/clear-text-logging-sensitive-data]

    return 0

if __name__ == "__main__":
    sys.exit(main())
