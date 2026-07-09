"""
Telemetry Metrics Collection Module

Minimal stdlib-only implementation for collecting build, deployment, and runtime metrics.

Usage:
    python -m codex.telemetry.metrics collect-build --duration 120 --profile core
    python -m codex.telemetry.metrics collect-sbom --version 0.1.0 --profiles core runtime full
    python -m codex.telemetry.metrics get-latest --phase build
"""

from __future__ import annotations

import json
import logging
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
METRICS_DIR = REPO_ROOT / ".codex" / "metrics"


class MetricsCollector:
    """Collect and store telemetry metrics."""

    def __init__(self, metrics_dir: Path | None = None):
        self.metrics_dir = metrics_dir or METRICS_DIR
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics: dict[str, Any] = {
            "version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def add_build_metrics(
        self,
        duration_seconds: float,
        profile: str,
        wheel_sizes: dict[str, int] | None = None,
        dependency_count: int = 0,
    ) -> None:
        """Add build phase metrics."""
        self.metrics["build"] = {
            "duration_seconds": duration_seconds,
            "profile": profile,
            "wheel_sizes": wheel_sizes or {},
            "dependency_count": dependency_count,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "platform": platform.system(),
            "architecture": platform.machine(),
        }

    def add_sbom_metrics(
        self,
        version: str,
        profiles: list[str],
        components: int,
        signatures_valid: bool,
        generation_time_seconds: float,
    ) -> None:
        """Add SBOM generation metrics."""
        self.metrics["sbom"] = {
            "generated": True,
            "version": version,
            "profiles": profiles,
            "components": components,
            "signatures_valid": signatures_valid,
            "generation_time_seconds": generation_time_seconds,
        }

    def add_release_metrics(
        self,
        tag: str,
        artifacts_uploaded: int,
        sbom_attached: bool,
        wheel_hashes_verified: bool,
    ) -> None:
        """Add release metrics."""
        self.metrics["release"] = {
            "tag": tag,
            "artifacts_uploaded": artifacts_uploaded,
            "sbom_attached": sbom_attached,
            "wheel_hashes_verified": wheel_hashes_verified,
        }

    def add_offline_install_metrics(
        self,
        profile: str,
        duration_seconds: float,
        packages_installed: int,
        verification_time_seconds: float,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        """Add offline installation test metrics."""
        self.metrics["offline_install"] = {
            "profile": profile,
            "duration_seconds": duration_seconds,
            "packages_installed": packages_installed,
            "verification_time_seconds": verification_time_seconds,
            "errors": errors or [],
            "warnings": warnings or [],
        }

    def add_error(self, error_type: str, message: str) -> None:
        """Record an error."""
        if "errors" not in self.metrics:
            self.metrics["errors"] = {}
        if error_type not in self.metrics["errors"]:
            self.metrics["errors"][error_type] = []
        self.metrics["errors"][error_type].append(message)

    def add_warning(self, warning_type: str, message: str) -> None:
        """Record a warning."""
        if "warnings" not in self.metrics:
            self.metrics["warnings"] = {}
        if warning_type not in self.metrics["warnings"]:
            self.metrics["warnings"][warning_type] = []
        self.metrics["warnings"][warning_type].append(message)

    def save(self, filename: str | None = None) -> Path:
        """Save metrics to JSON file."""
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            phase = "unknown"
            if "build" in self.metrics:
                phase = "build"
            elif "sbom" in self.metrics:
                phase = "sbom"
            elif "release" in self.metrics:
                phase = "release"
            filename = f"{phase}-{timestamp}.json"

        filepath = self.metrics_dir / filename
        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)

        logger.info(f"Saved metrics to {filepath}")
        return filepath

    def to_dict(self) -> dict[str, Any]:
        """Get metrics as dictionary."""
        return self.metrics

    def to_json(self) -> str:
        """Get metrics as JSON string."""
        return json.dumps(self.metrics, indent=2)


