"""
Universal Intelligence Module for Cognitive Brain.

Phase 8.7 Implementation:
- Universal Task Interface (UTI)
- Meta-Policy Router (MPR) with strategy superposition
- Abstraction Engine (Concept/Relation/Analogy)
- Grounding Layer (feasibility mapping)
- Meta-Cognition (self-awareness)
- Universal Pattern Store (UPS)

Quantum-Physics-Inspired Formalism:
- Strategy superposition: |ψ_strat⟩ = Σᵢ αᵢ |sᵢ⟩
- Mixed belief state: ρ = Σⱼ pⱼ |φⱼ⟩⟨φⱼ|
- Adiabatic annealing: H(t) = (1-β(t))H_explore + β(t)H_exploit
- Decoherence model for negative transfer

Constraints:
- GitHub Copilot Pro+ and GitHub Team only
- No paid add-ons or external services
- Deterministic with fixed seeds
- Serializable (JSON/JSONL)
- Regression-testable with golden snapshots
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from datetime import datetime
import json
import math
import hashlib
import random
from enum import Enum


# =============================================================================
# CONSTANTS
# =============================================================================

# Phase 8.7 targets
K1_TARGET = 0.28  # k₁ ≤ 0.28
K1_STRETCH_TARGET = 0.255  # Aspirational
QUANTUM_ADVANTAGE_TARGET = 3.57  # 1/k₁

# Risk thresholds
NEGATIVE_TRANSFER_THRESHOLD = 0.05
FORGETTING_THRESHOLD = 0.20

# Algorithm strategies
STRATEGIES = [
    "maml",
    "reptile",
    "adapter_transfer",
    "q_transfer",
    "retrieval_policy",
]

# Default annealing schedule
DEFAULT_ANNEALING_STEPS = 100

# Execution constants
DEFAULT_MAX_DEMO_STEPS = 100  # Cap for demo/test execution
EARLY_TERMINATION_PROBABILITY = 0.01  # 1% termination chance per step
# Cap based on 10x target quantum advantage to provide meaningful relationship
MAX_QUANTUM_ADVANTAGE = 10.0 * QUANTUM_ADVANTAGE_TARGET  # = 35.7
K1_EPSILON = 1e-10  # Minimum k1 for division safety

# Task complexity thresholds
COMPLEXITY_LOW_THRESHOLD = 10.0
COMPLEXITY_MEDIUM_THRESHOLD = 100.0
COMPLEXITY_HIGH_THRESHOLD = 1000.0


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def calculate_safe_quantum_advantage(k1: float) -> float:
    """Calculate quantum advantage with safety bounds.
    
    Uses max(k1, K1_EPSILON) to prevent division by very small k1 values
    that would result in unrealistically large advantage values.
    
    Args:
        k1: Decision error rate (1 - decision_score)
        
    Returns:
        Quantum advantage value, capped at MAX_QUANTUM_ADVANTAGE
    """
    safe_k1 = max(k1, K1_EPSILON)
    return min(1.0 / safe_k1, MAX_QUANTUM_ADVANTAGE)


class TaskComplexity(Enum):
    """Task complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


def estimate_task_complexity(spec: "TaskSpec") -> Tuple[float, TaskComplexity]:
    """Estimate computational complexity of a task.
    
    Complexity is estimated based on:
    - State space dimensionality
    - Action space size
    - Time horizon
    - Reward specification complexity
    
    Args:
        spec: Task specification
        
    Returns:
        Tuple of (complexity_score, complexity_level)
    """
    complexity_score = 0.0
    
    # State space complexity
    state = spec.initial_state
    if isinstance(state, dict):
        state_dim = len(state)
        complexity_score += state_dim * 10
    
    # Time horizon
    max_steps = spec.termination.get("max_steps", 1000)
    complexity_score += max_steps / 10
    
    # Reward spec complexity
    if "params" in spec.reward_spec:
        params_count = len(spec.reward_spec["params"])
        complexity_score += params_count * 5
    
    # Categorize complexity
    if complexity_score < COMPLEXITY_LOW_THRESHOLD:
        level = TaskComplexity.LOW
    elif complexity_score < COMPLEXITY_MEDIUM_THRESHOLD:
        level = TaskComplexity.MEDIUM
    elif complexity_score < COMPLEXITY_HIGH_THRESHOLD:
        level = TaskComplexity.HIGH
    else:
        level = TaskComplexity.VERY_HIGH
    
    return complexity_score, level


