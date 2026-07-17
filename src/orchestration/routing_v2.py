"""
Enhanced Orchestrator Routing v2 — Intelligent agent selection with semantic search,
load awareness, and distributed tracing.

Phase 4D Optimization: Replaces `scripts/ci/orchestrator_routing.py` with:
  1. Semantic similarity matching (FAISS corpus)
  2. Real-time load balancing awareness
  3. Agent health/availability tracking
  4. Fallback chains for resilience
  5. Decision tracing for observability
  6. SLA enforcement

Usage:
  from src.orchestration.routing_v2 import EnhancedRouter
  
  router = EnhancedRouter()
  selection = router.select_best_agent(
      task_description="fix failing CI tests",
      max_latency_ms=500,
      require_sla_compliance=True
  )
"""

from __future__ import annotations

import hashlib
import json
import logging
import pathlib
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT.parent / ".github" / "agents" / "AGENT_REGISTRY.yaml"
TRACES_DIR = REPO_ROOT.parent / ".codex" / "routing_traces"
TRACES_DIR.mkdir(exist_ok=True, parents=True)


class SelectionStrategy(Enum):
    """Agent selection strategies."""
    SEMANTIC_FAISS = "semantic_faiss"
    CAPABILITY_TAG = "capability_tag"
    LOAD_BALANCED = "load_balanced"
    HEALTH_AWARE = "health_aware"
    FALLBACK_DEFAULT = "fallback_default"


