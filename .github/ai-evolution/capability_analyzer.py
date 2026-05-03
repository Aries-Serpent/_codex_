"""
AI Agent Capability Gap Analyzer

Analyzes agent interactions and limitations to identify tooling opportunities.
This enables AI agents to detect patterns where custom tools would improve efficiency.

Author: mbaetiong
Generated: 2025-12-21
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CapabilityGap:
    """Represents a detected capability gap that could be addressed with tooling."""
    gap_id: str
    category: str
    description: str
    frequency: int
    impact_score: float
    current_workaround: Optional[str]
    proposed_tool: Optional[dict[str, Any]]
    examples: list[dict[str, Any]] = field(default_factory=list)
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ToolOpportunity:
    """Represents an opportunity to create a new tool."""
    opportunity_id: str
    gap_id: str
    tool_type: str
    estimated_complexity: float  # 0.0 to 1.0
    potential_impact: float  # 0.0 to 1.0
    reusability_score: float  # 0.0 to 1.0
    implementation_sketch: str
    dependencies: list[str] = field(default_factory=list)
    priority_score: float = 0.0  # Calculated from impact and complexity


class CapabilityGapAnalyzer:
    """Analyzes agent interactions to identify tooling opportunities."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize the analyzer.

        Args:
            storage_path: Path to store analysis results (defaults to .github/ai-evolution/data)
        """
        self.storage_path = storage_path or Path(".github/ai-evolution/data")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.interaction_log: list[dict[str, Any]] = []
        self.pattern_memory: dict[str, list[dict]] = defaultdict(list)
        self.gap_registry: dict[str, CapabilityGap] = {}
        self.tool_opportunities: list[ToolOpportunity] = []

        # Load existing data
        self._load_state()

    def analyze_interaction(self, interaction: dict[str, Any]) -> list[CapabilityGap]:
        """Analyze a single interaction for capability gaps.

        Args:
            interaction: Dict containing interaction data with keys:
                - action: The action performed
                - duration: Time taken
                - success: Whether it succeeded
                - pattern_type: Type of pattern (optional)
                - operation_type: Type of operation (optional)
                - domain: Knowledge domain (optional)

        Returns:
            List of detected capability gaps
        """
        gaps = []

        # Pattern: Repetitive code generation
        if self._detect_repetition(interaction):
            gap = CapabilityGap(
                gap_id=self._generate_gap_id("repetition", interaction),
                category="code_generation",
                description="Repetitive pattern detected that could be templated",
                frequency=self._count_pattern_frequency(interaction),
                impact_score=self._calculate_impact(interaction),
                current_workaround="Manual generation each time",
                proposed_tool={
                    "type": "template_generator",
                    "name": f"Template_{interaction.get('pattern_type', 'generic')}",
                    "parameters": self._extract_template_params(interaction),
                },
                examples=[interaction],
            )
            gaps.append(gap)

        # Pattern: Complex multi-step operations
        if self._detect_complex_sequence(interaction):
            gap = CapabilityGap(
                gap_id=self._generate_gap_id("complexity", interaction),
                category="orchestration",
                description="Complex operation that could be automated",
                frequency=1,
                impact_score=min(interaction.get("duration", 0) * 0.1, 1.0),
                current_workaround="Manual step-by-step execution",
                proposed_tool={
                    "type": "orchestrator",
                    "name": f"Orchestrator_{interaction.get('operation_type', 'generic')}",
                    "steps": self._extract_operation_steps(interaction),
                },
            )
            gaps.append(gap)

        # Pattern: Missing context or knowledge
        if self._detect_knowledge_gap(interaction):
            gap = CapabilityGap(
                gap_id=self._generate_gap_id("knowledge", interaction),
                category="knowledge_base",
                description="Missing knowledge that required external lookup",
                frequency=self._count_knowledge_requests(interaction),
                impact_score=0.7,
                current_workaround="Manual search or user input",
                proposed_tool={
                    "type": "knowledge_extractor",
                    "domain": interaction.get("domain", "general"),
                    "sources": self._identify_knowledge_sources(interaction),
                },
            )
            gaps.append(gap)

        # Store interaction for pattern learning
        self.interaction_log.append(interaction)

        # Register gaps
        for gap in gaps:
            if gap.gap_id in self.gap_registry:
                # Update existing gap
                existing = self.gap_registry[gap.gap_id]
                existing.frequency += 1
                existing.examples.append(interaction)
            else:
                self.gap_registry[gap.gap_id] = gap

        # Save state periodically
        if len(self.interaction_log) % 10 == 0:
            self._save_state()

        return gaps

    def _generate_gap_id(self, gap_type: str, interaction: dict) -> str:
        """Generate unique ID for a gap."""
        content = f"{gap_type}_{interaction.get('action', '')}_{interaction.get('pattern_type', '')}"
        return f"gap_{gap_type}_{hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:8]}"  # nosec B324 - Not for security, gap ID generation only

    def _detect_repetition(self, interaction: dict) -> bool:
        """Detect if interaction shows repetitive pattern."""
        action = interaction.get("action", "")
        pattern_type = interaction.get("pattern_type", "")

        # Check if similar actions have been performed before
        similar_actions = [
            log for log in self.interaction_log[-50:]  # Check last 50 interactions
            if log.get("action") == action and log.get("pattern_type") == pattern_type
        ]

        return len(similar_actions) >= 3

    def _detect_complex_sequence(self, interaction: dict) -> bool:
        """Detect if interaction represents complex multi-step operation."""
        # Consider it complex if:
        # - Duration is high
        # - Has multiple steps
        # - Operation type indicates complexity
        duration = interaction.get("duration", 0)
        steps = interaction.get("steps", [])
        operation_type = interaction.get("operation_type", "")

        return (
            duration > 60 or  # More than 1 minute
            len(steps) > 5 or  # More than 5 steps
            "complex" in operation_type.lower() or
            "multi" in operation_type.lower()
        )

    def _detect_knowledge_gap(self, interaction: dict) -> bool:
        """Detect if interaction shows missing knowledge."""
        # Indicators of knowledge gaps:
        # - Requires external lookup
        # - User had to provide context
        # - Multiple retries
        return (
            interaction.get("required_lookup", False) or
            interaction.get("user_context_needed", False) or
            interaction.get("retry_count", 0) > 2
        )

    def _count_pattern_frequency(self, interaction: dict) -> int:
        """Count how often this pattern has occurred."""
        pattern_type = interaction.get("pattern_type", "")
        if not pattern_type:
            return 1

        return len(self.pattern_memory.get(pattern_type, [])) + 1

    def _calculate_impact(self, interaction: dict) -> float:
        """Calculate impact score for a gap (0.0 to 1.0)."""
        # Factors: duration, frequency, complexity
        duration_score = min(interaction.get("duration", 0) / 300, 1.0)  # Normalize to 5 minutes
        frequency = self._count_pattern_frequency(interaction)
        frequency_score = min(frequency / 10, 1.0)  # Normalize to 10 occurrences

        # Weight: 40% duration, 60% frequency
        return (duration_score * 0.4) + (frequency_score * 0.6)

    def _extract_template_params(self, interaction: dict) -> dict[str, Any]:
        """Extract parameters that could be used in a template."""
        return {
            "pattern_type": interaction.get("pattern_type", ""),
            "common_params": interaction.get("parameters", {}),
            "output_format": interaction.get("output_format", ""),
        }

    def _extract_operation_steps(self, interaction: dict) -> list[str]:
        """Extract steps from a complex operation."""
        return interaction.get("steps", [])

    def _count_knowledge_requests(self, interaction: dict) -> int:
        """Count knowledge lookup requests."""
        return interaction.get("lookup_count", 1)

    def _identify_knowledge_sources(self, interaction: dict) -> list[str]:
        """Identify sources of knowledge that were needed."""
        return interaction.get("knowledge_sources", ["documentation", "codebase"])

    def synthesize_tool_opportunities(self) -> list[ToolOpportunity]:
        """Synthesize tool opportunities from detected gaps.

        Returns:
            List of tool opportunities, ranked by priority (ROI)
        """
        opportunities = []

        # Group similar gaps
        gap_clusters = self._cluster_gaps()

        for cluster_id, gaps in gap_clusters.items():
            # Only create tools for frequently occurring gaps
            if len(gaps) >= 2 or any(gap.frequency >= 3 for gap in gaps):
                opportunity = self._create_tool_opportunity(cluster_id, gaps)
                opportunities.append(opportunity)

        # Calculate priority scores (ROI: impact / complexity)
        for opp in opportunities:
            opp.priority_score = opp.potential_impact / max(opp.estimated_complexity, 0.1)

        # Rank by priority
        opportunities.sort(key=lambda x: x.priority_score, reverse=True)

        self.tool_opportunities = opportunities
        self._save_state()

        return opportunities

    def _cluster_gaps(self) -> dict[str, list[CapabilityGap]]:
        """Cluster similar gaps together."""
        clusters: dict[str, list[CapabilityGap]] = defaultdict(list)

        for gap in self.gap_registry.values():
            # Cluster by category
            clusters[gap.category].append(gap)

        return dict(clusters)

    def _create_tool_opportunity(
        self,
        cluster_id: str,
        gaps: list[CapabilityGap],
    ) -> ToolOpportunity:
        """Create a tool opportunity from a cluster of gaps."""
        # Determine tool type based on gap categories
        primary_gap = max(gaps, key=lambda g: g.impact_score * g.frequency)

        tool_types = {
            "code_generation": "generator",
            "orchestration": "workflow",
            "knowledge_base": "extractor",
            "analysis": "analyzer",
            "transformation": "transformer",
        }

        tool_type = tool_types.get(primary_gap.category, "utility")

        # Calculate metrics
        total_impact = sum(gap.impact_score * gap.frequency for gap in gaps)
        complexity = self._estimate_complexity(gaps)
        reusability = self._calculate_reusability(gaps)

        # Generate implementation sketch
        sketch = self._generate_implementation_sketch(gaps, tool_type)

        return ToolOpportunity(
            opportunity_id=f"opp_{cluster_id}_{len(self.tool_opportunities)}",
            gap_id=primary_gap.gap_id,
            tool_type=tool_type,
            estimated_complexity=complexity,
            potential_impact=min(total_impact, 1.0),
            reusability_score=reusability,
            implementation_sketch=sketch,
            dependencies=self._identify_dependencies(sketch),
        )

    def _estimate_complexity(self, gaps: list[CapabilityGap]) -> float:
        """Estimate implementation complexity (0.0 to 1.0)."""
        # More gaps = more complex to unify
        # More examples = more edge cases
        gap_count_factor = min(len(gaps) / 10, 1.0)
        example_count = sum(len(gap.examples) for gap in gaps)
        example_factor = min(example_count / 50, 1.0)

        return (gap_count_factor * 0.5) + (example_factor * 0.5)

    def _calculate_reusability(self, gaps: list[CapabilityGap]) -> float:
        """Calculate reusability score (0.0 to 1.0)."""
        # Higher frequency = more reusable
        # More examples = more generalizable
        total_frequency = sum(gap.frequency for gap in gaps)
        total_examples = sum(len(gap.examples) for gap in gaps)

        frequency_score = min(total_frequency / 20, 1.0)
        example_score = min(total_examples / 30, 1.0)

        return (frequency_score * 0.6) + (example_score * 0.4)

    def _generate_implementation_sketch(
        self,
        gaps: list[CapabilityGap],
        tool_type: str,
    ) -> str:
        """Generate initial implementation sketch for a tool."""
        primary_gap = gaps[0]

        return f"""
