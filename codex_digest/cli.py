from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .pipeline import run_pipeline
from .error_capture import make_error_block


def main(argv=None) -> int:
    ap = argparse.ArgumentParser("codex-digest")
    ap.add_argument("--context-file", type=Path, help="Priming context file (optional)")
    ap.add_argument("--input-file", type=Path, required=True, help="Raw description file")
    ap.add_argument("--out-md", type=Path, default=Path(".codex_digest.md"))
    ap.add_argument("--out-json", type=Path, default=Path(".codex_digest.plan.json"))
    ap.add_argument("--dry-run", action="store_true", default=True)
    args = ap.parse_args(argv)

    context = (
        args.context_file.read_text(encoding="utf-8")
        if args.context_file and args.context_file.exists()
        else ""
    )
    raw = args.input_file.read_text(encoding="utf-8")

    try:
        out = run_pipeline(context, raw, dry_run=args.dry_run)
        args.out_md.write_text(out.tasks_md, encoding="utf-8")
        args.out_json.write_text(json.dumps(out.plan_json, indent=2), encoding="utf-8")
        if out.opportunity_areas:
            sys.stderr.write("\n".join(out.opportunity_areas) + "\n")
        return 0
    except Exception as e:  # pragma: no cover - safety net
        blk = make_error_block("CLI", "codex-digest run", str(e), "executing pipeline")
        sys.stderr.write(blk + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
