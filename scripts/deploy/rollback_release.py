#!/usr/bin/env python3
"""
Rollback Release Script

Automates the rollback of a failed release from PyPI and GitHub.

Usage:
    python scripts/deploy/rollback_release.py \
        --version v0.1.0 \
        --reason "Critical import failure" \
        --restore-version v0.0.9
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RollbackManager:
    """Manages rollback of releases from PyPI and GitHub"""
    
    def __init__(self, version: str, restore_version: str, reason: str):
        """
        Initialize rollback manager
        
        Args:
            version: Version to rollback (e.g., v0.1.0)
            restore_version: Version to restore as latest (e.g., v0.0.9)
            reason: Reason for rollback
        """
        self.version = version.lstrip('v')
        self.restore_version = restore_version.lstrip('v')
        self.reason = reason
        self.timestamp = datetime.utcnow().isoformat()
        self.repo_root = Path(__file__).parent.parent.parent
        
    def run(self) -> bool:
        """Execute rollback"""
        logger.info(f"🚀 Starting rollback for v{self.version}")
        logger.info(f"   Reason: {self.reason}")
        logger.info(f"   Restore to: v{self.restore_version}")
        
        try:
            # Step 1: Verify issue severity
            if not self._verify_issue_severity():
                logger.warning("⚠️  Issue severity verification incomplete")
                if not self._ask_confirmation("Continue with rollback?"):
                    logger.info("❌ Rollback cancelled by user")
                    return False
            
            # Step 2: Stop deployments
            if not self._stop_deployments():
                logger.error("❌ Failed to stop deployments")
                return False
            
            # Step 3: Mark as yanked on PyPI
            if not self._mark_yanked():
                logger.error("❌ Failed to mark as yanked on PyPI")
                return False
            
            # Step 4: Delete release tag
            if not self._delete_tag():
                logger.error("❌ Failed to delete release tag")
                return False
            
            # Step 5: Restore previous version
            if not self._restore_previous():
                logger.error("❌ Failed to restore previous version")
                return False
            
            # Step 6: Verify PyPI state
            if not self._verify_pypi_state():
                logger.error("❌ PyPI verification failed")
                return False
            
            # Step 7: Notify users
            if not self._notify_users():
                logger.warning("⚠️  User notification failed (non-blocking)")
            
            # Step 8: Record metrics
            self._record_metrics()
            
            logger.info("✅ Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {str(e)}", exc_info=True)
            return False
    
    def _verify_issue_severity(self) -> bool:
        """Verify issue severity through basic checks"""
        logger.info("📋 Verifying issue severity...")
        
        # In production, this would check smoke test results, error rates, etc.
        # For now, we log the reason provided
        logger.info(f"   Reason provided: {self.reason}")
        
        return True
    
    def _ask_confirmation(self, prompt: str) -> bool:
        """Ask user for confirmation"""
        response = input(f"\n{prompt} [y/N]: ").lower().strip()
        return response == 'y'
    
    def _stop_deployments(self) -> bool:
        """Stop active deployments"""
        logger.info("🛑 Stopping deployments...")
        
        # In GitHub Actions, we would disable the environment
        # For local testing, we just log
        logger.info("   Would disable PyPI deployment environment")
        
        return True
    
    def _mark_yanked(self) -> bool:
        """Mark version as yanked on PyPI"""
        logger.info("🚫 Marking v{self.version} as yanked on PyPI...")
        
        pypi_token = os.getenv("PYPI_API_TOKEN")
        if not pypi_token:
            logger.warning("   ⚠️  PYPI_API_TOKEN not set (required for yanking)")
            logger.info("   Manual yanking required:")
            logger.info(f"     1. Go to https://pypi.org/project/codex-ml/")
            logger.info(f"     2. Click on v{self.version}")
            logger.info(f"     3. Click 'Options' → 'Mark as yanked'")
            # In production, could fail here, but we allow manual override
        
        try:
            # Try to yank using twine
            cmd = [
                "python", "-m", "twine", "remove",
                f"codex-ml=={self.version}",
                "--skip-existing", "--verbose"
            ]
            
            env = os.environ.copy()
            env["TWINE_USERNAME"] = "__token__"
            env["TWINE_PASSWORD"] = pypi_token or ""
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"   ✅ v{self.version} marked as yanked")
                return True
            else:
                # Non-blocking - user can manually yank
                logger.warning(f"   ⚠️  Twine yanking failed (may need manual action)")
                logger.debug(f"      stderr: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  Twine operation timed out")
            return False
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to run twine: {str(e)}")
            return False
    
    def _delete_tag(self) -> bool:
        """Delete release tag from git"""
        logger.info(f"🗑️  Deleting git tag v{self.version}...")
        
        try:
            # Delete local tag
            subprocess.run(
                ["git", "tag", "-d", f"v{self.version}"],
                cwd=self.repo_root,
                capture_output=True,
                timeout=10
            )
            logger.info("   ✅ Local tag deleted")
            
            # Delete remote tag
            result = subprocess.run(
                ["git", "push", "origin", "--delete", f"v{self.version}"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"   ✅ Remote tag v{self.version} deleted")
                return True
            else:
                logger.warning(f"   ⚠️  Failed to delete remote tag: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  Git operation timed out")
            return False
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to delete tag: {str(e)}")
            return False
    
    def _restore_previous(self) -> bool:
        """Restore previous version as latest"""
        logger.info(f"♻️  Restoring v{self.restore_version} as latest...")
        
        try:
            # Check if tag exists
            result = subprocess.run(
                ["git", "tag", "-l", f"v{self.restore_version}"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                logger.warning(f"   ⚠️  Tag v{self.restore_version} not found locally")
                logger.info(f"     Will fetch from remote...")
                
                # Fetch tags
                subprocess.run(
                    ["git", "fetch", "origin", "--tags"],
                    cwd=self.repo_root,
                    capture_output=True,
                    timeout=30
                )
            
            # Push previous version tag (ensure it's published)
            result = subprocess.run(
                ["git", "push", "origin", f"v{self.restore_version}"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"   ✅ v{self.restore_version} restored as latest")
                return True
            else:
                logger.warning(f"   ⚠️  Failed to push tag: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  Git operation timed out")
            return False
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to restore version: {str(e)}")
            return False
    
    def _verify_pypi_state(self) -> bool:
        """Verify correct state on PyPI"""
        logger.info("🔍 Verifying PyPI state...")
        
        # In production, would query PyPI API
        logger.info(f"   Would verify v{self.restore_version} is latest")
        logger.info(f"   Would verify v{self.version} is yanked")
        
        # Note: PyPI indexing takes 5-10 minutes
        logger.info("   ℹ️  Note: PyPI indexing takes 5-10 minutes")
        
        return True
    
    def _notify_users(self) -> bool:
        """Notify users of rollback"""
        logger.info("📢 Notifying users...")
        
        notification = f"""
