#!/usr/bin/env python3
"""
🔐 Bootstrap Extractor for _codex_ Token Security System

Extracts base64-encoded tools from GitHub variables/secrets
"""
import base64
import json
import os
from pathlib import Path
from typing import Any


class BootstrapExtractor:
    """Extracts and deploys token security tools from environment variables"""

    # Environment variable names for encoded payloads
    ENV_VARS = {
        'encryption_tool': 'CODEX_SECURITY_ENCRYPTION_TOOL_B64',
        'decoder_module': 'CODEX_SECURITY_DECODER_MODULE_B64',
        'admin_guide': 'CODEX_SECURITY_ADMIN_GUIDE_B64',
        'copilot_guide': 'CODEX_SECURITY_COPILOT_GUIDE_B64',
        'manifest': 'CODEX_SECURITY_MANIFEST_JSON'
    }

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load manifest from environment or use defaults"""
        manifest_json = os.getenv(self.ENV_VARS['manifest'])

        if manifest_json:
            try:
                return json.loads(base64.b64decode(manifest_json).decode())
            except Exception:
                pass

        # Default manifest
        return {
            'version': '1.0.0',
            'tools': {
                'encryption_tool': {
                    'filename': 'token_encryption_tool.py',
                    'output_path': 'scripts/security/',
                    'executable': True,
                    'description': 'Admin tool for token encryption'
                },
                'decoder_module': {
                    'filename': 'copilot_token_decoder.py',
                    'output_path': 'scripts/security/',
                    'executable': False,
                    'description': 'Copilot module for token decryption'
                },
                'admin_guide': {
                    'filename': 'ADMIN_TOKEN_SETUP.md',
                    'output_path': 'docs/admin/security/',
                    'executable': False,
                    'description': 'Admin setup documentation'
                },
                'copilot_guide': {
                    'filename': 'COPILOT_TOKEN_USAGE.md',
                    'output_path': 'docs/admin/security/',
                    'executable': False,
                    'description': 'Copilot implementation guide'
                }
            }
        }

    def extract_tool(self, tool_name: str) -> bool:
        """Extract a specific tool from environment variable"""
        env_var = self.ENV_VARS.get(tool_name)
        if not env_var:
            print(f"❌ Unknown tool: {tool_name}")
            return False

        encoded_content = os.getenv(env_var)
        if not encoded_content:
            print(f"⚠️  Environment variable {env_var} not set")
            return False

        try:
            # Decode base64 content
            content = base64.b64decode(encoded_content).decode('utf-8')

            # Get tool metadata from manifest
            tool_meta = self.manifest['tools'].get(tool_name, {})
            output_path = Path(tool_meta.get('output_path', '.'))
            filename = tool_meta.get('filename', f'{tool_name}.txt')
            executable = tool_meta.get('executable', False)

            # Create output directory
            full_output_dir = self.output_dir / output_path
            full_output_dir.mkdir(parents=True, exist_ok=True)

            # Write file
            output_file = full_output_dir / filename
            output_file.write_text(content)

            # Make executable if needed (owner-only for security)
            if executable:
                os.chmod(output_file, 0o700)

            print(f"✅ Extracted: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to extract {tool_name}: {e}")
            return False

    def extract_all(self) -> int:
        """Extract all tools, return count of successful extractions"""
        print("\n🔐 _CODEX_ Security Tools Bootstrap Extractor")
        print("=" * 70)

        success_count = 0
        for tool_name in self.manifest['tools'].keys():
            if self.extract_tool(tool_name):
                success_count += 1

        print("=" * 70)
        print(f"✅ Successfully extracted {success_count}/{len(self.manifest['tools'])} tools")

        return success_count

    def print_setup_instructions(self):
        """Print human-readable setup instructions"""
        print("\n📋 NEXT STEPS FOR ADMIN SETUP:")
        print("=" * 70)
        print("1. Run the encryption tool:")
        print("   python scripts/security/token_encryption_tool.py")
        print("")
        print("2. Follow the prompts to encrypt your GitHub token")
        print("")
        print("3. Copy the generated secret values to GitHub:")
        print("   https://github.com/Aries-Serpent/_codex_/settings/secrets/actions")
        print("")
        print("4. Revoke the original token after setup")
        print("")
        print("5. Test Copilot Agent token retrieval:")
        print("   python -c 'from scripts.security.copilot_token_decoder import copilot_get_github_token; print(\"✅\" if copilot_get_github_token() else \"❌\")'")
        print("=" * 70)


def main():
    """Main entry point for bootstrap extraction"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract _codex_ token security tools from environment'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory (default: current directory)'
    )
    parser.add_argument(
        '--tool',
        choices=['encryption_tool', 'decoder_module', 'admin_guide', 'copilot_guide', 'all'],
        default='all',
        help='Tool to extract (default: all)'
    )

    args = parser.parse_args()

    extractor = BootstrapExtractor(args.output_dir)

    if args.tool == 'all':
        extractor.extract_all()
    else:
        extractor.extract_tool(args.tool)

    extractor.print_setup_instructions()


if __name__ == '__main__':
    main()
