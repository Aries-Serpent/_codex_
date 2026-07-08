"""Campaign Framework for orchestrating multi-phase workflows with parallel agent delegation."""

from .orchestrator import (
    CampaignDefinition,
    CampaignExecution,
    CampaignOrchestrator,
    CampaignPhase,
    CampaignRegistryLoader,
    CampaignStatus,
    PhaseExecutionResult,
)

__all__ = [
    "CampaignDefinition",
    "CampaignExecution",
    "CampaignOrchestrator",
    "CampaignPhase",
    "CampaignRegistryLoader",
    "CampaignStatus",
    "PhaseExecutionResult",
]
