"""Inject agent_context.json variables into GITHUB_ENV.

Reads .codex/agent_context.json and writes all non-private, non-empty
key=value pairs to the GITHUB_ENV file so the Copilot agent session
sees them as environment variables.

Skips keys that start with '_' (private/internal) and empty values.
Keys must match the POSIX pattern [A-Za-z_][A-Za-z0-9_]* to be safe.
Values are stripped of all control characters before writing.
"""

import json
import os
import re
import sys

CONTEXT_FILE = ".codex/agent_context.json"

# Only allow POSIX-safe environment variable names
_SAFE_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _sanitize_value(value: str) -> str:
    """Strip all control characters from an env-var value.

    This prevents GITHUB_ENV injection attacks (e.g. embedded newlines
    that introduce extra KEY=value lines or multiline-delimiter sequences).
    """
    return re.sub(r"[\x00-\x1f\x7f]", " ", value).strip()


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
            if not _SAFE_KEY_RE.match(key):
                print(f"Skipping unsafe key: {key!r}")
                continue
            safe_value = _sanitize_value(str(value))
            if not safe_value:
                continue
            env_fh.write(f"{key}={safe_value}\n")
            injected += 1

    print(f"Injected {injected} variables into GITHUB_ENV")
    return 0


if __name__ == "__main__":
    sys.exit(main())
