from __future__ import annotations

import argparse
import json
import pathlib
import sys

from codex_crm.d365_admin.generate import emit_d365_config
from codex_crm.diagram.flows import flow_to_mermaid
from codex_crm.evidence.emit import write_evidence
from codex_crm.pa_legacy.reader import read_pa_legacy, to_template
from codex_crm.zaf_legacy.reader import read_zaf, scaffold_template
from codex_crm.zd_admin.generate import emit_zendesk_config


def _write_json(path: pathlib.Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser("codex-crm")
    sub = parser.add_subparsers(dest="command", required=True)

    apply_zd = sub.add_parser("apply-zd", help="Emit Zendesk configuration scaffolds")
    apply_zd.add_argument("--out", required=True, help="Output directory for Zendesk JSON")

    apply_d365 = sub.add_parser("apply-d365", help="Emit Dynamics 365 configuration scaffolds")
    apply_d365.add_argument("--out", required=True, help="Output directory for Dynamics CSVs")

    import_pa = sub.add_parser(
        "import-pa-zip", help="Convert a legacy Power Automate ZIP into a template"
    )
    import_pa.add_argument("--in", dest="in_path", required=True, help="Path to ZIP file")
    import_pa.add_argument(
        "--out", required=True, help="Directory for rendered Power Automate template"
    )

    import_zaf = sub.add_parser("import-zaf-zip", help="Normalize a Zendesk App Framework ZIP")
    import_zaf.add_argument("--in", dest="in_path", required=True, help="Path to ZIP file")
    import_zaf.add_argument("--out", required=True, help="Directory for scaffold output")

    gen_diagram = sub.add_parser(
        "gen-diagram", help="Generate a Mermaid diagram from workflow steps"
    )
    gen_diagram.add_argument("--flow", required=True, help="Name of the flow")
    gen_diagram.add_argument(
        "--steps",
        required=True,
        help="Semicolon-separated list of workflow steps",
    )
    gen_diagram.add_argument("--out", required=True, help="Path to write the Mermaid file")

    evidence = sub.add_parser("evidence-pack", help="Emit an evidence bundle")
    evidence.add_argument("--out", required=True, help="Directory for the evidence bundle")

    args = parser.parse_args(argv)

    if args.command == "apply-zd":
        emit_zendesk_config(args.out)
        return 0
    if args.command == "apply-d365":
        emit_d365_config(args.out)
        return 0
    if args.command == "import-pa-zip":
        package = read_pa_legacy(args.in_path)
        template = to_template(package)
        output_dir = pathlib.Path(args.out)
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_json(output_dir / "template.json", template)
        return 0
    if args.command == "import-zaf-zip":
        zaf_package = read_zaf(args.in_path)
        scaffold_template(zaf_package, args.out)
        return 0
    if args.command == "gen-diagram":
        steps = [step.strip() for step in args.steps.split(";") if step.strip()]
        output_path = pathlib.Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(flow_to_mermaid(args.flow, steps), encoding="utf-8")
        return 0
    if args.command == "evidence-pack":
        write_evidence(args.out)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
