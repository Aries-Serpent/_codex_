"""Test MCP checkpoint payload serialization."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class Checkpoint:
    checkpoint_id: str
    state: Dict[str, Any]
    metadata: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "Checkpoint":
        data = json.loads(json_str)
        return cls(
            checkpoint_id=data["checkpoint_id"], state=data["state"], metadata=data["metadata"]
        )


def test_checkpoint_serialization():
    """Test checkpoint to JSON."""
    checkpoint = Checkpoint(
        checkpoint_id="ckpt_001",
        state={"model": "weights", "epoch": 10},
        metadata={"timestamp": "2024-01-01", "version": "1.0"},
    )

    json_str = checkpoint.to_json()
    data = json.loads(json_str)

    assert data["checkpoint_id"] == "ckpt_001", "Data must not be empty"
    assert data["state"]["epoch"] == 10, "Data must not be empty"


def test_checkpoint_deserialization():
    """Test checkpoint from JSON."""
    json_str = """{"checkpoint_id": "ckpt_001", "state": {"model": "weights"}, "metadata": {"version": "1.0"}}"""

    checkpoint = Checkpoint.from_json(json_str)

    assert checkpoint.checkpoint_id == "ckpt_001", "checkpoint_id is not valid"
    assert checkpoint.state["model"] == "weights", "Condition must be true"


def test_checkpoint_roundtrip():
    """Test checkpoint serialization roundtrip."""
    original = Checkpoint(
        checkpoint_id="ckpt_002", state={"data": [1, 2, 3]}, metadata={"type": "training"}
    )

    json_str = original.to_json()
    restored = Checkpoint.from_json(json_str)

    assert restored.checkpoint_id == original.checkpoint_id, "checkpoint_id is not valid"
    assert restored.state == original.state, "state is not valid"
    assert restored.metadata == original.metadata, "Data must not be empty"


def test_checkpoint_with_nested_state():
    """Test checkpoint with nested state."""
    checkpoint = Checkpoint(
        checkpoint_id="ckpt_003",
        state={
            "model": {"layers": [{"weights": [0.1, 0.2]}, {"bias": [0.05]}]},
            "optimizer": {"lr": 0.001},
        },
        metadata={},
    )

    json_str = checkpoint.to_json()
    restored = Checkpoint.from_json(json_str)

    assert restored.state["model"]["layers"][0]["weights"] == [0.1, 0.2]
