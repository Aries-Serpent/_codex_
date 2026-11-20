#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local/opt/codex-node"
LOCAL_BIN="${HOME}/.local/bin"
NODE_VERSION="22.22.2"

find_feature_runtime() {
    local candidate node_version node_dir
    local candidates=(
        "$PREFIX/bin/node"
        "${CODEX_NODE_FEATURE_BIN:-}"
        "${HOME}/.local/share/mise/shims/node"
        "/usr/local/share/nvm/current/bin/node"
        "/usr/local/bin/node"
        "$(command -v node 2>/dev/null || true)"
    )

    for candidate in "${candidates[@]}"; do
        [ -n "$candidate" ] && [ -x "$candidate" ] || continue
        node_version="$($candidate --version 2>/dev/null || true)"
        case "$node_version" in
            v22.* | v24.* | v26.*) ;;
            *) continue ;;
        esac
        node_dir="$(dirname "$candidate")"
        [ -x "$node_dir/npm" ] && [ -x "$node_dir/npx" ] || continue
        NODE_BIN="$candidate"
        NPM_BIN="$node_dir/npm"
        NPX_BIN="$node_dir/npx"
        return 0
    done
    return 1
}

install_pinned_runtime() {
    local architecture artifact checksum stage_dir tmp_dir
    architecture="$(uname -m)"
    case "$architecture" in
        x86_64)
            artifact="node-v${NODE_VERSION}-linux-x64.tar.gz"
            checksum="978978a635eef872fa68beae09f0aad0bbbae6757e444da80b570964a97e62a3"
            ;;
        aarch64 | arm64)
            artifact="node-v${NODE_VERSION}-linux-arm64.tar.gz"
            checksum="b2f3a96f31486bfc365192ad65ced14833ad2a3c2e1bcefec4846902f264fa28"
            ;;
        *)
            echo "Unsupported Node fallback architecture: $architecture" >&2
            return 1
            ;;
    esac

    mkdir -p "$(dirname "$PREFIX")"
    tmp_dir="$(mktemp -d)"
    stage_dir="$(mktemp -d "${PREFIX}.tmp.XXXXXX")"
    trap 'rm -rf "$tmp_dir" "$stage_dir"' RETURN
    curl -fsSL -o "$tmp_dir/$artifact" \
        "https://nodejs.org/dist/v${NODE_VERSION}/${artifact}"
    printf '%s  %s\n' "$checksum" "$artifact" > "$tmp_dir/SHA256SUMS"
    (cd "$tmp_dir" && sha256sum -c SHA256SUMS)

    tar -xzf "$tmp_dir/$artifact" -C "$stage_dir" --strip-components=1
    [ -x "$stage_dir/bin/node" ]
    [ -x "$stage_dir/bin/npm" ]
    [ -x "$stage_dir/bin/npx" ]
    rm -rf "$PREFIX"
    mv "$stage_dir" "$PREFIX"
    trap 'rm -rf "$tmp_dir"' RETURN
    NODE_BIN="$PREFIX/bin/node"
    NPM_BIN="$PREFIX/bin/npm"
    NPX_BIN="$PREFIX/bin/npx"
}

if [ "${CODEX_NODE_FORCE_FALLBACK:-0}" = "1" ] || ! find_feature_runtime; then
    install_pinned_runtime
fi

NODE_ACTUAL="$("$NODE_BIN" --version)"
NPM_ACTUAL="$(PATH="$(dirname "$NODE_BIN"):${PATH}" "$NPM_BIN" --version)"
case "$NODE_ACTUAL" in
    v22.* | v24.* | v26.*) ;;
    *) exit 1 ;;
esac
[ -n "$NPM_ACTUAL" ]

mkdir -p "$LOCAL_BIN"
ln -sfn "$NODE_BIN" "$LOCAL_BIN/node"
ln -sfn "$NPM_BIN" "$LOCAL_BIN/npm"
ln -sfn "$NPX_BIN" "$LOCAL_BIN/npx"
printf 'node=%s npm=%s source=%s\n' "$NODE_ACTUAL" "$NPM_ACTUAL" "$NODE_BIN"
