import subprocess


def git_out(args):
    try:
        return subprocess.check_output(["git"] + args, text=True).strip()
    except Exception:
        return ""


def changed_since(ref="HEAD~1"):
    return git_out(["diff", "--name-status", ref, "HEAD"])
