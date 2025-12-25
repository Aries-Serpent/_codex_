"""Zendesk quantum orchestration adapters."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from codex.zendesk.model.trigger import _ZendeskBaseModel
from src.quantum.orchestrator import ThermodynamicOrchestrator, ThermodynamicTask

logger = logging.getLogger(__name__)


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
    """Quantum orchestrator for Zendesk ticket management."""

    def __init__(
        self,
        *,
        global_temperature: float = 1.0,
        max_energy_per_cycle: float = 100.0,
    ) -> None:
        self.orchestrator = ThermodynamicOrchestrator(
            global_temperature=global_temperature,
            max_energy_per_cycle=max_energy_per_cycle,
        )
        logger.info("ZendeskQuantumOrchestrator initialized")

    def prioritize_tickets(
        self,
        tickets: Iterable[ZendeskTicket],
    ) -> list[tuple[int, float]]:
        """Prioritize tickets using thermodynamic principles."""
        ticket_list = list(tickets)
        tasks = [ticket.to_thermodynamic_task() for ticket in ticket_list]

        for task in tasks:
            self.orchestrator.register_task(task)

        priorities = []
        for ticket, task in zip(ticket_list, tasks):
            free_energy = task.calculate_free_energy()
            priority_score = 1.0 / (1.0 + free_energy)
            priorities.append((ticket.ticket_id, priority_score))

        priorities.sort(key=lambda item: (item[1], -item[0]), reverse=True)
        return priorities

    def execute_cycle(self) -> dict[str, Any]:
        """Execute one orchestration cycle."""
        return self.orchestrator.execute_thermodynamic_cycle()


__all__ = ["ZendeskQuantumOrchestrator", "ZendeskTicket"]
