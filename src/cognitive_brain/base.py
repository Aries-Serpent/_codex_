"""
Cognitive Brain Base Classes

Abstract Base Classes for the cognitive architecture that enforce
a unified interface for agents and decision-making components.

Part of Phase 1: Split Brain Resolution
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ObservationData:
    """Data from the Observe step of OODA loop."""
    
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OrientationResult:
    """Result from the Orient step of OODA loop."""
    
    context: Dict[str, Any]
    analysis: str
    confidence: float
    alternatives: List[Dict[str, Any]]


@dataclass
class Decision:
    """Decision from the Decide step of OODA loop."""
    
    action: str
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float
    timestamp: datetime


@dataclass
class ActionResult:
    """Result from the Act step of OODA loop."""
    
    success: bool
    output: Any
    metrics: Dict[str, float]
    errors: List[str]


class Planner(ABC):
    """
    Abstract base class for planning and decision-making components.
    
    Implements the OODA (Observe, Orient, Decide, Act) loop interface
    that all agents must follow to ensure unified decision-making.
    """
    
    @abstractmethod
    def observe(self, input_data: Dict[str, Any]) -> ObservationData:
        """
        Observe: Gather and structure raw input data.
        
        Args:
            input_data: Raw input data from various sources
            
        Returns:
            Structured observation data
        """
        pass
    
    @abstractmethod
    def orient(self, observation: ObservationData) -> OrientationResult:
        """
        Orient: Analyze observation in context, identify patterns.
        
        Args:
            observation: Structured observation data
            
        Returns:
            Orientation result with context and analysis
        """
        pass
    
    @abstractmethod
    def decide(self, orientation: OrientationResult) -> Decision:
        """
        Decide: Make decision based on orientation.
        
        Args:
            orientation: Orientation result
            
        Returns:
            Decision with action and reasoning
        """
        pass
    
    @abstractmethod
    def act(self, decision: Decision) -> ActionResult:
        """
        Act: Execute the decision and return results.
        
        Args:
            decision: Decision to execute
            
        Returns:
            Action result with success status and metrics
        """
        pass
    
    def ooda_loop(self, input_data: Dict[str, Any]) -> ActionResult:
        """
        Execute complete OODA loop: Observe -> Orient -> Decide -> Act.
        
        This is the main entry point for agent execution.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Action result from the Act step
        """
        observation = self.observe(input_data)
        orientation = self.orient(observation)
        decision = self.decide(orientation)
        result = self.act(decision)
        return result


class MemoryInterface(ABC):
    """
    Abstract base class for memory and state management.
    
    Provides unified interface for storing and retrieving agent
    memory, context, and historical data.
    """
    
    @abstractmethod
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a value in memory.
        
        Args:
            key: Unique identifier for the stored value
            value: Value to store (can be any serializable type)
            metadata: Optional metadata about the stored value
            
        Returns:
            True if storage was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory.
        
        Args:
            key: Unique identifier for the value
            
        Returns:
            Stored value if found, None otherwise
        """
        pass
    
    @abstractmethod
    def search(self, query: Dict[str, Any], limit: int = 10) -> List[tuple[str, Any]]:
        """
        Search memory based on query criteria.
        
        Args:
            query: Search criteria as key-value pairs
            limit: Maximum number of results to return
            
        Returns:
            List of (key, value) tuples matching the query
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a value from memory.
        
        Args:
            key: Unique identifier for the value to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all memory.
        
        Returns:
            True if clear was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_history(self, key: str, limit: int = 10) -> List[tuple[datetime, Any]]:
        """
        Get historical versions of a value.
        
        Args:
            key: Unique identifier for the value
            limit: Maximum number of historical versions to return
            
        Returns:
            List of (timestamp, value) tuples in reverse chronological order
        """
        pass


class PhysicsOfThought:
    """
    Unified "Physics of Thought" engine that enforces consistent
    reasoning patterns across all agents.
    
    This prevents logic duplication and ensures all agents follow
    the same fundamental reasoning principles.
    """
    
    def __init__(self, planner: Planner, memory: MemoryInterface):
        """
        Initialize the Physics of Thought engine.
        
        Args:
            planner: Planner instance for decision-making
            memory: Memory interface for state management
        """
        self.planner = planner
        self.memory = memory
    
    def reason(self, input_data: Dict[str, Any]) -> ActionResult:
        """
        Execute unified reasoning process.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Action result from reasoning
        """
        # Store input in memory
        self.memory.store(
            f"input_{datetime.now().isoformat()}",
            input_data,
            metadata={"type": "input", "timestamp": datetime.now().isoformat()}
        )
        
        # Execute OODA loop
        result = self.planner.ooda_loop(input_data)
        
        # Store result in memory
        self.memory.store(
            f"result_{datetime.now().isoformat()}",
            result,
            metadata={"type": "result", "timestamp": datetime.now().isoformat()}
        )
        
        return result
