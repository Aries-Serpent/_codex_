
# Minimal helpers for GitHub App auth; replace with full implementation.
import os, time, jwt, httpx

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID")
GITHUB_PRIVATE_KEY_PEM = os.getenv("GITHUB_PRIVATE_KEY_PEM")  # PEM text

def _app_jwt() -> str:
    if not (GITHUB_APP_ID and GITHUB_PRIVATE_KEY_PEM):
        raise RuntimeError("GitHub App env not configured")
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (9 * 60),
        "iss": GITHUB_APP_ID,
    }
    return jwt.encode(payload, GITHUB_PRIVATE_KEY_PEM, algorithm="RS256")

async def installation_token() -> str:
    token_url = f"https://api.github.com/app/installations/{GITHUB_INSTALLATION_ID}/access_tokens"
    headers = {"Authorization": f"Bearer {_app_jwt()}", "Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(token_url, headers=headers)
        r.raise_for_status()
        return r.json()["token"]

async def create_or_update_pr(repo: str, title: str, body: str, base: str, head: str, labels: list[str] | None = None) -> str:
    token = await installation_token()
    api = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(api, headers=headers, json={"title": title, "body": body, "base": base, "head": head})
        r.raise_for_status()
        pr = r.json()
        pr_url = pr.get("html_url", "")
        if labels:
            issues_api = f"https://api.github.com/repos/{repo}/issues/{pr['number']}"
            await client.patch(issues_api, headers=headers, json={"labels": labels})
        return pr_url
