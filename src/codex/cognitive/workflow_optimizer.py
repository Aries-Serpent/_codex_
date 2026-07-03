"""
Workflow Optimizer - Phase 4.4 of Long-term Plan 4.

This module provides workflow analysis and optimization capabilities for:
- Identifying pending approval workflows
- Analyzing workflow performance and redundancies
- Recommending cache strategies
- Tracking immutable components
- Providing markers/checkpoints for workflow state
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Status of a workflow run."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ACTION_REQUIRED = "action_required"
    PENDING_APPROVAL = "pending_approval"


class WorkflowCategory(Enum):
    """Categories of workflows."""

    SECURITY = "security"  # CodeQL, Semgrep, security scans
    TESTING = "testing"  # Unit tests, integration tests
    QUALITY = "quality"  # Linting, code quality
    BUILD = "build"  # Build and packaging
    DOCUMENTATION = "documentation"  # Doc generation, link checking
    DEPLOYMENT = "deployment"  # Deploys and releases
    MAINTENANCE = "maintenance"  # Cache cleanup, archival
    MONITORING = "monitoring"  # Health checks, analytics
    OTHER = "other"


class OptimizationType(Enum):
    """Types of workflow optimizations."""

    CONSOLIDATION = "consolidation"  # Merge similar workflows
    CACHING = "caching"  # Improve cache usage
    PARALLELIZATION = "parallelization"  # Run jobs in parallel
    ELIMINATION = "elimination"  # Remove redundant workflows
    REORDERING = "reordering"  # Optimize execution order
    CHECKPOINT = "checkpoint"  # Add checkpoints for resumption


@dataclass
class WorkflowInfo:
    """Information about a workflow."""

    name: str
    path: str
    category: WorkflowCategory
    triggers: list[str]  # push, pull_request, schedule, etc.
    estimated_duration_min: float
    uses_cache: bool
    cache_keys: list[str]
    dependencies: list[str]  # Other workflows it depends on
    outputs: list[str]  # Artifacts/outputs produced
    is_required: bool  # Required for merge
    approval_required: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "category": self.category.value,
            "triggers": self.triggers,
            "estimated_duration_min": self.estimated_duration_min,
            "uses_cache": self.uses_cache,
            "cache_keys": self.cache_keys,
            "dependencies": self.dependencies,
            "outputs": self.outputs,
            "is_required": self.is_required,
            "approval_required": self.approval_required,
        }


@dataclass
class WorkflowRun:
    """A single workflow run."""

    run_id: str
    workflow_name: str
    status: WorkflowStatus
    conclusion: str | None
    started_at: datetime
    completed_at: datetime | None
    duration_seconds: float | None
    head_sha: str
    branch: str
    cache_hit: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "conclusion": self.conclusion,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "head_sha": self.head_sha,
            "branch": self.branch,
            "cache_hit": self.cache_hit,
        }


@dataclass
class OptimizationRecommendation:
    """A recommendation for workflow optimization."""

    optimization_type: OptimizationType
    target_workflows: list[str]
    description: str
    estimated_savings_min: float
    priority: int  # 1 = highest
    implementation_effort: str  # low, medium, high
    code_changes: list[str]  # Suggested code changes

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "optimization_type": self.optimization_type.value,
            "target_workflows": self.target_workflows,
            "description": self.description,
            "estimated_savings_min": self.estimated_savings_min,
            "priority": self.priority,
            "implementation_effort": self.implementation_effort,
            "code_changes": self.code_changes,
        }


@dataclass
class ImmutableComponent:
    """A component that should not change."""

    component_id: str
    name: str
    path: str
    checksum: str
    verified_at: datetime
    verified_by: str  # workflow name that verified it
    reason: str  # Why it's immutable

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component_id": self.component_id,
            "name": self.name,
            "path": self.path,
            "checksum": self.checksum,
            "verified_at": self.verified_at.isoformat(),
            "verified_by": self.verified_by,
            "reason": self.reason,
        }


@dataclass
class WorkflowCheckpoint:
    """A checkpoint in workflow execution."""

    checkpoint_id: str
    workflow_name: str
    step_name: str
    status: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_name": self.workflow_name,
            "step_name": self.step_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class WorkflowCategorizer:
    """Categorize workflows by their purpose."""

    CATEGORY_PATTERNS = {
        WorkflowCategory.SECURITY: [
            r"codeql",
            r"security",
            r"semgrep",
            r"secret",
            r"vulnerability",
            r"scan",
        ],
        WorkflowCategory.TESTING: [
            r"test",
            r"pytest",
            r"coverage",
            r"spec",
            r"unittest",
        ],
        WorkflowCategory.QUALITY: [
            r"lint",
            r"quality",
            r"ruff",
            r"black",
            r"format",
            r"mypy",
        ],
        WorkflowCategory.BUILD: [
            r"build",
            r"compile",
            r"package",
            r"docker",
            r"artifact",
        ],
        WorkflowCategory.DOCUMENTATION: [
            r"doc",
            r"mkdocs",
            r"pages",
            r"readme",
            r"wiki",
        ],
        WorkflowCategory.DEPLOYMENT: [
            r"deploy",
            r"release",
            r"publish",
            r"production",
        ],
        WorkflowCategory.MAINTENANCE: [
            r"cleanup",
            r"cache",
            r"archive",
            r"prune",
            r"rotate",
        ],
        WorkflowCategory.MONITORING: [
            r"health",
            r"monitor",
            r"analytics",
            r"metric",
            r"status",
        ],
    }

    def categorize(self, workflow_name: str, workflow_path: str) -> WorkflowCategory:
        """Categorize a workflow by name and path."""
        text = f"{workflow_name} {workflow_path}".lower()

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return category

        return WorkflowCategory.OTHER


class WorkflowAnalyzer:
    """Analyze workflow configurations."""

    def __init__(self, workflows_dir: Path | None = None):
        """Initialize analyzer."""
        self.workflows_dir = workflows_dir or Path(".github/workflows")
        self.categorizer = WorkflowCategorizer()
        self._workflows: dict[str, WorkflowInfo] = {}

    def scan_workflows(self) -> list[WorkflowInfo]:
        """Scan all workflow files."""
        workflows: list[Any] = []

        if not self.workflows_dir.exists():
            return workflows

        for yml_file in self.workflows_dir.glob("*.yml"):
            try:
                info = self._parse_workflow_file(yml_file)
                if info:
                    workflows.append(info)
                    self._workflows[info.name] = info
            except (OSError, yaml.YAMLError):
                logger.debug("Suppressed exception in handler", exc_info=True)
        return workflows

    def _parse_workflow_file(self, path: Path) -> WorkflowInfo | None:
        """Parse a workflow file."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f)

            if not data or not isinstance(data, dict):
                return None

            name = data.get("name", path.stem)
            triggers = list(data.get("on", {}).keys()) if isinstance(data.get("on"), dict) else []

            # Detect cache usage (checking for action names/YAML keys)
            workflow_text = path.read_text()
            uses_cache = "actions/cache" in workflow_text or "cache:" in workflow_text  # nosec
            cache_keys = re.findall(r"key:\s*['\"]?([^'\"}\n]+)", workflow_text)

            # Detect approval requirements (YAML key detection, not URL validation)
            approval_required = (
                "environment:" in workflow_text  # nosec - YAML key detection
                or "needs-approval" in workflow_text.lower()  # nosec
            )

            return WorkflowInfo(
                name=name,
                path=str(path),
                category=self.categorizer.categorize(name, str(path)),
                triggers=triggers,
                estimated_duration_min=5.0,  # Default estimate
                uses_cache=uses_cache,
                cache_keys=cache_keys[:5],
                dependencies=[],
                outputs=[],
                is_required="required" in workflow_text.lower(),  # nosec - YAML key detection
                approval_required=approval_required,
            )
        except (IOError, OSError):
            # Workflow parsing failed - skip this file
            return None

    def _parse_workflow_basic(self, path: Path) -> WorkflowInfo | None:
        """Basic workflow parsing without yaml library.

        Note: The substring checks below (e.g., 'push:' in content) are used
        to detect YAML keys in workflow files, not for URL/domain validation.
        This is safe as we're parsing local workflow files, not validating URLs.
        """
        try:
            content = path.read_text()

            # Extract name
            name_match = re.search(r'^name:\s*["\']?([^"\'}\n]+)', content, re.MULTILINE)
            name = name_match.group(1).strip() if name_match else path.stem

            # Detect triggers (looking for YAML keys in workflow files)
            triggers = []
            if "push:" in content:  # nosec - YAML key detection, not URL validation
                triggers.append("push")
            if "pull_request:" in content:  # nosec - YAML key detection
                triggers.append("pull_request")
            if "schedule:" in content:  # nosec - YAML key detection
                triggers.append("schedule")
            if "workflow_dispatch:" in content:  # nosec - YAML key detection
                triggers.append("workflow_dispatch")

            # Detect cache usage (checking for action names/YAML keys)
            uses_cache = "actions/cache" in content or "cache:" in content  # nosec
            cache_keys = re.findall(r"key:\s*['\"]?([^'\"}\n]+)", content)

            # Detect approval (YAML key detection, not URL validation)
            approval_required = (
                "environment:" in content  # nosec - YAML key detection
                or "needs-approval" in content.lower()  # nosec
            )

            return WorkflowInfo(
                name=name,
                path=str(path),
                category=self.categorizer.categorize(name, str(path)),
                triggers=triggers,
                estimated_duration_min=5.0,
                uses_cache=uses_cache,
                cache_keys=cache_keys[:5],
                dependencies=[],
                outputs=[],
                is_required="required" in content.lower(),  # nosec - YAML key detection
                approval_required=approval_required,
            )
        except (IOError, OSError):
            # Workflow parsing failed - skip this file
            return None

    def find_pending_approval_workflows(self) -> list[WorkflowInfo]:
        """Find workflows that require approval."""
        return [w for w in self._workflows.values() if w.approval_required]

    def get_workflows_by_category(self, category: WorkflowCategory) -> list[WorkflowInfo]:
        """Get workflows by category."""
        return [w for w in self._workflows.values() if w.category == category]


