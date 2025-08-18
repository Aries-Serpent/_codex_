#!/usr/bin/env python3
"""Placeholder workflow helper.

This script intentionally keeps logic minimal while reserving the interface
for future expansion. It enforces the repository policy that GitHub Actions
workflows must not be activated.
"""
from __future__ import annotations

import argparse

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True


def main() -> None:
    parser = argparse.ArgumentParser(description="codex workflow helper")
    parser.add_argument("--apply", action="store_true", help="no-op")
    parser.parse_args()
    print("codex workflow executed")


if __name__ == "__main__":
    assert DO_NOT_ACTIVATE_GITHUB_ACTIONS, "GitHub Actions must remain untouched."
    main()
