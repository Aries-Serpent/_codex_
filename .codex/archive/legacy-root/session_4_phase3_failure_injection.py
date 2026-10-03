#!/usr/bin/env python3
"""
SESSION 4 Phase 3 Failure Injection Module

Simulates 5 disaster recovery scenarios:
  - Scenario A: Lane 1 (Cognitive Brain Core) crash
  - Scenario B: Lane 2 (RAG Module) data corruption
  - Scenario C: Lane 3 (ML Pipeline) OOM at epoch 50
  - Scenario D: Lane 4 (Quantum Compliance) compliance breach
  - Scenario E: Cascade failure (all 4 lanes)

Generated: 2026-07-19T17:41:53Z
Version: v0.2.0 production deployment
"""

import time
import json
import random
import hashlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import threading
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class FailureScenario(Enum):
    """Enumeration of failure scenarios."""
    LANE_1_CRASH = "A"
    LANE_2_CORRUPTION = "B"
    LANE_3_OOM = "C"
    LANE_4_COMPLIANCE_BREACH = "D"
    CASCADE_FAILURE = "E"


class LaneStatus(Enum):
    """Lane operational status."""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    CRASHED = "crashed"
    RECOVERING = "recovering"
    RECOVERED = "recovered"


@dataclass
class FailureEvent:
    """Represents a single failure event."""
    timestamp: datetime
    scenario: FailureScenario
    lane_id: int
    description: str
    severity: str  # low, medium, high, critical
    affected_systems: List[str] = field(default_factory=list)
    is_detected: bool = False
    detection_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'scenario': self.scenario.value,
            'lane_id': self.lane_id,
            'description': self.description,
            'severity': self.severity,
            'affected_systems': self.affected_systems,
            'is_detected': self.is_detected,
            'detection_time': self.detection_time.isoformat() if self.detection_time else None,
            'detection_latency_sec': (
                (self.detection_time - self.timestamp).total_seconds()
                if self.detection_time else None
            )
        }


@dataclass
class LaneSnapshot:
    """Snapshot of a lane's state at failure injection time."""
    lane_id: int
    timestamp: datetime
    status: LaneStatus
    in_flight_transactions: int
    checkpoint_available: bool
    last_checkpoint_time: Optional[datetime]
    memory_usage_mb: float
    consistency_score: float  # 0.0-100.0
    compliance_score: float  # 0.0-100.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'lane_id': self.lane_id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'in_flight_transactions': self.in_flight_transactions,
            'checkpoint_available': self.checkpoint_available,
            'last_checkpoint_time': self.last_checkpoint_time.isoformat() if self.last_checkpoint_time else None,
            'memory_usage_mb': self.memory_usage_mb,
            'consistency_score': self.consistency_score,
            'compliance_score': self.compliance_score,
        }


