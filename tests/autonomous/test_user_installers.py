"""Offline tests for user-local devcontainer runtime installers."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts.autonomous import install_gh_user

ROOT = Path(__file__).resolve().parents[2]
NODE_INSTALLER = ROOT / "scripts" / "autonomous" / "install_node_user.sh"
CHROMIUM_INSTALLER = ROOT / "scripts" / "autonomous" / "install_chromium_user.sh"
POST_START = ROOT / ".devcontainer" / "scripts" / "post-start.sh"


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def isolated_path(bin_dir: Path) -> str:
    return f"{bin_dir}:/usr/bin:/bin"


def test_gh_installer_uses_literal_release_urls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    urls: list[str] = []

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def read(self) -> bytes:
            return b"artifact"

    def fake_urlopen(request: Any, timeout: int) -> Response:
        assert timeout == 30
        urls.append(request.full_url)
        return Response()

    monkeypatch.setattr(install_gh_user.urllib.request, "urlopen", fake_urlopen)

    install_gh_user.download_archive("amd64", tmp_path / "amd64.tar.gz")
    install_gh_user.download_archive("arm64", tmp_path / "arm64.tar.gz")

    assert urls == [
        "https://github.com/cli/cli/releases/download/v2.83.0/gh_2.83.0_linux_amd64.tar.gz",
        "https://github.com/cli/cli/releases/download/v2.83.0/gh_2.83.0_linux_arm64.tar.gz",
    ]
    with pytest.raises(RuntimeError):
        install_gh_user.download_archive("unexpected", tmp_path / "invalid.tar.gz")


def test_post_start_uses_configurable_bind_and_secret_files() -> None:
    script = POST_START.read_text(encoding="utf-8")

    assert '--host "${CLI_API_BIND_HOST}"' in script
    assert "UI_BOOTSTRAP_BROWSER_FILE" in script
    assert 'printf \'%s\' "$UI_BOOTSTRAP_BROWSER" > "$UI_BOOTSTRAP_BROWSER_FILE"' in script
    assert "UI launch fragment: #codex_ui_bootstrap=${UI_BOOTSTRAP_BROWSER}" not in script


def test_node_installer_uses_supported_feature_runtime_without_apk(tmp_path: Path) -> None:
    home = tmp_path / "home"
    feature_bin = tmp_path / "feature-bin"
    home.mkdir()
    feature_bin.mkdir()
    write_executable(
        feature_bin / "node",
        "#!/usr/bin/env bash\nprintf 'v24.22.3\\n'\n",
    )
    write_executable(
        feature_bin / "npm",
        "#!/usr/bin/env bash\nprintf '11.11.0\\n'\n",
    )
    write_executable(
        feature_bin / "npx",
        "#!/usr/bin/env bash\nprintf '11.11.0\\n'\n",
    )
    (tmp_path / "bin").mkdir()
    env = os.environ | {
        "HOME": str(home),
        "PATH": isolated_path(tmp_path / "bin"),
        "CODEX_NODE_FEATURE_BIN": str(feature_bin / "node"),
    }

    result = subprocess.run(
        ["bash", str(NODE_INSTALLER)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "node=v24.22.3 npm=11.11.0" in result.stdout
    assert (home / ".local" / "bin" / "node").resolve() == feature_bin / "node"


def test_node_installer_reuses_valid_user_runtime(tmp_path: Path) -> None:
    home = tmp_path / "home"
    runtime_bin = home / ".local" / "opt" / "codex-node" / "bin"
    fake_bin = tmp_path / "bin"
    runtime_bin.mkdir(parents=True)
    fake_bin.mkdir()
    for name, output in (("node", "v22.22.2"), ("npm", "10.9.2"), ("npx", "10.9.2")):
        write_executable(runtime_bin / name, f"#!/usr/bin/env bash\nprintf '{output}\\n'\n")
    download_log = tmp_path / "download.log"
    write_executable(
        fake_bin / "curl",
        '#!/usr/bin/env bash\nprintf download >> "$DOWNLOAD_LOG"\nexit 91\n',
    )
    env = os.environ | {
        "HOME": str(home),
        "PATH": isolated_path(fake_bin),
        "DOWNLOAD_LOG": str(download_log),
    }

    result = subprocess.run(
        ["bash", str(NODE_INSTALLER)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not download_log.exists()
    assert (home / ".local" / "bin" / "node").resolve() == runtime_bin / "node"


def test_node_fallback_rejects_checksum_mismatch_without_network(tmp_path: Path) -> None:
    home = tmp_path / "home"
    fake_bin = tmp_path / "bin"
    home.mkdir()
    fake_bin.mkdir()
    curl_log = tmp_path / "curl.log"
    write_executable(
        fake_bin / "curl",
        """#!/usr/bin/env bash
