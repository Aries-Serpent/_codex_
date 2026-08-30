"""Adapter layer converting Phase 9.2 Cascade Orchestrator outputs to Phase 9.3
Semantic Router inputs.

This module implements bidirectional transformation between:

- Cascade orchestrator pattern detection → Semantic task specification
- Semantic router routing decisions → Cascade execution plans

Integration focuses on preserving cascade backward compatibility while leveraging
semantic routing for enhanced agent selection.

Author: Phase 9.2 ↔ 9.3 Integration
Date: 2026-06-26
"""

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PatternID(Enum):
    """Pattern identifiers from Phase 9.2 cascade orchestrator."""

    RP_001 = "RP-001"  # Unused Imports
    RP_002 = "RP-002"  # Type Annotations
    RP_003 = "RP-003"  # Test Assertions
    RP_004 = "RP-004"  # Dependency Conflicts
    RP_005 = "RP-005"  # YAML Formatting
    RP_006 = "RP-006"  # Coverage Thresholds
    RP_007 = "RP-007"  # Documentation Links
    RP_008 = "RP-008"  # Import Path Issues
    RP_009 = "RP-009"  # Flaky Tests
    RP_010 = "RP-010"  # Workflow Compliance
    RP_011 = "RP-011"  # Cargo Features
    RP_012 = "RP-012"  # CodeQL/Security


class TaskType(Enum):
    """Task type classifications for semantic router."""

    CI_FIX = "ci_fix"
    CODE_FIX = "code_fix"
    TEST_FIX = "test_fix"
    DEPENDENCY_FIX = "dependency_fix"
    YAML_FIX = "yaml_fix"
    COVERAGE_FIX = "coverage_fix"
    DOC_FIX = "doc_fix"
    IMPORT_FIX = "import_fix"
    FLAKY_FIX = "flaky_fix"
    WORKFLOW_FIX = "workflow_fix"
    CARGO_FIX = "cargo_fix"
    SECURITY_FIX = "security_fix"


class ExecutionStrategy(Enum):
    """Strategy for executing fix based on routing decision."""

    SEMANTIC_PRIMARY = "semantic"
    CASCADE_DEFAULT = "cascade_default"
    HYBRID = "hybrid"
    ESCALATE = "escalate"


# ============================================================================
# Phase 9.2 Cascade Orchestrator Data Structures
# ============================================================================


@dataclass
class PatternMatch:
    """Pattern detection result from cascade orchestrator.

    Attributes:
        pattern_id: RP-001 through RP-012
        pattern_name: Human-readable name
        confidence: Detection confidence (0.0-1.0)
        match_count: Number of pattern occurrences
        primary_regex: Matched regex signature
        error_context: Full error message snippet
        affected_files: Files where pattern detected
        extraction_metadata: Additional context from pattern match
        timestamp: ISO 8601 detection timestamp
    """

    pattern_id: str
    pattern_name: str
    confidence: float
    match_count: int
    primary_regex: str
    error_context: str
    affected_files: List[str]
    extraction_metadata: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatternMatch":
        """Create from dictionary representation."""
        return cls(**data)


@dataclass
class CascadeContext:
    """Context for cascade orchestrator execution.

    Attributes:
        session_id: Unique cascade session identifier
        pr_number: GitHub PR number
        failure_log: Full CI failure log text
        detected_patterns: List of detected patterns
        repository: Repository name (owner/repo)
        branch: Git branch name
        workflow_name: GitHub Actions workflow name
        run_id: GitHub Actions run ID
    """

    session_id: str
    pr_number: int
    failure_log: str
    detected_patterns: List[PatternMatch]
    repository: str
    branch: str
    workflow_name: str
    run_id: str


# ============================================================================
# Phase 9.3 Semantic Router Data Structures
# ============================================================================


@dataclass
class SemanticTask:
    """Task specification for semantic router.

    Attributes:
        id: Unique task identifier
        description: Natural language task description
        task_type: Semantic task classification
        priority: Priority level (high/medium/low)
        timeout_seconds: Maximum execution time
        required_capabilities: List of required capabilities
        excluded_agents: Agent IDs to exclude from routing
        max_concurrent_agents: Maximum parallel agents
        dependencies: Task IDs this depends on
        metadata: Additional context for routing decisions
    """

    id: str
    description: str
    task_type: str
    priority: str = "medium"
    timeout_seconds: int = 300
    required_capabilities: List[str] = field(default_factory=list)
    excluded_agents: List[str] = field(default_factory=list)
    max_concurrent_agents: int = 3
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class AgentAssignment:
    """Agent assignment from semantic router.

    Attributes:
        agent_id: Canonical agent identifier
        agent_name: Human-readable agent name
        rank: Assignment rank (0=primary, 1-2=fallback)
        similarity_score: Semantic similarity (0-1)
        confidence: Routing confidence (0-100)
        assignment_reason: Explanation for assignment
    """

    agent_id: str
    agent_name: str
    rank: int
    similarity_score: float
    confidence: float
    assignment_reason: str


