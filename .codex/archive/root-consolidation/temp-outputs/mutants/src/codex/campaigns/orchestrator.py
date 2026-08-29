"""
Campaign Framework: Orchestrate multi-phase workflows with parallel agent delegation.

This module provides the core Campaign orchestration engine that:
1. Activates campaigns on trigger events
2. Executes phases with multiple agents in parallel
3. Verifies gates and escalates on failures
4. Learns from outcomes to improve future routing
5. Integrates with cognitive brain pattern store
"""

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


class CampaignStatus(Enum):
    """Campaign execution status."""

    IDLE = "idle"
    ACTIVATED = "activated"
    PHASE_RUNNING = "phase_running"
    GATE_CHECK = "gate_check"
    COMPLETE = "complete"
    FAILED = "failed"
    ESCALATED = "escalated"


@dataclass
class CampaignPhase:
    """Definition of a campaign phase with agents and gate condition."""

    phase_id: str
    name: str
    description: str
    parallel_agents: list[str]
    gate_condition: Optional[Callable[[dict[str, Any]], bool]] = None
    timeout_seconds: int = 600
    artifacts: list[str] = field(default_factory=list)
    metrics_expected: list[str] = field(default_factory=list)


@dataclass
class CampaignDefinition:
    """High-level campaign definition with objectives and phases."""

    campaign_id: str
    name: str
    description: str
    category: str
    objectives: list[str]
    phases: list[CampaignPhase]
    success_criteria: list[str]
    escalation_threshold: int = 3
    rollback_strategy: str = "revert_and_alert"  # or "commit_and_alert"


@dataclass
class PhaseExecutionResult:
    """Result of executing a single phase."""

    phase_id: str
    status: str  # "passed" | "failed" | "timeout"
    agent_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    artifacts_collected: list[Path] = field(default_factory=list)
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass
class CampaignExecution:
    """Runtime state of campaign execution."""

    campaign_id: str
    activation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    current_phase_index: int = 0
    agent_results: dict[str, Any] = field(default_factory=dict)
    phase_results: list[PhaseExecutionResult] = field(default_factory=list)
    iterations: int = 0
    status: CampaignStatus = CampaignStatus.IDLE
    artifacts_collected: dict[str, Path] = field(default_factory=dict)
    error_messages: list[str] = field(default_factory=list)

    def duration_seconds(self) -> float:
        """Calculate total execution duration."""
        return (datetime.now(timezone.utc) - self.activation_time).total_seconds()


