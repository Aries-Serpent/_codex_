"""
Tutorial Generator for Documentation Agent
Creates tutorials from usage patterns and examples
"""
import random
from dataclasses import dataclass
from typing import Any

RANDOM_SEED = 48

@dataclass
class TutorialSection:
    """Tutorial section"""
    title: str
    content: str
    code_example: str
    difficulty: str  # beginner, intermediate, advanced

class TutorialGenerator:
    """Generate tutorials from usage patterns"""

    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.sections: list[TutorialSection] = []
        self.initialized = True

    def add_section(self, title: str, content: str, code: str, difficulty: str = "beginner") -> TutorialSection:
        """Add tutorial section"""
        section = TutorialSection(
            title=title,
            content=content,
            code_example=code,
            difficulty=difficulty
        )
        self.sections.append(section)
        return section

    def generate_tutorial(self, topic: str) -> str:
        """Generate complete tutorial"""
        if not self.sections:
            return f"# {topic} Tutorial\n\nNo sections available.\n"

        tutorial = f"# {topic} Tutorial\n\n"
        tutorial += f"**Difficulty**: {self._get_overall_difficulty()}\n\n"
        tutorial += "## Table of Contents\n\n"

        for i, section in enumerate(self.sections, 1):
            tutorial += f"{i}. [{section.title}](#{section.title.lower().replace(' ', '-')})\n"

        tutorial += "\n---\n\n"

        for section in self.sections:
            tutorial += f"## {section.title}\n\n"
            tutorial += f"**Difficulty**: {section.difficulty}\n\n"
            tutorial += f"{section.content}\n\n"
            tutorial += "### Example\n\n"
            tutorial += f"```python\n{section.code_example}\n```\n\n"
            tutorial += "---\n\n"

        return tutorial

    def _get_overall_difficulty(self) -> str:
        """Calculate overall difficulty"""
        if not self.sections:
            return "beginner"
        difficulties = [s.difficulty for s in self.sections]
        if "advanced" in difficulties:
            return "advanced"
        if "intermediate" in difficulties:
            return "intermediate"
        return "beginner"

    def get_metrics(self) -> dict[str, Any]:
        """Get metrics"""
        return {
            "seed": self.seed,
            "total_sections": len(self.sections),
            "difficulty_distribution": {
                "beginner": sum(1 for s in self.sections if s.difficulty == "beginner"),
                "intermediate": sum(1 for s in self.sections if s.difficulty == "intermediate"),
                "advanced": sum(1 for s in self.sections if s.difficulty == "advanced")
            },
            "initialized": self.initialized
        }

def create_tutorial_generator(seed: int = RANDOM_SEED) -> TutorialGenerator:
    """Factory function"""
    return TutorialGenerator(seed=seed)