@dataclass
class RoutingDecision:
    """Routing decision from semantic router.

    Attributes:
        task_id: Task being routed
        assigned_agents: List of all assignments (ranked)
        primary_agent: Best match agent
        fallback_chain: Backup agents
        confidence_score: Overall confidence (0-100)
        latency_ms: Router latency
        cache_hit: Whether decision was cached
    """

    task_id: str
    assigned_agents: List[AgentAssignment]
    primary_agent: AgentAssignment
    fallback_chain: List[AgentAssignment]
    confidence_score: float
    latency_ms: float
    cache_hit: bool


# ============================================================================
# Adapter Output Data Structures
# ============================================================================


@dataclass
class SemanticRoutingResult:
    """Result of semantic routing adapter transformation.

    Attributes:
        pattern_id: Original cascade pattern ID
        primary_agent: Top router match
        fallback_agents: Semantic router fallback chain
        semantic_confidence: Router confidence (0-100)
        cascade_default_agent: Cascade default agent for pattern
        override_default_routing: Use semantic routing instead of default
        execution_strategy: How to execute (semantic/default/hybrid)
        reasoning: Explanation for routing decision
        latency_ms: Total transformation + routing time
        routing_decision: Full routing decision from router
    """

    pattern_id: str
    primary_agent: Optional[str]
    fallback_agents: List[str]
    semantic_confidence: float
    cascade_default_agent: str
    override_default_routing: bool
    execution_strategy: ExecutionStrategy
    reasoning: str
    latency_ms: float
    routing_decision: Optional[RoutingDecision] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        data["execution_strategy"] = self.execution_strategy.value
        return data


@dataclass
class EscalationMetadata:
    """Metadata for escalation from cascade to semantic router.

    Used when cascade orchestrator experiences failure and needs to
    escalate to semantic router for alternative agent selection.

    Attributes:
        original_pattern: Failed pattern ID
        cascade_error: Error message from cascade
        cascade_confidence: Original pattern confidence
        failed_agent: Agent that failed
        attempt_count: Number of attempts made
        max_attempts: Maximum allowed attempts
        available_fallbacks: Cascade fallback options
        should_use_semantic_router: Whether to try semantic routing
        requested_priority: Task priority level
    """

    original_pattern: str
    cascade_error: str
    cascade_confidence: float
    failed_agent: str
    attempt_count: int
    max_attempts: int
    available_fallbacks: List[str]
    should_use_semantic_router: bool
    requested_priority: str


# ============================================================================
# Cascade to Router Adapter
# ============================================================================


