"""Code audit CLI - Phase 1 implementation stub."""

import json
import logging
import subprocess
import sys
from pathlib import Path

import click

logger = logging.getLogger(__name__)


@click.command()
@click.option("--check-dependencies", is_flag=True, help="Check for vulnerable dependencies")
@click.option("--check-vulns", is_flag=True, help="Check for security vulnerabilities")
@click.option("--format", type=click.Choice(["json", "yaml", "html"]), default="json")
@click.option("--output", type=click.Path(), help="Output file")
def audit_main(check_dependencies: bool, check_vulns: bool, format: str, output: str):
    """Run security and quality audit.

    Examples:
        codex-audit --check-dependencies --check-vulns
        codex-audit --format html --output audit.html
    """
    result: dict = {"status": "ok", "vulnerabilities": [], "summary": {}}

    # Try pip-audit first
    pip_audit_result = None
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip_audit", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode == 0 and proc.stdout:
            pip_audit_result = json.loads(proc.stdout)
    except Exception:
        logger.debug("Suppressed exception in handler", exc_info=True)
    if pip_audit_result is not None:
        vulns = pip_audit_result.get("vulnerabilities", [])
        result["vulnerabilities"] = vulns
        result["summary"]["pip_audit"] = {"vulnerable_packages": len(vulns)}
    else:
        # Fallback: scan requirements*.txt for packages
        repo_root = Path(__file__).resolve()
    # Walk up to find the repo root (marker: pyproject.toml or .git)
    for parent in repo_root.parents:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            _repo_root = parent
            break
    else:
        repo_root = Path(__file__).resolve().parents[4]
        req_files = list(repo_root.glob("requirements*.txt"))
        packages = []
        for rf in req_files:
            try:
                for line in rf.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        packages.append(line.split("==")[0].split(">=")[0].split("<=")[0].strip())
            except Exception:
                logger.debug("Suppressed exception in handler", exc_info=True)
        result["summary"]["scanned_requirements_files"] = len(req_files)
        result["summary"]["total_packages"] = len(packages)
        result["summary"]["note"] = "pip-audit not available; manual review recommended"

    output_text = json.dumps(result, indent=2)
    if output:
        Path(output).write_text(output_text)
        click.echo(f"Audit report written to {output}")
    else:
        click.echo(output_text)


if __name__ == "__main__":
    audit_main()