# Tool Implementation Sketch: {tool_type.title()}Tool
# Purpose: {primary_gap.description}
# Addresses {len(gaps)} capability gap(s)

class {tool_type.title()}Tool:
    '''Generated tool to address: {primary_gap.description}'''

    def __init__(self):
        self.config = {primary_gap.proposed_tool}
        self.usage_count = 0
        self.success_rate = 1.0

    def execute(self, context):
        '''Main execution method'''
        self.usage_count += 1

        # Implementation based on gap analysis
        # TODO: Implement specific logic for {tool_type}

        return result

    def learn_from_feedback(self, feedback):
        '''Improve based on usage'''
        # Update internal state based on success/failure
        pass
"""

    def _identify_dependencies(self, sketch: str) -> list[str]:
        """Identify dependencies from implementation sketch."""
        # Simple heuristic: look for common imports that would be needed
        dependencies = []

        if "async" in sketch:
            dependencies.append("asyncio")
        if "json" in sketch.lower():
            dependencies.append("json")
        if "http" in sketch.lower() or "api" in sketch.lower():
            dependencies.append("aiohttp")

        return dependencies

    def get_status_summary(self) -> dict[str, Any]:
        """Get summary of analyzer status."""
        return {
            "total_interactions": len(self.interaction_log),
            "detected_gaps": len(self.gap_registry),
            "tool_opportunities": len(self.tool_opportunities),
            "high_priority_opportunities": len([
                opp for opp in self.tool_opportunities
                if opp.priority_score > 0.7
            ]),
            "categories": list(set(gap.category for gap in self.gap_registry.values())),
        }

    def _save_state(self):
        """Save analyzer state to disk."""
        try:
            state = {
                "gaps": {
                    gap_id: {
                        "gap_id": gap.gap_id,
                        "category": gap.category,
                        "description": gap.description,
                        "frequency": gap.frequency,
                        "impact_score": gap.impact_score,
                        "detected_at": gap.detected_at,
                    }
                    for gap_id, gap in self.gap_registry.items()
                },
                "opportunities": [
                    {
                        "opportunity_id": opp.opportunity_id,
                        "tool_type": opp.tool_type,
                        "priority_score": opp.priority_score,
                        "potential_impact": opp.potential_impact,
                        "estimated_complexity": opp.estimated_complexity,
                    }
                    for opp in self.tool_opportunities
                ],
                "summary": self.get_status_summary(),
            }

            with open(self.storage_path / "analyzer_state.json", "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save analyzer state: {e}")

    def _load_state(self):
        """Load analyzer state from disk."""
        state_file = self.storage_path / "analyzer_state.json"
        if not state_file.exists():
            return

        try:
            with open(state_file) as f:
                state = json.load(f)

            # Restore gaps (simplified - full restoration would need dataclass reconstruction)
            logger.info(f"Loaded {len(state.get('gaps', {}))} gaps from previous session")

        except Exception as e:
            logger.warning(f"Failed to load analyzer state: {e}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    analyzer = CapabilityGapAnalyzer()

    # Example interaction
    interaction = {
        "action": "generate_test_file",
        "duration": 45,
        "pattern_type": "unit_test",
        "success": True,
        "parameters": {"framework": "pytest", "coverage": True},
    }

    gaps = analyzer.analyze_interaction(interaction)
    print(f"Detected {len(gaps)} gaps")

    opportunities = analyzer.synthesize_tool_opportunities()
    print(f"\nTool Opportunities: {len(opportunities)}")

    for opp in opportunities[:3]:
        print(f"\n  Priority: {opp.priority_score:.2f}")
        print(f"  Type: {opp.tool_type}")
        print(f"  Impact: {opp.potential_impact:.2f}")
        print(f"  Complexity: {opp.estimated_complexity:.2f}")

    print(f"\nStatus: {json.dumps(analyzer.get_status_summary(), indent=2)}")
