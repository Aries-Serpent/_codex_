"""
GitHub Guru Agent — Cognitive Brain Adapter

Bridges GitHubGuruAgent to the cognitive brain Planner ABC via
LegacyAgentAdapter. Implements the full OODA loop:
  Observe → Orient → Decide → Act → Reflect

Physics scoring equation applied:
  Score = (Impact × Confidence × Momentum) / (Energy × (1 + Risk) × (1 + Friction))
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Locate repo root and inject into sys.path for cognitive brain imports
_here = Path(__file__).resolve()
_repo_root = _here.parents[3]  # .github/agents/github-guru-agent/ → repo root
if str(_repo_root / "src") not in sys.path:
    sys.path.insert(0, str(_repo_root / "src"))
if str(_repo_root / "agents") not in sys.path:
    sys.path.insert(0, str(_repo_root / "agents"))

try:
    from cognitive_brain.base import (  # type: ignore[import]  # noqa: I001
        ActionResult,
        Decision,
        ObservationData,
        OrientationResult,
        Planner,
    )
    from cognitive_adapter import SimpleDictMemory  # type: ignore[import]  # noqa: F401
    _COGNITIVE_BRAIN_AVAILABLE = True
    logger.debug("Cognitive brain ABCs available (available=%s)", _COGNITIVE_BRAIN_AVAILABLE)
except ImportError:
    _COGNITIVE_BRAIN_AVAILABLE = False
    logger.debug("Cognitive brain ABCs not available (available=%s); using inline stubs", _COGNITIVE_BRAIN_AVAILABLE)

    # ---- Inline stubs so the module is importable without the full repo --------
    from abc import ABC, abstractmethod  # noqa: I001
    from dataclasses import dataclass

    @dataclass
    class ObservationData:  # type: ignore[no-redef]
        timestamp: datetime
        source: str
        data: dict[str, Any]
        metadata: Optional[dict[str, Any]] = None

    @dataclass
    class OrientationResult:  # type: ignore[no-redef]
        context: dict[str, Any]
        analysis: str
        confidence: float
        alternatives: list[dict[str, Any]]

    @dataclass
    class Decision:  # type: ignore[no-redef]
        action: str
        parameters: dict[str, Any]
        reasoning: str
        confidence: float
        timestamp: datetime

    @dataclass
    class ActionResult:  # type: ignore[no-redef]
        success: bool
        output: Any
        metrics: dict[str, float]
        errors: list[str]

    class Planner(ABC):  # type: ignore[no-redef]
        @abstractmethod
        def observe(self, input_data: dict[str, Any]) -> "ObservationData":
            raise NotImplementedError
        @abstractmethod
        def orient(self, observation: "ObservationData") -> "OrientationResult":
            raise NotImplementedError
        @abstractmethod
        def decide(self, orientation: "OrientationResult") -> "Decision":
            raise NotImplementedError
        @abstractmethod
        def act(self, decision: "Decision") -> "ActionResult":
            raise NotImplementedError

    class SimpleDictMemory:  # type: ignore[no-redef]
        def __init__(self) -> None:
            self._storage: dict[str, Any] = {}

        def store(self, key: str, value: Any, **_kw: Any) -> bool:
            self._storage[key] = value
            return True

        def retrieve(self, key: str) -> Optional[Any]:
            return self._storage.get(key)

        def search(self, query: dict[str, Any], limit: int = 10) -> list[Any]:
            return []


def _physics_score(
    impact: float,
    confidence: float,
    momentum: float,
    energy: float,
    risk: float,
    friction: float,
) -> float:
    """
    Apply the physics scoring equation.

    Score = (Impact × Confidence × Momentum) / (Energy × (1 + Risk) × (1 + Friction))

    All inputs should be normalised to reasonable ranges; returns 0–∞ (higher = better path).
    """
    denominator = energy * (1.0 + risk) * (1.0 + friction)
    if denominator <= 0:
        return 0.0
    return (impact * confidence * momentum) / denominator


class GitHubGuruAdapter(Planner):
    """
    Bridges GitHubGuruAgent to the cognitive brain Planner ABC.

    Wraps the agent in the full OODA + Reflect loop so it participates
    in orchestrated multi-agent workflows via PhysicsInspiredOrchestrator.
    """

    # Capability physics parameters (used for routing score)
    _CAPABILITY_PHYSICS: dict[str, dict[str, float]] = {
        "pr_analysis":                 {"impact": 0.9, "energy": 20, "risk": 0.1, "friction": 2},
        "issue_triage":                {"impact": 0.8, "energy": 15, "risk": 0.1, "friction": 1},
        "workflow_health_monitoring":  {"impact": 0.85, "energy": 25, "risk": 0.15, "friction": 3},
        "branch_governance":           {"impact": 0.5, "energy": 10, "risk": 0.05, "friction": 1},
        "contributor_intelligence":    {"impact": 0.6, "energy": 12, "risk": 0.05, "friction": 2},
        "repository_hygiene_reporting":{"impact": 0.7, "energy": 18, "risk": 0.1, "friction": 2},
        "codebase_navigation_guidance":{"impact": 0.4, "energy": 5,  "risk": 0.0, "friction": 0},
        "dependency_drift_detection":  {"impact": 0.75, "energy": 20, "risk": 0.2, "friction": 2},
        "stale_resource_detection":    {"impact": 0.5, "energy": 10, "risk": 0.05, "friction": 1},
        "label_taxonomy_enforcement":  {"impact": 0.55, "energy": 8,  "risk": 0.0, "friction": 1},
        "create_copilot_pr":           {"impact": 0.95, "energy": 10, "risk": 0.2, "friction": 1},
    }

    def __init__(self, guru_agent: Any):
        self.guru_agent = guru_agent
        self.memory = SimpleDictMemory()
        self._reflection_log: list[dict[str, Any]] = []

    # ---- OODA loop implementation ----------------------------------------------

    def observe(self, input_data: dict[str, Any]) -> ObservationData:
        """
        Observe: Wrap GitHub event payload in ObservationData.

        Extracts event_type, entity_id, and capability hint from input.
        """
        self.memory.store("last_observation", input_data)
        return ObservationData(
            timestamp=datetime.now(tz=timezone.utc),
            source="github_event",
            data=input_data,
            metadata={
                "agent": "GitHubGuruAgent",
                "event_type": input_data.get("event_type", "unknown"),
                "entity_id": input_data.get("entity_id"),
            },
        )

    def orient(self, observation: ObservationData) -> OrientationResult:
        """
        Orient: Map observation to the best capability using physics scoring.

        Evaluates all capabilities and scores them by impact/energy ratio.
        """
        event_type = observation.data.get("event_type", "")
        momentum = observation.data.get("urgency", 5.0)  # 1–10

        # Score each capability
        scored: list[dict[str, Any]] = []
        for cap, params in self._CAPABILITY_PHYSICS.items():
            # Confidence from event→capability alignment
            confidence = self._event_capability_confidence(event_type, cap)
            score = _physics_score(
                impact=params["impact"],
                confidence=confidence,
                momentum=momentum,
                energy=params["energy"],
                risk=params["risk"],
                friction=params["friction"],
            )
            scored.append({"capability": cap, "score": score, "confidence": confidence})

        scored.sort(key=lambda x: x["score"], reverse=True)
        best = scored[0] if scored else {"capability": "pr_analysis", "score": 0.0, "confidence": 0.5}

        analysis = (
            f"Event '{event_type}' routed to capability '{best['capability']}' "
            f"(score={best['score']:.3f}, confidence={best['confidence']:.2f})"
        )

        return OrientationResult(
            context={
                "capability": best["capability"],
                "observation": observation.data,
                "alternatives": scored[1:3],
            },
            analysis=analysis,
            confidence=best["confidence"],
            alternatives=scored[1:3],
        )

    def decide(self, orientation: OrientationResult) -> Decision:
        """
        Decide: Commit to a capability and prepare parameters.

        Falls back to pr_analysis if confidence is too low.
        """
        capability = orientation.context.get("capability", "pr_analysis")
        confidence = orientation.confidence

        # Below threshold → fall back to repository hygiene (low-risk default)
        if confidence < 0.3:
            capability = "repository_hygiene_reporting"

        return Decision(
            action=capability,
            parameters=orientation.context.get("observation", {}),
            reasoning=orientation.analysis,
            confidence=confidence,
            timestamp=datetime.now(tz=timezone.utc),
        )

    def act(self, decision: Decision) -> ActionResult:
        """
        Act: Execute the selected capability on the GitHubGuruAgent.

        Maps action name to the corresponding agent method.
        """
        capability = decision.action
        params = decision.parameters
        errors: list[str] = []
        output: Any = None

        try:
            if hasattr(self.guru_agent, capability):
                method = getattr(self.guru_agent, capability)
                output = method(**params) if params else method()
            elif hasattr(self.guru_agent, "handle_event"):
                output = self.guru_agent.handle_event({
                    "capability": capability,
                    **params,
                })
            else:
                errors.append(f"GitHubGuruAgent has no method '{capability}'")
        except Exception as exc:
            logger.error("Capability '%s' failed: %s", capability, exc)
            errors.append(str(exc))

        return ActionResult(
            success=len(errors) == 0,
            output=output,
            metrics={"capability_energy": self._CAPABILITY_PHYSICS.get(capability, {}).get("energy", 0)},
            errors=errors,
        )

    def reflect(self, result: ActionResult) -> None:
        """
        Reflect: Record outcome for self-appraisal and pattern refinement.

        Stores lesson in memory and reflection log.
        """
        entry = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "success": result.success,
            "errors": result.errors,
            "metrics": result.metrics,
        }
        self._reflection_log.append(entry)
        self.memory.store(f"reflection_{len(self._reflection_log)}", entry)
        if not result.success:
            logger.warning("Reflection: action failed — %s", result.errors)

    def ooda_loop(self, input_data: dict[str, Any]) -> ActionResult:
        """Execute the full OODA + Reflect loop."""
        obs = self.observe(input_data)
        ori = self.orient(obs)
        dec = self.decide(ori)
        res = self.act(dec)
        self.reflect(res)
        return res

    def get_reflection_log(self) -> list[dict[str, Any]]:
        """Return the accumulated reflection log."""
        return list(self._reflection_log)

    def physics_score_for(self, capability: str, urgency: float = 5.0) -> float:
        """Compute physics score for a specific capability at a given urgency."""
        params = self._CAPABILITY_PHYSICS.get(capability)
        if not params:
            return 0.0
        return _physics_score(
            impact=params["impact"],
            confidence=1.0,
            momentum=urgency,
            energy=params["energy"],
            risk=params["risk"],
            friction=params["friction"],
        )

    # ---- Helpers ---------------------------------------------------------------

    def create_copilot_pr(
        self,
        title: str,
        head_branch: str,
        base_branch: str = "main",
        copilot_task: str = "",
        body: str = "",
        owner: str = "Aries-Serpent",
        repo: str = "_codex_",
        github_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a GitHub Pull Request whose body starts with ``@copilot <task>``
        to trigger a GitHub Copilot autonomous agent session.

        The PR body is prefixed with the ``@copilot`` mention so GitHub routes
        the request to the Copilot coding agent immediately on PR creation.

        Args:
            title: PR title (e.g. "fix: remediate P0 CodeQL alerts").
            head_branch: Branch containing the changes (created externally).
            base_branch: Target branch (default "main").
            copilot_task: Task description appended to the @copilot mention.
                          e.g. "Remediate all P0 sql-injection alerts."
            body: Additional PR body content appended after the @copilot line.
            owner: GitHub repository owner.
            repo: GitHub repository name.
            github_token: Personal access token (falls back to env GITHUB_TOKEN).

        Returns:
            Dict with keys: pr_url, pr_number, copilot_triggered (bool), errors.
        """
        token = github_token or os.environ.get("GITHUB_TOKEN", "")
        errors: list[str] = []

        # Build @copilot-triggered body
        copilot_line = f"@copilot {copilot_task}".strip()
        full_body = f"{copilot_line}\n\n{body}".strip() if body else copilot_line

        if not token:
            errors.append("GITHUB_TOKEN not set; cannot create PR")
            return {"pr_url": None, "pr_number": None, "copilot_triggered": False, "errors": errors}

        try:
            payload = json.dumps({
                "title": title,
                "body": full_body,
                "head": head_branch,
                "base": base_branch,
            }).encode()

            req = urllib.request.Request(
                url=f"https://api.github.com/repos/{owner}/{repo}/pulls",
                data=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                pr_url = data.get("html_url")
                pr_number = data.get("number")
                logger.info("Created Copilot PR #%s: %s", pr_number, pr_url)
                return {
                    "pr_url": pr_url,
                    "pr_number": pr_number,
                    "copilot_triggered": True,
                    "errors": [],
                }
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode(errors="replace") if exc.fp else ""
            errors.append(f"HTTP {exc.code} from GitHub API: {body_text[:200]}")
            logger.error("create_copilot_pr HTTP error %s: %s", exc.code, body_text[:200])
        except urllib.error.URLError as exc:
            errors.append(f"Network error creating PR: {exc.reason}")
            logger.error("create_copilot_pr network error: %s", exc.reason)
        except Exception as exc:
            errors.append(f"PR creation failed: {exc}")
            logger.error("create_copilot_pr unexpected error: %s", exc)
        return {"pr_url": None, "pr_number": None, "copilot_triggered": False, "errors": errors}

    @staticmethod
    def _event_capability_confidence(event_type: str, capability: str) -> float:
        """Return confidence that event_type maps to capability."""
        _EVENT_MAP: dict[str, list[str]] = {
            "pull_request": ["pr_analysis", "label_taxonomy_enforcement"],
            "issues": ["issue_triage", "label_taxonomy_enforcement"],
            "workflow_run": ["workflow_health_monitoring"],
            "push": ["branch_governance", "repository_hygiene_reporting"],
            "schedule": [
                "workflow_health_monitoring",
                "stale_resource_detection",
                "dependency_drift_detection",
                "repository_hygiene_reporting",
                "branch_governance",
            ],
            "workflow_dispatch": [
                "pr_analysis",
                "issue_triage",
                "workflow_health_monitoring",
                "repository_hygiene_reporting",
                "dependency_drift_detection",
                "create_copilot_pr",
            ],
        }
        mapped = _EVENT_MAP.get(event_type, [])
        if not mapped:
            return 0.2  # unknown event: low confidence
        if capability in mapped:
            return 0.9 if mapped.index(capability) == 0 else 0.6
        return 0.1
