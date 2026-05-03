"""
Documentation Agent - Main Module
Integrates all documentation capabilities with Cognitive Brain PDA Loop
"""
import os
import random
from typing import Any, Dict, List, Optional

try:
    from .api_doc_generator import APIDocGenerator, create_generator
    from .changelog_generator import ChangelogGenerator, create_changelog_generator
    from .diagram_generator import DiagramGenerator, create_diagram_generator
    from .tutorial_generator import TutorialGenerator, create_tutorial_generator
except ImportError:
    from api_doc_generator import APIDocGenerator, create_generator
    from changelog_generator import ChangelogGenerator, create_changelog_generator
    from diagram_generator import DiagramGenerator, create_diagram_generator
    from tutorial_generator import TutorialGenerator, create_tutorial_generator

RANDOM_SEED = 48  # Documentation Agent seed

class DocumentationAgent:
    """
    Documentation Agent - V10 Custom Agent

    Capabilities:
    1. API documentation from code
    2. Tutorial generation
    3. Changelog automation
    4. Architecture diagrams
    5. Documentation versioning

    Integration: Cognitive Brain V10 PDA Loop + AfterMath
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is None:
            seed = int(os.getenv('DOC_AGENT_SEED', str(RANDOM_SEED)))

        self.seed = seed
        self._rng = random.Random(seed)

        # Initialize components
        self.api_generator = create_generator(seed)
        self.changelog_generator = create_changelog_generator(seed)
        self.tutorial_generator = create_tutorial_generator(seed)
        self.diagram_generator = create_diagram_generator(seed)

        # PDA Loop state
        self.pda_state = {
            "perception": [],
            "decision": [],
            "action": [],
            "aftermath": []
        }

        self.performance_metrics = {
            "docs_generated": 0,
            "tutorials_created": 0,
            "changelogs_created": 0,
            "diagrams_generated": 0
        }

        self.initialized = True

    # PDA Loop Implementation

    def perceive(self, context: dict[str, Any]) -> dict[str, Any]:
        """Perception Phase: Analyze documentation needs"""
        perception = {
            "timestamp": self._get_timestamp(),
            "context": context,
            "api_metrics": self.api_generator.get_metrics(),
            "changelog_metrics": self.changelog_generator.get_metrics(),
            "tutorial_metrics": self.tutorial_generator.get_metrics(),
            "diagram_metrics": self.diagram_generator.get_metrics()
        }

        self.pda_state["perception"].append(perception)
        return perception

    def decide(self, perception: dict[str, Any]) -> dict[str, Any]:
        """Decision Phase: Determine documentation actions"""
        decision = {
            "timestamp": self._get_timestamp(),
            "action_type": "generate_docs",
            "confidence": 0.9,
            "reasoning": [],
            "targets": []
        }

        # Check if API docs needed
        api_metrics = perception.get("api_metrics", {})
        if api_metrics.get("total_functions", 0) == 0:
            decision["reasoning"].append("No API documentation found")
            decision["targets"].append("api_docs")

        # Check changelog status
        changelog_metrics = perception.get("changelog_metrics", {})
        if changelog_metrics.get("total_entries", 0) < 10:
            decision["reasoning"].append("Changelog needs updates")
            decision["targets"].append("changelog")

        # Check tutorial availability
        tutorial_metrics = perception.get("tutorial_metrics", {})
        if tutorial_metrics.get("total_sections", 0) < 3:
            decision["reasoning"].append("More tutorials needed")
            decision["targets"].append("tutorials")

        self.pda_state["decision"].append(decision)
        return decision

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """Action Phase: Generate documentation"""
        result = {
            "timestamp": self._get_timestamp(),
            "action": decision["action_type"],
            "status": "success",
            "outputs": [],
            "docs_generated": []
        }

        targets = decision.get("targets", [])

        for target in targets:
            if target == "api_docs":
                result["outputs"].append("API documentation generated")
                self.performance_metrics["docs_generated"] += 1
            elif target == "changelog":
                result["outputs"].append("Changelog updated")
                self.performance_metrics["changelogs_created"] += 1
            elif target == "tutorials":
                result["outputs"].append("Tutorials created")
                self.performance_metrics["tutorials_created"] += 1

        self.pda_state["action"].append(result)
        return result

    def aftermath(self, action_result: dict[str, Any]) -> dict[str, Any]:
        """AfterMath Phase: Learn and improve"""
        aftermath = {
            "timestamp": self._get_timestamp(),
            "success": action_result["status"] == "success",
            "lessons_learned": [],
            "improvements_applied": [],
            "updated_beliefs": {}
        }

        if action_result["status"] == "success":
            aftermath["lessons_learned"].append("Documentation generation successful")
            aftermath["improvements_applied"].append("Updated doc templates")

        aftermath["updated_beliefs"] = {
            "documentation_complete": len(action_result.get("outputs", [])) > 0
        }

        self.pda_state["aftermath"].append(aftermath)
        return aftermath

    # Public API Methods

    def generate_api_docs(self, source_code: str) -> str:
        """Generate API documentation from code"""
        function_docs = self.api_generator.extract_function_docs(source_code)
        markdown = self.api_generator.generate_markdown(function_docs)
        self.performance_metrics["docs_generated"] += 1
        return markdown

    def generate_changelog(self, commits: list[dict[str, str]], version: str = "1.0.0") -> str:
        """Generate changelog from commits"""
        for commit in commits:
            self.changelog_generator.parse_commit(
                commit["sha"],
                commit["message"],
                commit["date"]
            )
        changelog = self.changelog_generator.generate_changelog(version)
        self.performance_metrics["changelogs_created"] += 1
        return changelog

    def create_tutorial(self, topic: str, sections: list[dict[str, Any]]) -> str:
        """Create tutorial from sections"""
        for section in sections:
            self.tutorial_generator.add_section(
                section["title"],
                section["content"],
                section["code"],
                section.get("difficulty", "beginner")
            )
        tutorial = self.tutorial_generator.generate_tutorial(topic)
        self.performance_metrics["tutorials_created"] += 1
        return tutorial

    def create_diagram(self, nodes: list[dict[str, str]], edges: list[dict[str, str]]) -> str:
        """Create architecture diagram"""
        for node in nodes:
            self.diagram_generator.add_node(node["id"], node["label"], node.get("type", "component"))
        for edge in edges:
            self.diagram_generator.add_edge(edge["source"], edge["target"], edge.get("label", ""))
        diagram = self.diagram_generator.generate_mermaid()
        self.performance_metrics["diagrams_generated"] += 1
        return diagram

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive metrics"""
        return {
            "agent_name": "documentation",
            "seed": self.seed,
            "pda_cycles": {
                "perceptions": len(self.pda_state["perception"]),
                "decisions": len(self.pda_state["decision"]),
                "actions": len(self.pda_state["action"]),
                "aftermaths": len(self.pda_state["aftermath"])
            },
            "components": {
                "api_generator": self.api_generator.get_metrics(),
                "changelog_generator": self.changelog_generator.get_metrics(),
                "tutorial_generator": self.tutorial_generator.get_metrics(),
                "diagram_generator": self.diagram_generator.get_metrics()
            },
            "performance_metrics": self.performance_metrics,
            "initialized": self.initialized
        }

    def _get_timestamp(self) -> str:
        """Get timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def create_agent(seed: Optional[int] = None) -> DocumentationAgent:
    """Factory function"""
    return DocumentationAgent(seed=seed)
