#!/usr/bin/env python3
"""Generate scaffolds for Zendesk desired state files."""

from __future__ import annotations

import json
from pathlib import Path


def prompt_trigger() -> dict[str, object]:
    name = input("Trigger name: ")
    category = input("Category: ")
    position = int(input("Position (integer): "))
    conditions: dict[str, list[dict[str, str]]] = {"all": []}
    while True:
        add_cond = input("Add condition? (y/n): ").strip().lower()
        if add_cond != "y":
            break
        field = input("  Field: ")
        operator = input("  Operator: ")
        value = input("  Value: ")
        conditions.setdefault("all", []).append(
            {"field": field, "operator": operator, "value": value}
        )
    actions: list[dict[str, str]] = []
    while True:
        add_action = input("Add action? (y/n): ").strip().lower()
        if add_action != "y":
            break
        field = input("  Action field: ")
        value = input("  Action value: ")
        actions.append({"field": field, "value": value})
    return {
        "name": name,
        "category": category,
        "conditions": conditions,
        "actions": actions,
        "position": position,
    }


def main() -> None:
    base_dir = Path("configs/desired")
    base_dir.mkdir(parents=True, exist_ok=True)
    triggers: list[dict[str, object]] = []
    while True:
        add_trig = input("Create a new trigger? (y/n): ").strip().lower()
        if add_trig != "y":
            break
        triggers.append(prompt_trigger())
    target = base_dir / "triggers.json"
    target.write_text(json.dumps(triggers, indent=2), encoding="utf-8")
    print(f"Wrote {len(triggers)} triggers to {target}")


if __name__ == "__main__":
    main()
