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
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
            self.magic +
            self.version.to_bytes(1, "big") +
            int(self.flags).to_bytes(1, "big") +
            self.length.to_bytes(4, "big") +
            self.checksum.to_bytes(4, "big")
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


def x_compress_message__mutmut_orig(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_1(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) <= threshold:
        return data, False
    
    compressed = zlib.compress(data, level=6)
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_2(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, True
    
    compressed = zlib.compress(data, level=6)
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_3(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, False
    
    compressed = None
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_4(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, False
    
    compressed = zlib.compress(None, level=6)
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_5(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, False
    
    compressed = zlib.compress(data, level=None)
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_6(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, False
    
    compressed = zlib.compress(level=6)
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_7(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, False
    
    compressed = zlib.compress(data, )
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_8(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
    """Compress message if above threshold and compression is beneficial.
    
    Args:
        data: Raw message data
        threshold: Minimum size to consider compression
        
    Returns:
        Tuple of (output_data, was_compressed)
    """
    if len(data) < threshold:
        return data, False
    
    compressed = zlib.compress(data, level=7)
    
    # Only use compression if we save at least MIN_COMPRESSION_SAVINGS
    savings = 1.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_9(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
    savings = None
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_10(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
    savings = 1.0 + (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_11(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
    savings = 2.0 - (len(compressed) / len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_12(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
    savings = 1.0 - (len(compressed) * len(data))
    if savings >= MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_13(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
    if savings > MIN_COMPRESSION_SAVINGS:
        logger.debug(
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_14(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
            None
        )
        return compressed, True
    
    return data, False


def x_compress_message__mutmut_15(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, False
    
    return data, False


def x_compress_message__mutmut_16(data: bytes, threshold: int = COMPRESSION_THRESHOLD) -> tuple[bytes, bool]:
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
            f"Compressed message: {len(data)} -> {len(compressed)} bytes "
            f"({savings:.1%} savings)"
        )
        return compressed, True
    
    return data, True

x_compress_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_compress_message__mutmut_1': x_compress_message__mutmut_1, 
    'x_compress_message__mutmut_2': x_compress_message__mutmut_2, 
    'x_compress_message__mutmut_3': x_compress_message__mutmut_3, 
    'x_compress_message__mutmut_4': x_compress_message__mutmut_4, 
    'x_compress_message__mutmut_5': x_compress_message__mutmut_5, 
    'x_compress_message__mutmut_6': x_compress_message__mutmut_6, 
    'x_compress_message__mutmut_7': x_compress_message__mutmut_7, 
    'x_compress_message__mutmut_8': x_compress_message__mutmut_8, 
    'x_compress_message__mutmut_9': x_compress_message__mutmut_9, 
    'x_compress_message__mutmut_10': x_compress_message__mutmut_10, 
    'x_compress_message__mutmut_11': x_compress_message__mutmut_11, 
    'x_compress_message__mutmut_12': x_compress_message__mutmut_12, 
    'x_compress_message__mutmut_13': x_compress_message__mutmut_13, 
    'x_compress_message__mutmut_14': x_compress_message__mutmut_14, 
    'x_compress_message__mutmut_15': x_compress_message__mutmut_15, 
    'x_compress_message__mutmut_16': x_compress_message__mutmut_16
}

def compress_message(*args, **kwargs):
    result = _mutmut_trampoline(x_compress_message__mutmut_orig, x_compress_message__mutmut_mutants, args, kwargs)
    return result 

compress_message.__signature__ = _mutmut_signature(x_compress_message__mutmut_orig)
x_compress_message__mutmut_orig.__name__ = 'x_compress_message'


def x_decompress_message__mutmut_orig(data: bytes, is_compressed: bool) -> bytes:
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


def x_decompress_message__mutmut_1(data: bytes, is_compressed: bool) -> bytes:
    """Decompress message if it was compressed.
    
    Args:
        data: Message data (possibly compressed)
        is_compressed: Whether data is compressed
        
    Returns:
        Decompressed data
    """
    if is_compressed:
        return data
    
    return zlib.decompress(data)


def x_decompress_message__mutmut_2(data: bytes, is_compressed: bool) -> bytes:
    """Decompress message if it was compressed.
    
    Args:
        data: Message data (possibly compressed)
        is_compressed: Whether data is compressed
        
    Returns:
        Decompressed data
    """
    if not is_compressed:
        return data
    
    return zlib.decompress(None)

x_decompress_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_decompress_message__mutmut_1': x_decompress_message__mutmut_1, 
    'x_decompress_message__mutmut_2': x_decompress_message__mutmut_2
}

def decompress_message(*args, **kwargs):
    result = _mutmut_trampoline(x_decompress_message__mutmut_orig, x_decompress_message__mutmut_mutants, args, kwargs)
    return result 

decompress_message.__signature__ = _mutmut_signature(x_decompress_message__mutmut_orig)
x_decompress_message__mutmut_orig.__name__ = 'x_decompress_message'


def x_compute_checksum__mutmut_orig(data: bytes) -> int:
    """Compute CRC32 checksum for message integrity.
    
    Args:
        data: Message data
        
    Returns:
        32-bit checksum
    """
    return zlib.crc32(data) & 0xFFFFFFFF


def x_compute_checksum__mutmut_1(data: bytes) -> int:
    """Compute CRC32 checksum for message integrity.
    
    Args:
        data: Message data
        
    Returns:
        32-bit checksum
    """
    return zlib.crc32(data) | 0xFFFFFFFF


def x_compute_checksum__mutmut_2(data: bytes) -> int:
    """Compute CRC32 checksum for message integrity.
    
    Args:
        data: Message data
        
    Returns:
        32-bit checksum
    """
    return zlib.crc32(None) & 0xFFFFFFFF


def x_compute_checksum__mutmut_3(data: bytes) -> int:
    """Compute CRC32 checksum for message integrity.
    
    Args:
        data: Message data
        
    Returns:
        32-bit checksum
    """
    return zlib.crc32(data) & 4294967296

x_compute_checksum__mutmut_mutants : ClassVar[MutantDict] = {
'x_compute_checksum__mutmut_1': x_compute_checksum__mutmut_1, 
    'x_compute_checksum__mutmut_2': x_compute_checksum__mutmut_2, 
    'x_compute_checksum__mutmut_3': x_compute_checksum__mutmut_3
}

def compute_checksum(*args, **kwargs):
    result = _mutmut_trampoline(x_compute_checksum__mutmut_orig, x_compute_checksum__mutmut_mutants, args, kwargs)
    return result 

compute_checksum.__signature__ = _mutmut_signature(x_compute_checksum__mutmut_orig)
x_compute_checksum__mutmut_orig.__name__ = 'x_compute_checksum'


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
    
    def xǁMultiClientBridgeǁ__init____mutmut_orig(
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
    
    def xǁMultiClientBridgeǁ__init____mutmut_1(
        self,
        max_clients: int = 11,
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
    
    def xǁMultiClientBridgeǁ__init____mutmut_2(
        self,
        max_clients: int = 10,
        heartbeat_timeout: float = 61.0,
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
    
    def xǁMultiClientBridgeǁ__init____mutmut_3(
        self,
        max_clients: int = 10,
        heartbeat_timeout: float = 60.0,
        cleanup_interval: float = 31.0,
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
    
    def xǁMultiClientBridgeǁ__init____mutmut_4(
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
        self.max_clients = None
        self.heartbeat_timeout = heartbeat_timeout
        self.cleanup_interval = cleanup_interval
        
        self.clients: dict[str, ClientInfo] = {}
        self._lock = threading.RLock()
        self._round_robin_index = 0
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_5(
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
        self.heartbeat_timeout = None
        self.cleanup_interval = cleanup_interval
        
        self.clients: dict[str, ClientInfo] = {}
        self._lock = threading.RLock()
        self._round_robin_index = 0
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_6(
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
        self.cleanup_interval = None
        
        self.clients: dict[str, ClientInfo] = {}
        self._lock = threading.RLock()
        self._round_robin_index = 0
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_7(
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
        
        self.clients: dict[str, ClientInfo] = None
        self._lock = threading.RLock()
        self._round_robin_index = 0
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_8(
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
        self._lock = None
        self._round_robin_index = 0
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_9(
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
        self._round_robin_index = None
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_10(
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
        self._round_robin_index = 1
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_11(
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
        self._cleanup_thread: Optional[threading.Thread] = ""
        self._running = False
    
    def xǁMultiClientBridgeǁ__init____mutmut_12(
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
        self._running = None
    
    def xǁMultiClientBridgeǁ__init____mutmut_13(
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
        self._running = True
    
    xǁMultiClientBridgeǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁ__init____mutmut_1': xǁMultiClientBridgeǁ__init____mutmut_1, 
        'xǁMultiClientBridgeǁ__init____mutmut_2': xǁMultiClientBridgeǁ__init____mutmut_2, 
        'xǁMultiClientBridgeǁ__init____mutmut_3': xǁMultiClientBridgeǁ__init____mutmut_3, 
        'xǁMultiClientBridgeǁ__init____mutmut_4': xǁMultiClientBridgeǁ__init____mutmut_4, 
        'xǁMultiClientBridgeǁ__init____mutmut_5': xǁMultiClientBridgeǁ__init____mutmut_5, 
        'xǁMultiClientBridgeǁ__init____mutmut_6': xǁMultiClientBridgeǁ__init____mutmut_6, 
        'xǁMultiClientBridgeǁ__init____mutmut_7': xǁMultiClientBridgeǁ__init____mutmut_7, 
        'xǁMultiClientBridgeǁ__init____mutmut_8': xǁMultiClientBridgeǁ__init____mutmut_8, 
        'xǁMultiClientBridgeǁ__init____mutmut_9': xǁMultiClientBridgeǁ__init____mutmut_9, 
        'xǁMultiClientBridgeǁ__init____mutmut_10': xǁMultiClientBridgeǁ__init____mutmut_10, 
        'xǁMultiClientBridgeǁ__init____mutmut_11': xǁMultiClientBridgeǁ__init____mutmut_11, 
        'xǁMultiClientBridgeǁ__init____mutmut_12': xǁMultiClientBridgeǁ__init____mutmut_12, 
        'xǁMultiClientBridgeǁ__init____mutmut_13': xǁMultiClientBridgeǁ__init____mutmut_13
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁ__init____mutmut_orig)
    xǁMultiClientBridgeǁ__init____mutmut_orig.__name__ = 'xǁMultiClientBridgeǁ__init__'
    
    def xǁMultiClientBridgeǁstart__mutmut_orig(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_1(self) -> None:
        """Start the bridge manager."""
        self._running = None
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_2(self) -> None:
        """Start the bridge manager."""
        self._running = False
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_3(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = None
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_4(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=None,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_5(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=None,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_6(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name=None,
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_7(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_8(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_9(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_10(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=False,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_11(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="XXBridgeCleanupXX",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_12(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="bridgecleanup",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_13(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BRIDGECLEANUP",
        )
        self._cleanup_thread.start()
        logger.info("MultiClientBridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_14(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info(None)
    
    def xǁMultiClientBridgeǁstart__mutmut_15(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("XXMultiClientBridge startedXX")
    
    def xǁMultiClientBridgeǁstart__mutmut_16(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("multiclientbridge started")
    
    def xǁMultiClientBridgeǁstart__mutmut_17(self) -> None:
        """Start the bridge manager."""
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="BridgeCleanup",
        )
        self._cleanup_thread.start()
        logger.info("MULTICLIENTBRIDGE STARTED")
    
    xǁMultiClientBridgeǁstart__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁstart__mutmut_1': xǁMultiClientBridgeǁstart__mutmut_1, 
        'xǁMultiClientBridgeǁstart__mutmut_2': xǁMultiClientBridgeǁstart__mutmut_2, 
        'xǁMultiClientBridgeǁstart__mutmut_3': xǁMultiClientBridgeǁstart__mutmut_3, 
        'xǁMultiClientBridgeǁstart__mutmut_4': xǁMultiClientBridgeǁstart__mutmut_4, 
        'xǁMultiClientBridgeǁstart__mutmut_5': xǁMultiClientBridgeǁstart__mutmut_5, 
        'xǁMultiClientBridgeǁstart__mutmut_6': xǁMultiClientBridgeǁstart__mutmut_6, 
        'xǁMultiClientBridgeǁstart__mutmut_7': xǁMultiClientBridgeǁstart__mutmut_7, 
        'xǁMultiClientBridgeǁstart__mutmut_8': xǁMultiClientBridgeǁstart__mutmut_8, 
        'xǁMultiClientBridgeǁstart__mutmut_9': xǁMultiClientBridgeǁstart__mutmut_9, 
        'xǁMultiClientBridgeǁstart__mutmut_10': xǁMultiClientBridgeǁstart__mutmut_10, 
        'xǁMultiClientBridgeǁstart__mutmut_11': xǁMultiClientBridgeǁstart__mutmut_11, 
        'xǁMultiClientBridgeǁstart__mutmut_12': xǁMultiClientBridgeǁstart__mutmut_12, 
        'xǁMultiClientBridgeǁstart__mutmut_13': xǁMultiClientBridgeǁstart__mutmut_13, 
        'xǁMultiClientBridgeǁstart__mutmut_14': xǁMultiClientBridgeǁstart__mutmut_14, 
        'xǁMultiClientBridgeǁstart__mutmut_15': xǁMultiClientBridgeǁstart__mutmut_15, 
        'xǁMultiClientBridgeǁstart__mutmut_16': xǁMultiClientBridgeǁstart__mutmut_16, 
        'xǁMultiClientBridgeǁstart__mutmut_17': xǁMultiClientBridgeǁstart__mutmut_17
    }
    
    def start(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁstart__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁstart__mutmut_mutants"), args, kwargs, self)
        return result 
    
    start.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁstart__mutmut_orig)
    xǁMultiClientBridgeǁstart__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁstart'
    
    def xǁMultiClientBridgeǁstop__mutmut_orig(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info("MultiClientBridge stopped")
    
    def xǁMultiClientBridgeǁstop__mutmut_1(self) -> None:
        """Stop the bridge manager."""
        self._running = None
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info("MultiClientBridge stopped")
    
    def xǁMultiClientBridgeǁstop__mutmut_2(self) -> None:
        """Stop the bridge manager."""
        self._running = True
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info("MultiClientBridge stopped")
    
    def xǁMultiClientBridgeǁstop__mutmut_3(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=None)
        logger.info("MultiClientBridge stopped")
    
    def xǁMultiClientBridgeǁstop__mutmut_4(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=6.0)
        logger.info("MultiClientBridge stopped")
    
    def xǁMultiClientBridgeǁstop__mutmut_5(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info(None)
    
    def xǁMultiClientBridgeǁstop__mutmut_6(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info("XXMultiClientBridge stoppedXX")
    
    def xǁMultiClientBridgeǁstop__mutmut_7(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info("multiclientbridge stopped")
    
    def xǁMultiClientBridgeǁstop__mutmut_8(self) -> None:
        """Stop the bridge manager."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
        logger.info("MULTICLIENTBRIDGE STOPPED")
    
    xǁMultiClientBridgeǁstop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁstop__mutmut_1': xǁMultiClientBridgeǁstop__mutmut_1, 
        'xǁMultiClientBridgeǁstop__mutmut_2': xǁMultiClientBridgeǁstop__mutmut_2, 
        'xǁMultiClientBridgeǁstop__mutmut_3': xǁMultiClientBridgeǁstop__mutmut_3, 
        'xǁMultiClientBridgeǁstop__mutmut_4': xǁMultiClientBridgeǁstop__mutmut_4, 
        'xǁMultiClientBridgeǁstop__mutmut_5': xǁMultiClientBridgeǁstop__mutmut_5, 
        'xǁMultiClientBridgeǁstop__mutmut_6': xǁMultiClientBridgeǁstop__mutmut_6, 
        'xǁMultiClientBridgeǁstop__mutmut_7': xǁMultiClientBridgeǁstop__mutmut_7, 
        'xǁMultiClientBridgeǁstop__mutmut_8': xǁMultiClientBridgeǁstop__mutmut_8
    }
    
    def stop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁstop__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁstop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    stop.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁstop__mutmut_orig)
    xǁMultiClientBridgeǁstop__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁstop'
    
    def xǁMultiClientBridgeǁregister_client__mutmut_orig(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
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
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_1(
        self,
        client_id: str,
        socket_path: str,
        priority: int = 1,
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
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
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_2(
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
            if len(self.clients) > self.max_clients:
                logger.warning(
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
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
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_3(
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
                    None
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
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_4(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return True
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                socket_path=socket_path,
                priority=priority,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_5(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id not in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                socket_path=socket_path,
                priority=priority,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_6(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(None)
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                socket_path=socket_path,
                priority=priority,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_7(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = None
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_8(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                client_id=None,
                socket_path=socket_path,
                priority=priority,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_9(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                socket_path=None,
                priority=priority,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_10(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                socket_path=socket_path,
                priority=None,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_11(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                socket_path=socket_path,
                priority=priority,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_12(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                priority=priority,
            )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_13(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
                )
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client {client_id} already registered, updating")
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                socket_path=socket_path,
                )
            
            logger.info(
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_14(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
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
                None
            )
            return True
    
    def xǁMultiClientBridgeǁregister_client__mutmut_15(
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
                    f"Cannot register client {client_id}: at capacity "
                    f"({self.max_clients} clients)"
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
                f"Registered client {client_id} (priority={priority}, "
                f"total={len(self.clients)})"
            )
            return False
    
    xǁMultiClientBridgeǁregister_client__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁregister_client__mutmut_1': xǁMultiClientBridgeǁregister_client__mutmut_1, 
        'xǁMultiClientBridgeǁregister_client__mutmut_2': xǁMultiClientBridgeǁregister_client__mutmut_2, 
        'xǁMultiClientBridgeǁregister_client__mutmut_3': xǁMultiClientBridgeǁregister_client__mutmut_3, 
        'xǁMultiClientBridgeǁregister_client__mutmut_4': xǁMultiClientBridgeǁregister_client__mutmut_4, 
        'xǁMultiClientBridgeǁregister_client__mutmut_5': xǁMultiClientBridgeǁregister_client__mutmut_5, 
        'xǁMultiClientBridgeǁregister_client__mutmut_6': xǁMultiClientBridgeǁregister_client__mutmut_6, 
        'xǁMultiClientBridgeǁregister_client__mutmut_7': xǁMultiClientBridgeǁregister_client__mutmut_7, 
        'xǁMultiClientBridgeǁregister_client__mutmut_8': xǁMultiClientBridgeǁregister_client__mutmut_8, 
        'xǁMultiClientBridgeǁregister_client__mutmut_9': xǁMultiClientBridgeǁregister_client__mutmut_9, 
        'xǁMultiClientBridgeǁregister_client__mutmut_10': xǁMultiClientBridgeǁregister_client__mutmut_10, 
        'xǁMultiClientBridgeǁregister_client__mutmut_11': xǁMultiClientBridgeǁregister_client__mutmut_11, 
        'xǁMultiClientBridgeǁregister_client__mutmut_12': xǁMultiClientBridgeǁregister_client__mutmut_12, 
        'xǁMultiClientBridgeǁregister_client__mutmut_13': xǁMultiClientBridgeǁregister_client__mutmut_13, 
        'xǁMultiClientBridgeǁregister_client__mutmut_14': xǁMultiClientBridgeǁregister_client__mutmut_14, 
        'xǁMultiClientBridgeǁregister_client__mutmut_15': xǁMultiClientBridgeǁregister_client__mutmut_15
    }
    
    def register_client(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁregister_client__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁregister_client__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_client.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁregister_client__mutmut_orig)
    xǁMultiClientBridgeǁregister_client__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁregister_client'
    
    def xǁMultiClientBridgeǁunregister_client__mutmut_orig(self, client_id: str) -> bool:
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
            logger.info(
                f"Unregistered client {client_id} (total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁunregister_client__mutmut_1(self, client_id: str) -> bool:
        """Unregister a client.
        
        Args:
            client_id: Client to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if client_id in self.clients:
                return False
            
            del self.clients[client_id]
            logger.info(
                f"Unregistered client {client_id} (total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁunregister_client__mutmut_2(self, client_id: str) -> bool:
        """Unregister a client.
        
        Args:
            client_id: Client to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if client_id not in self.clients:
                return True
            
            del self.clients[client_id]
            logger.info(
                f"Unregistered client {client_id} (total={len(self.clients)})"
            )
            return True
    
    def xǁMultiClientBridgeǁunregister_client__mutmut_3(self, client_id: str) -> bool:
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
            logger.info(
                None
            )
            return True
    
    def xǁMultiClientBridgeǁunregister_client__mutmut_4(self, client_id: str) -> bool:
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
            logger.info(
                f"Unregistered client {client_id} (total={len(self.clients)})"
            )
            return False
    
    xǁMultiClientBridgeǁunregister_client__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁunregister_client__mutmut_1': xǁMultiClientBridgeǁunregister_client__mutmut_1, 
        'xǁMultiClientBridgeǁunregister_client__mutmut_2': xǁMultiClientBridgeǁunregister_client__mutmut_2, 
        'xǁMultiClientBridgeǁunregister_client__mutmut_3': xǁMultiClientBridgeǁunregister_client__mutmut_3, 
        'xǁMultiClientBridgeǁunregister_client__mutmut_4': xǁMultiClientBridgeǁunregister_client__mutmut_4
    }
    
    def unregister_client(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁunregister_client__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁunregister_client__mutmut_mutants"), args, kwargs, self)
        return result 
    
    unregister_client.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁunregister_client__mutmut_orig)
    xǁMultiClientBridgeǁunregister_client__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁunregister_client'
    
    def xǁMultiClientBridgeǁheartbeat__mutmut_orig(self, client_id: str) -> bool:
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
    
    def xǁMultiClientBridgeǁheartbeat__mutmut_1(self, client_id: str) -> bool:
        """Update client heartbeat.
        
        Args:
            client_id: Client sending heartbeat
            
        Returns:
            True if client found, False otherwise
        """
        with self._lock:
            if client_id in self.clients:
                return False
            
            self.clients[client_id].update_heartbeat()
            return True
    
    def xǁMultiClientBridgeǁheartbeat__mutmut_2(self, client_id: str) -> bool:
        """Update client heartbeat.
        
        Args:
            client_id: Client sending heartbeat
            
        Returns:
            True if client found, False otherwise
        """
        with self._lock:
            if client_id not in self.clients:
                return True
            
            self.clients[client_id].update_heartbeat()
            return True
    
    def xǁMultiClientBridgeǁheartbeat__mutmut_3(self, client_id: str) -> bool:
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
            return False
    
    xǁMultiClientBridgeǁheartbeat__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁheartbeat__mutmut_1': xǁMultiClientBridgeǁheartbeat__mutmut_1, 
        'xǁMultiClientBridgeǁheartbeat__mutmut_2': xǁMultiClientBridgeǁheartbeat__mutmut_2, 
        'xǁMultiClientBridgeǁheartbeat__mutmut_3': xǁMultiClientBridgeǁheartbeat__mutmut_3
    }
    
    def heartbeat(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁheartbeat__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁheartbeat__mutmut_mutants"), args, kwargs, self)
        return result 
    
    heartbeat.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁheartbeat__mutmut_orig)
    xǁMultiClientBridgeǁheartbeat__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁheartbeat'
    
    def xǁMultiClientBridgeǁget_client__mutmut_orig(self, client_id: str) -> Optional[ClientInfo]:
        """Get client info by ID.
        
        Args:
            client_id: Client to look up
            
        Returns:
            ClientInfo if found, None otherwise
        """
        with self._lock:
            return self.clients.get(client_id)
    
    def xǁMultiClientBridgeǁget_client__mutmut_1(self, client_id: str) -> Optional[ClientInfo]:
        """Get client info by ID.
        
        Args:
            client_id: Client to look up
            
        Returns:
            ClientInfo if found, None otherwise
        """
        with self._lock:
            return self.clients.get(None)
    
    xǁMultiClientBridgeǁget_client__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁget_client__mutmut_1': xǁMultiClientBridgeǁget_client__mutmut_1
    }
    
    def get_client(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁget_client__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁget_client__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_client.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁget_client__mutmut_orig)
    xǁMultiClientBridgeǁget_client__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁget_client'
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_orig(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_1(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = None
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_2(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(None)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_3(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_4(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = None
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_5(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                None,
                key=lambda c: c.priority,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_6(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=None,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_7(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=None,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_8(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                key=lambda c: c.priority,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_9(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_10(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_11(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: None,
                reverse=True,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_12(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=False,
            )
            
            return sorted_clients[0].socket_path
    
    def xǁMultiClientBridgeǁroute_by_priority__mutmut_13(self) -> Optional[str]:
        """Get socket path for highest priority alive client.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Sort by priority (descending)
            sorted_clients = sorted(
                alive_clients,
                key=lambda c: c.priority,
                reverse=True,
            )
            
            return sorted_clients[1].socket_path
    
    xǁMultiClientBridgeǁroute_by_priority__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁroute_by_priority__mutmut_1': xǁMultiClientBridgeǁroute_by_priority__mutmut_1, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_2': xǁMultiClientBridgeǁroute_by_priority__mutmut_2, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_3': xǁMultiClientBridgeǁroute_by_priority__mutmut_3, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_4': xǁMultiClientBridgeǁroute_by_priority__mutmut_4, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_5': xǁMultiClientBridgeǁroute_by_priority__mutmut_5, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_6': xǁMultiClientBridgeǁroute_by_priority__mutmut_6, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_7': xǁMultiClientBridgeǁroute_by_priority__mutmut_7, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_8': xǁMultiClientBridgeǁroute_by_priority__mutmut_8, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_9': xǁMultiClientBridgeǁroute_by_priority__mutmut_9, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_10': xǁMultiClientBridgeǁroute_by_priority__mutmut_10, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_11': xǁMultiClientBridgeǁroute_by_priority__mutmut_11, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_12': xǁMultiClientBridgeǁroute_by_priority__mutmut_12, 
        'xǁMultiClientBridgeǁroute_by_priority__mutmut_13': xǁMultiClientBridgeǁroute_by_priority__mutmut_13
    }
    
    def route_by_priority(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁroute_by_priority__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁroute_by_priority__mutmut_mutants"), args, kwargs, self)
        return result 
    
    route_by_priority.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁroute_by_priority__mutmut_orig)
    xǁMultiClientBridgeǁroute_by_priority__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁroute_by_priority'
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_orig(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_1(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = None
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_2(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(None)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_3(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_4(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index = len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_5(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index /= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_6(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = None
            self._round_robin_index += 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_7(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index = 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_8(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index -= 1
            
            return client.socket_path
    
    def xǁMultiClientBridgeǁroute_round_robin__mutmut_9(self) -> Optional[str]:
        """Get socket path using round-robin among alive clients.
        
        Returns:
            Socket path or None if no clients available
        """
        with self._lock:
            alive_clients = [
                c for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
            
            if not alive_clients:
                return None
            
            # Round-robin selection
            self._round_robin_index %= len(alive_clients)
            client = alive_clients[self._round_robin_index]
            self._round_robin_index += 2
            
            return client.socket_path
    
    xǁMultiClientBridgeǁroute_round_robin__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁroute_round_robin__mutmut_1': xǁMultiClientBridgeǁroute_round_robin__mutmut_1, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_2': xǁMultiClientBridgeǁroute_round_robin__mutmut_2, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_3': xǁMultiClientBridgeǁroute_round_robin__mutmut_3, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_4': xǁMultiClientBridgeǁroute_round_robin__mutmut_4, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_5': xǁMultiClientBridgeǁroute_round_robin__mutmut_5, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_6': xǁMultiClientBridgeǁroute_round_robin__mutmut_6, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_7': xǁMultiClientBridgeǁroute_round_robin__mutmut_7, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_8': xǁMultiClientBridgeǁroute_round_robin__mutmut_8, 
        'xǁMultiClientBridgeǁroute_round_robin__mutmut_9': xǁMultiClientBridgeǁroute_round_robin__mutmut_9
    }
    
    def route_round_robin(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁroute_round_robin__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁroute_round_robin__mutmut_mutants"), args, kwargs, self)
        return result 
    
    route_round_robin.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁroute_round_robin__mutmut_orig)
    xǁMultiClientBridgeǁroute_round_robin__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁroute_round_robin'
    
    def xǁMultiClientBridgeǁbroadcast_targets__mutmut_orig(self) -> list[str]:
        """Get socket paths for all alive clients (for broadcast).
        
        Returns:
            List of socket paths
        """
        with self._lock:
            return [
                c.socket_path
                for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            ]
    
    def xǁMultiClientBridgeǁbroadcast_targets__mutmut_1(self) -> list[str]:
        """Get socket paths for all alive clients (for broadcast).
        
        Returns:
            List of socket paths
        """
        with self._lock:
            return [
                c.socket_path
                for c in self.clients.values()
                if c.is_alive(None)
            ]
    
    xǁMultiClientBridgeǁbroadcast_targets__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁbroadcast_targets__mutmut_1': xǁMultiClientBridgeǁbroadcast_targets__mutmut_1
    }
    
    def broadcast_targets(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁbroadcast_targets__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁbroadcast_targets__mutmut_mutants"), args, kwargs, self)
        return result 
    
    broadcast_targets.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁbroadcast_targets__mutmut_orig)
    xǁMultiClientBridgeǁbroadcast_targets__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁbroadcast_targets'
    
    def xǁMultiClientBridgeǁget_stats__mutmut_orig(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_1(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = None
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_2(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                None
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_3(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                2 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_4(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(None)
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_5(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "XXtotal_clientsXX": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_6(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "TOTAL_CLIENTS": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_7(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "XXalive_clientsXX": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_8(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "ALIVE_CLIENTS": alive_count,
                "max_clients": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_9(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "XXmax_clientsXX": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_10(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "MAX_CLIENTS": self.max_clients,
                "clients": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_11(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "XXclientsXX": [c.to_dict() for c in self.clients.values()],
            }
    
    def xǁMultiClientBridgeǁget_stats__mutmut_12(self) -> dict[str, Any]:
        """Get bridge statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            alive_count = sum(
                1 for c in self.clients.values()
                if c.is_alive(self.heartbeat_timeout)
            )
            
            return {
                "total_clients": len(self.clients),
                "alive_clients": alive_count,
                "max_clients": self.max_clients,
                "CLIENTS": [c.to_dict() for c in self.clients.values()],
            }
    
    xǁMultiClientBridgeǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁget_stats__mutmut_1': xǁMultiClientBridgeǁget_stats__mutmut_1, 
        'xǁMultiClientBridgeǁget_stats__mutmut_2': xǁMultiClientBridgeǁget_stats__mutmut_2, 
        'xǁMultiClientBridgeǁget_stats__mutmut_3': xǁMultiClientBridgeǁget_stats__mutmut_3, 
        'xǁMultiClientBridgeǁget_stats__mutmut_4': xǁMultiClientBridgeǁget_stats__mutmut_4, 
        'xǁMultiClientBridgeǁget_stats__mutmut_5': xǁMultiClientBridgeǁget_stats__mutmut_5, 
        'xǁMultiClientBridgeǁget_stats__mutmut_6': xǁMultiClientBridgeǁget_stats__mutmut_6, 
        'xǁMultiClientBridgeǁget_stats__mutmut_7': xǁMultiClientBridgeǁget_stats__mutmut_7, 
        'xǁMultiClientBridgeǁget_stats__mutmut_8': xǁMultiClientBridgeǁget_stats__mutmut_8, 
        'xǁMultiClientBridgeǁget_stats__mutmut_9': xǁMultiClientBridgeǁget_stats__mutmut_9, 
        'xǁMultiClientBridgeǁget_stats__mutmut_10': xǁMultiClientBridgeǁget_stats__mutmut_10, 
        'xǁMultiClientBridgeǁget_stats__mutmut_11': xǁMultiClientBridgeǁget_stats__mutmut_11, 
        'xǁMultiClientBridgeǁget_stats__mutmut_12': xǁMultiClientBridgeǁget_stats__mutmut_12
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁget_stats__mutmut_orig)
    xǁMultiClientBridgeǁget_stats__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁget_stats'
    
    def xǁMultiClientBridgeǁ_cleanup_loop__mutmut_orig(self) -> None:
        """Background thread to clean up dead clients."""
        while self._running:
            time.sleep(self.cleanup_interval)
            self._cleanup_dead_clients()
    
    def xǁMultiClientBridgeǁ_cleanup_loop__mutmut_1(self) -> None:
        """Background thread to clean up dead clients."""
        while self._running:
            time.sleep(None)
            self._cleanup_dead_clients()
    
    xǁMultiClientBridgeǁ_cleanup_loop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁ_cleanup_loop__mutmut_1': xǁMultiClientBridgeǁ_cleanup_loop__mutmut_1
    }
    
    def _cleanup_loop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁ_cleanup_loop__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁ_cleanup_loop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _cleanup_loop.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁ_cleanup_loop__mutmut_orig)
    xǁMultiClientBridgeǁ_cleanup_loop__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁ_cleanup_loop'
    
    def xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_orig(self) -> None:
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
                    f"Cleaned up {len(dead_clients)} dead clients, "
                    f"{len(self.clients)} remaining"
                )
    
    def xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_1(self) -> None:
        """Remove clients that haven't sent heartbeat."""
        with self._lock:
            dead_clients = None
            
            for client_id in dead_clients:
                del self.clients[client_id]
                logger.info(f"Cleaned up dead client: {client_id}")
            
            if dead_clients:
                logger.info(
                    f"Cleaned up {len(dead_clients)} dead clients, "
                    f"{len(self.clients)} remaining"
                )
    
    def xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_2(self) -> None:
        """Remove clients that haven't sent heartbeat."""
        with self._lock:
            dead_clients = [
                client_id
                for client_id, client in self.clients.items()
                if client.is_alive(self.heartbeat_timeout)
            ]
            
            for client_id in dead_clients:
                del self.clients[client_id]
                logger.info(f"Cleaned up dead client: {client_id}")
            
            if dead_clients:
                logger.info(
                    f"Cleaned up {len(dead_clients)} dead clients, "
                    f"{len(self.clients)} remaining"
                )
    
    def xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_3(self) -> None:
        """Remove clients that haven't sent heartbeat."""
        with self._lock:
            dead_clients = [
                client_id
                for client_id, client in self.clients.items()
                if not client.is_alive(None)
            ]
            
            for client_id in dead_clients:
                del self.clients[client_id]
                logger.info(f"Cleaned up dead client: {client_id}")
            
            if dead_clients:
                logger.info(
                    f"Cleaned up {len(dead_clients)} dead clients, "
                    f"{len(self.clients)} remaining"
                )
    
    def xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_4(self) -> None:
        """Remove clients that haven't sent heartbeat."""
        with self._lock:
            dead_clients = [
                client_id
                for client_id, client in self.clients.items()
                if not client.is_alive(self.heartbeat_timeout)
            ]
            
            for client_id in dead_clients:
                del self.clients[client_id]
                logger.info(None)
            
            if dead_clients:
                logger.info(
                    f"Cleaned up {len(dead_clients)} dead clients, "
                    f"{len(self.clients)} remaining"
                )
    
    def xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_5(self) -> None:
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
                    None
                )
    
    xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_1': xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_1, 
        'xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_2': xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_2, 
        'xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_3': xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_3, 
        'xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_4': xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_4, 
        'xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_5': xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_5
    }
    
    def _cleanup_dead_clients(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_orig"), object.__getattribute__(self, "xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _cleanup_dead_clients.__signature__ = _mutmut_signature(xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_orig)
    xǁMultiClientBridgeǁ_cleanup_dead_clients__mutmut_orig.__name__ = 'xǁMultiClientBridgeǁ_cleanup_dead_clients'


def x_encode_message__mutmut_orig(
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


def x_encode_message__mutmut_1(
    payload: bytes,
    flags: MessageFlags = MessageFlags.NONE,
    compress: bool = False,
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


def x_encode_message__mutmut_2(
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
        payload, was_compressed = None
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


def x_encode_message__mutmut_3(
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
        payload, was_compressed = compress_message(None)
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


def x_encode_message__mutmut_4(
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
            flags = MessageFlags.COMPRESSED
    
    # Compute checksum
    checksum = compute_checksum(payload)
    
    # Create header
    header = ProtocolHeader(
        flags=flags,
        length=len(payload),
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_5(
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
            flags &= MessageFlags.COMPRESSED
    
    # Compute checksum
    checksum = compute_checksum(payload)
    
    # Create header
    header = ProtocolHeader(
        flags=flags,
        length=len(payload),
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_6(
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
    checksum = None
    
    # Create header
    header = ProtocolHeader(
        flags=flags,
        length=len(payload),
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_7(
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
    checksum = compute_checksum(None)
    
    # Create header
    header = ProtocolHeader(
        flags=flags,
        length=len(payload),
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_8(
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
    header = None
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_9(
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
        flags=None,
        length=len(payload),
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_10(
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
        length=None,
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_11(
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
        checksum=None,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_12(
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
        length=len(payload),
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_13(
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
        checksum=checksum,
    )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_14(
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
        )
    
    return header.to_bytes() + payload


def x_encode_message__mutmut_15(
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
    
    return header.to_bytes() - payload

x_encode_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_encode_message__mutmut_1': x_encode_message__mutmut_1, 
    'x_encode_message__mutmut_2': x_encode_message__mutmut_2, 
    'x_encode_message__mutmut_3': x_encode_message__mutmut_3, 
    'x_encode_message__mutmut_4': x_encode_message__mutmut_4, 
    'x_encode_message__mutmut_5': x_encode_message__mutmut_5, 
    'x_encode_message__mutmut_6': x_encode_message__mutmut_6, 
    'x_encode_message__mutmut_7': x_encode_message__mutmut_7, 
    'x_encode_message__mutmut_8': x_encode_message__mutmut_8, 
    'x_encode_message__mutmut_9': x_encode_message__mutmut_9, 
    'x_encode_message__mutmut_10': x_encode_message__mutmut_10, 
    'x_encode_message__mutmut_11': x_encode_message__mutmut_11, 
    'x_encode_message__mutmut_12': x_encode_message__mutmut_12, 
    'x_encode_message__mutmut_13': x_encode_message__mutmut_13, 
    'x_encode_message__mutmut_14': x_encode_message__mutmut_14, 
    'x_encode_message__mutmut_15': x_encode_message__mutmut_15
}

def encode_message(*args, **kwargs):
    result = _mutmut_trampoline(x_encode_message__mutmut_orig, x_encode_message__mutmut_mutants, args, kwargs)
    return result 

encode_message.__signature__ = _mutmut_signature(x_encode_message__mutmut_orig)
x_encode_message__mutmut_orig.__name__ = 'x_encode_message'


def x_decode_message__mutmut_orig(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_1(data: bytes) -> tuple[bytes, ProtocolHeader]:
    """Decode a protocol v2 message.
    
    Args:
        data: Raw message data
        
    Returns:
        Tuple of (payload, header)
        
    Raises:
        ValueError: If message is invalid or corrupted
    """
    if len(data) <= ProtocolHeader.size():
        raise ValueError(f"Message too short: {len(data)} bytes")
    
    # Parse header
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_2(data: bytes) -> tuple[bytes, ProtocolHeader]:
    """Decode a protocol v2 message.
    
    Args:
        data: Raw message data
        
    Returns:
        Tuple of (payload, header)
        
    Raises:
        ValueError: If message is invalid or corrupted
    """
    if len(data) < ProtocolHeader.size():
        raise ValueError(None)
    
    # Parse header
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_3(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = None
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_4(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(None)
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_5(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = None
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_6(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() - header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_7(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) == header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_8(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            None
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_9(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = None
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_10(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(None)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_11(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum == header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_12(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            None
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_13(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED not in header.flags:
        payload = decompress_message(payload, True)
    
    return payload, header


def x_decode_message__mutmut_14(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = None
    
    return payload, header


def x_decode_message__mutmut_15(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(None, True)
    
    return payload, header


def x_decode_message__mutmut_16(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, None)
    
    return payload, header


def x_decode_message__mutmut_17(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(True)
    
    return payload, header


def x_decode_message__mutmut_18(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, )
    
    return payload, header


def x_decode_message__mutmut_19(data: bytes) -> tuple[bytes, ProtocolHeader]:
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
    header = ProtocolHeader.from_bytes(data[:ProtocolHeader.size()])
    
    # Extract payload
    payload = data[ProtocolHeader.size():ProtocolHeader.size() + header.length]
    
    if len(payload) != header.length:
        raise ValueError(
            f"Payload length mismatch: expected {header.length}, "
            f"got {len(payload)}"
        )
    
    # Verify checksum
    computed_checksum = compute_checksum(payload)
    if computed_checksum != header.checksum:
        raise ValueError(
            f"Checksum mismatch: expected {header.checksum:08x}, "
            f"got {computed_checksum:08x}"
        )
    
    # Decompress if needed
    if MessageFlags.COMPRESSED in header.flags:
        payload = decompress_message(payload, False)
    
    return payload, header

x_decode_message__mutmut_mutants : ClassVar[MutantDict] = {
'x_decode_message__mutmut_1': x_decode_message__mutmut_1, 
    'x_decode_message__mutmut_2': x_decode_message__mutmut_2, 
    'x_decode_message__mutmut_3': x_decode_message__mutmut_3, 
    'x_decode_message__mutmut_4': x_decode_message__mutmut_4, 
    'x_decode_message__mutmut_5': x_decode_message__mutmut_5, 
    'x_decode_message__mutmut_6': x_decode_message__mutmut_6, 
    'x_decode_message__mutmut_7': x_decode_message__mutmut_7, 
    'x_decode_message__mutmut_8': x_decode_message__mutmut_8, 
    'x_decode_message__mutmut_9': x_decode_message__mutmut_9, 
    'x_decode_message__mutmut_10': x_decode_message__mutmut_10, 
    'x_decode_message__mutmut_11': x_decode_message__mutmut_11, 
    'x_decode_message__mutmut_12': x_decode_message__mutmut_12, 
    'x_decode_message__mutmut_13': x_decode_message__mutmut_13, 
    'x_decode_message__mutmut_14': x_decode_message__mutmut_14, 
    'x_decode_message__mutmut_15': x_decode_message__mutmut_15, 
    'x_decode_message__mutmut_16': x_decode_message__mutmut_16, 
    'x_decode_message__mutmut_17': x_decode_message__mutmut_17, 
    'x_decode_message__mutmut_18': x_decode_message__mutmut_18, 
    'x_decode_message__mutmut_19': x_decode_message__mutmut_19
}

def decode_message(*args, **kwargs):
    result = _mutmut_trampoline(x_decode_message__mutmut_orig, x_decode_message__mutmut_mutants, args, kwargs)
    return result 

decode_message.__signature__ = _mutmut_signature(x_decode_message__mutmut_orig)
x_decode_message__mutmut_orig.__name__ = 'x_decode_message'


__all__ = [
    "PROTOCOL_VERSION",
    "COMPRESSION_THRESHOLD",
    "MIN_COMPRESSION_SAVINGS",
    "MessageFlags",
    "ProtocolHeader",
    "ClientInfo",
    "MultiClientBridge",
    "compress_message",
    "decompress_message",
    "compute_checksum",
    "encode_message",
    "decode_message",
]