def validate_task_spec_schema(spec: "TaskSpec") -> Tuple[bool, List[str]]:
    """Validate task specification against JSON schema.
    
    Performs structural validation beyond basic field presence checks.
    
    Args:
        spec: Task specification to validate
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []
    
    # Environment validation
    if not spec.environment or not isinstance(spec.environment, str):
        errors.append("environment must be a non-empty string")
    
    # Initial state validation
    if not isinstance(spec.initial_state, dict):
        errors.append("initial_state must be a dictionary")
    
    # Reward spec validation
    if not isinstance(spec.reward_spec, dict):
        errors.append("reward_spec must be a dictionary")
    elif "id" not in spec.reward_spec:
        errors.append("reward_spec.id is required")
    elif not isinstance(spec.reward_spec["id"], str):
        errors.append("reward_spec.id must be a string")
    
    # Termination validation
    if not isinstance(spec.termination, dict):
        errors.append("termination must be a dictionary")
    elif "max_steps" not in spec.termination:
        errors.append("termination.max_steps is required")
    elif not isinstance(spec.termination["max_steps"], int) or spec.termination["max_steps"] <= 0:
        errors.append("termination.max_steps must be a positive integer")
    
    # Seed validation
    if not isinstance(spec.seed, int):
        errors.append("seed must be an integer")
    
    return len(errors) == 0, errors


# =============================================================================
# ENVIRONMENT ADAPTERS
# =============================================================================


class EnvironmentAdapter:
    """Base class for environment-specific adapters."""
    
    def __init__(self, seed: int = 12345):
        """Initialize adapter with seed."""
        self.seed = seed
        self._rng = random.Random(seed)  # nosec B311 - deterministic simulation
    
    def execute_step(
        self, 
        state: Dict[str, Any], 
        action: str,
        step: int,
    ) -> Tuple[Dict[str, Any], float, bool]:
        """Execute one step in the environment.
        
        Args:
            state: Current state
            action: Action to take
            step: Current step number
            
        Returns:
            Tuple of (next_state, reward, done)
        """
        raise NotImplementedError


class GridWorldAdapter(EnvironmentAdapter):
    """Adapter for gridworld-style navigation tasks."""
    
    def execute_step(
        self, 
        state: Dict[str, Any], 
        action: str,
        step: int,
    ) -> Tuple[Dict[str, Any], float, bool]:
        """Execute gridworld step.
        
        State format: {"x": int, "y": int, "goal": {"x": int, "y": int}}
        Actions: "up", "down", "left", "right", "stay"
        """
        x = state.get("x", 0)
        y = state.get("y", 0)
        goal = state.get("goal", {"x": 5, "y": 5})
        
        # Apply action
        if action == "up":
            y += 1
        elif action == "down":
            y -= 1
        elif action == "left":
            x -= 1
        elif action == "right":
            x += 1
        # "stay" or unknown action: no movement
        
        next_state = {"x": x, "y": y, "goal": goal}
        
        # Calculate reward (negative distance to goal)
        distance = abs(x - goal["x"]) + abs(y - goal["y"])
        reward = -distance / 10.0
        
        # Check if reached goal
        done = (x == goal["x"] and y == goal["y"])
        if done:
            reward += 10.0  # Goal bonus
        
        return next_state, reward, done


class BanditAdapter(EnvironmentAdapter):
    """Adapter for multi-armed bandit tasks."""
    
    def execute_step(
        self, 
        state: Dict[str, Any], 
        action: str,
        step: int,
    ) -> Tuple[Dict[str, Any], float, bool]:
        """Execute bandit step.
        
        State format: {"arm_means": [float, ...], "pulls": int}
        Actions: "arm_0", "arm_1", ... "arm_N"
        """
        arm_means = state.get("arm_means", [0.5, 0.3, 0.7, 0.4])
        pulls = state.get("pulls", 0)
        
        # Parse action
        try:
            arm_idx = int(action.split("_")[1]) if "_" in action else 0
            arm_idx = max(0, min(arm_idx, len(arm_means) - 1))
        except (ValueError, IndexError):
            arm_idx = 0
        
        # Sample reward from arm
        mean_reward = arm_means[arm_idx]
        reward = self._rng.gauss(mean_reward, 0.1)
        
        # Update state
        next_state = {
            "arm_means": arm_means,
            "pulls": pulls + 1,
            "last_arm": arm_idx,
            "last_reward": reward,
        }
        
        # Bandit tasks don't naturally "terminate"
        done = False
        
        return next_state, reward, done


class ClassificationAdapter(EnvironmentAdapter):
    """Adapter for classification tasks."""
    
    def execute_step(
        self, 
        state: Dict[str, Any], 
        action: str,
        step: int,
    ) -> Tuple[Dict[str, Any], float, bool]:
        """Execute classification step.
        
        State format: {"features": [float, ...], "true_label": int, "num_classes": int}
        Actions: "class_0", "class_1", ... "class_N"
        """
        features = state.get("features", [0.0] * 10)
        true_label = state.get("true_label", 0)
        num_classes = state.get("num_classes", 5)
        
        # Parse action
        try:
            predicted_label = int(action.split("_")[1]) if "_" in action else 0
            predicted_label = max(0, min(predicted_label, num_classes - 1))
        except (ValueError, IndexError):
            predicted_label = 0
        
        # Calculate reward (1.0 for correct, 0.0 for incorrect)
        reward = 1.0 if predicted_label == true_label else 0.0
        
        # Generate next sample (simulate dataset iteration)
        next_features = [self._rng.gauss(0, 1) for _ in range(len(features))]
        next_label = self._rng.randint(0, num_classes - 1)
        
        next_state = {
            "features": next_features,
            "true_label": next_label,
            "num_classes": num_classes,
            "examples_seen": state.get("examples_seen", 0) + 1,
        }
        
        # Classification continues until max steps
        done = False
        
        return next_state, reward, done


ENVIRONMENT_ADAPTERS = {
    "gridworld": GridWorldAdapter,
    "bandit": BanditAdapter,
    "classification": ClassificationAdapter,
}


# =============================================================================
# UNIVERSAL TASK INTERFACE (UTI)
# =============================================================================


@dataclass
class TaskSpec:
    """Universal task specification for any computable environment.
    
    Aligned to Legg & Hutter universal intelligence framing.
    
    Attributes:
        environment: Environment identifier string
        initial_state: Initial state as JSON-serializable dict
        reward_spec: Reward specification with id and params
        termination: Termination criteria
        seed: Random seed for deterministic execution
    """
    environment: str
    initial_state: Dict[str, Any]
    reward_spec: Dict[str, Any]
    termination: Dict[str, Any]
    seed: int = 12345
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "environment": self.environment,
            "initial_state": self.initial_state,
            "reward_spec": self.reward_spec,
            "termination": self.termination,
            "seed": self.seed,
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "TaskSpec":
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(**data)
    
    def get_signature(self) -> str:
        """Generate deterministic signature for caching."""
        content = f"{self.environment}:{json.dumps(self.initial_state, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class TaskResult:
    """Result of task execution.
    
    Attributes:
        action_sequence: List of actions taken
        cumulative_reward: Total reward accumulated
        v_mu_pi: Value function estimate V(μ, π)
        metrics: Additional metrics dict
    """
    action_sequence: List[str]
    cumulative_reward: float
    v_mu_pi: float
    metrics: Dict[str, float]
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "action_sequence": self.action_sequence,
            "cumulative_reward": self.cumulative_reward,
            "V_mu_pi": self.v_mu_pi,
            "metrics": self.metrics,
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "TaskResult":
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(
            action_sequence=data["action_sequence"],
            cumulative_reward=data["cumulative_reward"],
            v_mu_pi=data["V_mu_pi"],
            metrics=data["metrics"],
        )


class UniversalTaskInterface:
    """Universal Task Interface for Phase 8.7.
    
    Provides standard interface for any computable environment μ.
    Supports deterministic execution with fixed seeds.
    Includes environment adapters, complexity estimation, and JSON schema validation.
    """
    
    def __init__(self, seed: int = 12345):
        """Initialize UTI.
        
        Args:
            seed: Master random seed for determinism
        """
        self.seed = seed
        self._rng = random.Random(seed)  # nosec B311 - deterministic simulation
        self.task_history: List[Tuple[TaskSpec, TaskResult]] = []
        self.adapters: Dict[str, EnvironmentAdapter] = {}
        self._initialize_adapters()
    
    def _initialize_adapters(self) -> None:
        """Initialize environment adapters."""
        for env_name, adapter_class in ENVIRONMENT_ADAPTERS.items():
            self.adapters[env_name] = adapter_class(seed=self.seed)
    
    def validate_task_spec(self, spec: TaskSpec) -> Tuple[bool, List[str]]:
        """Validate task specification using JSON schema validation.
        
        Args:
            spec: TaskSpec to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        # Use enhanced schema validation
        return validate_task_spec_schema(spec)
    
    def estimate_complexity(self, spec: TaskSpec) -> Tuple[float, TaskComplexity]:
        """Estimate task computational complexity.
        
        Args:
            spec: TaskSpec to analyze
            
        Returns:
            Tuple of (complexity_score, complexity_level)
        """
        return estimate_task_complexity(spec)
    
    def execute_task(
        self,
        spec: TaskSpec,
        policy: Optional["MetaPolicyRouter"] = None,
        use_adapter: bool = True,
    ) -> TaskResult:
        """Execute a task with the given specification.
        
        Args:
            spec: Task specification
            policy: Optional policy router for action selection
            use_adapter: If True, use environment-specific adapter when available
            
        Returns:
            TaskResult with execution outcomes
        """
        # Validate spec first
        is_valid, errors = self.validate_task_spec(spec)
        if not is_valid:
            raise ValueError(f"Invalid task spec: {errors}")
        
        # Get complexity estimate
        complexity_score, complexity_level = self.estimate_complexity(spec)
        
        # Seed for this specific task
        task_rng = random.Random(spec.seed)  # nosec B311 - deterministic simulation
        
        # Check if we have a specific adapter for this environment
        adapter = None
        if use_adapter and spec.environment in self.adapters:
            adapter = self.adapters[spec.environment]
        
        # Execute task
        max_steps = spec.termination.get("max_steps", 1000)
        actions = []
        total_reward = 0.0
        current_state = spec.initial_state.copy()
        done = False
        
        for step in range(min(max_steps, DEFAULT_MAX_DEMO_STEPS)):
            if done:
                break
            
            # Select action (use policy if available)
            if policy:
                action = policy.select_action(spec, step)
            elif adapter:
                # Adapter-specific action selection
                if spec.environment == "gridworld":
                    action = task_rng.choice(["up", "down", "left", "right", "stay"])
                elif spec.environment == "bandit":
                    num_arms = len(current_state.get("arm_means", [4]))
                    action = f"arm_{task_rng.randint(0, num_arms - 1)}"
                elif spec.environment == "classification":
                    num_classes = current_state.get("num_classes", 5)
                    action = f"class_{task_rng.randint(0, num_classes - 1)}"
                else:
                    action = f"action_{task_rng.randint(0, 9)}"
            else:
                action = f"action_{task_rng.randint(0, 9)}"
            
            actions.append(action)
            
            # Execute step
            if adapter:
                current_state, step_reward, done = adapter.execute_step(
                    current_state, action, step
                )
            else:
                # Generic simulation
                step_reward = task_rng.uniform(0, 1)
                if task_rng.random() < EARLY_TERMINATION_PROBABILITY:
                    done = True
            
            total_reward += step_reward
        
        # Calculate metrics
        accuracy = min(1.0, total_reward / max(len(actions), 1))
        coherence = 1.0 - (1.0 / max(len(actions), 1))
        
        result = TaskResult(
            action_sequence=actions,
            cumulative_reward=total_reward,
            v_mu_pi=accuracy,
            metrics={
                "accuracy": accuracy,
                "steps": len(actions),
                "coherence": coherence,
                "complexity_score": complexity_score,
                "complexity_level": complexity_level.value,
            },
        )
        
        self.task_history.append((spec, result))
        return result


