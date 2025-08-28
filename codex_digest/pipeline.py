from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List
from .tokenizer import DefaultTokenizer
from .semparser import SemParser
from .mapper import map_intents
from .workflow import compose_workflow, execute_step
from .utils import redact, five_whys, pick_best


@dataclass
class PipelineOutput:
    tasks_md: str
    plan_json: Dict[str, Any]
    convergence: float
    opportunity_areas: List[str]


class CodexPipeline:
    def __init__(self) -> None:
        self.tk = DefaultTokenizer()
        self.sp = SemParser()

    def run(self, context: str, description: str, dry_run: bool = True) -> PipelineOutput:
        x0 = self.tk.normalize(context + " " + description)
        tokens = self.tk.tokenize(x0)

        pr = self.sp.parse(x0)
        if not pr.intents:
            return PipelineOutput(
                tasks_md="No intents detected.",
                plan_json={},
                convergence=0.0,
                opportunity_areas=[
                    "Tokenization rules insufficient for domain vocabulary.",
                    "Add patterns for repo audit / CI / testing / reproducibility.",
                ],
            )

        cand = [(i.name, i.confidence) for i in pr.intents[:3]]
        best_name, best_score = pick_best(cand)

        actions = map_intents(pr.intents)
        plan = compose_workflow(actions)

        results = []
        for st in plan.steps:
            results.append(execute_step(st, env={}))

        lines = ["# Codex Digest — Organized Task Plan", "", "## Prioritized Tasks"]
        for step in plan.steps:
            lines.append(f"- **{step.action_kind}** → {redact(str(step.params))}")
        lines += ["", "## Key Entities", f"- {', '.join(pr.key_entities) or '(none)'}"]
        lines += ["", "## Intents (scored)"]
        for nm, sc in cand:
            lines.append(f"- {nm}: {sc:.2f}")

        conv = min(1.0, 0.5 * best_score + 0.1 * len(actions))
        opp: List[str] = []
        if conv < 0.7:
            opp = five_whys("Low convergence between detected intents and actions")

        return PipelineOutput(
            tasks_md="\n".join(lines),
            plan_json={"steps": [s.__dict__ for s in plan.steps], "results": results},
            convergence=conv,
            opportunity_areas=opp,
        )


def run_pipeline(context: str, description: str, dry_run: bool = True) -> PipelineOutput:
    return CodexPipeline().run(context, description, dry_run=dry_run)
