"""MCP service lifecycle management module."""
from typing import Optional, Dict, Any, Callable
from enum import Enum

class LifecycleStatus(str, Enum):
    """MCP lifecycle status enumeration."""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"

class MCPLifecycleManager:
    """Manages the lifecycle of MCP services."""
    
    def __init__(self):
        """Initialize the lifecycle manager."""
        self.status = LifecycleStatus.INITIALIZING
        self._hooks: Dict[str, list] = {
            "on_start": [],
            "on_ready": [],
            "on_stop": [],
        }
    
    def add_hook(self, event: str, callback: Callable) -> None:
        """Register a lifecycle hook."""
        if event in self._hooks:
            self._hooks[event].append(callback)
    
    def start(self) -> None:
        """Start the MCP service."""
        self.status = LifecycleStatus.RUNNING
        for callback in self._hooks["on_start"]:
            callback()
    
    def stop(self) -> None:
        """Stop the MCP service."""
        self.status = LifecycleStatus.STOPPED
        for callback in self._hooks["on_stop"]:
            callback()

__all__ = ["MCPLifecycleManager", "LifecycleStatus"]
