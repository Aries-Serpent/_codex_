"""Unified CLI entry-point for Codex CRM administrative tasks."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from codex_crm.d365_admin.generate import emit_d365_config
from codex_crm.diagram.flows import flow_to_mermaid
from codex_crm.evidence.emit import write_evidence
from codex_crm.pa_legacy.reader import read_pa_legacy, to_template
from codex_crm.zaf_legacy.reader import read_zaf, scaffold_template
from codex_crm.zd_admin.generate import emit_zendesk_config

DEFAULT_OUTPUT_ROOT = Path(".codex") / "crm"
DEFAULT_ZENDESK_OUTPUT = DEFAULT_OUTPUT_ROOT / "zendesk"
DEFAULT_D365_OUTPUT = DEFAULT_OUTPUT_ROOT / "d365"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("codex-crm")
    sub = parser.add_subparsers(dest="command", required=True)

    apply_zd = sub.add_parser("apply-zd", help="Emit Zendesk config-as-data artifacts")
    apply_zd.add_argument(
        "--out",
        default=str(DEFAULT_ZENDESK_OUTPUT),
        help="Output directory for Zendesk artifacts (default: .codex/crm/zendesk)",
    )

    apply_d365 = sub.add_parser("apply-d365", help="Emit Dynamics 365 config-as-data artifacts")
    apply_d365.add_argument(
        "--out",
        default=str(DEFAULT_D365_OUTPUT),
        help="Output directory for D365 artifacts (default: .codex/crm/d365)",
    )

    import_pa = sub.add_parser("import-pa-zip", help="Import a legacy Power Automate package")
    import_pa.add_argument(
        "--in",
        dest="source",
        required=True,
        help="Path to the Power Automate ZIP",
    )
    import_pa.add_argument(
        "--out",
        required=True,
        help="Output directory for the template",
    )

    import_zaf = sub.add_parser(
        "import-zaf-zip",
        help="Import a legacy Zendesk App Framework package",
    )
    import_zaf.add_argument(
        "--in",
        dest="source",
        required=True,
        help="Path to the ZAF ZIP",
    )
    import_zaf.add_argument(
        "--out",
        required=True,
        help="Output directory for the scaffold",
    )

    diagram = sub.add_parser("gen-diagram", help="Generate a Mermaid diagram for a flow")
    diagram.add_argument("--flow", required=True, help="Flow name")
    diagram.add_argument("--steps", required=True, help="Semicolon-delimited list of steps")
    diagram.add_argument("--out", required=True, help="Output path for the .mmd file")

    evidence = sub.add_parser("evidence-pack", help="Write an evidence bundle")
    evidence.add_argument("--out", required=True, help="Output directory for the evidence bundle")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "apply-zd":
        emit_zendesk_config(args.out)
        return 0
    elif args.command == "apply-d365":
        emit_d365_config(args.out)
        return 0
    elif args.command == "import-pa-zip":
        package = read_pa_legacy(args.source)
        template = to_template(package)
        destination = Path(args.out)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "template.json").write_text(json.dumps(template, indent=2), encoding="utf-8")
        return 0
    elif args.command == "import-zaf-zip":
        zaf_package = read_zaf(args.source)
        scaffold_template(zaf_package, args.out)
        return 0
    elif args.command == "gen-diagram":
        steps = [step.strip() for step in args.steps.split(";") if step.strip()]
        Path(args.out).write_text(flow_to_mermaid(args.flow, steps), encoding="utf-8")
        return 0
    elif args.command == "evidence-pack":
        write_evidence(args.out)
        return 0
    else:  # pragma: no cover - defensive branch
        parser.print_help()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
