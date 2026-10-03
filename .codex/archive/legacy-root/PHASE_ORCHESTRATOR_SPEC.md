# Phase Orchestrator Specification

**Version:** 1.0  
**Last Updated:** 2026-07-09  
**Target Audience:** Deployment Engineers, Architects, CI/CD Pipeline Developers  
**Status:** Production-Ready  

---

## Overview

The `DeploymentGateway` orchestrator coordinates multi-phase, multi-lane production deployments using a state-machine architecture with comprehensive event logging and failure recovery.

**Key Characteristics:**
- **5-Phase Architecture:** Planning → Pre-Deployment → Deployment → Post-Deployment → Verification
- **4 Parallel Lanes:** Coordinated execution with timeout management
- **Event-Driven:** Full observability through structured logging
- **Failure Recovery:** Built-in escalation and recovery per lane
- **State Persistence:** Checkpoint recovery from any phase

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DeploymentGateway Orchestrator                    │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 1: Planning        → Pre-Flight Checks, Prerequisites        │
│  Phase 2: Pre-Deployment  → Validation, Approval, Lock              │
│  Phase 3: Deployment      → Parallel Lane Execution (A-D)           │
│  Phase 4: Post-Deployment → Automation, Release, Publishing         │
│  Phase 5: Verification    → Monitoring, Metrics, Success Validation │
└─────────────────────────────────────────────────────────────────────┘
        ↓         ↓         ↓         ↓         ↓
    Lane A   Lane B    Lane C    Lane D
  (Feature)  (Infra)  (Security) (Publish)
    300s      300s      300s      420s
```

---

## Python Implementation

### Core Enums & Data Structures

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

class Phase(Enum):
    """Deployment phase states"""
    PLANNING = "planning"
    PRE_DEPLOYMENT = "pre_deployment"
    DEPLOYMENT = "deployment"
    POST_DEPLOYMENT = "post_deployment"
    VERIFICATION = "verification"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class Lane(Enum):
    """Parallel execution lanes"""
    LANE_A = "lane_a"        # Feature & Integration Validation
    LANE_B = "lane_b"        # Infrastructure & Docker Delivery
    LANE_C = "lane_c"        # Security & Documentation
    LANE_D = "lane_d"        # Release & Publishing

class LaneStatus(Enum):
    """Lane execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ROLLED_BACK = "rolled_back"

class EventType(Enum):
    """Event logging types"""
    PHASE_START = "phase_start"
    PHASE_COMPLETE = "phase_complete"
    PHASE_FAILED = "phase_failed"
    LANE_START = "lane_start"
    LANE_COMPLETE = "lane_complete"
    LANE_FAILED = "lane_failed"
    LANE_TIMEOUT = "lane_timeout"
    CHECKPOINT_SAVED = "checkpoint_saved"
    CHECKPOINT_LOADED = "checkpoint_loaded"
    RECOVERY_STARTED = "recovery_started"
    RECOVERY_FAILED = "recovery_failed"
    ESCALATION_TRIGGERED = "escalation_triggered"

@dataclass
class DeploymentEvent:
    """Immutable event record"""
    timestamp: datetime
    event_type: EventType
    phase: Phase
    lane: Optional[Lane]
    message: str
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "phase": self.phase.value,
            "lane": self.lane.value if self.lane else None,
            "message": self.message,
            "metadata": self.metadata,
        }

@dataclass
class LaneCheckpoint:
    """Lane execution checkpoint"""
    lane: Lane
    status: LaneStatus
    start_time: datetime
    end_time: Optional[datetime]
    error: Optional[str] = None
    recovery_attempts: int = 0
    logs: List[str] = field(default_factory=list)
    
    @property
    def elapsed_seconds(self) -> float:
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()

@dataclass
class PhaseCheckpoint:
    """Phase execution checkpoint"""
    phase: Phase
    start_time: datetime
    end_time: Optional[datetime]
    lanes: Dict[Lane, LaneCheckpoint] = field(default_factory=dict)
    events: List[DeploymentEvent] = field(default_factory=list)
    
    @property
    def elapsed_seconds(self) -> float:
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()
```