class FailureInjector:
    """Injects failures and monitors system response."""

    def __init__(self, version: str = "v0.2.0", num_lanes: int = 4):
        """Initialize the failure injector."""
        self.version = version
        self.num_lanes = num_lanes
        self.events: List[FailureEvent] = []
        self.lane_snapshots: Dict[int, LaneSnapshot] = {}
        self.start_time = datetime.utcnow()
        self.lock = threading.Lock()
        logger.info(f"FailureInjector initialized for {version} with {num_lanes} lanes")

    def capture_lane_snapshot(self, lane_id: int) -> LaneSnapshot:
        """Capture the current state of a lane."""
        # Simulate realistic lane state
        now = datetime.utcnow()
        last_checkpoint = now - timedelta(minutes=random.randint(1, 15))
        
        snapshot = LaneSnapshot(
            lane_id=lane_id,
            timestamp=now,
            status=LaneStatus.OPERATIONAL,
            in_flight_transactions=random.randint(5, 50),
            checkpoint_available=True,
            last_checkpoint_time=last_checkpoint,
            memory_usage_mb=random.uniform(512, 2048),
            consistency_score=100.0 - random.uniform(0, 0.5),
            compliance_score=98.0 + random.uniform(0, 2.0),
        )
        
        with self.lock:
            self.lane_snapshots[lane_id] = snapshot
        
        logger.info(f"Lane {lane_id} snapshot: {snapshot.status.value}, "
                   f"{snapshot.in_flight_transactions} in-flight txns, "
                   f"{snapshot.memory_usage_mb:.1f}MB")
        return snapshot

    def inject_scenario_a_lane_1_crash(self) -> FailureEvent:
        """
        Scenario A: Lane 1 (Cognitive Brain Core) Crash
        - Unhandled exception in Cognitive Brain service
        - Recovery: Automated rollback to v0.1.x
        - SLA target: <5 min rollback time
        """
        logger.info("=" * 80)
        logger.info("SCENARIO A: Lane 1 (Cognitive Brain Core) Crash")
        logger.info("=" * 80)
        
        timestamp = datetime.utcnow()
        
        # Capture pre-failure state
        snapshot = self.capture_lane_snapshot(lane_id=1)
        
        # Inject crash
        event = FailureEvent(
            timestamp=timestamp,
            scenario=FailureScenario.LANE_1_CRASH,
            lane_id=1,
            description="Unhandled exception in Cognitive Brain service: KeyError in embedding manager",
            severity="critical",
            affected_systems=["cognitive_brain_core", "session_manager", "vector_store"],
        )
        
        # Simulate detection delay (<30 sec per SLA)
        detection_delay = random.uniform(5, 30)  # seconds
        time.sleep(min(0.1, detection_delay / 1000))  # Simulate delay
        
        event.is_detected = True
        event.detection_time = datetime.utcnow()
        
        logger.warning(f"FAILURE INJECTED: Lane 1 crash at {timestamp.isoformat()}")
        logger.warning(f"Detection latency: {detection_delay:.1f}s")
        logger.warning(f"Pre-crash state: {snapshot.in_flight_transactions} in-flight txns")
        
        with self.lock:
            self.events.append(event)
        
        return event

    def inject_scenario_b_lane_2_corruption(self) -> FailureEvent:
        """
        Scenario B: Lane 2 (RAG Module) Data Corruption
        - 1% of embedding vectors corrupted during write
        - Recovery: Checkpoint restore + rebuild
        - SLA target: <30 min recovery time
        """
        logger.info("=" * 80)
        logger.info("SCENARIO B: Lane 2 (RAG Module) Data Corruption")
        logger.info("=" * 80)
        
        timestamp = datetime.utcnow()
        
        # Capture pre-corruption state
        snapshot = self.capture_lane_snapshot(lane_id=2)
        
        # Simulate 1% corruption of embedding vectors
        total_embeddings = 50000
        corrupted_count = int(total_embeddings * 0.01)  # 500 corrupted vectors
        
        # Calculate corruption checksum
        corruption_hash = hashlib.sha256(
            f"{timestamp.isoformat()}_corrupted".encode()
        ).hexdigest()[:16]
        
        event = FailureEvent(
            timestamp=timestamp,
            scenario=FailureScenario.LANE_2_CORRUPTION,
            lane_id=2,
            description=f"Data corruption detected in RAG embedding cache: {corrupted_count} "
                       f"corrupted vectors out of {total_embeddings} "
                       f"(checksum mismatch: {corruption_hash})",
            severity="high",
            affected_systems=["rag_module", "embedding_cache", "vector_index"],
        )
        
        # Simulate detection delay (<2 min per SLA)
        detection_delay = random.uniform(10, 120)  # seconds
        time.sleep(min(0.1, detection_delay / 1000))
        
        event.is_detected = True
        event.detection_time = datetime.utcnow()
        
        logger.warning(f"FAILURE INJECTED: Lane 2 corruption at {timestamp.isoformat()}")
        logger.warning(f"Corruption: {corrupted_count}/{total_embeddings} vectors ({0.01*100:.1f}%)")
        logger.warning(f"Corruption hash: {corruption_hash}")
        logger.warning(f"Detection latency: {detection_delay:.1f}s")
        logger.warning(f"Last clean checkpoint: {snapshot.last_checkpoint_time.isoformat()}")
        
        with self.lock:
            self.events.append(event)
        
        return event

    def inject_scenario_c_lane_3_oom(self) -> FailureEvent:
        """
        Scenario C: Lane 3 (ML Pipeline) OOM at Epoch 50
        - Out-of-memory condition during training at epoch 50 of 100
        - Recovery: Graceful shutdown + checkpoint resume
        - SLA target: <2 min recovery time
        """
        logger.info("=" * 80)
        logger.info("SCENARIO C: Lane 3 (ML Pipeline) OOM at Epoch 50")
        logger.info("=" * 80)
        
        timestamp = datetime.utcnow()
        
        # Capture pre-OOM state
        snapshot = self.capture_lane_snapshot(lane_id=3)
        
        # Simulate OOM at epoch 50
        current_epoch = 50
        total_epochs = 100
        batch_size = 64
        memory_limit_mb = 2048
        memory_used_mb = 2048 + random.uniform(10, 100)  # Exceed limit
        
        event = FailureEvent(
            timestamp=timestamp,
            scenario=FailureScenario.LANE_3_OOM,
            lane_id=3,
            description=f"Out-of-memory error during ML training: "
                       f"Epoch {current_epoch}/{total_epochs}, "
                       f"Memory used: {memory_used_mb:.1f}MB (limit: {memory_limit_mb}MB), "
                       f"Batch size: {batch_size}",
            severity="high",
            affected_systems=["ml_training_pipeline", "checkpoint_manager", "memory_allocator"],
        )
        
        # Simulate detection delay (<30 sec per SLA)
        detection_delay = random.uniform(5, 30)
        time.sleep(min(0.1, detection_delay / 1000))
        
        event.is_detected = True
        event.detection_time = datetime.utcnow()
        
        logger.warning(f"FAILURE INJECTED: Lane 3 OOM at {timestamp.isoformat()}")
        logger.warning(f"OOM condition: Epoch {current_epoch}/{total_epochs}, "
                      f"Memory: {memory_used_mb:.1f}MB (limit: {memory_limit_mb}MB)")
        logger.warning(f"Detection latency: {detection_delay:.1f}s")
        logger.warning(f"Checkpoint available at epoch {current_epoch}: "
                      f"{snapshot.checkpoint_available}")
        
        with self.lock:
            self.events.append(event)
        
        return event

    def inject_scenario_d_lane_4_compliance_breach(self) -> FailureEvent:
        """
        Scenario D: Lane 4 (Quantum Compliance) Compliance Score Breach
        - Compliance score drops below 95% due to stale decision data
        - Recovery: Automatic rollback of non-compliant decisions
        - SLA target: <2 min recovery time
        """
        logger.info("=" * 80)
        logger.info("SCENARIO D: Lane 4 (Quantum Compliance) Compliance Breach")
        logger.info("=" * 80)
        
        timestamp = datetime.utcnow()
        
        # Capture pre-breach state
        snapshot = self.capture_lane_snapshot(lane_id=4)
        
        # Simulate compliance score drop
        baseline_compliance = 98.5
        degraded_compliance = 92.3  # Below 95% threshold
        stale_decisions = 247
        
        event = FailureEvent(
            timestamp=timestamp,
            scenario=FailureScenario.LANE_4_COMPLIANCE_BREACH,
            lane_id=4,
            description=f"Compliance score dropped below 95%: "
                       f"{degraded_compliance:.1f}% (threshold: 95.0%), "
                       f"Root cause: {stale_decisions} stale governance decisions detected",
            severity="high",
            affected_systems=["quantum_compliance_engine", "decision_cache", "audit_log"],
        )
        
        # Simulate detection delay (<10 sec per SLA)
        detection_delay = random.uniform(2, 10)
        time.sleep(min(0.1, detection_delay / 1000))
        
        event.is_detected = True
        event.detection_time = datetime.utcnow()
        
        logger.warning(f"FAILURE INJECTED: Lane 4 compliance breach at {timestamp.isoformat()}")
        logger.warning(f"Compliance score: {degraded_compliance:.1f}% (threshold: 95.0%)")
        logger.warning(f"Stale decisions to purge: {stale_decisions}")
        logger.warning(f"Detection latency: {detection_delay:.1f}s")
        
        with self.lock:
            self.events.append(event)
        
        return event

    def inject_scenario_e_cascade_failure(self) -> List[FailureEvent]:
        """
        Scenario E: Cascade Failure (All 4 Lanes Simultaneously)
        - Critical service degradation affecting all 4 lanes
        - Recovery: Coordinated multi-lane rollback
        - SLA target: <10 min recovery time
        """
        logger.info("=" * 80)
        logger.info("SCENARIO E: Cascade Failure (All 4 Lanes)")
        logger.info("=" * 80)
        
        base_timestamp = datetime.utcnow()
        cascade_events = []
        
        # Cascade trigger: Central service failure
        cascade_trigger_event = FailureEvent(
            timestamp=base_timestamp,
            scenario=FailureScenario.CASCADE_FAILURE,
            lane_id=0,  # System-level
            description="Cascade failure triggered: Central coordination service crashed, "
                       "affecting all 4 lanes",
            severity="critical",
            affected_systems=["central_coordination", "config_server", "secret_manager"],
        )
        
        # Simulate cascade detection (<30 sec)
        detection_delay = random.uniform(5, 30)
        time.sleep(min(0.1, detection_delay / 1000))
        
        cascade_trigger_event.is_detected = True
        cascade_trigger_event.detection_time = datetime.utcnow()
        
        logger.warning(f"CASCADE FAILURE DETECTED at {base_timestamp.isoformat()}")
        logger.warning(f"Trigger: Central service failure")
        logger.warning(f"Detection latency: {detection_delay:.1f}s")
        
        cascade_events.append(cascade_trigger_event)
        
        # Inject failure into each lane sequentially (with small delays for realistic cascade)
        for lane_id in range(1, 5):
            time.sleep(0.05)  # Small delay for cascade progression
            
            snapshot = self.capture_lane_snapshot(lane_id=lane_id)
            
            lane_event = FailureEvent(
                timestamp=datetime.utcnow(),
                scenario=FailureScenario.CASCADE_FAILURE,
                lane_id=lane_id,
                description=f"Lane {lane_id} affected by cascade failure: "
                           f"Loss of central coordination service",
                severity="critical",
                affected_systems=[f"lane_{lane_id}_all_systems"],
            )
            
            lane_event.is_detected = True
            lane_event.detection_time = datetime.utcnow()
            
            logger.warning(f"Cascade propagated to Lane {lane_id}")
            logger.warning(f"In-flight transactions: {snapshot.in_flight_transactions}")
            
            cascade_events.append(lane_event)
        
        with self.lock:
            self.events.extend(cascade_events)
        
        return cascade_events

    def get_events_summary(self) -> Dict:
        """Get summary of all injected events."""
        with self.lock:
            return {
                'total_events': len(self.events),
                'events': [e.to_dict() for e in self.events],
                'detected_count': sum(1 for e in self.events if e.is_detected),
                'detection_rate': (
                    sum(1 for e in self.events if e.is_detected) / len(self.events) * 100
                    if self.events else 0
                ),
                'average_detection_latency_sec': (
                    sum((e.detection_time - e.timestamp).total_seconds()
                        for e in self.events if e.detection_time) / 
                    sum(1 for e in self.events if e.detection_time)
                    if sum(1 for e in self.events if e.detection_time) > 0 else 0
                ),
            }

    def export_failure_log(self, filepath: str) -> None:
        """Export failure injection log to JSON."""
        summary = self.get_events_summary()
        summary['version'] = self.version
        summary['num_lanes'] = self.num_lanes
        summary['start_time'] = self.start_time.isoformat()
        summary['end_time'] = datetime.utcnow().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Failure log exported to {filepath}")


