#!/usr/bin/env python3
"""Print environment details for reproducibility."""

from __future__ import annotations

import json
import sys

from codex_ml.utils.env import environment_summary


def main() -> None:
    info = environment_summary()
    json.dump(info, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