class CacheOptimizer:
    """Optimize workflow caching strategies."""

    def __init__(self) -> None:
        """Initialize optimizer."""
        self._cache_analysis: dict[str, Any] = {}

    def analyze_cache_usage(self, workflows: list[WorkflowInfo]) -> dict[str, Any]:
        """Analyze cache usage across workflows."""
        cache_users = [w for w in workflows if w.uses_cache]
        non_cache_users = [w for w in workflows if not w.uses_cache]

        # Find duplicate cache keys
        key_usage: dict[str, list[str]] = {}
        for workflow in cache_users:
            for key in workflow.cache_keys:
                key_usage.setdefault(key, []).append(workflow.name)

        shared_keys = {k: v for k, v in key_usage.items() if len(v) > 1}

        self._cache_analysis = {
            "total_workflows": len(workflows),
            "using_cache": len(cache_users),
            "not_using_cache": len(non_cache_users),
            "cache_adoption_rate": len(cache_users) / len(workflows) if workflows else 0,
            "unique_cache_keys": len(key_usage),
            "shared_cache_keys": shared_keys,
            "workflows_without_cache": [w.name for w in non_cache_users],
        }

        return self._cache_analysis

    def recommend_cache_improvements(
        self, workflows: list[WorkflowInfo]
    ) -> list[OptimizationRecommendation]:
        """Generate cache improvement recommendations."""
        recommendations = []

        if not self._cache_analysis:
            self.analyze_cache_usage(workflows)

        # Recommend adding cache to workflows without it
        no_cache = self._cache_analysis.get("workflows_without_cache", [])
        if no_cache:
            recommendations.append(
                OptimizationRecommendation(
                    optimization_type=OptimizationType.CACHING,
                    target_workflows=no_cache[:5],
                    description=f"Add caching to {len(no_cache)} workflows without cache",
                    estimated_savings_min=len(no_cache) * 2,  # ~2 min per workflow
                    priority=2,
                    implementation_effort="low",
                    code_changes=[
                        "Add actions/cache step for pip/npm/go dependencies",
                        "Use setup-python/setup-node with cache option",
                    ],
                )
            )

        # Recommend sharing cache keys
        shared = self._cache_analysis.get("shared_cache_keys", {})
        if shared:
            recommendations.append(
                OptimizationRecommendation(
                    optimization_type=OptimizationType.CACHING,
                    target_workflows=list({w for wl in shared.values() for w in wl})[:5],
                    description="Optimize shared cache keys for better hit rates",
                    estimated_savings_min=3,
                    priority=3,
                    implementation_effort="medium",
                    code_changes=[
                        "Standardize cache key patterns across workflows",
                        "Use restore-keys for fallback cache hits",
                    ],
                )
            )

        return recommendations