def collect_build_metrics(
    duration_seconds: float,
    profile: str,
    wheel_sizes: dict[str, int] | None = None,
    dependency_count: int = 0,
) -> Path:
    """Collect build phase metrics."""
    collector = MetricsCollector()
    collector.add_build_metrics(
        duration_seconds=duration_seconds,
        profile=profile,
        wheel_sizes=wheel_sizes,
        dependency_count=dependency_count,
    )
    return collector.save()


def collect_sbom_metrics(
    version: str,
    profiles: list[str],
    components: int,
    signatures_valid: bool = True,
    generation_time_seconds: float = 0.0,
) -> Path:
    """Collect SBOM generation metrics."""
    collector = MetricsCollector()
    collector.add_sbom_metrics(
        version=version,
        profiles=profiles,
        components=components,
        signatures_valid=signatures_valid,
        generation_time_seconds=generation_time_seconds,
    )
    return collector.save()


def collect_release_metrics(
    tag: str,
    artifacts_uploaded: int,
    sbom_attached: bool = True,
    wheel_hashes_verified: bool = True,
) -> Path:
    """Collect release metrics."""
    collector = MetricsCollector()
    collector.add_release_metrics(
        tag=tag,
        artifacts_uploaded=artifacts_uploaded,
        sbom_attached=sbom_attached,
        wheel_hashes_verified=wheel_hashes_verified,
    )
    return collector.save()


def collect_offline_install_metrics(
    profile: str,
    duration_seconds: float,
    packages_installed: int,
    verification_time_seconds: float,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> Path:
    """Collect offline installation test metrics."""
    collector = MetricsCollector()
    collector.add_offline_install_metrics(
        profile=profile,
        duration_seconds=duration_seconds,
        packages_installed=packages_installed,
        verification_time_seconds=verification_time_seconds,
        errors=errors,
        warnings=warnings,
    )
    return collector.save()


def load_metrics(filepath: Path) -> dict[str, Any]:
    """Load metrics from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def get_latest_metrics(phase: str = "build") -> dict[str, Any] | None:
    """Get latest metrics for a phase."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    metrics_files = sorted(METRICS_DIR.glob(f"{phase}-*.json"), reverse=True)
    if metrics_files:
        return load_metrics(metrics_files[0])
    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Telemetry metrics collection")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Collect build
    build_parser = subparsers.add_parser("collect-build", help="Collect build metrics")
    build_parser.add_argument("--duration", type=float, required=True)
    build_parser.add_argument("--profile", choices=["core", "runtime", "full"])
    build_parser.add_argument("--dependencies", type=int, default=0)

    # Collect SBOM
    sbom_parser = subparsers.add_parser("collect-sbom", help="Collect SBOM metrics")
    sbom_parser.add_argument("--version", required=True)
    sbom_parser.add_argument("--profiles", nargs="+", required=True)
    sbom_parser.add_argument("--components", type=int, required=True)
    sbom_parser.add_argument("--generation-time", type=float, default=0.0)

    # Collect release
    release_parser = subparsers.add_parser("collect-release", help="Collect release metrics")
    release_parser.add_argument("--tag", required=True)
    release_parser.add_argument("--artifacts", type=int, required=True)

    # Get latest
    latest_parser = subparsers.add_parser("get-latest", help="Get latest metrics")
    latest_parser.add_argument("--phase", default="build")

    args = parser.parse_args()

    if args.command == "collect-build":
        filepath = collect_build_metrics(
            duration_seconds=args.duration,
            profile=args.profile,
            dependency_count=args.dependencies,
        )
        print(f"Metrics saved to {filepath}")

    elif args.command == "collect-sbom":
        filepath = collect_sbom_metrics(
            version=args.version,
            profiles=args.profiles,
            components=args.components,
            generation_time_seconds=args.generation_time,
        )
        print(f"Metrics saved to {filepath}")

    elif args.command == "collect-release":
        filepath = collect_release_metrics(
            tag=args.tag,
            artifacts_uploaded=args.artifacts,
        )
        print(f"Metrics saved to {filepath}")

    elif args.command == "get-latest":
        metrics = get_latest_metrics(phase=args.phase)
        if metrics:
            print(json.dumps(metrics, indent=2))
        else:
            print(f"No metrics found for phase: {args.phase}")
