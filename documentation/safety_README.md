<!-- BEGIN: CODEX_SAFETY_DOCS -->

# Safety Filters & Sandbox

## Filters

- **Blocklist/Allowlist**: literal matches (case-insensitive).
- **Regex Heuristics**: basic credential and destructive command patterns.
- **Logits Masking**: helper to set banned token ids to -inf before sampling.

## Sandbox

- Stdlib-only confinement via resource limits (CPU/memory/NOFILE), minimal env, umask 077, ephemeral working directory.
- Optional: integrate with **firejail** or **docker** if present (not required).

## Permissions & Logs

- Output directories created with **0o700**, files effectively **0o600** via `umask(0o077)`.
- Logs scrub simple secret-looking strings (password, api_key, secret, AKIA).

## Limitations

- Not a full VM; best-effort sandbox. For stronger isolation, use containers or VMs.
- Network isolation is best-effort unless firejail/docker are used.

**Acceptance**: Dangerous outputs filtered; sandbox prevents filesystem modification during evaluation.
