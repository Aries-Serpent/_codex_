"""
Autonomy Control-Plane package for Codex.

Implements the six-phase Safe Full Copilot Cloud Agent Autonomy blueprint:

    Phase 1 — Unify Control State   → registry.py
    Phase 2 — Token Broker          → token_broker.py
    Phase 3 — Ingress Gateway       → ingress.py
    Phase 4 — Prompt Registry       → prompt_registry.py
    Phase 5 — Observability / Audit → audit.py
    Phase 6 — Expansion Gate        → expansion_gate.py

Blueprint source: .codex/docs/AUTONOMY_BLUEPRINT.md
"""

from __future__ import annotations

from .audit import AuditLogger, AuditRecord
from .expansion_gate import ExpansionGate, GateResult
from .ingress import IngressDecision, IngressEvent, IngressGateway
from .prompt_registry import PromptMetadata, PromptRegistry
from .registry import AutonomyMode, AutonomyRegistry, ControlClass, MutationClass
from .token_broker import TokenBroker, TokenResolution

__all__ = [
    # Phase 1 — registry
    "AutonomyMode",
    "AutonomyRegistry",
    "ControlClass",
    "MutationClass",
    # Phase 2 — token broker
    "TokenBroker",
    "TokenResolution",
    # Phase 3 — ingress
    "IngressDecision",
    "IngressEvent",
    "IngressGateway",
    # Phase 4 — prompt registry
    "PromptMetadata",
    "PromptRegistry",
    # Phase 5 — audit / observability
    "AuditLogger",
    "AuditRecord",
    # Phase 6 — expansion gate
    "ExpansionGate",
    "GateResult",
]
