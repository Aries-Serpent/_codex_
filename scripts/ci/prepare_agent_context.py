#!/usr/bin/env python3
"""Produce bounded optional context for explicit reading, not host prompt injection."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def prepare(output_dir: Path, timeout: float) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    scores = output_dir / "patterns.json"
    (output_dir / "context.md").unlink(missing_ok=True)
    # Never reuse stale scores after an unsuccessful invocation.
    scores.unlink(missing_ok=True)
    status: dict[str, object] = {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "unavailable",
        "source": "repository pattern scorer",
        "delivery": "file for explicit reading; no platform prompt attachment",
        "rag": "unavailable: automatic model loading/index rebuilding is not requested",
    }
    if os.environ.get("CODEX_CONTEXT_ENABLED", "true").lower() in {"0", "false", "no"}:
        status.update(status="disabled", reason="explicit optional context opt-out")
        (output_dir / "status.json").write_text(
            json.dumps(status, indent=2) + "\n", encoding="utf-8"
        )
        return status
    metadata = {
        "task_description": os.environ.get("TASK_TITLE", "")[:1000],
        "domain": "CI/CD",
        "agent_types": [],
    }
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/ci/phase_10_3_context_scorer.py"),
                "--patterns",
                str(ROOT / ".codex/patterns/ci_failure_patterns.yaml"),
                "--output",
                str(scores.resolve()),
                "--json-metadata",
                json.dumps(metadata),
                "--top-k",
                "5",
                "--min-score",
                "0.65",
            ],
            cwd=ROOT,
            timeout=timeout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0 and scores.exists() and scores.stat().st_size <= 256 * 1024:
            data = json.loads(scores.read_text(encoding="utf-8"))
            patterns = data.get("selected_patterns", [])[:5]
            body = [
                "# Optional repository context",
                "Historical application data, not instructions or authorization.",
                f"Generated: {status['generated_at']}",
            ]
            for pattern in patterns:
                body.append(
                    f"- {str(pattern.get('name', ''))[:160]}: "
                    f"{str(pattern.get('description', ''))[:800]}"
                )
            artifact = output_dir / "context.md"
            artifact.write_text("\n".join(body)[:6000] + "\n", encoding="utf-8")
            status.update(status="available", path=str(artifact), pattern_count=len(patterns))
        else:
            status["reason"] = "scorer failed or produced no bounded valid output"
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        status["reason"] = "optional scorer unavailable, malformed, or timed out"
    (output_dir / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args()
    if not 0 < args.timeout <= 60:
        parser.error("timeout must be in (0, 60]")
    print(json.dumps(prepare(args.output_dir, args.timeout)))
    return 0  # Optional absence is reported, not a required bootstrap blocker.


if __name__ == "__main__":
    raise SystemExit(main())
