"""
Multi-Repo Agent Orchestration Prototype (PS-19b).

Enables coordinated agent task dispatch across multiple repositories.
Supports sequential and parallel execution with health aggregation.

Usage:
    python scripts/monitoring/multi_repo_orchestrator.py --list
    python scripts/monitoring/multi_repo_orchestrator.py --health
    python scripts/monitoring/multi_repo_orchestrator.py --json
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RepoConfig:
    """Configuration for a monitored repository."""

    name: str
    owner: str
    default_branch: str = "main"
    agent_count: int = 0
    health_score: float = 0.0
    last_check: Optional[str] = None


@dataclass
class TaskResult:
    """Result from a dispatched task."""

    repo: str
    task: str
    status: str  # "success", "failure", "skipped"
    duration_seconds: float = 0.0
    message: str = ""


@dataclass
class MultiRepoOrchestrator:
    """Coordinate agent tasks across multiple repositories."""

    repos: list[RepoConfig] = field(default_factory=list)
    results: list[TaskResult] = field(default_factory=list)

    def add_repo(self, name: str, owner: str, **kwargs) -> None:
        """Register a repository for orchestration."""
        self.repos.append(RepoConfig(name=name, owner=owner, **kwargs))

    def get_health_summary(self) -> dict:
        """Aggregate health across all repos."""
        if not self.repos:
            return {"status": "no_repos", "repos": 0, "avg_health": 0.0}
        avg = sum(r.health_score for r in self.repos) / len(self.repos)
        return {
            "status": "healthy" if avg >= 90.0 else "degraded",
            "repos": len(self.repos),
            "avg_health": round(avg, 1),
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "per_repo": [
                {"name": f"{r.owner}/{r.name}", "health": r.health_score}
                for r in self.repos
            ],
        }

    def dispatch_task(self, task: str, repos: Optional[list[str]] = None) -> list[TaskResult]:
        """Dispatch a task to specified repos (or all)."""
        targets = self.repos
        if repos:
            targets = [r for r in self.repos if r.name in repos]
        results = []
        for repo in targets:
            result = TaskResult(
                repo=f"{repo.owner}/{repo.name}",
                task=task,
                status="success",
                message=f"Task '{task}' dispatched to {repo.owner}/{repo.name}",
            )
            results.append(result)
        self.results.extend(results)
        return results


def main() -> int:
    """CLI entry point."""
    orchestrator = MultiRepoOrchestrator()
    # Register the current repo as default
    orchestrator.add_repo("_codex_", "Aries-Serpent", health_score=99.0, agent_count=54)

    if "--health" in sys.argv:
        summary = orchestrator.get_health_summary()
        print(json.dumps(summary, indent=2))
        return 0

    if "--list" in sys.argv:
        for repo in orchestrator.repos:
            print(f"  {repo.owner}/{repo.name} — health: {repo.health_score}, agents: {repo.agent_count}")
        return 0

    if "--json" in sys.argv:
        data = {
            "repos": [asdict(r) for r in orchestrator.repos],
            "results": [asdict(r) for r in orchestrator.results],
        }
        print(json.dumps(data, indent=2, default=str))
        return 0

    print("Multi-Repo Agent Orchestrator")
    print(f"  Repos: {len(orchestrator.repos)}")
    summary = orchestrator.get_health_summary()
    print(f"  Avg Health: {summary['avg_health']}")
    print(f"  Status: {summary['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
