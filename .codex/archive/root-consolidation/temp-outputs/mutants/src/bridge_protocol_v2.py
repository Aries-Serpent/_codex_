"""Bridge Protocol v2 Enhancements.

PS-02 Enhancement: Implements advanced bridge features:
- Message compression for large payloads (zlib)
- Multi-client support with client registry
- Protocol versioning for backward compatibility

This module extends the IPC Bridge Hardening planset with
enterprise-grade communication capabilities.
"""

from __future__ import annotations

import logging
import threading
import time
import zlib
from dataclasses import dataclass, field
from enum import IntFlag
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Protocol Constants
PROTOCOL_VERSION = 2
MAGIC_BYTES = b"CBv2"  # Codex Bridge v2
COMPRESSION_THRESHOLD = 100 * 1024  # 100KB - compress if larger
MIN_COMPRESSION_SAVINGS = 0.1  # Only compress if 10%+ savings


class MessageFlags(IntFlag):
    """Message flag bits for protocol header."""

    NONE = 0
    COMPRESSED = 1 << 0  # Payload is zlib compressed
    ENCRYPTED = 1 << 1  # Payload is encrypted (reserved)
    FRAGMENTED = 1 << 2  # Message is fragmented (reserved)
    PRIORITY = 1 << 3  # High priority message
    ACK_REQUIRED = 1 << 4  # Acknowledgment required
    BROADCAST = 1 << 5  # Send to all clients


@dataclass
class ProtocolHeader:
    """Bridge Protocol v2 header structure.

    Wire format:
    | Magic (4B) | Version (1B) | Flags (1B) | Length (4B) | Checksum (4B) |
    Total: 14 bytes
    """

    magic: bytes = MAGIC_BYTES
    version: int = PROTOCOL_VERSION
    flags: MessageFlags = MessageFlags.NONE
    length: int = 0
    checksum: int = 0

    def to_bytes(self) -> bytes:
        """Serialize header to bytes."""
        return (
            self.magic
            + self.version.to_bytes(1, "big")
            + int(self.flags).to_bytes(1, "big")
            + self.length.to_bytes(4, "big")
            + self.checksum.to_bytes(4, "big")
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> ProtocolHeader:
        """Deserialize header from bytes."""
        if len(data) < 14:
            raise ValueError(f"Header too short: {len(data)} bytes")

        magic = data[0:4]
        if magic != MAGIC_BYTES:
            raise ValueError(f"Invalid magic bytes: {magic!r}")

        return cls(
            magic=magic,
            version=data[4],
            flags=MessageFlags(data[5]),
            length=int.from_bytes(data[6:10], "big"),
            checksum=int.from_bytes(data[10:14], "big"),
        )

    @staticmethod
    def size() -> int:
        """Return header size in bytes."""
        return 14


def compress_message(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.

    Args:
        data: Raw message data
        threshold: Minimum size to consider compression

    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, False

    compressed = zlib.compress(data, level=6)

    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes ({savings:.1%} savings)"
        )
        return compressed, True

    return data, False


def decompress_message(data: bytes, is_compressed: bool) -> bytes:
    """Decompress message if it was compressed.

    Args:
        data: Message data (possibly compressed)
        is_compressed: Whether data is compressed

    Returns:
        Decompressed data
    """
    if not is_compressed:
        return data

    return zlib.decompress(data)


def compute_checksum(data: bytes) -> int:
    """Compute CRC32 checksum for message integrity.

    Args:
        data: Message data

    Returns:
        32-bit checksum
    """
    return zlib.crc32(data) & 0xFFFFFFFF


@dataclass
class ClientInfo:
    """Information about a connected client."""

    client_id: str
    socket_path: str
    priority: int = 0
    connected_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    message_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0

    def update_heartbeat(self) -> None:
        """Update last heartbeat timestamp."""
        self.last_heartbeat = time.time()

    def is_alive(self, timeout: float = 60.0) -> bool:
        """Check if client is still alive based on heartbeat."""
        return (time.time() - self.last_heartbeat) < timeout

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "client_id": self.client_id,
            "socket_path": self.socket_path,
            "priority": self.priority,
            "connected_at": self.connected_at,
            "last_heartbeat": self.last_heartbeat,
            "message_count": self.message_count,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "is_alive": self.is_alive(),
        }


