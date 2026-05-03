from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlanStep:
    name: str
    action_kind: str
    params: dict[str, str]
    requires: list[str] = field(default_factory=list)


@dataclass
class Plan:
    steps: list[PlanStep]


def compose_workflow(actions) -> Plan:
    steps: list[PlanStep] = []
    for a in actions:
        reqs: list[str] = []
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


def execute_step(step: PlanStep, env: dict[str, str]) -> dict[str, str]:
    return {"status": "ok", "step": step.name, "action": step.action_kind, "params": step.params}