class CascadeToRouterAdapter:
    """Adapter converting Phase 9.2 cascade outputs to Phase 9.3 router inputs.

    This adapter handles:
    - PatternMatch → SemanticTask transformation
    - Capability extraction from patterns
    - Schema validation
    - Backward compatibility with cascade default routing
    """

    # Pattern to task type mapping
    PATTERN_TO_TASK_TYPE: Dict[str, TaskType] = {
        "RP-001": TaskType.CI_FIX,
        "RP-002": TaskType.CODE_FIX,
        "RP-003": TaskType.TEST_FIX,
        "RP-004": TaskType.DEPENDENCY_FIX,
        "RP-005": TaskType.YAML_FIX,
        "RP-006": TaskType.COVERAGE_FIX,
        "RP-007": TaskType.DOC_FIX,
        "RP-008": TaskType.IMPORT_FIX,
        "RP-009": TaskType.FLAKY_FIX,
        "RP-010": TaskType.WORKFLOW_FIX,
        "RP-011": TaskType.CARGO_FIX,
        "RP-012": TaskType.SECURITY_FIX,
    }

    # Pattern to cascade default agent mapping
    PATTERN_TO_DEFAULT_AGENT: Dict[str, str] = {
        "RP-001": "ci-auto-healer-agent",
        "RP-002": "python-312-type-fixer",
        "RP-003": "autonomous-test-healer-agent",
        "RP-004": "dependency-conflict-agent",
        "RP-005": "workflow-ci-fixer",
        "RP-006": "unified-coverage-agent",
        "RP-007": "link-validator-agent",
        "RP-008": "ci-importerror-agent",
        "RP-009": "autonomous-test-healer-agent",
        "RP-010": "workflow-compliance-guardian",
        "RP-011": "ci-testing-agent",
        "RP-012": "code-scanning-remediation-agent",
    }

    # Pattern to required capabilities mapping
    PATTERN_TO_CAPABILITIES: Dict[str, List[str]] = {
        "RP-001": ["import_analysis", "linting", "code_modification"],
        "RP-002": ["type_checking", "python_312_compat", "mypy"],
        "RP-003": ["test_execution", "assertion_analysis", "pytest"],
        "RP-004": ["pip_resolution", "version_pinning", "constraint_analysis"],
        "RP-005": ["yaml_parsing", "indentation_fixing", "yamllint"],
        "RP-006": ["coverage_analysis", "test_writing", "threshold_adjustment"],
        "RP-007": ["link_validation", "documentation_management", "path_resolution"],
        "RP-008": [
            "sys_path_manipulation",
            "p19_shadow_detection",
            "import_analysis",
        ],
        "RP-009": ["test_execution", "timing_analysis", "test_stabilization"],
        "RP-010": ["yaml_validation", "workflow_compliance", "concurrency_config"],
        "RP-011": ["rust_compilation", "feature_config", "cargo_analysis"],
        "RP-012": ["code_scanning", "security_remediation", "sast_analysis"],
    }

    def __init__(self):
        """Initialize adapter."""
        self.transforms_total = 0
        self.validation_failures = 0

    def transform_pattern_to_task(
        self, pattern: PatternMatch, context: CascadeContext
    ) -> Tuple[Optional[SemanticTask], bool]:
        """Transform cascade pattern detection to semantic router task.

        Args:
            pattern: PatternMatch from cascade orchestrator
            context: CascadeContext with metadata

        Returns:
            Tuple of (SemanticTask, validation_success)
        """
        self.transforms_total += 1

        # Validate input
        if not self._validate_pattern_match(pattern):
            self.validation_failures += 1
            logger.error(f"Invalid PatternMatch for {pattern.pattern_id}")
            return None, False

        try:
            # Build semantic description
            description = self._build_task_description(pattern, context)

            # Extract required capabilities
            capabilities = self.PATTERN_TO_CAPABILITIES.get(pattern.pattern_id, []).copy()

            # Identify agents to exclude
            excluded = self._identify_excluded_agents(pattern.pattern_id)

            # Create semantic task
            task = SemanticTask(
                id=f"cascade_{context.session_id}_{pattern.pattern_id}",
                description=description,
                task_type=self.PATTERN_TO_TASK_TYPE[pattern.pattern_id].value,
                priority=self._map_priority(pattern.confidence),
                timeout_seconds=300,
                required_capabilities=capabilities,
                excluded_agents=excluded,
                max_concurrent_agents=3,
                dependencies=[],
                metadata={
                    "cascade_session_id": context.session_id,
                    "pattern_id": pattern.pattern_id,
                    "pattern_name": pattern.pattern_name,
                    "pattern_confidence": pattern.confidence,
                    "pr_number": context.pr_number,
                    "repository": context.repository,
                    "branch": context.branch,
                    "affected_files": pattern.affected_files,
                    "match_count": pattern.match_count,
                    "original_error": pattern.error_context[:500],
                    "workflow_name": context.workflow_name,
                    "run_id": context.run_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            )

            # Validate output
            if not self._validate_semantic_task(task):
                self.validation_failures += 1
                logger.error(f"Invalid SemanticTask generated for {pattern.pattern_id}")
                return None, False

            logger.info(f"Transformed {pattern.pattern_id} to semantic task")
            return task, True

        except Exception as e:
            self.validation_failures += 1
            logger.error(f"Transformation failed for {pattern.pattern_id}: {e}")
            return None, False

    def transform_routing_decision(
        self, routing_decision: RoutingDecision, pattern_id: str, context: CascadeContext
    ) -> SemanticRoutingResult:
        """Transform semantic router decision to cascade execution plan.

        Args:
            routing_decision: RoutingDecision from semantic router
            pattern_id: Original cascade pattern ID
            context: CascadeContext with metadata

        Returns:
            SemanticRoutingResult with execution strategy
        """
        cascade_default_agent = self.PATTERN_TO_DEFAULT_AGENT.get(pattern_id, "unknown")

        primary_agent = (
            routing_decision.primary_agent.agent_id if routing_decision.primary_agent else None
        )
        fallback_agents = [agent.agent_id for agent in routing_decision.fallback_chain]

        # Determine execution strategy
        strategy = self._determine_execution_strategy(
            routing_decision.confidence_score,
            cascade_default_agent,
            primary_agent,
        )

        # Build reasoning
        reasoning = self._build_reasoning(
            pattern_id,
            routing_decision.confidence_score,
            cascade_default_agent,
            primary_agent,
            strategy,
        )

        return SemanticRoutingResult(
            pattern_id=pattern_id,
            primary_agent=primary_agent,
            fallback_agents=fallback_agents,
            semantic_confidence=routing_decision.confidence_score,
            cascade_default_agent=cascade_default_agent,
            override_default_routing=strategy == ExecutionStrategy.SEMANTIC_PRIMARY,
            execution_strategy=strategy,
            reasoning=reasoning,
            latency_ms=routing_decision.latency_ms,
            routing_decision=routing_decision,
        )

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_pattern_match(self, pattern: PatternMatch) -> bool:
        """Validate cascade pattern match structure.

        Args:
            pattern: PatternMatch to validate

        Returns:
            True if valid, False otherwise
        """
        checks = [
            pattern.pattern_id in self.PATTERN_TO_TASK_TYPE,
            0.0 <= pattern.confidence <= 1.0,
            isinstance(pattern.match_count, int) and pattern.match_count > 0,
            len(pattern.error_context) > 0,
            isinstance(pattern.affected_files, list) and len(pattern.affected_files) > 0,
            isinstance(pattern.timestamp, str) and "T" in pattern.timestamp,
        ]

        valid = all(checks)
        if not valid:
            logger.warning(f"Pattern validation failed: {pattern.pattern_id}")
            logger.debug(f"  Checks: {checks}")
        return valid

    def _validate_semantic_task(self, task: SemanticTask) -> bool:
        """Validate semantic task structure.

        Args:
            task: SemanticTask to validate

        Returns:
            True if valid, False otherwise
        """
        checks = [
            len(task.id) > 0,
            len(task.description) > 10,
            task.task_type in [tt.value for tt in TaskType],
            task.priority in ["high", "medium", "low"],
            0 <= task.timeout_seconds <= 3600,
            all(cap in self._get_valid_capabilities() for cap in task.required_capabilities),
            len(task.required_capabilities) > 0,
            "cascade_session_id" in task.metadata,
            "pattern_id" in task.metadata,
        ]

        valid = all(checks)
        if not valid:
            logger.warning(f"Task validation failed: {task.id}")
            logger.debug(f"  Checks: {checks}")
        return valid

    # ========================================================================
    # Transformation Helper Methods
    # ========================================================================

    def _build_task_description(self, pattern: PatternMatch, context: CascadeContext) -> str:
        """Build natural language task description from pattern.

        Args:
            pattern: PatternMatch to describe
            context: CascadeContext for additional context

        Returns:
            Natural language task description
        """
        return f"""Detect and remediate CI failure: {pattern.pattern_name}

Pattern Type: {pattern.pattern_id}
Detection Confidence: {pattern.confidence:.1%}
Match Count: {pattern.match_count}

Affected Files ({len(pattern.affected_files)} total):
{', '.join(pattern.affected_files[:5])}{'...' if len(pattern.affected_files) > 5 else ''}

Error Context:
{pattern.error_context[:300]}

Repository: {context.repository}
Branch: {context.branch}
PR: #{context.pr_number}
Workflow: {context.workflow_name}

Required Actions:
1. Analyze the failure pattern
2. Determine root cause
3. Apply targeted fix
4. Validate with tests
5. Update PR with results"""

    def _map_priority(self, confidence: float) -> str:
        """Map pattern confidence to task priority.

        Args:
            confidence: Pattern confidence (0-1)

        Returns:
            Priority level (high/medium/low)
        """
        if confidence > 0.85:
            return "high"
        elif confidence > 0.70:
            return "medium"
        else:
            return "low"

    def _identify_excluded_agents(self, pattern_id: str) -> List[str]:
        """Identify agents to exclude from routing.

        Certain agents should not be used for specific patterns due to
        conflicts or incompatibilities.

        Args:
            pattern_id: Pattern identifier

        Returns:
            List of agent IDs to exclude
        """
        # Security patterns should not go to test agents
        if pattern_id == "RP-012":
            return ["ci-testing-agent", "autonomous-test-healer-agent"]

        # Type annotation patterns should not go to YAML agents
        if pattern_id == "RP-002":
            return ["workflow-ci-fixer", "workflow-compliance-guardian"]

        return []

    def _determine_execution_strategy(
        self,
        semantic_confidence: float,
        cascade_default_agent: str,
        semantic_primary_agent: Optional[str],
    ) -> ExecutionStrategy:
        """Determine execution strategy based on router confidence.

        Args:
            semantic_confidence: Router confidence (0-100)
            cascade_default_agent: Cascade default agent for pattern
            semantic_primary_agent: Semantic router primary agent

        Returns:
            ExecutionStrategy to use
        """
        # If semantic confidence is very high, use semantic routing
        if semantic_confidence >= 85 and semantic_primary_agent:
            return ExecutionStrategy.SEMANTIC_PRIMARY

        # If semantic confidence is good, hybrid with fallback to default
        if semantic_confidence >= 70 and semantic_primary_agent:
            return ExecutionStrategy.HYBRID

        # If semantic confidence is too low, use cascade default
        if semantic_confidence < 60:
            return ExecutionStrategy.CASCADE_DEFAULT

        # If no semantic primary agent available, escalate
        if not semantic_primary_agent:
            return ExecutionStrategy.ESCALATE

        # Default to hybrid
        return ExecutionStrategy.HYBRID

    def _build_reasoning(
        self,
        pattern_id: str,
        semantic_confidence: float,
        cascade_default_agent: str,
        semantic_primary_agent: Optional[str],
        strategy: ExecutionStrategy,
    ) -> str:
        """Build reasoning explanation for routing decision.

        Args:
            pattern_id: Pattern ID
            semantic_confidence: Semantic router confidence
            cascade_default_agent: Default agent for pattern
            semantic_primary_agent: Selected semantic agent
            strategy: Chosen execution strategy

        Returns:
            Reasoning explanation string
        """
        if strategy == ExecutionStrategy.SEMANTIC_PRIMARY:
            return (
                f"High confidence semantic match ({semantic_confidence:.1f}%) "
                f"to {semantic_primary_agent} for {pattern_id}"
            )
        elif strategy == ExecutionStrategy.HYBRID:
            return (
                f"Medium confidence semantic match ({semantic_confidence:.1f}%) "
                f"to {semantic_primary_agent}, fallback available"
            )
        elif strategy == ExecutionStrategy.CASCADE_DEFAULT:
            return (
                f"Low semantic confidence ({semantic_confidence:.1f}%), "
                f"using cascade default {cascade_default_agent}"
            )
        else:
            return f"Escalation required for {pattern_id} (no suitable agent found)"

    def _get_valid_capabilities(self) -> set:
        """Get set of all valid capabilities across all patterns.

        Returns:
            Set of valid capability strings
        """
        all_capabilities = set()
        for capabilities in self.PATTERN_TO_CAPABILITIES.values():
            all_capabilities.update(capabilities)
        return all_capabilities

    # ========================================================================
    # Statistics & Metrics
    # ========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """Get adapter metrics and statistics.

        Returns:
            Dictionary with adapter performance metrics
        """
        failure_rate = (
            (self.validation_failures / self.transforms_total * 100)
            if self.transforms_total > 0
            else 0
        )

        return {
            "transforms_total": self.transforms_total,
            "validation_failures": self.validation_failures,
            "validation_failure_rate": failure_rate,
            "success_rate": 100 - failure_rate,
        }


# ============================================================================
# Escalation Handler
# ============================================================================


class CascadeEscalationHandler:
    """Handles escalation from cascade orchestrator to semantic router.

    When cascade orchestrator encounters failures, this handler determines
    whether to escalate to semantic router for alternative agent selection.
    """

    # Escalation thresholds
    ESCALATE_IF_CONFIDENCE_ABOVE = 0.70
    CASCADE_FAILED_THRESHOLD = 1
    ATTEMPT_EXHAUSTION_THRESHOLD = 3

    def should_escalate_to_semantic(self, metadata: EscalationMetadata) -> bool:
        """Determine if cascade failure should be escalated to semantic router.

        Args:
            metadata: EscalationMetadata with failure context

        Returns:
            True if should escalate, False otherwise
        """
        checks = [
            metadata.cascade_confidence >= self.ESCALATE_IF_CONFIDENCE_ABOVE,
            metadata.attempt_count >= self.CASCADE_FAILED_THRESHOLD,
            metadata.attempt_count < metadata.max_attempts,
            metadata.should_use_semantic_router,
        ]

        return all(checks)

    def should_escalate_to_human(self, metadata: EscalationMetadata) -> bool:
        """Determine if cascade failure should be escalated to human review.

        Args:
            metadata: EscalationMetadata with failure context

        Returns:
            True if should escalate, False otherwise
        """
        checks = [
            metadata.attempt_count >= metadata.max_attempts,
            metadata.cascade_confidence >= 0.50,
        ]

        return all(checks)