class RedundancyDetector:
    """Detect redundant workflows."""

    def find_similar_workflows(self, workflows: list[WorkflowInfo]) -> list[tuple[list[str], str]]:
        """Find workflows that might be duplicates."""
        similar_groups: list[tuple[list[str], str]] = []

        # Group by category
        by_category: dict[WorkflowCategory, list[WorkflowInfo]] = {}
        for w in workflows:
            by_category.setdefault(w.category, []).append(w)

        # Check for duplicates within category
        for category, group in by_category.items():
            if len(group) > 2:
                # Multiple workflows in same category
                names = [w.name for w in group]
                similar_groups.append((names, f"Multiple {category.value} workflows"))

        return similar_groups

    def recommend_consolidations(
        self, similar_groups: list[tuple[list[str], str]]
    ) -> list[OptimizationRecommendation]:
        """Generate consolidation recommendations."""
        recommendations = []

        for names, reason in similar_groups:
            if len(names) >= 3:
                recommendations.append(
                    OptimizationRecommendation(
                        optimization_type=OptimizationType.CONSOLIDATION,
                        target_workflows=names,
                        description=f"Consider consolidating: {reason}",
                        estimated_savings_min=len(names) * 3,
                        priority=2,
                        implementation_effort="high",
                        code_changes=[
                            "Create unified workflow with matrix strategy",
                            "Use reusable workflow template",
                            "Implement job-level conditions",
                        ],
                    )
                )

        return recommendations


