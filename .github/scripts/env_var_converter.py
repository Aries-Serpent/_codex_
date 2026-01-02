#!/usr/bin/env python3
"""
Automated GitHub Environment Variable Converter

Converts eligible Python files to base64-encoded environment variables and
maintains synchronization between source files and GitHub environment variables.

PDA Loop: Problem → Definition → Analysis
AfterMath: Validation → Impact Analysis → Continuous Improvement

Usage:
    python3 env_var_converter.py --mode encode --file src/path/to/file.py
    python3 env_var_converter.py --mode sync --environment production
    python3 env_var_converter.py --mode verify --all
    python3 env_var_converter.py --mode list-candidates
"""

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
MAX_ENV_SIZE = 48 * 1024  # 48KB GitHub limit
BASE64_OVERHEAD = 1.33  # Base64 increases size by ~33%
MAX_ORIGINAL_SIZE = int(MAX_ENV_SIZE / BASE64_OVERHEAD)  # ~36KB

# Candidate files with priority and metadata
CANDIDATES_CONFIG = [
    {
        "path": "src/cognitive_brain/quantum/ghz_states.py",
        "env_var": "COGNITIVE_BRAIN_GHZ_STATES",
        "priority": 1,
        "description": "Multi-agent GHZ state management",
        "category": "cognitive_brain",
        "auto_sync": True,
    },
    {
        "path": "src/cognitive_brain/quantum/multi_agent_coordinator.py",
        "env_var": "COGNITIVE_BRAIN_COORDINATOR",
        "priority": 1,
        "description": "Multi-agent orchestration hub",
        "category": "cognitive_brain",
        "auto_sync": True,
    },
    {
        "path": "src/cognitive_brain/quantum/topology_manager.py",
        "env_var": "COGNITIVE_BRAIN_TOPOLOGY",
        "priority": 2,
        "description": "Network topology management",
        "category": "cognitive_brain",
        "auto_sync": True,
    },
    {
        "path": "src/codex_ml/data/validation.py",
        "env_var": "CODEX_ML_VALIDATION",
        "priority": 2,
        "description": "Data validation framework",
        "category": "validation",
        "auto_sync": True,
    },
    {
        "path": "src/codex_ml/config/__init__.py",
        "env_var": "CODEX_ML_CONFIG",
        "priority": 3,
        "description": "Configuration management (near limit)",
        "category": "config",
        "auto_sync": False,  # Manual due to size concerns
    },
]


@dataclass
class EnvVarMetadata:
    """Metadata for environment variable"""
    env_var: str
    file_path: str
    original_size: int
    encoded_size: int
    sha256: str
    last_updated: str
    git_commit: str
    version: str
    priority: int
    category: str
    auto_sync: bool


