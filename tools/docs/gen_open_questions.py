"""Generate "Open Questions" documentation grouped by capability."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

SOURCE = Path("audit_artifacts/capabilities_scored.json")
TARGET = Path("docs/reference/open_questions_by_capability.md")


def generate() -> Path:
    data = json.loads(SOURCE.read_text(encoding="utf-8")) if SOURCE.exists() else {}
    by_capability: dict[str, list[str]] = defaultdict(list)
    for item in data.get("items", []):
        capability = item.get("capability")
        question = item.get("question")
        score = float(item.get("score", 1.0))
        open_flag = bool(item.get("open", False))
        if not capability or not question:
            continue
        if score < 0.95 or open_flag:
            by_capability[capability].append(str(question))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open("w", encoding="utf-8") as fh:
        if not by_capability:
            fh.write(
                "_No open questions fell below the 0.95 threshold or carried an explicit open flag._\n"
            )
        for capability, questions in sorted(by_capability.items()):
            fh.write(f"## {capability}\n")
            for question in questions:
                fh.write(f"- {question}\n")
            fh.write("\n")
    return TARGET


def main() -> None:
    path = generate()
    print(f"Wrote {path}")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
