"""Pattern Discovery Skill Handler.

Discover, classify, and score recurring patterns in memory for promotion
to long-term storage. Supports decision, error, performance, success, and
risk patterns with improvement area tagging.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Any, Optional

from aries_serpent_core.brain.pattern_discovery import (
    PatternDiscovery,
    PatternType,
    ImprovementArea,
)

logger = logging.getLogger(__name__)


def run(
    *,
    memory_data: dict[str, Any],
    min_frequency: int = 2,
    min_confidence: float = 0.7,
    improvement_areas: Optional[list[str]] = None,
    limit: int = 50,
    **kwargs: Any,
) -> dict[str, Any]:
    """Discover and score patterns from memory data.

    Args:
        memory_data: Dictionary of memory entries (entries keyed by id).
        min_frequency: Minimum frequency threshold for pattern promotion.
        min_confidence: Minimum confidence score (0-1) for pattern inclusion.
        improvement_areas: Filter patterns by improvement area (optional).
        limit: Maximum number of patterns to return.
        **kwargs: Additional arguments (unused).

    Returns:
        Dictionary with discovered patterns, scores, promotion recommendations,
        and aggregated metrics.
    """
    try:
        discovery = PatternDiscovery()

        # Ingest memory data
        for entry_id, entry in memory_data.items():
            discovery.add_entry(entry_id, entry, source="memory_sync")

        # Discover patterns
        patterns = discovery.discover_patterns()

        # Score and filter patterns
        scored = [
            {
                "id": p.id,
                "name": p.name,
                "type": p.type.value,
                "frequency": p.frequency,
                "confidence": p.confidence,
                "improvement_area": p.improvement_area.value if p.improvement_area else None,
                "sample_entries": p.sample_entries[:3],
                "promotion_score": p.confidence * (p.frequency / max(p.frequency, 10)),
            }
            for p in patterns
            if p.frequency >= min_frequency
            and p.confidence >= min_confidence
            and (
                not improvement_areas
                or (p.improvement_area and p.improvement_area.value in improvement_areas)
            )
        ]

        # Sort by promotion score descending
        scored.sort(key=lambda p: p["promotion_score"], reverse=True)
        scored = scored[:limit]

        # Generate recommendations
        promoted = [p for p in scored if p["promotion_score"] >= 0.8]
        pending_review = [p for p in scored if 0.5 <= p["promotion_score"] < 0.8]

        return {
            "status": "ok",
            "data": {
                "patterns_discovered": len(scored),
                "patterns_promoted": len(promoted),
                "patterns_pending_review": len(pending_review),
                "total_memory_entries_analyzed": len(memory_data),
                "patterns": scored,
                "promoted": promoted,
                "pending_review": pending_review,
                "metrics": {
                    "avg_confidence": (
                        sum(p["confidence"] for p in scored) / len(scored)
                        if scored
                        else 0.0
                    ),
                    "avg_frequency": (
                        sum(p["frequency"] for p in scored) / len(scored)
                        if scored
                        else 0.0
                    ),
                    "coverage_pct": (len(scored) / max(len(memory_data), 1)) * 100,
                },
            },
        }
    except Exception as e:
        logger.exception("Pattern discovery failed: %s", e)
        return {
            "status": "error",
            "error": {
                "type": "discovery_error",
                "message": str(e),
            },
        }
