"""
OODA Loop Orchestrator

Centralized orchestrator for the OODA (Observe, Orient, Decide, Act) loop.
This consolidates fragmented decision logic from agents/ into a single,
unified orchestrator within the cognitive_app runtime.

Part of Phase 1: Split Brain Resolution
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import asdict

# Import from cognitive brain base
import sys
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root / "src"))

from cognitive_brain.base import (
    Planner,
    MemoryInterface,
    ObservationData,
    OrientationResult,
    Decision,
    ActionResult,
    PhysicsOfThought,
)

logger = logging.getLogger(__name__)


class OODAOrchestrator:
    """
    Centralized OODA Loop orchestrator.
    
    This class consolidates the OODA loop logic that was previously
    fragmented across multiple agents, providing a single entry point
    for all decision-making processes.
    """
    
    def __init__(self, planner: Planner, memory: MemoryInterface):
        """
        Initialize the OODA orchestrator.
        
        Args:
            planner: Planner implementation for decision-making
            memory: Memory interface for state management
        """
        self.planner = planner
        self.memory = memory
        self.physics_of_thought = PhysicsOfThought(planner, memory)
        self._execution_history: List[Dict[str, Any]] = []
        
        logger.info("OODA Orchestrator initialized")
    
    def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """
        Execute the complete OODA loop with orchestration.
        
        Args:
            input_data: Raw input data to process
            context: Optional additional context
            
        Returns:
            Action result from the execution
        """
        execution_id = f"exec_{datetime.now().isoformat()}"
        start_time = datetime.now()
        
        logger.info(f"Starting OODA execution: {execution_id}")
        
        try:
            # Add context to input if provided
            if context:
                input_data["_context"] = context
            
            # Execute through Physics of Thought engine
            result = self.physics_of_thought.reason(input_data)
            
            # Record execution
            execution_record = {
                "execution_id": execution_id,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "success": result.success,
                "metrics": result.metrics,
            }
            
            self._execution_history.append(execution_record)
            self.memory.store(
                f"execution_{execution_id}",
                execution_record,
                metadata={"type": "execution_record"}
            )
            
            logger.info(
                f"OODA execution complete: {execution_id}, "
                f"success={result.success}, "
                f"duration={execution_record['duration_seconds']:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"OODA execution failed: {execution_id}, error={e}")
            # Return failure result
            return ActionResult(
                success=False,
                output=None,
                metrics={"error_count": 1},
                errors=[str(e)]
            )
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent execution history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        return self._execution_history[-limit:]
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated execution metrics.
        
        Returns:
            Dictionary of metrics including success rate, average duration, etc.
        """
        if not self._execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
            }
        
        total = len(self._execution_history)
        successes = sum(1 for record in self._execution_history if record["success"])
        durations = [record["duration_seconds"] for record in self._execution_history]
        
        return {
            "total_executions": total,
            "success_rate": successes / total if total > 0 else 0.0,
            "average_duration": sum(durations) / len(durations) if durations else 0.0,
            "min_duration": min(durations) if durations else 0.0,
            "max_duration": max(durations) if durations else 0.0,
        }


class CognitiveAppMain:
    """
    Main entry point for the cognitive application.
    
    This serves as the unified runtime that all agents must route through,
    enforcing the "Physics of Thought" and preventing logic duplication.
    """
    
    def __init__(self):
        """Initialize the cognitive application main."""
        self._orchestrator: Optional[OODAOrchestrator] = None
        logger.info("Cognitive App Main initialized")
    
    def initialize(self, planner: Planner, memory: MemoryInterface) -> None:
        """
        Initialize the application with planner and memory.
        
        Args:
            planner: Planner implementation
            memory: Memory interface implementation
        """
        self._orchestrator = OODAOrchestrator(planner, memory)
        logger.info("Cognitive App initialized with orchestrator")
    
    def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """
        Process input through the cognitive architecture.
        
        Args:
            input_data: Input data to process
            context: Optional context
            
        Returns:
            Action result
        """
        if not self._orchestrator:
            raise RuntimeError("Cognitive App not initialized. Call initialize() first.")
        
        return self._orchestrator.execute(input_data, context)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get application metrics.
        
        Returns:
            Dictionary of metrics
        """
        if not self._orchestrator:
            return {}
        
        return self._orchestrator.get_execution_metrics()


# Global instance for easy access
_cognitive_app_instance: Optional[CognitiveAppMain] = None


def get_cognitive_app() -> CognitiveAppMain:
    """
    Get the global cognitive app instance.
    
    Returns:
        Cognitive app instance
    """
    global _cognitive_app_instance
    if _cognitive_app_instance is None:
        _cognitive_app_instance = CognitiveAppMain()
    return _cognitive_app_instance


def initialize_cognitive_app(planner: Planner, memory: MemoryInterface) -> None:
    """
    Initialize the global cognitive app instance.
    
    Args:
        planner: Planner implementation
        memory: Memory interface implementation
    """
    app = get_cognitive_app()
    app.initialize(planner, memory)


def process_through_cognitive_app(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> ActionResult:
    """
    Process input through the cognitive app.
    
    This is the main entry point that all agents should use
    instead of implementing their own decision loops.
    
    Args:
        input_data: Input data to process
        context: Optional context
        
    Returns:
        Action result
    """
    app = get_cognitive_app()
    return app.process(input_data, context)
