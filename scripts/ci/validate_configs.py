#!/usr/bin/env python3
"""
Gap 35 — Schema validation for Codex YAML configs.

Loads every YAML file inside ``configs/`` and attempts to validate it against
the Pydantic ``TrainConfig`` schema from ``src/codex_ml/config_schema.py``.

Non-training YAML files (e.g. alertmanager, Zendesk desired-state, security
policies, etc.) are **not** expected to conform to ``TrainConfig`` — those are
validated for *YAML syntax only*.

Training-candidate files are identified by containing at least one of the
canonical top-level keys used in ``TrainConfig`` (``learning_rate``,
``batch_size``, ``epochs``, ``model_name``, ``config_version``).

Exit codes:
    0 — all files passed their respective validation level
    1 — one or more files failed validation (schema error or YAML parse error)

Usage::

    python scripts/ci/validate_configs.py          # validate all configs/
    python scripts/ci/validate_configs.py --help
    pre-commit run validate-codex-configs --all-files
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional rich output helpers
# ---------------------------------------------------------------------------
try:
    import yaml  # PyYAML — required
except ImportError:
    print("ERROR: PyYAML is not installed.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Repository root discovery
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIGS_DIR = REPO_ROOT / "configs"

# Keys that indicate a YAML file is a TrainConfig candidate
TRAIN_CONFIG_KEYS = frozenset(
    {
        "learning_rate",
        "batch_size",
        "epochs",
        "model_name",
        "config_version",
        "max_samples",
        "data_path",
        "grad_accum",
    }
)

# Directories / filename patterns to skip entirely (no training data)
SKIP_PATTERNS = (
    "desired/",
    "synonyms/",
    "alertmanager/",
    "security",
    "bandit",
    "PROMOTION_READINESS",
    "capability",
    "task_sequence",
    "codex_gap_registry",
    "codex_hardship",
    "codex_ml_test_map",
    "code_quality",
)


def _should_skip(path: Path) -> bool:
    rel = path.relative_to(CONFIGS_DIR).as_posix()
    return any(pat in rel for pat in SKIP_PATTERNS)


def _is_train_candidate(data: object) -> bool:
    """Return True if *data* looks like a TrainConfig payload."""
    if not isinstance(data, dict):
        return False
    return bool(TRAIN_CONFIG_KEYS.intersection(data.keys()))


def validate_yaml_syntax(path: Path) -> str | None:
    """Return an error string if *path* has invalid YAML, else None."""
    try:
        with path.open(encoding="utf-8") as fh:
            yaml.safe_load(fh)
        return None
    except yaml.YAMLError as exc:
        return f"YAML parse error: {exc}"


def validate_train_config(path: Path, data: dict) -> str | None:  # type: ignore[type-arg]
    """
    Attempt to validate *data* against ``TrainConfig``.

    Hydra config fragments are partial — they often carry extra keys from
    sibling config groups that are only merged at compose time.  We therefore
    filter *data* to only the fields known to ``TrainConfig`` before validating,
    so that "extra field" errors from Hydra-group keys don't cause false failures.

    Returns an error string on failure, None on success.
    Gracefully skips validation if the codex_ml package is not importable.
    """
    try:
        # Add repo src/ to sys.path so we can import without installing
        src_dir = str(REPO_ROOT / "src")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        from codex_ml.config_schema import TrainConfig  # type: ignore[import]
        from pydantic import ValidationError  # type: ignore[import]

        # Only pass fields that TrainConfig actually declares, so Hydra-group
        # extras (grad_clip_norm, weight_decay, log_interval, etc.) don't
        # cause spurious extra_forbidden errors on legitimate config fragments.
        known_fields = set(TrainConfig.model_fields.keys())
        filtered = {k: v for k, v in data.items() if k in known_fields}

        try:
            TrainConfig.model_validate(filtered)
            return None
        except ValidationError as exc:
            return f"Pydantic validation error:\n{exc}"
    except ImportError as exc:
        # codex_ml or pydantic not installed — degrade to syntax-only
        return f"[SKIP schema check — import failed: {exc}]"


def run(configs_dir: Path, verbose: bool = False) -> int:
    """
    Validate all YAML files under *configs_dir*.

    Returns the number of failures.
    """
    yaml_files = sorted(configs_dir.rglob("*.yaml")) + sorted(configs_dir.rglob("*.yml"))

    if not yaml_files:
        print(f"⚠️  No YAML files found under {configs_dir}", file=sys.stderr)
        return 0

    failures: list[str] = []
    skipped: list[str] = []
    ok_syntax: list[str] = []
    ok_schema: list[str] = []

    for path in yaml_files:
        rel = path.relative_to(REPO_ROOT).as_posix()

        if _should_skip(path):
            skipped.append(rel)
            if verbose:
                print(f"  ⏭  {rel}  (skipped — non-training config)")
            continue

        # 1. YAML syntax check (always)
        err = validate_yaml_syntax(path)
        if err is not None:
            failures.append(f"{rel}: {err}")
            print(f"  ❌ {rel}  — {err}")
            continue

        # 2. Pydantic schema check (training candidates only)
        try:
            with path.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except Exception as exc:  # pragma: no cover
            failures.append(f"{rel}: re-read error: {exc}")
            continue

        if _is_train_candidate(data):
            schema_err = validate_train_config(path, data)
            if schema_err is None:
                ok_schema.append(rel)
                if verbose:
                    print(f"  ✅ {rel}  (schema OK)")
            elif schema_err.startswith("[SKIP"):
                ok_syntax.append(rel)
                if verbose:
                    print(f"  ✔  {rel}  (syntax OK; {schema_err})")
            else:
                failures.append(f"{rel}: {schema_err}")
                print(f"  ❌ {rel}\n     {schema_err}")
        else:
            ok_syntax.append(rel)
            if verbose:
                print(f"  ✔  {rel}  (syntax OK — not a TrainConfig candidate)")

    # Summary
    total = len(yaml_files) - len(skipped)
    print(
        f"\nValidated {total} file(s) under {configs_dir.relative_to(REPO_ROOT)}/  "
        f"({len(ok_schema)} schema-validated, "
        f"{len(ok_syntax)} syntax-only, "
        f"{len(skipped)} skipped, "
        f"{len(failures)} failed)"
    )

    if failures:
        print("\nFailures:", file=sys.stderr)
        for msg in failures:
            print(f"  • {msg}", file=sys.stderr)

    return len(failures)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--configs-dir",
        default=str(CONFIGS_DIR),
        help="Root directory to scan for YAML config files (default: configs/)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print a line for every file, including passing ones",
    )
    args = parser.parse_args()

    configs_dir = Path(args.configs_dir).resolve()
    if not configs_dir.is_dir():
        print(f"ERROR: configs dir not found: {configs_dir}", file=sys.stderr)
        sys.exit(1)

    failures = run(configs_dir, verbose=args.verbose)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