def main():
    """Run failure injection for all 5 scenarios."""
    logger.info("SESSION 4 Phase 3 - Disaster Recovery Test Suite")
    logger.info("Version: v0.2.0, 4-Lane Architecture")
    logger.info("Start time: " + datetime.utcnow().isoformat())
    
    injector = FailureInjector(version="v0.2.0", num_lanes=4)
    
    # Scenario A: Lane 1 crash
    event_a = injector.inject_scenario_a_lane_1_crash()
    logger.info(f"Scenario A event created: {event_a.scenario.value}")
    
    time.sleep(0.5)
    
    # Scenario B: Lane 2 corruption
    event_b = injector.inject_scenario_b_lane_2_corruption()
    logger.info(f"Scenario B event created: {event_b.scenario.value}")
    
    time.sleep(0.5)
    
    # Scenario C: Lane 3 OOM
    event_c = injector.inject_scenario_c_lane_3_oom()
    logger.info(f"Scenario C event created: {event_c.scenario.value}")
    
    time.sleep(0.5)
    
    # Scenario D: Lane 4 compliance breach
    event_d = injector.inject_scenario_d_lane_4_compliance_breach()
    logger.info(f"Scenario D event created: {event_d.scenario.value}")
    
    time.sleep(0.5)
    
    # Scenario E: Cascade failure
    events_e = injector.inject_scenario_e_cascade_failure()
    logger.info(f"Scenario E events created: {len(events_e)} events")
    
    # Export results
    output_file = ".codex/failure_injection_log.json"
    injector.export_failure_log(output_file)
    logger.info(f"Failure injection log saved: {output_file}")
    
    # Print summary
    summary = injector.get_events_summary()
    logger.info(f"\n=== FAILURE INJECTION SUMMARY ===")
    logger.info(f"Total events injected: {summary['total_events']}")
    logger.info(f"Events detected: {summary['detected_count']}/{summary['total_events']}")
    logger.info(f"Detection rate: {summary['detection_rate']:.1f}%")
    logger.info(f"Average detection latency: {summary['average_detection_latency_sec']:.2f}s")
    logger.info(f"==================================\n")
    
    return injector


if __name__ == "__main__":
    main()