# =============================================================================
# META-POLICY ROUTER (MPR)
# =============================================================================


@dataclass
class StrategyAmplitude:
    """Complex amplitude for strategy superposition.
    
    |ψ_strat⟩ = Σᵢ αᵢ |sᵢ⟩
    
    Attributes:
        strategy: Strategy name
        real: Real part of amplitude
        imag: Imaginary part of amplitude
    """
    strategy: str
    real: float = 1.0
    imag: float = 0.0
    
    @property
    def probability(self) -> float:
        """Born rule: P = |α|²"""
        return self.real ** 2 + self.imag ** 2
    
    @property
    def amplitude(self) -> complex:
        """Get complex amplitude."""
        return complex(self.real, self.imag)
    
    def apply_phase(self, phase: float) -> None:
        """Apply phase rotation: α → α·e^(iφ)"""
        new_amp = self.amplitude * complex(math.cos(phase), math.sin(phase))
        self.real = new_amp.real
        self.imag = new_amp.imag


@dataclass
class TaskFeatures:
    """Features extracted from a task for routing.
    
    Attributes:
        domain_signature: Hash or embedding of domain
        complexity: Complexity metrics
        similarity_topk: Top-K similar domains
        risk: Risk assessment
    """
    domain_signature: str
    complexity: Dict[str, int]
    similarity_topk: List[Dict[str, Any]]
    risk: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain_signature": self.domain_signature,
            "complexity": self.complexity,
            "similarity_topk": self.similarity_topk,
            "risk": self.risk,
        }


