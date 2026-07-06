import asyncio

from codex_core import Orchestrator


async def copilot_generate_fix(error_type: str) -> str:
    await asyncio.sleep(0.2)
    return f"# Proposed patch from Python callback for: {error_type}"


async def main() -> None:
    orchestrator = Orchestrator(copilot_generate_fix)
    patch = await orchestrator.triage_failure("ImportError")
    print("=== PATCH FROM RUST ORCHESTRATOR ===")
    print(patch)


if __name__ == "__main__":
    asyncio.run(main())
