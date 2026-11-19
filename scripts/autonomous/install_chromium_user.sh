#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local/opt/codex-chromium"
LOCAL_BIN="${HOME}/.local/bin"

if [ ! -x "${PREFIX}/usr/bin/chromium-browser" ]; then
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    cd "$TMP_DIR"
    apk fetch --recursive chromium >/dev/null
    mkdir -p "$PREFIX"
    for package in *.apk; do
        tar -xzf "$package" -C "$PREFIX"
    done
fi

mkdir -p "$LOCAL_BIN"
cat > "${LOCAL_BIN}/chromium" <<'EOF'
#!/usr/bin/env bash
PREFIX="${HOME}/.local/opt/codex-chromium"
export LD_LIBRARY_PATH="${PREFIX}/usr/lib:${PREFIX}/usr/lib/pulseaudio:${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
exec "${PREFIX}/usr/bin/chromium-browser" "$@"
EOF
chmod 0755 "${LOCAL_BIN}/chromium"
"${LOCAL_BIN}/chromium" --version
