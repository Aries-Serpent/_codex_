#!/usr/bin/env python3
"""Sigstore verification for critical PyPI dependencies.

Verifies package signatures using the sigstore Python SDK where available.
Falls back to a structured warning when sigstore is not installed.

Usage:
    python scripts/security/sigstore_verify.py [--requirements <file>] [--output <file>]

Exit codes:
    0 — all critical packages verified (or no signature mismatch found)
    1 — actual signature mismatch detected on a critical package
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Packages considered critical — a signature mismatch here causes exit(1).
CRITICAL_PACKAGES: frozenset[str] = frozenset(
    {
        "cryptography",
        "paramiko",
        "requests",
        "urllib3",
        "certifi",
        "setuptools",
        "pip",
        "wheel",
        "sigstore",
        "pyopenssl",
        "pyjwt",
        "bcrypt",
        "pynacl",
    }
)

# ---------------------------------------------------------------------------
# Sigstore import (optional)
# ---------------------------------------------------------------------------

_SIGSTORE_AVAILABLE = importlib.util.find_spec("sigstore") is not None
if not _SIGSTORE_AVAILABLE:
    logger.warning(
        "sigstore is not installed — package signature verification will be skipped. "
        "Install with: pip install sigstore"
    )


# ---------------------------------------------------------------------------
# Requirements parsing
# ---------------------------------------------------------------------------

_REQ_LINE_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_\-\.]+)"  # package name
    r"(?:==(?P<version>[^\s;#]+))?",      # optional pinned version
    re.ASCII,
)


def parse_requirements(path: Path) -> list[dict[str, str]]:
    """Return a list of {name, version} dicts from a pip-style lock file.

    Handles:
    * ``requirements/lock.txt`` (pip-compile format)
    * ``uv.lock`` (TOML-ish, best-effort)
    * Generic ``requirements*.txt``
    """
    packages: list[dict[str, str]] = []
    seen: set[str] = set()

    suffix = path.suffix.lower()
    content = path.read_text(encoding="utf-8")

    if suffix == ".lock" and "[[package]]" in content:
        # uv.lock TOML-ish format
        for block in content.split("[[package]]"):
            name_match = re.search(r'name\s*=\s*"([^"]+)"', block)
            ver_match = re.search(r'version\s*=\s*"([^"]+)"', block)
            if name_match:
                name = name_match.group(1).lower()
                version = ver_match.group(1) if ver_match else "unknown"
                if name not in seen:
                    seen.add(name)
                    packages.append({"name": name, "version": version})
    else:
        # pip-compile / standard requirements format
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "-", "http", "git+")):
                continue
            m = _REQ_LINE_RE.match(line)
            if m:
                name = m.group("name").lower()
                version = m.group("version") or "unknown"
                if name not in seen:
                    seen.add(name)
                    packages.append({"name": name, "version": version})

    return packages


# ---------------------------------------------------------------------------
# Verification logic
# ---------------------------------------------------------------------------

class VerificationResult:
    """Holds the outcome of a single package verification attempt."""

    def __init__(
        self,
        name: str,
        version: str,
        status: str,  # "verified" | "unverified" | "error" | "mismatch"
        detail: str = "",
    ) -> None:
        self.name = name
        self.version = version
        self.status = status
        self.detail = detail
        self.is_critical = name.lower() in CRITICAL_PACKAGES

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "critical": self.is_critical,
            "detail": self.detail,
        }


def _verify_with_sigstore(name: str, version: str) -> VerificationResult:
    """Attempt sigstore verification for a single package.

    Real sigstore verification would download the transparency-log bundle
    from PyPI's attestation API.  The current PyPI attestation endpoint is:
        https://pypi.org/simple/{name}/#sigstore-bundle

    This implementation performs a best-effort check:
    1. Queries PyPI JSON API for the package release.
    2. Checks for ``provenance`` / attestation metadata in the release data.
    3. If attestation data is present, delegates to ``sigstore`` SDK.
    4. If no attestation exists → "unverified" (not an error; most packages
       haven't published Sigstore bundles yet).
    """
    import urllib.error
    import urllib.request

    url = f"https://pypi.org/pypi/{name}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return VerificationResult(name, version, "error", f"PyPI HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(name, version, "error", f"Network error: {exc}")

    # Check for sigstore attestation in release metadata
    release_files = data.get("urls", [])
    for file_info in release_files:
        provenance = file_info.get("provenance")
        if provenance:
            # Attestation present — attempt real SDK verification
            try:
                # sigstore SDK verification (bundle from provenance URL)
                from sigstore.models import Bundle  # type: ignore[import-untyped]
                from sigstore.verify import Verifier  # type: ignore[import-untyped]

                bundle_url = provenance
                with urllib.request.urlopen(bundle_url, timeout=15) as r:  # noqa: S310
                    bundle_data = json.loads(r.read())
                bundle = Bundle.from_dict(bundle_data)
                verifier = Verifier.production()
                verifier.verify_artifact(bundle=bundle, identity=None)
                return VerificationResult(
                    name, version, "verified", "Sigstore attestation validated"
                )
            except Exception as exc:  # noqa: BLE001
                # If verification raises, treat as mismatch for critical packages
                return VerificationResult(
                    name, version, "mismatch", f"Attestation verification failed: {exc}"
                )

    # No attestation found — most packages don't have Sigstore yet
    return VerificationResult(
        name, version, "unverified", "No Sigstore attestation found on PyPI"
    )


def _verify_without_sigstore(name: str, version: str) -> VerificationResult:
    """Fallback when sigstore SDK is not installed."""
    return VerificationResult(
        name,
        version,
        "unverified",
        "sigstore SDK not installed — install with: pip install sigstore",
    )


def verify_package(name: str, version: str) -> VerificationResult:
    """Verify a single package, choosing the right backend."""
    if _SIGSTORE_AVAILABLE:
        return _verify_with_sigstore(name, version)
    return _verify_without_sigstore(name, version)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(packages: list[dict[str, str]]) -> dict[str, Any]:
    """Verify all packages and return a structured JSON report."""
    verified: list[dict[str, Any]] = []
    unverified: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []

    total = len(packages)
    for i, pkg in enumerate(packages, 1):
        name = pkg["name"]
        version = pkg["version"]
        logger.info("[%d/%d] Checking %s==%s …", i, total, name, version)

        result = verify_package(name, version)
        row = result.to_dict()

        if result.status == "verified":
            verified.append(row)
        elif result.status == "mismatch":
            mismatches.append(row)
            errors.append(row)
        elif result.status == "error":
            errors.append(row)
        else:
            unverified.append(row)

    return {
        "sigstore_sdk_available": _SIGSTORE_AVAILABLE,
        "summary": {
            "total": total,
            "verified": len(verified),
            "unverified": len(unverified),
            "errors": len(errors),
            "mismatches": len(mismatches),
        },
        "verified": verified,
        "unverified": unverified,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _default_requirements() -> Path:
    """Return the first requirements file that exists."""
    candidates = [
        Path("requirements/lock.txt"),
        Path("uv.lock"),
        Path("requirements.txt"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]  # will fail gracefully in main()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--requirements",
        type=Path,
        default=None,
        help="Path to requirements/lock file (default: requirements/lock.txt or uv.lock)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path for JSON report output (prints to stdout if omitted)",
    )
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Only verify packages in the critical list",
    )
    args = parser.parse_args(argv)

    req_file = args.requirements or _default_requirements()
    if not req_file.exists():
        logger.error("Requirements file not found: %s", req_file)
        return 2

    logger.info("Using requirements file: %s", req_file)
    if not _SIGSTORE_AVAILABLE:
        logger.warning(
            "sigstore SDK not installed. Install with: pip install sigstore\n"
            "Running in structured-warning mode — all packages will be 'unverified'."
        )

    packages = parse_requirements(req_file)
    if args.critical_only:
        packages = [p for p in packages if p["name"].lower() in CRITICAL_PACKAGES]

    logger.info("Found %d packages to check", len(packages))
    report = build_report(packages)

    report_json = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report_json, encoding="utf-8")
        logger.info("Report written to %s", args.output)
    else:
        print(report_json)

    # Exit 1 only on actual signature mismatches (not missing signatures)
    mismatches = [e for e in report["errors"] if e.get("status") == "mismatch"]
    if mismatches:
        critical_mismatches = [m for m in mismatches if m.get("critical")]
        if critical_mismatches:
            logger.error(
                "CRITICAL signature mismatch on %d package(s): %s",
                len(critical_mismatches),
                [m["name"] for m in critical_mismatches],
            )
            return 1
        logger.warning(
            "Signature mismatch on non-critical package(s): %s",
            [m["name"] for m in mismatches],
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
