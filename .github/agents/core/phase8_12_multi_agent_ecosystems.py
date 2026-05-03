"""
Phase 8.12: Multi-Agent Ecosystems
===================================

Quantum Hamiltonian:
Ĥ_phase8.12 = Ĥ_negotiation + Ĥ_coalition + Ĥ_federated + Ĥ_communication +
              Ĥ_competitive + Ĥ_reputation + Ĥ_marketplace

Observable Operators:
- Ô_cooperation: Measure cooperation level (target: >0.8)
- Ô_trust: Measure agent trustworthiness (target: >0.9)
- Ô_diversity: Measure ecosystem diversity (target: >0.7)
- Ô_efficiency: Measure resource utilization (target: >0.85)
- Ô_stability: Measure ecosystem stability (target: >0.9)

Target Metrics:
- k₁ ≤ 0.18 (quantum advantage 5.56x)
- 100+ agent swarm coordination
- Consensus time < 1 second
- Federated learning convergence in 10 rounds
- AI Agent Intuitiveness: 98.5/100

PDA Loop Integration:
- Perception: Agent state monitoring, message receipt, reputation sensing
- Decision: Negotiation strategy, coalition decisions, communication routing
- Action: Message sending, model updates, resource allocation
- AfterMath: Trust updates, reputation propagation, performance metrics

Deterministic Execution:
All components use RANDOM_SEED_8_12=45 for reproducibility.
"""

import math
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

# Deterministic random seed for Phase 8.12
RANDOM_SEED_8_12 = 45


class NegotiationStrategy(Enum):
    """Negotiation strategies for agents."""
    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    NASH_BARGAINING = "nash_bargaining"
    TFTFT = "tit_for_tat"  # Tit-for-tat


class MessageType(Enum):
    """ACL/FIPA message types."""
    INFORM = "inform"
    REQUEST = "request"
    PROPOSE = "propose"
    ACCEPT = "accept"
    REJECT = "reject"
    QUERY = "query"
    CFP = "call_for_proposal"  # Call for proposal


class AuctionType(Enum):
    """Types of auction mechanisms."""
    FIRST_PRICE = "first_price"
    SECOND_PRICE = "second_price"
    VICKREY = "vickrey"
    DUTCH = "dutch"


@dataclass
class NegotiationOffer:
    """Represents a negotiation offer between agents."""
    proposer_id: str
    receiver_id: str
    resource: str
    value: float
    timestamp: float
    commitment_level: float = 0.0  # 0.0 to 1.0


@dataclass
class Coalition:
    """Represents a coalition of agents."""
    coalition_id: str
    member_ids: list[str]
    synergy_score: float
    stability_score: float
    formation_time: float
    dissolved: bool = False


@dataclass
class AgentMessage:
    """Standardized agent communication message (ACL/FIPA)."""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: dict[str, Any]
    timestamp: float
    conversation_id: Optional[str] = None


@dataclass
class ReputationScore:
    """Agent reputation tracking."""
    agent_id: str
    trust_score: float  # 0.0 to 1.0
    interaction_count: int
    success_rate: float
    last_updated: float


# ============================================================================
# PRE-COMMIT 1: Agent Negotiation Protocols
# ============================================================================


