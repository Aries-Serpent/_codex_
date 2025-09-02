#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def sh(cmd, check=True, capture=False, input_bytes=None):
    proc = subprocess.run(cmd, check=False, capture_output=capture, input=input_bytes)
    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd, proc.stdout, proc.stderr)
    return proc


def now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")


def emit_question(step_no_desc, err_msg, ctx):
    print(f"Question from ChatGPT @codex {now()}:")
    print(f"While performing [{step_no_desc}], encountered the following error: {err_msg}")
    print(
        f"Context: {ctx}. What are the possible causes, and how can this be resolved while preserving intended functionality?"
    )


def sanitize_patch(src: Path, dst: Path):
    raw = src.read_bytes()
    # Strip UTF-8 BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    # Convert CRLF to LF
    raw = raw.replace(b"\r\n", b"\n")
    text = raw.decode("utf-8", errors="replace").splitlines()
    out = []
    fence = False
    for line in text:
        # toggle markdown fences
        if line.strip().startswith("```"):
            fence = not fence
            continue
        # strip common email quote prefix
        if line.startswith("> "):
            line = line[2:]
        out.append(line)
    cleaned = ("\n".join(out) + "\n").encode("utf-8")
    dst.write_bytes(cleaned)


def is_mbox(p: Path) -> bool:
    try:
        with p.open("rb") as f:
            head = f.read(5)
        return head.startswith(b"From ")
    except Exception:
        return False


def show_head(p: Path, n=20):
    try:
        with p.open("rb") as f:
            head = f.read(2048)
        print("----- patch head -----")
        print(head.decode("utf-8", errors="replace"))
        print("----- end head -----")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("patch", type=Path, help="Path to .diff/.patch file")
    args = ap.parse_args()

    try:
        sh(["git", "rev-parse", "--show-toplevel"], check=True)
    except subprocess.CalledProcessError as e:
        emit_question("1:verify repo root", str(e), "running in non-git directory")
        sys.exit(2)

    if not args.patch.exists() or args.patch.stat().st_size == 0:
        emit_question("1.1:verify patch presence", "patch missing or empty", f"patch={args.patch}")
        sys.exit(2)

    cleaned = args.patch.with_suffix(args.patch.suffix + ".cleaned")
    try:
        sanitize_patch(args.patch, cleaned)
    except Exception as e:
        emit_question("1.2:sanitize patch", repr(e), f"patch={args.patch}")
        sys.exit(2)

    show_head(cleaned, 30)

    # Try git apply (standard)
    try:
        sh(["git", "apply", "--index", "--reject", "--whitespace=fix", str(cleaned)], check=True)
        print("Applied with: git apply --index --reject --whitespace=fix")
        sys.exit(0)
    except subprocess.CalledProcessError as e1:
        # try ignore-space-change
        try:
            sh(
                ["git", "apply", "--index", "--reject", "--ignore-space-change", str(cleaned)],
                check=True,
            )
            print("Applied with: git apply --index --reject --ignore-space-change")
            sys.exit(0)
        except subprocess.CalledProcessError:
            # try mbox with git am --3way
            if is_mbox(cleaned):
                try:
                    sh(["git", "am", "--3way", str(cleaned)], check=True)
                    print("Applied with: git am --3way")
                    sys.exit(0)
                except subprocess.CalledProcessError as e3:
                    emit_question(
                        "2:git am --3way",
                        e3.stderr.decode("utf-8", errors="replace"),
                        "applying mbox-formatted patch",
                    )
                    # fall through
            # try GNU patch if available
            if shutil.which("patch"):
                try:
                    sh(
                        ["patch", "-p1", "--backup", "--reject-file=-"],
                        check=True,
                        capture=True,
                        input_bytes=cleaned.read_bytes(),
                    )
                    print("Applied with: patch -p1")
                    sys.exit(0)
                except subprocess.CalledProcessError as e4:
                    emit_question(
                        "2:patch -p1",
                        e4.stderr.decode("utf-8", errors="replace"),
                        "applying unified/context diff via GNU patch",
                    )
            # all strategies failed
            emit_question(
                "2:git apply --index --reject --whitespace=fix",
                e1.stderr.decode("utf-8", errors="replace") or "patch with only garbage",
                f"file={args.patch} cleaned={cleaned}",
            )
            print("\nSuggested next steps:")
            print(" - Regenerate patch from PR #407 or exact commit range:")
            print("   git fetch origin pull/407/head:pr-407 && git checkout pr-407")
            print(
                "   git diff --binary --patch --no-renames origin/0B_base_...HEAD > regenerated.diff"
            )
            print("   git checkout - && git apply --index --3way regenerated.diff")
            print(" - Or cherry-pick the commits from pr-407 onto your branch (3-way).")
            sys.exit(3)


if __name__ == "__main__":
    main()