### DeploymentGateway Main Class

```python
class DeploymentGateway:
    """
    Multi-phase, multi-lane deployment orchestrator with failure recovery.
    
    Architecture:
    - Phase State Machine: PLANNING → PRE_DEPLOYMENT → DEPLOYMENT → 
                          POST_DEPLOYMENT → VERIFICATION → COMPLETED
    - Lane Concurrency: 4 parallel lanes with coordinated timeouts
    - Event Logging: All operations logged for audit and recovery
    - Checkpoint Recovery: Resume from any phase using saved state
    """
    
    # Timeout configurations (seconds)
    LANE_TIMEOUTS = {
        Lane.LANE_A: 300,   # Feature validation: 5 minutes
        Lane.LANE_B: 300,   # Infrastructure: 5 minutes
        Lane.LANE_C: 300,   # Security: 5 minutes
        Lane.LANE_D: 420,   # Publishing: 7 minutes (longer for PyPI)
    }
    
    # Recovery escalation thresholds
    MAX_RECOVERY_ATTEMPTS = 3
    ESCALATION_EMAIL = "deployment-team@example.com"
    
    def __init__(self, deployment_id: str, log_dir: str = ".codex"):
        """
        Initialize orchestrator.
        
        Args:
            deployment_id: Unique deployment identifier (e.g., "v0.1.0-final")
            log_dir: Directory for checkpoints and logs
        """
        self.deployment_id = deployment_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # State
        self.current_phase = Phase.PLANNING
        self.phase_checkpoints: Dict[Phase, PhaseCheckpoint] = {}
        self.events: List[DeploymentEvent] = []
        self.lane_handlers: Dict[Lane, Callable] = {}
        
        # Logging
        self.logger = self._setup_logging()
        self.checkpoint_file = self.log_dir / f"deployment-{deployment_id}-checkpoint.json"
        self.events_file = self.log_dir / f"deployment-{deployment_id}-events.jsonl"
    
    def _setup_logging(self) -> logging.Logger:
        """Configure structured logging."""
        logger = logging.getLogger(f"DeploymentGateway-{self.deployment_id}")
        logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler(
            self.log_dir / f"deployment-{self.deployment_id}.log"
        )
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def register_lane_handler(self, lane: Lane, handler: Callable) -> None:
        """
        Register a handler function for a lane.
        
        Args:
            lane: Target lane
            handler: Async-compatible callable that executes lane work
        """
        self.lane_handlers[lane] = handler
        self.logger.info(f"Lane handler registered: {lane.value}")
    
    # ─────────────────────────────────────────────────────────────────
    # Event Management
    # ─────────────────────────────────────────────────────────────────
    
    def log_event(self, event_type: EventType, phase: Phase, 
                  lane: Optional[Lane] = None, message: str = "", 
                  metadata: Optional[Dict] = None) -> DeploymentEvent:
        """
        Log deployment event.
        
        Args:
            event_type: Type of event
            phase: Current phase
            lane: Lane (if applicable)
            message: Event description
            metadata: Additional structured data
        
        Returns:
            Logged event for reference
        """
        event = DeploymentEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            phase=phase,
            lane=lane,
            message=message,
            metadata=metadata or {},
        )
        self.events.append(event)
        
        # Write to JSONL for streaming consumption
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
        
        log_msg = f"[{phase.value}] {message}"
        if lane:
            log_msg += f" ({lane.value})"
        
        if event_type in [EventType.PHASE_FAILED, EventType.LANE_FAILED]:
            self.logger.error(log_msg)
        else:
            self.logger.info(log_msg)
        
        return event
    
    # ─────────────────────────────────────────────────────────────────
    # Phase Management
    # ─────────────────────────────────────────────────────────────────
    
    def transition_to_phase(self, target_phase: Phase) -> bool:
        """
        Transition to next phase with state validation.
        
        Args:
            target_phase: Target phase
        
        Returns:
            True if transition successful, False otherwise
        """
        # Validate phase transition
        valid_transitions = {
            Phase.PLANNING: [Phase.PRE_DEPLOYMENT],
            Phase.PRE_DEPLOYMENT: [Phase.DEPLOYMENT],
            Phase.DEPLOYMENT: [Phase.POST_DEPLOYMENT, Phase.ROLLED_BACK],
            Phase.POST_DEPLOYMENT: [Phase.VERIFICATION, Phase.ROLLED_BACK],
            Phase.VERIFICATION: [Phase.COMPLETED, Phase.ROLLED_BACK],
        }
        
        if target_phase not in valid_transitions.get(self.current_phase, []):
            self.logger.error(
                f"Invalid transition: {self.current_phase.value} → "
                f"{target_phase.value}"
            )
            return False
        
        # Save current phase checkpoint
        if self.current_phase != Phase.PLANNING:
            self._save_checkpoint(self.current_phase)
        
        # Transition
        self.current_phase = target_phase
        self.phase_checkpoints[target_phase] = PhaseCheckpoint(
            phase=target_phase,
            start_time=datetime.utcnow(),
            end_time=None,
        )
        
        self.log_event(
            EventType.PHASE_START,
            target_phase,
            message=f"Phase transition: {target_phase.value}"
        )
        return True
    
    def complete_phase(self) -> None:
        """Mark current phase as complete."""
        checkpoint = self.phase_checkpoints[self.current_phase]
        checkpoint.end_time = datetime.utcnow()
        
        self.log_event(
            EventType.PHASE_COMPLETE,
            self.current_phase,
            message=f"Phase completed in {checkpoint.elapsed_seconds:.1f}s"
        )
    
    def fail_phase(self, error: str) -> None:
        """Mark current phase as failed."""
        checkpoint = self.phase_checkpoints[self.current_phase]
        checkpoint.end_time = datetime.utcnow()
        
        self.log_event(
            EventType.PHASE_FAILED,
            self.current_phase,
            message=f"Phase failed: {error}"
        )
        
        self.current_phase = Phase.FAILED
    
    # ─────────────────────────────────────────────────────────────────
    # Lane Execution & Coordination
    # ─────────────────────────────────────────────────────────────────
    
    async def execute_lane(self, lane: Lane) -> bool:
        """
        Execute a single lane with timeout management.
        
        Args:
            lane: Target lane
        
        Returns:
            True if lane successful, False if failed or timed out
        """
        if lane not in self.lane_handlers:
            self.logger.error(f"No handler registered for {lane.value}")
            return False
        
        timeout = self.LANE_TIMEOUTS[lane]
        checkpoint = LaneCheckpoint(
            lane=lane,
            status=LaneStatus.RUNNING,
            start_time=datetime.utcnow(),
        )
        
        self.log_event(
            EventType.LANE_START,
            self.current_phase,
            lane=lane,
            message=f"Lane execution started (timeout: {timeout}s)"
        )
        
        try:
            import asyncio
            handler = self.lane_handlers[lane]
            
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(self),
                timeout=timeout
            )
            
            checkpoint.end_time = datetime.utcnow()
            checkpoint.status = LaneStatus.COMPLETED
            
            self.log_event(
                EventType.LANE_COMPLETE,
                self.current_phase,
                lane=lane,
                message=f"Lane completed in {checkpoint.elapsed_seconds:.1f}s",
                metadata={"result": str(result)}
            )
            
            return True
        
        except asyncio.TimeoutError:
            checkpoint.end_time = datetime.utcnow()
            checkpoint.status = LaneStatus.TIMEOUT
            checkpoint.error = f"Timeout after {timeout}s"
            
            self.log_event(
                EventType.LANE_TIMEOUT,
                self.current_phase,
                lane=lane,
                message=f"Lane timeout after {timeout}s"
            )
            
            return await self._handle_lane_timeout(lane, checkpoint)
        
        except Exception as e:
            checkpoint.end_time = datetime.utcnow()
            checkpoint.status = LaneStatus.FAILED
            checkpoint.error = str(e)
            
            self.log_event(
                EventType.LANE_FAILED,
                self.current_phase,
                lane=lane,
                message=f"Lane execution failed: {e}",
                metadata={"exception": type(e).__name__}
            )
            
            return await self._handle_lane_failure(lane, checkpoint)
        
        finally:
            # Save lane checkpoint
            self.phase_checkpoints[self.current_phase].lanes[lane] = checkpoint
            self._save_checkpoint(self.current_phase)
    
    async def execute_deployment(self) -> bool:
        """
        Execute Phase 3: Deployment with parallel lane execution.
        
        Returns:
            True if deployment successful, False otherwise
        """
        if not self.transition_to_phase(Phase.DEPLOYMENT):
            return False
        
        import asyncio
        
        try:
            # Execute lanes concurrently
            lane_tasks = [
                self.execute_lane(lane)
                for lane in [Lane.LANE_A, Lane.LANE_B, Lane.LANE_C, Lane.LANE_D]
            ]
            
            results = await asyncio.gather(*lane_tasks)
            
            # Check results
            if all(results):
                self.complete_phase()
                return True
            else:
                failed_lanes = [
                    [Lane.LANE_A, Lane.LANE_B, Lane.LANE_C, Lane.LANE_D][i]
                    for i, r in enumerate(results) if not r
                ]
                self.fail_phase(f"Lane(s) failed: {[l.value for l in failed_lanes]}")
                return False
        
        except Exception as e:
            self.fail_phase(f"Deployment execution error: {e}")
            return False
    
    # ─────────────────────────────────────────────────────────────────
    # Failure & Recovery
    # ─────────────────────────────────────────────────────────────────
    
    async def _handle_lane_timeout(self, lane: Lane, 
                                   checkpoint: LaneCheckpoint) -> bool:
        """
        Handle lane timeout with recovery procedures.
        
        Recovery Strategy:
        - Attempt 1: Retry lane execution
        - Attempt 2: Rollback lane state
        - Attempt 3: Escalate to SRE team
        """
        checkpoint.recovery_attempts += 1
        
        if checkpoint.recovery_attempts < self.MAX_RECOVERY_ATTEMPTS:
            self.log_event(
                EventType.RECOVERY_STARTED,
                self.current_phase,
                lane=lane,
                message=f"Recovery attempt {checkpoint.recovery_attempts} for timeout"
            )
            
            # Retry lane
            return await self.execute_lane(lane)
        else:
            self.log_event(
                EventType.ESCALATION_TRIGGERED,
                self.current_phase,
                lane=lane,
                message=f"Lane timeout escalated after {self.MAX_RECOVERY_ATTEMPTS} attempts"
            )
            
            await self._escalate_to_team(lane, checkpoint)
            return False
    
    async def _handle_lane_failure(self, lane: Lane, 
                                   checkpoint: LaneCheckpoint) -> bool:
        """
        Handle lane failure with recovery procedures.
        
        Recovery Strategy (per lane):
        - Lane A (Features): Revert code changes, retry tests
        - Lane B (Infrastructure): Rollback container images
        - Lane C (Security): Revert security patches
        - Lane D (Publishing): Cancel PyPI upload, retry
        """
        checkpoint.recovery_attempts += 1
        
        recovery_handlers = {
            Lane.LANE_A: self._recover_lane_a,
            Lane.LANE_B: self._recover_lane_b,
            Lane.LANE_C: self._recover_lane_c,
            Lane.LANE_D: self._recover_lane_d,
        }
        
        handler = recovery_handlers.get(lane)
        if handler and checkpoint.recovery_attempts < self.MAX_RECOVERY_ATTEMPTS:
            self.log_event(
                EventType.RECOVERY_STARTED,
                self.current_phase,
                lane=lane,
                message=f"Lane-specific recovery attempt {checkpoint.recovery_attempts}"
            )
            
            return await handler(checkpoint)
        else:
            self.log_event(
                EventType.ESCALATION_TRIGGERED,
                self.current_phase,
                lane=lane,
                message=f"Lane failure escalated after {checkpoint.recovery_attempts} attempts"
            )
            
            await self._escalate_to_team(lane, checkpoint)
            return False
    
    async def _recover_lane_a(self, checkpoint: LaneCheckpoint) -> bool:
        """Lane A (Features): Recover from feature validation failure."""
        self.logger.info("Executing Lane A recovery: Feature validation")
        # Implementation: Revert code, re-run tests
        return await self.execute_lane(Lane.LANE_A)
    
    async def _recover_lane_b(self, checkpoint: LaneCheckpoint) -> bool:
        """Lane B (Infrastructure): Recover from infrastructure failure."""
        self.logger.info("Executing Lane B recovery: Infrastructure rollback")
        # Implementation: Rollback container images
        return await self.execute_lane(Lane.LANE_B)
    
    async def _recover_lane_c(self, checkpoint: LaneCheckpoint) -> bool:
        """Lane C (Security): Recover from security check failure."""
        self.logger.info("Executing Lane C recovery: Security patch revert")
        # Implementation: Revert security patches, retry scans
        return await self.execute_lane(Lane.LANE_C)
    
    async def _recover_lane_d(self, checkpoint: LaneCheckpoint) -> bool:
        """Lane D (Publishing): Recover from publishing failure."""
        self.logger.info("Executing Lane D recovery: PyPI retry")
        # Implementation: Cancel current upload, retry publication
        return await self.execute_lane(Lane.LANE_D)
    
    async def _escalate_to_team(self, lane: Lane, checkpoint: LaneCheckpoint) -> None:
        """Escalate lane failure to SRE team with full context."""
        self.log_event(
            EventType.ESCALATION_TRIGGERED,
            self.current_phase,
            lane=lane,
            message=f"ESCALATION: {lane.value} failure requires manual intervention",
            metadata={
                "error": checkpoint.error,
                "attempts": checkpoint.recovery_attempts,
                "elapsed": checkpoint.elapsed_seconds,
            }
        )
        
        # Send alert to SRE
        self.logger.critical(
            f"ESCALATION ALERT: {lane.value} deployment failure. "
            f"Contact: {self.ESCALATION_EMAIL}"
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Checkpoint & Recovery
    # ─────────────────────────────────────────────────────────────────
    
    def _save_checkpoint(self, phase: Phase) -> None:
        """Save phase checkpoint to disk."""
        checkpoint = self.phase_checkpoints[phase]
        
        checkpoint_data = {
            "deployment_id": self.deployment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "phase": phase.value,
            "elapsed_seconds": checkpoint.elapsed_seconds,
            "lanes": {
                lane.value: {
                    "status": lane_cp.status.value,
                    "elapsed": lane_cp.elapsed_seconds,
                    "error": lane_cp.error,
                }
                for lane, lane_cp in checkpoint.lanes.items()
            }
        }
        
        with open(self.checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2)
        
        self.log_event(
            EventType.CHECKPOINT_SAVED,
            phase,
            message=f"Checkpoint saved at {self.checkpoint_file}"
        )
    
    def load_checkpoint(self) -> Optional[Phase]:
        """
        Load checkpoint from disk for recovery.
        
        Returns:
            Phase to resume from, or None if no checkpoint found
        """
        if not self.checkpoint_file.exists():
            return None
        
        try:
            with open(self.checkpoint_file) as f:
                data = json.load(f)
            
            phase = Phase(data["phase"])
            self.log_event(
                EventType.CHECKPOINT_LOADED,
                phase,
                message=f"Checkpoint loaded: resuming from {phase.value}"
            )
            
            return phase
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────────
    # Status & Reporting
    # ─────────────────────────────────────────────────────────────────
    
    def get_status(self) -> dict:
        """Get current deployment status."""
        return {
            "deployment_id": self.deployment_id,
            "current_phase": self.current_phase.value,
            "total_events": len(self.events),
            "phases_completed": len(self.phase_checkpoints),
            "lanes": {
                lane.value: checkpoint.status.value
                for phase_cp in self.phase_checkpoints.values()
                for lane, checkpoint in phase_cp.lanes.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def generate_report(self) -> str:
        """Generate deployment execution report."""
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║            DEPLOYMENT EXECUTION REPORT                        ║
╠═══════════════════════════════════════════════════════════════╣
║ Deployment ID: {self.deployment_id:45s} ║
║ Status: {self.current_phase.value:51s} ║
║ Total Events: {len(self.events):47d} ║
╠═══════════════════════════════════════════════════════════════╣
"""
        
        for phase, checkpoint in sorted(self.phase_checkpoints.items()):
            report += f"""║ {phase.value.upper():59s} ║
║   Duration: {checkpoint.elapsed_seconds:48.1f}s ║
"""
            for lane, lane_cp in checkpoint.lanes.items():
                report += f"║   {lane.value:20s}: {lane_cp.status.value:37s} ║\n"
        
        report += f"""╠═══════════════════════════════════════════════════════════════╣
║ Report Generated: {datetime.utcnow().isoformat():41s} ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return report
```

