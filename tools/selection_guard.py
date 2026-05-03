#!/usr/bin/env python
"""Selection Guard: verify the chosen assistant message includes required docs surface + guardrails.

Inputs:
  --rules: JSON config listing required_signals, optional_signals, and path_hints to find diffs/messages.
  --input: A project summary / response log JSON (e.g., summary-02.json).
  --selected: Optional candidate index (1..n) to assert your current choice.

Behavior:
  - Locates the 'owner' turn with four assistant siblings via the path hint
    (e.g., turn_mapping.task_e_*~*.turn.worklog.messages[*]) or falls back to sibling turns.
  - For each candidate, extracts diff/message via path_hints and scans for required_signals.
  - Prints a ranked table and returns:
      0 if --selected provided and that candidate satisfies all required signals,
      1 if --selected provided but does not satisfy all required signals,
      2 if no candidate satisfies all required signals.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Candidate:
    idx: int
    turn_id: str
    payload: str
    hits: list[str]
    missing: list[str]


def _read_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_rules(path: str) -> dict[str, Any]:
    obj = _read_json(path)
    if "required_signals" not in obj or not isinstance(obj["required_signals"], list):
        raise ValueError("rules file missing 'required_signals' list")
    obj.setdefault("optional_signals", [])
    obj.setdefault("path_hints", ["output_diff.diff", "pr.output_diff.diff", "pr_message", "diff"])
    return obj


def _path_variants(path: Iterable[str]) -> list[str]:
    parts = list(path)
    if not parts:
        return [""]
    variants = [".".join(parts)]
    merged: list[str] = []
    for component in parts:
        if component.isdigit() and merged:
            merged[-1] = f"{merged[-1]}[{component}]"
        else:
            merged.append(component)
    bracketed = ".".join(merged)
    if bracketed and bracketed not in variants:
        variants.append(bracketed)
    return [variant for variant in variants if variant]


def _normalize_pattern(pattern: str) -> str:
    return pattern.replace("[*]", ".*")


def _glob_first(d: dict[str, Any], pattern: str) -> Optional[tuple[str, Any]]:
    """Depth-first search over nested structures returning first key path matching pattern."""
    pattern = _normalize_pattern(pattern)
    stack: list[tuple[list[str], Any]] = [([], d)]
    while stack:
        path, cur = stack.pop()
        if isinstance(cur, dict):
            for key, val in cur.items():
                new_path = path + [key]
                for candidate in _path_variants(new_path):
                    if fnmatch.fnmatch(candidate, pattern):
                        return candidate, val
                stack.append((new_path, val))
        elif isinstance(cur, list):
            for idx, val in enumerate(cur):
                new_path = path + [str(idx)]
                for candidate in _path_variants(new_path):
                    if fnmatch.fnmatch(candidate, pattern):
                        return candidate, val
                stack.append((new_path, val))
    return None


def _glob_all(d: dict[str, Any], pattern: str) -> list[tuple[str, Any]]:
    """Return all key paths matching pattern in traversal order."""
    pattern = _normalize_pattern(pattern)
    matches: list[tuple[str, Any]] = []

    def _visit(path: list[str], cur: Any) -> None:
        for candidate in _path_variants(path):
            if candidate and fnmatch.fnmatch(candidate, pattern):
                matches.append((candidate, cur))
                break
        if isinstance(cur, dict):
            for key, val in cur.items():
                _visit(path + [key], val)
        elif isinstance(cur, list):
            for idx, val in enumerate(cur):
                _visit(path + [str(idx)], val)

    _visit([], d)
    return matches


def _extract_siblings(tm: dict[str, Any]) -> list[str]:
    owners = [key for key in tm if key.startswith("task_e_") and "~" in key]
    if not owners:
        owners = [
            key for key, value in tm.items() if isinstance(value, dict) and "children" in value
        ]
    if not owners:
        return []
    owner = owners[0]
    children = tm.get(owner, {}).get("children", [])
    return children if isinstance(children, list) else []


def _resolve_turn_id(node: Any) -> Optional[str]:
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return None
    for key in ("turn_id", "id", "message_id"):
        value = node.get(key)
        if isinstance(value, str):
            return value
    turn = node.get("turn")
    if isinstance(turn, dict):
        for key in ("turn_id", "id"):
            value = turn.get(key)
            if isinstance(value, str):
                return value
    return None


def _extract_turn_obj(entry: Any) -> dict[str, Any]:
    if isinstance(entry, dict):
        turn = entry.get("turn")
        if isinstance(turn, dict):
            return turn
        return entry
    return {}


def _extract_payload(turn_obj: dict[str, Any], path_hints: list[str]) -> str:
    for hint in path_hints:
        hit = _glob_first(turn_obj, hint)
        if hit and isinstance(hit[1], str):
            return hit[1]
    payloads: list[str] = []
    for hint in ("diff", "pr_message", "message_text"):
        hit = _glob_first(turn_obj, f"*{hint}")
        if hit and isinstance(hit[1], str):
            payloads.append(hit[1])
    return "\n\n".join(payloads)


def _scan_payload(payload: str, required: list[str]) -> tuple[list[str], list[str]]:
    hits: list[str] = []
    missing: list[str] = []
    lowered = payload.lower()
    for signal in required:
        if signal.lower() in lowered:
            hits.append(signal)
        else:
            missing.append(signal)
    return hits, missing


def _iter_candidates(data: dict[str, Any], rules: dict[str, Any]) -> list[Candidate]:
    tm = data.get("turn_mapping", {})
    selection_hint = rules.get("selection_path_hint")
    candidate_ids: list[str] = []
    candidate_turns: list[dict[str, Any]] = []

    if selection_hint:
        for path, node in _glob_all(data, selection_hint):
            turn_id = _resolve_turn_id(node)
            turn_info = tm.get(turn_id, {}) if turn_id else {}
            turn_obj = _extract_turn_obj(turn_info)
            if not turn_obj and isinstance(node, dict):
                turn_obj = _extract_turn_obj(node)
            if not turn_obj:
                continue
            candidate_ids.append(turn_id or path)
            candidate_turns.append(turn_obj)

    if not candidate_ids:
        siblings = _extract_siblings(tm)
        for turn_id in siblings:
            turn_info = tm.get(turn_id, {})
            turn_obj = _extract_turn_obj(turn_info)
            candidate_ids.append(turn_id)
            candidate_turns.append(turn_obj)

    candidates: list[Candidate] = []
    seen: set[str] = set()
    display_idx = 1
    for turn_id, turn_obj in zip(candidate_ids, candidate_turns):
        if turn_id in seen:
            continue
        seen.add(turn_id)
        payload = _extract_payload(turn_obj, rules["path_hints"])
        hits, missing = _scan_payload(payload, rules["required_signals"])
        candidates.append(Candidate(display_idx, turn_id, payload, hits, missing))
        display_idx += 1
    return candidates


def _print_table(candidates: list[Candidate], optional: list[str]) -> None:
    print("== Selection Guard Report ==")
    print("idx | req_hits/total | opt_hits | status")
    print("----+---------------+----------+--------")
    for cand in candidates:
        opt_hits = sum(1 for sig in optional if sig.lower() in cand.payload.lower())
        status = "OK" if not cand.missing else "MISSING"
        print(
            f"{cand.idx:>3} | {len(cand.hits):>3}/{len(cand.hits)+len(cand.missing):<9} | {opt_hits:>8} | {status}"
        )
        if cand.missing:
            print(f"     missing: {', '.join(cand.missing)}")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify docs surface + guardrails on selected assistant message."
    )
    parser.add_argument("--rules", required=True, help="Path to selection_guard_rules.json")
    parser.add_argument("--input", required=True, help="Path to summary JSON containing candidates")
    parser.add_argument(
        "--selected", type=int, default=None, help="Chosen candidate index (1..n) to assert"
    )
    args = parser.parse_args(argv)

    rules = _read_rules(args.rules)
    data = _read_json(args.input)
    candidates = _iter_candidates(data, rules)
    if not candidates:
        print("[selection-guard] No candidates found; check input shape.", file=sys.stderr)
        return 2

    _print_table(candidates, rules.get("optional_signals", []))
    if not any(not cand.missing for cand in candidates):
        print("[selection-guard] No candidate satisfies all required signals.", file=sys.stderr)
        return 2

    if args.selected is not None:
        chosen = next((cand for cand in candidates if cand.idx == args.selected), None)
        if chosen is None:
            print(
                f"[selection-guard] Selected index {args.selected} not in candidates.",
                file=sys.stderr,
            )
            return 1
        if chosen.missing:
            print(
                f"[selection-guard] Selected #{args.selected} missing: {', '.join(chosen.missing)}",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
