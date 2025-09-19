"""Demonstration script showing Codex orchestrating ITA calls."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, List

from .bridge import CodexBridgeClient
from .config import ClientConfig


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Demo orchestration against the Internal Tools API"
    )
    parser.add_argument("--query", required=True, help="Query to run against /kb/search")
    parser.add_argument(
        "--run-tests", nargs="*", default=[], help="Test targets to send to /tests/run"
    )
    parser.add_argument(
        "--confirm", action="store_true", help="Set confirm=true and dry_run=false for the PR call"
    )
    parser.add_argument("--repo", default="example/repo", help="Repository slug for PR simulation")
    parser.add_argument("--title", default="Codex Demo", help="PR title to use in the simulation")
    parser.add_argument("--head", default="feature/demo", help="Branch head for the PR simulation")
    parser.add_argument("--base", default="main", help="Base branch for the PR simulation")
    return parser.parse_args(argv)


def _format_section(title: str) -> str:
    return f"\n{'=' * len(title)}\n{title}\n{'=' * len(title)}"


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    config = ClientConfig.from_environment()
    report: List[str] = []

    with CodexBridgeClient(config) as client:
        report.append(_format_section("Knowledge Search"))
        knowledge = client.kb_search(args.query)
        report.append(json.dumps(knowledge.model_dump(), indent=2))

        report.append(_format_section("Repo Hygiene"))
        diff = """diff --git a/app.py b/app.py
@@
+print("TODO: remove debug output")
"""
        hygiene = client.repo_hygiene(diff, checks=["lint", "format", "secrets"])
        report.append(json.dumps(hygiene.model_dump(), indent=2))

        if args.run_tests:
            report.append(_format_section("Tests"))
            tests = client.tests_run(args.run_tests)
            report.append(json.dumps(tests.model_dump(), indent=2))

        report.append(_format_section("Pull Request"))
        pr = client.git_create_pr(
            repo=args.repo,
            title=args.title,
            body="Codex demo run",  # usually generated from plan
            base=args.base,
            head=args.head,
            dry_run=not args.confirm,
            confirm=args.confirm,
        )
        report.append(json.dumps(pr.model_dump(), indent=2))

    sys.stdout.write("\n".join(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