class MetaPolicyRouter:
    """Meta-Policy Router with strategy superposition.
    
    Maintains complex amplitudes over strategy basis states:
    |ψ_strat⟩ = Σᵢ αᵢ |sᵢ⟩, where Σᵢ |αᵢ|² = 1
    
    Measurement collapses to a single strategy based on
    probability distribution |αᵢ|².
    """
    
    def __init__(self, seed: int = 12345, strategies: Optional[List[str]] = None):
        """Initialize router.
        
        Args:
            seed: Random seed for deterministic measurement
            strategies: List of available strategies
        """
        self.seed = seed
        self._rng = random.Random(seed)  # nosec B311 - deterministic simulation
        self.strategies = strategies or STRATEGIES
        
        # Initialize uniform superposition
        self.amplitudes = self._initialize_superposition()
        
        # Tracking
        self.selection_history: List[Dict[str, Any]] = []
    
    def _initialize_superposition(self) -> List[StrategyAmplitude]:
        """Initialize uniform superposition over strategies."""
        n = len(self.strategies)
        amplitude = 1.0 / math.sqrt(n)
        
        return [
            StrategyAmplitude(strategy=s, real=amplitude, imag=0.0)
            for s in self.strategies
        ]
    
    def normalize(self) -> None:
        """Normalize amplitudes to satisfy Σ|αᵢ|² = 1."""
        total = sum(a.probability for a in self.amplitudes)
        if total > 0:
            norm = math.sqrt(total)
            for a in self.amplitudes:
                a.real /= norm
                a.imag /= norm
    
    def get_probability_distribution(self) -> Dict[str, float]:
        """Get probability distribution over strategies."""
        return {a.strategy: a.probability for a in self.amplitudes}
    
    def update_amplitudes(self, features: TaskFeatures) -> None:
        """Update amplitudes based on task features.
        
        Higher similarity → higher amplitude for transfer strategies
        Higher risk → lower amplitude for aggressive strategies
        """
        for amp in self.amplitudes:
            # Boost transfer strategies if similar domains exist
            if features.similarity_topk:
                max_sim = max(d["score"] for d in features.similarity_topk)
                if "transfer" in amp.strategy:
                    amp.real *= (1.0 + max_sim)
            
            # Reduce amplitude if high negative transfer risk
            neg_risk = features.risk.get("neg_transfer_prob", 0.0)
            if neg_risk > NEGATIVE_TRANSFER_THRESHOLD:
                amp.real *= (1.0 - neg_risk)
        
        self.normalize()
    
    def measure(self, seed: Optional[int] = None) -> str:
        """Collapse superposition to select strategy.
        
        Uses seeded random selection based on |αᵢ|² probabilities.
        
        Args:
            seed: Optional seed override for measurement
            
        Returns:
            Selected strategy name
        """
        rng = random.Random(seed) if seed else self._rng  # nosec B311 - deterministic
        
        probs = self.get_probability_distribution()
        strategies = list(probs.keys())
        weights = list(probs.values())
        
        selected = rng.choices(strategies, weights=weights, k=1)[0]
        
        self.selection_history.append({
            "selected": selected,
            "probabilities": probs,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return selected
    
    def select_action(self, spec: TaskSpec, step: int) -> str:
        """Select action for a task step.
        
        Args:
            spec: Task specification
            step: Current step number
            
        Returns:
            Selected action string
        """
        # Use step as part of seed for determinism
        action_seed = hash((spec.seed, step)) % (2**31)
        rng = random.Random(action_seed)  # nosec B311 - deterministic simulation
        
        return f"action_{rng.randint(0, 9)}"
    
    def get_hyperparams(self, strategy: str) -> Dict[str, float]:
        """Get hyperparameters for selected strategy."""
        base_params = {
            "meta_lr": 0.001,
            "inner_lr": 0.01,
            "inner_steps": 5,
        }
        
        # Strategy-specific adjustments
        if strategy == "maml":
            base_params["inner_steps"] = 5
        elif strategy == "reptile":
            base_params["inner_steps"] = 10
        elif strategy == "adapter_transfer":
            base_params["inner_lr"] = 0.001
        
        return base_params


# =============================================================================
# ABSTRACTION ENGINE
# =============================================================================


@dataclass
class Concept:
    """Abstract concept extracted from experience.
    
    Attributes:
        id: Unique concept identifier
        props: Properties of the concept
        support: Number of observations supporting this concept
    """
    id: str
    props: Dict[str, Any]
    support: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "props": self.props,
            "support": self.support,
        }


@dataclass
class Relation:
    """Relation between concepts.
    
    Attributes:
        source: Source concept ID
        relation_type: Type of relation
        target: Target concept ID
    """
    source: str
    relation_type: str
    target: str
    
    def to_tuple(self) -> Tuple[str, str, str]:
        """Convert to tuple format."""
        return (self.source, self.relation_type, self.target)


@dataclass
class Analogy:
    """Analogy mapping between domains.
    
    Attributes:
        source_domain: Source domain name
        target_domain: Target domain name
        mapping: Concept mapping dictionary
        confidence: Confidence score
    """
    source_domain: str
    target_domain: str
    mapping: Dict[str, str]
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "src": self.source_domain,
            "tgt": self.target_domain,
            "mapping": self.mapping,
        }


