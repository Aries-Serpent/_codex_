from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Generate a CycloneDX SBOM if tooling is available."""

    tool = shutil.which("cyclonedx-bom") or shutil.which("cyclonedx-py")
    if tool is None:
        print("cyclonedx tool not installed", file=sys.stderr)
        sys.exit(1)
    out = Path("artifacts/sbom.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [tool, "-o", str(out)] if "cyclonedx-py" in tool else [tool, "--output", str(out)]
    subprocess.run(cmd, check=False)
    print(f"SBOM written to {out}")


if __name__ == "__main__":
    main()