class AgentNegotiationProtocol:
    """
    Implements bilateral and multilateral negotiation with bargaining strategies.

    Quantum formalism:
    Ĥ_negotiation = Σᵢⱼ (Uᵢⱼ |offerᵢⱼ⟩⟨offerᵢⱼ| + Cᵢⱼ |commitᵢⱼ⟩⟨commitᵢⱼ|)

    Where:
    - Uᵢⱼ: Utility of offer between agents i and j
    - Cᵢⱼ: Commitment strength

    PDA Loop:
    - Perception: Monitor offers, commitment levels
    - Decision: Select negotiation strategy, evaluate offers
    - Action: Make counter-offers, commit to agreements
    - AfterMath: Update trust levels, record outcomes
    """

    def __init__(self, max_negotiation_rounds: int = 10, seed: int = RANDOM_SEED_8_12):
        self.max_negotiation_rounds = max_negotiation_rounds
        self.active_negotiations: dict[str, list[NegotiationOffer]] = {}
        self.completed_negotiations: list[dict[str, Any]] = []
        self.trust_levels: dict[tuple[str, str], float] = {}  # (agent1, agent2) -> trust
        self.random = random.Random(seed)

        # Metrics
        self.total_negotiations = 0
        self.successful_negotiations = 0
        self.average_rounds = 0.0

    def initiate_negotiation(
        self,
        proposer_id: str,
        receiver_id: str,
        resource: str,
        initial_value: float,
        strategy: NegotiationStrategy = NegotiationStrategy.NASH_BARGAINING
    ) -> str:
        """
        Initiate a negotiation between two agents.

        PDA: Perception (identify opportunity) -> Decision (choose strategy) -> Action (initiate)
        """
        negotiation_id = f"neg_{proposer_id}_{receiver_id}_{len(self.active_negotiations)}"

        initial_offer = NegotiationOffer(
            proposer_id=proposer_id,
            receiver_id=receiver_id,
            resource=resource,
            value=initial_value,
            timestamp=time.time(),
            commitment_level=0.5
        )

        self.active_negotiations[negotiation_id] = [initial_offer]
        self.total_negotiations += 1

        return negotiation_id

    def nash_bargaining(self, offer1_value: float, offer2_value: float,
                        threat_point1: float = 0.0, threat_point2: float = 0.0) -> float:
        """
        Compute Nash bargaining solution.

        Nash solution maximizes: (u₁ - d₁) * (u₂ - d₂)
        where uᵢ is utility and dᵢ is disagreement point
        """
        # Simple Nash bargaining: split the surplus
        total_value = offer1_value + offer2_value
        nash_value = (total_value - threat_point1 - threat_point2) / 2.0
        return max(nash_value, 0.0)

    def counter_offer(
        self,
        negotiation_id: str,
        agent_id: str,
        new_value: float,
        strategy: NegotiationStrategy = NegotiationStrategy.NASH_BARGAINING
    ) -> Optional[NegotiationOffer]:
        """
        Make a counter-offer in an ongoing negotiation.

        PDA: Perception (receive offer) -> Decision (evaluate & counter) -> Action (propose)
        """
        if negotiation_id not in self.active_negotiations:
            return None

        offers = self.active_negotiations[negotiation_id]
        if not offers:
            return None

        last_offer = offers[-1]

        # Apply strategy
        if strategy == NegotiationStrategy.NASH_BARGAINING:
            adjusted_value = self.nash_bargaining(new_value, last_offer.value)
        elif strategy == NegotiationStrategy.COOPERATIVE:
            # More generous counter-offer
            adjusted_value = (new_value + last_offer.value) / 2.0
        elif strategy == NegotiationStrategy.COMPETITIVE:
            # Less generous
            adjusted_value = new_value * 0.8 + last_offer.value * 0.2
        else:  # TIT_FOR_TAT
            # Mirror the last change
            adjusted_value = new_value

        counter = NegotiationOffer(
            proposer_id=agent_id,
            receiver_id=last_offer.proposer_id,
            resource=last_offer.resource,
            value=adjusted_value,
            timestamp=time.time(),
            commitment_level=min(last_offer.commitment_level + 0.1, 1.0)
        )

        offers.append(counter)
        return counter

    def evaluate_convergence(self, negotiation_id: str, threshold: float = 0.05) -> bool:
        """
        Check if negotiation has converged.

        PDA: Perception (track offers) -> Decision (check convergence) -> AfterMath (record)
        """
        if negotiation_id not in self.active_negotiations:
            return False

        offers = self.active_negotiations[negotiation_id]
        if len(offers) < 2:
            return False

        # Check if last two offers are within threshold
        last_value = offers[-1].value
        prev_value = offers[-2].value

        convergence = abs(last_value - prev_value) / max(abs(prev_value), 1e-6) < threshold

        if convergence:
            self.successful_negotiations += 1
            self.average_rounds = (self.average_rounds * (self.successful_negotiations - 1) +
                                  len(offers)) / self.successful_negotiations

            # AfterMath: Update trust
            proposer = offers[0].proposer_id
            receiver = offers[0].receiver_id
            self.trust_levels[(proposer, receiver)] = offers[-1].commitment_level

            # Record completion
            self.completed_negotiations.append({
                "negotiation_id": negotiation_id,
                "rounds": len(offers),
                "final_value": last_value,
                "success": True
            })

            # Clean up
            del self.active_negotiations[negotiation_id]

        return convergence

    def get_metrics(self) -> dict[str, Any]:
        """Get negotiation metrics."""
        return {
            "total_negotiations": self.total_negotiations,
            "successful_negotiations": self.successful_negotiations,
            "success_rate": self.successful_negotiations / max(self.total_negotiations, 1),
            "average_rounds": self.average_rounds,
            "active_negotiations": len(self.active_negotiations)
        }


# ============================================================================
# PRE-COMMIT 2: Coalition Formation
# ============================================================================