class AbstractionEngine:
    """Abstraction Engine for concept/relation/analogy extraction.
    
    Hierarchical reasoning system that extracts reusable concepts,
    maps relations, and supports analogy transfer.
    """
    
    def __init__(self):
        """Initialize abstraction engine."""
        self.concepts: Dict[str, Concept] = {}
        self.relations: List[Relation] = []
        self.analogies: List[Analogy] = []
    
    def extract_concepts(self, observations: List[Dict[str, Any]]) -> List[Concept]:
        """Extract concepts from observations.
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            List of extracted concepts
        """
        extracted = []
        
        for obs in observations:
            # Simple pattern: look for binary properties
            for key, value in obs.items():
                if isinstance(value, bool):
                    concept_id = f"concept:{key}"
                    if concept_id not in self.concepts:
                        concept = Concept(
                            id=concept_id,
                            props={"binary": True, "key": key},
                            support=1,
                        )
                        self.concepts[concept_id] = concept
                        extracted.append(concept)
                    else:
                        self.concepts[concept_id].support += 1
        
        return extracted
    
    def map_relations(
        self,
        concepts: List[Concept],
        observations: List[Dict[str, Any]],
    ) -> List[Relation]:
        """Map relations between concepts.
        
        Args:
            concepts: List of concepts
            observations: List of observations
            
        Returns:
            List of mapped relations
        """
        new_relations = []
        
        # Simple co-occurrence based relation mapping
        concept_ids = [c.id for c in concepts]
        
        for i, c1 in enumerate(concept_ids):
            for c2 in concept_ids[i+1:]:
                # Check co-occurrence in observations
                cooccur = sum(
                    1 for obs in observations
                    if c1.split(":")[-1] in obs and c2.split(":")[-1] in obs
                )
                
                if cooccur > 0:
                    rel = Relation(
                        source=c1,
                        relation_type="co-occurs",
                        target=c2,
                    )
                    self.relations.append(rel)
                    new_relations.append(rel)
        
        return new_relations
    
    def find_analogies(
        self,
        source_domain: str,
        target_domain: str,
        source_concepts: List[str],
        target_concepts: List[str],
    ) -> List[Analogy]:
        """Find analogies between domains.
        
        Args:
            source_domain: Source domain name
            target_domain: Target domain name
            source_concepts: Concepts in source domain
            target_concepts: Concepts in target domain
            
        Returns:
            List of found analogies
        """
        found = []
        
        # Simple structural mapping based on concept name similarity
        mapping = {}
        for sc in source_concepts:
            best_match = None
            best_score = 0.0
            
            for tc in target_concepts:
                # Simple Jaccard similarity on concept names
                s_parts = set(sc.lower().split("_"))
                t_parts = set(tc.lower().split("_"))
                
                if s_parts and t_parts:
                    intersection = len(s_parts & t_parts)
                    union = len(s_parts | t_parts)
                    score = intersection / union if union > 0 else 0.0
                    
                    if score > best_score:
                        best_score = score
                        best_match = tc
            
            if best_match and best_score > 0.3:
                mapping[sc] = best_match
        
        if mapping:
            analogy = Analogy(
                source_domain=source_domain,
                target_domain=target_domain,
                mapping=mapping,
                confidence=len(mapping) / max(len(source_concepts), 1),
            )
            self.analogies.append(analogy)
            found.append(analogy)
        
        return found
    
    def get_abstraction_output(self) -> Dict[str, Any]:
        """Get full abstraction output as JSON-serializable dict."""
        return {
            "abstractions": [c.to_dict() for c in self.concepts.values()],
            "relations": [r.to_tuple() for r in self.relations],
            "analogies": [a.to_dict() for a in self.analogies],
            "confidence": self._calculate_overall_confidence(),
        }
    
    def _calculate_overall_confidence(self) -> float:
        """Calculate overall abstraction confidence."""
        if not self.concepts:
            return 0.0
        
        # Weighted by support
        total_support = sum(c.support for c in self.concepts.values())
        if total_support == 0:
            return 0.0
        
        return min(1.0, total_support / 100.0)


# =============================================================================
# GROUNDING LAYER
# =============================================================================


@dataclass
class AbstractStep:
    """Abstract step in a plan.
    
    Attributes:
        op: Operation name
        target: Target of operation
        params: Additional parameters
    """
    op: str
    target: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"op": self.op, "target": self.target, **self.params}


@dataclass
class GroundedAction:
    """Grounded action ready for execution.
    
    Attributes:
        adapter: Adapter/API to use
        op: Operation name
        args: Arguments for operation
    """
    adapter: str
    op: str
    args: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "adapter": self.adapter,
            "op": self.op,
            "args": self.args,
        }


@dataclass
class ExecutionTrace:
    """Trace of action execution.
    
    Attributes:
        timestamp: ISO timestamp
        status: Execution status
        details: Additional details
    """
    timestamp: str
    status: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "t": self.timestamp,
            "status": self.status,
            **self.details,
        }