class EnvVarConverter:
    """Convert and manage GitHub environment variables"""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.metadata_file = self.repo_root / ".github" / "scripts" / "env_var_metadata.json"
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, EnvVarMetadata]:
        """Load metadata from JSON file"""
        if not self.metadata_file.exists():
            return {}

        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
            return {
                k: EnvVarMetadata(**v) for k, v in data.items()
            }
        except Exception as e:
            print(f"⚠️  Warning: Could not load metadata: {e}")
            return {}

    def _save_metadata(self):
        """Save metadata to JSON file"""
        data = {
            k: asdict(v) for k, v in self.metadata.items()
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Metadata saved to {self.metadata_file}")

    def _get_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()[:8]
        except Exception:
            return "unknown"

    def _calculate_sha256(self, content: bytes) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content).hexdigest()

    def encode_file(self, file_path: Path) -> Tuple[str, EnvVarMetadata]:
        """
        Encode file to base64 and return encoded string with metadata.

        Args:
            file_path: Path to file to encode

        Returns:
            Tuple of (encoded_string, metadata)

        Raises:
            ValueError: If file is too large or doesn't exist
        """
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        # Read file
        with open(file_path, 'rb') as f:
            content = f.read()

        original_size = len(content)

        # Check size limit
        if original_size > MAX_ORIGINAL_SIZE:
            raise ValueError(
                f"File too large: {original_size:,} bytes "
                f"(max: {MAX_ORIGINAL_SIZE:,} bytes after base64 encoding)"
            )

        # Encode
        encoded = base64.b64encode(content).decode('ascii')
        encoded_size = len(encoded)

        if encoded_size > MAX_ENV_SIZE:
            raise ValueError(
                f"Encoded size exceeds limit: {encoded_size:,} bytes "
                f"(max: {MAX_ENV_SIZE:,} bytes)"
            )

        # Find config for this file
        config = self._find_config(str(file_path))
        if not config:
            raise ValueError(f"No configuration found for {file_path}")

        # Calculate hash
        sha256 = self._calculate_sha256(content)

        # Get version from git tag
        try:
            version_result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                capture_output=True,
                text=True
            )
            version = version_result.stdout.strip()
        except Exception:
            version = "v0.0.0"

        # Create metadata
        metadata = EnvVarMetadata(
            env_var=config["env_var"],
            file_path=str(file_path),
            original_size=original_size,
            encoded_size=encoded_size,
            sha256=sha256,
            last_updated=datetime.utcnow().isoformat(),
            git_commit=self._get_git_commit(),
            version=version,
            priority=config["priority"],
            category=config["category"],
            auto_sync=config["auto_sync"],
        )

        # Update metadata cache
        self.metadata[config["env_var"]] = metadata
        self._save_metadata()

        return encoded, metadata

    def _find_config(self, file_path: str) -> Optional[dict]:
        """Find configuration for file path"""
        for config in CANDIDATES_CONFIG:
            if file_path.endswith(config["path"]) or config["path"] in file_path:
                return config
        return None

    def verify_file(self, file_path: Path, env_var: str) -> Tuple[bool, str]:
        """
        Verify if file needs updating based on hash comparison.

        Args:
            file_path: Path to source file
            env_var: Environment variable name

        Returns:
            Tuple of (needs_update, reason)
        """
        # Check if we have metadata
        if env_var not in self.metadata:
            return True, "No metadata found (never synced)"

        # Check if file exists
        if not file_path.exists():
            return False, f"Source file not found: {file_path}"

        # Calculate current hash
        with open(file_path, 'rb') as f:
            current_content = f.read()
        current_hash = self._calculate_sha256(current_content)

        # Compare with stored hash
        stored_hash = self.metadata[env_var].sha256

        if current_hash != stored_hash:
            return True, "File content has changed (hash mismatch)"

        return False, "File is up to date"

    def list_candidates(self):
        """List all candidate files with status"""
        print("=" * 100)
        print("GITHUB ENVIRONMENT VARIABLE CANDIDATES")
        print("=" * 100)
        print()

        for i, config in enumerate(CANDIDATES_CONFIG, 1):
            file_path = self.repo_root / config["path"]
            env_var = config["env_var"]

            print(f"{i}. {config['env_var']}")
            print(f"   File: {config['path']}")
            print(f"   Priority: {config['priority']} ({'⭐' * config['priority']})")
            print(f"   Category: {config['category']}")
            print(f"   Auto-sync: {'✅ Yes' if config['auto_sync'] else '❌ Manual'}")
            print(f"   Description: {config['description']}")

            # Check file status
            if not file_path.exists():
                print(f"   Status: ❌ File not found")
            else:
                size = file_path.stat().st_size
                encoded_size = int(size * BASE64_OVERHEAD)
                pct_used = (encoded_size / MAX_ENV_SIZE) * 100

                print(f"   Size: {size:,} bytes → {encoded_size:,} bytes (base64)")
                print(f"   Env usage: {pct_used:.1f}% of 48KB")

                if encoded_size > MAX_ENV_SIZE:
                    print(f"   Fits: ❌ TOO LARGE (exceeds 48KB limit)")
                else:
                    print(f"   Fits: ✅ YES ({MAX_ENV_SIZE - encoded_size:,} bytes headroom)")

                # Check if synced
                if env_var in self.metadata:
                    needs_update, reason = self.verify_file(file_path, env_var)
                    if needs_update:
                        print(f"   Sync status: ⚠️  OUT OF SYNC - {reason}")
                    else:
                        meta = self.metadata[env_var]
                        print(f"   Sync status: ✅ UP TO DATE")
                        print(f"   Last synced: {meta.last_updated}")
                        print(f"   Git commit: {meta.git_commit}")
                else:
                    print(f"   Sync status: 🔄 NEVER SYNCED")

            print()

    def sync_all(self, environment: str = "production", dry_run: bool = False):
        """
        Sync all auto-sync enabled files to GitHub environment.

        Args:
            environment: GitHub environment name
            dry_run: If True, only show what would be synced
        """
        print(f"{'🔍 DRY RUN: ' if dry_run else ''}Syncing to environment: {environment}")
        print("=" * 100)
        print()

        synced_count = 0
        skipped_count = 0
        failed_count = 0

        for config in CANDIDATES_CONFIG:
            file_path = self.repo_root / config["path"]
            env_var = config["env_var"]

            print(f"Processing: {env_var}")

            # Check if auto-sync enabled
            if not config["auto_sync"]:
                print(f"  ⏭️  Skipped (manual sync required)")
                skipped_count += 1
                print()
                continue

            # Check if file exists
            if not file_path.exists():
                print(f"  ❌ Failed (file not found: {file_path})")
                failed_count += 1
                print()
                continue

            # Check if needs update
            needs_update, reason = self.verify_file(file_path, env_var)

            if not needs_update:
                print(f"  ✅ Up to date ({reason})")
                skipped_count += 1
                print()
                continue

            print(f"  🔄 Needs update: {reason}")

            try:
                # Encode file
                encoded, metadata = self.encode_file(file_path)

                print(f"  📦 Encoded: {metadata.original_size:,} → {metadata.encoded_size:,} bytes")
                print(f"  📊 Usage: {(metadata.encoded_size/MAX_ENV_SIZE)*100:.1f}% of 48KB")

                if not dry_run:
                    # Update GitHub environment variable
                    self._update_github_env_var(environment, env_var, encoded)
                    print(f"  ✅ Synced to GitHub")
                    synced_count += 1
                else:
                    print(f"  🔍 Would sync to GitHub (dry run)")
                    synced_count += 1

            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed_count += 1

            print()

        # Summary
        print("=" * 100)
        print("SYNC SUMMARY")
        print("=" * 100)
        print(f"Synced: {synced_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Failed: {failed_count}")
        print()

        if dry_run:
            print("🔍 This was a dry run. Use --no-dry-run to actually sync.")

    def _update_github_env_var(self, environment: str, var_name: str, value: str):
        """
        Update GitHub environment variable using gh CLI.

        Args:
            environment: Environment name (e.g., 'production')
            var_name: Variable name
            value: Variable value (base64 encoded)
        """
        # Get repo info
        repo_result = subprocess.run(
            ['gh', 'repo', 'view', '--json', 'nameWithOwner', '--jq', '.nameWithOwner'],
            capture_output=True,
            text=True,
            check=True
        )
        repo = repo_result.stdout.strip()

        # Update variable using gh API
        api_url = f"repos/{repo}/environments/{environment}/variables"

        # Check if variable exists
        try:
            subprocess.run(
                ['gh', 'api', f"{api_url}/{var_name}"],
                capture_output=True,
                text=True,
                check=True
            )
            # Variable exists, update it
            method = 'PATCH'
            url = f"{api_url}/{var_name}"
        except subprocess.CalledProcessError:
            # Variable doesn't exist, create it
            method = 'POST'
            url = api_url

        # Update/create variable
        subprocess.run(
            [
                'gh', 'api',
                url,
                '-X', method,
                '-F', f'name={var_name}',
                '-F', f'value={value}'
            ],
            check=True,
            capture_output=True
        )

    def verify_all(self):
        """Verify all files and report status"""
        print("=" * 100)
        print("VERIFICATION REPORT")
        print("=" * 100)
        print()

        needs_sync = []
        up_to_date = []
        not_synced = []

        for config in CANDIDATES_CONFIG:
            file_path = self.repo_root / config["path"]
            env_var = config["env_var"]

            if not file_path.exists():
                continue

            if env_var not in self.metadata:
                not_synced.append((env_var, config["path"]))
            else:
                needs_update, reason = self.verify_file(file_path, env_var)
                if needs_update:
                    needs_sync.append((env_var, config["path"], reason))
                else:
                    up_to_date.append((env_var, config["path"]))

        # Report
        print(f"📊 SUMMARY:")
        print(f"  Up to date: {len(up_to_date)}")
        print(f"  Needs sync: {len(needs_sync)}")
        print(f"  Never synced: {len(not_synced)}")
        print()

        if up_to_date:
            print("✅ UP TO DATE:")
            for env_var, path in up_to_date:
                meta = self.metadata[env_var]
                print(f"  • {env_var}")
                print(f"    File: {path}")
                print(f"    Last synced: {meta.last_updated}")
                print(f"    Git commit: {meta.git_commit}")
            print()

        if needs_sync:
            print("⚠️  NEEDS SYNC:")
            for env_var, path, reason in needs_sync:
                print(f"  • {env_var}")
                print(f"    File: {path}")
                print(f"    Reason: {reason}")
            print()

        if not_synced:
            print("🔄 NEVER SYNCED:")
            for env_var, path in not_synced:
                print(f"  • {env_var}")
                print(f"    File: {path}")
            print()

        # Return exit code
        return 0 if not needs_sync and not not_synced else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GitHub Environment Variable Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all candidates with status
  %(prog)s --mode list-candidates

  # Encode a single file
  %(prog)s --mode encode --file src/cognitive_brain/quantum/ghz_states.py

  # Sync all auto-sync files (dry run)
  %(prog)s --mode sync --environment production --dry-run

  # Sync all auto-sync files (actual)
  %(prog)s --mode sync --environment production --no-dry-run

  # Verify all files
  %(prog)s --mode verify --all
        """
    )

    parser.add_argument(
        '--mode',
        choices=['encode', 'sync', 'verify', 'list-candidates'],
        required=True,
        help='Operation mode'
    )

    parser.add_argument(
        '--file',
        type=Path,
        help='File to encode (for encode mode)'
    )

    parser.add_argument(
        '--environment',
        default='production',
        help='GitHub environment name (default: production)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry run mode (default: True)'
    )

    parser.add_argument(
        '--no-dry-run',
        action='store_false',
        dest='dry_run',
        help='Disable dry run (actually sync)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Verify all files (for verify mode)'
    )

    args = parser.parse_args()

    # Initialize converter
    converter = EnvVarConverter()

    try:
        if args.mode == 'list-candidates':
            converter.list_candidates()

        elif args.mode == 'encode':
            if not args.file:
                print("❌ Error: --file required for encode mode")
                sys.exit(1)

            print(f"Encoding: {args.file}")
            encoded, metadata = converter.encode_file(args.file)

            print()
            print("=" * 100)
            print("ENCODING COMPLETE")
            print("=" * 100)
            print(f"Environment Variable: {metadata.env_var}")
            print(f"Original Size: {metadata.original_size:,} bytes")
            print(f"Encoded Size: {metadata.encoded_size:,} bytes")
            print(f"Usage: {(metadata.encoded_size/MAX_ENV_SIZE)*100:.1f}% of 48KB")
            print(f"SHA256: {metadata.sha256}")
            print(f"Git Commit: {metadata.git_commit}")
            print()
            print("Encoded value (copy to GitHub):")
            print("-" * 100)
            print(encoded)
            print("-" * 100)

        elif args.mode == 'sync':
            converter.sync_all(args.environment, dry_run=args.dry_run)

        elif args.mode == 'verify':
            if not args.all:
                print("❌ Error: --all required for verify mode")
                sys.exit(1)

            exit_code = converter.verify_all()
            sys.exit(exit_code)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
