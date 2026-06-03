"""Inject agent_context.json variables into GITHUB_ENV.

Reads .codex/agent_context.json and writes all non-private, non-empty
key=value pairs to the GITHUB_ENV file so the Copilot agent session
sees them as environment variables.

Skips keys that start with '_' (private/internal) and empty values.
"""

import json
import os
import sys

CONTEXT_FILE = ".codex/agent_context.json"


def main() -> int:
    github_env = os.environ.get("GITHUB_ENV")
    if not github_env:
        print("Warning: GITHUB_ENV not set — skipping variable injection")
        return 0

    try:
        with open(CONTEXT_FILE) as fh:
            ctx = json.load(fh)
    except FileNotFoundError:
        print(f"No {CONTEXT_FILE} — skipping (run copilot-agent-vars-bootstrap first)")
        return 0
    except json.JSONDecodeError as exc:
        print(f"Warning: {CONTEXT_FILE} is not valid JSON: {exc}")
        return 0

    injected = 0
    with open(github_env, "a") as env_fh:
        for key, value in ctx.items():
            if key.startswith("_") or not value:
                continue
            # Sanitise: strip newlines to prevent GITHUB_ENV multi-line injection
            safe_value = str(value).replace("\n", " ").replace("\r", " ")
            env_fh.write(f"{key}={safe_value}\n")
            injected += 1

    print(f"Injected {injected} variables into GITHUB_ENV")
    return 0


if __name__ == "__main__":
    sys.exit(main())
