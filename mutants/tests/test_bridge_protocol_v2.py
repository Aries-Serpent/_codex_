"""Tests for Bridge Protocol v2 enhancements.

PS-02 Enhancement: Tests for advanced bridge features:
- Message compression
- Multi-client support
- Protocol encoding/decoding
"""

import tempfile
import time

import pytest

from bridge_protocol_v2 import (
    COMPRESSION_THRESHOLD,
    MIN_COMPRESSION_SAVINGS,
    PROTOCOL_VERSION,
    ClientInfo,
    MessageFlags,
    MultiClientBridge,
    ProtocolHeader,
    compress_message,
    compute_checksum,
    decode_message,
    decompress_message,
    encode_message,
)

# Expected compression ratio threshold for assertions
EXPECTED_COMPRESSION_RATIO = 1.0 - MIN_COMPRESSION_SAVINGS  # 0.9 (90%)


class TestMessageCompression:
    """Test message compression functionality."""

    def test_compress_small_message(self):
        """Small messages should not be compressed."""
        data = b"small message"
        compressed, was_compressed = compress_message(data)

        assert was_compressed is False, "was_compressed is not valid"
        assert compressed == data, "Data must not be empty"

    def test_compress_large_message(self):
        """Large compressible messages should be compressed."""
        # Create highly compressible data
        data = b"A" * (COMPRESSION_THRESHOLD + 1000)
        compressed, was_compressed = compress_message(data)

        assert was_compressed is True, "was_compressed is not valid"
        assert len(compressed) < len(data), "Compressed must not be empty"

    def test_compress_incompressible(self):
        """Random data may not compress well."""
        import os

        data = os.urandom(COMPRESSION_THRESHOLD + 1000)
        compressed, was_compressed = compress_message(data)

        # Random data typically doesn't compress well
        # Result depends on actual compression ratio
        if was_compressed:
            assert len(compressed) < len(data) * EXPECTED_COMPRESSION_RATIO, "Compressed must not be empty"

    def test_decompress_message(self):
        """Test decompression of compressed data."""
        original = b"test data " * 10000
        compressed, was_compressed = compress_message(original)

        if was_compressed:
            decompressed = decompress_message(compressed, True)
            assert decompressed == original, "decompressed is not valid"

    def test_decompress_uncompressed(self):
        """Uncompressed data passes through unchanged."""
        data = b"not compressed"
        result = decompress_message(data, False)
        assert result == data, "Result must not be empty"


class TestProtocolHeader:
    """Test protocol header serialization."""

    def test_header_to_bytes(self):
        """Test header serialization."""
        header = ProtocolHeader(
            flags=MessageFlags.COMPRESSED | MessageFlags.PRIORITY,
            length=1024,
            checksum=0x12345678,
        )

        data = header.to_bytes()
        assert len(data) == ProtocolHeader.size(), "Data must not be empty"
        assert data[:4] == b"CBv2", "Data must not be empty"

    def test_header_from_bytes(self):
        """Test header deserialization."""
        header = ProtocolHeader(
            flags=MessageFlags.COMPRESSED,
            length=512,
            checksum=0xDEADBEEF,
        )

        data = header.to_bytes()
        parsed = ProtocolHeader.from_bytes(data)

        assert parsed.version == PROTOCOL_VERSION, "version is not valid"
        assert MessageFlags.COMPRESSED in parsed.flags, "Condition must be true"
        assert parsed.length == 512, "Length must be greater than zero"
        assert parsed.checksum == 0xDEADBEEF, "checksum is not valid"

    def test_invalid_magic(self):
        """Test rejection of invalid magic bytes."""
        data = b"XXXX" + b"\x00" * 10

        with pytest.raises(ValueError, match="Invalid magic"):
            ProtocolHeader.from_bytes(data)

    def test_header_too_short(self):
        """Test rejection of truncated header."""
        data = b"CBv2\x02"  # Too short

        with pytest.raises(ValueError, match="too short"):
            ProtocolHeader.from_bytes(data)


