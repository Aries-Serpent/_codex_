"""
Secure Bridge Manager for Cognitive-Copilot Communication

Replaces the fragile file-based IPC at temp/bridge_codex_copilot_bridge
with a secure Named Pipe (FIFO) or Unix domain socket implementation.

Part of Phase 2: Fragile Bridge Elimination
Part of PS-02: IPC Bridge Hardening (Authentication & Audit Trail)
"""
from __future__ import annotations

import os
import fcntl
import json
import logging
import socket
import tempfile
import secrets
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime, UTC
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
    auth_token: Optional[str] = None  # Authentication token (PS-02)
    
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
    Secure IPC bridge manager with authentication and audit trail.
    
    Replaces temp/bridge_codex_copilot_bridge with secure Named Pipe
    or Unix domain socket with proper permissions, authentication, and logging.
    
    Security Features (PS-02):
    - Named pipes with 0o600 permissions (owner-only)
    - Authentication token validation (CODEX_BRIDGE_TOKEN)
    - Security audit trail logging
    - File-based locking for race condition prevention
    """
    
    def __init__(
        self,
        bridge_dir: Optional[Path] = None,
        mode: BridgeMode = BridgeMode.NAMED_PIPE,
        owner_only: bool = True,
        require_auth: bool = True,
        audit_file: Optional[Path] = None
    ):
        """
        Initialize bridge manager.
        
        Args:
            bridge_dir: Directory for bridge files (defaults to secure temp location)
            mode: Communication mode (named_pipe or unix_socket)
            owner_only: Restrict permissions to owner only (0o600)
            require_auth: Require authentication token (default: True)
            audit_file: Path to audit log file (default: bridge_dir/audit.log)
        """
        if bridge_dir is None:
            # Use secure temp directory with restricted permissions
            bridge_dir = Path(tempfile.gettempdir()) / "codex_secure_bridge"
        
        self.bridge_dir = Path(bridge_dir)
        self.mode = mode
        self.owner_only = owner_only
        self.require_auth = require_auth
        
        # Get auth token from environment
        self.auth_token = os.getenv("CODEX_BRIDGE_TOKEN")
        if self.require_auth and not self.auth_token:
            logger.warning(
                "CODEX_BRIDGE_TOKEN not set. Authentication disabled. "
                "Set CODEX_BRIDGE_TOKEN for secure operation."
            )
            self.require_auth = False
        
        # Create bridge directory with secure permissions
        self.bridge_dir.mkdir(parents=True, exist_ok=True)
        if owner_only:
            os.chmod(self.bridge_dir, 0o700)  # Owner only: rwx------
        
        # Set up paths
        self.lock_path = self.bridge_dir / "bridge.lock"
        self.pipe_path = self.bridge_dir / "bridge.fifo"
        self.socket_path = self.bridge_dir / "bridge.sock"
        
        # Set up audit logging (PS-02)
        if audit_file is None:
            audit_file = self.bridge_dir / "audit.log"
        self.audit_file = audit_file
        
        # Create audit log with secure permissions
        if not self.audit_file.exists():
            self.audit_file.touch()
            if owner_only:
                os.chmod(self.audit_file, 0o600)
        
        self._audit_log("BRIDGE_INIT", {
            "mode": mode.value,
            "owner_only": owner_only,
            "require_auth": require_auth,
            "bridge_dir": str(bridge_dir)
        })
        
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
    
    def _audit_log(self, event: str, details: Dict[str, Any]) -> None:
        """
        Write security audit log entry (PS-02).
        
        Args:
            event: Event type (e.g., "AUTH_SUCCESS", "AUTH_FAILURE", "MESSAGE_SENT")
            details: Event details dictionary
        """
        try:
            timestamp = datetime.now(UTC).isoformat()
            log_entry = {
                "timestamp": timestamp,
                "event": event,
                "pid": os.getpid(),
                "uid": os.getuid(),
                "details": details
            }
            
            with open(self.audit_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def _verify_auth_token(self, message: ContextMessage) -> bool:
        """
        Verify authentication token (PS-02).
        
        Args:
            message: Message to authenticate
            
        Returns:
            True if authentication passed, False otherwise
        """
        if not self.require_auth:
            return True
        
        if not message.auth_token:
            self._audit_log("AUTH_FAILURE", {
                "reason": "missing_token",
                "source": message.source,
                "message_type": message.message_type
            })
            logger.warning(f"Authentication failed: missing token from {message.source}")
            return False
        
        # Compare tokens using constant-time comparison to prevent timing attacks
        expected_hash = hashlib.sha256(self.auth_token.encode()).hexdigest()
        provided_hash = hashlib.sha256(message.auth_token.encode()).hexdigest()
        
        if not secrets.compare_digest(expected_hash, provided_hash):
            self._audit_log("AUTH_FAILURE", {
                "reason": "invalid_token",
                "source": message.source,
                "message_type": message.message_type
            })
            logger.warning(f"Authentication failed: invalid token from {message.source}")
            return False
        
        self._audit_log("AUTH_SUCCESS", {
            "source": message.source,
            "message_type": message.message_type
        })
        return True
    
    def write_message(self, message: ContextMessage) -> bool:
        """
        Write a message to the bridge with locking and authentication (PS-02).
        
        Args:
            message: Context message to send
            
        Returns:
            True if write successful, False otherwise
        """
        if not message.validate():
            logger.error("Invalid message format")
            self._audit_log("MESSAGE_INVALID", {
                "source": message.source,
                "message_type": message.message_type
            })
            return False
        
        # Verify authentication token (PS-02)
        if not self._verify_auth_token(message):
            return False
        
        try:
            with bridge_lock(self.lock_path):
                if self.mode == BridgeMode.NAMED_PIPE:
                    result = self._write_to_pipe(message)
                elif self.mode == BridgeMode.UNIX_SOCKET:
                    result = self._write_to_socket(message)
                else:
                    result = False
                
                if result:
                    self._audit_log("MESSAGE_SENT", {
                        "source": message.source,
                        "message_type": message.message_type,
                        "mode": self.mode.value
                    })
                
                return result
        
        except TimeoutError as e:
            logger.error(f"Bridge write timeout: {e}")
            self._audit_log("WRITE_TIMEOUT", {
                "error": str(e),
                "source": message.source
            })
            return False
        except Exception as e:
            logger.error(f"Bridge write error: {e}")
            self._audit_log("WRITE_ERROR", {
                "error": str(e),
                "source": message.source
            })
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
        Read a message from the bridge with locking and audit logging (PS-02).
        
        Args:
            timeout: Maximum seconds to wait for message
            
        Returns:
            ContextMessage if read successful, None otherwise
        """
        try:
            with bridge_lock(self.lock_path, timeout=timeout or 5):
                if self.mode == BridgeMode.NAMED_PIPE:
                    message = self._read_from_pipe()
                elif self.mode == BridgeMode.UNIX_SOCKET:
                    message = self._read_from_socket()
                else:
                    message = None
                
                if message:
                    # Verify authentication for received messages (PS-02)
                    if not self._verify_auth_token(message):
                        return None
                    
                    self._audit_log("MESSAGE_RECEIVED", {
                        "source": message.source,
                        "message_type": message.message_type,
                        "mode": self.mode.value
                    })
                    return message
                
                return None
        
        except TimeoutError as e:
            logger.warning(f"Bridge read timeout: {e}")
            self._audit_log("READ_TIMEOUT", {"error": str(e)})
            return None
        except Exception as e:
            logger.error(f"Bridge read error: {e}")
            self._audit_log("READ_ERROR", {"error": str(e)})
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
        """Clean up bridge resources and audit log final state (PS-02)."""
        try:
            self._audit_log("BRIDGE_CLEANUP", {
                "mode": self.mode.value,
                "bridge_dir": str(self.bridge_dir)
            })
            
            if self.mode == BridgeMode.NAMED_PIPE and self.pipe_path.exists():
                self.pipe_path.unlink()
            elif self.mode == BridgeMode.UNIX_SOCKET and self.socket_path.exists():
                self.socket_path.unlink()
            
            if self.lock_path.exists():
                self.lock_path.unlink()
            
            logger.info("Bridge cleaned up")
            
        except Exception as e:
            logger.error(f"Bridge cleanup error: {e}")
            self._audit_log("CLEANUP_ERROR", {"error": str(e)})


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
    
    # Get auth token from environment for authentication (PS-02)
    auth_token = os.getenv("CODEX_BRIDGE_TOKEN")
    
    message = ContextMessage(
        timestamp=datetime.now(UTC).isoformat(),
        source="cognitive_brain",
        message_type="context_update",
        context=context,
        metadata={"version": "1.0"},
        auth_token=auth_token
    )
    
    return bridge.write_message(message)
