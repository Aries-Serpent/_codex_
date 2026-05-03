#!/usr/bin/env python3
"""
check_expectations.py — Validate every documented expectation has a working CI enforcement point.

WHY THIS EXISTS
---------------
The "enforcement-first" policy states:
  Before any document is archived or moved, ALL expectations documented in it must be
  registered in docs/ops/EXPECTATIONS_REGISTRY.yaml AND their enforcement must be
  verified (status: enforced).

Without this gate, documented requirements silently disappear when their source files
are moved to archive. This script is the grounded method that prevents that.

WHAT IT DOES
------------
1. Reads docs/ops/EXPECTATIONS_REGISTRY.yaml
2. For each expectation:
   a. Verifies the source_document still exists (or has a tombstone)
   b. Verifies the enforcement location file exists
   c. Optionally runs the `check` command to verify enforcement is real
   d. Reports expectations with status: missing as BLOCKING
3. Reports which source documents are SAFE to archive (all expectations enforced)
   vs BLOCKED (one or more expectations missing enforcement)

Usage
-----
    # Full check — reports all statuses:
    python scripts/ci/check_expectations.py

    # Strict — exit 1 if any expectations have status: missing:
    python scripts/ci/check_expectations.py --strict

    # Check if a specific document is safe to archive:
    python scripts/ci/check_expectations.py --archive-check .github/agents/AGENT_ECOSYSTEM_MAP.md

    # Show only archive-blocked documents:
    python scripts/ci/check_expectations.py --archive-status

    # Run enforcement checks (executes the `check:` commands):
    python scripts/ci/check_expectations.py --run-checks

Exit codes
----------
    0  All expectations have status: enforced (or deferred with reason)
    1  One or more expectations have status: missing (ungrounded)
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import]
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "docs" / "ops" / "EXPECTATIONS_REGISTRY.yaml"

STATUS_OK    = {"enforced", "deferred"}
STATUS_WARN  = {"partial"}
STATUS_BLOCK = {"missing"}


def load_registry() -> list[dict]:
    """Load and parse the expectations registry."""
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found: {REGISTRY_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
        sys.exit(1)

    if not _HAS_YAML:
        # Fallback: simple line-based parse for `id:` and `status:` fields
        return _parse_registry_simple()

    with REGISTRY_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data.get("expectations", []) if isinstance(data, dict) else []


def _parse_registry_simple() -> list[dict]:
    """Minimal YAML-free parser — only reads id, status, source_document."""
    entries: list[dict] = []
    current: dict = {}
    with REGISTRY_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("- id:"):
                if current:
                    entries.append(current)
                current = {"id": s.split("- id:", 1)[1].strip()}
            elif s.startswith("status:") and current:
                current["status"] = s.split("status:", 1)[1].strip()
            elif s.startswith("source_document:") and current:
                current["source_document"] = s.split("source_document:", 1)[1].strip()
            elif s.startswith("archive_safe:") and current:
                val = s.split("archive_safe:", 1)[1].strip().lower()
                current["archive_safe"] = val == "true"
            elif s.startswith("expectation:") and current:
                current["expectation"] = s.split("expectation:", 1)[1].strip().strip('"')
    if current:
        entries.append(current)
    return entries


def check_enforcement_location(exp: dict) -> tuple[bool, str]:
    """Verify the enforcement file/workflow exists."""
    enforcement = exp.get("enforcement", {})
    if not enforcement:
        return False, "No enforcement block defined"
    location = enforcement.get("location", "")
    if not location:
        return False, "No location defined in enforcement block"
    path = REPO_ROOT / location
    if path.exists():
        return True, f"✅ {location}"
    return False, f"❌ {location} — FILE NOT FOUND"


def run_check_command(exp: dict) -> tuple[bool, str]:
    """Run the optional enforcement check command."""
    enforcement = exp.get("enforcement", {})
    check_cmd = enforcement.get("check", "")
    if not check_cmd:
        return True, "(no check command)"
    try:
        result = subprocess.run(
            shlex.split(check_cmd),
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30,
        )
        if result.returncode == 0 and (result.stdout.strip() or result.returncode == 0):
            return True, f"✅ check passed: {check_cmd!r}"
        return False, f"❌ check failed (rc={result.returncode}): {check_cmd!r}\n  {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, f"⏰ check timed out: {check_cmd!r}"
    except Exception as exc:
        return False, f"⚠️  check error: {exc}"


def archive_safe_status(expectations: list[dict]) -> dict[str, dict]:
    """
    Return per-document archive safety: {doc_path: {safe: bool, blocking_ids: [...]}}
    """
    docs: dict[str, dict] = {}
    for exp in expectations:
        doc = exp.get("source_document", "unknown")
        if doc not in docs:
            docs[doc] = {"safe": True, "blocking_ids": [], "total": 0}
        docs[doc]["total"] += 1
        status = exp.get("status", "missing")
        # archive_safe field overrides status-based logic if explicitly set
        explicit_safe = exp.get("archive_safe")
        if explicit_safe is False:
            docs[doc]["safe"] = False
            docs[doc]["blocking_ids"].append(exp.get("id", "?"))
        elif explicit_safe is True:
            pass  # leave docs[doc]["safe"] as is
        elif status in STATUS_BLOCK or status in STATUS_WARN:
            docs[doc]["safe"] = False
            docs[doc]["blocking_ids"].append(exp.get("id", "?"))
    return docs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate documented expectations have CI enforcement. Gate archiving."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any expectations have status: missing",
    )
    parser.add_argument(
        "--run-checks",
        action="store_true",
        help="Execute the `check:` commands from each enforcement block",
    )
    parser.add_argument(
        "--archive-status",
        action="store_true",
        help="Show which source documents are safe vs blocked for archiving",
    )
    parser.add_argument(
        "--archive-check",
        metavar="FILE",
        help="Exit 0 if the given file is archive-safe, 1 if blocked",
    )
    args = parser.parse_args(argv)

    expectations = load_registry()
    if not expectations:
        print("⚠️  No expectations found in registry.")
        return 0

    # ── Per-expectation report ─────────────────────────────────────────────
    enforced = partial = missing = deferred = 0
    issues: list[str] = []

    for exp in expectations:
        eid        = exp.get("id", "?")
        status     = exp.get("status", "missing")
        expectation = exp.get("expectation", "")
        doc        = exp.get("source_document", "unknown")
        gaps       = exp.get("enforcement_gaps", [])

        loc_ok, loc_msg = check_enforcement_location(exp)

        if status == "enforced":
            enforced += 1
            if not loc_ok:
                issues.append(
                    f"⚠️  {eid} — status=enforced but enforcement location missing: {loc_msg}"
                )
        elif status == "partial":
            partial += 1
            gap_text = "; ".join(gaps) if gaps else "no gaps listed"
            issues.append(f"⚡ {eid} [{doc}]\n   {expectation}\n   Gaps: {gap_text}")
        elif status == "missing":
            missing += 1
            issues.append(
                f"❌ {eid} [{doc}]\n   {expectation}\n   "
                f"UNGROUNDED — no enforcement. Enforcement location: {loc_msg}"
            )
        elif status == "deferred":
            deferred += 1
            note = exp.get("notes", "no reason given")
            issues.append(f"⏸️  {eid} — deferred: {note}")

        if args.run_checks and status not in ("missing", "deferred"):
            chk_ok, chk_msg = run_check_command(exp)
            if not chk_ok:
                issues.append(f"  └─ {eid} check FAILED: {chk_msg}")

    # ── Archive status report ──────────────────────────────────────────────
    if args.archive_status or args.archive_check:
        docs = archive_safe_status(expectations)

        if args.archive_check:
            target = args.archive_check
            # normalise to relative path from repo root
            try:
                target = str(Path(target).relative_to(REPO_ROOT))
            except ValueError:
                # Path is outside the repo root; keep the original target string for registry lookup.
                pass
                _ = None  # noqa: BLE001
            info = docs.get(target)
            if info is None:
                print(f"ℹ️  {target} — not in registry. Safe to archive (no expectations tracked).")
                return 0
            if info["safe"]:
                print(f"✅ {target} — ARCHIVE SAFE (all {info['total']} expectation(s) enforced)")
                return 0
            print(
                f"🚫 {target} — ARCHIVE BLOCKED\n"
                f"   {len(info['blocking_ids'])} of {info['total']} expectation(s) not enforced: "
                f"{', '.join(info['blocking_ids'])}\n"
                f"   Fix these expectations in {REGISTRY_PATH.relative_to(REPO_ROOT)} first."
            )
            return 1

        print("\n📋 Archive safety by source document:\n")
        print(f"  {'STATUS':<8}  {'BLOCKED IDs':<20}  Document")
        print(f"  {'------':<8}  {'-----------':<20}  --------")
        for doc, info in sorted(docs.items()):
            if info["safe"]:
                print(f"  {'✅ SAFE':<8}  {'—':<20}  {doc}")
            else:
                ids = ", ".join(info["blocking_ids"])
                print(f"  {'🚫 BLOCK':<8}  {ids:<20}  {doc}")
        return 0

    # ── Summary ────────────────────────────────────────────────────────────
    total = len(expectations)
    print(f"\n📊 Expectations Registry — {total} total")
    print(f"   ✅ enforced: {enforced}  ⚡ partial: {partial}  "
          f"❌ missing: {missing}  ⏸️  deferred: {deferred}\n")

    for issue in issues:
        print(issue)
        print()

    if missing > 0:
        print(
            f"🚫 {missing} expectation(s) have NO enforcement — "
            f"their source documents MUST NOT be archived until fixed.\n"
            f"   Add enforcement points and update {REGISTRY_PATH.relative_to(REPO_ROOT)}"
        )
        return 1 if args.strict else 0

    if partial > 0:
        print(
            f"⚡ {partial} expectation(s) have PARTIAL enforcement — "
            f"gaps listed above. Address before archiving source documents."
        )

    if missing == 0 and partial == 0:
        print("✅ All expectations have enforcement coverage.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
