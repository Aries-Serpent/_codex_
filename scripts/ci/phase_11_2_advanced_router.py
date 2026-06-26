#!/usr/bin/env python3
"""
Phase 11.2 — Advanced Agent Router
====================================
Semantic task classification + confidence-based routing engine for the 145-agent ecosystem.

Implements:
- Domain keyword matching with configurable weight
- Cosine-similarity semantic routing (pure-Python, no external FAISS dependency at runtime)
- Confidence-based approval gates (auto-approve ≥ 90%, review 75-89%, escalate <75%)
- 3-agent fallback chain
- Structured JSON routing decisions

Usage::

    python scripts/ci/phase_11_2_advanced_router.py --task "fix CI coverage failures"
    python scripts/ci/phase_11_2_advanced_router.py --task "security scan" --json
    python scripts/ci/phase_11_2_advanced_router.py --batch tasks.json
    python scripts/ci/phase_11_2_advanced_router.py --self-test
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class AgentProfile:
    """Lightweight agent profile for routing purposes."""

    agent_id: str
    name: str
    category: str
    keywords: List[str]
    fallback_agents: List[str] = field(default_factory=list)
    # Embedding vector (unit-normalised TF representation, computed lazily)
    _embedding: Optional[List[float]] = field(default=None, repr=False, compare=False)

    def embedding(self, vocab: Dict[str, int]) -> List[float]:
        if self._embedding is None:
            self._embedding = _build_embedding(self.keywords, vocab)
        return self._embedding


@dataclass
class RoutingDecision:
    """A single routing decision with confidence and approval gate."""

    task: str
    primary_agent: str
    confidence: float  # 0–100
    approval_gate: str  # "auto-approve" | "human-review" | "escalate"
    fallback_chain: List[str]
    routing_latency_ms: float
    timestamp: str
    keyword_score: float
    semantic_score: float
    top_candidates: List[Dict]


# ---------------------------------------------------------------------------
# Agent capability registry (inline — authoritative source is AGENT_REGISTRY.yaml)
# ---------------------------------------------------------------------------

_AGENT_PROFILES: List[AgentProfile] = [
    AgentProfile(
        "unified-coverage-agent",
        "Unified Coverage Agent",
        "testing",
        ["test", "coverage", "pytest", "gap", "fill", "coverage-gapfill", "fail_under", "branch"],
        ["test-enhancement-agent", "coverage-gapfill-agent"],
    ),
    AgentProfile(
        "unified-security-scanner",
        "Unified Security Scanner",
        "security",
        ["security", "scan", "vulnerability", "cve", "sast", "secrets", "dependency", "codeql"],
        ["code-scanning-remediation-agent", "secret-detection-agent"],
    ),
    AgentProfile(
        "workflow-ci-fixer",
        "Workflow CI Fixer",
        "ci",
        ["ci", "workflow", "github-actions", "yaml", "pipeline", "build", "lint"],
        ["ci-emergency-response-agent", "ci-auto-healer-agent"],
    ),
    AgentProfile(
        "unified-doc-agent",
        "Unified Doc Agent",
        "documentation",
        ["documentation", "docs", "link", "freshness", "readme", "markdown", "broken"],
        ["doc-freshness-checker", "link-validator-agent"],
    ),
    AgentProfile(
        "performance-regression-detector",
        "Performance Regression Detector",
        "performance",
        ["performance", "benchmark", "regression", "latency", "throughput", "slow"],
        ["performance-monitor-agent"],
    ),
    AgentProfile(
        "ci-importerror-agent",
        "CI ImportError Agent",
        "ci",
        ["import", "module", "importerror", "modulenot", "modulenotfounderror", "sys.path"],
        ["ci-testing-agent", "ci-failure-resolution-agent"],
    ),
    AgentProfile(
        "code-analysis-agent",
        "Code Analysis Agent",
        "quality",
        ["code", "review", "analysis", "quality", "static", "refactor", "smell"],
        ["mypy-manager-agent", "python-312-type-fixer"],
    ),
    AgentProfile(
        "pypi-publishing-operations-agent",
        "PyPI Publishing Operations Agent",
        "release",
        ["release", "version", "deploy", "publish", "pypi", "package", "distribution"],
        ["packaging-validation-agent"],
    ),
    AgentProfile(
        "workflow-health-monitor",
        "Workflow Health Monitor",
        "monitoring",
        ["health", "monitor", "alert", "uptime", "heartbeat", "status", "degraded"],
        ["artifact-monitor-agent", "ci-health-alert-agent"],
    ),
    AgentProfile(
        "dependency-conflict-agent",
        "Dependency Conflict Agent",
        "dependencies",
        ["dependency", "package", "conflict", "pip", "requirement", "lock", "pin"],
        ["dependency-security-review-agent", "dependency-vulnerability-scanner"],
    ),
    AgentProfile(
        "ci-failure-resolution-agent",
        "CI Failure Resolution Agent",
        "ci",
        ["failure", "broken", "error", "fix", "flaky", "failing", "ci-fail"],
        ["ci-emergency-response-agent", "self-healing-orchestrator-agent"],
    ),
    AgentProfile(
        "autonomous-test-healer-agent",
        "Autonomous Test Healer",
        "testing",
        ["test", "healer", "flaky", "unstable", "p19", "shadow-import", "fix-test"],
        ["fragile-test-guardian", "test-pattern-guardian"],
    ),
    AgentProfile(
        "recon-scout-agent",
        "Recon Scout Agent",
        "discovery",
        ["recon", "discover", "undocumented", "api", "gap", "explore", "inventory"],
        ["orchestrator-agent"],
    ),
    AgentProfile(
        "orchestrator-agent",
        "Orchestrator Agent",
        "orchestration",
        ["orchestrate", "coordinate", "multi-agent", "parallel", "delegate", "route"],
        ["agent-orchestrator"],
    ),
    AgentProfile(
        "mypy-manager-agent",
        "Mypy Manager Agent",
        "types",
        ["mypy", "type", "annotation", "typing", "typecheck", "py.typed"],
        ["python-312-type-fixer"],
    ),
]


# ---------------------------------------------------------------------------
# Vocabulary + embedding helpers (pure Python, no external deps)
# ---------------------------------------------------------------------------


def _build_vocab(profiles: List[AgentProfile]) -> Dict[str, int]:
    """Build a vocabulary index from all agent keyword sets."""
    vocab: Dict[str, int] = {}
    for p in profiles:
        for kw in p.keywords:
            for token in _tokenise(kw):
                if token not in vocab:
                    vocab[token] = len(vocab)
    return vocab


def _tokenise(text: str) -> List[str]:
    """Split text into lowercase tokens (letters + digits only)."""
    return [t.lower() for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def _build_embedding(keywords: List[str], vocab: Dict[str, int]) -> List[float]:
    """Build a TF unit-vector over the vocabulary for a keyword list."""
    dim = len(vocab)
    if dim == 0:
        return []
    vec = [0.0] * dim
    for kw in keywords:
        for token in _tokenise(kw):
            idx = vocab.get(token)
            if idx is not None:
                vec[idx] += 1.0
    # Unit-normalise
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# Keyword scoring
# ---------------------------------------------------------------------------


def _keyword_score(task_tokens: List[str], profile: AgentProfile) -> float:
    """Compute a 0–100 keyword match score."""
    if not task_tokens:
        return 0.0
    agent_tokens: set = set()
    for kw in profile.keywords:
        agent_tokens.update(_tokenise(kw))
    matches = sum(1 for t in task_tokens if t in agent_tokens)
    # Normalise: full overlap = 100
    max_possible = min(len(task_tokens), len(agent_tokens))
    if max_possible == 0:
        return 0.0
    return min(100.0, (matches / max_possible) * 100.0)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------


class AdvancedAgentRouter:
    """Semantic agent router implementing Phase 11.2 routing specification."""

    # Confidence formula weights
    KEYWORD_WEIGHT = 0.4
    SEMANTIC_WEIGHT = 0.6

    # Approval gate thresholds
    AUTO_APPROVE_THRESHOLD = 90.0
    HUMAN_REVIEW_THRESHOLD = 75.0

    def __init__(self, profiles: Optional[List[AgentProfile]] = None) -> None:
        self._profiles = profiles or _AGENT_PROFILES
        self._vocab = _build_vocab(self._profiles)
        # Pre-build all embeddings
        for p in self._profiles:
            p.embedding(self._vocab)

    def route(self, task: str) -> RoutingDecision:
        """Route a task description to the best matching agent."""
        start = time.monotonic()

        task_tokens = _tokenise(task)
        task_vec = _build_embedding(task_tokens, self._vocab)

        candidates: List[Tuple[str, float, float, float]] = []
        for profile in self._profiles:
            kw = _keyword_score(task_tokens, profile)
            sem = _cosine(task_vec, profile.embedding(self._vocab)) * 100.0
            conf = self.KEYWORD_WEIGHT * kw + self.SEMANTIC_WEIGHT * sem
            candidates.append((profile.agent_id, conf, kw, sem))

        # Sort by confidence descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        top = candidates[:3]

        best_id, best_conf, best_kw, best_sem = top[0]
        best_profile = next(p for p in self._profiles if p.agent_id == best_id)

        approval_gate = self._approval_gate(best_conf)
        fallback_chain = self._build_fallback(best_profile, [c[0] for c in top[1:]])

        latency_ms = (time.monotonic() - start) * 1000.0

        return RoutingDecision(
            task=task,
            primary_agent=best_id,
            confidence=round(best_conf, 2),
            approval_gate=approval_gate,
            fallback_chain=fallback_chain,
            routing_latency_ms=round(latency_ms, 3),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            keyword_score=round(best_kw, 2),
            semantic_score=round(best_sem, 2),
            top_candidates=[
                {"agent_id": c[0], "confidence": round(c[1], 2)}
                for c in top
            ],
        )

    def _approval_gate(self, confidence: float) -> str:
        if confidence >= self.AUTO_APPROVE_THRESHOLD:
            return "auto-approve"
        if confidence >= self.HUMAN_REVIEW_THRESHOLD:
            return "human-review"
        return "escalate"

    def _build_fallback(
        self, primary: AgentProfile, runner_up_ids: List[str]
    ) -> List[str]:
        """Build the 3-agent fallback chain per spec."""
        chain: List[str] = []
        # 1. Primary agent's configured fallbacks
        chain.extend(primary.fallback_agents)
        # 2. Next best candidates from routing
        for aid in runner_up_ids:
            if aid not in chain and aid != primary.agent_id:
                chain.append(aid)
        # 3. Always terminate with orchestrator/escalation
        for escalation in ("orchestrator-agent", "recon-scout-agent"):
            if escalation not in chain and escalation != primary.agent_id:
                chain.append(escalation)
        return chain[:3]

    def batch_route(self, tasks: List[str]) -> List[RoutingDecision]:
        """Route multiple tasks and return decisions in order."""
        return [self.route(t) for t in tasks]

    def self_test(self) -> Dict:
        """Run built-in correctness checks. Returns summary dict."""
        test_cases = [
            ("fix CI coverage failures in pytest", "unified-coverage-agent"),
            ("security scan for vulnerabilities", "unified-security-scanner"),
            ("GitHub Actions workflow yaml syntax error", "workflow-ci-fixer"),
            ("broken documentation links", "unified-doc-agent"),
            ("performance regression in benchmark", "performance-regression-detector"),
            ("ModuleNotFoundError in CI", "ci-importerror-agent"),
            ("publish package to PyPI", "pypi-publishing-operations-agent"),
        ]
        results = {"passed": 0, "failed": 0, "cases": []}
        for task, expected_agent in test_cases:
            decision = self.route(task)
            passed = decision.primary_agent == expected_agent
            results["passed" if passed else "failed"] += 1
            results["cases"].append(
                {
                    "task": task,
                    "expected": expected_agent,
                    "got": decision.primary_agent,
                    "confidence": decision.confidence,
                    "latency_ms": decision.routing_latency_ms,
                    "passed": passed,
                }
            )
        total = len(test_cases)
        results["accuracy"] = round(results["passed"] / total * 100, 1)
        results["total"] = total
        results["meets_target"] = results["accuracy"] >= 95.0
        return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_decision(decision: RoutingDecision, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(asdict(decision), indent=2))
        return
    gate_icon = {"auto-approve": "✅", "human-review": "⚠️", "escalate": "🔴"}.get(
        decision.approval_gate, "?"
    )
    print(f"\n{'='*60}")
    print(f"  Task: {decision.task}")
    print(f"  Primary Agent: {decision.primary_agent}")
    kw = decision.keyword_score
    sem = decision.semantic_score
    print(f"  Confidence: {decision.confidence:.1f}%  (kw={kw:.1f}, sem={sem:.1f})")
    print(f"  Gate: {gate_icon} {decision.approval_gate.upper()}")
    print(f"  Fallback chain: {' → '.join(decision.fallback_chain)}")
    print(f"  Latency: {decision.routing_latency_ms:.2f}ms")
    print(f"{'='*60}\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 11.2 Advanced Agent Router",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--task", help="Single task description to route")
    parser.add_argument("--batch", help="JSON file containing list of task strings")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in accuracy tests")
    parser.add_argument("--list-agents", action="store_true", help="List all routable agents")

    args = parser.parse_args(argv)
    router = AdvancedAgentRouter()

    if args.list_agents:
        data = [{"id": p.agent_id, "name": p.name, "category": p.category} for p in _AGENT_PROFILES]
        print(json.dumps(data, indent=2))
        return 0

    if args.self_test:
        results = router.self_test()
        print(json.dumps(results, indent=2))
        return 0 if results["meets_target"] else 1

    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"ERROR: batch file not found: {args.batch}", file=sys.stderr)
            return 2
        tasks: List[str] = json.loads(batch_path.read_text())
        decisions = router.batch_route(tasks)
        if args.json:
            print(json.dumps([asdict(d) for d in decisions], indent=2))
        else:
            for d in decisions:
                _print_decision(d)
        return 0

    if args.task:
        decision = router.route(args.task)
        _print_decision(decision, as_json=args.json)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
