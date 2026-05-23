"""
Mental Mapping Model with Stored Reasoning for Iterative Review and Self-Appraisal

This module implements a cognitive framework that:
1. Stores reasoning chains and decision paths
2. Creates mental maps of problem spaces
3. Enables iterative review and self-appraisal
4. Learns from past decisions to improve future choices

The mental map represents the agent's understanding of:
- Problem structure and relationships
- Solution pathways and their outcomes
- Reasoning chains that led to decisions
- Self-assessment of decision quality
"""

import json
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

# =============================================================================
# CLOCK ABSTRACTION
# =============================================================================


def _default_clock() -> str:
    """Default clock implementation using system time."""
    return datetime.now(UTC).isoformat()


# Module-level clock function that can be overridden for testing.
# Note: This is not thread-safe by design - it's intended for use in tests
# where a single test process controls the clock. For production multi-threaded
# environments, consider using dependency injection or a context manager.
_clock: Callable[[], str] = _default_clock


def set_clock(clock_fn: Callable[[], str]) -> None:
    """
    Set a custom clock function for timestamp generation.

    Useful for testing to provide deterministic timestamps.

    Note: This function is not thread-safe. It should only be used in
    single-threaded test environments or with proper synchronization.

    Args:
        clock_fn: A callable that returns an ISO format timestamp string.
    """
    global _clock
    _clock = clock_fn


def reset_clock() -> None:
    """
    Reset the clock to the default implementation.

    Note: This function is not thread-safe. It should only be used in
    single-threaded test environments or with proper synchronization.
    """
    global _clock
    _clock = _default_clock


def get_timestamp() -> str:
    """Get current timestamp using the configured clock."""
    return _clock()


class NodeType(Enum):
    """Types of nodes in the mental map"""

    PROBLEM = "problem"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    DECISION = "decision"
    ACTION = "action"
    OUTCOME = "outcome"
    REFLECTION = "reflection"
    LEARNING = "learning"
    CONCEPT = "concept"
    ENTITY = "entity"
    OBSERVATION = "observation"
    REASONING = "reasoning"
    SOLUTION = "solution"
    GOAL = "goal"
    CONSTRAINT = "constraint"


class EdgeType(Enum):
    """Types of relationships between nodes"""

    CAUSES = "causes"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONFLICTS_WITH = "conflicts_with"
    LEADS_TO = "leads_to"
    SIMILAR_TO = "similar_to"
    DEPENDS_ON = "depends_on"
    REFINES = "refines"
    VALIDATES = "validates"
    RELATED = "related"
    IMPLEMENTS = "implements"
    DERIVES_FROM = "derives_from"


@dataclass
class ReasoningStep:
    """A single step in a reasoning chain"""

    step_id: str
    timestamp: str = field(default_factory=get_timestamp)
    thought: str = ""
    description: str = ""  # Alias for thought
    reasoning_type: str = "deductive"  # deductive, inductive, abductive, analogical
    confidence: float = 0.5  # 0-1
    inputs: list[str] = field(default_factory=list)  # Alternative to alternatives_considered
    outputs: list[str] = field(default_factory=list)  # Alternative to evidence_used
    alternatives_considered: list[str] = field(default_factory=list)
    evidence_used: list[str] = field(default_factory=list)

    @property
    def evidence(self) -> list[str]:
        """Alias for evidence_used for backward compatibility."""
        return self.evidence_used

    @evidence.setter
    def evidence(self, value: list[str]) -> None:
        """Set evidence_used via evidence property."""
        self.evidence_used = value

    def __post_init__(self):
        """Handle parameter aliases and defaults"""
        # Use description if provided and thought is empty
        if self.description and not self.thought:
            self.thought = self.description
        # Use thought if description is empty
        elif self.thought and not self.description:
            self.description = self.thought

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MentalNode:
    """A node in the mental map representing a concept, decision, or observation"""

    node_id: str
    node_type: NodeType
    content: str
    timestamp: str

    # Reasoning metadata
    reasoning_chain: list[ReasoningStep] = field(default_factory=list)
    confidence: float = 0.5
    importance: float = 0.5

    # Self-appraisal
    quality_score: float = 0.0  # Self-assessed quality (0-1)
    needs_review: bool = False
    review_count: int = 0
    last_reviewed: Optional[str] = None

    # Learning
    was_correct: Optional[bool] = None  # Outcome validation
    lessons_learned: list[str] = field(default_factory=list)

    # Connections
    connected_nodes: set[str] = field(default_factory=set)

    # Metadata
    tags: list[str] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def add_reasoning_step(
        self,
        thought: str,
        reasoning_type: str,
        confidence: float,
        alternatives: list[str] = None,
        evidence: list[str] = None,
    ) -> ReasoningStep:
        """Add a reasoning step to this node's chain"""
        step = ReasoningStep(
            step_id=str(uuid.uuid4()),
            timestamp=get_timestamp(),
            thought=thought,
            reasoning_type=reasoning_type,
            confidence=confidence,
            alternatives_considered=alternatives or [],
            evidence_used=evidence or [],
        )
        self.reasoning_chain.append(step)
        return step

    def mark_for_review(self, reason: str = "low_confidence") -> None:
        """Mark this node as needing review"""
        self.needs_review = True
        self.context["review_reason"] = reason

    def review(self, new_quality_score: float, notes: str = "") -> None:
        """Conduct a review of this node"""
        self.quality_score = new_quality_score
        self.needs_review = False
        self.review_count += 1
        self.last_reviewed = get_timestamp()

        if notes:
            self.context["review_notes"] = self.context.get("review_notes", [])
            self.context["review_notes"].append({"timestamp": self.last_reviewed, "notes": notes})

    def add_lesson(self, lesson: str) -> None:
        """Record a lesson learned from this node"""
        self.lessons_learned.append({"timestamp": get_timestamp(), "lesson": lesson})

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        d = asdict(self)
        d["node_type"] = self.node_type.value
        d["connected_nodes"] = list(self.connected_nodes)
        return d

    def __hash__(self) -> int:
        """Make MentalNode hashable for use in sets and as dict keys."""
        return hash(self.node_id)

    def __eq__(self, other) -> bool:
        """Equality based on node_id."""
        if not isinstance(other, MentalNode):
            return False
        return self.node_id == other.node_id


