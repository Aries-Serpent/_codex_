"""Test restore pipeline module 1."""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import List

import pytest


class RestorePhase(Enum):
    INITIAL = "initial"
    DISCOVERING = "discovering"
    VALIDATING = "validating"
    RESTORING = "restoring"
    VERIFIED = "verified"


class RestorePipeline:
    def __init__(self, name: str):
        self.name = name
        self.phase = RestorePhase.INITIAL
        self.artifacts: List[str] = []

    async def discover_artifacts(self) -> List[str]:
        self.phase = RestorePhase.DISCOVERING
        self.artifacts = ["artifact1", "artifact2"]
        return self.artifacts

    async def validate_artifacts(self) -> bool:
        self.phase = RestorePhase.VALIDATING
        return True

    async def restore(self) -> bool:
        self.phase = RestorePhase.RESTORING
        self.phase = RestorePhase.VERIFIED
        return True


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_restore_pipeline_1_init():
    """Test restore pipeline initialization."""
    pipeline = RestorePipeline("disaster_recovery_1")
    assert pipeline.name == "disaster_recovery_1", "name is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_restore_pipeline_1_discover():
    """Test artifact discovery."""
    pipeline = RestorePipeline("dr")
    artifacts = await asyncio.wait_for(pipeline.discover_artifacts(), timeout=30)

    assert len(artifacts) > 0, "Artifacts must not be empty"
    assert pipeline.phase == RestorePhase.DISCOVERING, "phase is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_restore_pipeline_1_validate():
    """Test artifact validation."""
    pipeline = RestorePipeline("dr")
    await asyncio.wait_for(pipeline.discover_artifacts(), timeout=30)
    result = await asyncio.wait_for(pipeline.validate_artifacts(), timeout=30)

    assert result is True, "Result must not be empty"
    assert pipeline.phase == RestorePhase.VALIDATING, "phase is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_restore_pipeline_1_restore():
    """Test pipeline restore."""
    pipeline = RestorePipeline("dr")
    await asyncio.wait_for(pipeline.discover_artifacts(), timeout=30)
    await asyncio.wait_for(pipeline.validate_artifacts(), timeout=30)
    result = await asyncio.wait_for(pipeline.restore(), timeout=30)

    assert result is True, "Result must not be empty"
    assert pipeline.phase == RestorePhase.VERIFIED, "phase is not valid"
