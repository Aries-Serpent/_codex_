from __future__ import annotations

from scripts.ci.agent_resource_profile import (
    ResourceCapacity,
    choose_resource_profile,
)


def test_healthy_runner_uses_bounded_workers_and_serial_dependency_graph() -> None:
    decision = choose_resource_profile(
        ResourceCapacity(memory_available_mib=12 * 1024, cpu_count=8, process_slots=2048),
        current_runner_profile="ubuntu-latest-m",
        high_headroom_runner_profile="ubuntu-8-core",
    )

    assert decision.mode == "bounded"
    assert decision.agent_workers == 2
    assert decision.dependency_graph_workers == 1
    assert decision.dependency_graph_serialized is True
    assert decision.runner_profile == "ubuntu-latest-m"
    assert decision.larger_runner_required is False


def test_constrained_runner_serializes_agent_and_dependencies() -> None:
    decision = choose_resource_profile(
        ResourceCapacity(memory_available_mib=6 * 1024, cpu_count=4, process_slots=512),
        current_runner_profile="ubuntu-latest-m",
    )

    assert decision.mode == "serialized"
    assert decision.agent_workers == 1
    assert decision.dependency_graph_workers == 1
    assert decision.npm_jobs == 1
    assert decision.node_heap_mib == 3072
    assert decision.runner_profile == "ubuntu-latest-m"
    assert decision.larger_runner_required is False


def test_critical_headroom_escalates_only_to_configured_runner() -> None:
    capacity = ResourceCapacity(memory_available_mib=3 * 1024, cpu_count=2, process_slots=64)

    configured = choose_resource_profile(
        capacity,
        current_runner_profile="ubuntu-latest-m",
        high_headroom_runner_profile="ubuntu-8-core",
    )
    unconfigured = choose_resource_profile(
        capacity,
        current_runner_profile="ubuntu-latest-m",
    )

    assert configured.mode == "serialized"
    assert configured.larger_runner_required is True
    assert configured.runner_profile == "ubuntu-8-core"
    assert unconfigured.larger_runner_required is True
    assert unconfigured.runner_profile == "ubuntu-latest-m"


def test_missing_telemetry_fails_closed_to_serialized_mode() -> None:
    decision = choose_resource_profile(
        ResourceCapacity(memory_available_mib=None, cpu_count=8, process_slots=None),
        current_runner_profile="ubuntu-latest-m",
    )

    assert decision.mode == "serialized"
    assert decision.agent_workers == 1
    assert decision.dependency_graph_workers == 1
    assert decision.gomaxprocs == 2
    assert decision.node_heap_mib == 512