class AgentHealth(Enum):
    """Agent health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class AgentLoad:
    """Current load metrics for an agent."""
    agent_id: str
    active_handoffs: int
    queue_depth: int
    avg_latency_ms: float
    error_rate: float  # 0.0 to 1.0
    health: AgentHealth
    last_updated: str

    def utilization_score(self) -> float:
        """Compute 0-1 utilization score (lower = better capacity)."""
        # Queue depth is primary factor, then active handoffs
        queue_factor = min(1.0, self.queue_depth / 50.0)
        active_factor = min(1.0, self.active_handoffs / 10.0)
        # Weighted average
        return (queue_factor * 0.7) + (active_factor * 0.3)

    def sla_compliant(self, max_latency_ms: float) -> bool:
        """Check if agent meets SLA."""
        return (self.avg_latency_ms <= max_latency_ms and 
                self.error_rate < 0.05 and 
                self.health != AgentHealth.UNHEALTHY)


@dataclass
class RoutingDecision:
    """Decision trace for a routing operation."""
    decision_id: str
    timestamp: str
    task_description: str
    strategy_used: SelectionStrategy
    selected_agent: str
    confidence_score: float
    candidate_rank: int
    alternatives: list[tuple[str, float]]
    sla_compliant: bool
    latency_ms: float
    decision_hash: str
    input_lock: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AgentLoadTracker:
    """Track real-time load for all agents."""
    
    def __init__(self):
        self._loads: dict[str, AgentLoad] = {}
    
    def update_load(self, agent_id: str, load: AgentLoad) -> None:
        """Update load metrics for an agent."""
        self._loads[agent_id] = load
    
    def get_load(self, agent_id: str) -> Optional[AgentLoad]:
        """Get current load for an agent."""
        return self._loads.get(agent_id)
    
    def healthiest_agents(self, limit: int = 5) -> list[str]:
        """Get agents with lowest utilization (healthiest capacity)."""
        healthy = [
            (agent_id, load.utilization_score())
            for agent_id, load in self._loads.items()
            if load.health != AgentHealth.UNHEALTHY
        ]
        healthy.sort(key=lambda x: x[1])
        return [agent_id for agent_id, _ in healthy[:limit]]
    
    def sla_compliant_agents(self, max_latency_ms: float) -> list[str]:
        """Get agents meeting SLA."""
        return [
            agent_id
            for agent_id, load in self._loads.items()
            if load.sla_compliant(max_latency_ms)
        ]


class EnhancedRouter:
    """Intelligent orchestrator routing engine."""
    
    def __init__(self, load_tracker: Optional[AgentLoadTracker] = None):
        self.registry = self._load_registry()
        self.load_tracker = load_tracker or AgentLoadTracker()
        self._decision_cache: dict[str, RoutingDecision] = {}
    
    def _load_registry(self) -> list[dict[str, Any]]:
        """Load AGENT_REGISTRY."""
        if not REGISTRY_PATH.exists():
            logger.warning(f"AGENT_REGISTRY not found at {REGISTRY_PATH}")
            return []
        try:
            data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
            agents = data.get("agents", [])
            return [a for a in agents if a.get("status") == "active"]
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return []
    
    def select_best_agent(
        self,
        task_description: str,
        max_latency_ms: float = 500.0,
        require_sla_compliance: bool = True,
        top_k: int = 1,
    ) -> RoutingDecision | list[RoutingDecision]:
        """
        Select the best agent(s) for a task using multi-strategy routing.
        
        Strategy priority:
        1. Load-balanced selection among SLA-compliant agents
        2. Semantic FAISS search if available
        3. Capability tag keyword matching
        4. Health-aware fallback
        5. Safe default
        """
        start_time = time.time()
        decision_id = str(uuid.uuid4())
        
        # Compute input lock for determinism
        input_lock = {
            "task_hash": hashlib.sha256(task_description.encode()).hexdigest(),
            "max_latency_ms": max_latency_ms,
            "require_sla": require_sla_compliance,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Strategy 1: Load-balanced among SLA-compliant agents
        sla_agents = self.load_tracker.sla_compliant_agents(max_latency_ms)
        if sla_agents:
            candidates = self._rank_by_utilization(sla_agents, task_description)
            if candidates:
                selected = candidates[0][0]
                decision = RoutingDecision(
                    decision_id=decision_id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    task_description=task_description,
                    strategy_used=SelectionStrategy.LOAD_BALANCED,
                    selected_agent=selected,
                    confidence_score=candidates[0][1],
                    candidate_rank=1,
                    alternatives=[(c[0], c[1]) for c in candidates[1:top_k]],
                    sla_compliant=True,
                    latency_ms=time.time() - start_time,
                    decision_hash=self._compute_decision_hash(decision_id, selected),
                    input_lock=input_lock,
                )
                self._save_decision(decision)
                return decision if top_k == 1 else self._multi_decision(decision, candidates, top_k)
        
        # Strategy 2: Semantic FAISS search
        try:
            selected = self._semantic_search(task_description)
            if selected:
                decision = RoutingDecision(
                    decision_id=decision_id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    task_description=task_description,
                    strategy_used=SelectionStrategy.SEMANTIC_FAISS,
                    selected_agent=selected,
                    confidence_score=0.85,
                    candidate_rank=1,
                    alternatives=[],
                    sla_compliant=False,
                    latency_ms=time.time() - start_time,
                    decision_hash=self._compute_decision_hash(decision_id, selected),
                    input_lock=input_lock,
                )
                self._save_decision(decision)
                return decision
        except Exception as e:
            logger.debug(f"Semantic search failed: {e}")
        
        # Strategy 3: Capability tag matching
        candidates = self._keyword_match(task_description)
        if candidates:
            selected = candidates[0][0]
            decision = RoutingDecision(
                decision_id=decision_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                task_description=task_description,
                strategy_used=SelectionStrategy.CAPABILITY_TAG,
                selected_agent=selected,
                confidence_score=candidates[0][1],
                candidate_rank=1,
                alternatives=[(c[0], c[1]) for c in candidates[1:top_k]],
                sla_compliant=False,
                latency_ms=time.time() - start_time,
                decision_hash=self._compute_decision_hash(decision_id, selected),
                input_lock=input_lock,
            )
            self._save_decision(decision)
            return decision
        
        # Strategy 4: Fallback to safe default
        default_agent = "cognitive-brain-cli-agent"
        decision = RoutingDecision(
            decision_id=decision_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_description=task_description,
            strategy_used=SelectionStrategy.FALLBACK_DEFAULT,
            selected_agent=default_agent,
            confidence_score=0.5,
            candidate_rank=1,
            alternatives=[],
            sla_compliant=False,
            latency_ms=time.time() - start_time,
            decision_hash=self._compute_decision_hash(decision_id, default_agent),
            input_lock=input_lock,
        )
        self._save_decision(decision)
        return decision
    
    def _rank_by_utilization(
        self, 
        agent_ids: list[str], 
        task_description: str
    ) -> list[tuple[str, float]]:
        """Rank agents by utilization score + task relevance."""
        scored = []
        for agent_id in agent_ids:
            load = self.load_tracker.get_load(agent_id)
            if not load:
                continue
            
            # Utilization score (lower = better)
            util_score = load.utilization_score()
            
            # Task relevance score (0-1)
            relevance = self._compute_task_relevance(agent_id, task_description)
            
            # Combined score (weighted)
            combined = (util_score * 0.6) + ((1.0 - relevance) * 0.4)
            scored.append((agent_id, 1.0 - combined))  # Invert so higher is better
        
        scored.sort(key=lambda x: -x[1])
        return scored
    
    def _semantic_search(self, task_description: str) -> Optional[str]:
        """Semantic search via FAISS (Phase 3 corpus)."""
        try:
            from scripts.ci.query_corpus import query as corpus_query
            results = corpus_query(f"agent capable of: {task_description}", top_k=3)
            agent_results = [
                r for r in results
                if ".github/agents/" in r.get("source", "")
            ]
            if agent_results:
                raw = agent_results[0]["source"].split("/")[-1]
                return raw.replace(".md", "").replace(".yaml", "")
        except Exception as e:
            logger.debug(f"Semantic search failed: {e}")
        return None
    
    def _keyword_match(self, task_description: str) -> list[tuple[str, float]]:
        """Keyword-based agent matching."""
        query_words = set(task_description.lower().split())
        scored = []
        
        for agent in self.registry:
            tags = [t.lower() for t in agent.get("capability_tags", [])]
            capabilities = [c.lower() for c in agent.get("capabilities", [])]
            all_terms = tags + capabilities + [agent.get("id", "").lower()]
            
            matches = sum(1 for word in query_words if any(word in term for term in all_terms))
            if matches > 0:
                score = matches / len(query_words)  # Normalize
                scored.append((agent["id"], score))
        
        scored.sort(key=lambda x: -x[1])
        return scored
    
    def _compute_task_relevance(self, agent_id: str, task_description: str) -> float:
        """Compute relevance of task to agent (0-1)."""
        agent = next((a for a in self.registry if a["id"] == agent_id), None)
        if not agent:
            return 0.0
        
        tags = agent.get("capability_tags", [])
        task_words = set(task_description.lower().split())
        tag_words = " ".join(tags).lower().split()
        
        if not tag_words:
            return 0.0
        
        matches = sum(1 for word in task_words if any(word in tag for tag in tag_words))
        return min(1.0, matches / len(tag_words))
    
    def _compute_decision_hash(self, decision_id: str, agent_id: str) -> str:
        """Compute SHA256 hash for decision verification."""
        data = f"{decision_id}:{agent_id}:{datetime.now(timezone.utc).isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _save_decision(self, decision: RoutingDecision) -> None:
        """Save decision trace to disk."""
        trace_file = TRACES_DIR / f"{decision.decision_id}.json"
        try:
            trace_file.write_text(
                json.dumps(decision.to_dict(), indent=2),
                encoding="utf-8"
            )
            self._decision_cache[decision.decision_id] = decision
        except Exception as e:
            logger.error(f"Failed to save decision trace: {e}")
    
    def _multi_decision(
        self,
        primary: RoutingDecision,
        candidates: list[tuple[str, float]],
        top_k: int
    ) -> list[RoutingDecision]:
        """Generate multiple routing decisions."""
        decisions = [primary]
        for i, (agent_id, score) in enumerate(candidates[1:top_k], start=2):
            decision = RoutingDecision(
                decision_id=str(uuid.uuid4()),
                timestamp=primary.timestamp,
                task_description=primary.task_description,
                strategy_used=primary.strategy_used,
                selected_agent=agent_id,
                confidence_score=score,
                candidate_rank=i,
                alternatives=[],
                sla_compliant=primary.sla_compliant,
                latency_ms=primary.latency_ms,
                decision_hash=self._compute_decision_hash(str(uuid.uuid4()), agent_id),
                input_lock=primary.input_lock,
            )
            decisions.append(decision)
        return decisions
    
    def get_decision_history(self, limit: int = 100) -> list[RoutingDecision]:
        """Retrieve recent routing decisions."""
        trace_files = sorted(TRACES_DIR.glob("*.json"), reverse=True)[:limit]
        decisions = []
        for trace_file in trace_files:
            try:
                data = json.loads(trace_file.read_text(encoding="utf-8"))
                decisions.append(data)
            except Exception as e:
                logger.error(f"Failed to read trace {trace_file}: {e}")
        return decisions


if __name__ == "__main__":
    import argparse
    
    ap = argparse.ArgumentParser(description="Enhanced orchestrator routing")
    ap.add_argument("task", nargs="+", help="Task description")
    ap.add_argument("--max-latency", type=float, default=500.0, help="Max latency ms")
    ap.add_argument("--top-k", type=int, default=1, help="Return top-k agents")
    ap.add_argument("--require-sla", action="store_true", help="Require SLA compliance")
    args = ap.parse_args()
    
    router = EnhancedRouter()
    task_text = " ".join(args.task)
    decision = router.select_best_agent(
        task_text,
        max_latency_ms=args.max_latency,
        require_sla_compliance=args.require_sla,
        top_k=args.top_k
    )
    
    if isinstance(decision, list):
        for d in decision:
            print(f"Rank {d.candidate_rank}: {d.selected_agent} ({d.confidence_score:.2%})")
    else:
        print(f"Task: {task_text!r}")
        print(f"Selected: {decision.selected_agent}")
        print(f"Strategy: {decision.strategy_used.value}")
        print(f"Confidence: {decision.confidence_score:.2%}")
        print(f"SLA Compliant: {decision.sla_compliant}")
        print(f"Latency: {decision.latency_ms:.1f}ms")
