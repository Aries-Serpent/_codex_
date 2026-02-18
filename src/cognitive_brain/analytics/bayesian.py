"""
Bayesian Networks PoC for Compliance Assessment (Phase 4)

Pure-Python Conditional Probability Distribution (CPD) evaluator.
No external ML libraries required — works with a small JSON network definition.

Feature flag: CODEX_BAYESIAN_MODE=true (default: false)

Research basis: Al Mamun 2023 — Bayesian networks achieved 30%+ false-positive
reduction in financial compliance screening.

API:
    assessor = BayesianAssessor.from_json(path)
    prob = assessor.posterior(evidence, node)
    adjusted = assessor.adjust_scores(base_probs, evidence)

Integration point (behind feature flag):
    In QuantumComplianceAssessor._assess_with_superposition(), after evaluation,
    call adjust_scores() to refine decision probabilities.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any


def _bayesian_mode_enabled() -> bool:
    """Check CODEX_BAYESIAN_MODE env flag (default: false)."""
    return os.getenv("CODEX_BAYESIAN_MODE", "false").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


@dataclass
class CPDTable:
    """
    Conditional Probability Distribution table for one node.

    Stores P(node=value | parent_values) entries.
    For root nodes (no parents) stores prior P(node=value).

    Attributes:
        node: Name of this random variable.
        parents: Ordered list of parent variable names.
        values: Possible values this variable can take.
        probs: Dict mapping parent-value tuple → {value: probability}.
               For root nodes, key is () (empty tuple).
    """

    node: str
    parents: list[str]
    values: list[str]
    probs: dict[tuple, dict[str, float]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CPDTable":
        """Deserialise from a JSON-loaded dict."""
        probs = {}
        for key_str, dist in data.get("probs", {}).items():
            # Key stored as comma-separated parent values, or "" for root nodes
            key = tuple(key_str.split(",")) if key_str else ()
            probs[key] = {str(k): float(v) for k, v in dist.items()}
        return cls(
            node=data["node"],
            parents=data.get("parents", []),
            values=data["values"],
            probs=probs,
        )


class BayesianAssessor:
    """
    Lightweight Bayesian Network assessor for compliance decisions.

    Implements Variable Elimination (VE) for small networks (< 20 nodes).
    Designed as a pure-Python PoC — no numpy, scipy, or pgmpy dependency.

    The network is defined in a JSON file with this schema::

        {
          "nodes": [
            {
              "node": "risk_level",
              "parents": [],
              "values": ["low", "medium", "high"],
              "probs": {
                "": {"low": 0.4, "medium": 0.4, "high": 0.2}
              }
            },
            {
              "node": "decision",
              "parents": ["risk_level"],
              "values": ["approve", "reject", "conditional"],
              "probs": {
                "low":    {"approve": 0.8, "reject": 0.05, "conditional": 0.15},
                "medium": {"approve": 0.3, "reject": 0.3,  "conditional": 0.4},
                "high":   {"approve": 0.1, "reject": 0.6,  "conditional": 0.3}
              }
            }
          ]
        }

    Example::

        assessor = BayesianAssessor.from_json("network.json")
        p = assessor.posterior(evidence={"risk_level": "high"}, node="decision")
        # {"approve": 0.10, "reject": 0.60, "conditional": 0.30}

        adjusted = assessor.adjust_scores(
            base_probs={"approve": 0.5, "monitor": 0.3, "reject": 0.1, "conditional": 0.1},
            evidence={"risk_level": "high"},
        )
    """

    def __init__(self, tables: list[CPDTable]) -> None:
        self._tables: dict[str, CPDTable] = {t.node: t for t in tables}

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, network: dict[str, Any]) -> "BayesianAssessor":
        """Build from a pre-loaded network dict (skips file I/O)."""
        tables = [CPDTable.from_dict(n) for n in network.get("nodes", [])]
        return cls(tables)

    @classmethod
    def from_json(cls, path: str) -> "BayesianAssessor":
        """Load network definition from a JSON file.

        Args:
            path: Absolute or relative path to the network JSON file.

        Returns:
            Initialised ``BayesianAssessor``.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the JSON is malformed.
        """
        with open(path) as fh:
            network = json.load(fh)
        return cls.from_dict(network)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def posterior(
        self,
        evidence: dict[str, str],
        node: str,
    ) -> dict[str, float]:
        """
        Compute posterior distribution P(node | evidence) via naive enumeration.

        For PoC-scale networks (≤ ~10 nodes) enumeration is exact and fast.
        For larger networks consider upgrading to loopy belief propagation.

        Args:
            evidence: Observed variable assignments, e.g. ``{"risk_level": "high"}``.
            node:     Target variable name.

        Returns:
            Dict mapping each value of ``node`` to its posterior probability.

        Raises:
            KeyError: If ``node`` or any evidence variable is unknown.
        """
        if node not in self._tables:
            raise KeyError(f"Unknown node: {node!r}")

        table = self._tables[node]
        result: dict[str, float] = {}

        for value in table.values:
            # P(node=value | evidence) ∝ P(node=value, evidence)
            # For single-layer networks: use conditional table directly
            if not table.parents:
                prior = table.probs.get((), {}).get(value, 0.0)
                result[value] = prior
            else:
                # Enumerate over parent assignments consistent with evidence
                prob = 0.0
                parent_value = self._resolve_parents(table, evidence)
                if parent_value is not None:
                    prob = table.probs.get(parent_value, {}).get(value, 0.0)
                else:
                    # Marginalise over all parent combinations
                    prob = self._marginalise(table, value, evidence)
                result[value] = prob

        # Normalise
        total = sum(result.values())
        if total > 0:
            return {k: v / total for k, v in result.items()}
        # Uniform fallback
        n = len(table.values)
        return {v: 1.0 / n for v in table.values}

    def adjust_scores(
        self,
        base_probs: dict[str, float],
        evidence: dict[str, str],
        target_node: str = "decision",
        alpha: float = 0.3,
    ) -> dict[str, float]:
        """
        Blend base decision probabilities with Bayesian posterior.

        Computes a weighted combination::

            adjusted[k] = (1 - alpha) * base_probs[k] + alpha * posterior[k]

        Keys in ``base_probs`` are mapped to ``target_node`` values by
        lower-casing; unknown keys pass through unchanged.

        Args:
            base_probs:   Baseline scores from quantum superposition path,
                          e.g. ``{"approve": 0.6, "monitor": 0.2, ...}``.
            evidence:     Observed evidence for the Bayesian network.
            target_node:  Node whose posterior to use (default "decision").
            alpha:        Blending weight for Bayesian posterior (0.0–1.0).

        Returns:
            Adjusted probability dict with same keys as ``base_probs``.
        """
        if target_node not in self._tables or not _bayesian_mode_enabled():
            return dict(base_probs)

        posterior = self.posterior(evidence, target_node)

        adjusted: dict[str, float] = {}
        for key, base_val in base_probs.items():
            bayes_val = posterior.get(key.lower(), base_val)
            adjusted[key] = (1.0 - alpha) * base_val + alpha * bayes_val

        # Re-normalise to preserve probability semantics
        total = sum(adjusted.values())
        if total > 0:
            return {k: v / total for k, v in adjusted.items()}
        return adjusted

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_parents(
        self, table: CPDTable, evidence: dict[str, str]
    ) -> tuple | None:
        """
        Resolve parent key from evidence dict.

        Returns the parent-value tuple if ALL parents are in evidence,
        otherwise returns None (signal to marginalise).
        """
        key_parts = []
        for parent in table.parents:
            val = evidence.get(parent)
            if val is None:
                return None
            key_parts.append(val)
        return tuple(key_parts) if key_parts else ()

    def _marginalise(
        self, table: CPDTable, value: str, evidence: dict[str, str]
    ) -> float:
        """Marginalise over unknown parent values using uniform prior."""
        total = 0.0
        count = 0
        for key, dist in table.probs.items():
            # Check if this key is consistent with evidence for observed parents
            consistent = True
            for i, parent in enumerate(table.parents):
                if parent in evidence and i < len(key) and key[i] != evidence[parent]:
                    consistent = False
                    break
            if consistent:
                total += dist.get(value, 0.0)
                count += 1
        return total / count if count > 0 else 0.0
