"""
Infrastructure Enhancements

Implements Phase 4 infrastructure capabilities:
- Dynamic Docker tag strategies (semver, hash-based)
- Artifact lifecycle management
- Multi-architecture builds
- Progressive deployment gates

Phase 4: Infrastructure

Author: mbaetiong
Generated: 2025-12-22
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


class TagStrategy(Enum):
    """Docker tag strategy types."""

    SEMVER = "semver"
    HASH_BASED = "hash_based"
    DATE_BASED = "date_based"
    BRANCH_BASED = "branch_based"
    HYBRID = "hybrid"


class DeploymentGate(Enum):
    """Deployment gate types."""

    TESTS = "tests"
    SECURITY_SCAN = "security_scan"
    CODE_REVIEW = "code_review"
    PERFORMANCE = "performance"
    MANUAL_APPROVAL = "manual_approval"


@dataclass
class DockerTag:
    """Represents a Docker image tag."""

    tag: str
    strategy: TagStrategy
    commit_sha: str
    branch: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Artifact:
    """Represents a build artifact."""

    artifact_id: str
    name: str
    artifact_type: str  # docker, binary, archive, documentation
    version: str
    size_bytes: int
    created_at: str
    expires_at: Optional[str]
    retention_days: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildConfiguration:
    """Multi-architecture build configuration."""

    build_id: str
    platforms: list[str]
    base_image: str
    build_args: dict[str, str]
    cache_from: list[str]
    labels: dict[str, str]
    created_at: str


@dataclass
class DeploymentStage:
    """Deployment stage in progressive rollout."""

    stage_id: str
    name: str
    gates: list[DeploymentGate]
    traffic_percentage: int
    duration_minutes: int
    rollback_on_failure: bool
    status: str  # pending, active, completed, failed, rolled_back


# ============================================================================
# Dynamic Docker Tag Strategies
# ============================================================================


class DockerTagManager:
    """
    Manages dynamic Docker tag strategies.

    Supports multiple tagging strategies:
    - Semantic versioning (semver)
    - Hash-based (commit SHA)
    - Date-based (YYYYMMDD)
    - Branch-based (sanitized branch name)
    - Hybrid (combination)
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize Docker tag manager."""
        self.storage_path = storage_path or Path(
            "data/docker_tags"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.tags: dict[str, DockerTag] = {}
        self.current_version: tuple[int, int, int] = (0, 1, 0)

        self._load_state()

        logger.info(
            f"✅ DockerTagManager initialized | "
            f"Current version: {self._version_string()}"
        )

    def _load_state(self) -> None:
        """Load tag state from disk."""
        state_file = self.storage_path / "state.json"
        try:
            if state_file.exists():
                with open(state_file) as f:
                    data = json.load(f)
                    self.current_version = tuple(data.get("version", [0, 1, 0]))
                    for tid, tdata in data.get("tags", {}).items():
                        tdata["strategy"] = TagStrategy(tdata["strategy"])
                        self.tags[tid] = DockerTag(**tdata)
        except Exception as e:
            logger.warning(f"Failed to load tag state: {e}")

    def _save_state(self) -> None:
        """Save tag state to disk."""
        state_file = self.storage_path / "state.json"
        try:
            data = {
                "version": list(self.current_version),
                "tags": {
                    tid: {
                        "tag": t.tag,
                        "strategy": t.strategy.value,
                        "commit_sha": t.commit_sha,
                        "branch": t.branch,
                        "created_at": t.created_at,
                        "metadata": t.metadata,
                    }
                    for tid, t in self.tags.items()
                },
            }
            with open(state_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save tag state: {e}")

    def _version_string(self) -> str:
        """Get current version as string."""
        return f"{self.current_version[0]}.{self.current_version[1]}.{self.current_version[2]}"

    def sanitize_branch_name(self, branch: str) -> str:
        """
        Sanitize branch name for Docker tag compliance.

        Docker tags must:
        - Start with alphanumeric
        - Contain only alphanumeric, _, -, .
        - Be max 128 characters

        Args:
            branch: Branch name to sanitize

        Returns:
            Sanitized tag-safe string
        """
        # Convert to lowercase
        sanitized = branch.lower()

        # Replace slashes with hyphens
        sanitized = sanitized.replace("/", "-")

        # Replace colons with hyphens
        sanitized = sanitized.replace(":", "-")

        # Remove invalid characters
        sanitized = re.sub(r"[^a-z0-9._-]", "-", sanitized)

        # Remove leading/trailing hyphens and dots
        sanitized = sanitized.strip("-.")

        # Ensure it starts with alphanumeric
        if sanitized and not sanitized[0].isalnum():
            sanitized = "b-" + sanitized

        # Limit length
        if len(sanitized) > 128:
            sanitized = sanitized[:128]

        return sanitized or "latest"

    def generate_tag(
        self,
        strategy: TagStrategy,
        commit_sha: str,
        branch: str = "main",
        bump_type: Optional[str] = None,
    ) -> DockerTag:
        """
        Generate a Docker tag using the specified strategy.

        Args:
            strategy: Tag strategy to use
            commit_sha: Git commit SHA
            branch: Git branch name
            bump_type: For semver, type of version bump (major, minor, patch)

        Returns:
            Generated DockerTag
        """
        now = datetime.utcnow()
        tag_value = ""

        if strategy == TagStrategy.SEMVER:
            # Bump version
            major, minor, patch = self.current_version
            if bump_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif bump_type == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1

            self.current_version = (major, minor, patch)
            tag_value = f"v{major}.{minor}.{patch}"

        elif strategy == TagStrategy.HASH_BASED:
            # Use short commit SHA
            tag_value = f"sha-{commit_sha[:8]}"

        elif strategy == TagStrategy.DATE_BASED:
            # Use date format
            tag_value = now.strftime("%Y%m%d.%H%M%S")

        elif strategy == TagStrategy.BRANCH_BASED:
            # Use sanitized branch name
            sanitized = self.sanitize_branch_name(branch)
            tag_value = f"{sanitized}-latest"

        elif strategy == TagStrategy.HYBRID:
            # Combine version, date, and short hash
            version = self._version_string()
            date = now.strftime("%Y%m%d")
            short_sha = commit_sha[:7]
            tag_value = f"v{version}-{date}-{short_sha}"

        docker_tag = DockerTag(
            tag=tag_value,
            strategy=strategy,
            commit_sha=commit_sha,
            branch=branch,
            created_at=now.isoformat(),
            metadata={"bump_type": bump_type} if bump_type else {},
        )

        self.tags[tag_value] = docker_tag
        self._save_state()

        logger.info(f"🏷️ Generated tag: {tag_value} ({strategy.value})")

        return docker_tag

    def get_latest_tags(self, count: int = 5) -> list[DockerTag]:
        """Get most recent tags."""
        sorted_tags = sorted(
            self.tags.values(),
            key=lambda t: t.created_at,
            reverse=True,
        )
        return sorted_tags[:count]

    def get_tag_statistics(self) -> dict[str, Any]:
        """Get tag statistics."""
        by_strategy = {}
        for tag in self.tags.values():
            strategy = tag.strategy.value
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1

        return {
            "total_tags": len(self.tags),
            "current_version": self._version_string(),
            "by_strategy": by_strategy,
            "latest_tag": self.get_latest_tags(1)[0].tag if self.tags else None,
        }


# ============================================================================
# Artifact Lifecycle Management
# ============================================================================


class ArtifactLifecycleManager:
    """
    Manages artifact lifecycle including retention and cleanup.

    Features:
    - Automatic expiration based on retention policies
    - Size-based cleanup
    - Artifact metadata tracking
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        retention_policies: Optional[dict[str, int]] = None,
    ):
        """
        Initialize artifact lifecycle manager.

        Args:
            storage_path: Path for artifact storage
            retention_policies: Custom retention policies (days) per artifact type.
                              Can also be configured via environment variables:
                              - ARTIFACT_RETENTION_DOCKER (default: 90)
                              - ARTIFACT_RETENTION_BINARY (default: 30)
                              - ARTIFACT_RETENTION_ARCHIVE (default: 60)
                              - ARTIFACT_RETENTION_DOCUMENTATION (default: 365)
                              - ARTIFACT_RETENTION_TEST_RESULTS (default: 14)
                              - ARTIFACT_RETENTION_COVERAGE (default: 30)
        """
        self.storage_path = storage_path or Path(
            "data/artifacts"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.artifacts: dict[str, Artifact] = {}

        # Default retention policies (days)
        # Rationale:
        # - docker (90): Container images need long-term availability for rollbacks
        # - binary (30): Binaries are rebuilt frequently, older ones rarely needed
        # - archive (60): Archives are for backup/audit, moderate retention
        # - documentation (365): Docs should be available for reference for a year
        # - test_results (14): Test results are short-lived, only recent ones matter
        # - coverage (30): Coverage reports are analyzed monthly
        self.retention_policies = self._load_retention_policies(retention_policies)

        self._load_artifacts()

        logger.info(
            f"✅ ArtifactLifecycleManager initialized | "
            f"Artifacts: {len(self.artifacts)}"
        )

    def _load_retention_policies(
        self, custom_policies: Optional[dict[str, int]]
    ) -> dict[str, int]:
        """
        Load retention policies from custom config or environment variables.

        Priority: custom_policies > environment variables > defaults
        """
        defaults = {
            "docker": 90,
            "binary": 30,
            "archive": 60,
            "documentation": 365,
            "test_results": 14,
            "coverage": 30,
        }

        # Apply environment variable overrides
        env_prefix = "ARTIFACT_RETENTION_"
        for key in defaults:
            env_key = f"{env_prefix}{key.upper()}"
            env_value = os.environ.get(env_key)
            if env_value:
                try:
                    defaults[key] = int(env_value)
                    logger.info(f"📋 Loaded {key} retention from {env_key}: {defaults[key]} days")
                except ValueError:
                    logger.warning(f"Invalid value for {env_key}: {env_value}")

        # Apply custom policy overrides
        if custom_policies:
            for key, value in custom_policies.items():
                if key in defaults:
                    defaults[key] = value
                    logger.info(f"📋 Custom {key} retention: {value} days")

        return defaults

    def _load_artifacts(self) -> None:
        """Load artifacts from disk."""
        artifacts_file = self.storage_path / "artifacts.json"
        try:
            if artifacts_file.exists():
                with open(artifacts_file) as f:
                    data = json.load(f)
                    for aid, adata in data.items():
                        self.artifacts[aid] = Artifact(**adata)
        except Exception as e:
            logger.warning(f"Failed to load artifacts: {e}")

    def _save_artifacts(self) -> None:
        """Save artifacts to disk."""
        artifacts_file = self.storage_path / "artifacts.json"
        try:
            data = {
                aid: {
                    "artifact_id": a.artifact_id,
                    "name": a.name,
                    "artifact_type": a.artifact_type,
                    "version": a.version,
                    "size_bytes": a.size_bytes,
                    "created_at": a.created_at,
                    "expires_at": a.expires_at,
                    "retention_days": a.retention_days,
                    "metadata": a.metadata,
                }
                for aid, a in self.artifacts.items()
            }
            with open(artifacts_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save artifacts: {e}")

    def register_artifact(
        self,
        name: str,
        artifact_type: str,
        version: str,
        size_bytes: int,
        metadata: Optional[dict[str, Any]] = None,
        retention_days: Optional[int] = None,
    ) -> Artifact:
        """
        Register a new artifact.

        Args:
            name: Artifact name
            artifact_type: Type of artifact
            version: Artifact version
            size_bytes: Size in bytes
            metadata: Additional metadata
            retention_days: Custom retention period

        Returns:
            Created Artifact
        """
        artifact_id = hashlib.md5(
            f"{name}:{version}:{datetime.utcnow().isoformat()}".encode(), usedforsecurity=False
        ).hexdigest()[:12]  # nosec B324 - Not for security, ID generation only

        retention = retention_days or self.retention_policies.get(artifact_type, 30)
        now = datetime.utcnow()
        expires = now + timedelta(days=retention)

        artifact = Artifact(
            artifact_id=artifact_id,
            name=name,
            artifact_type=artifact_type,
            version=version,
            size_bytes=size_bytes,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            retention_days=retention,
            metadata=metadata or {},
        )

        self.artifacts[artifact_id] = artifact
        self._save_artifacts()

        logger.info(
            f"📦 Registered artifact: {name} v{version} "
            f"(expires: {expires.strftime('%Y-%m-%d')})"
        )

        return artifact

    def get_expired_artifacts(self) -> list[Artifact]:
        """Get list of expired artifacts."""
        now = datetime.utcnow()
        expired = []

        for artifact in self.artifacts.values():
            if artifact.expires_at:
                expires = datetime.fromisoformat(artifact.expires_at)
                if expires < now:
                    expired.append(artifact)

        return expired

    def cleanup_expired(self) -> list[str]:
        """
        Remove expired artifacts.

        Returns:
            List of removed artifact IDs
        """
        expired = self.get_expired_artifacts()
        removed = []

        for artifact in expired:
            del self.artifacts[artifact.artifact_id]
            removed.append(artifact.artifact_id)

        if removed:
            self._save_artifacts()
            logger.info(f"🗑️ Cleaned up {len(removed)} expired artifacts")

        return removed

    def get_artifacts_by_type(self, artifact_type: str) -> list[Artifact]:
        """Get artifacts of a specific type."""
        return [a for a in self.artifacts.values() if a.artifact_type == artifact_type]

    def get_total_size(self) -> int:
        """Get total size of all artifacts in bytes."""
        return sum(a.size_bytes for a in self.artifacts.values())

    def get_lifecycle_statistics(self) -> dict[str, Any]:
        """Get lifecycle statistics."""
        by_type = {}
        for artifact in self.artifacts.values():
            atype = artifact.artifact_type
            if atype not in by_type:
                by_type[atype] = {"count": 0, "size_bytes": 0}
            by_type[atype]["count"] += 1
            by_type[atype]["size_bytes"] += artifact.size_bytes

        return {
            "total_artifacts": len(self.artifacts),
            "total_size_bytes": self.get_total_size(),
            "total_size_mb": self.get_total_size() / (1024 * 1024),
            "expired_count": len(self.get_expired_artifacts()),
            "by_type": by_type,
            "retention_policies": self.retention_policies,
        }


# ============================================================================
# Multi-Architecture Builds
# ============================================================================


class MultiArchBuilder:
    """
    Manages multi-architecture Docker builds.

    Supports building for multiple platforms:
    - linux/amd64
    - linux/arm64
    - linux/arm/v7
    - etc.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize multi-arch builder."""
        self.storage_path = storage_path or Path(
            "data/builds"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.builds: dict[str, BuildConfiguration] = {}

        # Supported platforms
        self.supported_platforms = [
            "linux/amd64",
            "linux/arm64",
            "linux/arm/v7",
            "linux/386",
            "linux/ppc64le",
            "linux/s390x",
        ]

        # Default build configuration
        self.default_platforms = ["linux/amd64", "linux/arm64"]

        self._load_builds()

        logger.info(
            f"✅ MultiArchBuilder initialized | "
            f"Builds: {len(self.builds)}"
        )

    def _load_builds(self) -> None:
        """Load builds from disk."""
        builds_file = self.storage_path / "builds.json"
        try:
            if builds_file.exists():
                with open(builds_file) as f:
                    data = json.load(f)
                    for bid, bdata in data.items():
                        self.builds[bid] = BuildConfiguration(**bdata)
        except Exception as e:
            logger.warning(f"Failed to load builds: {e}")

    def _save_builds(self) -> None:
        """Save builds to disk."""
        builds_file = self.storage_path / "builds.json"
        try:
            data = {
                bid: {
                    "build_id": b.build_id,
                    "platforms": b.platforms,
                    "base_image": b.base_image,
                    "build_args": b.build_args,
                    "cache_from": b.cache_from,
                    "labels": b.labels,
                    "created_at": b.created_at,
                }
                for bid, b in self.builds.items()
            }
            with open(builds_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save builds: {e}")

    def create_build_config(
        self,
        base_image: str,
        platforms: Optional[list[str]] = None,
        build_args: Optional[dict[str, str]] = None,
        cache_from: Optional[list[str]] = None,
        labels: Optional[dict[str, str]] = None,
    ) -> BuildConfiguration:
        """
        Create a multi-architecture build configuration.

        Args:
            base_image: Base Docker image
            platforms: Target platforms
            build_args: Build arguments
            cache_from: Cache sources
            labels: Image labels

        Returns:
            BuildConfiguration
        """
        build_id = hashlib.md5(
            f"{base_image}:{datetime.utcnow().isoformat()}".encode(), usedforsecurity=False
        ).hexdigest()[:12]  # nosec B324 - Not for security, ID generation only

        # Validate platforms
        platforms = platforms or self.default_platforms
        for platform in platforms:
            if platform not in self.supported_platforms:
                logger.warning(f"Unsupported platform: {platform}")

        config = BuildConfiguration(
            build_id=build_id,
            platforms=platforms,
            base_image=base_image,
            build_args=build_args or {},
            cache_from=cache_from or [],
            labels=labels or {},
            created_at=datetime.utcnow().isoformat(),
        )

        self.builds[build_id] = config
        self._save_builds()

        logger.info(
            f"🏗️ Created build config: {build_id} "
            f"({len(platforms)} platforms)"
        )

        return config

    def generate_buildx_command(self, config: BuildConfiguration) -> str:
        """
        Generate docker buildx command for multi-arch build.

        Args:
            config: Build configuration

        Returns:
            Docker buildx command string
        """
        cmd_parts = ["docker", "buildx", "build"]

        # Add platforms
        platforms_str = ",".join(config.platforms)
        cmd_parts.extend(["--platform", platforms_str])

        # Add build args
        for key, value in config.build_args.items():
            cmd_parts.extend(["--build-arg", f"{key}={value}"])

        # Add cache
        for cache in config.cache_from:
            cmd_parts.extend(["--cache-from", cache])

        # Add labels
        for key, value in config.labels.items():
            cmd_parts.extend(["--label", f"{key}={value}"])

        # Add push flag for multi-platform
        cmd_parts.append("--push")

        # Add context
        cmd_parts.append(".")

        return " ".join(cmd_parts)

    def generate_github_action_step(
        self, config: BuildConfiguration, image_name: str
    ) -> dict[str, Any]:
        """
        Generate GitHub Actions step for multi-arch build.

        Args:
            config: Build configuration
            image_name: Target image name

        Returns:
            GitHub Actions step definition
        """
        return {
            "name": "Build and push multi-arch image",
            "uses": "docker/build-push-action@v6",
            "with": {
                "context": ".",
                "platforms": ",".join(config.platforms),
                "push": True,
                "tags": image_name,
                "build-args": "\n".join(
                    f"{k}={v}" for k, v in config.build_args.items()
                ),
                "cache-from": "type=gha",
                "cache-to": "type=gha,mode=max",
                "labels": "\n".join(
                    f"{k}={v}" for k, v in config.labels.items()
                ),
            },
        }

    def get_build_statistics(self) -> dict[str, Any]:
        """Get build statistics."""
        platform_usage = {}
        for build in self.builds.values():
            for platform in build.platforms:
                platform_usage[platform] = platform_usage.get(platform, 0) + 1

        return {
            "total_builds": len(self.builds),
            "supported_platforms": self.supported_platforms,
            "default_platforms": self.default_platforms,
            "platform_usage": platform_usage,
        }


# ============================================================================
# Progressive Deployment Gates
# ============================================================================


class ProgressiveDeployment:
    """
    Manages progressive deployment with gates.

    Features:
    - Multiple deployment stages
    - Gate checks before progressing
    - Automatic rollback on failure
    - Traffic percentage control
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize progressive deployment."""
        self.storage_path = storage_path or Path(
            "data/deployments"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.stages: dict[str, DeploymentStage] = {}
        self.deployment_history: list[dict[str, Any]] = []

        self._initialize_default_stages()

        logger.info(
            f"✅ ProgressiveDeployment initialized | "
            f"Stages: {len(self.stages)}"
        )

    def _initialize_default_stages(self) -> None:
        """Initialize default deployment stages."""
        default_stages = [
            DeploymentStage(
                stage_id="canary",
                name="Canary",
                gates=[DeploymentGate.TESTS, DeploymentGate.SECURITY_SCAN],
                traffic_percentage=5,
                duration_minutes=30,
                rollback_on_failure=True,
                status="pending",
            ),
            DeploymentStage(
                stage_id="staging",
                name="Staging",
                gates=[
                    DeploymentGate.TESTS,
                    DeploymentGate.SECURITY_SCAN,
                    DeploymentGate.PERFORMANCE,
                ],
                traffic_percentage=25,
                duration_minutes=60,
                rollback_on_failure=True,
                status="pending",
            ),
            DeploymentStage(
                stage_id="production",
                name="Production",
                gates=[
                    DeploymentGate.TESTS,
                    DeploymentGate.SECURITY_SCAN,
                    DeploymentGate.CODE_REVIEW,
                    DeploymentGate.MANUAL_APPROVAL,
                ],
                traffic_percentage=100,
                duration_minutes=0,
                rollback_on_failure=True,
                status="pending",
            ),
        ]

        for stage in default_stages:
            self.stages[stage.stage_id] = stage

    def check_gate(
        self, gate: DeploymentGate, context: dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Check if a deployment gate passes.

        Args:
            gate: Gate to check
            context: Context for the check

        Returns:
            Tuple of (passed, message)
        """
        if gate == DeploymentGate.TESTS:
            test_passed = context.get("tests_passed", False)
            return (
                test_passed,
                "All tests passed" if test_passed else "Tests failed",
            )

        if gate == DeploymentGate.SECURITY_SCAN:
            vulnerabilities = context.get("vulnerabilities", 0)
            passed = vulnerabilities == 0
            return (
                passed,
                "No vulnerabilities found"
                if passed
                else f"Found {vulnerabilities} vulnerabilities",
            )

        if gate == DeploymentGate.CODE_REVIEW:
            approvals = context.get("approvals", 0)
            required = context.get("required_approvals", 1)
            passed = approvals >= required
            return (
                passed,
                f"Got {approvals}/{required} approvals"
                if passed
                else f"Need {required - approvals} more approvals",
            )

        if gate == DeploymentGate.PERFORMANCE:
            latency = context.get("latency_ms", 1000)
            threshold = context.get("latency_threshold_ms", 200)
            passed = latency <= threshold
            return (
                passed,
                f"Latency {latency}ms (< {threshold}ms)"
                if passed
                else f"Latency {latency}ms exceeds {threshold}ms",
            )

        if gate == DeploymentGate.MANUAL_APPROVAL:
            approved = context.get("manually_approved", False)
            return (
                approved,
                "Manually approved" if approved else "Awaiting manual approval",
            )

        return (False, f"Unknown gate: {gate.value}")

    def advance_stage(
        self,
        stage_id: str,
        context: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """
        Attempt to advance to the next deployment stage.

        Args:
            stage_id: Current stage ID
            context: Context for gate checks

        Returns:
            Tuple of (success, messages)
        """
        if stage_id not in self.stages:
            return (False, [f"Unknown stage: {stage_id}"])

        stage = self.stages[stage_id]
        messages = []
        all_passed = True

        # Check all gates
        for gate in stage.gates:
            passed, message = self.check_gate(gate, context)
            messages.append(f"{gate.value}: {message}")
            if not passed:
                all_passed = False

        if all_passed:
            stage.status = "completed"
            self.deployment_history.append(
                {
                    "stage_id": stage_id,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "messages": messages,
                }
            )
            logger.info(f"✅ Stage {stage_id} completed")
        else:
            if stage.rollback_on_failure:
                stage.status = "rolled_back"
                messages.append("Rolled back due to gate failure")
            else:
                stage.status = "failed"
            logger.warning(f"❌ Stage {stage_id} failed")

        return (all_passed, messages)

    def get_deployment_plan(self) -> list[dict[str, Any]]:
        """
        Get the full deployment plan.

        Returns:
            List of stage configurations
        """
        return [
            {
                "stage_id": s.stage_id,
                "name": s.name,
                "gates": [g.value for g in s.gates],
                "traffic_percentage": s.traffic_percentage,
                "duration_minutes": s.duration_minutes,
                "rollback_on_failure": s.rollback_on_failure,
                "status": s.status,
            }
            for s in self.stages.values()
        ]

    def generate_github_workflow(self) -> dict[str, Any]:
        """
        Generate GitHub Actions workflow for progressive deployment.

        Returns:
            Workflow definition
        """
        jobs = {}

        stage_list = list(self.stages.values())
        for i, stage in enumerate(stage_list):
            job_id = f"deploy_{stage.stage_id}"

            needs = []
            if i > 0:
                needs.append(f"deploy_{stage_list[i-1].stage_id}")

            steps = [
                {
                    "name": "Checkout",
                    "uses": "actions/checkout@v4",
                },
            ]

            # Add gate steps
            for gate in stage.gates:
                if gate == DeploymentGate.TESTS:
                    steps.append(
                        {
                            "name": "Run tests",
                            "run": "pytest --tb=short",
                        }
                    )
                elif gate == DeploymentGate.SECURITY_SCAN:
                    steps.append(
                        {
                            "name": "Security scan",
                            "uses": "github/codeql-action/analyze@v3",
                        }
                    )

            # Add deployment step
            steps.append(
                {
                    "name": f"Deploy to {stage.name}",
                    "run": f"echo 'Deploying {stage.traffic_percentage}% traffic'",
                }
            )

            # Add wait step if there's a duration
            if stage.duration_minutes > 0:
                steps.append(
                    {
                        "name": f"Wait for {stage.duration_minutes} minutes",
                        "run": f"sleep {stage.duration_minutes * 60}",
                    }
                )

            jobs[job_id] = {
                "name": f"Deploy to {stage.name}",
                "runs-on": "ubuntu-latest",
                "needs": needs if needs else None,
                "steps": steps,
            }

            # Clean up None values
            if jobs[job_id]["needs"] is None:
                del jobs[job_id]["needs"]

        return {
            "name": "Progressive Deployment",
            "on": {"push": {"branches": ["main"]}},
            "jobs": jobs,
        }

    def get_deployment_statistics(self) -> dict[str, Any]:
        """Get deployment statistics."""
        status_counts = {}
        for stage in self.stages.values():
            status_counts[stage.status] = status_counts.get(stage.status, 0) + 1

        return {
            "total_stages": len(self.stages),
            "status_counts": status_counts,
            "history_count": len(self.deployment_history),
            "available_gates": [g.value for g in DeploymentGate],
        }