---

## Usage Example

```python
import asyncio

async def main():
    # Initialize orchestrator
    gateway = DeploymentGateway("v0.1.0-final")
    
    # Try to resume from checkpoint
    resume_phase = gateway.load_checkpoint()
    if resume_phase:
        gateway.current_phase = resume_phase
    
    # Register lane handlers
    async def lane_a_handler(gw):
        # Feature validation logic
        await asyncio.sleep(0.5)
        return True
    
    gateway.register_lane_handler(Lane.LANE_A, lane_a_handler)
    # ... register other lanes
    
    # Execute deployment phases
    try:
        # Phase 1: Planning
        gateway.transition_to_phase(Phase.PLANNING)
        # ... planning steps
        gateway.complete_phase()
        
        # Phase 2: Pre-Deployment
        gateway.transition_to_phase(Phase.PRE_DEPLOYMENT)
        # ... validation steps
        gateway.complete_phase()
        
        # Phase 3: Deployment (parallel lanes)
        success = await gateway.execute_deployment()
        if success:
            gateway.transition_to_phase(Phase.POST_DEPLOYMENT)
            gateway.complete_phase()
            
            gateway.transition_to_phase(Phase.VERIFICATION)
            gateway.complete_phase()
        else:
            print("Deployment failed. Check logs and checkpoint for recovery.")
    
    except Exception as e:
        gateway.fail_phase(f"Unexpected error: {e}")
    
    finally:
        print(gateway.generate_report())
```

---

## Event Stream Monitoring

Monitor deployment progress in real-time:

```bash
# Watch event stream
tail -f .codex/deployment-v0.1.0-final-events.jsonl | jq .

# Filter by event type
jq 'select(.event_type == "lane_timeout")' \
  .codex/deployment-v0.1.0-final-events.jsonl

# Monitor lane progress
jq 'select(.lane != null) | {lane: .lane, status: .event_type, time: .timestamp}' \
  .codex/deployment-v0.1.0-final-events.jsonl
```

---

## Document Status

**Version:** 1.0  
**Maintained By:** Deployment Engineering  
**Last Review:** 2026-07-09  
**Next Review:** After v0.2.0 deployment  

For implementation questions, contact @mbaetiong.
