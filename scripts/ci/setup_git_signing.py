#!/usr/bin/env python3
"""Configure persistent SSH commit signing for Copilot Agent Codespaces."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.github_rate_limit import GitHubRateLimitError, credentials_for_token, request

API_BASE = "https://api.github.com"
CODESPACE_TOKEN_SOURCES = ("CODEX_BACKUP_KEY", "CODEX_MASTER_KEY", "CODEX_ADMIN_KEY")


def api_request(
    token: str, method: str, path: str, body: dict | None = None
) -> tuple[int, dict | list | None]:
    try:
        response = request(
            method,
            API_BASE + path,
            credentials=credentials_for_token(token, sources=CODESPACE_TOKEN_SOURCES),
            body=body,
            user_agent="codex-git-signing-bootstrap/1.1",
        )
        return response.status, response.payload
    except GitHubRateLimitError:
        return 429, {"message": "All signing-capable credentials are rate-limited"}


def get_pat() -> str:
    for name in ("CODEX_BACKUP_KEY", "CODEX_MASTER_KEY", "GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def derive_public_key(private_key_path: Path) -> str:
    result = subprocess.run(
        ["ssh-keygen", "-y", "-f", str(private_key_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    public_base = result.stdout.strip()
    if not public_base:
        raise RuntimeError("ssh-keygen returned an empty public key")
    email = subprocess.run(
        ["git", "config", "--get", "user.email"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    comment = email or "GitHub Copilot Coding Agent"
    fields = public_base.split()
    if len(fields) < 2:
        raise RuntimeError("Derived SSH public key has an invalid format")
    return f"{fields[0]} {fields[1]} {comment}\n"


def ensure_private_key(key_path: Path) -> tuple[bool, str]:
    secret = (
        os.environ.get("_GIT_SIGNING_PRIVATE_KEY")
        or os.environ.get("GIT_SIGNING_PRIVATE_KEY")
        or ""
    )
    created = False

    if secret and "OPENSSH PRIVATE KEY" in secret:
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(secret.rstrip("\n") + "\n", encoding="utf-8")
        key_path.chmod(0o600)
    elif not key_path.is_file():
        key_path.parent.mkdir(parents=True, exist_ok=True)
        email = subprocess.run(
            ["git", "config", "--get", "user.email"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        comment = email or "GitHub Copilot Coding Agent"
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-C", comment, "-f", str(key_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        key_path.chmod(0o600)
        created = True

    return created, key_path.read_text(encoding="utf-8")


def configure_git(private_key_path: Path, public_key_line: str) -> None:
    subprocess.run(["git", "config", "--global", "gpg.format", "ssh"], check=True)
    subprocess.run(
        ["git", "config", "--global", "user.signingkey", str(private_key_path)], check=True
    )
    subprocess.run(["git", "config", "--global", "commit.gpgsign", "true"], check=True)
    subprocess.run(["git", "config", "--global", "tag.gpgsign", "true"], check=True)

    email = subprocess.run(
        ["git", "config", "--get", "user.email"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if email:
        fields = public_key_line.strip().split()
        if len(fields) >= 2:
            allowed_signers = Path.home() / ".ssh" / "allowed_signers"
            allowed_signers.parent.mkdir(parents=True, exist_ok=True)
            existing = (
                allowed_signers.read_text(encoding="utf-8") if allowed_signers.is_file() else ""
            )
            line = f"{email} {fields[0]} {fields[1]}\n"
            if line not in existing:
                allowed_signers.write_text(existing + line, encoding="utf-8")
                allowed_signers.chmod(0o600)
            subprocess.run(
                ["git", "config", "--global", "gpg.ssh.allowedSignersFile", str(allowed_signers)],
                check=True,
            )


def register_public_key(token: str, public_key_line: str, title: str) -> tuple[bool, str]:
    status, existing = api_request(token, "GET", "/user/ssh_signing_keys?per_page=100")
    if status == 200 and isinstance(existing, list):
        key_parts = set(public_key_line.strip().split()[:2])
        for item in existing:
            key = str((item or {}).get("key", "")).strip()
            if set(key.split()[:2]) == key_parts:
                return True, "already_registered"
    status, payload = api_request(
        token,
        "POST",
        "/user/ssh_signing_keys",
        {"key": public_key_line.strip(), "title": title},
    )
    if status in (201, 200):
        return True, "registered"
    message = payload.get("message", "") if isinstance(payload, dict) else ""
    return False, f"HTTP {status}: {message}" if message else f"HTTP {status}"


def sync_codespace_private_key(
    token: str, owner: str, repo: str, private_key: str
) -> tuple[bool, str]:
    try:
        from nacl.public import PublicKey, SealedBox
    except ImportError:
        return False, "PyNaCl unavailable"

    status, repo_data = api_request(token, "GET", f"/repos/{owner}/{repo}")
    if status != 200 or not isinstance(repo_data, dict) or not isinstance(repo_data.get("id"), int):
        return False, f"repository lookup HTTP {status}"

    status, public_key_data = api_request(token, "GET", "/user/codespaces/secrets/public-key")
    if status != 200 or not isinstance(public_key_data, dict):
        return False, f"Codespaces public-key HTTP {status}"

    try:
        public_key = PublicKey(base64.b64decode(public_key_data["key"]))
        ciphertext = SealedBox(public_key).encrypt(private_key.encode("utf-8"))
        encrypted_value = base64.b64encode(ciphertext).decode("ascii")
    except Exception:
        return False, "Codespaces public-key encryption failed"

    body = {
        "encrypted_value": encrypted_value,
        "key_id": public_key_data["key_id"],
        "selected_repository_ids": [int(repo_data["id"])],
    }
    status, _ = api_request(token, "PUT", "/user/codespaces/secrets/_GIT_SIGNING_PRIVATE_KEY", body)
    if status not in (201, 204):
        if status == 422:
            status, _ = api_request(
                token,
                "PUT",
                "/user/codespaces/secrets/_GIT_SIGNING_PRIVATE_KEY",
                {"encrypted_value": encrypted_value, "key_id": public_key_data["key_id"]},
            )
    if status not in (201, 204):
        return False, f"Codespaces secret HTTP {status}"
    return True, "synced"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="Aries-Serpent/_codex_")
    parser.add_argument("--key-path", default=str(Path.home() / ".ssh" / "codex_signing_ed25519"))
    register_group = parser.add_mutually_exclusive_group()
    register_group.add_argument("--register", dest="register", action="store_true")
    register_group.add_argument("--no-register", dest="register", action="store_false")
    parser.set_defaults(register=True)
    sync_group = parser.add_mutually_exclusive_group()
    sync_group.add_argument("--sync-codespace-secret", dest="sync_secret", action="store_true")
    sync_group.add_argument("--no-sync-codespace-secret", dest="sync_secret", action="store_false")
    parser.set_defaults(sync_secret=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    owner, repo_name = args.repo.split("/", 1)
    key_path = Path(args.key_path).expanduser()
    created, private_key = ensure_private_key(key_path)
    public_key_path = Path(f"{key_path}.pub")
    public_key_line = derive_public_key(key_path)
    public_key_path.write_text(public_key_line, encoding="utf-8")
    public_key_path.chmod(0o644)
    configure_git(key_path, public_key_line)

    result: dict[str, object] = {
        "key_created": created,
        "git_signing_configured": True,
        "public_key_registered": False,
        "public_key_registration_status": "disabled",
        "codespace_signing_key_synced": False,
        "codespace_signing_key_status": "disabled",
    }

    pat = get_pat()
    if args.register:
        if pat:
            codespace_name = os.environ.get("CODESPACE_NAME", "copilot-codespace")
            registered, status = register_public_key(
                pat, public_key_line, f"GitHub Copilot Codespace {codespace_name}"
            )
            result["public_key_registered"] = registered
            result["public_key_registration_status"] = status
        else:
            result["public_key_registration_status"] = "PAT unavailable"

    if args.sync_secret:
        if pat:
            synced, status = sync_codespace_private_key(pat, owner, repo_name, private_key)
            result["codespace_signing_key_synced"] = synced
            result["codespace_signing_key_status"] = status
        else:
            result["codespace_signing_key_status"] = "PAT unavailable"

    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("Git signing configured:", bool(result["git_signing_configured"]))
        print("Public key registered:", bool(result["public_key_registered"]))
        print("Codespace signing key synced:", bool(result["codespace_signing_key_synced"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