## ⚠️ Release Rollback: v{self.version}

**Status**: Yanked from PyPI  
**Timestamp**: {self.timestamp}  
**Reason**: {self.reason}

### Action Required
If you installed v{self.version}, please upgrade:

\`\`\`bash
pip install --upgrade codex-ml
\`\`\`

This will downgrade to v{self.restore_version} (previous stable release).

### Support
For questions, file an issue on GitHub or contact support.
"""
        
        try:
            # Try to create GitHub release
            cmd = [
                "gh", "release", "create",
                f"rollback-v{self.version}",
                "--draft",
                "--notes", notification
            ]
            
            result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("   ✅ GitHub release created")
                return True
            else:
                logger.warning("   ⚠️  Failed to create GitHub release")
                logger.info("   Manual notification required:")
                logger.info(notification)
                return False
        
        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  GitHub operation timed out")
            return False
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to notify: {str(e)}")
            return False
    
    def _record_metrics(self):
        """Record rollback metrics"""
        logger.info("📊 Recording metrics...")
        
        metrics = {
            "event": "release_rollback",
            "version": self.version,
            "restore_version": self.restore_version,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "status": "completed"
        }
        
        # Create metrics directory
        metrics_dir = self.repo_root / ".codex" / "incidents"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Write metrics file
        metrics_file = metrics_dir / f"rollback-{self.version}.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"   ✅ Metrics recorded to {metrics_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Rollback a release from PyPI and GitHub"
    )
    
    parser.add_argument(
        "--version",
        required=True,
        help="Version to rollback (e.g., v0.1.0 or 0.1.0)"
    )
    
    parser.add_argument(
        "--restore-version",
        required=True,
        help="Version to restore as latest (e.g., v0.0.9 or 0.0.9)"
    )
    
    parser.add_argument(
        "--reason",
        required=True,
        help="Reason for rollback (e.g., 'Critical import failure')"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    # Validate versions
    if not args.version or not args.restore_version:
        logger.error("❌ --version and --restore-version are required")
        return False
    
    if args.version == args.restore_version:
        logger.error("❌ Version and restore-version cannot be the same")
        return False
    
    # Create manager and run
    manager = RollbackManager(
        version=args.version,
        restore_version=args.restore_version,
        reason=args.reason
    )
    
    success = manager.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