@dataclass
class MentalEdge:
    """An edge connecting two nodes in the mental map"""

    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0  # Strength of relationship

    # Reasoning for this connection
    justification: str = ""
    evidence: list[str] = field(default_factory=list)

    # Validation
    validated: bool = False
    validation_date: Optional[str] = None

    @property
    def source(self) -> str:
        """Alias for source_id for backward compatibility."""
        return self.source_id

    @property
    def target(self) -> str:
        """Alias for target_id for backward compatibility."""
        return self.target_id

    def to_dict(self) -> dict:
        d = asdict(self)
        d["edge_type"] = self.edge_type.value if self.edge_type else None
        return d


class MentalMappingModel:
    """
    Mental Mapping Model for AI Agent Cognition

    Features:
    - Builds mental maps of problem spaces
    - Stores complete reasoning chains
    - Enables iterative review and self-appraisal
    - Learns from outcomes to improve future decisions
    - Tracks confidence and quality over time
    """

    def __init__(self, agent_id: str = "default_agent"):
        self.agent_id = agent_id
        self.map_id = str(uuid.uuid4())
        self.created_at = get_timestamp()

        # Mental map structure
        self.nodes: dict[str, MentalNode] = {}
        self.edges: dict[str, MentalEdge] = {}

        # Indexes for fast lookup
        self.nodes_by_type: dict[NodeType, set[str]] = {nt: set() for nt in NodeType}
        self.nodes_needing_review: set[str] = set()

        # Learning history
        self.learning_history: list[dict] = []
        self.pattern_library: dict[str, dict] = {}

        # Self-appraisal metrics
        self.appraisal_metrics = {
            "total_decisions": 0,
            "total_outcomes": 0,
            "correct_decisions": 0,
            "average_confidence": 0.0,
            "average_quality": 0.0,
            "review_rate": 0.0,
        }

    def create_node(
        self,
        node_type: NodeType,
        content: str = "",
        properties: Optional[dict] = None,
        confidence: float = 0.5,
        importance: float = 0.5,
        tags: Optional[list[str]] = None,
        context: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> MentalNode:
        """
        Create a new node in the mental map.

        Args:
            node_type: Type of node
            content: Node content (optional)
            properties: Alternative to explicit parameters (backward compat)
            confidence: Confidence level
            importance: Importance level
            tags: Tags list
            context: Context dict
            metadata: Metadata dict

        Returns:
            MentalNode object
        """
        # Handle properties parameter for backward compatibility
        if properties is not None:
            content = properties.get("content", content or f"{node_type.value}_node")
            confidence = properties.get("confidence", confidence)
            importance = properties.get("importance", importance)
            tags = properties.get("tags", tags)
            context = properties.get("context", context)
        else:
            if not content:
                content = f"{node_type.value}_node"

        node = MentalNode(
            node_id=str(uuid.uuid4()),
            node_type=node_type,
            content=content,
            timestamp=get_timestamp(),
            confidence=confidence,
            importance=importance,
            tags=tags or [],
            context=context or {},
            metadata=metadata or {},
        )

        self.nodes[node.node_id] = node
        self.nodes_by_type[node_type].add(node.node_id)

        # Auto-mark for review if confidence is low
        if confidence < 0.5:
            node.mark_for_review("low_confidence")
            self.nodes_needing_review.add(node.node_id)

        return node

    def create_node_id(
        self, node_type: NodeType, properties: Optional[dict] = None, **kwargs
    ) -> str:
        """
        Create a new node and return its ID (backward compatibility method).

        Args:
            node_type: Type of node
            properties: Properties dictionary with content, confidence, etc.
            **kwargs: Additional arguments passed to create_node

        Returns:
            Node ID string
        """
        node = self.create_node(node_type, properties=properties, **kwargs)
        return node.node_id

    def add_node(self, node: MentalNode) -> None:
        """
        Add a pre-created node to the mental map.

        Args:
            node: MentalNode instance to add
        """
        self.nodes[node.node_id] = node
        self.nodes_by_type[node.node_type].add(node.node_id)

        # Auto-mark for review if confidence is low
        if node.confidence < 0.5:
            node.mark_for_review("low_confidence")
            self.nodes_needing_review.add(node.node_id)

    def connect_nodes(
        self,
        source_id: str = None,
        target_id: str = None,
        source: str = None,  # Alias for source_id
        target: str = None,  # Alias for target_id
        edge_type: EdgeType = None,
        properties: dict = None,
        weight: float = 1.0,
        justification: str = "",
        evidence: list[str] = None,
    ) -> MentalEdge:
        """
        Create a connection between two nodes.

        Args:
            source_id: Source node ID (or MentalNode object)
            target_id: Target node ID (or MentalNode object)
            source: Alias for source_id
            target: Alias for target_id
            edge_type: Type of edge
            properties: Alternative parameter dict (backward compat)
            weight: Edge weight
            justification: Reasoning for connection
            evidence: Supporting evidence
        """
        # Handle MentalNode objects (extract node_id)
        if hasattr(source_id, 'node_id'):
            source_id = source_id.node_id
        if hasattr(target_id, 'node_id'):
            target_id = target_id.node_id

        # Handle parameter aliases
        if source and not source_id:
            source_id = source
        if target and not target_id:
            target_id = target

        # Handle properties parameter
        if properties is not None:
            weight = properties.get("weight", weight)
            justification = properties.get("justification", justification)
            evidence = properties.get("evidence", evidence)

        # Ensure node IDs are valid hashable keys for dict/set operations
        if not isinstance(source_id, str) or not isinstance(target_id, str):
            raise TypeError("source_id and target_id must be strings")

        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both nodes must exist in the map")

        edge = MentalEdge(
            edge_id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            justification=justification,
            evidence=evidence or [],
        )

        self.edges[edge.edge_id] = edge

        # Update node connections
        self.nodes[source_id].connected_nodes.add(target_id)
        self.nodes[target_id].connected_nodes.add(source_id)

        return edge

    def think_through_problem(
        self, problem: str, context: dict = None
    ) -> tuple[MentalNode, list[ReasoningStep]]:
        """
        Think through a problem, storing the complete reasoning chain

        Returns the problem node and the reasoning steps
        """
        print(f"\n{'='*60}")
        print("THINKING THROUGH PROBLEM")
        print(f"{'='*60}")
        print(f"Problem: {problem}")

        # Create problem node
        problem_node = self.create_node(
            node_type=NodeType.PROBLEM,
            content=problem,
            confidence=1.0,  # We're certain about the problem
            importance=0.9,
            tags=["active", "needs_solution"],
            context=context or {},
        )

        # Reasoning chain
        reasoning_steps = []

        # Step 1: Problem decomposition
        print("\n[Step 1] Decomposing problem...")
        step1 = problem_node.add_reasoning_step(
            thought="Decomposing the problem into sub-components",
            reasoning_type="deductive",
            confidence=0.8,
            alternatives=["solve_directly", "gather_more_info"],
            evidence=["problem_complexity", "available_resources"],
        )
        reasoning_steps.append(step1)
        print(f"  Thought: {step1.thought}")
        print(f"  Confidence: {step1.confidence}")

        # Step 2: Hypothesis generation
        print("\n[Step 2] Generating hypotheses...")
        hypothesis_node = self.create_node(
            node_type=NodeType.HYPOTHESIS,
            content=f"Potential solution approach for: {problem}",
            confidence=0.6,
            importance=0.7,
            tags=["hypothesis", "needs_validation"],
        )

        step2 = hypothesis_node.add_reasoning_step(
            thought="Considering multiple solution approaches based on similar past problems",
            reasoning_type="analogical",
            confidence=0.6,
            alternatives=["approach_a", "approach_b", "hybrid"],
            evidence=["past_experience", "domain_knowledge"],
        )
        reasoning_steps.append(step2)
        print(f"  Thought: {step2.thought}")
        print(f"  Confidence: {step2.confidence}")

        # Connect problem to hypothesis
        self.connect_nodes(
            problem_node.node_id,
            hypothesis_node.node_id,
            edge_type=EdgeType.LEADS_TO,
            weight=0.7,
            justification="Hypothesis generated from problem analysis",
        )

        # Step 3: Evidence gathering
        print("\n[Step 3] Gathering evidence...")
        evidence_node = self.create_node(
            node_type=NodeType.EVIDENCE,
            content="Evidence supporting hypothesis",
            confidence=0.7,
            importance=0.8,
            tags=["evidence", "validation"],
        )

        step3 = evidence_node.add_reasoning_step(
            thought="Collecting data and evidence to validate hypothesis",
            reasoning_type="inductive",
            confidence=0.7,
            alternatives=["quantitative_data", "qualitative_analysis"],
            evidence=["test_results", "audit_data", "metrics", "gathered_evidence"],
        )
        reasoning_steps.append(step3)
        print(f"  Thought: {step3.thought}")
        print(f"  Confidence: {step3.confidence}")

        # Connect hypothesis to evidence
        self.connect_nodes(
            hypothesis_node.node_id,
            evidence_node.node_id,
            edge_type=EdgeType.SUPPORTS,
            weight=0.8,
            justification="Evidence validates hypothesis",
        )

        print(f"\n✓ Problem thinking complete. Created {len(reasoning_steps)} reasoning steps.")

        return problem_node, reasoning_steps

    def make_decision(
        self,
        decision_content: str,
        problem_node_id: str,
        confidence: float,
        alternatives_considered: list[str],
        reasoning: str,
    ) -> MentalNode:
        """
        Make a decision and record the reasoning

        This creates a decision node connected to the problem
        """
        print(f"\n{'='*60}")
        print("MAKING DECISION")
        print(f"{'='*60}")
        print(f"Decision: {decision_content}")
        print(f"Confidence: {confidence:.2f}")

        # Create decision node
        decision_node = self.create_node(
            node_type=NodeType.DECISION,
            content=decision_content,
            confidence=confidence,
            importance=0.9,
            tags=["decision", "active"],
            context={"alternatives": alternatives_considered, "reasoning_summary": reasoning},
        )

        # Add reasoning step
        decision_node.add_reasoning_step(
            thought=reasoning,
            reasoning_type="deductive",
            confidence=confidence,
            alternatives=alternatives_considered,
            evidence=["analysis", "assessment"],
        )

        # Connect to problem
        self.connect_nodes(
            problem_node_id,
            decision_node.node_id,
            edge_type=EdgeType.LEADS_TO,
            weight=confidence,
            justification="Decision made to address problem",
        )

        # Update metrics
        self.appraisal_metrics["total_decisions"] += 1

        print(f"✓ Decision recorded with {len(alternatives_considered)} alternatives considered")

        return decision_node

    def record_outcome(
        self,
        decision_node_id: str,
        outcome_content: str,
        success: bool,
        actual_impact: float,
        learned_lessons: list[str] = None,
    ) -> MentalNode:
        """
        Record the outcome of a decision for learning

        Args:
            decision_node_id: ID of the decision node
            outcome_content: Description of the outcome
            success: Whether the decision was successful
            actual_impact: Numerical impact (0-1)
            learned_lessons: Optional list of lessons learned from this outcome
        """
        print(f"\n{'='*60}")
        print("RECORDING OUTCOME")
        print(f"{'='*60}")
        print(f"Outcome: {outcome_content}")
        print(f"Success: {success}")
        print(f"Impact: {actual_impact:.2f}")

        # Create outcome node
        outcome_context = {
            "success": success,
            "actual_impact": actual_impact,
        }
        if learned_lessons:
            outcome_context["learned_lessons"] = learned_lessons

        outcome_node = self.create_node(
            node_type=NodeType.OUTCOME,
            content=outcome_content,
            confidence=1.0,  # We're certain about what happened
            importance=actual_impact,
            tags=["outcome", "validated"],
            context=outcome_context,
        )

        # Add learned lessons to the node if provided
        if learned_lessons:
            for lesson in learned_lessons:
                outcome_node.add_lesson(lesson)

        # Connect to decision
        self.connect_nodes(
            decision_node_id,
            outcome_node.node_id,
            EdgeType.LEADS_TO,
            weight=1.0,
            justification="Outcome resulted from decision",
        )

        # Update decision node with outcome
        decision_node = self.nodes[decision_node_id]
        decision_node.was_correct = success

        # Update metrics
        self.appraisal_metrics["total_outcomes"] += 1
        if success:
            self.appraisal_metrics["correct_decisions"] += 1

        # Trigger self-appraisal
        self._self_appraise_decision(decision_node_id, outcome_node.node_id)

        print("✓ Outcome recorded and self-appraisal triggered")

        return outcome_node

    def _self_appraise_decision(self, decision_node_id: str, outcome_node_id: str) -> None:
        """
        Perform self-appraisal of a decision based on its outcome
        """
        print(f"\n{'='*60}")
        print("SELF-APPRAISAL")
        print(f"{'='*60}")

        decision_node = self.nodes[decision_node_id]
        outcome_node = self.nodes[outcome_node_id]

        # Create reflection node
        reflection_node = self.create_node(
            node_type=NodeType.REFLECTION,
            content=f"Reflecting on decision: {decision_node.content}",
            confidence=1.0,
            importance=0.8,
            tags=["reflection", "meta_cognition"],
        )

        # Analyze decision quality
        expected_confidence = decision_node.confidence
        actual_success = decision_node.was_correct
        actual_impact = outcome_node.importance

        # Calculate quality score
        # If we were confident and correct, high quality
        # If we were uncertain and correct, medium quality (got lucky)
        # If we were confident and wrong, low quality (overconfident)
        # If we were uncertain and wrong, medium quality (appropriately cautious)
        if actual_success:
            quality = 0.5 + (expected_confidence * 0.5)  # 0.5 to 1.0
        else:
            quality = 0.5 - (expected_confidence * 0.5)  # 0.0 to 0.5

        quality *= actual_impact  # Weight by impact

        decision_node.quality_score = quality

        print("Decision Quality Analysis:")
        print(f"  Expected Confidence: {expected_confidence:.2f}")
        print(f"  Actual Success: {actual_success}")
        print(f"  Actual Impact: {actual_impact:.2f}")
        print(f"  ⭐ Quality Score: {quality:.2f}")

        # Generate lessons learned
        lessons = []

        if actual_success and expected_confidence > 0.7:
            lessons.append("High confidence decision validated - good judgment")
        elif actual_success and expected_confidence < 0.5:
            lessons.append("Low confidence but succeeded - may need more confidence")
        elif not actual_success and expected_confidence > 0.7:
            lessons.append("Overconfident - need better assessment methods")
        elif not actual_success and expected_confidence < 0.5:
            lessons.append("Appropriately cautious - correct to be uncertain")

        # Check if alternatives would have been better
        if not actual_success:
            lessons.append(
                f"Explore alternative: {decision_node.context.get('alternatives', ['unknown'])[0]}"
            )

        for lesson in lessons:
            decision_node.add_lesson(lesson)
            print(f"  📚 Lesson: {lesson}")

        # Create a LEARNING node when there are lessons or the decision failed
        if lessons or not actual_success:
            learning_node = self.create_node(
                node_type=NodeType.LEARNING,
                content=f"Learning from {'failure' if not actual_success else 'experience'}: {decision_node.content}",
                confidence=0.9,
                importance=0.8,
                tags=["learning", "improvement"],
                context={"lessons": lessons, "success": actual_success},
            )
            self.connect_nodes(
                reflection_node.node_id,
                learning_node.node_id,
                EdgeType.LEADS_TO,
                weight=1.0,
                justification="Reflection leads to learning",
            )
            print(f"  🎓 Learning node created: {learning_node.node_id}")

        # Connect reflection to decision and outcome
        self.connect_nodes(
            decision_node_id,
            reflection_node.node_id,
            EdgeType.REFINES,
            weight=1.0,
            justification="Reflection on decision outcome",
        )

        self.connect_nodes(
            outcome_node_id,
            reflection_node.node_id,
            EdgeType.VALIDATES,
            weight=1.0,
            justification="Reflection validates outcome",
        )

        # Store in learning history
        self.learning_history.append(
            {
                "timestamp": get_timestamp(),
                "decision_id": decision_node_id,
                "outcome_id": outcome_node_id,
                "reflection_id": reflection_node.node_id,
                "quality_score": quality,
                "lessons": lessons,
                "success": actual_success,
            }
        )

        # Update appraisal metrics
        self._update_appraisal_metrics()

    def iterative_review(self, review_threshold: float = 0.5) -> list[str]:
        """
        Perform iterative review of nodes needing attention

        Returns list of node IDs that were reviewed
        """
        print(f"\n{'='*60}")
        print("ITERATIVE REVIEW")
        print(f"{'='*60}")
        print(f"Quality Threshold: {review_threshold:.2f}")

        # Find nodes needing review
        nodes_to_review = [
            node_id for node_id in self.nodes_needing_review if node_id in self.nodes
        ]

        # Also review nodes with needs_review flag set directly (e.g. externally)
        for node_id, node in self.nodes.items():
            if node.needs_review and node_id not in nodes_to_review:
                nodes_to_review.append(node_id)

        # Also review nodes with low quality scores
        for node_id, node in self.nodes.items():
            if node.quality_score < review_threshold and node.quality_score > 0:
                nodes_to_review.append(node_id)

        reviewed_nodes = []

        print(f"Found {len(nodes_to_review)} nodes to review")

        for node_id in nodes_to_review:
            node = self.nodes[node_id]

            print(f"\nReviewing: {node.node_type.value} - {node.content[:50]}...")
            print(f"  Current Quality: {node.quality_score:.2f}")
            print(f"  Confidence: {node.confidence:.2f}")
            print(f"  Review Count: {node.review_count}")

            # Perform review analysis
            review_notes = []

            # Check reasoning chain
            if len(node.reasoning_chain) == 0:
                review_notes.append("No reasoning chain - add explicit reasoning")

            # Check confidence calibration
            if node.was_correct is not None:
                if node.was_correct and node.confidence < 0.5:
                    review_notes.append("Under-confident - adjust confidence upward")
                elif not node.was_correct and node.confidence > 0.7:
                    review_notes.append("Over-confident - adjust confidence downward")

            # Check connections
            if len(node.connected_nodes) < 2:
                review_notes.append("Isolated node - consider more connections")

            # Calculate new quality score based on review
            improvement_factor = 0.1 * (node.review_count + 1)
            new_quality = min(node.quality_score + improvement_factor, 1.0)

            # Conduct review
            node.review(new_quality_score=new_quality, notes=" | ".join(review_notes))

            print(f"  New Quality: {new_quality:.2f}")
            print(f"  Notes: {review_notes}")

            reviewed_nodes.append(node_id)

            # Remove from review queue
            if node_id in self.nodes_needing_review:
                self.nodes_needing_review.remove(node_id)

        print(f"\n✓ Reviewed {len(reviewed_nodes)} nodes")

        return reviewed_nodes

    def _update_appraisal_metrics(self) -> None:
        """Update overall self-appraisal metrics"""
        total_decisions = self.appraisal_metrics["total_decisions"]

        if total_decisions > 0:
            # Accuracy rate
            self.appraisal_metrics["accuracy_rate"] = (
                self.appraisal_metrics["correct_decisions"] / total_decisions
            )

            # Average confidence
            confidences = [
                node.confidence
                for node in self.nodes.values()
                if node.node_type == NodeType.DECISION
            ]
            if confidences:
                self.appraisal_metrics["average_confidence"] = sum(confidences) / len(confidences)

            # Average quality
            qualities = [
                node.quality_score for node in self.nodes.values() if node.quality_score > 0
            ]
            if qualities:
                self.appraisal_metrics["average_quality"] = sum(qualities) / len(qualities)

            # Review rate
            reviewed = sum(1 for n in self.nodes.values() if n.review_count > 0)
            self.appraisal_metrics["review_rate"] = reviewed / len(self.nodes)

    def get_mental_map_summary(self) -> dict:
        """Get a summary of the mental map"""
        return {
            "map_id": self.map_id,
            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": {nt.value: len(ids) for nt, ids in self.nodes_by_type.items()},
            "nodes_needing_review": len(self.nodes_needing_review),
            "learning_history_size": len(self.learning_history),
            "appraisal_metrics": self.appraisal_metrics,
        }

    def visualize_reasoning_path(self, start_node_id: str, max_depth: int = 5) -> str:
        """Generate a text visualization of reasoning path from a node"""
        if start_node_id not in self.nodes:
            return "Node not found"

        visited = set()

        def traverse(node_id: str, depth: int = 0) -> list[str]:
            if depth >= max_depth or node_id in visited:
                return []

            visited.add(node_id)
            node = self.nodes[node_id]

            indent = "  " * depth
            lines = [f"{indent}[{node.node_type.value}] {node.content[:60]}..."]
            lines.append(
                f"{indent}  Confidence: {node.confidence:.2f} | Quality: {node.quality_score:.2f}"
            )

            # Show reasoning steps
            if node.reasoning_chain:
                lines.append(f"{indent}  Reasoning:")
                for step in node.reasoning_chain[:2]:  # Show first 2 steps
                    lines.append(f"{indent}    - {step.thought[:50]}...")

            # Traverse connected nodes
            for connected_id in node.connected_nodes:
                if connected_id not in visited:
                    # Find edge type
                    edge = next(
                        (
                            e
                            for e in self.edges.values()
                            if e.source_id == node_id and e.target_id == connected_id
                        ),
                        None,
                    )
                    if edge:
                        lines.append(f"{indent}  └─[{edge.edge_type.value}]→")
                        lines.extend(traverse(connected_id, depth + 1))

            return lines

        return "\n".join(traverse(start_node_id))

    def cluster_nodes(self, similarity_threshold: float = 0.7) -> dict[str, list[str]]:
        """
        Cluster nodes based on similarity of content and connections.

        Args:
            similarity_threshold: Minimum similarity to be in same cluster (0-1)

        Returns:
            Dictionary mapping cluster_id to list of node_ids
        """
        _ = similarity_threshold
        clusters = {}
        clustered_nodes = set()
        cluster_id = 0

        for node_id, node in self.nodes.items():
            if node_id in clustered_nodes:
                continue

            # Start new cluster
            cluster_key = f"cluster_{cluster_id}"
            clusters[cluster_key] = [node_id]
            clustered_nodes.add(node_id)

            # Find similar nodes
            for other_id, other_node in self.nodes.items():
                if other_id in clustered_nodes:
                    continue

                # Simple similarity: same type and connected
                if node.node_type == other_node.node_type and (
                    other_id in node.connected_nodes or node_id in other_node.connected_nodes
                ):
                    clusters[cluster_key].append(other_id)
                    clustered_nodes.add(other_id)

            cluster_id += 1

        return clusters

    def get_subgraph(self, node_ids: list[str] = None, nodes: list[str] = None) -> dict[str, Any]:
        """
        Extract a subgraph containing only specified nodes.

        Args:
            node_ids: list of node IDs to include in subgraph
            nodes: Alias for node_ids (backward compatibility)

        Returns:
            Dictionary with 'nodes' and 'edges' for the subgraph
        """
        # Handle parameter alias
        if nodes is not None and node_ids is None:
            node_ids = nodes

        if node_ids is None:
            node_ids = []

        node_id_set = set(node_ids)
        subgraph = {"nodes": {}, "edges": {}}

        # Add nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                subgraph["nodes"][node_id] = self.nodes[node_id].to_dict()

        # Add edges that connect nodes within the subgraph
        for edge_id, edge in self.edges.items():
            if edge.source_id in node_id_set and edge.target_id in node_id_set:
                subgraph["edges"][edge_id] = edge.to_dict()

        return subgraph

    def shortest_path(
        self,
        start_id: str = None,
        end_id: str = None,
        source: Union[str, "MentalNode"] = None,  # Alias for start_id, can be node or ID
        target: Union[str, "MentalNode"] = None,  # Alias for end_id, can be node or ID
    ) -> Optional[list[Union[str, "MentalNode"]]]:
        """
        Find shortest path between two nodes using BFS.

        Args:
            start_id: Starting node ID (string)
            end_id: Ending node ID (string)
            source: Alias for start_id (can be MentalNode object or string ID)
            target: Alias for end_id (can be MentalNode object or string ID)

        Returns:
            list of node IDs or MentalNode objects forming the path, or None if no path exists
        """
        # Handle parameter aliases and extract IDs from MentalNode objects
        return_nodes = False  # Track if we should return nodes or IDs

        if source is not None:
            if isinstance(source, MentalNode):
                start_id = source.node_id
                return_nodes = True
            else:
                start_id = source

        if target is not None:
            if isinstance(target, MentalNode):
                end_id = target.node_id
                return_nodes = True
            else:
                end_id = target

        if not start_id or not end_id:
            return None

        if start_id not in self.nodes or end_id not in self.nodes:
            return None

        # Special case: same node
        if start_id == end_id:
            if return_nodes:
                return [self.nodes[start_id]]
            return [start_id]

        # BFS to find shortest path
        from collections import deque

        queue = deque([(start_id, [start_id])])
        visited = {start_id}

        while queue:
            current_id, path = queue.popleft()
            current_node = self.nodes[current_id]

            for neighbor_id in current_node.connected_nodes:
                if neighbor_id == end_id:
                    final_path = path + [neighbor_id]
                    if return_nodes:
                        return [self.nodes[nid] for nid in final_path]
                    return final_path

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None  # No path found

    def bfs(self, start_node: str = None, start_id: str = None) -> list[str]:
        """
        Breadth-first search traversal from a starting node.

        Args:
            start_node: Starting node ID (primary parameter name)
            start_id: Alias for start_node

        Returns:
            list of node IDs in BFS order
        """
        # Handle parameter alias
        if start_id and not start_node:
            start_node = start_id

        if not start_node or start_node not in self.nodes:
            return []

        from collections import deque

        queue = deque([start_node])
        visited = {start_node}
        result = []

        while queue:
            current_id = queue.popleft()
            result.append(current_id)
            current_node = self.nodes[current_id]

            for neighbor_id in current_node.connected_nodes:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)

        return result

    def dfs(self, start_node: str = None, start_id: str = None) -> list[str]:
        """
        Depth-first search traversal from a starting node.

        Args:
            start_node: Starting node ID (primary parameter name)
            start_id: Alias for start_node

        Returns:
            list of node IDs in DFS order
        """
        # Handle parameter alias
        if start_id and not start_node:
            start_node = start_id

        if not start_node or start_node not in self.nodes:
            return []

        visited = set()
        result = []

        def dfs_recursive(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            result.append(node_id)

            current_node = self.nodes[node_id]
            for neighbor_id in current_node.connected_nodes:
                dfs_recursive(neighbor_id)

        dfs_recursive(start_node)
        return result

    def save_mental_map(self, output_path: Path) -> None:
        """Save the complete mental map to JSON"""
        data = {
            "map_id": self.map_id,
            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "edges": {eid: edge.to_dict() for eid, edge in self.edges.items()},
            "learning_history": self.learning_history,
            "appraisal_metrics": self.appraisal_metrics,
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n💾 Mental map saved to: {output_path}")

    def load_mental_map(self, input_path: Path) -> None:
        """Load a mental map from JSON"""
        with open(input_path) as f:
            data = json.load(f)

        self.map_id = data["map_id"]
        self.agent_id = data["agent_id"]
        self.created_at = data["created_at"]
        self.learning_history = data["learning_history"]
        self.appraisal_metrics = data["appraisal_metrics"]

        # Reconstruct nodes
        for node_data in data["nodes"].values():
            node_data["node_type"] = NodeType(node_data["node_type"])
            node_data["connected_nodes"] = set(node_data["connected_nodes"])
            # Reconstruct reasoning steps
            reasoning_chain = []
            for step_data in node_data["reasoning_chain"]:
                reasoning_chain.append(ReasoningStep(**step_data))
            node_data["reasoning_chain"] = reasoning_chain

            node = MentalNode(**node_data)
            self.nodes[node.node_id] = node
            self.nodes_by_type[node.node_type].add(node.node_id)

            if node.needs_review:
                self.nodes_needing_review.add(node.node_id)

        # Reconstruct edges
        for edge_data in data["edges"].values():
            edge_data["edge_type"] = EdgeType(edge_data["edge_type"]) if edge_data.get("edge_type") else None
            edge = MentalEdge(**edge_data)
            self.edges[edge.edge_id] = edge

        print(f"\n📂 Mental map loaded from: {input_path}")
        print(f"   Nodes: {len(self.nodes)}, Edges: {len(self.edges)}")

    def save(self, output_path: Path) -> None:
        """Alias for save_mental_map for backward compatibility."""
        return self.save_mental_map(output_path)

    def load(self, input_path: Path) -> None:
        """Alias for load_mental_map for backward compatibility."""
        return self.load_mental_map(input_path)

    def get_connected_nodes(self, node_id: str) -> list[MentalNode]:
        """
        Get all nodes connected to the specified node.

        Args:
            node_id: The ID of the node to get connections for

        Returns:
            List of MentalNode objects connected to this node
        """
        if node_id not in self.nodes:
            return []

        connected = []
        for edge in self.edges.values():
            if edge.source_id == node_id:
                if edge.target_id in self.nodes:
                    connected.append(self.nodes[edge.target_id])
            elif edge.target_id == node_id and edge.source_id in self.nodes:
                connected.append(self.nodes[edge.source_id])

        return connected

    def calculate_metrics(self) -> dict[str, Any]:
        """
        Calculate graph metrics for the mental map.

        Returns:
            Dictionary with graph metrics
        """
        return {
            "num_nodes": len(self.nodes),
            "num_edges": len(self.edges),
            "density": len(self.edges) / max(len(self.nodes) * (len(self.nodes) - 1) / 2, 1),
            "avg_degree": sum(len(n.connected_nodes) for n in self.nodes.values())
            / max(len(self.nodes), 1),
            "nodes_by_type": {node_type: len(ids) for node_type, ids in self.nodes_by_type.items()},
        }

    def get_node_centrality(self, node_id: str) -> float:
        """
        Calculate centrality score for a node (degree centrality).

        Args:
            node_id: Node ID to calculate centrality for

        Returns:
            Centrality score (0.0 to 1.0)
        """
        if node_id not in self.nodes:
            return 0.0

        node = self.nodes[node_id]
        num_nodes = len(self.nodes)

        if num_nodes <= 1:
            return 0.0

        # Degree centrality: connections / max possible connections
        return len(node.connected_nodes) / (num_nodes - 1)

    def to_dict(self) -> dict[str, Any]:
        """
        Export mental mapping model to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "map_id": self.map_id,
            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": {edge_id: edge.to_dict() for edge_id, edge in self.edges.items()},
            "learning_history": self.learning_history,
            "appraisal_metrics": self.appraisal_metrics,
            "pattern_library": self.pattern_library,
            "nodes_needing_review": list(self.nodes_needing_review),
        }


# Example usage
if __name__ == "__main__":
    # Create mental mapping model
    mental_map = MentalMappingModel(agent_id="codex_agent_001")

    print(f"\n{'#'*60}")
    print("# MENTAL MAPPING MODEL DEMONSTRATION")
    print(f"{'#'*60}")

    # Think through a problem
    problem_node, reasoning_steps = mental_map.think_through_problem(
        problem="Fix unused format arguments in visualization modules",
        context={"pr_number": 2459, "files_affected": 4},
    )

    # Make a decision
    decision_node = mental_map.make_decision(
        decision_content="Remove unused timestamp and version parameters",
        problem_node_id=problem_node.node_id,
        confidence=0.85,
        alternatives_considered=[
            "Add timestamp to templates",
            "Remove unused parameters",
            "Suppress warnings",
        ],
        reasoning="Code review indicated unused parameters. Removing is cleaner than adding to templates.",
    )

    # Simulate outcome
    mental_map.record_outcome(
        decision_node_id=decision_node.node_id,
        outcome_content="Code changes successful, tests pass, review comments resolved",
        success=True,
        actual_impact=0.8,
    )

    # Perform iterative review
    print(f"Reviewed nodes: {mental_map.iterative_review(review_threshold=0.6)}")

    # Show summary
    print(f"\n{'='*60}")
    print("MENTAL MAP SUMMARY")
    print(f"{'='*60}")
    summary = mental_map.get_mental_map_summary()
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    # Visualize reasoning path
    print(f"\n{'='*60}")
    print("REASONING PATH VISUALIZATION")
    print(f"{'='*60}")
    print(mental_map.visualize_reasoning_path(problem_node.node_id))

    # Save mental map
    output_path = Path("mental_map.json")
    mental_map.save_mental_map(output_path)

    print(f"\n{'#'*60}")
    print("# DEMONSTRATION COMPLETE")
    print(f"{'#'*60}")


# Create MentalMap as an alias for backward compatibility
# Many tests expect MentalMap class name
MentalMap = MentalMappingModel

# Additional alias for tests expecting 'MentalMapping' name
MentalMapping = MentalMappingModel
assert MentalMap and MentalMapping