class MultiClientBridge:
    """Bridge manager with multi-client support.

    Features:
    - Client registration and lifecycle management
    - Priority-based message routing
    - Round-robin load balancing
    - Client health monitoring
    """

    def __init__(
        self,
        max_clients: int = 10,
        heartbeat_timeout: float = 60.0,
        cleanup_interval: float = 30.0,
    ):
        """Initialize multi-client bridge.

        Args:
            max_clients: Maximum number of concurrent clients
            heartbeat_timeout: Seconds before client considered dead
            cleanup_interval: Seconds between dead client cleanup
        """
        self.max_clients = max_clients
        self.heartbeat_timeout = heartbeat_timeout
        self.cleanup_interval = cleanup_interval

        self.clients: dict[str, ClientInfo] = {}
        self._lock = threading.RLock()
        self._round_robin_index = 0
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False

    def start(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")

    def stop(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info("MultiClientBridge stopped")

    def register_client(
        self,
        client_id: str,
        socket_path: str,
        priority: int = 0,
    ) -> bool:
        """Register a new client.

        Args:
            client_id: Unique client identifier
            socket_path: Path to client's socket
            priority: Client priority (higher = more important)

        Returns:
            True if registered, False if at capacity
        """
        with self._lock:
            if len(self.clients) >= self.max_clients:
                logger.warning(
                    f"Cannot register client {client_id}: at capacity ({self.max_clients} clients)"
                )
                return False

            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")

            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                socket_path=socket_path,
                priority=priority,
            )

            logger.info(
                f"Registered client {client_id} (priority={priority}, total={len(self.clients)})"
            )
            return True

    def unregister_client(self, client_id: str) -> bool:
        """Unregister a client.

        Args:
            client_id: Client to unregister

        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if client_id not in self.clients:
                return False

            del self.clients[client_id]
            logger.info(f"Unregistered client {client_id} (total={len(self.clients)})")
            return True

    def heartbeat(self, client_id: str) -> bool:
        """Update client heartbeat.

        Args:
            client_id: Client sending heartbeat

        Returns:
            True if client found, False otherwise
        """
        with self._lock:
            if client_id not in self.clients:
                return False

            self.clients[client_id].update_heartbeat()
            return True

    def get_client(self, client_id: str) -> Optional[ClientInfo]:
        """Get client info by ID.

        Args:
            client_id: Client to look up

        Returns:
            ClientInfo if found, None otherwise
        """
        with self._lock:
            return self.clients.get(client_id)

    def route_by_priority(self) -> Optional[str]:
        """Get socket path for highest priority alive client.

        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [c for c in self.clients.values() if c.is_alive(self.heartbeat_timeout)]

            if not alive_clients:
                return None

            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=True,
            )

            return sorted_clients[0].socket_path

    def route_round_robin(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.

        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [c for c in self.clients.values() if c.is_alive(self.heartbeat_timeout)]

            if not alive_clients:
                return None

            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 1

            return client.socket_path

    def broadcast_targets(self) -> list[str]:
        """Get socket paths for all alive clients (for broadcast).

        Returns:
            List of socket paths
        """
        with self._lock:
            return [
                c.socket_path for c in self.clients.values() if c.is_alive(self.heartbeat_timeout)
            ]

    def get_stats(self) -> dict[str, Any]:
        """Get bridge statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values() if c.is_alive(self.heartbeat_timeout)
            )

            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }

    def _cleanup_loop(self) -> None:
        """Background thread to clean up dead clients."""
        while self._running:
            time.sleep(self.cleanup_interval)
            self._cleanup_dead_clients()

    def _cleanup_dead_clients(self) -> None:
        """Remove clients that haven't sent heartbeat."""
        with self._lock:
            dead_clients = [
                client_id
                for client_id, client in self.clients.items()
                if not client.is_alive(self.heartbeat_timeout)
            ]

            for client_id in dead_clients:
                del self.clients[client_id]
                logger.info(f"Cleaned up dead client: {client_id}")

            if dead_clients:
                logger.info(
                    f"Cleaned up {len(dead_clients)} dead clients, {len(self.clients)} remaining"
                )


def encode_message(
    payload: bytes,
    flags: MessageFlags = MessageFlags.NONE,
    compress: bool = True,
) -> bytes:
    """Encode a message with protocol v2 header.

    Args:
        payload: Message payload
        flags: Message flags
        compress: Whether to attempt compression

    Returns:
        Encoded message with header
    """
    # Compress if enabled and beneficial
    if compress:
        payload, was_compressed = compress_message(payload)
        if was_compressed:
            flags |= MessageFlags.COMPRESSED

    # Compute checksum
    checksum = compute_checksum(payload)

    # Create header
    header = ProtocolHeader(
        flags=flags,
        length=len(payload),
        checksum=checksum,
    )

    return header.to_bytes() + payload


def decode_message(data: bytes) -> tuple[bytes, ProtocolHeader]:
    """Decode a protocol v2 message.

    Args:
        data: Raw message data

    Returns:
        Tuple of (payload, header)

    Raises:
        ValueError: If message is invalid or corrupted
    """
    if len(data) < ProtocolHeader.size():
        raise ValueError(f"Message too short: {len(data)} bytes")

    # Parse header
    header = ProtocolHeader.from_bytes(data[: ProtocolHeader.size()])

    # Extract payload
    payload = data[ProtocolHeader.size() : ProtocolHeader.size() + header.length]

    if len(payload) != header.length:
        raise ValueError(f"Payload length mismatch: expected {header.length}, got {len(payload)}")

    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, got {computed_checksum:08x}"
        )

    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)

    return payload, header


__all__ = [
    "COMPRESSION_THRESHOLD",
    "MIN_COMPRESSION_SAVINGS",
    "PROTOCOL_VERSION",
    "ClientInfo",
    "MessageFlags",
    "MultiClientBridge",
    "ProtocolHeader",
    "compress_message",
    "compute_checksum",
    "decode_message",
    "decompress_message",
    "encode_message",
]