class ImmutableRegistry:
    """Registry of immutable components."""

    def __init__(self, registry_path: Path | None = None):
        """Initialize registry."""
        self.registry_path = registry_path or Path(".codex/knowledge/immutable_registry.json")
        self._components: dict[str, ImmutableComponent] = {}
        self._load()

    def _load(self) -> None:
        """Load registry from disk."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    data = json.load(f)
                    for comp_data in data.get("components", []):
                        comp = ImmutableComponent(
                            component_id=comp_data["component_id"],
                            name=comp_data["name"],
                            path=comp_data["path"],
                            checksum=comp_data["checksum"],
                            verified_at=datetime.fromisoformat(comp_data["verified_at"]),
                            verified_by=comp_data["verified_by"],
                            reason=comp_data["reason"],
                        )
                        self._components[comp.component_id] = comp
            except (json.JSONDecodeError, KeyError):
                logger.debug("Suppressed exception in handler", exc_info=True)

    def save(self) -> None:
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump(
                {
                    "version": "1.0",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "components": [c.to_dict() for c in self._components.values()],
                },
                f,
                indent=2,
            )

    def register(
        self,
        name: str,
        path: str,
        checksum: str,
        verified_by: str,
        reason: str,
    ) -> ImmutableComponent:
        """Register an immutable component."""
        comp_id = f"IMM-{len(self._components) + 1:04d}"
        comp = ImmutableComponent(
            component_id=comp_id,
            name=name,
            path=path,
            checksum=checksum,
            verified_at=datetime.now(timezone.utc),
            verified_by=verified_by,
            reason=reason,
        )
        self._components[comp_id] = comp
        self.save()
        return comp

    def verify(self, component_id: str, current_checksum: str) -> bool:
        """Verify a component hasn't changed."""
        comp = self._components.get(component_id)
        if not comp:
            return False
        return comp.checksum == current_checksum

    def get_all(self) -> list[ImmutableComponent]:
        """Get all registered components."""
        return list(self._components.values())


