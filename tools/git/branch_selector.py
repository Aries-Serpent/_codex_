import subprocess
from typing import Optional

def most_recent_branch() -> Optional[str]:
    """
    Return the most recently updated local branch name using `git for-each-ref`.
    Offline-first; relies on local refs. Falls back to 'main' if none found.
    """
    try:
        fmt = "%(committerdate:iso8601)%09%(refname:short)"
        out = subprocess.check_output(
            ["git", "for-each-ref", "--sort=-committerdate", f"--format={fmt}", "refs/heads"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        if not lines:
            return "main"
        # first line is most recent: "<date>\t<branch>"
        parts = lines[0].split("\t")
        return parts[-1] if len(parts) > 1 else "main"
    except Exception:
        return "main"
