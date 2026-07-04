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
    return (
        f"# Proposed fix for {error_type}\n"
        f"# Context: {log_excerpt}\n"
        "def apply_fix():\n"
        "    return 'patched'\n"
    )


async def main() -> None:
    orchestrator = Orchestrator(copilot_generate_fix, timeout_seconds=60)

    patch = await orchestrator.triage_failure(SAMPLE_ERROR)
    state = await orchestrator.get_state()

    assert isinstance(patch, str), "Expected patch as string"
    assert state == "patched", f"Unexpected final state: {state}"

    print("=== PATCH FROM RUST ORCHESTRATOR ===")
    print(patch)
    print("=== FINAL STATE ===")
    print(state)


if __name__ == "__main__":
    asyncio.run(main())