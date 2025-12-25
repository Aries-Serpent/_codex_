"""Tests for Zendesk quantum orchestration and RAG bridge."""

from __future__ import annotations

from codex.monitoring import metrics
from codex.zendesk.monitoring.mcp_bridge import export_zendesk_metrics
from codex.zendesk.monitoring.zendesk_metrics import register_zendesk_metrics
from codex.zendesk.quantum import ZendeskQuantumOrchestrator, ZendeskTicket
from codex.zendesk.rag import ZendeskRAGBridge
from src.mcp.metrics.mcp_metrics import MetricCollector


def test_prioritize_tickets_edge_cases():
    orchestrator = ZendeskQuantumOrchestrator()
    tickets = [
        ZendeskTicket(
            ticket_id=1,
            subject="Reset password",
            priority="high",
            sla_deadline=0.0,
            complexity=1.0,
        ),
        ZendeskTicket(
            ticket_id=2,
            subject="Billing issue",
            priority="unknown",
            sla_deadline=48.0,
            complexity=3.5,
        ),
        ZendeskTicket(
            ticket_id=3,
            subject="Outage",
            priority="critical",
            sla_deadline=2.0,
            complexity=9.0,
        ),
    ]

    priorities = orchestrator.prioritize_tickets(tickets)

    assert len(priorities) == 3
    scores = [score for _, score in priorities]
    assert scores == sorted(scores, reverse=True)


def test_rag_bridge_deterministic_ordering():
    bridge = ZendeskRAGBridge()
    tickets = [
        ZendeskTicket(
            ticket_id=10,
            subject="Billing invoice mismatch",
            priority="medium",
            sla_deadline=12.0,
            complexity=2.0,
        ),
        ZendeskTicket(
            ticket_id=11,
            subject="Login not working",
            priority="low",
            sla_deadline=24.0,
            complexity=1.5,
        ),
    ]

    contexts = bridge.retrieve_ticket_context("billing", tickets, top_k=2)
    assert contexts

    ordered = sorted(contexts, key=lambda item: (-item.score, item.ticket_id))
    assert contexts == ordered


def test_metrics_registration_side_effects():
    register_zendesk_metrics()
    metrics.emit_counter("zendesk_api_calls_total", 2)
    diff_metric = metrics.get("zendesk_diff_operations")
    assert diff_metric is not None
    diff_metric.observe(3)

    collector = MetricCollector()
    snapshots = export_zendesk_metrics(collector)

    assert any(item["name"] == "zendesk_api_calls_total" for item in snapshots)
    assert collector.get_gauge("zendesk_api_calls_total") == 2.0
    assert collector.get_gauge("zendesk_diff_operations_count") == 1.0
    assert collector.get_gauge("zendesk_diff_operations_sum") == 3.0
