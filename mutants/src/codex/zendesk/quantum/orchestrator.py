"""Zendesk quantum orchestration adapters with scope validation.

This module integrates scope-based authorization into the quantum orchestrator,
ensuring all operations are properly authorized based on token scopes.

**UUID-to-Integer Conversion Strategy**:
The `create_ticket_with_scope_check()` method converts UUID ticket IDs to 128-bit
integers to maintain compatibility with the quantum orchestrator's integer-based
task tracking while preserving uniqueness guarantees.

Design Decisions:
- UUIDs provide globally unique identifiers without coordination
- Integer conversion preserves uniqueness via UUID's 128-bit space
- Maintains compatibility with existing integer-based APIs
- Migration path: Systems expecting smaller IDs need adapter layer

Trade-offs:
- Pro: No collision risk, globally unique across distributed systems
- Pro: Can generate IDs offline without database coordination
- Con: 128-bit integers may exceed some system limits (e.g., 64-bit DBs)
- Con: Human-unfriendly IDs in logs/UIs (consider display formatting)

For systems with ID size constraints, consider:
1. Mapping layer: UUID ↔ Sequential ID with database lookup
2. Shorter hash: Use 64-bit hash of UUID (accept collision risk)
3. ID prefixes: Store full UUID, use truncated version for display

See .codex/architecture/uuid_ticket_id_strategy.md for detailed ADR.

Part of PS-05 Enhancement: Scope Validation Integration - Priority 4
"""

from __future__ import annotations

import contextvars
import logging
import uuid
from collections.abc import Iterable
from typing import Any, Optional

from codex.zendesk.model.trigger import _ZendeskBaseModel
from quantum.orchestrator import ThermodynamicOrchestrator, ThermodynamicTask

# Import scope validation infrastructure
try:
    from security.scope_validator import ScopeValidator, TokenScope

    HAS_SCOPE_VALIDATION = True
except ImportError:
    HAS_SCOPE_VALIDATION = False
    logger = logging.getLogger(__name__)
    logger.warning("Scope validation not available - security features disabled")

logger = logging.getLogger(__name__)

# Context variable for thread-safe scope validator storage
_scope_validator_ctx: contextvars.ContextVar[Optional[ScopeValidator]] = contextvars.ContextVar(
    "scope_validator", default=None
)


class ZendeskTicket(_ZendeskBaseModel):
    """Minimal ticket representation for quantum orchestration."""

    ticket_id: int
    subject: str
    priority: str
    sla_deadline: float
    complexity: float = 1.0

    def to_thermodynamic_task(self) -> ThermodynamicTask:
        """Convert this ticket into a thermodynamic task."""
        energy = self.complexity * 2.0
        temperature = max(0.1, self.sla_deadline / 24.0)
        entropy = 0.5 if self.priority == "unknown" else 0.1

        return ThermodynamicTask(
            name=f"ticket_{self.ticket_id}",
            task_func=self._process_ticket,
            energy=energy,
            temperature=temperature,
            entropy=entropy,
        )

    def _process_ticket(self) -> dict[str, Any]:
        return {"ticket_id": self.ticket_id, "status": "processed"}


