"""Install a checksum-verified GitHub CLI into the current user's local bin."""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

VERSION = "2.83.0"
RELEASE_ROOT = f"https://github.com/cli/cli/releases/download/v{VERSION}"


def architecture() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "amd64"
    if machine in {"aarch64", "arm64"}:
        return "arm64"
    raise RuntimeError(f"unsupported architecture: {machine}")


def download_archive(target_architecture: str, destination: Path) -> None:
    if target_architecture == "amd64":
        url = "https://github.com/cli/cli/releases/download/v2.83.0/" "gh_2.83.0_linux_amd64.tar.gz"
    elif target_architecture == "arm64":
        url = "https://github.com/cli/cli/releases/download/v2.83.0/" "gh_2.83.0_linux_arm64.tar.gz"
    else:
        raise RuntimeError("unsupported GitHub CLI architecture")
    request = urllib.request.Request(url, headers={"User-Agent": "codex-maintainer-bootstrap"})
    with urllib.request.urlopen(request, timeout=30) as response:
        destination.write_bytes(response.read())


def download_checksums(destination: Path) -> None:
    request = urllib.request.Request(
        "https://github.com/cli/cli/releases/download/v2.83.0/gh_2.83.0_checksums.txt",
        headers={"User-Agent": "codex-maintainer-bootstrap"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        destination.write_bytes(response.read())


def expected_checksum(checksums: Path, archive_name: str) -> str:
    for line in checksums.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == archive_name:
            return parts[0]
    raise RuntimeError(f"checksum not found for {archive_name}")


def installed_version(executable: Path) -> bool:
    try:
        result = subprocess.run(
            [str(executable), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except OSError:
        return False
    return result.returncode == 0 and VERSION in result.stdout.splitlines()[0]


def main() -> int:
    target_dir = Path(os.environ.get("HOME", "")) / ".local" / "bin"
    target = target_dir / "gh"
    if installed_version(target):
        print(f"gh {VERSION} already installed at {target}")
        return 0

    archive_name = f"gh_{VERSION}_linux_{architecture()}.tar.gz"
    target_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex-gh-") as temporary:
        temp_dir = Path(temporary)
        archive = temp_dir / archive_name
        checksums = temp_dir / "checksums.txt"
        download_archive(architecture(), archive)
        download_checksums(checksums)
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        expected = expected_checksum(checksums, archive_name)
        if actual != expected:
            raise RuntimeError("GitHub CLI archive checksum mismatch")
        with tarfile.open(archive, "r:gz") as bundle:
            bundle.extractall(temp_dir, filter="data")
        source = temp_dir / f"gh_{VERSION}_linux_{architecture()}" / "bin" / "gh"
        staged = target_dir / f".gh-{os.getpid()}.tmp"
        shutil.copy2(source, staged)
        staged.chmod(0o755)
        staged.replace(target)

    if not installed_version(target):
        raise RuntimeError("installed GitHub CLI failed version validation")
    print(f"gh {VERSION} installed at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
