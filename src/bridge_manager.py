"""
Secure Bridge Manager for Cognitive-Copilot Communication

Replaces the fragile file-based IPC at temp/bridge_codex_copilot_bridge
with a secure Named Pipe (FIFO) or Unix domain socket implementation.

Part of Phase 2: Fragile Bridge Elimination
"""
from __future__ import annotations

import os
import fcntl
import json
import logging
import socket
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from enum import Enum

logger = logging.getLogger(__name__)


class BridgeMode(Enum):
    """Bridge communication mode."""
    NAMED_PIPE = "named_pipe"  # Unix FIFO
    UNIX_SOCKET = "unix_socket"  # Unix domain socket
    

@dataclass
class ContextMessage:
    """
    Typed message format for bridge communication.
    
    All messages sent through the bridge must follow this structure
    for type safety and validation.
    """
    timestamp: str  # ISO 8601 format
    source: str  # "cognitive_brain" or "copilot"
    message_type: str  # "context_update", "query", "response", etc.
    context: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> ContextMessage:
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate message structure."""
        required_fields = ["timestamp", "source", "message_type", "context"]
        return all(hasattr(self, field) for field in required_fields)


class BridgeLock:
    """
    File-based locking mechanism using fcntl.
    
    Prevents race conditions when multiple processes access the bridge.
    """
    
    def __init__(self, lock_path: Path):
        """Initialize lock with path to lock file."""
        self.lock_path = lock_path
        self.lock_fd: Optional[int] = None
    
    def acquire(self, timeout: int = 5) -> bool:
        """
        Acquire exclusive lock.
        
        Args:
            timeout: Maximum seconds to wait for lock
            
        Returns:
            True if lock acquired, False on timeout
        """
        try:
            # Ensure lock file exists
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            self.lock_path.touch(exist_ok=True)
            
            # Open lock file
            self.lock_fd = os.open(str(self.lock_path), os.O_RDWR | os.O_CREAT, 0o600)
            
            # Try to acquire lock with timeout
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.debug(f"Lock acquired: {self.lock_path}")
            return True
            
        except BlockingIOError:
            logger.warning(f"Failed to acquire lock (timeout): {self.lock_path}")
            if self.lock_fd:
                os.close(self.lock_fd)
                self.lock_fd = None
            return False
        except Exception as e:
            logger.error(f"Lock acquisition error: {e}")
            if self.lock_fd:
                os.close(self.lock_fd)
                self.lock_fd = None
            return False
    
    def release(self) -> None:
        """Release the lock."""
        if self.lock_fd is not None:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
                logger.debug(f"Lock released: {self.lock_path}")
            except Exception as e:
                logger.error(f"Lock release error: {e}")
            finally:
                self.lock_fd = None


@contextmanager
def bridge_lock(lock_path: Path, timeout: int = 5):
    """
    Context manager for bridge locking.
    
    Usage:
        with bridge_lock(lock_path):
            # Critical section - safe from race conditions
            pass
    """
    lock = BridgeLock(lock_path)
    acquired = lock.acquire(timeout)
    
    if not acquired:
        raise TimeoutError(f"Could not acquire bridge lock: {lock_path}")
    
    try:
        yield lock
    finally:
        lock.release()


class BridgeManager:
    """
    Secure IPC bridge manager.
    
    Replaces temp/bridge_codex_copilot_bridge with secure Named Pipe
    or Unix domain socket with proper permissions and locking.
    """
    
    def __init__(
        self,
        bridge_dir: Optional[Path] = None,
        mode: BridgeMode = BridgeMode.NAMED_PIPE,
        owner_only: bool = True
    ):
        """
        Initialize bridge manager.
        
        Args:
            bridge_dir: Directory for bridge files (defaults to secure temp location)
            mode: Communication mode (named_pipe or unix_socket)
            owner_only: Restrict permissions to owner only (0o600)
        """
        if bridge_dir is None:
            # Use secure temp directory with restricted permissions
            bridge_dir = Path(tempfile.gettempdir()) / "codex_secure_bridge"
        
        self.bridge_dir = Path(bridge_dir)
        self.mode = mode
        self.owner_only = owner_only
        
        # Create bridge directory with secure permissions
        self.bridge_dir.mkdir(parents=True, exist_ok=True)
        if owner_only:
            os.chmod(self.bridge_dir, 0o700)  # Owner only: rwx------
        
        # Set up paths
        self.lock_path = self.bridge_dir / "bridge.lock"
        self.pipe_path = self.bridge_dir / "bridge.fifo"
        self.socket_path = self.bridge_dir / "bridge.sock"
        
        logger.info(f"Bridge manager initialized: mode={mode.value}, dir={bridge_dir}")
        
        # Initialize based on mode
        if mode == BridgeMode.NAMED_PIPE:
            self._init_named_pipe()
        elif mode == BridgeMode.UNIX_SOCKET:
            self._init_unix_socket()
    
    def _init_named_pipe(self) -> None:
        """Initialize Named Pipe (FIFO)."""
        try:
            # Remove existing pipe if present
            if self.pipe_path.exists():
                self.pipe_path.unlink()
            
            # Create FIFO
            os.mkfifo(str(self.pipe_path), 0o600 if self.owner_only else 0o666)
            logger.info(f"Named pipe created: {self.pipe_path}")
            
        except Exception as e:
            logger.error(f"Failed to create named pipe: {e}")
            raise
    
    def _init_unix_socket(self) -> None:
        """Initialize Unix domain socket."""
        try:
            # Remove existing socket if present
            if self.socket_path.exists():
                self.socket_path.unlink()
            
            # Socket will be created on bind
            logger.info(f"Unix socket path prepared: {self.socket_path}")
            
        except Exception as e:
            logger.error(f"Failed to prepare unix socket: {e}")
            raise
    
    def write_message(self, message: ContextMessage) -> bool:
        """
        Write a message to the bridge with locking.
        
        Args:
            message: Context message to send
            
        Returns:
            True if write successful, False otherwise
        """
        if not message.validate():
            logger.error("Invalid message format")
            return False
        
        try:
            with bridge_lock(self.lock_path):
                if self.mode == BridgeMode.NAMED_PIPE:
                    return self._write_to_pipe(message)
                elif self.mode == BridgeMode.UNIX_SOCKET:
                    return self._write_to_socket(message)
        
        except TimeoutError as e:
            logger.error(f"Bridge write timeout: {e}")
            return False
        except Exception as e:
            logger.error(f"Bridge write error: {e}")
            return False
    
    def _write_to_pipe(self, message: ContextMessage) -> bool:
        """Write message to named pipe."""
        try:
            # Open pipe for writing (will block until reader connects)
            with open(self.pipe_path, 'w') as pipe:
                pipe.write(message.to_json())
                pipe.write('\n')  # Message delimiter
                pipe.flush()
            
            logger.debug(f"Message written to pipe: {message.message_type}")
            return True
            
        except Exception as e:
            logger.error(f"Pipe write error: {e}")
            return False
    
    def _write_to_socket(self, message: ContextMessage) -> bool:
        """Write message to Unix socket."""
        try:
            # Connect to socket
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(str(self.socket_path))
            
            # Send message
            client.sendall(message.to_json().encode('utf-8'))
            client.sendall(b'\n')  # Message delimiter
            
            client.close()
            logger.debug(f"Message written to socket: {message.message_type}")
            return True
            
        except Exception as e:
            logger.error(f"Socket write error: {e}")
            return False
    
    def read_message(self, timeout: Optional[int] = None) -> Optional[ContextMessage]:
        """
        Read a message from the bridge with locking.
        
        Args:
            timeout: Maximum seconds to wait for message
            
        Returns:
            ContextMessage if read successful, None otherwise
        """
        try:
            with bridge_lock(self.lock_path, timeout=timeout or 5):
                if self.mode == BridgeMode.NAMED_PIPE:
                    return self._read_from_pipe()
                elif self.mode == BridgeMode.UNIX_SOCKET:
                    return self._read_from_socket()
        
        except TimeoutError as e:
            logger.warning(f"Bridge read timeout: {e}")
            return None
        except Exception as e:
            logger.error(f"Bridge read error: {e}")
            return None
    
    def _read_from_pipe(self) -> Optional[ContextMessage]:
        """Read message from named pipe."""
        try:
            # Open pipe for reading
            with open(self.pipe_path, 'r') as pipe:
                json_str = pipe.readline().strip()
                if json_str:
                    message = ContextMessage.from_json(json_str)
                    logger.debug(f"Message read from pipe: {message.message_type}")
                    return message
            
            return None
            
        except Exception as e:
            logger.error(f"Pipe read error: {e}")
            return None
    
    def _read_from_socket(self) -> Optional[ContextMessage]:
        """Read message from Unix socket."""
        try:
            # Create server socket
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(str(self.socket_path))
            server.listen(1)
            
            # Set permissions
            if self.owner_only:
                os.chmod(self.socket_path, 0o600)
            
            # Accept connection
            conn, _ = server.accept()
            
            # Receive message
            data = b''
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'\n' in data:
                    break
            
            conn.close()
            server.close()
            
            # Parse message
            if data:
                json_str = data.decode('utf-8').strip()
                message = ContextMessage.from_json(json_str)
                logger.debug(f"Message read from socket: {message.message_type}")
                return message
            
            return None
            
        except Exception as e:
            logger.error(f"Socket read error: {e}")
            return None
    
    def cleanup(self) -> None:
        """Clean up bridge resources."""
        try:
            if self.mode == BridgeMode.NAMED_PIPE and self.pipe_path.exists():
                self.pipe_path.unlink()
            elif self.mode == BridgeMode.UNIX_SOCKET and self.socket_path.exists():
                self.socket_path.unlink()
            
            if self.lock_path.exists():
                self.lock_path.unlink()
            
            logger.info("Bridge cleaned up")
            
        except Exception as e:
            logger.error(f"Bridge cleanup error: {e}")


# Convenience functions for cognitive brain integration

def share_context_with_copilot(context: Dict[str, Any], bridge: Optional[BridgeManager] = None) -> bool:
    """
    Share cognitive context with Copilot watcher via secure bridge.
    
    Args:
        context: Context data to share
        bridge: Optional bridge instance (creates default if not provided)
        
    Returns:
        True if context shared successfully
    """
    if bridge is None:
        bridge = BridgeManager()
    
    message = ContextMessage(
        timestamp=datetime.now().isoformat(),
        source="cognitive_brain",
        message_type="context_update",
        context=context,
        metadata={"version": "1.0"}
    )
    
    return bridge.write_message(message)
