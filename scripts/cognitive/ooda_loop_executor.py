#!/usr/bin/env python3
"""
OODA Loop Executor - Phase 10.3

Implements the complete Observe-Orient-Decide-Act (OODA) loop with:
- 4-phase cycle (Observe → Orient → Decide → Act)
- State machine with transaction support
- Concurrent execution (100+ parallel loops)
- Graceful degradation (4 fallback levels)
- Performance monitoring (< 200ms target)

Target Performance:
- Cycle time: < 200ms (99th percentile)
- Decision accuracy: > 95%
- Concurrent loops: > 100 parallel
- Integration test pass rate: > 99%
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import threading
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OODAPhase(Enum):
    """OODA cycle phase enumeration."""
    IDLE = "idle"
    OBSERVE = "observe"
    ORIENT = "orient"
    DECIDE = "decide"
    ACT = "act"
    FEEDBACK = "feedback"


class DegradationLevel(Enum):
    """Graceful degradation levels."""
    FULL_CONTEXT = "full_context"  # All sources available
    PATTERN_ONLY = "pattern_only"  # LTM available
    NO_CONTEXT = "no_context"  # Repository state only
    EMERGENCY = "emergency"  # Last known good strategy


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ObservationData:
    """Phase 1: OBSERVE - Current state snapshot."""
    timestamp: datetime
    repo_state: Dict[str, Any]
    task: Dict[str, Any]
    agent_state: Dict[str, Any]
    environment: Dict[str, Any]
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ContextData:
    """Phase 2: ORIENT - Context information."""
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    external: Dict[str, Any] = field(default_factory=dict)
    degradation_level: DegradationLevel = DegradationLevel.FULL_CONTEXT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class OrientationData:
    """Phase 2: ORIENT - Situation assessment output."""
    observation: ObservationData
    context: ContextData
    improvement_area: str
    urgency: float  # 0-1
    confidence: float  # 0-1
    risk_level: RiskLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "observation": self.observation.to_dict(),
            "context": self.context.to_dict(),
            "improvement_area": self.improvement_area,
            "urgency": self.urgency,
            "confidence": self.confidence,
            "risk_level": self.risk_level.value,
        }


@dataclass
class Strategy:
    """A candidate strategy for the decision phase."""
    id: str
    name: str
    description: str
    expected_success_rate: float
    estimated_duration_ms: int
    risk_level: RiskLevel
    guardrail_status: str  # "pass", "warn", "fail"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "expected_success_rate": self.expected_success_rate,
            "estimated_duration_ms": self.estimated_duration_ms,
            "risk_level": self.risk_level.value,
            "guardrail_status": self.guardrail_status,
        }


@dataclass
class DecisionData:
    """Phase 3: DECIDE - Strategy selection output."""
    orientation: OrientationData
    strategies: List[Strategy] = field(default_factory=list)
    selected_strategy: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    success_probability: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "orientation": self.orientation.to_dict(),
            "strategies": [s.to_dict() for s in self.strategies],
            "selected_strategy": self.selected_strategy,
            "confidence_score": self.confidence_score,
            "success_probability": self.success_probability,
        }


@dataclass
class ActionResult:
    """Phase 4: ACT - Execution result."""
    status: str  # "success", "partial", "failure"
    output: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class OODAState:
    """Complete OODA cycle state."""
    cycle_id: str
    phase: OODAPhase
    start_time: datetime
    observation: Optional[ObservationData] = None
    orientation: Optional[OrientationData] = None
    decision: Optional[DecisionData] = None
    action_result: Optional[ActionResult] = None
    metrics: Dict[str, float] = field(default_factory=dict)  # Phase timings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cycle_id": self.cycle_id,
            "phase": self.phase.value,
            "start_time": self.start_time.isoformat(),
            "observation": self.observation.to_dict() if self.observation else None,
            "orientation": self.orientation.to_dict() if self.orientation else None,
            "decision": self.decision.to_dict() if self.decision else None,
            "action_result": self.action_result.to_dict() if self.action_result else None,
            "metrics": self.metrics,
        }


class StateProvider(ABC):
    """Abstract base for state providers (repo, agent, environment)."""
    
    @abstractmethod
    def get_repo_state(self) -> Dict[str, Any]:
        """Get current repository state."""
        pass
    
    @abstractmethod
    def get_agent_state(self) -> Dict[str, Any]:
        """Get agent ecosystem state."""
        pass
    
    @abstractmethod
    def get_environment_state(self) -> Dict[str, Any]:
        """Get system environment state."""
        pass
    
    @abstractmethod
    def get_task_context(self, task_id: str) -> Dict[str, Any]:
        """Get task-specific context."""
        pass


class ContextProvider(ABC):
    """Abstract base for context providers."""
    
    @abstractmethod
    async def get_patterns(self, observation: ObservationData, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get similar patterns from LTM."""
        pass
    
    @abstractmethod
    async def get_sessions(self, task_type: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get relevant session contexts."""
        pass
    
    @abstractmethod
    async def get_external_context(self) -> Dict[str, Any]:
        """Get external context (GitHub, CI health, etc.)."""
        pass


class OODAExecutor:
    """Main OODA loop executor with 4 phases and concurrency support."""
    
    def __init__(
        self,
        state_provider: StateProvider,
        context_provider: Optional[ContextProvider] = None,
        max_concurrent_loops: int = 100,
    ):
        """
        Initialize OODA executor.
        
        Args:
            state_provider: Provider for repository/agent/environment state
            context_provider: Optional provider for context injection
            max_concurrent_loops: Maximum parallel OODA cycles
        """
        self.state_provider = state_provider
        self.context_provider = context_provider
        self.max_concurrent_loops = max_concurrent_loops
        
        # State management
        self.active_cycles: Dict[str, OODAState] = {}
        self.cycle_history: deque = deque(maxlen=1000)
        self.lock = threading.RLock()
        
        # Metrics
        self.metrics = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "phase_timings": {
                "observe": [],
                "orient": [],
                "decide": [],
                "act": [],
            },
        }
    
    async def execute_cycle(
        self,
        task_id: str,
        task_type: str,
        priority: str = "P2",
    ) -> OODAState:
        """
        Execute a complete OODA cycle.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task (ci_fix, ml_pattern, etc.)
            priority: Task priority (P0-P2)
        
        Returns:
            Complete OODAState with all phase results
        """
        cycle_id = str(uuid.uuid4())
        state = OODAState(cycle_id=cycle_id, phase=OODAPhase.OBSERVE, start_time=datetime.now())
        
        try:
            # Enforce concurrency limit
            while len(self.active_cycles) >= self.max_concurrent_loops:
                await asyncio.sleep(0.01)
            
            with self.lock:
                self.active_cycles[cycle_id] = state
            
            # Phase 1: Observe (target < 50ms)
            logger.info(f"[{cycle_id}] Starting OBSERVE phase")
            state.observation = await self._observe(task_id, task_type)
            state.metrics["observe_ms"] = (datetime.now() - state.start_time).total_seconds() * 1000
            logger.info(f"[{cycle_id}] OBSERVE phase: {state.metrics['observe_ms']:.1f}ms")
            
            # Phase 2: Orient (target < 50ms)
            state.phase = OODAPhase.ORIENT
            state.orientation = await self._orient(state.observation)
            state.metrics["orient_ms"] = (
                (datetime.now() - state.start_time).total_seconds() * 1000 - 
                state.metrics["observe_ms"]
            )
            logger.info(f"[{cycle_id}] ORIENT phase: {state.metrics['orient_ms']:.1f}ms")
            
            # Phase 3: Decide (target < 50ms)
            state.phase = OODAPhase.DECIDE
            state.decision = await self._decide(state.orientation, priority)
            state.metrics["decide_ms"] = (
                (datetime.now() - state.start_time).total_seconds() * 1000 - 
                state.metrics["observe_ms"] - state.metrics["orient_ms"]
            )
            logger.info(f"[{cycle_id}] DECIDE phase: {state.metrics['decide_ms']:.1f}ms")
            
            # Phase 4: Act (target < 50ms)
            state.phase = OODAPhase.ACT
            state.action_result = await self._act(state.decision)
            state.metrics["act_ms"] = (
                (datetime.now() - state.start_time).total_seconds() * 1000 - 
                state.metrics["observe_ms"] - state.metrics["orient_ms"] - state.metrics["decide_ms"]
            )
            total_ms = state.metrics["observe_ms"] + state.metrics["orient_ms"] + state.metrics["decide_ms"] + state.metrics["act_ms"]
            logger.info(f"[{cycle_id}] ACT phase: {state.metrics['act_ms']:.1f}ms (total cycle: {total_ms:.1f}ms)")
            
            # Record metrics
            with self.lock:
                self.metrics["total_cycles"] += 1
                if state.action_result.status in ["success", "partial"]:
                    self.metrics["successful_cycles"] += 1
                    self.metrics["phase_timings"]["observe"].append(state.metrics["observe_ms"])
                    self.metrics["phase_timings"]["orient"].append(state.metrics["orient_ms"])
                    self.metrics["phase_timings"]["decide"].append(state.metrics["decide_ms"])
                    self.metrics["phase_timings"]["act"].append(state.metrics["act_ms"])
                self.cycle_history.append(state)
            
            state.phase = OODAPhase.FEEDBACK
            return state
            
        except Exception as e:
            logger.error(f"[{cycle_id}] OODA cycle failed: {e}", exc_info=True)
            state.action_result = ActionResult(
                status="failure",
                errors=[str(e)],
                execution_time_ms=(datetime.now() - state.start_time).total_seconds() * 1000,
            )
            return state
        finally:
            with self.lock:
                self.active_cycles.pop(cycle_id, None)
    
    async def _observe(self, task_id: str, task_type: str) -> ObservationData:
        """Phase 1: Collect current state (target < 50ms)."""
        start_time = datetime.now()
        
        # Collect state from providers
        repo_state = self.state_provider.get_repo_state()
        agent_state = self.state_provider.get_agent_state()
        environment = self.state_provider.get_environment_state()
        task = self.state_provider.get_task_context(task_id)
        task["type"] = task_type
        
        observation = ObservationData(
            timestamp=datetime.now(),
            repo_state=repo_state,
            task=task,
            agent_state=agent_state,
            environment=environment,
            events=[],  # Would be populated from session log in production
        )
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        if elapsed > 50:
            logger.warning(f"OBSERVE phase exceeded 50ms target: {elapsed:.1f}ms")
        
        return observation
    
    async def _orient(self, observation: ObservationData) -> OrientationData:
        """Phase 2: Inject context and assess situation (target < 50ms)."""
        start_time = datetime.now()
        
        # Determine degradation level and get context
        context = ContextData()
        degradation_level = DegradationLevel.FULL_CONTEXT
        
        try:
            # Try to get context from all sources
            if self.context_provider:
                patterns = await asyncio.wait_for(
                    self.context_provider.get_patterns(observation, top_k=5),
                    timeout=0.03
                )
                context.patterns = patterns
                
                sessions = await asyncio.wait_for(
                    self.context_provider.get_sessions(observation.task.get("type", ""), limit=3),
                    timeout=0.03
                )
                context.sessions = sessions
                
                external = await asyncio.wait_for(
                    self.context_provider.get_external_context(),
                    timeout=0.02
                )
                context.external = external
            else:
                degradation_level = DegradationLevel.NO_CONTEXT
        except asyncio.TimeoutError:
            logger.warning("Context injection timeout - degrading to pattern-only mode")
            degradation_level = DegradationLevel.PATTERN_ONLY
        except Exception as e:
            logger.warning(f"Context injection failed: {e} - degrading to no-context mode")
            degradation_level = DegradationLevel.NO_CONTEXT
        
        context.degradation_level = degradation_level
        
        # Assess situation
        improvement_area = observation.task.get("type", "unknown")
        urgency = float(observation.agent_state.get("queue_depth", 0) > 10)
        confidence = float(len(context.patterns) > 0) * 0.6 + float(len(context.sessions) > 0) * 0.4
        risk_level = RiskLevel.LOW if confidence > 0.7 else RiskLevel.MEDIUM if confidence > 0.4 else RiskLevel.HIGH
        
        orientation = OrientationData(
            observation=observation,
            context=context,
            improvement_area=improvement_area,
            urgency=urgency,
            confidence=confidence,
            risk_level=risk_level,
        )
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        if elapsed > 50:
            logger.warning(f"ORIENT phase exceeded 50ms target: {elapsed:.1f}ms")
        
        return orientation
    
    async def _decide(self, orientation: OrientationData, priority: str) -> DecisionData:
        """Phase 3: Select strategy with confidence scoring (target < 50ms)."""
        start_time = datetime.now()
        
        decision = DecisionData(orientation=orientation)
        
        # Generate candidate strategies based on degradation level
        if orientation.context.degradation_level == DegradationLevel.FULL_CONTEXT:
            strategies = self._generate_full_context_strategies(orientation)
        elif orientation.context.degradation_level == DegradationLevel.PATTERN_ONLY:
            strategies = self._generate_pattern_only_strategies(orientation)
        elif orientation.context.degradation_level == DegradationLevel.NO_CONTEXT:
            strategies = self._generate_default_strategies(orientation)
        else:
            strategies = self._generate_emergency_strategy(orientation)
        
        decision.strategies = strategies
        
        # Select best strategy
        if strategies:
            selected = strategies[0]  # First strategy (already sorted by success rate)
            decision.selected_strategy = {
                "id": selected.id,
                "name": selected.name,
                "description": selected.description,
                "action_plan": [
                    {"step": 1, "description": "Execute selected strategy", "agent_type": "semantic-router"},
                ],
                "confidence_score": orientation.confidence,
                "success_probability": selected.expected_success_rate,
                "estimated_duration_ms": selected.estimated_duration_ms,
            }
            decision.confidence_score = orientation.confidence
            decision.success_probability = selected.expected_success_rate
        else:
            decision.selected_strategy = self._create_fallback_strategy()
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        if elapsed > 50:
            logger.warning(f"DECIDE phase exceeded 50ms target: {elapsed:.1f}ms")
        
        return decision
    
    async def _act(self, decision: DecisionData) -> ActionResult:
        """Phase 4: Execute strategy and collect feedback (target < 50ms)."""
        start_time = datetime.now()
        
        if not decision.selected_strategy:
            return ActionResult(status="failure", errors=["No strategy selected"])
        
        # In production, this would dispatch to semantic router and execute agents
        # For now, simulate execution
        await asyncio.sleep(0.001)  # Minimal overhead
        
        result = ActionResult(
            status="success",
            output={
                "strategy": decision.selected_strategy.get("name"),
                "simulated": True,
            },
            execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            metrics={
                "success_rate": decision.success_probability,
                "confidence": decision.confidence_score,
            },
        )
        
        elapsed = result.execution_time_ms
        if elapsed > 50:
            logger.warning(f"ACT phase exceeded 50ms target: {elapsed:.1f}ms")
        
        return result
    
    def _generate_full_context_strategies(self, orientation: OrientationData) -> List[Strategy]:
        """Generate strategies using full context."""
        strategies = []
        
        # Strategy 1: Follow top pattern
        if orientation.context.patterns:
            pattern = orientation.context.patterns[0]
            strategies.append(Strategy(
                id="pattern_follow",
                name=f"Follow pattern: {pattern.get('name', 'Unknown')}",
                description=f"Execute top-matching historical pattern (similarity: {pattern.get('similarity', 0):.2f})",
                expected_success_rate=pattern.get("success_rate", 0.8),
                estimated_duration_ms=300,
                risk_level=RiskLevel.LOW if pattern.get("success_rate", 0) > 0.8 else RiskLevel.MEDIUM,
                guardrail_status="pass",
            ))
        
        # Strategy 2: Session replay
        if orientation.context.sessions:
            session = orientation.context.sessions[0]
            strategies.append(Strategy(
                id="session_replay",
                name=f"Replay session: {session.get('session_id', 'Unknown')[:8]}",
                description="Replay successful session with similar task",
                expected_success_rate=0.85,
                estimated_duration_ms=250,
                risk_level=RiskLevel.LOW,
                guardrail_status="pass",
            ))
        
        # Strategy 3: Combined approach
        strategies.append(Strategy(
            id="combined",
            name="Combined pattern + session approach",
            description="Execute pattern with session modifications",
            expected_success_rate=0.80,
            estimated_duration_ms=350,
            risk_level=RiskLevel.LOW,
            guardrail_status="pass",
        ))
        
        # Sort by expected success rate (descending)
        strategies.sort(key=lambda s: s.expected_success_rate, reverse=True)
        return strategies
    
    def _generate_pattern_only_strategies(self, orientation: OrientationData) -> List[Strategy]:
        """Generate strategies using pattern context only."""
        strategies = []
        
        if orientation.context.patterns:
            pattern = orientation.context.patterns[0]
            strategies.append(Strategy(
                id="pattern_follow",
                name=f"Follow pattern: {pattern.get('name', 'Unknown')}",
                description="Execute top-matching historical pattern",
                expected_success_rate=pattern.get("success_rate", 0.7),
                estimated_duration_ms=200,
                risk_level=RiskLevel.MEDIUM,
                guardrail_status="pass",
            ))
        
        strategies.append(Strategy(
            id="conservative",
            name="Conservative safe strategy",
            description="Execute minimal, low-risk action",
            expected_success_rate=0.6,
            estimated_duration_ms=100,
            risk_level=RiskLevel.LOW,
            guardrail_status="pass",
        ))
        
        strategies.sort(key=lambda s: s.expected_success_rate, reverse=True)
        return strategies
    
    def _generate_default_strategies(self, orientation: OrientationData) -> List[Strategy]:
        """Generate default strategies without context."""
        return [
            Strategy(
                id="default_safe",
                name="Default safe strategy",
                description="Minimal action based on task type",
                expected_success_rate=0.5,
                estimated_duration_ms=100,
                risk_level=RiskLevel.MEDIUM,
                guardrail_status="pass",
            ),
        ]
    
    def _generate_emergency_strategy(self, orientation: OrientationData) -> List[Strategy]:
        """Generate emergency fallback strategy."""
        return [
            Strategy(
                id="emergency",
                name="Emergency fallback",
                description="Last known good strategy",
                expected_success_rate=0.3,
                estimated_duration_ms=50,
                risk_level=RiskLevel.HIGH,
                guardrail_status="warn",
            ),
        ]
    
    def _create_fallback_strategy(self) -> Dict[str, Any]:
        """Create fallback strategy when none available."""
        return {
            "id": "fallback",
            "name": "Fallback strategy",
            "description": "Emergency fallback - log and escalate",
            "action_plan": [
                {"step": 1, "description": "Log error and escalate to Track 10.1", "agent_type": "escalation"},
            ],
            "confidence_score": 0.1,
            "success_probability": 0.2,
            "estimated_duration_ms": 50,
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated OODA metrics."""
        with self.lock:
            metrics = dict(self.metrics)
            metrics["active_cycles"] = len(self.active_cycles)
            
            # Calculate percentiles for phase timings
            for phase in ["observe", "orient", "decide", "act"]:
                timings = metrics["phase_timings"][phase]
                if timings:
                    timings_sorted = sorted(timings)
                    metrics[f"{phase}_p50_ms"] = timings_sorted[len(timings_sorted) // 2]
                    metrics[f"{phase}_p99_ms"] = timings_sorted[int(len(timings_sorted) * 0.99)]
                    metrics[f"{phase}_max_ms"] = max(timings)
        
        return metrics


def main():
    """Demo OODA executor usage."""
    
    # Mock state provider
    class MockStateProvider(StateProvider):
        def get_repo_state(self) -> Dict[str, Any]:
            return {"branch": "main", "uncommitted_changes": 0, "test_status": "passing"}
        
        def get_agent_state(self) -> Dict[str, Any]:
            return {"health": 0.95, "queue_depth": 5, "performance": {"success_rate": 0.9}}
        
        def get_environment_state(self) -> Dict[str, Any]:
            return {"ci_health": 0.8, "resource_utilization": {"cpu": 0.4, "memory": 0.6}}
        
        def get_task_context(self, task_id: str) -> Dict[str, Any]:
            return {"id": task_id, "priority": "P1", "dependencies": []}
    
    # Initialize executor
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    # Run sample cycle
    async def demo():
        print("=" * 60)
        print("OODA Loop Executor Demo")
        print("=" * 60)
        
        state = await executor.execute_cycle(
            task_id="sample_task_001",
            task_type="ci_fix",
            priority="P1",
        )
        
        print(f"\nCycle ID: {state.cycle_id}")
        print(f"Phase: {state.phase.value}")
        print(f"Metrics: {state.metrics}")
        print(f"Final Result: {state.action_result.status}")
        print("\nAggregate Metrics:")
        print(json.dumps(executor.get_metrics(), indent=2, default=str))
    
    asyncio.run(demo())


if __name__ == "__main__":
    main()