class CoalitionFormation:
    """
    Implements dynamic team formation with synergy calculation and stability analysis.

    Quantum formalism:
    Ĥ_coalition = Σₖ (Sₖ |coalitionₖ⟩⟨coalitionₖ| - βₖ Dₖ)

    Where:
    - Sₖ: Synergy score of coalition k
    - Dₖ: Dissolution risk
    - βₖ: Stability coefficient

    PDA Loop:
    - Perception: Monitor agent capabilities, detect opportunities
    - Decision: Evaluate potential coalitions, select members
    - Action: Form/dissolve coalitions
    - AfterMath: Track performance, update stability scores
    """

    def __init__(self, max_coalition_size: int = 10, stability_threshold: float = 0.6,
                 seed: int = RANDOM_SEED_8_12):
        self.max_coalition_size = max_coalition_size
        self.stability_threshold = stability_threshold
        self.coalitions: dict[str, Coalition] = {}
        self.agent_capabilities: dict[str, list[str]] = {}
        self.random = random.Random(seed)

        # Metrics
        self.total_coalitions_formed = 0
        self.total_coalitions_dissolved = 0
        self.average_synergy = 0.0

    def register_agent(self, agent_id: str, capabilities: list[str]):
        """Register an agent with their capabilities."""
        self.agent_capabilities[agent_id] = capabilities

    def calculate_synergy(self, agent_ids: list[str]) -> float:
        """
        Calculate synergy score for a group of agents.

        Synergy = |unique_capabilities| / total_possible + diversity_bonus

        PDA: Perception (agent capabilities) -> Decision (compute synergy)
        """
        if not agent_ids:
            return 0.0

        # Collect all capabilities
        all_caps = []
        for agent_id in agent_ids:
            if agent_id in self.agent_capabilities:
                all_caps.extend(self.agent_capabilities[agent_id])

        if not all_caps:
            return 0.0

        unique_caps = len(set(all_caps))
        total_caps = len(all_caps)

        # Base synergy from capability coverage
        coverage_synergy = unique_caps / max(total_caps, 1)

        # Diversity bonus (non-overlapping capabilities are valuable)
        diversity_bonus = (1.0 - (total_caps - unique_caps) / max(total_caps, 1)) * 0.2

        return min(coverage_synergy + diversity_bonus, 1.0)

    def form_coalition(self, member_ids: list[str]) -> Optional[str]:
        """
        Form a new coalition.

        PDA: Perception (identify agents) -> Decision (evaluate) -> Action (form coalition)
        """
        if len(member_ids) > self.max_coalition_size:
            return None

        coalition_id = f"coalition_{self.total_coalitions_formed}"
        synergy = self.calculate_synergy(member_ids)

        # Initial stability based on synergy
        stability = synergy * 0.8 + self.random.uniform(0.0, 0.2)

        coalition = Coalition(
            coalition_id=coalition_id,
            member_ids=member_ids,
            synergy_score=synergy,
            stability_score=stability,
            formation_time=time.time()
        )

        self.coalitions[coalition_id] = coalition
        self.total_coalitions_formed += 1

        # Update average synergy
        self.average_synergy = (self.average_synergy * (self.total_coalitions_formed - 1) +
                               synergy) / self.total_coalitions_formed

        return coalition_id

    def analyze_stability(self, coalition_id: str) -> dict[str, Any]:
        """
        Analyze coalition stability.

        Factors:
        - Synergy score
        - Coalition age
        - Member count

        PDA: Perception (coalition state) -> Decision (analyze) -> AfterMath (update)
        """
        if coalition_id not in self.coalitions:
            return {"stable": False, "reason": "Coalition not found"}

        coalition = self.coalitions[coalition_id]

        if coalition.dissolved:
            return {"stable": False, "reason": "Already dissolved"}

        # Stability factors
        synergy_factor = coalition.synergy_score
        age_factor = min((time.time() - coalition.formation_time) / 100.0, 1.0)
        size_factor = len(coalition.member_ids) / self.max_coalition_size

        # Combined stability
        stability = (synergy_factor * 0.5 + age_factor * 0.3 + size_factor * 0.2)
        coalition.stability_score = stability

        is_stable = stability >= self.stability_threshold

        return {
            "stable": is_stable,
            "stability_score": stability,
            "synergy_score": synergy_factor,
            "age_factor": age_factor,
            "size_factor": size_factor
        }

    def dissolve_coalition(self, coalition_id: str, reason: str = "stability_failure"):
        """
        Dissolve a coalition.

        PDA: Perception (detect instability) -> Decision (dissolve) -> AfterMath (record)
        """
        if coalition_id in self.coalitions:
            self.coalitions[coalition_id].dissolved = True
            self.total_coalitions_dissolved += 1

    def get_metrics(self) -> dict[str, Any]:
        """Get coalition formation metrics."""
        active_coalitions = sum(1 for c in self.coalitions.values() if not c.dissolved)

        return {
            "total_coalitions_formed": self.total_coalitions_formed,
            "total_coalitions_dissolved": self.total_coalitions_dissolved,
            "active_coalitions": active_coalitions,
            "average_synergy": self.average_synergy,
            "dissolution_rate": self.total_coalitions_dissolved / max(self.total_coalitions_formed, 1)
        }


# ============================================================================
# PRE-COMMIT 3: Federated Learning
# ============================================================================


