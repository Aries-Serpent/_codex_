"""Ecosystem Coordinator Agent - Main Module"""
from typing import Dict, Any, Optional
import os, random

try:
    from .task_decomposer import TaskDecomposer, create_decomposer
except ImportError:
    from task_decomposer import TaskDecomposer, create_decomposer

RANDOM_SEED = 51

class EcosystemCoordinatorAgent:
    """Ecosystem Coordinator Agent - V10 Custom Agent"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is None:
            seed = int(os.getenv('ECOSYSTEM_COORD_SEED', str(RANDOM_SEED)))
        self.seed = seed
        self._rng = random.Random(seed)
        self.task_decomposer = create_decomposer(seed)
        self.pda_state = {"perception": [], "decision": [], "action": [], "aftermath": []}
        self.performance_metrics = {"tasks_coordinated": 0}
        self.initialized = True
    
    def perceive(self, context: Dict[str, Any]) -> Dict[str, Any]:
        perception = {"timestamp": self._get_timestamp(), "context": context,
                     "decomposer_metrics": self.task_decomposer.get_metrics()}
        self.pda_state["perception"].append(perception)
        return perception
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        decision = {"timestamp": self._get_timestamp(), "action_type": "coordinate",
                   "confidence": 0.9, "reasoning": ["Coordinate multi-agent tasks"]}
        self.pda_state["decision"].append(decision)
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        result = {"timestamp": self._get_timestamp(), "action": decision["action_type"],
                 "status": "success", "outputs": ["Coordination complete"]}
        self.pda_state["action"].append(result)
        return result
    
    def aftermath(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        aftermath = {"timestamp": self._get_timestamp(), "success": action_result["status"] == "success",
                    "lessons_learned": ["Coordination improved"], "improvements_applied": []}
        self.pda_state["aftermath"].append(aftermath)
        return aftermath
    
    def coordinate_task(self, task_name: str, complexity: int) -> list:
        subtasks = self.task_decomposer.decompose(task_name, complexity)
        self.performance_metrics["tasks_coordinated"] += 1
        return subtasks
    
    def get_metrics(self) -> Dict[str, Any]:
        return {"agent_name": "ecosystem-coordinator", "seed": self.seed,
                "pda_cycles": {k: len(v) for k, v in self.pda_state.items()},
                "components": {"task_decomposer": self.task_decomposer.get_metrics()},
                "performance_metrics": self.performance_metrics, "initialized": self.initialized}
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

def create_agent(seed: Optional[int] = None) -> EcosystemCoordinatorAgent:
    return EcosystemCoordinatorAgent(seed=seed)
