"""Task Router — routes incoming tasks to appropriate agents by capability.

This module was identified as missing during the AAIS honest recalibration
(Session 24).  It uses the AGENT_REGISTRY capability_tags to route tasks
to the most-capable agent, with fallback to the cognitive brain pattern
store for historical success-rate data.

Usage
-----
::

    from codex.cognitive.task_router import TaskRouter, RoutingRequest

    router = TaskRouter()
    result = router.route(RoutingRequest(
        task_description="Fix failing CI check in embedding-index-rebuild.yml",
        tags=["ci_failure", "python_version"],
        urgency="high",
    ))
    logger.info(result.selected_agent)
    logger.info(result.confidence)
    logger.info(result.reasoning)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codex.logging.structured_logger import logger

_REGISTRY_PATH = Path(".github/agents/AGENT_REGISTRY.yaml")
_PATTERN_STORE = Path(".codex/cognitive_brain/pattern_learning_store.json")


@dataclass
class RoutingRequest:
    """Input to the task router."""

    task_description: str
    tags: list[str] = field(default_factory=list)
    urgency: str = "normal"  # "low" | "normal" | "high" | "critical"
    preferred_agent: str | None = None
    exclude_agents: list[str] = field(default_factory=list)


@dataclass
class RoutingResult:
    """Output of the task router."""

    selected_agent: str
    confidence: float  # 0.0 – 1.0
    reasoning: str
    alternative_agents: list[str] = field(default_factory=list)
    matched_tags: list[str] = field(default_factory=list)
    fallback_used: bool = False


class TaskRouter:
    """Routes tasks to agents using AGENT_REGISTRY capability_tags.

    Routing algorithm (priority order):
    1. If ``preferred_agent`` is set and active → use it directly (confidence=1.0)
    2. Tag intersection: agents with the most ``capability_tags`` overlap
    3. Pattern store success-rate tie-break
    4. Fallback: first active agent with any matching tag (confidence=0.3)
    5. Final fallback: ``ci-testing-agent`` (confidence=0.1)
    """

    _FALLBACK_AGENT = "ci-testing-agent"

    def __init__(
        self,
        registry_path: Path = _REGISTRY_PATH,
        pattern_store_path: Path = _PATTERN_STORE,
    ) -> None:
        self._registry: list[dict[str, Any]] = self._load_registry(registry_path)
        self._pattern_success: dict[str, float] = self._load_pattern_success(pattern_store_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(self, request: RoutingRequest) -> RoutingResult:
        """Route *request* to the best available agent."""
        # 1. Preferred agent override
        if request.preferred_agent:
            agent = self._find_agent(request.preferred_agent)
            if agent and self._is_active(agent):
                return RoutingResult(
                    selected_agent=request.preferred_agent,
                    confidence=1.0,
                    reasoning=f"Preferred agent '{request.preferred_agent}' is active.",
                )

        candidates = [
            a
            for a in self._registry
            if self._is_active(a) and a.get("name", "") not in request.exclude_agents
        ]

        if not candidates:
            return RoutingResult(
                selected_agent=self._FALLBACK_AGENT,
                confidence=0.1,
                reasoning="No active agents found; using default fallback.",
                fallback_used=True,
            )

        # 2. Score by tag intersection
        scored: list[tuple[float, list[str], dict[str, Any]]] = []
        for agent in candidates:
            agent_tags = set(agent.get("capability_tags", []))
            request_tags = {t.lower() for t in request.tags}
            matched = list(agent_tags & request_tags)
            score = 0.0 if not agent_tags else len(matched) / max(len(request_tags), 1)
            # 3. Pattern store success-rate tie-break
            name = agent.get("name", "")
            success_bonus = self._pattern_success.get(name, 0.0) * 0.1
            scored.append((score + success_bonus, matched, agent))

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_matched, best_agent = scored[0]

        agent_name = best_agent.get("name", self._FALLBACK_AGENT)

        if best_score == 0.0:
            # 4. Fallback — no tags matched
            return RoutingResult(
                selected_agent=agent_name,
                confidence=0.3,
                reasoning=(
                    f"No capability_tags matched for request tags {request.tags!r}. "
                    "Routing to highest-priority active agent."
                ),
                alternative_agents=[a.get("name", "") for _, _, a in scored[1:4]],
                fallback_used=True,
            )

        confidence = min(best_score, 1.0)
        reasoning = (
            f"Matched {len(best_matched)}/{len(request.tags)} capability_tags "
            f"({best_matched!r}) for agent '{agent_name}'."
        )

        return RoutingResult(
            selected_agent=agent_name,
            confidence=confidence,
            reasoning=reasoning,
            alternative_agents=[a.get("name", "") for _, _, a in scored[1:4]],
            matched_tags=best_matched,
        )

    def route_many(self, requests: list[RoutingRequest]) -> list[RoutingResult]:
        """Route a batch of requests."""
        return [self.route(r) for r in requests]

    def available_agents(self, tag: str | None = None) -> list[str]:
        """Return names of all active agents, optionally filtered by tag."""
        agents = [a for a in self._registry if self._is_active(a)]
        if tag:
            agents = [a for a in agents if tag in a.get("capability_tags", [])]
        return [a.get("name", "") for a in agents]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_registry(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            logger.warning("AGENT_REGISTRY not found at %s; routing degraded.", path)
            return []
        try:
            import yaml

            data = yaml.safe_load(path.read_text())
            return data.get("agents", []) if isinstance(data, dict) else []
        except (IOError, OSError):
            logger.exception("Failed to load AGENT_REGISTRY from %s", path)
            return []

    @staticmethod
    def _load_pattern_success(path: Path) -> dict[str, float]:
        """Return agent_name -> success_rate from pattern store learning_log."""
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text())
            log = data.get("learning_log", [])
            # Build success-rate keyed by agent_name recorded in each log entry.
            # (patterns_applied entries are pattern IDs, not agent identifiers.)
            counts: dict[str, list[int]] = {}
            for entry in log:
                agent = entry.get("agent_name", "")
                if not agent:
                    continue
                outcome = entry.get("outcome", "")
                if agent not in counts:
                    counts[agent] = [0, 0]
                counts[agent][1] += 1
                if "success" in outcome.lower():
                    counts[agent][0] += 1
            return {name: wins / total if total else 0.0 for name, (wins, total) in counts.items()}
        except (ValueError, TypeError, RuntimeError):
            logger.exception("Failed to load pattern success rates.")
            return {}

    def _find_agent(self, name: str) -> dict[str, Any] | None:
        for agent in self._registry:
            if agent.get("name", "").lower() == name.lower():
                return agent
        return None

    @staticmethod
    def _is_active(agent: dict[str, Any]) -> bool:
        status = agent.get("status", "active")
        return str(status).lower() not in {"deprecated", "disabled", "inactive"}
