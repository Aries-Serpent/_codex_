#!/usr/bin/env python3
import subprocess


def main():
    try:
        out = subprocess.check_output(
            ["git","for-each-ref","--sort=-committerdate","--format=%(refname:short) %(committerdate:iso8601)","refs/heads"],
            text=True
        ).strip().splitlines()
        print(out[0].split()[0] if out else "main")
    except Exception:
        print("main")
if __name__ == "__main__": main()
