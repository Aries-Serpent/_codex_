# Shell Session Hooks

The `scripts/session_hooks.sh` script exposes two functions for lightweight
session logging:

- `codex_session_start [args…]` – record the start of a shell session.
- `codex_session_end [exit_code]` – record the end of a session and exit code.

Both functions rely on a small Python snippet to append newline-delimited JSON
entries to the directory indicated by `CODEX_SESSION_LOG_DIR` (default
`.codex/sessions`). After each Python call the script checks the exit status. If
logging fails, an error message is written to `stderr` but the calling shell
continues.

Example:

```bash
. scripts/session_hooks.sh
codex_session_start "my-cli" "$@"
trap 'codex_session_end $?' EXIT
```
The start hook stores the current time so that the end hook can compute and
record the session duration in seconds. Both hooks are best-effort and will not
abort the main script when logging errors occur.
