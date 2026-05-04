"""
autonomy_gate_check.py — CLI guard for AutonomyRegistry policy enforcement.

Called from GitHub Actions workflow steps to verify that the autonomy registry
permits a given surface / control-class before a write operation proceeds.

Usage::

    python scripts/ci/autonomy_gate_check.py \\
        --surface AUT-007 \\
        --class ADVISORY_WRITE \\
        --actor copilot-swe-agent[bot]

Exit codes:
    0  — permitted
    1  — denied by policy (kill_switch, mode insufficient, or class not allowed)
         also returned when the autonomy package is not importable (fail-closed)

Blueprint: .codex/docs/AUTONOMY_BLUEPRINT.md — Phase 1 wiring
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Allow the script to run from the repo root without a full editable install.
# Relies on the standard src-layout convention; the package must be importable
# via this path for the gate check to be authoritative.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_PATH = str(_REPO_ROOT / "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)


def _check(surface: str, control_class: str, actor: str = "") -> int:
    """
    Load the registry and evaluate the permission.

    Returns 0 (permitted) or 1 (denied / unavailable).
    Fails closed: if the autonomy package cannot be imported the check returns 1
    to prevent a missing-package bypass.  Use ``--no-fail`` for advisory mode.
    """
    try:
        from codex.autonomy.registry import AutonomyRegistry  # noqa: PLC0415
    except ImportError:
        logger.critical(
            "GATE ERROR: codex.autonomy package not importable — "
            "cannot verify registry policy.  "
            "Run `pip install -e .` in the repo root, or pass --no-fail for advisory mode."
        )
        return 1

    reg = AutonomyRegistry.load()
    allowed, reason = reg.is_permitted(surface, control_class, actor=actor)

    mode_val = reg.effective_mode.value
    dry_run_tag = "  [DRY-RUN]" if reg.dry_run else ""

    if allowed:
        logger.info(
            "✅  GATE OPEN  surface=%s  class=%s  mode=%s%s — %s",
            surface,
            control_class,
            mode_val,
            dry_run_tag,
            reason,
        )
        return 0
    else:
        logger.error(
            "🚫  GATE CLOSED  surface=%s  class=%s  mode=%s — %s",
            surface,
            control_class,
            mode_val,
            reason,
        )
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate AutonomyRegistry policy before a workflow actuation step.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--surface",
        required=True,
        help="Surface identifier (e.g. AUT-007)",
    )
    parser.add_argument(
        "--class",
        dest="control_class",
        required=True,
        help="ControlClass name (e.g. ADVISORY_WRITE, INFRA_WRITE)",
    )
    parser.add_argument(
        "--actor",
        default="",
        help="Actor login (optional, for audit trail)",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help=(
            "Advisory mode: exit 0 even when denied or package unavailable. "
            "Use in CI steps where the gate is informational only."
        ),
    )
    args = parser.parse_args(argv)

    rc = _check(args.surface, args.control_class, actor=args.actor)
    if rc != 0 and args.no_fail:
        logger.warning("--no-fail set; treating GATE CLOSED/ERROR as advisory warning only.")
        return 0
    return rc


if __name__ == "__main__":
    sys.exit(main())