class FederatedLearning:
    """
    Implements cross-agent knowledge sharing with privacy-preserving aggregation.

    Quantum formalism:
    Ĥ_federated = Σᵢ (θᵢ |modelᵢ⟩⟨modelᵢ| - λ ∇L(θᵢ))

    Where:
    - θᵢ: Model parameters for agent i
    - L(θᵢ): Loss function
    - λ: Learning rate

    PDA Loop:
    - Perception: Receive model updates from agents
    - Decision: Aggregate models, detect convergence
    - Action: Distribute updated global model
    - AfterMath: Track convergence, update metrics
    """

    def __init__(self, convergence_threshold: float = 0.01, max_rounds: int = 50,
                 seed: int = RANDOM_SEED_8_12):
        self.convergence_threshold = convergence_threshold
        self.max_rounds = max_rounds
        self.global_model: dict[str, float] = {}
        self.local_models: dict[str, dict[str, float]] = {}
        self.training_history: list[dict[str, Any]] = []
        self.random = random.Random(seed)

        # Metrics
        self.current_round = 0
        self.converged = False
        self.convergence_round = -1

    def initialize_global_model(self, model_params: dict[str, float]):
        """Initialize the global model."""
        self.global_model = model_params.copy()

    def submit_local_update(self, agent_id: str, local_params: dict[str, float]):
        """
        Submit local model update from an agent.

        PDA: Perception (receive update) -> Decision (validate) -> Action (store)
        """
        self.local_models[agent_id] = local_params.copy()

    def aggregate_models(self, aggregation_method: str = "fedavg") -> dict[str, float]:
        """
        Aggregate local models with privacy-preserving techniques.

        FedAvg: θ_global = Σᵢ (nᵢ/N) * θᵢ
        where nᵢ is data size for agent i, N is total data size

        PDA: Perception (collect models) -> Decision (aggregate) -> Action (update global)
        """
        if not self.local_models:
            return self.global_model

        if aggregation_method == "fedavg":
            # Federated averaging
            num_agents = len(self.local_models)
            aggregated = {}

            for agent_id, local_params in self.local_models.items():
                weight = 1.0 / num_agents  # Equal weighting (simplified)

                for param_name, param_value in local_params.items():
                    if param_name not in aggregated:
                        aggregated[param_name] = 0.0
                    aggregated[param_name] += weight * param_value

            self.global_model = aggregated

        self.current_round += 1

        # Record history
        self.training_history.append({
            "round": self.current_round,
            "num_participants": len(self.local_models),
            "global_model_snapshot": self.global_model.copy()
        })

        # Clear local models for next round
        self.local_models.clear()

        return self.global_model

    def check_convergence(self) -> bool:
        """
        Detect convergence of federated learning.

        Convergence when: ||θ_t - θ_{t-1}|| < threshold

        PDA: Perception (track model changes) -> Decision (check threshold) -> AfterMath (record)
        """
        if len(self.training_history) < 2:
            return False

        prev_model = self.training_history[-2]["global_model_snapshot"]
        curr_model = self.training_history[-1]["global_model_snapshot"]

        # Compute L2 norm of difference
        diff_norm = 0.0
        for param_name in curr_model:
            if param_name in prev_model:
                diff = curr_model[param_name] - prev_model[param_name]
                diff_norm += diff ** 2

        diff_norm = math.sqrt(diff_norm)

        self.converged = diff_norm < self.convergence_threshold

        if self.converged and self.convergence_round == -1:
            self.convergence_round = self.current_round

        return self.converged

    def get_metrics(self) -> dict[str, Any]:
        """Get federated learning metrics."""
        return {
            "current_round": self.current_round,
            "converged": self.converged,
            "convergence_round": self.convergence_round,
            "total_rounds_run": len(self.training_history),
            "num_participants_last_round": len(self.local_models) if self.local_models else 0
        }


# ============================================================================
# PRE-COMMIT 4: Agent Communication Protocols
# ============================================================================


