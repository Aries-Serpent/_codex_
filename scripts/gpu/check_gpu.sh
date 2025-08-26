# BEGIN: CODEX_GPU_CHECK
#!/usr/bin/env bash
set -euo pipefail
umask 077
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "GPU detected:"
  nvidia-smi || true
else
  echo "No NVIDIA GPU detected."
fi
# END: CODEX_GPU_CHECK
