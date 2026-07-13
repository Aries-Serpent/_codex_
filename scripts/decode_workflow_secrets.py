#!/usr/bin/env python3
"""
Decode Workflow Secrets

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/decode_workflow_secrets.py [options]

    Examples:
    $ python scripts/decode_workflow_secrets.py --help

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


from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

import yaml

# Import security utilities for sanitizing sensitive data
try:
    from src.aries_serpent_core.security_utils import sanitize_log_message
except ImportError:
    # Fallback: simple sanitization if security_utils not available
    def sanitize_log_message(msg: str) -> str:
        """Fallback message sanitization."""
        import re
        patterns = [
            (r"ghp_[a-zA-Z0-9]{36,}", "[REDACTED_GITHUB_TOKEN]"),
            (r"github_pat_[a-zA-Z0-9_]{82}", "[REDACTED_GITHUB_PAT]"),
        ]
        result = msg
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        return result


def decode_secret_name(encoded: str) -> str:
    """Decode a base64-encoded secret name."""
    try:
        return base64.b64decode(encoded.encode('ascii')).decode('utf-8')
    except Exception as e:
        return f"[DECODE_ERROR: {e}]"


def list_secret_tokens(inventory_path: Path) -> None:
    """List secret tokens and hints from inventory (safe for display)."""
    if not inventory_path.exists():
        print(f"❌ Inventory file not found: {inventory_path}")
        return

    with open(inventory_path) as f:
        inventory = yaml.safe_load(f)

    print("=" * 70)
    print("SECRET TOKENS (Obfuscated)")
    print("=" * 70)
    print()

    all_secrets = {}
    for workflow in inventory.get("workflows", []):
        for secret_info in workflow.get("secrets_used", []):
            token = secret_info.get("token")
            hint = secret_info.get("hint", "N/A")
            filename = workflow.get("filename", "unknown")

            if token:
                if token not in all_secrets:
                    all_secrets[token] = {
                        "hint": hint,
                        "workflows": []
                    }
                all_secrets[token]["workflows"].append(filename)

    if not all_secrets:
        print("No secrets found in inventory.")
        return

    for i, (token, info) in enumerate(sorted(all_secrets.items()), 1):
        # Security: Use masked fingerprint instead of partial token
        # to prevent clear-text token exposure in logs/output
        token_fp = f"{sanitize_log_message(f'Token: {token[:4]}')}"
        print(f"{i}. {token_fp}... (SHA256)")
        print(f"   Hint: {info['hint']}")
        print(f"   Used in {len(info['workflows'])} workflow(s)")
        print()


def generate_secret_report(inventory_path: Path, authorized: bool = False) -> None:
    """
    Generate secret usage report.

    WARNING: This decodes secret names. Only use with --authorized flag
    in secure, audited contexts.
    """
    if not authorized:
        print("❌ ERROR: Secret decoding requires --authorized flag")
        print()
        print("This operation decodes obfuscated secret names and should only")
        print("be used in authorized security audit contexts.")
        print()
        print("Add --authorized flag to confirm you have permission to decode secrets.")
        sys.exit(1)

    if not inventory_path.exists():
        print(f"❌ Inventory file not found: {inventory_path}")
        return

    with open(inventory_path) as f:
        inventory = yaml.safe_load(f)

    print("=" * 70)
    print("🔐 SECRET USAGE REPORT (AUTHORIZED DECODING)")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This report contains decoded secret names.")
    print("    Do not expose this output in logs, dashboards, or public systems.")
    print()

    all_secrets = {}
    for workflow in inventory.get("workflows", []):
        for secret_info in workflow.get("secrets_used", []):
            encoded = secret_info.get("encoded")
            token = secret_info.get("token")
            hint = secret_info.get("hint", "N/A")
            filename = workflow.get("filename", "unknown")

            if encoded and token:
                decoded_name = decode_secret_name(encoded)

                if decoded_name not in all_secrets:
                    all_secrets[decoded_name] = {
                        "token": token,
                        "hint": hint,
                        "workflows": []
                    }
                all_secrets[decoded_name]["workflows"].append(filename)

    if not all_secrets:
        print("No secrets found in inventory.")
        return

    print(f"Total unique secrets: {len(all_secrets)}")
    print()

    for i, (secret_name, info) in enumerate(sorted(all_secrets.items()), 1):
        print(f"{i}. Secret: {secret_name}")
        # Security: Use masked token instead of partial token display
        # to prevent clear-text token exposure in logs/output
        token_fp = sanitize_log_message(f"Token: {info['token'][:4]}")
        print(f"   {token_fp}...")
        print(f"   Hint: {info['hint']}")
        print(f"   Used in {len(info['workflows'])} workflow(s):")
        for wf in sorted(info['workflows']):
            print(f"      - {wf}")
        print()

    print("=" * 70)
    print("End of report - Ensure secure handling of this output")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Decode tokenized secret names from workflow inventory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Decode single secret
  %(prog)s --encoded "R0lUSFVCX1RPS0VO"

  # List secret tokens (safe, no decoding)
  %(prog)s --list-tokens

  # Generate full report (requires authorization)
  %(prog)s --report --authorized
"""
    )

    parser.add_argument(
        "--encoded",
        help="Base64-encoded secret name to decode"
    )

    parser.add_argument(
        "--list-tokens",
        action="store_true",
        help="List secret tokens and hints (no decoding)"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate secret usage report (requires --authorized)"
    )

    parser.add_argument(
        "--authorized",
        action="store_true",
        help="Confirm authorization to decode secret names"
    )

    parser.add_argument(
        "--inventory",
        default=".github/workflow-archive/WORKFLOW_INVENTORY.yaml",
        help="Path to inventory file (default: .github/workflow-archive/WORKFLOW_INVENTORY.yaml)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.encoded, args.list_tokens, args.report]):
        parser.print_help()
        sys.exit(1)

    # Handle single decode
    if args.encoded:
        decoded = decode_secret_name(args.encoded)
        # Security: Use proper masking instead of showing any part of decoded secret
        # This prevents clear-text exposure of secret names
        if decoded and not decoded.startswith("["):
            # Secret was successfully decoded - mask it completely
            sanitized = sanitize_log_message(decoded)
            print(f"Decoded: {sanitized}")
        else:
            print(f"Decoded: {decoded}")
        return

    # Handle token listing (safe, no decoding)
    if args.list_tokens:
        list_secret_tokens(Path(args.inventory))
        return

    # Handle report generation (requires authorization)
    if args.report:
        generate_secret_report(Path(args.inventory), args.authorized)
        return


if __name__ == "__main__":
    main()
