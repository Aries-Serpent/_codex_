"""Command line interface for CRM administration helpers."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .diagram import intake_to_mermaid
from .pa_legacy import PowerAutomatePackageError, read_pa_legacy, to_template
from .zaf_legacy import ZendeskAppPackageError, read_zaf, scaffold_template


def _determine_output_file(out: Path, default_name: str) -> Path:
    """Resolve the output file path for commands that emit a single document."""

    if out.suffix:
        out.parent.mkdir(parents=True, exist_ok=True)
        return out

    out.mkdir(parents=True, exist_ok=True)
    return out / default_name


def _cmd_emit_cdm(_: argparse.Namespace) -> int:
    print("emit-cdm is currently a placeholder. See documentation for generation steps.")
    return 0


def _cmd_apply_placeholder(args: argparse.Namespace) -> int:
    print(f"Command '{args.cmd}' is currently a dry-run placeholder. No changes applied.")
    return 0


def _cmd_import_pa_zip(args: argparse.Namespace) -> int:
    package = read_pa_legacy(args.input)
    template = to_template(package)

    default_name = f"{Path(args.input).stem}.template.json"
    output_path = _determine_output_file(Path(args.out), default_name)
    output_path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote Power Automate template to {output_path}")
    return 0


def _cmd_import_zaf_zip(args: argparse.Namespace) -> int:
    bundle = read_zaf(args.input)
    created_files = scaffold_template(bundle, args.out)
    print(f"Wrote {len(created_files)} files to {args.out}")
    return 0


def _cmd_gen_diagram(args: argparse.Namespace) -> int:
    steps = [step.strip() for step in args.steps.split(";") if step.strip()] if args.steps else []

    diagram = intake_to_mermaid(args.flow, steps)
    output_path = _determine_output_file(Path(args.out), f"{args.flow}.mmd")
    output_path.write_text(diagram, encoding="utf-8")
    print(f"Wrote Mermaid diagram to {output_path}")
    return 0


def _cmd_evidence_pack(args: argparse.Namespace) -> int:
    output_root = Path(args.out)
    output_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "message": "Evidence pack placeholder",
        "paths": [],
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Initialised evidence pack at {manifest_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("codex-crm", description=__doc__)
    sub = parser.add_subparsers(dest="cmd")
    sub.required = True

    emit_parser = sub.add_parser("emit-cdm", help="Emit canonical data model artifacts")
    emit_parser.set_defaults(func=_cmd_emit_cdm)

    for cmd in ("apply-zd", "apply-d365"):
        apply_parser = sub.add_parser(
            cmd, help=f"Apply {cmd.split('-')[1].upper()} configuration (dry-run placeholder)"
        )
        apply_parser.set_defaults(func=_cmd_apply_placeholder)

    pa_parser = sub.add_parser(
        "import-pa-zip", help="Convert a Power Automate legacy ZIP into a template"
    )
    pa_parser.add_argument(
        "--in", dest="input", required=True, help="Path to the Power Automate ZIP file"
    )
    pa_parser.add_argument(
        "--out", required=True, help="Output directory or file for the generated template"
    )
    pa_parser.set_defaults(func=_cmd_import_pa_zip)

    zaf_parser = sub.add_parser(
        "import-zaf-zip", help="Convert a Zendesk App ZIP into a scaffolded directory"
    )
    zaf_parser.add_argument(
        "--in", dest="input", required=True, help="Path to the Zendesk App ZIP file"
    )
    zaf_parser.add_argument("--out", required=True, help="Directory to write the scaffolded app")
    zaf_parser.set_defaults(func=_cmd_import_zaf_zip)

    diagram_parser = sub.add_parser(
        "gen-diagram", help="Generate a Mermaid diagram for an intake flow"
    )
    diagram_parser.add_argument("--flow", required=True, help="Name of the flow")
    diagram_parser.add_argument("--steps", default="", help="Semicolon separated list of steps")
    diagram_parser.add_argument(
        "--out", required=True, help="Output directory or file for the diagram"
    )
    diagram_parser.set_defaults(func=_cmd_gen_diagram)

    evidence_parser = sub.add_parser("evidence-pack", help="Initialise an evidence pack directory")
    evidence_parser.add_argument(
        "--out", required=True, help="Directory where the evidence pack should be created"
    )
    evidence_parser.set_defaults(func=_cmd_evidence_pack)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except (PowerAutomatePackageError, ZendeskAppPackageError, FileNotFoundError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
