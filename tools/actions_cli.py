#!/usr/bin/env python3
"""
actions_cli: Small helper for 'discover -> fetch -> cite' workflows
against Aries-Serpent/_codex_ using the GitHub REST API.

Usage examples:
  python tools/actions_cli.py branches
  python tools/actions_cli.py search --q "tokenization" --ref 0D_base_
  python tools/actions_cli.py fetch --path docs/prompts/custom_gpt_self_healing_engineer.md --ref 0D_base_
  python tools/actions_cli.py cite --path docs/prompts/custom_gpt_self_healing_engineer.md --ref 0D_base_ --note "Prompt used by CustomGPT"
"""
from __future__ import annotations
import argparse, datetime, os, pathlib, sys
from typing import List

from src.codex_bridge.github_client import list_branches, get_text, code_search

DEFAULT_OWNER = os.getenv("CODEX_GH_OWNER", "Aries-Serpent")
DEFAULT_REPO = os.getenv("CODEX_GH_REPO", "_codex_")
DEFAULT_CITATIONS_DIR = os.getenv("CODEX_CITATIONS_DIR", "reports/citations")


def cmd_branches(args: argparse.Namespace) -> int:
    branches = list_branches(DEFAULT_OWNER, DEFAULT_REPO)
    for b in branches:
        name = b.get("name")
        default_marker = "[default]" if b.get("default", False) else ""
        print(f"- {name} {default_marker}".strip())
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    q = args.q
    ref = args.ref
    data = code_search(DEFAULT_OWNER, DEFAULT_REPO, q, ref)
    items = data.get("items", [])
    print(f"# Search results for {q!r} @ {ref} ({len(items)} hits)")
    for it in items:
        path = it.get("path")
        print(f"\n## {path}")
        try:
            text = get_text(DEFAULT_OWNER, DEFAULT_REPO, ref, path)
        except Exception as e:  # pragma: no cover - defensive
            print(f"(error fetching file: {e})")
            continue
        snippet = text[:800]
        print("```text")
        print(snippet)
        print("```")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    content = get_text(DEFAULT_OWNER, DEFAULT_REPO, args.ref, args.path)
    sys.stdout.write(content)
    return 0


def _write_citation(path: str, ref: str, note: str) -> pathlib.Path:
    outdir = pathlib.Path(DEFAULT_CITATIONS_DIR)
    outdir.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.utcnow()
    fname = outdir / f"citations-{now.date().isoformat()}.md"
    header_needed = not fname.exists()
    with fname.open("a", encoding="utf-8") as f:
        if header_needed:
            f.write("# DeepResearch Citations\n\n")
        ts = now.isoformat() + "Z"
        f.write(f"- {ts} | `{ref}` | `{path}` — {note}\n")
    return fname


def cmd_cite(args: argparse.Namespace) -> int:
    p = _write_citation(args.path, args.ref, args.note)
    print(str(p))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_b = sub.add_parser("branches", help="List branches")
    sp_b.set_defaults(func=cmd_branches)

    sp_s = sub.add_parser("search", help="Search code and show snippets")
    sp_s.add_argument("--q", required=True)
    sp_s.add_argument("--ref", default="main")
    sp_s.set_defaults(func=cmd_search)

    sp_f = sub.add_parser("fetch", help="Fetch raw file content")
    sp_f.add_argument("--path", required=True)
    sp_f.add_argument("--ref", required=True)
    sp_f.set_defaults(func=cmd_fetch)

    sp_c = sub.add_parser("cite", help="Append a DeepResearch citation entry")
    sp_c.add_argument("--path", required=True)
    sp_c.add_argument("--ref", required=True)
    sp_c.add_argument("--note", required=True)
    sp_c.set_defaults(func=cmd_cite)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