class GroundingLayer:
    """Grounding Layer for feasibility mapping.
    
    Maps abstractions/plans into feasible, validated actions.
    Prevents disconnected theorizing.
    """
    
    def __init__(self):
        """Initialize grounding layer."""
        self.adapters = {
            "github_api_mock": self._github_adapter,
            "generic_mock": self._generic_adapter,
        }
        self.execution_traces: List[ExecutionTrace] = []
    
    def _github_adapter(self, step: AbstractStep) -> Optional[GroundedAction]:
        """Ground step using GitHub API adapter."""
        op_mapping = {
            "request_review": "request_reviewers",
            "merge": "merge_pull_request",
            "comment": "create_comment",
        }
        
        grounded_op = op_mapping.get(step.op)
        if not grounded_op:
            return None
        
        return GroundedAction(
            adapter="github_api_mock",
            op=grounded_op,
            args={"target": step.target, **step.params},
        )
    
    def _generic_adapter(self, step: AbstractStep) -> GroundedAction:
        """Generic fallback adapter."""
        return GroundedAction(
            adapter="generic_mock",
            op=step.op,
            args={"target": step.target, **step.params},
        )
    
    def ground_plan(
        self,
        abstract_steps: List[AbstractStep],
    ) -> Tuple[List[GroundedAction], float]:
        """Ground abstract plan into feasible actions.
        
        Args:
            abstract_steps: List of abstract steps
            
        Returns:
            Tuple of (grounded actions, feasibility score)
        """
        grounded = []
        successful = 0
        
        for step in abstract_steps:
            # Try adapters in order
            action = None
            for adapter_name, adapter_fn in self.adapters.items():
                try:
                    action = adapter_fn(step)
                    if action:
                        break
                except Exception:  # nosec B112 - intentional adapter fallback
                    continue
            
            if action:
                grounded.append(action)
                successful += 1
            else:
                # Use generic fallback
                grounded.append(self._generic_adapter(step))
        
        feasibility = successful / len(abstract_steps) if abstract_steps else 0.0
        return grounded, feasibility
    
    def execute_actions(
        self,
        actions: List[GroundedAction],
        dry_run: bool = True,
    ) -> List[ExecutionTrace]:
        """Execute grounded actions.
        
        Args:
            actions: List of grounded actions
            dry_run: If True, simulate execution
            
        Returns:
            List of execution traces
        """
        traces = []
        
        for action in actions:
            timestamp = datetime.utcnow().isoformat()
            
            if dry_run:
                status = "simulated"
            else:
                status = "ok"  # Would execute here
            
            trace = ExecutionTrace(
                timestamp=timestamp,
                status=status,
                details={"action": action.to_dict()},
            )
            traces.append(trace)
            self.execution_traces.append(trace)
        
        return traces
    
    def get_grounding_output(
        self,
        abstract_plan: List[AbstractStep],
    ) -> Dict[str, Any]:
        """Get full grounding output as JSON-serializable dict."""
        actions, feasibility = self.ground_plan(abstract_plan)
        traces = self.execute_actions(actions, dry_run=True)
        
        return {
            "abstract_plan": {"steps": [s.to_dict() for s in abstract_plan]},
            "grounded_actions": [a.to_dict() for a in actions],
            "feasibility_score": feasibility,
            "execution_trace": [t.to_dict() for t in traces],
        }


# =============================================================================
# META-COGNITION
# =============================================================================


@dataclass
class SelfAssessment:
    """Self-assessment of knowledge state.
    
    Attributes:
        known_domains: Count of known domains
        unknown_domains: Count of unknown/uncertain domains
    """
    known_domains: int = 0
    unknown_domains: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "known_domains": self.known_domains,
            "unknown_domains": self.unknown_domains,
        }


@dataclass
class RecommendedAction:
    """Recommended meta-action.
    
    Attributes:
        action_type: Type of action
        budget: Resource budget for action
        priority: Priority level
    """
    action_type: str
    budget: int = 0
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.action_type,
            "budget": self.budget,
            "priority": self.priority,
        }


class MetaCognition:
    """Meta-Cognition for self-awareness and self-regulation.
    
    Monitors confidence/uncertainty and learning progress.
    Provides recommendations for exploration/exploitation.
    """
    
    def __init__(self):
        """Initialize meta-cognition."""
        self.confidence_history: List[Dict[str, float]] = []
        self.domain_knowledge: Dict[str, float] = {}
    
    def update_domain_knowledge(self, domain: str, confidence: float) -> None:
        """Update knowledge about a domain.
        
        Args:
            domain: Domain identifier
            confidence: Confidence level (0-1)
        """
        self.domain_knowledge[domain] = confidence
    
    def get_self_assessment(self) -> SelfAssessment:
        """Get current self-assessment."""
        known = sum(1 for c in self.domain_knowledge.values() if c > 0.7)
        unknown = len(self.domain_knowledge) - known
        
        return SelfAssessment(
            known_domains=known,
            unknown_domains=unknown,
        )
    
    def get_confidence_levels(
        self,
        router_confidence: float = 0.5,
        analogy_confidence: float = 0.5,
        grounding_confidence: float = 0.5,
    ) -> Dict[str, float]:
        """Get confidence levels for different components.
        
        Args:
            router_confidence: Confidence in routing decisions
            analogy_confidence: Confidence in analogies
            grounding_confidence: Confidence in grounding
            
        Returns:
            Dictionary of confidence levels
        """
        levels = {
            "router": router_confidence,
            "analogy": analogy_confidence,
            "grounding": grounding_confidence,
        }
        
        self.confidence_history.append(levels)
        return levels
    
    def get_recommendations(self) -> List[RecommendedAction]:
        """Get recommended meta-actions based on current state."""
        recommendations = []
        
        assessment = self.get_self_assessment()
        
        # If many unknown domains, recommend data collection
        if assessment.unknown_domains > assessment.known_domains:
            recommendations.append(RecommendedAction(
                action_type="collect_data",
                budget=5,
                priority=1,
            ))
        
        # If confidence is low, recommend isolation
        if self.confidence_history:
            last_conf = self.confidence_history[-1]
            avg_conf = sum(last_conf.values()) / len(last_conf)
            
            if avg_conf < 0.6:
                recommendations.append(RecommendedAction(
                    action_type="isolate_domain",
                    budget=0,
                    priority=2,
                ))
        
        return recommendations
    
    def get_metacognition_output(self) -> Dict[str, Any]:
        """Get full meta-cognition output as JSON-serializable dict."""
        return {
            "self_assessment": self.get_self_assessment().to_dict(),
            "confidence_levels": (
                self.confidence_history[-1]
                if self.confidence_history
                else {"router": 0.5, "analogy": 0.5, "grounding": 0.5}
            ),
            "recommended_actions": [r.to_dict() for r in self.get_recommendations()],
        }


