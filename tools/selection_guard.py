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
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Candidate:
    idx: int
    turn_id: str
    payload: str
    hits: List[str]
    missing: List[str]


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_rules(path: str) -> Dict[str, Any]:
    obj = _read_json(path)
    if "required_signals" not in obj or not isinstance(obj["required_signals"], list):
        raise ValueError("rules file missing 'required_signals' list")
    obj.setdefault("optional_signals", [])
    obj.setdefault("path_hints", ["output_diff.diff", "pr.output_diff.diff", "pr_message", "diff"])
    return obj


def _glob_first(d: Dict[str, Any], pattern: str) -> Optional[Tuple[str, Any]]:
    """Depth-first search over nested structures returning first key path matching pattern."""
    stack: List[Tuple[List[str], Any]] = [([], d)]
    while stack:
        path, cur = stack.pop()
        if isinstance(cur, dict):
            for key, val in cur.items():
                new_path = path + [key]
                joined = ".".join(new_path)
                if fnmatch.fnmatch(joined, pattern):
                    return joined, val
                stack.append((new_path, val))
        elif isinstance(cur, list):
            for idx, val in enumerate(cur):
                stack.append((path + [str(idx)], val))
    return None


def _extract_siblings(tm: Dict[str, Any]) -> List[str]:
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


def _extract_payload(turn_obj: Dict[str, Any], path_hints: List[str]) -> str:
    for hint in path_hints:
        hit = _glob_first(turn_obj, hint)
        if hit and isinstance(hit[1], str):
            return hit[1]
    payloads: List[str] = []
    for hint in ("diff", "pr_message", "message_text"):
        hit = _glob_first(turn_obj, f"*{hint}")
        if hit and isinstance(hit[1], str):
            payloads.append(hit[1])
    return "\n\n".join(payloads)


def _scan_payload(payload: str, required: List[str]) -> Tuple[List[str], List[str]]:
    hits: List[str] = []
    missing: List[str] = []
    lowered = payload.lower()
    for signal in required:
        if signal.lower() in lowered:
            hits.append(signal)
        else:
            missing.append(signal)
    return hits, missing


def _iter_candidates(data: Dict[str, Any], rules: Dict[str, Any]) -> List[Candidate]:
    tm = data.get("turn_mapping", {})
    siblings = _extract_siblings(tm)
    candidates: List[Candidate] = []
    for idx, turn_id in enumerate(siblings, start=1):
        turn_info = tm.get(turn_id, {})
        turn = turn_info.get("turn", {}) if isinstance(turn_info, dict) else {}
        payload = _extract_payload(turn, rules["path_hints"])
        hits, missing = _scan_payload(payload, rules["required_signals"])
        candidates.append(Candidate(idx, turn_id, payload, hits, missing))
    return candidates


def _print_table(candidates: List[Candidate], optional: List[str]) -> None:
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


def main(argv: Optional[List[str]] = None) -> int:
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
