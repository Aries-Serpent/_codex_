"""Phase 4 Telemetry Classifier - Pattern Execution & Classification

This module integrates pattern execution telemetry with Phase 4 self-healing loop.
Captures pattern-based CI failure fixes and routes unknown failures to classifier.

Key Functions:
  - record_pattern_execution(): Log pattern execution with outcome
  - classify_unknown_failure(): Map unmapped errors to best-matching pattern
  - generate_telemetry_summary(): Aggregate per-session metrics
  - route_to_self_healer(): Queue pattern for autonomous fix attempt

Integration Points:
  - CI Auto-Healer Agent: Executes patterns, calls record_pattern_execution()
  - Telemetry Classifier Agent: Reads JSONL, classifies unknowns
  - Knowledge Graph: Queries pattern metadata for routing
  - Self-Healing Loop: Receives routed patterns from classifier

Telemetry Output:
  - `.codex/telemetry/pattern_execution_{session_id}.jsonl` (live events)
  - `.codex/telemetry/pattern_summary_{session_id}.json` (session aggregate)
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class PatternExecutionEvent:
    """Telemetry event for pattern execution"""
    pattern_id: str
    timestamp: str
    phase: int
    lane: int
    session_id: str
    agent_id: str
    status: str  # "success", "failure", "timeout"
    duration_ms: int
    execution_count: int
    context: Dict


@dataclass
class TelemetrySummary:
    """Per-session telemetry aggregate"""
    session_id: str
    timestamp_start: str
    timestamp_end: str
    total_patterns_executed: int
    successful: int
    failed: int
    avg_duration_ms: int
    total_overhead_ms: int
    patterns_used: List[str]
    phase: int
    lane: int
    unknown_classifications: int


class PatternExecutionTelemetry:
    """Telemetry collection for pattern-based CI self-healing"""
    
    def __init__(self, telemetry_dir: str = ".codex/telemetry", 
                 knowledge_graph_path: str = ".codex/knowledge_graph/graph.json"):
        self.telemetry_dir = Path(telemetry_dir)
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_graph_path = knowledge_graph_path
        self.session_events: List[PatternExecutionEvent] = []
        self.session_start = datetime.utcnow().isoformat() + "Z"
        
    def load_knowledge_graph(self) -> Dict:
        """Load pattern metadata from knowledge graph"""
        try:
            with open(self.knowledge_graph_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"nodes": [], "edges": []}
    
    def record_pattern_execution(self, pattern_id: str, status: str, 
                                  duration_ms: int, session_id: str, 
                                  phase: int, lane: int, agent_id: str,
                                  context: Optional[Dict] = None) -> Dict:
        """Record pattern execution event to JSONL
        
        Args:
            pattern_id: RP-XXX pattern identifier
            status: "success", "failure", or "timeout"
            duration_ms: Execution time in milliseconds
            session_id: Unique session identifier
            phase: Phase number (1, 2, 3, ...)
            lane: Lane number (1, 2, 3, 4)
            agent_id: Executing agent identifier
            context: Additional context (workflow, commit, etc.)
            
        Returns:
            Event dict as written to telemetry JSONL
        """
        event = PatternExecutionEvent(
            pattern_id=pattern_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=phase,
            lane=lane,
            session_id=session_id,
            agent_id=agent_id,
            status=status,
            duration_ms=duration_ms,
            execution_count=1,  # Aggregated by pattern classifier
            context=context or {}
        )
        
        self.session_events.append(event)
        
        # Write to session telemetry JSONL
        telemetry_file = self.telemetry_dir / f"pattern_execution_{session_id}.jsonl"
        with open(telemetry_file, "a") as f:
            f.write(json.dumps(asdict(event)) + "\n")
        
        return asdict(event)
    
    def classify_unknown_failure(self, error_signature: str, 
                                 error_text: str, 
                                 workflow: str,
                                 session_id: str) -> Optional[str]:
        """Classify unknown failure to best-matching pattern
        
        Uses error signature and text similarity to find best pattern match.
        If confidence > threshold, routes to self-healer.
        
        Args:
            error_signature: Error class/category (e.g., "ImportError", "AssertionError")
            error_text: Full error message
            workflow: Affected workflow file
            session_id: Session for routing
            
        Returns:
            Matched pattern ID (RP-XXX) or None if below confidence threshold
        """
        kg = self.load_knowledge_graph()
        
        # Build error signature hash for pattern matching
        sig_hash = hashlib.md5(f"{error_signature}:{workflow}".encode()).hexdigest()[:8]
        
        best_match = None
        best_score = 0.0
        
        for node in kg.get("nodes", []):
            # Score based on trigger matching
            trigger = node.get("trigger", "").lower()
            error_lower = error_text.lower()
            
            # Simple keyword matching
            match_score = 0.0
            if error_signature in trigger:
                match_score += 0.5
            if any(word in error_lower for word in trigger.split()):
                match_score += 0.3
            
            if match_score > best_score and node.get("confidence", 0) > 0.80:
                best_score = match_score
                best_match = node["id"]
        
        # Record classification to telemetry
        if best_match and best_score > 0.3:
            self.record_pattern_execution(
                pattern_id=best_match,
                status="classified",
                duration_ms=50,
                session_id=session_id,
                phase=4,
                lane=1,
                agent_id="telemetry-classifier-agent",
                context={
                    "error_signature": error_signature,
                    "workflow": workflow,
                    "match_score": best_score
                }
            )
            return best_match
        
        return None
    
    def generate_telemetry_summary(self, session_id: str, phase: int, 
                                   lane: int) -> TelemetrySummary:
        """Generate per-session summary metrics
        
        Args:
            session_id: Session to summarize
            phase: Phase number
            lane: Lane number
            
        Returns:
            TelemetrySummary with aggregated metrics
        """
        successful = sum(1 for e in self.session_events if e.status == "success")
        failed = sum(1 for e in self.session_events if e.status == "failure")
        total_duration = sum(e.duration_ms for e in self.session_events)
        patterns_used = list(set(e.pattern_id for e in self.session_events))
        unknown_classifs = sum(1 for e in self.session_events if e.status == "classified")
        
        summary = TelemetrySummary(
            session_id=session_id,
            timestamp_start=self.session_start,
            timestamp_end=datetime.utcnow().isoformat() + "Z",
            total_patterns_executed=len(self.session_events),
            successful=successful,
            failed=failed,
            avg_duration_ms=int(total_duration / len(self.session_events)) if self.session_events else 0,
            total_overhead_ms=int(total_duration * 0.08),  # ~8% overhead estimate
            patterns_used=patterns_used,
            phase=phase,
            lane=lane,
            unknown_classifications=unknown_classifs
        )
        
        # Write summary
        summary_file = self.telemetry_dir / f"pattern_summary_{session_id}.json"
        with open(summary_file, "w") as f:
            json.dump(asdict(summary), f, indent=2)
        
        return summary
    
    def route_to_self_healer(self, pattern_id: str, context: Dict) -> bool:
        """Queue pattern for autonomous fix attempt in Phase 4
        
        Args:
            pattern_id: RP-XXX pattern to execute
            context: Execution context (workflow, commit, etc.)
            
        Returns:
            True if routed successfully
        """
        routing_file = self.telemetry_dir / f"pattern_routing_queue.jsonl"
        
        route_event = {
            "pattern_id": pattern_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "context": context,
            "status": "queued"
        }
        
        with open(routing_file, "a") as f:
            f.write(json.dumps(route_event) + "\n")
        
        return True


# Phase 4 Integration Example
if __name__ == "__main__":
    # Initialize telemetry
    telemetry = PatternExecutionTelemetry()
    
    # Simulate pattern execution
    telemetry.record_pattern_execution(
        pattern_id="RP-001",
        status="success",
        duration_ms=2345,
        session_id="S348",
        phase=2,
        lane=1,
        agent_id="ci-auto-healer-agent",
        context={"workflow": "codeql-analysis.yml", "commit": "abc1234567"}
    )
    
    # Classify unknown failure
    matched = telemetry.classify_unknown_failure(
        error_signature="ImportError",
        error_text="cannot import name 'foo' from 'bar'",
        workflow="test-suite.yml",
        session_id="S348"
    )
    
    if matched:
        print(f"✅ Classified to {matched}, routed to self-healer")
        telemetry.route_to_self_healer(matched, {"workflow": "test-suite.yml"})
    
    # Generate summary
    summary = telemetry.generate_telemetry_summary("S348", phase=2, lane=1)
    print(f"✅ Telemetry Summary: {summary.total_patterns_executed} patterns, {summary.successful} successful")