class CheckpointManager:
    """Manage workflow checkpoints."""

    def __init__(self, checkpoint_path: Path | None = None):
        """Initialize manager."""
        self.checkpoint_path = checkpoint_path or Path(".codex/knowledge/checkpoints.json")
        self._checkpoints: dict[str, WorkflowCheckpoint] = {}
        self._load()

    def _load(self) -> None:
        """Load checkpoints from disk."""
        if self.checkpoint_path.exists():
            try:
                with open(self.checkpoint_path) as f:
                    data = json.load(f)
                    for cp_data in data.get("checkpoints", []):
                        cp = WorkflowCheckpoint(
                            checkpoint_id=cp_data["checkpoint_id"],
                            workflow_name=cp_data["workflow_name"],
                            step_name=cp_data["step_name"],
                            status=cp_data["status"],
                            created_at=datetime.fromisoformat(cp_data["created_at"]),
                            metadata=cp_data.get("metadata", {}),
                        )
                        self._checkpoints[cp.checkpoint_id] = cp
            except (json.JSONDecodeError, KeyError):
                logger.debug("Suppressed exception in handler", exc_info=True)

    def save(self) -> None:
        """Save checkpoints to disk."""
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_path, "w") as f:
            json.dump(
                {
                    "version": "1.0",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "checkpoints": [cp.to_dict() for cp in self._checkpoints.values()],
                },
                f,
                indent=2,
            )

    def create_checkpoint(
        self,
        workflow_name: str,
        step_name: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowCheckpoint:
        """Create a new checkpoint."""
        cp_id = f"CP-{len(self._checkpoints) + 1:05d}"
        cp = WorkflowCheckpoint(
            checkpoint_id=cp_id,
            workflow_name=workflow_name,
            step_name=step_name,
            status=status,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self._checkpoints[cp_id] = cp
        self.save()
        return cp

    def get_latest_checkpoint(self, workflow_name: str) -> WorkflowCheckpoint | None:
        """Get latest checkpoint for a workflow."""
        workflow_cps = [
            cp for cp in self._checkpoints.values() if cp.workflow_name == workflow_name
        ]
        if not workflow_cps:
            return None
        return max(workflow_cps, key=lambda x: x.created_at)

    def get_all_for_workflow(self, workflow_name: str) -> list[WorkflowCheckpoint]:
        """Get all checkpoints for a workflow."""
        return [cp for cp in self._checkpoints.values() if cp.workflow_name == workflow_name]


class WorkflowOptimizer:
    """Main class for workflow optimization."""

    def __init__(
        self,
        workflows_dir: Path | None = None,
        knowledge_dir: Path | None = None,
    ):
        """Initialize optimizer."""
        self.analyzer = WorkflowAnalyzer(workflows_dir)
        self.cache_optimizer = CacheOptimizer()
        self.redundancy_detector = RedundancyDetector()

        knowledge_dir = knowledge_dir or Path(".codex/knowledge")
        self.immutable_registry = ImmutableRegistry(knowledge_dir / "immutable_registry.json")
        self.checkpoint_manager = CheckpointManager(knowledge_dir / "checkpoints.json")

        self._workflows: list[WorkflowInfo] = []

    def scan(self) -> int:
        """Scan workflows and return count."""
        self._workflows = self.analyzer.scan_workflows()
        return len(self._workflows)

    def get_pending_approval_workflows(self) -> list[WorkflowInfo]:
        """Get workflows pending approval."""
        return self.analyzer.find_pending_approval_workflows()

    def analyze_all(self) -> dict[str, Any]:
        """Run full analysis."""
        if not self._workflows:
            self.scan()

        cache_analysis = self.cache_optimizer.analyze_cache_usage(self._workflows)
        similar_groups = self.redundancy_detector.find_similar_workflows(self._workflows)

        return {
            "total_workflows": len(self._workflows),
            "by_category": {
                cat.value: len(self.analyzer.get_workflows_by_category(cat))
                for cat in WorkflowCategory
            },
            "pending_approval": len(self.get_pending_approval_workflows()),
            "cache_analysis": cache_analysis,
            "similar_workflow_groups": len(similar_groups),
        }

    def get_recommendations(self) -> list[OptimizationRecommendation]:
        """Get all optimization recommendations."""
        if not self._workflows:
            self.scan()

        recommendations = []

        # Cache recommendations
        recommendations.extend(self.cache_optimizer.recommend_cache_improvements(self._workflows))

        # Consolidation recommendations
        similar = self.redundancy_detector.find_similar_workflows(self._workflows)
        recommendations.extend(self.redundancy_detector.recommend_consolidations(similar))

        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)

        return recommendations

    def register_immutable(
        self,
        name: str,
        path: str,
        checksum: str,
        verified_by: str,
        reason: str,
    ) -> ImmutableComponent:
        """Register an immutable component."""
        return self.immutable_registry.register(name, path, checksum, verified_by, reason)

    def create_checkpoint(
        self,
        workflow_name: str,
        step_name: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowCheckpoint:
        """Create a workflow checkpoint."""
        return self.checkpoint_manager.create_checkpoint(workflow_name, step_name, status, metadata)

    def get_optimization_report(self) -> str:
        """Generate a human-readable optimization report."""
        if not self._workflows:
            self.scan()

        analysis = self.analyze_all()
        recommendations = self.get_recommendations()

        lines = [
            "# Workflow Optimization Report",
            "",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total workflows:** {analysis['total_workflows']}",
            f"- **Pending approval:** {analysis['pending_approval']}",
            f"- **Similar groups:** {analysis['similar_workflow_groups']}",
            "",
            "## Category Distribution",
            "",
        ]

        for cat, count in analysis["by_category"].items():
            if count > 0:
                lines.append(f"- {cat}: {count}")

        lines.extend(["", "## Cache Analysis", ""])
        cache = analysis["cache_analysis"]
        lines.append(f"- Using cache: {cache.get('using_cache', 0)} workflows")
        lines.append(f"- Cache adoption: {cache.get('cache_adoption_rate', 0) * 100:.1f}%")

        if recommendations:
            lines.extend(["", "## Recommendations", ""])
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"### {i}. {rec.optimization_type.value.title()}")
                lines.append(f"**Target:** {', '.join(rec.target_workflows[:3])}")
                lines.append(f"**Description:** {rec.description}")
                lines.append(f"**Estimated savings:** {rec.estimated_savings_min} min")
                lines.append(f"**Effort:** {rec.implementation_effort}")
                lines.append("")

        return "\n".join(lines)
