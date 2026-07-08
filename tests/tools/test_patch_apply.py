"""
Test Patch Apply

Test module for patch apply.
"""

import subprocess
import sys


def test_patch_apply_add_update_delete(tmp_path):
    patch = tmp_path / "p.diff"
    target = tmp_path / "foo.txt"
    patch.write_text(
        "\n".join(
            [
                "*** Begin Patch",
                f"*** Add File: {target}",
                "hello",
                "*** End Patch",
                "*** Begin Patch",
                f"*** Update File: {target}",
                "world",
                "*** End Patch",
                "*** Begin Patch",
                f"*** Delete File: {target}",
                "*** End Patch",
            ]
        ),
        encoding="utf-8",
    )
    code = subprocess.call(
        [
            sys.executable,
            "-c",
            "import tools.patch_apply as p; p.main()",
            "--patch-file",
            str(patch),
        ]
    )
    assert code == 0, "code is not valid"