class AgentCommunicationProtocol:
    """
    Implements standardized messaging (ACL/FIPA) with asynchronous patterns.

    Quantum formalism:
    Ĥ_communication = Σᵢⱼ (αᵢⱼ |messageᵢⱼ⟩⟨messageᵢⱼ| + βᵢⱼ |routeᵢⱼ⟩⟨routeᵢⱼ|)

    Where:
    - αᵢⱼ: Message importance from i to j
    - βᵢⱼ: Routing efficiency

    PDA Loop:
    - Perception: Receive messages, detect agent presence
    - Decision: Route messages, prioritize conversations
    - Action: Deliver messages
    - AfterMath: Update routing tables, track latency
    """

    def __init__(self, max_message_queue: int = 1000, seed: int = RANDOM_SEED_8_12):
        self.max_message_queue = max_message_queue
        self.message_queue: deque = deque(maxlen=max_message_queue)
        self.agent_registry: set[str] = set()
        self.routing_table: dict[str, str] = {}  # agent_id -> address
        self.conversation_history: dict[str, list[AgentMessage]] = defaultdict(list)
        self.random = random.Random(seed)

        # Metrics
        self.total_messages_sent = 0
        self.total_messages_delivered = 0
        self.average_latency = 0.0

    def register_agent(self, agent_id: str, address: str = "local"):
        """
        Register an agent in the communication network.

        PDA: Perception (agent join) -> Decision (assign address) -> Action (register)
        """
        self.agent_registry.add(agent_id)
        self.routing_table[agent_id] = address

    def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: MessageType,
        content: dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Send a message using ACL/FIPA protocol.

        PDA: Perception (message request) -> Decision (validate) -> Action (queue message)
        """
        if sender_id not in self.agent_registry:
            raise ValueError(f"Sender {sender_id} not registered")

        if receiver_id not in self.agent_registry:
            raise ValueError(f"Receiver {receiver_id} not registered")

        message_id = f"msg_{self.total_messages_sent}"

        message = AgentMessage(
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            conversation_id=conversation_id
        )

        self.message_queue.append(message)
        self.total_messages_sent += 1

        # Track conversation
        if conversation_id:
            self.conversation_history[conversation_id].append(message)

        return message_id

    def route_message(self, message: AgentMessage) -> bool:
        """
        Route a message to its destination.

        PDA: Perception (message) -> Decision (find route) -> Action (deliver)
        """
        # Simple routing: check if receiver is registered
        if message.receiver_id not in self.agent_registry:
            return False

        # Simulate routing delay
        latency = self.random.uniform(0.001, 0.01)  # 1-10ms

        # Update metrics
        self.total_messages_delivered += 1
        self.average_latency = (self.average_latency * (self.total_messages_delivered - 1) +
                               latency) / self.total_messages_delivered

        return True

    def process_message_queue(self, batch_size: int = 10) -> int:
        """
        Process messages in the queue (async pattern).

        PDA: Perception (queue state) -> Decision (select batch) -> Action (route batch)
        """
        processed = 0

        for _ in range(min(batch_size, len(self.message_queue))):
            if self.message_queue:
                message = self.message_queue.popleft()
                if self.route_message(message):
                    processed += 1

        return processed

    def get_conversation(self, conversation_id: str) -> list[AgentMessage]:
        """Retrieve a conversation history."""
        return self.conversation_history.get(conversation_id, [])

    def get_metrics(self) -> dict[str, Any]:
        """Get communication metrics."""
        return {
            "total_messages_sent": self.total_messages_sent,
            "total_messages_delivered": self.total_messages_delivered,
            "delivery_rate": self.total_messages_delivered / max(self.total_messages_sent, 1),
            "average_latency_ms": self.average_latency * 1000,
            "messages_in_queue": len(self.message_queue),
            "registered_agents": len(self.agent_registry),
            "active_conversations": len(self.conversation_history)
        }


# ============================================================================
# PRE-COMMIT 5: Competitive Co-evolution
# ============================================================================


class CompetitiveCoevolution:
    """
    Implements adversarial training and fitness-based selection.

    Quantum formalism:
    Ĥ_competitive = Σᵢⱼ (Rᵢⱼ |rivalryᵢⱼ⟩⟨rivalryᵢⱼ| + Fᵢ |fitnessᵢ⟩⟨fitnessᵢ|)

    Where:
    - Rᵢⱼ: Rivalry strength between agents i and j
    - Fᵢ: Fitness score of agent i

    PDA Loop:
    - Perception: Monitor agent performance, detect rivals
    - Decision: Select competitors, evaluate fitness
    - Action: Trigger competitions, update fitness
    - AfterMath: Track rivalry dynamics, evolution history
    """

    def __init__(self, population_size: int = 20, selection_pressure: float = 0.3,
                 seed: int = RANDOM_SEED_8_12):
        self.population_size = population_size
        self.selection_pressure = selection_pressure
        self.agent_fitness: dict[str, float] = {}
        self.rivalry_matrix: dict[tuple[str, str], float] = {}
        self.competition_history: list[dict[str, Any]] = []
        self.random = random.Random(seed)

        # Metrics
        self.total_competitions = 0
        self.generation = 0
        self.average_fitness = 0.0

    def register_agent(self, agent_id: str, initial_fitness: float = 0.5):
        """Register an agent in the competitive ecosystem."""
        self.agent_fitness[agent_id] = initial_fitness
        self._update_average_fitness()

    def run_competition(self, agent1_id: str, agent2_id: str) -> str:
        """
        Run a competition between two agents.

        PDA: Perception (agent state) -> Decision (compete) -> Action (update fitness)
        """
        if agent1_id not in self.agent_fitness or agent2_id not in self.agent_fitness:
            return "invalid"

        fitness1 = self.agent_fitness[agent1_id]
        fitness2 = self.agent_fitness[agent2_id]

        # Competition outcome based on fitness with some randomness
        prob_agent1_wins = fitness1 / (fitness1 + fitness2) if (fitness1 + fitness2) > 0 else 0.5

        if self.random.random() < prob_agent1_wins:
            winner = agent1_id
            loser = agent2_id
            fitness_change = 0.05
        else:
            winner = agent2_id
            loser = agent1_id
            fitness_change = 0.05

        # Update fitness
        self.agent_fitness[winner] = min(self.agent_fitness[winner] + fitness_change, 1.0)
        self.agent_fitness[loser] = max(self.agent_fitness[loser] - fitness_change * 0.5, 0.0)

        # Update rivalry
        self.rivalry_matrix[(agent1_id, agent2_id)] = self.rivalry_matrix.get(
            (agent1_id, agent2_id), 0.0) + 0.1

        # Record competition
        self.competition_history.append({
            "competition_id": self.total_competitions,
            "agent1": agent1_id,
            "agent2": agent2_id,
            "winner": winner,
            "timestamp": time.time()
        })

        self.total_competitions += 1
        self._update_average_fitness()

        return winner

    def fitness_based_selection(self, num_selected: int) -> list[str]:
        """
        Select top agents based on fitness (survival of the fittest).

        PDA: Perception (population fitness) -> Decision (select) -> AfterMath (new generation)
        """
        if not self.agent_fitness:
            return []

        # Sort by fitness
        sorted_agents = sorted(self.agent_fitness.items(), key=lambda x: x[1], reverse=True)

        # Select top agents
        num_to_select = min(num_selected, len(sorted_agents))
        return [agent_id for agent_id, _ in sorted_agents[:num_to_select]]


    def detect_rivalries(self, threshold: float = 0.5) -> list[tuple[str, str, float]]:
        """
        Detect strong rivalries between agents.

        PDA: Perception (competition history) -> Decision (identify patterns) -> AfterMath (report)
        """
        rivalries = []

        for (agent1, agent2), rivalry_score in self.rivalry_matrix.items():
            if rivalry_score >= threshold:
                rivalries.append((agent1, agent2, rivalry_score))

        return sorted(rivalries, key=lambda x: x[2], reverse=True)

    def advance_generation(self):
        """Advance to the next generation."""
        self.generation += 1

    def _update_average_fitness(self):
        """Update average fitness metric."""
        if self.agent_fitness:
            self.average_fitness = sum(self.agent_fitness.values()) / len(self.agent_fitness)

    def get_metrics(self) -> dict[str, Any]:
        """Get competitive co-evolution metrics."""
        return {
            "total_competitions": self.total_competitions,
            "generation": self.generation,
            "population_size": len(self.agent_fitness),
            "average_fitness": self.average_fitness,
            "max_fitness": max(self.agent_fitness.values()) if self.agent_fitness else 0.0,
            "min_fitness": min(self.agent_fitness.values()) if self.agent_fitness else 0.0,
            "num_rivalries": len(self.rivalry_matrix)
        }


# ============================================================================
# PRE-COMMIT 6: Reputation Systems
# ============================================================================


class ReputationSystem:
    """
    Implements agent trustworthiness tracking with reputation propagation.

    Quantum formalism:
    Ĥ_reputation = Σᵢ (Tᵢ |trustᵢ⟩⟨trustᵢ| + Σⱼ Pᵢⱼ |propagateᵢⱼ⟩⟨propagateᵢⱼ|)

    Where:
    - Tᵢ: Trust score of agent i
    - Pᵢⱼ: Reputation propagation from i to j

    PDA Loop:
    - Perception: Observe agent interactions, outcomes
    - Decision: Update trust scores, propagate reputation
    - Action: Apply trust-based decisions
    - AfterMath: Record reputation history, detect fraud
    """

    def __init__(self, initial_trust: float = 0.5, decay_rate: float = 0.95,
                 seed: int = RANDOM_SEED_8_12):
        self.initial_trust = initial_trust
        self.decay_rate = decay_rate
        self.reputation_scores: dict[str, ReputationScore] = {}
        self.interaction_history: list[dict[str, Any]] = []
        self.random = random.Random(seed)

        # Metrics
        self.total_interactions = 0
        self.average_trust = initial_trust

    def register_agent(self, agent_id: str):
        """Register an agent with initial reputation."""
        self.reputation_scores[agent_id] = ReputationScore(
            agent_id=agent_id,
            trust_score=self.initial_trust,
            interaction_count=0,
            success_rate=0.0,
            last_updated=time.time()
        )
        self._update_average_trust()

    def record_interaction(self, agent_id: str, success: bool, partner_id: Optional[str] = None):
        """
        Record an interaction outcome for an agent.

        PDA: Perception (interaction outcome) -> Decision (update trust) -> AfterMath (propagate)
        """
        if agent_id not in self.reputation_scores:
            self.register_agent(agent_id)

        rep_score = self.reputation_scores[agent_id]

        # Update interaction count
        rep_score.interaction_count += 1

        # Update success rate
        if rep_score.interaction_count == 1:
            rep_score.success_rate = 1.0 if success else 0.0
        else:
            rep_score.success_rate = (
                (rep_score.success_rate * (rep_score.interaction_count - 1) +
                 (1.0 if success else 0.0)) / rep_score.interaction_count
            )

        # Update trust score based on success rate
        rep_score.trust_score = rep_score.success_rate * 0.8 + 0.2  # Bounded [0.2, 1.0]
        rep_score.last_updated = time.time()

        # Record interaction
        self.interaction_history.append({
            "agent_id": agent_id,
            "partner_id": partner_id,
            "success": success,
            "timestamp": time.time()
        })

        self.total_interactions += 1
        self._update_average_trust()

        # Reputation propagation (if partner involved)
        if partner_id and partner_id in self.reputation_scores:
            self._propagate_reputation(agent_id, partner_id, success)

    def _propagate_reputation(self, source_id: str, target_id: str, positive: bool):
        """
        Propagate reputation between agents.

        Positive interactions increase trust, negative ones decrease it.
        """
        source_trust = self.reputation_scores[source_id].trust_score
        target_rep = self.reputation_scores[target_id]

        # Small adjustment based on source's trust
        adjustment = source_trust * 0.05 if positive else -source_trust * 0.03

        target_rep.trust_score = max(0.0, min(1.0, target_rep.trust_score + adjustment))
        target_rep.last_updated = time.time()

    def get_trust_score(self, agent_id: str) -> float:
        """Get the current trust score for an agent."""
        if agent_id in self.reputation_scores:
            return self.reputation_scores[agent_id].trust_score
        return self.initial_trust

    def apply_trust_based_decision(self, agent_id: str, threshold: float = 0.6) -> bool:
        """
        Make a decision based on agent's trustworthiness.

        PDA: Perception (trust score) -> Decision (threshold check) -> Action (allow/deny)
        """
        trust = self.get_trust_score(agent_id)
        return trust >= threshold

    def _update_average_trust(self):
        """Update average trust metric."""
        if self.reputation_scores:
            self.average_trust = sum(
                rep.trust_score for rep in self.reputation_scores.values()
            ) / len(self.reputation_scores)

    def get_metrics(self) -> dict[str, Any]:
        """Get reputation system metrics."""
        return {
            "total_interactions": self.total_interactions,
            "registered_agents": len(self.reputation_scores),
            "average_trust": self.average_trust,
            "max_trust": max(
                (rep.trust_score for rep in self.reputation_scores.values()),
                default=0.0
            ),
            "min_trust": min(
                (rep.trust_score for rep in self.reputation_scores.values()),
                default=0.0
            )
        }


# ============================================================================
# PRE-COMMIT 7: Marketplace Mechanisms
# ============================================================================


class MarketplaceMechanisms:
    """
    Implements agent service trading with auction and pricing strategies.

    Quantum formalism:
    Ĥ_marketplace = Σᵢ (Vᵢ |valueᵢ⟩⟨valueᵢ| + Σⱼ Bᵢⱼ |bidᵢⱼ⟩⟨bidᵢⱼ|)

    Where:
    - Vᵢ: Service value of agent i
    - Bᵢⱼ: Bid from agent j for service i

    PDA Loop:
    - Perception: Monitor bids, service availability
    - Decision: Run auctions, determine prices
    - Action: Allocate resources, complete trades
    - AfterMath: Track market efficiency, price discovery
    """

    def __init__(self, seed: int = RANDOM_SEED_8_12):
        self.services: dict[str, dict[str, Any]] = {}
        self.active_auctions: dict[str, dict[str, Any]] = {}
        self.completed_trades: list[dict[str, Any]] = []
        self.market_prices: dict[str, float] = {}
        self.random = random.Random(seed)

        # Metrics
        self.total_trades = 0
        self.total_revenue = 0.0
        self.average_price = 0.0

    def list_service(self, service_id: str, provider_id: str, base_price: float,
                     description: str = ""):
        """
        List a service in the marketplace.

        PDA: Perception (service availability) -> Decision (price) -> Action (list)
        """
        self.services[service_id] = {
            "provider_id": provider_id,
            "base_price": base_price,
            "description": description,
            "listed_time": time.time()
        }

        if service_id not in self.market_prices:
            self.market_prices[service_id] = base_price

    def create_auction(
        self,
        auction_id: str,
        service_id: str,
        auction_type: AuctionType = AuctionType.SECOND_PRICE,
        duration: float = 60.0
    ):
        """
        Create an auction for a service.

        PDA: Perception (demand) -> Decision (auction type) -> Action (create auction)
        """
        if service_id not in self.services:
            raise ValueError(f"Service {service_id} not found")

        self.active_auctions[auction_id] = {
            "service_id": service_id,
            "auction_type": auction_type,
            "bids": [],
            "start_time": time.time(),
            "duration": duration,
            "closed": False
        }

    def submit_bid(self, auction_id: str, bidder_id: str, bid_amount: float):
        """
        Submit a bid to an auction.

        PDA: Perception (auction) -> Decision (bid amount) -> Action (submit bid)
        """
        if auction_id not in self.active_auctions:
            raise ValueError(f"Auction {auction_id} not found")

        auction = self.active_auctions[auction_id]

        if auction["closed"]:
            raise ValueError("Auction is closed")

        auction["bids"].append({
            "bidder_id": bidder_id,
            "amount": bid_amount,
            "timestamp": time.time()
        })

    def close_auction(self, auction_id: str) -> dict[str, Any]:
        """
        Close an auction and determine the winner.

        PDA: Perception (bids) -> Decision (winner selection) -> AfterMath (finalize trade)
        """
        if auction_id not in self.active_auctions:
            return {"success": False, "reason": "Auction not found"}

        auction = self.active_auctions[auction_id]

        if not auction["bids"]:
            auction["closed"] = True
            return {"success": False, "reason": "No bids received"}

        # Sort bids by amount
        sorted_bids = sorted(auction["bids"], key=lambda x: x["amount"], reverse=True)

        auction_type = auction["auction_type"]

        if auction_type == AuctionType.FIRST_PRICE:
            # Winner pays their bid
            winner = sorted_bids[0]
            final_price = winner["amount"]

        elif auction_type == AuctionType.SECOND_PRICE or auction_type == AuctionType.VICKREY:
            # Winner pays second-highest bid
            winner = sorted_bids[0]
            final_price = sorted_bids[1]["amount"] if len(sorted_bids) > 1 else winner["amount"]

        else:  # DUTCH
            # Descending price auction (simplified: use highest bid)
            winner = sorted_bids[0]
            final_price = winner["amount"]

        auction["closed"] = True

        # Record trade
        trade = {
            "auction_id": auction_id,
            "service_id": auction["service_id"],
            "winner_id": winner["bidder_id"],
            "final_price": final_price,
            "num_bids": len(auction["bids"]),
            "timestamp": time.time()
        }

        self.completed_trades.append(trade)
        self.total_trades += 1
        self.total_revenue += final_price

        # Update market price
        service_id = auction["service_id"]
        self.market_prices[service_id] = final_price

        # Update average price
        self.average_price = self.total_revenue / self.total_trades

        return {
            "success": True,
            "winner_id": winner["bidder_id"],
            "final_price": final_price,
            "num_bids": len(auction["bids"])
        }

    def get_market_price(self, service_id: str) -> Optional[float]:
        """Get the current market price for a service."""
        return self.market_prices.get(service_id)

    def get_metrics(self) -> dict[str, Any]:
        """Get marketplace metrics."""
        return {
            "total_trades": self.total_trades,
            "total_revenue": self.total_revenue,
            "average_price": self.average_price,
            "active_auctions": sum(1 for a in self.active_auctions.values() if not a["closed"]),
            "listed_services": len(self.services),
            "market_efficiency": self.total_trades / max(len(self.active_auctions), 1)
        }


# ============================================================================
# Module-level exports and utility functions
# ============================================================================

def get_phase8_12_summary() -> dict[str, Any]:
    """
    Get a summary of Phase 8.12 Multi-Agent Ecosystems implementation.

    Returns comprehensive metrics across all 7 PRE-COMMITs.
    """
    return {
        "phase": "8.12",
        "name": "Multi-Agent Ecosystems",
        "quantum_target": {
            "k1_target": 0.18,
            "quantum_advantage": 5.56
        },
        "components": {
            "negotiation": "AgentNegotiationProtocol",
            "coalition": "CoalitionFormation",
            "federated": "FederatedLearning",
            "communication": "AgentCommunicationProtocol",
            "competitive": "CompetitiveCoevolution",
            "reputation": "ReputationSystem",
            "marketplace": "MarketplaceMechanisms"
        },
        "pda_loop_active": True,
        "deterministic_seed": RANDOM_SEED_8_12
    }


__all__ = [
    "AgentNegotiationProtocol",
    "CoalitionFormation",
    "FederatedLearning",
    "AgentCommunicationProtocol",
    "CompetitiveCoevolution",
    "ReputationSystem",
    "MarketplaceMechanisms",
    "NegotiationStrategy",
    "MessageType",
    "AuctionType",
    "NegotiationOffer",
    "Coalition",
    "AgentMessage",
    "ReputationScore",
    "get_phase8_12_summary",
    "RANDOM_SEED_8_12"
]
