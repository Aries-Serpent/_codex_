"""
Changelog Generator for Documentation Agent
Automatically generates changelogs from git commit history
"""
import random
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

RANDOM_SEED = 48

@dataclass
class ChangelogEntry:
    """Single changelog entry"""
    commit_sha: str
    date: str
    category: str  # feat, fix, docs, refactor, test, chore
    scope: Optional[str]
    message: str
    breaking: bool

class ChangelogGenerator:
    """Generate changelogs from commit messages"""

    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.entries: list[ChangelogEntry] = []
        self.initialized = True

    def parse_commit(self, commit_sha: str, message: str, date: str) -> Optional[ChangelogEntry]:
        """Parse conventional commit message"""
        # Pattern: type(scope): message
        pattern = r'^(feat|fix|docs|refactor|test|chore|perf|style)(?:\(([^)]+)\))?: (.+)$'
        match = re.match(pattern, message.strip(), re.MULTILINE)

        if not match:
            return None

        category = match.group(1)
        scope = match.group(2)
        msg = match.group(3)
        breaking = "BREAKING" in message or "!" in message

        entry = ChangelogEntry(
            commit_sha=commit_sha,
            date=date,
            category=category,
            scope=scope,
            message=msg,
            breaking=breaking
        )

        self.entries.append(entry)
        return entry

    def generate_changelog(self, version: str = "1.0.0") -> str:
        """Generate changelog in Keep a Changelog format"""
        if not self.entries:
            return f"# Changelog\n\n## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\nNo changes recorded.\n"

        # Group by category
        categories = {
            "feat": "Added",
            "fix": "Fixed",
            "docs": "Documentation",
            "refactor": "Changed",
            "perf": "Performance",
            "test": "Testing",
            "chore": "Maintenance"
        }

        grouped = {}
        breaking_changes = []

        for entry in self.entries:
            if entry.breaking:
                breaking_changes.append(entry)

            category_name = categories.get(entry.category, "Other")
            if category_name not in grouped:
                grouped[category_name] = []
            grouped[category_name].append(entry)

        # Generate markdown
        changelog = f"# Changelog\n\n## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"

        # Breaking changes first
        if breaking_changes:
            changelog += "### ⚠️ BREAKING CHANGES\n\n"
            for entry in breaking_changes:
                scope_str = f"**{entry.scope}**: " if entry.scope else ""
                changelog += f"- {scope_str}{entry.message} ({entry.commit_sha[:7]})\n"
            changelog += "\n"

        # Other categories
        for category_name in ["Added", "Fixed", "Changed", "Performance", "Documentation"]:
            if category_name in grouped:
                changelog += f"### {category_name}\n\n"
                for entry in grouped[category_name]:
                    if not entry.breaking:
                        scope_str = f"**{entry.scope}**: " if entry.scope else ""
                        changelog += f"- {scope_str}{entry.message} ({entry.commit_sha[:7]})\n"
                changelog += "\n"

        return changelog

    def get_metrics(self) -> dict[str, Any]:
        """Get generator metrics"""
        return {
            "seed": self.seed,
            "total_entries": len(self.entries),
            "breaking_changes": sum(1 for e in self.entries if e.breaking),
            "categories": {cat: sum(1 for e in self.entries if e.category == cat)
                          for cat in ["feat", "fix", "docs", "refactor"]},
            "initialized": self.initialized
        }

def create_changelog_generator(seed: int = RANDOM_SEED) -> ChangelogGenerator:
    """Factory function"""
    return ChangelogGenerator(seed=seed)
