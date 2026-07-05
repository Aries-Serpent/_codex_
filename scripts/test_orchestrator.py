import asyncio
import logging
from typing import Final

from codex_core import Orchestrator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

SAMPLE_ERROR: Final[str] = "ImportError"


async def copilot_generate_fix(error_type: str, log_excerpt: str) -> str:
    await asyncio.sleep(0.2)

    # Example unresolved token path for telemetry testing:
    if error_type == "ValidationError":
        return "UNABLE_TO_CLASSIFY"

    return (
        f"# Proposed fix for {error_type}\n"
        f"# Context: {log_excerpt}\n"
        "def apply_fix():\n"
        "    return 'patched'\n"
    )


async def main() -> None:
    orchestrator = Orchestrator(copilot_generate_fix, timeout_seconds=60)

    patch = await orchestrator.triage_failure(SAMPLE_ERROR)
    states = await orchestrator.get_state()
    telemetry = await orchestrator.get_telemetry()

    assert isinstance(patch, str), "Expected patch as string"
    assert states[SAMPLE_ERROR] in {"patched", "unresolved"}, f"Invalid state: {states[SAMPLE_ERROR]}"
    assert telemetry["total_triage"] >= 1

    print("=== PATCH FROM RUST ORCHESTRATOR ===")
    print(patch)
    print("=== STATES ===")
    print(states)
    print("=== TELEMETRY ===")
    print(telemetry)

    batch = await orchestrator.triage_batch(
        ["TimeoutError", "ValidationError", "ImportError"],
        max_concurrency=2,
    )
    print("=== BATCH RESULT ===")
    print(batch)

    states2 = await orchestrator.get_state()
    telemetry2 = await orchestrator.get_telemetry()
    print("=== STATES (POST-BATCH) ===")
    print(states2)
    print("=== TELEMETRY (POST-BATCH) ===")
    print(telemetry2)


if __name__ == "__main__":
    asyncio.run(main())
