#!/bin/bash
# >>> CODEX SESSION HOOKS (auto-injected)
if [ -f "scripts/session_logging.sh" ]; then
  . "scripts/session_logging.sh"
elif [ -f "$(dirname "$0")/scripts/session_logging.sh" ]; then
  . "$(dirname "$0")/scripts/session_logging.sh"
fi
codex_session_start "$0" "$@"
trap 'codex_session_end $?' EXIT
# <<< CODEX SESSION HOOKS


echo "=================================="
echo "Welcome to openai/codex-universal!"
echo "=================================="

/opt/codex/setup_universal.sh

. "$(dirname "$0")/setup.sh"
run_user_setup

echo "Environment ready. Dropping you into a bash shell."
exec bash --login "$@"