class ZendeskQuantumOrchestrator:
    """Quantum orchestrator for Zendesk ticket management with scope validation.

    This orchestrator enforces scope-based authorization for all operations:
    - create_ticket: Requires WRITE_ISSUES or ADMIN scope
    - prioritize_tickets: Requires READ_ISSUES or higher
    - execute_cycle: Requires WRITE_WORKFLOWS or ADMIN scope
    - query_knowledge_base: Requires READ_REPO scope
    """

    def __init__(
        self,
        *,
        global_temperature: float = 1.0,
        max_energy_per_cycle: float = 100.0,
        enforce_scopes: bool = True,
    ) -> None:
        """Initialize orchestrator with optional scope enforcement.

        Args:
            global_temperature: Global temperature for thermodynamic calculations
            max_energy_per_cycle: Maximum energy per orchestration cycle
            enforce_scopes: Enable scope validation (default: True)
        """
        self.orchestrator = ThermodynamicOrchestrator(
            global_temperature=global_temperature,
            max_energy_per_cycle=max_energy_per_cycle,
        )
        self.enforce_scopes = enforce_scopes and HAS_SCOPE_VALIDATION

        if enforce_scopes and not HAS_SCOPE_VALIDATION:
            logger.warning("Scope enforcement requested but validation module not available")

        logger.info(
            f"ZendeskQuantumOrchestrator initialized (scope enforcement: {self.enforce_scopes})"
        )

    def set_scope_validator(self, validator: ScopeValidator) -> None:
        """Set scope validator for this context.

        Args:
            validator: ScopeValidator instance with token scopes
        """
        _scope_validator_ctx.set(validator)

    def _check_scope(self, required_scopes: TokenScope) -> None:
        """Check if current context has required scopes.

        Args:
            required_scopes: Required scope flags

        Raises:
            InsufficientScopeError: If scopes insufficient
        """
        if not self.enforce_scopes:
            return

        validator = _scope_validator_ctx.get()
        if not validator:
            logger.warning("No scope validator set - skipping scope check")
            return

        # Validate scopes (using singular method name per ScopeValidator API)
        validator.require_scope(required_scopes)

    def create_ticket(
        self,
        subject: str,
        priority: str,
        sla_deadline: float,
        complexity: float = 1.0,
    ) -> ZendeskTicket:
        """Create a new ticket (requires WRITE_ISSUES or ADMIN scope).

        Args:
            subject: Ticket subject
            priority: Ticket priority
            sla_deadline: SLA deadline in hours
            complexity: Ticket complexity score

        Returns:
            Created ticket

        Raises:
            InsufficientScopeError: If insufficient scopes
        """
        # Enforce scope requirement
        if HAS_SCOPE_VALIDATION:
            self._check_scope(TokenScope.WRITE_ISSUES | TokenScope.ADMIN)

        # Create ticket (simplified - would integrate with Zendesk API).
        # Generate a unique ticket ID using uuid4().int (128-bit integer) to align with
        # the orchestrator's integer-based task tracking. See the module docstring and
        # ADR `.codex/architecture/uuid_ticket_id_strategy.md` for full design rationale.
        ticket_uuid = uuid.uuid4()
        ticket = ZendeskTicket(
            ticket_id=ticket_uuid.int,  # Full UUID as integer (128-bit)
            subject=subject,
            priority=priority,
            sla_deadline=sla_deadline,
            complexity=complexity,
        )

        logger.info(f"Created ticket {ticket.ticket_id}: {subject}")
        return ticket

    def prioritize_tickets(
        self,
        tickets: Iterable[ZendeskTicket],
    ) -> list[tuple[int, float]]:
        """Prioritize tickets using thermodynamic principles.

        Requires READ_ISSUES or higher scope.

        Args:
            tickets: Iterable of tickets to prioritize

        Returns:
            List of (ticket_id, priority_score) tuples

        Raises:
            InsufficientScopeError: If insufficient scopes
        """
        # Enforce scope requirement
        if HAS_SCOPE_VALIDATION:
            self._check_scope(TokenScope.READ_ISSUES)

        ticket_list = list(tickets)
        tasks = [ticket.to_thermodynamic_task() for ticket in ticket_list]

        for task in tasks:
            self.orchestrator.register_task(task)

        priorities = []
        for ticket, task in zip(ticket_list, tasks, strict=False):
            free_energy = task.calculate_free_energy()
            priority_score = 1.0 / (1.0 + free_energy)
            priorities.append((ticket.ticket_id, priority_score))

        priorities.sort(key=lambda item: (item[1], -item[0]), reverse=True)

        logger.info(f"Prioritized {len(priorities)} tickets")
        return priorities

    def execute_cycle(self) -> dict[str, Any]:
        """Execute one orchestration cycle.

        Requires WRITE_WORKFLOWS or ADMIN scope.

        Returns:
            Cycle execution results

        Raises:
            InsufficientScopeError: If insufficient scopes
        """
        # Enforce scope requirement
        if HAS_SCOPE_VALIDATION:
            self._check_scope(TokenScope.WRITE_WORKFLOWS | TokenScope.ADMIN)

        result = self.orchestrator.execute_thermodynamic_cycle()
        logger.info("Executed orchestration cycle")
        return result

    def query_knowledge_base(self, query: str) -> dict[str, Any]:
        """Query knowledge base (requires READ_REPO scope).

        Args:
            query: Search query

        Returns:
            Query results

        Raises:
            InsufficientScopeError: If insufficient scopes
        """
        # Enforce scope requirement
        if HAS_SCOPE_VALIDATION:
            self._check_scope(TokenScope.READ_REPO)

        # Simplified knowledge base query
        logger.info(f"Querying knowledge base: {query}")
        return {
            "query": query,
            "results": [],
            "message": "Knowledge base query (stub implementation)",
        }


__all__ = ["ZendeskQuantumOrchestrator", "ZendeskTicket"]
