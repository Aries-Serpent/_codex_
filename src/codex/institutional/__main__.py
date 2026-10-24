"""Installed offline CLI; JSON stdout and stable exit codes."""

from __future__ import annotations

import argparse
import errno
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from . import authority, core, storage


def execute(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = Path(args.root)
    if args.command == "inventory":
        return core.inventory(root, source_ref=args.source_ref), 0
    if args.command == "candidate":
        old = core.load(Path(args.previous)) if args.previous else None
        evidence = (
            next(
                (
                    r
                    for r in old["payload"]["records"]
                    if r.get("schema") == "codex.trust-evidence.v1"
                ),
                None,
            )
            if old is not None
            else None
        )
        value = core.candidate(root, args.session, previous_evidence=evidence)
        if args.previous:
            assert old is not None
            value["payload"]["predecessor"] = core.digest(old)
            value["payload"]["sequence"] = old["payload"]["sequence"] + 1
            value["supersedes"] = old["id"]
            value["extensions"] = old["extensions"]
            value["id"] = f"{value['schema']}:{core.digest(value['payload'])}"
            value["integrity"] = core.digest({k: v for k, v in value.items() if k != "integrity"})
        preview = storage.plan(root, value, args.expected)
        if args.write:
            storage.apply(root, value, preview)
        return {"preview": preview, "written": args.write, "record": value}, 0
    if args.command == "disengage":
        return storage.disengage(root), 0
    value = core.load(Path(args.input))
    if args.command == "authority":
        findings = core.inspect_candidate(value)
        if findings:
            raise core.Rejected("INVALID_CANDIDATE:" + ",".join(findings))
        request = authority.AuthorityRequest("activate", str(root.resolve()), core.digest(value))
        result = authority.evaluate(request)
        evaluation = core.record(
            "codex.authority-evaluation.v1",
            {**asdict(result), "reasons": list(result.reasons), "request": asdict(request)},
            evidence=[value["id"]],
        )
        return evaluation, 6 if result.status == "unsupported" else 3
    if args.command == "assess":
        return core.assess(value), 0
    if args.command in ("challenge", "verify", "status"):
        findings = (
            core.verify(value, root)
            if args.command != "challenge"
            else core.inspect_candidate(value)
        )
        strict = args.strict
        return {
            "findings": findings,
            "scope_complete": True,
            "technical_validation": "FAIL" if findings else "PASS",
            "semantic_review": "NOT_RUN",
            "independent_reproduction": "NOT_RUN",
            "approval": "NOT_RUN",
            "activation": "unsupported",
            "gates": value["payload"]["gates"],
        }, (2 if findings else 9 if strict else 0)
    if args.command == "activate":
        reasons = core.authority_diagnostics(
            value.get("extensions", {}).get("authority_claim", {}),
            core.digest(value),
            str(root.resolve()),
        )
        return {"reason": "AUTHORITY_DENIED", "findings": reasons}, 3
    if args.command in ("migrate", "downgrade"):
        raise core.Rejected("TRANSITION_UNSUPPORTED", 6)
    if args.command == "export":
        preview = storage.export_plan(
            value, Path(args.destination), args.classification, args.basis, args.assessor
        )
        return storage.export(value, preview, write=args.write), 0
    raise core.Rejected("UNSUPPORTED_OPERATION", 6)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "inventory",
            "candidate",
            "assess",
            "challenge",
            "verify",
            "status",
            "export",
            "disengage",
            "activate",
            "authority",
            "migrate",
            "downgrade",
        ],
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--input")
    parser.add_argument("--source-ref")
    parser.add_argument("--session", default="local")
    parser.add_argument("--previous")
    parser.add_argument("--expected")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--destination")
    parser.add_argument("--classification", default="Unknown")
    parser.add_argument("--basis", default="")
    parser.add_argument("--assessor", default="")
    try:
        args = parser.parse_args(argv)
        if args.command not in ("inventory", "candidate", "disengage") and not args.input:
            raise core.Rejected("INPUT_REQUIRED", 5)
        if args.command == "export" and not args.destination:
            raise core.Rejected("DESTINATION_REQUIRED", 5)
        result, code = execute(args)
    except core.Rejected as exc:
        result, code = {"reason": exc.reason, "scope_complete": False}, exc.code
    except OSError as exc:
        resource = exc.errno in (errno.ENOSPC, errno.EDQUOT, errno.ENOMEM, errno.EMFILE)
        result, code = {
            "reason": "BLOCKED_RESOURCE_LIMIT" if resource else "IO_FAILURE",
            "scope_complete": False,
            "recovery": "Preserve last valid checkpoint and partial outputs; unsaved work is not accepted.",
        }, (4 if resource else 8)
    except (ValueError, TypeError, KeyError, RecursionError):
        result, code = {"reason": "MALFORMED_OR_INACCESSIBLE_INPUT", "scope_complete": False}, 5
    print(core.canonical(result).decode())
    return code


if __name__ == "__main__":
    sys.exit(main())