class TestChecksum:
    """Test checksum computation."""

    def test_compute_checksum(self):
        """Test CRC32 checksum."""
        data = b"test payload"
        checksum = compute_checksum(data)

        assert isinstance(checksum, int)
        assert 0 <= checksum <= 0xFFFFFFFF, "0 is not valid"

    def test_checksum_deterministic(self):
        """Same data produces same checksum."""
        data = b"consistent data"

        checksum1 = compute_checksum(data)
        checksum2 = compute_checksum(data)

        assert checksum1 == checksum2, "checksum1 is not valid"

    def test_checksum_different(self):
        """Different data produces different checksums."""
        checksum1 = compute_checksum(b"data 1")
        checksum2 = compute_checksum(b"data 2")

        assert checksum1 != checksum2, "checksum1 is not valid"


class TestEncodeDecodeMessage:
    """Test message encoding and decoding."""

    def test_encode_small_message(self):
        """Test encoding small message."""
        payload = b"small payload"
        encoded = encode_message(payload)

        assert len(encoded) == ProtocolHeader.size() + len(payload), "Encoded must not be empty"

    def test_encode_large_message_compressed(self):
        """Test encoding large compressible message."""
        payload = b"A" * (COMPRESSION_THRESHOLD + 1000)
        encoded = encode_message(payload, compress=True)

        # Should be smaller than header + payload
        assert len(encoded) < ProtocolHeader.size() + len(payload), "Encoded must not be empty"

    def test_decode_message(self):
        """Test decoding encoded message."""
        original = b"test payload for encoding"
        encoded = encode_message(original)

        decoded, header = decode_message(encoded)

        assert decoded == original, "decoded is not valid"
        assert header.length > 0, "length must be positive"

    def test_decode_compressed_message(self):
        """Test decoding compressed message."""
        original = b"X" * (COMPRESSION_THRESHOLD + 1000)
        encoded = encode_message(original, compress=True)

        decoded, header = decode_message(encoded)

        assert decoded == original, "decoded is not valid"
        assert MessageFlags.COMPRESSED in header.flags, "Condition must be true"

    def test_decode_corrupted_checksum(self):
        """Test detection of corrupted message."""
        payload = b"test payload"
        encoded = encode_message(payload)

        # Corrupt the payload
        corrupted = bytearray(encoded)
        corrupted[-1] ^= 0xFF  # Flip bits in last byte

        with pytest.raises(ValueError, match="Checksum mismatch"):
            decode_message(bytes(corrupted))

    def test_decode_truncated_message(self):
        """Test detection of truncated message."""
        payload = b"test payload"
        encoded = encode_message(payload)

        # Truncate the message
        truncated = encoded[:-5]

        with pytest.raises(ValueError, match="length mismatch"):
            decode_message(truncated)


class TestClientInfo:
    """Test ClientInfo model."""

    def test_create_client_info(self):
        """Test creating client info."""
        client = ClientInfo(
            client_id="client-1",
            socket_path=os.path.join(tempfile.gettempdir(), "client1.sock"),
            priority=5,
        )

        assert client.client_id == "client-1", "client_id is not valid"
        assert client.priority == 5, "priority is not valid"
        assert client.message_count == 0, "Count must be greater than zero"

    def test_update_heartbeat(self):
        """Test heartbeat update."""
        client = ClientInfo(
            client_id="client-1",
            socket_path=os.path.join(tempfile.gettempdir(), "client1.sock"),
        )

        old_heartbeat = client.last_heartbeat
        time.sleep(0.1)
        client.update_heartbeat()

        assert client.last_heartbeat > old_heartbeat, "last_heartbeat must be greater than zero"

    def test_is_alive(self):
        """Test client alive check."""
        client = ClientInfo(
            client_id="client-1",
            socket_path=os.path.join(tempfile.gettempdir(), "client1.sock"),
        )

        assert client.is_alive(timeout=60.0) is True, "Condition must be true"
        assert client.is_alive(timeout=0.0) is False, "Condition must be true"

    def test_to_dict(self):
        """Test serialization to dict."""
        client = ClientInfo(
            client_id="client-1",
            socket_path=os.path.join(tempfile.gettempdir(), "client1.sock"),
        )

        d = client.to_dict()

        assert d["client_id"] == "client-1", "Condition must be true"
        assert "is_alive" in d, "Condition must be true"


