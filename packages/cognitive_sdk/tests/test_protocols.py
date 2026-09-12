from __future__ import annotations

import ast
from pathlib import Path

from codex_cognitive_sdk import GovernanceProtocol, MemoryProtocol, OODAProtocol

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class Policy:
    def evaluate(self, request: object) -> object:
        return request


class Memory:
    def store(self, record: object) -> None:
        pass

    def retrieve(self, query: object) -> tuple[object, ...]:
        return ()

    def delete(self, memory_id: str) -> bool:
        return False


class Planner:
    def observe(self, input_data: object) -> object:
        return input_data

    def orient(self, observation: object) -> object:
        return observation

    def decide(self, orientation: object) -> object:
        return orientation

    def act(self, decision: object) -> object:
        return decision


def test_protocols_are_structural() -> None:
    assert isinstance(Policy(), GovernanceProtocol)
    assert isinstance(Memory(), MemoryProtocol)
    assert isinstance(Planner(), OODAProtocol)


def test_package_has_no_monolith_or_third_party_imports() -> None:
    allowed = {
        "__future__",
        "dataclasses",
        "datetime",
        "importlib",
        "typing",
    }
    unexpected: list[str] = []
    for path in sorted((PACKAGE_ROOT / "src" / "codex_cognitive_sdk").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.partition(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = [node.module.partition(".")[0]]
            else:
                continue
            unexpected.extend(f"{path.name}: {root}" for root in roots if root not in allowed)

    assert not unexpected
