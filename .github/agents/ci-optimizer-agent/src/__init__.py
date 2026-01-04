"""CI Optimizer Agent - Main Module"""
from typing import Dict, Any, Optional
import os
import random

try:
    from .test_prioritizer import TestPrioritizer, create_prioritizer
except ImportError:
    from test_prioritizer import TestPrioritizer, create_prioritizer

RANDOM_SEED = 49

class CIOptimizerAgent:
    """CI Optimizer Agent - V10 Custom Agent"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is None:
            seed = int(os.getenv('CI_OPTIMIZER_SEED', str(RANDOM_SEED)))
        self.seed = seed
        self._rng = random.Random(seed)
        self.test_prioritizer = create_prioritizer(seed)
        self.pda_state = {"perception": [], "decision": [], "action": [], "aftermath": []}
        self.performance_metrics = {"tests_optimized": 0, "time_saved_ms": 0.0}
        self.initialized = True
    
    def perceive(self, context: Dict[str, Any]) -> Dict[str, Any]:
        perception = {"timestamp": self._get_timestamp(), "context": context,
                     "prioritizer_metrics": self.test_prioritizer.get_metrics()}
        self.pda_state["perception"].append(perception)
        return perception
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        decision = {"timestamp": self._get_timestamp(), "action_type": "optimize",
                   "confidence": 0.9, "reasoning": ["Optimize test execution order"]}
        self.pda_state["decision"].append(decision)
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        result = {"timestamp": self._get_timestamp(), "action": decision["action_type"],
                 "status": "success", "outputs": ["Tests optimized"]}
        self.pda_state["action"].append(result)
        return result
    
    def aftermath(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        aftermath = {"timestamp": self._get_timestamp(), "success": action_result["status"] == "success",
                    "lessons_learned": ["Optimization successful"], "improvements_applied": []}
        self.pda_state["aftermath"].append(aftermath)
        return aftermath
    
    def optimize_tests(self, tests: list) -> list:
        for test in tests:
            self.test_prioritizer.add_test(test["name"], test["duration"], test.get("failure_rate", 0.1))
        return self.test_prioritizer.get_prioritized_order()
    
    def get_metrics(self) -> Dict[str, Any]:
        return {"agent_name": "ci-optimizer", "seed": self.seed,
                "pda_cycles": {k: len(v) for k, v in self.pda_state.items()},
                "components": {"test_prioritizer": self.test_prioritizer.get_metrics()},
                "performance_metrics": self.performance_metrics, "initialized": self.initialized}
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

def create_agent(seed: Optional[int] = None) -> CIOptimizerAgent:
    return CIOptimizerAgent(seed=seed)