class TestMultiClientBridge:
    """Test MultiClientBridge functionality."""

    def test_register_client(self):
        """Test registering a client."""
        bridge = MultiClientBridge(max_clients=5)

        success = bridge.register_client(
            client_id="client-1",
            socket_path=os.path.join(tempfile.gettempdir(), "client1.sock"),
            priority=10,
        )

        assert success is True, "success is not valid"
        assert "client-1" in bridge.clients, "Condition must be true"

    def test_register_at_capacity(self):
        """Test registration at capacity."""
        bridge = MultiClientBridge(max_clients=2)

        bridge.register_client("client-1", os.path.join(tempfile.gettempdir(), "c1.sock"))
        bridge.register_client("client-2", os.path.join(tempfile.gettempdir(), "c2.sock"))
        success = bridge.register_client("client-3", os.path.join(tempfile.gettempdir(), "c3.sock"))

        assert success is False, "success is not valid"
        assert len(bridge.clients) == 2, "Collection must not be empty"

    def test_unregister_client(self):
        """Test unregistering a client."""
        bridge = MultiClientBridge()
        bridge.register_client("client-1", os.path.join(tempfile.gettempdir(), "c1.sock"))

        success = bridge.unregister_client("client-1")

        assert success is True, "success is not valid"
        assert "client-1" not in bridge.clients, "Condition must be true"

    def test_heartbeat(self):
        """Test heartbeat update."""
        bridge = MultiClientBridge()
        bridge.register_client("client-1", os.path.join(tempfile.gettempdir(), "c1.sock"))

        success = bridge.heartbeat("client-1")

        assert success is True, "success is not valid"

    def test_heartbeat_unknown_client(self):
        """Test heartbeat for unknown client."""
        bridge = MultiClientBridge()

        success = bridge.heartbeat("unknown")

        assert success is False, "success is not valid"

    def test_route_by_priority(self):
        """Test priority-based routing."""
        bridge = MultiClientBridge()
        bridge.register_client("low", os.path.join(tempfile.gettempdir(), "low.sock"), priority=1)
        bridge.register_client("high", os.path.join(tempfile.gettempdir(), "high.sock"), priority=10)

        socket = bridge.route_by_priority()

        assert socket == os.path.join(tempfile.gettempdir(), "high.sock"), "socket is not valid"

    def test_route_round_robin(self):
        """Test round-robin routing."""
        bridge = MultiClientBridge()
        bridge.register_client("client-1", os.path.join(tempfile.gettempdir(), "c1.sock"))
        bridge.register_client("client-2", os.path.join(tempfile.gettempdir(), "c2.sock"))

        sockets = set()
        for _ in range(4):
            socket = bridge.route_round_robin()
            if socket:
                sockets.add(socket)

        assert len(sockets) == 2, "Sockets must not be empty"

    def test_broadcast_targets(self):
        """Test getting broadcast targets."""
        bridge = MultiClientBridge()
        bridge.register_client("client-1", os.path.join(tempfile.gettempdir(), "c1.sock"))
        bridge.register_client("client-2", os.path.join(tempfile.gettempdir(), "c2.sock"))

        targets = bridge.broadcast_targets()

        assert len(targets) == 2, "Targets must not be empty"
        assert os.path.join(tempfile.gettempdir(), "c1.sock") in targets, "Condition must be true"
        assert os.path.join(tempfile.gettempdir(), "c2.sock") in targets, "Condition must be true"

    def test_get_stats(self):
        """Test getting bridge statistics."""
        bridge = MultiClientBridge(max_clients=10)
        bridge.register_client("client-1", os.path.join(tempfile.gettempdir(), "c1.sock"))

        stats = bridge.get_stats()

        assert stats["total_clients"] == 1, "Condition must be true"
        assert stats["max_clients"] == 10, "Condition must be true"
        assert len(stats["clients"]) == 1, "Collection must not be empty"


class TestMessageFlags:
    """Test message flags enumeration."""

    def test_flag_combinations(self):
        """Test combining flags."""
        flags = MessageFlags.COMPRESSED | MessageFlags.PRIORITY

        assert MessageFlags.COMPRESSED in flags, "Condition must be true"
        assert MessageFlags.PRIORITY in flags, "Condition must be true"
        assert MessageFlags.ENCRYPTED not in flags, "Condition must be true"

    def test_flag_none(self):
        """Test no flags."""
        flags = MessageFlags.NONE

        assert int(flags) == 0, "Condition must be true"
        assert MessageFlags.COMPRESSED not in flags, "Condition must be true"