printf '%s\n' "$@" > "$CURL_LOG"
output=''
while [ "$#" -gt 0 ]; do
    if [ "$1" = '-o' ]; then
        output="$2"
        shift 2
        continue
    fi
    shift
done
printf 'corrupted artifact' > "$output"
""",
    )
    env = os.environ | {
        "HOME": str(home),
        "PATH": isolated_path(fake_bin),
        "CODEX_NODE_FORCE_FALLBACK": "1",
        "CURL_LOG": str(curl_log),
    }

    result = subprocess.run(
        ["bash", str(NODE_INSTALLER)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "FAILED" in result.stdout or "WARNING" in result.stdout
    assert "node-v22.22.2-linux-x64.tar.gz" in curl_log.read_text(encoding="utf-8")
    assert not (home / ".local" / "opt" / "codex-node" / "bin" / "node").exists()


def test_chromium_installer_uses_pinned_playwright_revision(tmp_path: Path) -> None:
    home = tmp_path / "home"
    workspace = tmp_path / "workspace"
    browsers = workspace / "cognitive_app" / "node_modules" / "playwright-core"
    browser = home / ".cache" / "ms-playwright" / "chromium-1254" / "chrome-linux" / "chrome"
    browsers.mkdir(parents=True)
    browser.parent.mkdir(parents=True)
    (browsers / "browsers.json").write_text(
        '{"browsers":[{"name":"chromium","revision":"1254"}]}',
        encoding="utf-8",
    )
    write_executable(browser, "#!/usr/bin/env bash\nprintf 'Chromium 158.0.8127.18\\n'\n")
    env = os.environ | {
        "HOME": str(home),
        "CODESPACE_VSCODE_FOLDER": str(workspace),
        "PATH": "/usr/bin:/bin",
    }

    result = subprocess.run(
        ["bash", str(CHROMIUM_INSTALLER)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Chromium 158.0.8127.18" in result.stdout
    assert (home / ".local" / "bin" / "chromium").resolve() == browser


def test_chromium_installer_bootstraps_missing_playwright_browser(tmp_path: Path) -> None:
    home = tmp_path / "home"
    workspace = tmp_path / "workspace"
    playwright = workspace / "cognitive_app" / "node_modules" / "playwright-core"
    feature_bin = tmp_path / "feature-bin"
    playwright.mkdir(parents=True)
    feature_bin.mkdir()
    home.mkdir()
    (playwright / "browsers.json").write_text(
        '{"browsers":[{"name":"chromium","revision":"1254"}]}',
        encoding="utf-8",
    )
    (playwright / "cli.js").write_text("// offline fixture\n", encoding="utf-8")
    install_log = tmp_path / "install.log"
    write_executable(
        feature_bin / "node",
        """#!/usr/bin/env bash
printf '%s\n' "$@" > "$INSTALL_LOG"
browser="$HOME/.cache/ms-playwright/chromium-1254/chrome-linux/chrome"
mkdir -p "$(dirname "$browser")"
printf '#!/usr/bin/env bash\nprintf "Chromium bootstrapped\\\\n"\\n' > "$browser"
chmod +x "$browser"
""",
    )
    env = os.environ | {
        "HOME": str(home),
        "CODESPACE_VSCODE_FOLDER": str(workspace),
        "CODEX_NODE_FEATURE_BIN": str(feature_bin / "node"),
        "INSTALL_LOG": str(install_log),
        "PATH": "/usr/bin:/bin",
    }

    result = subprocess.run(
        ["bash", str(CHROMIUM_INSTALLER)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "install\nchromium" in install_log.read_text(encoding="utf-8")
    assert "Chromium bootstrapped" in result.stdout


def test_installers_do_not_depend_on_apk() -> None:
    assert "apk " not in NODE_INSTALLER.read_text(encoding="utf-8")
    assert "apk " not in CHROMIUM_INSTALLER.read_text(encoding="utf-8")
