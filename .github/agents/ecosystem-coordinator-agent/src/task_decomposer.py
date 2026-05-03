"""Task Decomposer for Ecosystem Coordinator Agent"""
import random
from dataclasses import dataclass
from typing import Any

RANDOM_SEED = 51

@dataclass
class SubTask:
    name: str
    agent_type: str
    priority: int
    dependencies: list[str]

class TaskDecomposer:
    """Decompose complex tasks into sub-tasks"""

    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.tasks: list[SubTask] = []
        self.initialized = True

    def decompose(self, task_name: str, complexity: int) -> list[SubTask]:
        """Decompose task into sub-tasks"""
        subtasks = []
        for i in range(min(complexity, 5)):
            st = SubTask(
                name=f"{task_name}_sub{i+1}",
                agent_type=["analysis", "execution", "validation"][i % 3],
                priority=complexity - i,
                dependencies=[]
            )
            subtasks.append(st)
            self.tasks.append(st)
        return subtasks

    def get_metrics(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "total_tasks": len(self.tasks),
            "agent_types": {t: sum(1 for st in self.tasks if st.agent_type == t)
                           for t in ["analysis", "execution", "validation"]},
            "initialized": self.initialized
        }

def create_decomposer(seed: int = RANDOM_SEED) -> TaskDecomposer:
    return TaskDecomposer(seed=seed)
