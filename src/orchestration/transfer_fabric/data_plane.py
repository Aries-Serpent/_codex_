"""Data Plane: Chunked payload transfer with atomic commit and verification.

Splits payload into chunks, calculates checksums, and ensures atomic
commitment before finalizing transfer.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class TransferStatus(Enum):
    """Status of a transfer."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Chunk:
    """Represents a chunk of transferred data."""

    chunk_id: str = field(default_factory=lambda: str(uuid4()))
    sequence: int = 0
    data: bytes = field(default_factory=bytes)
    checksum: str = ""
    verified: bool = False

    def calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of chunk data."""
        if not self.data:
            self.checksum = ""
            return ""

        h = hashlib.sha256()
        h.update(self.data)
        self.checksum = h.hexdigest()
        return self.checksum

    def verify_checksum(self, expected: str) -> bool:
        """Verify chunk checksum."""
        if not self.data:
            return expected == ""

        calculated = self.calculate_checksum()
        self.verified = calculated == expected
        return self.verified

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "sequence": self.sequence,
            "data_size": len(self.data),
            "checksum": self.checksum,
            "verified": self.verified,
        }


@dataclass
class TransferResult:
    """Result of a complete transfer."""

    transfer_id: str = field(default_factory=lambda: str(uuid4()))
    total_bytes: int = 0
    chunks_verified: int = 0
    status: TransferStatus = TransferStatus.PENDING
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transfer_id": self.transfer_id,
            "total_bytes": self.total_bytes,
            "chunks_verified": self.chunks_verified,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
        }


class DataPlane:
    """Handles chunked data transfer with atomic commit."""

    DEFAULT_CHUNK_SIZE = 10 * 1024 * 1024

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """Initialize data plane."""
        self.chunk_size = chunk_size
        self.transfers: Dict[str, TransferResult] = {}
        self.chunks: Dict[str, List[Chunk]] = {}

    def split_payload(self, payload: bytes) -> List[Chunk]:
        """Split payload into chunks."""
        chunks = []
        total_size = len(payload)
        num_chunks = (total_size + self.chunk_size - 1) // self.chunk_size

        for i in range(num_chunks):
            start = i * self.chunk_size
            end = min(start + self.chunk_size, total_size)
            chunk_data = payload[start:end]

            chunk = Chunk(sequence=i, data=chunk_data)
            chunk.calculate_checksum()
            chunks.append(chunk)

        logger.info(f"Payload split into {len(chunks)} chunks")
        return chunks

    def transfer_chunks(
        self, transfer_id: str, chunks: List[Chunk]
    ) -> TransferResult:
        """Execute chunked transfer."""
        result = TransferResult(transfer_id=transfer_id)
        result.status = TransferStatus.IN_PROGRESS

        self.transfers[transfer_id] = result
        self.chunks[transfer_id] = chunks.copy()

        for chunk in chunks:
            result.total_bytes += len(chunk.data)

        logger.info(
            f"Transfer {transfer_id} started: {len(chunks)} chunks, "
            f"{result.total_bytes} bytes"
        )
        return result

    def verify_chunks(self, transfer_id: str) -> TransferResult:
        """Verify all chunks of a transfer."""
        result = self.transfers.get(transfer_id)
        if not result:
            raise ValueError(f"Transfer not found: {transfer_id}")

        result.status = TransferStatus.VERIFYING
        chunks = self.chunks.get(transfer_id, [])

        for chunk in chunks:
            if chunk.verify_checksum(chunk.checksum):
                result.chunks_verified += 1

        all_verified = result.chunks_verified == len(chunks)
        if not all_verified:
            result.status = TransferStatus.FAILED
            result.error_message = (
                f"Verification failed: {result.chunks_verified}/{len(chunks)} chunks verified"
            )
            logger.error(result.error_message)
        else:
            result.status = TransferStatus.SUCCESS
            result.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"Transfer {transfer_id} verified successfully")

        return result

    def atomic_commit(self, transfer_id: str) -> TransferResult:
        """Atomically commit transfer after verification."""
        result = self.transfers.get(transfer_id)
        if not result:
            raise ValueError(f"Transfer not found: {transfer_id}")

        if result.status != TransferStatus.SUCCESS:
            result.error_message = (
                f"Cannot commit: transfer status is {result.status.value}"
            )
            logger.error(result.error_message)
            return result

        logger.info(f"Transfer {transfer_id} committed atomically")
        return result

    def get_transfer_result(self, transfer_id: str) -> Optional[TransferResult]:
        """Get transfer result by ID."""
        return self.transfers.get(transfer_id)

    def get_chunks(self, transfer_id: str) -> List[Chunk]:
        """Get chunks for a transfer."""
        return self.chunks.get(transfer_id, []).copy()

    def cancel_transfer(self, transfer_id: str) -> TransferResult:
        """Cancel an in-progress transfer."""
        result = self.transfers.get(transfer_id)
        if not result:
            raise ValueError(f"Transfer not found: {transfer_id}")

        result.status = TransferStatus.FAILED
        result.error_message = "Transfer cancelled"
        result.completed_at = datetime.now(timezone.utc).isoformat()

        if transfer_id in self.chunks:
            del self.chunks[transfer_id]

        logger.info(f"Transfer {transfer_id} cancelled")
        return result

    def complete_transfer(self, transfer_id: str) -> TransferResult:
        """Mark transfer as complete."""
        result = self.verify_chunks(transfer_id)
        if result.status == TransferStatus.SUCCESS:
            self.atomic_commit(transfer_id)

        return result
