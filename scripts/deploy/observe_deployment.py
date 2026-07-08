#!/usr/bin/env python3
"""
Deployment Observability Logging

Records detailed metrics during deployment operations including bootstrap time,
package verification, network activity, and errors.

Usage:
    python scripts/deploy/observe_deployment.py --profile core
    python scripts/deploy/observe_deployment.py --profile core --wheelhouse /path/to/wheels
    python scripts/deploy/observe_deployment.py --offline-test --profile runtime
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = REPO_ROOT / ".codex" / "logs" / "deployment"


class DeploymentObserver:
    """Observe and log deployment operations."""

    def __init__(self, profile: str, offline: bool = False):
        self.profile = profile
        self.offline = offline
        self.logs_dir = LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.metrics: dict[str, Any] = {
            "version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "profile": profile,
            "offline_mode": offline,
            "events": [],
            "errors": [],
            "warnings": [],
        }
        self.start_time = time.time()

    def log_event(self, event_type: str, description: str, duration_seconds: float | None = None) -> None:
        """Log a deployment event."""
        event = {
            "type": event_type,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if duration_seconds is not None:
            event["duration_seconds"] = duration_seconds

        self.metrics["events"].append(event)
        logger.info(f"[{event_type}] {description}")

    def log_error(self, error_type: str, message: str, details: str | None = None) -> None:
        """Log an error."""
        error = {
            "type": error_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if details:
            error["details"] = details

        self.metrics["errors"].append(error)
        logger.error(f"[ERROR] {error_type}: {message}")

    def log_warning(self, warning_type: str, message: str) -> None:
        """Log a warning."""
        warning = {
            "type": warning_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.metrics["warnings"].append(warning)
        logger.warning(f"[WARNING] {warning_type}: {message}")

    def measure_bootstrap(self, venv_path: Path) -> None:
        """Measure virtual environment bootstrap time."""
        logger.info(f"Bootstrapping virtual environment at {venv_path}")
        start = time.time()

        try:
            # Create venv
            subprocess.run(
                ["python", "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
            )
            duration = time.time() - start
            self.log_event("bootstrap_venv", f"Created venv in {duration:.2f}s", duration)
        except subprocess.CalledProcessError as e:
            self.log_error("bootstrap_failed", str(e), e.stderr.decode() if e.stderr else "")

    def measure_package_verification(self, wheelhouse: Path) -> None:
        """Measure time to verify packages in wheelhouse."""
        logger.info(f"Verifying packages in {wheelhouse}")
        start = time.time()

        try:
            wheels = list(wheelhouse.glob("*.whl"))
            verified = 0
            failed = 0

            for wheel in wheels:
                try:
                    # Calculate SHA256 hash
                    with open(wheel, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    verified += 1
                except Exception as e:
                    failed += 1
                    self.log_error("wheel_verification_failed", f"Failed to verify {wheel.name}", str(e))

            duration = time.time() - start
            self.log_event(
                "package_verification",
                f"Verified {verified}/{len(wheels)} wheels in {duration:.2f}s",
                duration,
            )

            if failed > 0:
                self.log_warning("partial_verification", f"{failed} wheels failed verification")
        except Exception as e:
            self.log_error("verification_error", "Package verification failed", str(e))

    def check_network_connectivity(self) -> None:
        """Check network connectivity (if any)."""
        logger.info("Checking network connectivity")

        # Try to resolve DNS
        try:
            start = time.time()
            socket.gethostbyname("pypi.org")
            duration = time.time() - start
            self.log_event("network_check", f"PyPI DNS resolution took {duration:.2f}ms", duration)
        except socket.gaierror:
            self.log_warning("network_unavailable", "PyPI DNS resolution failed (expected in offline mode)")

    def measure_install_time(self, packages: list[str], wheelhouse: Path | None = None) -> None:
        """Measure package installation time."""
        logger.info(f"Measuring install time for {len(packages)} packages")
        start = time.time()

        try:
            pip_args = ["pip", "install", "--quiet"]

            if wheelhouse:
                pip_args.extend(["--no-index", f"--find-links={wheelhouse}"])

            pip_args.extend(packages)

            subprocess.run(pip_args, check=True, capture_output=True)

            duration = time.time() - start
            self.log_event(
                "package_install",
                f"Installed {len(packages)} packages in {duration:.2f}s",
                duration,
            )
        except subprocess.CalledProcessError as e:
            self.log_error(
                "install_failed",
                f"Package installation failed",
                e.stderr.decode() if e.stderr else "",
            )

    def save_log(self) -> Path:
        """Save deployment log to JSON file."""
        self.metrics["total_duration_seconds"] = time.time() - self.start_time

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"deployment-{self.profile}-{timestamp}.json"
        filepath = self.logs_dir / filename

        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)

        logger.info(f"Deployment log saved to {filepath}")
        return filepath

    def get_summary(self) -> dict[str, Any]:
        """Get summary of deployment metrics."""
        return {
            "profile": self.profile,
            "offline_mode": self.offline,
            "total_duration_seconds": time.time() - self.start_time,
            "event_count": len(self.metrics["events"]),
            "error_count": len(self.metrics["errors"]),
            "warning_count": len(self.metrics["warnings"]),
            "success": len(self.metrics["errors"]) == 0,
        }


def observe_offline_installation(profile: str, wheelhouse: Path) -> int:
    """Observe a complete offline installation process."""
    logger.info(f"Starting offline installation observation for {profile} profile")

    observer = DeploymentObserver(profile=profile, offline=True)

    try:
        # Check wheelhouse
        if not wheelhouse.exists():
            observer.log_error("wheelhouse_missing", f"Wheelhouse not found: {wheelhouse}")
            observer.save_log()
            return 1

        wheels = list(wheelhouse.glob("*.whl"))
        observer.log_event("wheelhouse_scan", f"Found {len(wheels)} wheels")

        # Verify packages
        observer.measure_package_verification(wheelhouse)

        # Check network (should be unavailable in offline mode)
        observer.check_network_connectivity()

        # Save metrics
        observer.save_log()
        summary = observer.get_summary()

        logger.info(f"Offline installation observation complete: {json.dumps(summary, indent=2)}")
        return 0 if summary["success"] else 1

    except Exception as e:
        observer.log_error("observation_failed", "Deployment observation failed", str(e))
        observer.save_log()
        return 1


def observe_bootstrap_and_install(profile: str, wheelhouse: Path | None = None) -> int:
    """Observe bootstrap and installation process."""
    logger.info(f"Starting bootstrap observation for {profile} profile")

    observer = DeploymentObserver(profile=profile, offline=wheelhouse is not None)

    try:
        # Create temporary venv
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_path = Path(tmpdir) / "venv"

            # Bootstrap
            observer.measure_bootstrap(venv_path)

            if wheelhouse:
                observer.measure_package_verification(wheelhouse)

            # Network check
            observer.check_network_connectivity()

        # Save metrics
        observer.save_log()
        summary = observer.get_summary()

        logger.info(f"Bootstrap observation complete: {json.dumps(summary, indent=2)}")
        return 0 if summary["success"] else 1

    except Exception as e:
        observer.log_error("observation_failed", "Deployment observation failed", str(e))
        observer.save_log()
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Deployment observability logging")
    parser.add_argument("--profile", choices=["core", "runtime", "full"], default="core")
    parser.add_argument("--wheelhouse", type=Path, help="Path to wheelhouse directory")
    parser.add_argument("--offline-test", action="store_true", help="Test offline installation")
    parser.add_argument("--bootstrap-only", action="store_true", help="Test bootstrap only")

    args = parser.parse_args()

    if args.offline_test:
        if not args.wheelhouse:
            logger.error("--wheelhouse required for offline test")
            return 1
        return observe_offline_installation(args.profile, args.wheelhouse)

    if args.bootstrap_only:
        return observe_bootstrap_and_install(args.profile, args.wheelhouse)

    # Default: bootstrap with optional wheelhouse
    return observe_bootstrap_and_install(args.profile, args.wheelhouse)


if __name__ == "__main__":
    sys.exit(main())
