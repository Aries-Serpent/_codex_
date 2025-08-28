from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Action:
    kind: str
    params: Dict[str, str]
    rationale: str
    priority: int  # 1(high) .. 5(low)


PRIORITY = {
    "FIX_PRECOMMIT": 1,
    "TEST_COVERAGE": 1,
    "AUDIT_REPO": 2,
    "BUILD_PIPELINE": 2,
    "PLAN_TASKS": 3,
}


def map_intents(intents) -> List[Action]:
    out: List[Action] = []
    for it in intents:
        prio = PRIORITY.get(it.name, 3)
        if it.name == "FIX_PRECOMMIT":
            out.append(
                Action(
                    "RUN_PRECOMMIT_VERBOSE",
                    {"cmd": "pre-commit run --all-files --verbose"},
                    "Diagnose slow/hanging hooks and capture outputs.",
                    prio,
                )
            )
        elif it.name == "TEST_COVERAGE":
            out.append(
                Action(
                    "ENSURE_PYTEST_COV",
                    {"pip": "pytest-cov", "flags": "--cov=src/codex_ml --cov-report=term"},
                    "Install plugin and enforce coverage flags.",
                    prio,
                )
            )
        elif it.name == "AUDIT_REPO":
            out.append(
                Action(
                    "GENERATE_AUDIT",
                    {"entry": "python tools/audit_builder.py --prompt-file AUDIT_PROMPT.md"},
                    "Use internal offline audit generator.",
                    prio,
                )
            )
        elif it.name == "BUILD_PIPELINE":
            out.append(Action("BUILD_DIGEST_PIPELINE", {}, "Compose the five-stage Codex Digest pipeline.", prio))
        elif it.name == "PLAN_TASKS":
            out.append(Action("SYNTHESIZE_TASKS", {}, "Aggregate, dedupe, and prioritize tasks.", prio))
    return sorted(out, key=lambda a: a.priority)
