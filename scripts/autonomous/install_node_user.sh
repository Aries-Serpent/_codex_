#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local/opt/codex-node"
LOCAL_BIN="${HOME}/.local/bin"
NODE_VERSION="24.22.3"
NPM_VERSION="11.11.0"

if [ -x "${PREFIX}/usr/bin/node" ] && \
   LD_LIBRARY_PATH="${PREFIX}/usr/lib:${PREFIX}/lib" \
   "${PREFIX}/usr/bin/node" --version | grep -q "^v${NODE_VERSION}$"; then
    echo "Node ${NODE_VERSION} already installed at ${PREFIX}"
else
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    cd "$TMP_DIR"
    apk fetch --recursive nodejs npm >/dev/null
    rm -rf "$PREFIX"
    mkdir -p "$PREFIX"
    for package in *.apk; do
        tar -xzf "$package" -C "$PREFIX"
    done
fi

mkdir -p "$LOCAL_BIN"
cat > "${LOCAL_BIN}/node" <<'EOF'
#!/usr/bin/env bash
PREFIX="${HOME}/.local/opt/codex-node"
export LD_LIBRARY_PATH="${PREFIX}/usr/lib:${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export NODE_ICU_DATA="${PREFIX}/usr/share/icu/76.1"
exec "${PREFIX}/usr/bin/node" "$@"
EOF
cat > "${LOCAL_BIN}/npm" <<'EOF'
#!/usr/bin/env bash
PREFIX="${HOME}/.local/opt/codex-node"
export LD_LIBRARY_PATH="${PREFIX}/usr/lib:${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export NODE_ICU_DATA="${PREFIX}/usr/share/icu/76.1"
export PATH="${PREFIX}/usr/bin:${PATH}"
exec "${PREFIX}/usr/bin/npm" "$@"
EOF
cat > "${LOCAL_BIN}/npx" <<'EOF'
#!/usr/bin/env bash
PREFIX="${HOME}/.local/opt/codex-node"
export LD_LIBRARY_PATH="${PREFIX}/usr/lib:${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export NODE_ICU_DATA="${PREFIX}/usr/share/icu/76.1"
export PATH="${PREFIX}/usr/bin:${PATH}"
exec "${PREFIX}/usr/bin/npx" "$@"
EOF
chmod 0755 "${LOCAL_BIN}/node" "${LOCAL_BIN}/npm" "${LOCAL_BIN}/npx"

NODE_ACTUAL="$("${LOCAL_BIN}/node" --version)"
NPM_ACTUAL="$("${LOCAL_BIN}/npm" --version)"
[ "$NODE_ACTUAL" = "v${NODE_VERSION}" ]
[ "$NPM_ACTUAL" = "$NPM_VERSION" ]
printf 'node=%s npm=%s\n' "$NODE_ACTUAL" "$NPM_ACTUAL"
