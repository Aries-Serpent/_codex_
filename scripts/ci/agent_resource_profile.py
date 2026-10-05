#!/usr/bin/env python3
"""Choose bounded Copilot runtime concurrency from the runner's available resources."""

from __future__ import annotations

import argparse
import os
import re
import resource
from dataclasses import asdict, dataclass
from pathlib import Path

MIB = 1024 * 1024
CONSTRAINED_MEMORY_MIB = 8 * 1024
CRITICAL_MEMORY_MIB = 4 * 1024
CONSTRAINED_PROCESS_SLOTS = 512
CRITICAL_PROCESS_SLOTS = 128
RUNNER_LABEL = re.compile(r"^[A-Za-z0-9_.:-]{1,100}$")


@dataclass(frozen=True)
class ResourceCapacity:
    """Resource headroom visible to the current runner."""

    memory_available_mib: int | None
    cpu_count: int | None
    process_slots: int | None


@dataclass(frozen=True)
class ResourceDecision:
    """Runtime limits and optional runner escalation selected from capacity."""

    mode: str
    runner_profile: str
    larger_runner_required: bool
    agent_workers: int
    dependency_graph_workers: int
    dependency_graph_serialized: bool
    npm_jobs: int
    gomaxprocs: int
    node_heap_mib: int


def _read_integer(path: Path) -> int | None:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None
    if value in {"max", ""}:
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _cgroup_values(name: str) -> tuple[int | None, int | None]:
    for base in (Path("/sys/fs/cgroup"), Path("/sys/fs/cgroup") / name):
        limit = _read_integer(base / f"{name}.max")
        current = _read_integer(base / f"{name}.current")
        if limit is not None and current is not None:
            return limit, current
    return None, None


def _memory_available_mib() -> int | None:
    host_available: int | None = None
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemAvailable:"):
                host_available = int(line.split()[1]) // 1024
                break
    except (OSError, ValueError, IndexError):
        pass

    limit, current = _cgroup_values("memory")
    cgroup_available = (
        max(0, limit - current) // MIB
        if limit is not None and current is not None
        else None
    )
    values = [
        value for value in (host_available, cgroup_available) if value is not None
    ]
    return min(values) if values else None


def _process_slots() -> int | None:
    limit, current = _cgroup_values("pids")
    if limit is not None and current is not None:
        return max(0, limit - current)

    try:
        soft_limit, _ = resource.getrlimit(resource.RLIMIT_NPROC)
    except (AttributeError, OSError, ValueError):
        return None
    if soft_limit == resource.RLIM_INFINITY:
        return None

    try:
        process_count = sum(entry.name.isdigit() for entry in Path("/proc").iterdir())
    except OSError:
        process_count = 0
    return max(0, int(soft_limit) - process_count)


def probe_capacity() -> ResourceCapacity:
    """Read memory, CPU, and process headroom from the current Linux runner."""
    return ResourceCapacity(
        memory_available_mib=_memory_available_mib(),
        cpu_count=os.cpu_count(),
        process_slots=_process_slots(),
    )


def choose_resource_profile(
    capacity: ResourceCapacity,
    *,
    current_runner_profile: str,
    high_headroom_runner_profile: str | None = None,
) -> ResourceDecision:
    """Bound work and optionally select a configured larger runner on critical limits."""
    constrained = (
        capacity.memory_available_mib is None
        or capacity.cpu_count is None
        or capacity.process_slots is None
        or capacity.memory_available_mib < CONSTRAINED_MEMORY_MIB
        or capacity.cpu_count < 4
        or capacity.process_slots < CONSTRAINED_PROCESS_SLOTS
    )
    critical = (
        (capacity.memory_available_mib is not None
         and capacity.memory_available_mib < CRITICAL_MEMORY_MIB)
        or (capacity.cpu_count is not None and capacity.cpu_count <= 2)
        or (capacity.process_slots is not None
            and capacity.process_slots < CRITICAL_PROCESS_SLOTS)
    )
    runner_profile = current_runner_profile
    larger_runner_required = critical
    if critical and high_headroom_runner_profile:
        runner_profile = high_headroom_runner_profile

    memory = capacity.memory_available_mib
    heap_mib = min(4096, max(1024, (memory or 2048) // 2))
    gomaxprocs = min(2, max(1, capacity.cpu_count or 1))
    return ResourceDecision(
        mode="serialized" if constrained else "bounded",
        runner_profile=runner_profile,
        larger_runner_required=larger_runner_required,
        agent_workers=1 if constrained else 2,
        dependency_graph_workers=1,
        dependency_graph_serialized=True,
        npm_jobs=1,
        gomaxprocs=gomaxprocs,
        node_heap_mib=heap_mib,
    )


def _validate_runner_profile(profile: str) -> str:
    if not RUNNER_LABEL.fullmatch(profile):
        raise ValueError("runner profiles must be a single valid runner label")
    return profile


def _append_output(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github-output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--current-runner-profile", required=True)
    parser.add_argument("--high-headroom-runner-profile", default="")
    args = parser.parse_args()

    current_profile = _validate_runner_profile(args.current_runner_profile)
    high_profile = (
        _validate_runner_profile(args.high_headroom_runner_profile)
        if args.high_headroom_runner_profile
        else None
    )
    capacity = probe_capacity()
    decision = choose_resource_profile(
        capacity,
        current_runner_profile=current_profile,
        high_headroom_runner_profile=high_profile,
    )
    outputs = {
        "runner_profile": decision.runner_profile,
        "resource_mode": decision.mode,
        "larger_runner_required": str(decision.larger_runner_required).lower(),
        "agent_workers": str(decision.agent_workers),
        "dependency_graph_workers": str(decision.dependency_graph_workers),
        "dependency_graph_serialized": str(
            decision.dependency_graph_serialized
        ).lower(),
        "npm_jobs": str(decision.npm_jobs),
        "gomaxprocs": str(decision.gomaxprocs),
        "node_heap_mib": str(decision.node_heap_mib),
        "resource_capacity": str(asdict(capacity)),
    }
    _append_output(args.github_output, outputs)

    with args.summary.open("a", encoding="utf-8") as summary:
        summary.write("## Copilot runtime resource profile\n\n")
        summary.write(
            f"- Available capacity: `{asdict(capacity)}`\n"
            f"- Mode: **{decision.mode}**; agent workers: "
            f"`{decision.agent_workers}`; dependency graph workers: `1` "
            "(serialized).\n"
            f"- Runner profile: `{decision.runner_profile}`.\n"
        )
        if decision.larger_runner_required and not high_profile:
            summary.write(
                "- Critical headroom detected; configure "
                "`COPILOT_HIGH_HEADROOM_RUNNER_PROFILE` to enable runner "
                "escalation. This run will use serialized work.\n"
            )
        elif decision.larger_runner_required:
            summary.write(
                "- Critical headroom detected; selected the configured "
                "high-headroom runner.\n"
            )
    print(f"Selected {decision.mode} mode on {decision.runner_profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
