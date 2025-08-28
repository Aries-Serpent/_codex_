from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class PlanStep:
    name: str
    action_kind: str
    params: Dict[str, str]
    requires: List[str] = field(default_factory=list)


@dataclass
class Plan:
    steps: List[PlanStep]


def compose_workflow(actions) -> Plan:
    idx = {a.kind: i for i, a in enumerate(actions)}
    steps: List[PlanStep] = []
    for a in actions:
        reqs: List[str] = []
        if a.kind == "ENSURE_PYTEST_COV":
            reqs.append("RUN_PRECOMMIT_VERBOSE")
        steps.append(
            PlanStep(
                name=f"step_{len(steps)+1}",
                action_kind=a.kind,
                params=a.params,
                requires=reqs,
            )
        )
    return Plan(steps=steps)


def execute_step(step: PlanStep, env: Dict[str, str]) -> Dict[str, str]:
    return {"status": "ok", "step": step.name, "action": step.action_kind, "params": step.params}
