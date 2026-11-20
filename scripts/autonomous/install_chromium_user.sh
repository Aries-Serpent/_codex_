#!/usr/bin/env bash
set -euo pipefail

LOCAL_BIN="${HOME}/.local/bin"
WORKSPACE="${CODESPACE_VSCODE_FOLDER:-$(pwd)}"
PLAYWRIGHT_ROOT="${PLAYWRIGHT_BROWSERS_PATH:-${HOME}/.cache/ms-playwright}"
BROWSERS_JSON="$WORKSPACE/cognitive_app/node_modules/playwright-core/browsers.json"

resolve_chromium() {
    local candidate revision
    local candidates=(
        "${CODEX_CHROMIUM_EXECUTABLE:-}"
        "$(command -v chromium 2>/dev/null || true)"
        "$(command -v chromium-browser 2>/dev/null || true)"
        "$(command -v google-chrome 2>/dev/null || true)"
        "/usr/bin/chromium"
        "/usr/bin/chromium-browser"
        "/usr/bin/google-chrome"
    )
    for candidate in "${candidates[@]}"; do
        [ -n "$candidate" ] && [ "$candidate" != "$LOCAL_BIN/chromium" ] && \
            [ -x "$candidate" ] || continue
        "$candidate" --version >/dev/null 2>&1 || continue
        CHROMIUM_BIN="$candidate"
        return 0
    done

    [ -f "$BROWSERS_JSON" ] || return 1
    revision="$(python3 - "$BROWSERS_JSON" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    metadata = json.load(stream)
print(next(item["revision"] for item in metadata["browsers"] if item["name"] == "chromium"))
PY
)"
    [[ "$revision" =~ ^[0-9]+$ ]] || return 1
    for candidate in \
        "$PLAYWRIGHT_ROOT/chromium-$revision/chrome-linux/chrome" \
        "$PLAYWRIGHT_ROOT/chromium-$revision/chrome-linux64/chrome"; do
        [ -x "$candidate" ] || continue
        "$candidate" --version >/dev/null 2>&1 || continue
        CHROMIUM_BIN="$candidate"
        return 0
    done
    return 1
}

install_playwright_chromium() {
    local node_bin playwright_cli
    playwright_cli="$WORKSPACE/cognitive_app/node_modules/playwright-core/cli.js"
    node_bin="${CODEX_NODE_FEATURE_BIN:-$(command -v node 2>/dev/null || true)}"
    [ -x "$node_bin" ] && [ -f "$playwright_cli" ] || return 1
    PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_ROOT" \
        "$node_bin" "$playwright_cli" install chromium
}

if ! resolve_chromium; then
    install_playwright_chromium || {
        echo "Chromium unavailable; Playwright package or Node runtime is missing." >&2
        exit 1
    }
    resolve_chromium || {
        echo "Playwright Chromium installation did not produce an executable." >&2
        exit 1
    }
fi

mkdir -p "$LOCAL_BIN"
ln -sfn "$CHROMIUM_BIN" "$LOCAL_BIN/chromium"
"$LOCAL_BIN/chromium" --version
