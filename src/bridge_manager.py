"""
Secure Bridge Manager for Cognitive-Copilot Communication

Replaces the fragile file-based IPC at temp/bridge_codex_copilot_bridge
with a secure Named Pipe (FIFO) or Unix domain socket implementation.

Part of Phase 2: Fragile Bridge Elimination
Part of PS-02: IPC Bridge Hardening (Authentication & Audit Trail)

Enhanced with Bridge Protocol v2 (2026-01-09):
- Message compression for large payloads
- Multi-client support
- Protocol headers with integrity verification
"""
from __future__ import annotations

import os
import fcntl
import json
import logging
import socket
import tempfile
import secrets
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime, UTC
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from enum import Enum

# Import Bridge Protocol v2 for enhanced features
try:
    from bridge_protocol_v2 import (
        encode_message as v2_encode,
        decode_message as v2_decode,
        MultiClientBridge,
        MessageFlags,
        PROTOCOL_VERSION,
    )
    HAS_PROTOCOL_V2 = True
except ImportError:
    HAS_PROTOCOL_V2 = False

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
    
    Protocol v2 Features (PS-02 Enhancement):
    - Message compression for payloads >100KB
    - Multi-client support with routing
    - CRC32 integrity verification
    """
    
    def __init__(
        self,
        bridge_dir: Optional[Path] = None,
        mode: BridgeMode = BridgeMode.NAMED_PIPE,
        owner_only: bool = True,
        require_auth: bool = True,
        audit_file: Optional[Path] = None,
        use_protocol_v2: bool = True,
        enable_compression: bool = True,
        max_clients: int = 10,
    ):
        """
        Initialize bridge manager.
        
        Args:
            bridge_dir: Directory for bridge files (defaults to secure temp location)
            mode: Communication mode (named_pipe or unix_socket)
            owner_only: Restrict permissions to owner only (0o600)
            require_auth: Require authentication token (default: True)
            audit_file: Path to audit log file (default: bridge_dir/audit.log)
            use_protocol_v2: Enable Protocol v2 with compression (default: True)
            enable_compression: Enable payload compression (default: True)
            max_clients: Maximum concurrent clients for multi-client mode
        """
        if bridge_dir is None:
            # Use secure temp directory with restricted permissions
            bridge_dir = Path(tempfile.gettempdir()) / "codex_secure_bridge"
        
        self.bridge_dir = Path(bridge_dir)
        self.mode = mode
        self.owner_only = owner_only
        self.require_auth = require_auth
        
        # Protocol v2 settings
        self.use_protocol_v2 = use_protocol_v2 and HAS_PROTOCOL_V2
        self.enable_compression = enable_compression
        
        # Multi-client bridge (v2 feature)
        self._multi_client_bridge: Optional[MultiClientBridge] = None
        if self.use_protocol_v2:
            self._multi_client_bridge = MultiClientBridge(max_clients=max_clients)
            logger.info(f"Bridge Protocol v2 enabled (compression={enable_compression})")
        
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
        
        # Compare tokens directly using constant-time comparison to prevent timing attacks
        # Note: secrets.compare_digest requires same-length inputs for security
        if not secrets.compare_digest(self.auth_token, message.auth_token):
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
        """Write message to named pipe with optional v2 protocol."""
        try:
            payload = message.to_json().encode('utf-8')
            
            # Use Protocol v2 with compression if enabled
            if self.use_protocol_v2 and HAS_PROTOCOL_V2:
                payload = v2_encode(payload, compress=self.enable_compression)
                logger.debug(f"Using Protocol v2 (compressed={self.enable_compression})")
            
            # Open pipe for writing (will block until reader connects)
            with open(self.pipe_path, 'wb') as pipe:
                pipe.write(payload)
                if not self.use_protocol_v2:
                    pipe.write(b'\n')  # Message delimiter for v1
                pipe.flush()
            
            logger.debug(f"Message written to pipe: {message.message_type}")
            return True
            
        except Exception as e:
            logger.error(f"Pipe write error: {e}")
            return False
    
    def _write_to_socket(self, message: ContextMessage) -> bool:
        """Write message to Unix socket with optional v2 protocol."""
        try:
            payload = message.to_json().encode('utf-8')
            
            # Use Protocol v2 with compression if enabled
            if self.use_protocol_v2 and HAS_PROTOCOL_V2:
                payload = v2_encode(payload, compress=self.enable_compression)
            
            # Connect to socket
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(str(self.socket_path))
            
            # Send message
            client.sendall(payload)
            if not self.use_protocol_v2:
                client.sendall(b'\n')  # Message delimiter for v1
            
            client.close()
            logger.debug(f"Message written to socket: {message.message_type}")
            return True
            
        except Exception as e:
            logger.error(f"Socket write error: {e}")
            return False
    
    # ==================== Protocol v2 Methods ====================
    
    def register_client(self, client_id: str, socket_path: str, priority: int = 0) -> bool:
        """
        Register a client for multi-client bridge support (Protocol v2).
        
        Args:
            client_id: Unique client identifier
            socket_path: Path to client's socket
            priority: Client priority (higher = more important)
            
        Returns:
            True if registered successfully
        """
        if not self.use_protocol_v2 or not self._multi_client_bridge:
            logger.warning("Multi-client not available (Protocol v2 not enabled)")
            return False
        
        result = self._multi_client_bridge.register_client(client_id, socket_path, priority)
        if result:
            self._audit_log("CLIENT_REGISTERED", {
                "client_id": client_id,
                "priority": priority,
            })
        return result
    
    def unregister_client(self, client_id: str) -> bool:
        """Unregister a client from the multi-client bridge."""
        if not self.use_protocol_v2 or not self._multi_client_bridge:
            return False
        
        result = self._multi_client_bridge.unregister_client(client_id)
        if result:
            self._audit_log("CLIENT_UNREGISTERED", {"client_id": client_id})
        return result
    
    def get_bridge_stats(self) -> Dict[str, Any]:
        """Get bridge statistics including multi-client info."""
        stats = {
            "mode": self.mode.value,
            "protocol_v2": self.use_protocol_v2,
            "compression_enabled": self.enable_compression,
            "auth_required": self.require_auth,
        }
        
        if self.use_protocol_v2 and self._multi_client_bridge:
            stats["multi_client"] = self._multi_client_bridge.get_stats()
        
        return stats
    
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
        """Read message from named pipe with optional v2 protocol."""
        try:
            # Open pipe for reading
            with open(self.pipe_path, 'rb') as pipe:
                data = pipe.read()
                if not data:
                    return None
                
                # Decode using Protocol v2 if enabled and data has v2 header
                if self.use_protocol_v2 and HAS_PROTOCOL_V2 and data[:4] == b"CBv2":
                    payload, header = v2_decode(data)
                    json_str = payload.decode('utf-8')
                    logger.debug(f"Read v2 message (compressed={bool(header.flags & 1)})")
                else:
                    # Legacy v1 format
                    json_str = data.decode('utf-8').strip()
                
                if json_str:
                    message = ContextMessage.from_json(json_str)
                    logger.debug(f"Message read from pipe: {message.message_type}")
                    return message
            
            return None
            
        except Exception as e:
            logger.error(f"Pipe read error: {e}")
            return None
    
    def _read_from_socket(self) -> Optional[ContextMessage]:
        """Read message from Unix socket with optional v2 protocol."""
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
                # For v2 protocol, read based on header length
                if self.use_protocol_v2 and HAS_PROTOCOL_V2 and len(data) >= 14:
                    if data[:4] == b"CBv2":
                        # Extract length from header bytes 6-10
                        payload_len = int.from_bytes(data[6:10], "big")
                        if len(data) >= 14 + payload_len:
                            break
                elif b'\n' in data:
                    break
            
            conn.close()
            server.close()
            
            # Parse message with v2 protocol support
            if data:
                if self.use_protocol_v2 and HAS_PROTOCOL_V2 and data[:4] == b"CBv2":
                    payload, header = v2_decode(data)
                    json_str = payload.decode('utf-8')
                else:
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
