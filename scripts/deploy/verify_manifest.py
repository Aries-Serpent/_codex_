#!/usr/bin/env python3
"""
Verify hash integrity of release manifests and wheels.

Usage:
    python scripts/deploy/verify_manifest.py --manifest .codex/manifests/v0.1.0_RELEASE_MANIFEST_CORE.json --wheelhouse ./wheelhouse_core/ --master-key $CODEX_MASTER_KEY

Validation:
    1. Load manifest JSON
    2. Verify HMAC-SHA256 signature using master key
    3. Hash all wheels in wheelhouse directory
    4. Compare against manifest hashes
    5. Fail with clear error on any mismatch
    6. Log tampering attempts to audit log
"""

import json
import hashlib
import hmac
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ManifestVerifier:
    """Verifies integrity of release manifests and wheels."""

    def __init__(self, manifest_path: str, wheelhouse_dir: str = None, master_key: str = None, audit_log_path: str = None):
        """
        Initialize manifest verifier.

        Args:
            manifest_path: Path to manifest JSON file
            wheelhouse_dir: Directory containing wheels to verify
            master_key: HMAC-SHA256 master key (env var CODEX_MASTER_KEY if not provided)
            audit_log_path: Path to audit log file (default: .codex/security/manifest_audit.log)
        """
        self.manifest_path = Path(manifest_path)
        self.wheelhouse_dir = Path(wheelhouse_dir) if wheelhouse_dir else None
        self.master_key = (master_key or os.environ.get("CODEX_MASTER_KEY") or "").strip()
        self.audit_log_path = Path(audit_log_path or ".codex/security/manifest_audit.log")
        
        self.manifest = None
        self.errors = []
        self.warnings = []

    def log_audit(self, event: str, severity: str = "INFO", details: str = ""):
        """Log verification event to audit log."""
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.audit_log_path, "a") as f:
            timestamp = datetime.utcnow().isoformat() + "Z"
            f.write(f"{timestamp} | {severity:8} | {event:40} | {details}\n")

    def load_manifest(self) -> bool:
        """
        Load and parse manifest JSON.
        
        Returns:
            True if successfully loaded, False otherwise
        """
        if not self.manifest_path.exists():
            self.errors.append(f"Manifest file not found: {self.manifest_path}")
            self.log_audit("MANIFEST_NOT_FOUND", "ERROR", str(self.manifest_path))
            return False
        
        try:
            with open(self.manifest_path, "r") as f:
                self.manifest = json.load(f)
            logger.info(f"✓ Loaded manifest: {self.manifest_path}")
            self.log_audit("MANIFEST_LOADED", "INFO", f"version={self.manifest.get('release_version')}")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in manifest: {e}")
            self.log_audit("MANIFEST_INVALID_JSON", "ERROR", str(e))
            return False
        except Exception as e:
            self.errors.append(f"Failed to load manifest: {e}")
            self.log_audit("MANIFEST_LOAD_ERROR", "ERROR", str(e))
            return False

    def verify_signature(self) -> bool:
        """
        Verify HMAC-SHA256 signature of manifest.

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.manifest:
            self.errors.append("Manifest not loaded")
            return False

        stored_signature = (self.manifest.get("signature") or "").strip()
        if not stored_signature:
            error_msg = "Manifest signature missing; unsigned release manifests are not allowed"
            self.errors.append(error_msg)
            self.log_audit("SIGNATURE_MISSING", "ERROR", error_msg)
            logger.error(f"✗ {error_msg}")
            return False

        if not self.master_key:
            error_msg = "Master key missing; set CODEX_MASTER_KEY or pass --master-key to verify manifests"
            self.errors.append(error_msg)
            self.log_audit("SIGNATURE_KEY_MISSING", "ERROR", error_msg)
            logger.error(f"✗ {error_msg}")
            return False

        # Create a copy of manifest without signature for verification
        manifest_copy = dict(self.manifest)
        manifest_copy["signature"] = ""

        # Compute expected signature
        manifest_json = json.dumps(manifest_copy, sort_keys=True, separators=(",", ":"))
        expected_signature = hmac.new(
            self.master_key.encode(),
            manifest_json.encode(),
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(stored_signature, expected_signature):
            logger.info("✓ Manifest signature valid")
            self.log_audit("SIGNATURE_VALID", "INFO", f"signature={stored_signature[:16]}...")
            return True

        error_msg = (
            f"Signature mismatch! Expected {expected_signature[:16]}..., got {stored_signature[:16]}..."
        )
        self.errors.append(error_msg)
        self.log_audit("SIGNATURE_INVALID", "ERROR", error_msg)
        logger.error(f"✗ {error_msg}")
        return False

    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def discover_wheels(self) -> List[Tuple[Path, str]]:
        """
        Discover all wheel files in wheelhouse directory.
        
        Returns:
            List of (path, filename) tuples
        """
        if not self.wheelhouse_dir or not self.wheelhouse_dir.exists():
            logger.warning(f"Wheelhouse directory not found: {self.wheelhouse_dir}")
            return []
        
        wheels = []
        for wheel_file in self.wheelhouse_dir.glob("*.whl"):
            wheels.append((wheel_file, wheel_file.name))
        
        return sorted(wheels)

    def _manifest_wheels(self) -> dict[str, dict]:
        """Normalize supported manifest wheel schemas to {name: {sha256: ...}}."""
        raw_wheels = self.manifest.get("wheels", {})
        if isinstance(raw_wheels, dict):
            return {str(name): info for name, info in raw_wheels.items() if isinstance(info, dict)}
        if isinstance(raw_wheels, list):
            normalized: dict[str, dict] = {}
            for item in raw_wheels:
                if not isinstance(item, dict):
                    continue
                name = item.get("name") or item.get("file_name")
                if not name:
                    continue
                normalized[str(name)] = {
                    "sha256": item.get("sha256") or item.get("hash") or "",
                    **item,
                }
            return normalized
        return {}

    def verify_wheel_hashes(self) -> bool:
        """
        Verify SHA256 hashes of all wheels against manifest.
        
        Returns:
            True if all wheels match manifest hashes, False otherwise
        """
        if not self.manifest:
            self.errors.append("Manifest not loaded")
            return False
        
        if not self.wheelhouse_dir:
            logger.warning("No wheelhouse directory specified, skipping hash verification")
            self.warnings.append("Wheelhouse hash verification skipped")
            return True
        
        wheels = self.discover_wheels()
        manifest_wheels = self._manifest_wheels()
        manifest_hashes = {
            name: info.get("sha256") or info.get("hash")
            for name, info in manifest_wheels.items()
            if info.get("sha256") or info.get("hash")
        }
        
        if not wheels and not manifest_hashes:
            logger.info("✓ No wheels to verify")
            return True
        
        all_valid = True
        
        # Check each wheel in wheelhouse
        for wheel_path, wheel_name in wheels:
            if wheel_name not in manifest_hashes:
                error_msg = f"Wheel {wheel_name} not in manifest"
                self.errors.append(error_msg)
                self.log_audit("WHEEL_NOT_IN_MANIFEST", "ERROR", wheel_name)
                logger.error(f"✗ {error_msg}")
                all_valid = False
                continue
            
            # Calculate actual hash
            actual_hash = self.calculate_sha256(wheel_path)
            expected_hash = manifest_hashes[wheel_name]
            
            if actual_hash == expected_hash:
                logger.info(f"✓ {wheel_name}: hash valid")
                self.log_audit("WHEEL_HASH_VALID", "INFO", wheel_name)
            else:
                error_msg = f"Wheel hash mismatch for {wheel_name}"
                self.errors.append(f"{error_msg}: expected {expected_hash[:16]}..., got {actual_hash[:16]}...")
                self.log_audit("WHEEL_HASH_MISMATCH", "ERROR", wheel_name)
                logger.error(f"✗ {error_msg}")
                all_valid = False
        
        # Check for manifest wheels not in wheelhouse
        wheelhouse_names = {w[1] for w in wheels}
        for manifest_wheel_name in manifest_hashes.keys():
            if manifest_wheel_name not in wheelhouse_names:
                warning_msg = f"Manifest wheel {manifest_wheel_name} not found in wheelhouse"
                self.warnings.append(warning_msg)
                self.log_audit("WHEEL_MISSING_FROM_WHEELHOUSE", "WARNING", manifest_wheel_name)
                logger.warning(f"⚠ {warning_msg}")
        
        return all_valid

    def verify(self) -> bool:
        """
        Perform complete verification.
        
        Returns:
            True if all verifications pass, False otherwise
        """
        logger.info(f"Starting verification of {self.manifest_path}")
        
        # Step 1: Load manifest
        if not self.load_manifest():
            return False
        
        # Step 2: Verify signature
        if not self.verify_signature():
            return False
        
        # Step 3: Verify wheel hashes
        if not self.verify_wheel_hashes():
            return False
        
        return True

    def print_report(self):
        """Print verification report."""
        print("\n" + "=" * 70)
        print("MANIFEST VERIFICATION REPORT")
        print("=" * 70)
        
        if self.manifest:
            print(f"\nManifest:        {self.manifest_path}")
            print(f"Release Version: {self.manifest.get('release_version')}")
            print(f"Timestamp:       {self.manifest.get('timestamp')}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        else:
            print("\n✅ No errors detected")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Verify hash integrity of release manifests and wheels"
    )
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON file")
    parser.add_argument("--wheelhouse", help="Directory containing wheels to verify")
    parser.add_argument("--master-key", help="HMAC-SHA256 master key (uses CODEX_MASTER_KEY env var if not provided)")
    parser.add_argument("--audit-log", help="Path to audit log file")
    parser.add_argument("--strict", action="store_true", help="Fail on any warning")
    
    args = parser.parse_args()
    
    verifier = ManifestVerifier(
        manifest_path=args.manifest,
        wheelhouse_dir=args.wheelhouse,
        master_key=args.master_key,
        audit_log_path=args.audit_log,
    )
    
    success = verifier.verify()
    verifier.print_report()
    
    if success:
        print("\n✅ Verification successful!")
        return 0
    else:
        print("\n❌ Verification failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