class CampaignOrchestrator:
    """
    Orchestrate multi-phase campaigns with parallel agent delegation.

    Responsibilities:
    1. Load campaign definitions from registry
    2. Activate campaigns and dispatch phases
    3. Monitor agent execution in parallel
    4. Verify phase gates and escalate on failures
    5. Collect and aggregate artifacts
    6. Learn from outcomes and update pattern store
    7. Provide detailed campaign telemetry
    """

    def __init__(
        self,
        campaign_def: CampaignDefinition,
        artifact_dir: Path = Path(".codex/campaign_artifacts"),
        pattern_store_path: Path = Path(".codex/cognitive_brain/pattern_learning_store.json"),
    ):
        """Initialize campaign orchestrator.

        Args:
            campaign_def: Campaign definition with phases and objectives
            artifact_dir: Directory to store campaign artifacts
            pattern_store_path: Path to pattern learning store for cognitive brain
        """
        self.campaign = campaign_def
        self.execution = CampaignExecution(campaign_id=campaign_def.campaign_id)
        self.artifact_dir = artifact_dir
        self.pattern_store_path = pattern_store_path
        self._setup_artifact_dir()

    def _setup_artifact_dir(self) -> None:
        """Create artifact directory structure."""
        campaign_dir = self.artifact_dir / self.campaign.campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)
        self.execution.artifacts_collected["campaign_dir"] = campaign_dir

    def activate_campaign(self) -> None:
        """Activate campaign and prepare for phase execution."""
        self.execution.status = CampaignStatus.ACTIVATED
        self.execution.activation_time = datetime.now(timezone.utc)

        # Log activation
        self._log_event(
            "campaign_activated",
            {
                "campaign_id": self.campaign.campaign_id,
                "name": self.campaign.name,
                "phases_count": len(self.campaign.phases),
                "timestamp": self.execution.activation_time.isoformat(),
            },
        )

    def execute_phase(self, phase_index: int) -> list[str]:
        """
        Execute a phase by launching agents in parallel.

        Args:
            phase_index: Index of phase to execute (0-based)

        Returns:
            List of agent_ids launched (can be used for monitoring)
        """
        if phase_index >= len(self.campaign.phases):
            raise ValueError(f"Phase index {phase_index} out of range")

        phase = self.campaign.phases[phase_index]
        self.execution.current_phase_index = phase_index
        self.execution.status = CampaignStatus.PHASE_RUNNING

        # Log phase start
        self._log_event(
            "phase_started",
            {
                "campaign_id": self.campaign.campaign_id,
                "phase_id": phase.phase_id,
                "phase_name": phase.name,
                "agents_count": len(phase.parallel_agents),
                "timeout_seconds": phase.timeout_seconds,
            },
        )

        # In production: use task() tool to launch agents
        # For now, return list of agent IDs that would be launched
        agent_ids = phase.parallel_agents.copy()

        self._log_event(
            "phase_agents_dispatched",
            {
                "campaign_id": self.campaign.campaign_id,
                "phase_id": phase.phase_id,
                "agent_ids": agent_ids,
            },
        )

        return agent_ids

    def monitor_agents(
        self,
        agent_ids: list[str],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        """
        Poll agents until completion or timeout.

        Args:
            agent_ids: List of agent IDs to monitor
            timeout_seconds: Maximum time to wait for all agents

        Returns:
            Dictionary mapping agent_id to execution result
        """
        results: dict[str, dict[str, Any]] = {}
        start_time = time.time()

        while len(results) < len(agent_ids):
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                # Timeout: record remaining agents as timed out
                for agent_id in agent_ids:
                    if agent_id not in results:
                        results[agent_id] = {
                            "status": "timeout",
                            "agent_id": agent_id,
                            "elapsed_seconds": elapsed,
                        }
                break

            # In production: use read_agent(agent_id, wait=False) here
            # For now, simulate checking each agent
            for agent_id in agent_ids:
                if agent_id not in results:
                    # Simulate agent completion (would be real in production)
                    # Check if agent has completed
                    pass

            time.sleep(10)  # Poll every 10 seconds

        self.execution.agent_results.update(results)
        return results

    def verify_gate(self, phase_index: int, agent_results: dict[str, Any]) -> bool:
        """
        Evaluate gate condition for phase completion.

        Args:
            phase_index: Index of phase to verify
            agent_results: Results from agent execution

        Returns:
            True if gate passes, False otherwise
        """
        if phase_index >= len(self.campaign.phases):
            return False

        phase = self.campaign.phases[phase_index]
        self.execution.status = CampaignStatus.GATE_CHECK

        # If no gate condition defined, all results passing = gate passes
        if phase.gate_condition is None:
            gate_pass = all(
                result.get("status") == "completed" for result in agent_results.values()
            )
        else:
            # Evaluate custom gate condition
            try:
                gate_pass = phase.gate_condition(agent_results)
            except Exception as e:
                self._log_event(
                    "gate_evaluation_error",
                    {
                        "phase_id": phase.phase_id,
                        "error": str(e),
                    },
                )
                gate_pass = False

        self._log_event(
            "gate_evaluated",
            {
                "phase_id": phase.phase_id,
                "gate_pass": gate_pass,
                "agent_count": len(agent_results),
            },
        )

        return gate_pass

    def collect_artifacts(self, phase_index: int) -> None:
        """
        Collect artifacts produced by agents in a phase.

        Args:
            phase_index: Index of phase whose artifacts to collect
        """
        if phase_index >= len(self.campaign.phases):
            return

        phase = self.campaign.phases[phase_index]
        phase_dir = self.artifact_dir / self.campaign.campaign_id / f"phase_{phase.phase_id}"
        phase_dir.mkdir(parents=True, exist_ok=True)

        # In production: iterate through phase.artifacts and copy from agent results
        self.execution.artifacts_collected[f"phase_{phase.phase_id}"] = phase_dir

        self._log_event(
            "artifacts_collected",
            {
                "phase_id": phase.phase_id,
                "artifact_count": len(phase.artifacts),
            },
        )

    def escalate(self, reason: str) -> None:
        """
        Escalate campaign to human with full context.

        Args:
            reason: Human-readable reason for escalation
        """
        self.execution.status = CampaignStatus.ESCALATED
        self.execution.error_messages.append(reason)

        self._generate_escalation_issue(reason)

        self._log_event(
            "campaign_escalated",
            {
                "campaign_id": self.campaign.campaign_id,
                "reason": reason,
                "iterations": self.execution.iterations,
            },
        )

        # In production: use engine-tools-reply_to_comment or create GitHub issue
        # For now, just log

    def _generate_escalation_issue(self, reason: str) -> str:
        """Generate escalation issue body with full context."""
        state_dump = json.dumps(asdict(self.execution), indent=2, default=str)

        return f"""
[ESCALATION] Campaign {self.campaign.campaign_id} requires human intervention

**Campaign:** {self.campaign.name}
**Status:** {self.execution.status.value}
**Current Phase:** {self.execution.current_phase_index + 1}/{len(self.campaign.phases)}
**Iterations:** {self.execution.iterations}
**Reason:** {reason}

**Execution State:**
```json
{state_dump}
```

**Agent Results Summary:**
- Total agents executed: {len(self.execution.agent_results)}
- Successful agents: {sum(1 for r in self.execution.agent_results.values() if r.get("status") == "completed")}
- Failed agents: {sum(1 for r in self.execution.agent_results.values() if r.get("status") == "failed")}

**Recommendations:**
1. Review agent logs in artifacts directory
2. Verify all agent dependencies are available
3. Check if escalation threshold needs adjustment
4. Consider manual intervention or phase-specific fixes

cc: @mbaetiong
"""  # noqa: E501

    def finalize(self, status: CampaignStatus) -> None:
        """
        Finalize campaign execution and record learnings.

        Args:
            status: Final status (COMPLETE, FAILED, or ESCALATED)
        """
        self.execution.status = status
        duration = self.execution.duration_seconds()

        # Aggregate learnings
        learnings = {
            "campaign_id": self.campaign.campaign_id,
            "category": self.campaign.category,
            "status": status.value,
            "phases_completed": self.execution.current_phase_index + 1,
            "total_phases": len(self.campaign.phases),
            "iterations": self.execution.iterations,
            "duration_seconds": duration,
            "agents_used": list(self.execution.agent_results.keys()),
            "success": status == CampaignStatus.COMPLETE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Update pattern learning store
        self._update_pattern_store(learnings)

        # Log finalization
        self._log_event("campaign_finalized", learnings)

        # Save campaign execution record
        self._save_execution_record()

    def _update_pattern_store(self, learnings: dict[str, Any]) -> None:
        """Update pattern learning store with campaign outcomes."""
        try:
            if self.pattern_store_path.exists():
                with open(self.pattern_store_path, "r") as f:
                    pattern_store = json.load(f)
            else:
                pattern_store = {"patterns": []}

            # Record campaign as a pattern
            pattern_entry = {
                "pattern_id": f"campaign_{self.campaign.campaign_id}_{learnings['timestamp']}",
                "type": "campaign_execution",
                "campaign_id": self.campaign.campaign_id,
                "category": self.campaign.category,
                "success_rate": 1.0 if learnings["success"] else 0.0,
                "avg_fix_time_seconds": learnings["duration_seconds"],
                "occurrences": 1,
                "documented_fix": json.dumps(learnings),
            }

            pattern_store["patterns"].append(pattern_entry)

            with open(self.pattern_store_path, "w") as f:
                json.dump(pattern_store, f, indent=2)
        except (IOError, OSError) as e:
            self._log_event("pattern_store_update_error", {"error": str(e)})

    def _save_execution_record(self) -> None:
        """Save campaign execution record to JSONL log."""
        executions_log = self.artifact_dir.parent / "campaign_executions.jsonl"

        record = {
            "campaign_id": self.campaign.campaign_id,
            "status": self.execution.status.value,
            "activation_time": self.execution.activation_time.isoformat(),
            "completion_time": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": self.execution.duration_seconds(),
            "phases_completed": self.execution.current_phase_index + 1,
            "iterations": self.execution.iterations,
            "success": self.execution.status == CampaignStatus.COMPLETE,
        }

        try:
            with open(executions_log, "a") as f:
                f.write(json.dumps(record) + "\n")
        except (IOError, OSError) as e:
            self._log_event("execution_record_error", {"error": str(e)})

    def _log_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Log campaign event for observability."""
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "campaign_id": self.campaign.campaign_id,
            **data,
        }
        # In production: write to session logger
        # For now, just document the structure


class CampaignRegistryLoader:
    """Load campaign definitions from CAMPAIGN_REGISTRY.yaml."""

    @staticmethod
    def load_registry(registry_path: Path) -> dict[str, CampaignDefinition]:
        """Load all campaigns from registry file."""
        import yaml

        try:
            with open(registry_path, "r") as f:
                registry = yaml.safe_load(f)
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to load campaign registry: {e}")

        campaigns = {}
        for campaign_data in registry.get("campaigns", []):
            campaign_def = CampaignRegistryLoader.parse_campaign(campaign_data)
            campaigns[campaign_def.campaign_id] = campaign_def

        return campaigns

    @staticmethod
    def parse_campaign(campaign_data: dict[str, Any]) -> CampaignDefinition:
        """Parse a campaign definition from registry data."""
        phases = []
        for phase_data in campaign_data.get("phases", []):
            phase = CampaignPhase(
                phase_id=phase_data["id"],
                name=phase_data["name"],
                description=phase_data.get("description", ""),
                parallel_agents=phase_data["parallel_agents"],
                timeout_seconds=phase_data.get("timeout_seconds", 600),
                artifacts=phase_data.get("artifacts", []),
                metrics_expected=phase_data.get("metrics_expected", []),
            )
            phases.append(phase)

        return CampaignDefinition(
            campaign_id=campaign_data["id"],
            name=campaign_data["name"],
            description=campaign_data["description"],
            category=campaign_data["category"],
            objectives=campaign_data["objectives"],
            phases=phases,
            success_criteria=campaign_data["success_criteria"],
            escalation_threshold=campaign_data.get("escalation_threshold", 3),
            rollback_strategy=campaign_data.get("rollback_strategy", "revert_and_alert"),
        )