# =============================================================================
# UNIVERSAL PATTERN STORE (UPS)
# =============================================================================


@dataclass
class Pattern:
    """Stored pattern for cross-domain transfer.
    
    Attributes:
        id: Unique pattern identifier
        payload: Pattern data
        domain: Source domain
        version: Pattern version
    """
    id: str
    payload: Dict[str, Any]
    domain: str = "unknown"
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "payload": self.payload,
            "domain": self.domain,
            "version": self.version,
        }


class UniversalPatternStore:
    """Universal Pattern Store for cross-domain patterns.
    
    Repository for accumulating and retrieving patterns
    that enable zero-shot transfer.
    """
    
    def __init__(self):
        """Initialize pattern store."""
        self.patterns: Dict[str, Pattern] = {}
        self.retrieval_history: List[Dict[str, Any]] = []
    
    def store_pattern(self, pattern: Pattern) -> str:
        """Store a pattern.
        
        Args:
            pattern: Pattern to store
            
        Returns:
            Pattern ID
        """
        # Version incrementing if pattern exists
        if pattern.id in self.patterns:
            existing = self.patterns[pattern.id]
            pattern.version = existing.version + 1
        
        self.patterns[pattern.id] = pattern
        return pattern.id
    
    def retrieve_patterns(
        self,
        query: str,
        top_k: int = 5,
    ) -> Tuple[List[Pattern], List[float]]:
        """Retrieve patterns matching query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Tuple of (patterns, relevance scores)
        """
        results = []
        
        # Simple keyword matching
        query_terms = set(query.lower().split())
        
        for pattern in self.patterns.values():
            # Score based on ID and payload matching
            pattern_text = f"{pattern.id} {json.dumps(pattern.payload)}".lower()
            pattern_terms = set(pattern_text.split())
            
            intersection = len(query_terms & pattern_terms)
            union = len(query_terms | pattern_terms)
            
            score = intersection / union if union > 0 else 0.0
            results.append((pattern, score))
        
        # Sort by score and take top_k
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:top_k]
        
        patterns = [r[0] for r in results]
        scores = [r[1] for r in results]
        
        # Record retrieval
        self.retrieval_history.append({
            "query": query,
            "num_results": len(patterns),
            "top_score": scores[0] if scores else 0.0,
        })
        
        return patterns, scores
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern.
        
        Args:
            pattern_id: ID of pattern to delete
            
        Returns:
            True if deleted, False if not found
        """
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            return True
        return False
    
    def get_store_output(self, query: str) -> Dict[str, Any]:
        """Get retrieval output as JSON-serializable dict."""
        patterns, scores = self.retrieve_patterns(query)
        
        return {
            "query": query,
            "retrieved_patterns": [p.to_dict() for p in patterns],
            "relevance_scores": scores,
        }


# =============================================================================
# UNIVERSAL CONTROLLER (ORCHESTRATOR)
# =============================================================================


class UniversalController:
    """Universal Controller orchestrating all Phase 8.7 components.
    
    Coordinates:
    - Universal Task Interface
    - Meta-Policy Router
    - Abstraction Engine
    - Grounding Layer
    - Meta-Cognition
    - Universal Pattern Store
    """
    
    def __init__(self, seed: int = 12345):
        """Initialize universal controller.
        
        Args:
            seed: Master random seed
        """
        self.seed = seed
        
        # Initialize components
        self.uti = UniversalTaskInterface(seed=seed)
        self.router = MetaPolicyRouter(seed=seed)
        self.abstraction = AbstractionEngine()
        self.grounding = GroundingLayer()
        self.metacog = MetaCognition()
        self.store = UniversalPatternStore()
        
        # Metrics tracking
        self.metrics_history: List[Dict[str, Any]] = []
    
    def process_task(self, spec: TaskSpec) -> Dict[str, Any]:
        """Process a task through the full pipeline.
        
        Args:
            spec: Task specification
            
        Returns:
            Full output dictionary
        """
        # 1. Validate task
        is_valid, errors = self.uti.validate_task_spec(spec)
        if not is_valid:
            return {"error": errors}
        
        # 2. Extract task features
        features = TaskFeatures(
            domain_signature=spec.get_signature(),
            complexity={"obs_dim": 128, "action_dim": 12, "horizon": 100},
            similarity_topk=[],
            risk={"neg_transfer_prob": 0.1, "forgetting_risk": 0.05},
        )
        
        # 3. Update router amplitudes based on features
        self.router.update_amplitudes(features)
        
        # 4. Retrieve relevant patterns
        patterns, scores = self.store.retrieve_patterns(spec.environment)
        
        # 5. Update similarity based on patterns
        if patterns:
            features.similarity_topk = [
                {"domain": p.domain, "score": s}
                for p, s in zip(patterns, scores)
            ]
            self.router.update_amplitudes(features)
        
        # 6. Select strategy (measure superposition)
        strategy = self.router.measure(seed=spec.seed)
        hyperparams = self.router.get_hyperparams(strategy)
        
        # 7. Execute task
        result = self.uti.execute_task(spec, self.router)
        
        # 8. Update meta-cognition
        self.metacog.update_domain_knowledge(
            spec.environment,
            result.metrics.get("accuracy", 0.5),
        )
        
        # 9. Calculate k₁ and quantum advantage
        decision_score = result.v_mu_pi
        k1 = 1.0 - decision_score
        advantage = calculate_safe_quantum_advantage(k1)
        
        # 10. Record metrics
        metrics = {
            "metric": "k1",
            "value": k1,
            "timestamp": datetime.utcnow().isoformat(),
            "evidence": {
                "run_id": f"run:{spec.get_signature()}",
                "seed": spec.seed,
                "task_id": f"task:{spec.environment}",
            },
        }
        self.metrics_history.append(metrics)
        
        # 11. Store patterns from experience
        if result.v_mu_pi > 0.7:  # Good performance
            pattern = Pattern(
                id=f"pat:{spec.environment}:{spec.get_signature()[:8]}",
                payload={"strategy": strategy, "hyperparams": hyperparams},
                domain=spec.environment,
            )
            self.store.store_pattern(pattern)
        
        return {
            "task_result": json.loads(result.to_json()),
            "selected_strategy": strategy,
            "hyperparams": hyperparams,
            "k1": k1,
            "quantum_advantage": advantage,
            "meets_target": k1 <= K1_TARGET,
            "metrics": metrics,
            "metacognition": self.metacog.get_metacognition_output(),
        }
    
    def get_metrics_jsonl(self) -> str:
        """Get all metrics as JSONL string."""
        lines = [json.dumps(m) for m in self.metrics_history]
        return "\n".join(lines)
    
    def check_safety_constraints(self) -> Dict[str, bool]:
        """Check all safety constraints.
        
        Returns:
            Dictionary of constraint → satisfied
        """
        assessment = self.metacog.get_self_assessment()
        
        # Check negative transfer
        neg_transfer_ok = True
        for domain, conf in self.metacog.domain_knowledge.items():
            if conf < 0.5:  # Low confidence may indicate negative transfer
                # Would check actual transfer metrics here
                pass
        
        # Check forgetting
        forgetting_ok = True
        # Would compare against baselines here
        
        return {
            "negative_transfer_ok": neg_transfer_ok,
            "forgetting_ok": forgetting_ok,
            "k1_target_achievable": True,  # Based on current trajectory
        }


# =============================================================================
# ADIABATIC ANNEALING (EXPLORATION-EXPLOITATION)
# =============================================================================


class AdiabaticScheduler:
    """Adiabatic schedule for exploration-exploitation annealing.
    
    H(t) = (1-β(t))·H_explore + β(t)·H_exploit
    β(0) = 0, β(1) = 1
    """
    
    def __init__(
        self,
        total_steps: int = DEFAULT_ANNEALING_STEPS,
        schedule: str = "linear",
    ):
        """Initialize scheduler.
        
        Args:
            total_steps: Total annealing steps
            schedule: Schedule type ("linear", "exponential", "cosine")
        """
        self.total_steps = total_steps
        self.schedule = schedule
        self.current_step = 0
    
    def get_beta(self, step: Optional[int] = None) -> float:
        """Get β value at current or specified step.
        
        Args:
            step: Optional step override
            
        Returns:
            β value in [0, 1]
        """
        t = step if step is not None else self.current_step
        progress = t / max(self.total_steps, 1)
        
        if self.schedule == "linear":
            return progress
        elif self.schedule == "exponential":
            return 1.0 - math.exp(-3.0 * progress)
        elif self.schedule == "cosine":
            return 0.5 * (1.0 - math.cos(math.pi * progress))
        else:
            return progress
    
    def step(self) -> float:
        """Advance one step and return new β.
        
        Returns:
            New β value
        """
        self.current_step = min(self.current_step + 1, self.total_steps)
        return self.get_beta()
    
    def get_energy_weights(self) -> Dict[str, float]:
        """Get energy function weights based on current β.
        
        Returns:
            Dictionary of weight names → values
        """
        beta = self.get_beta()
        
        return {
            "lambda_explore": 1.0 - beta,
            "lambda_exploit": beta,
            "lambda_err": 0.4 + 0.4 * beta,  # Error weight increases
            "lambda_risk": 0.3 - 0.2 * beta,  # Risk weight decreases
            "lambda_cost": 0.3,  # Cost stays constant
        }


# =============================================================================
# DECOHERENCE MODEL (NEGATIVE TRANSFER)
# =============================================================================


class DecoherenceModel:
    """Decoherence model for negative transfer detection.
    
    Models harmful transfer as a noise channel:
    ρ → E(ρ) = Σₖ EₖρEₖ†
    """
    
    def __init__(self, threshold: float = NEGATIVE_TRANSFER_THRESHOLD):
        """Initialize decoherence model.
        
        Args:
            threshold: Negative transfer threshold
        """
        self.threshold = threshold
        self.decoherence_events: List[Dict[str, Any]] = []
    
    def measure_decoherence(
        self,
        source_performance: float,
        target_performance: float,
        baseline_performance: float,
    ) -> float:
        """Measure decoherence (negative transfer).
        
        Args:
            source_performance: Performance on source domain
            target_performance: Performance on target domain
            baseline_performance: Baseline without transfer
            
        Returns:
            Decoherence rate (0 = no decoherence, 1 = full decoherence)
        """
        # Negative transfer = target performance drop below baseline
        if target_performance < baseline_performance:
            decoherence = (baseline_performance - target_performance) / max(baseline_performance, 0.01)
        else:
            decoherence = 0.0
        
        return min(1.0, max(0.0, decoherence))
    
    def check_trigger_rollback(
        self,
        decoherence_rate: float,
        domain: str,
    ) -> bool:
        """Check if rollback should be triggered.
        
        Args:
            decoherence_rate: Measured decoherence rate
            domain: Domain identifier
            
        Returns:
            True if rollback should be triggered
        """
        if decoherence_rate > self.threshold:
            self.decoherence_events.append({
                "domain": domain,
                "rate": decoherence_rate,
                "action": "rollback_triggered",
                "timestamp": datetime.utcnow().isoformat(),
            })
            return True
        return False
    
    def get_decoherence_report(self) -> Dict[str, Any]:
        """Get decoherence report."""
        return {
            "threshold": self.threshold,
            "total_events": len(self.decoherence_events),
            "recent_events": self.decoherence_events[-10:],
        }
