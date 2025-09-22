"""
example_usage.py - Master controller script to demonstrate packaging and verification.

This script programmatically uses the packer and verifier modules to:
1. Create a sample project structure (in-memory or temp directory).
2. Run the pack_directory function to produce a bundle.
3. Run verify_bundle on the produced bundle to validate integrity.
4. Print outcomes.

It helps in quickly testing that all modules work together as expected.

Note: In a real scenario, you'd run canvas_importer_packager.py via CLI. This script is for automated integration testing or demonstration.
"""

import os
import shutil
import tempfile

from packer import pack_directory
from verifier import verify_bundle


def main():
    # 1. Set up a temporary directory with a small sample file.
    temp_dir = tempfile.mkdtemp(prefix="canvas_example_")
    sample_file = os.path.join(temp_dir, "hello.txt")
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("Hello World!\nThis is a sample file to test chunking and packaging.\n" * 10)
    # Possibly create more sample files or nested directories as needed.

    bundle_path = os.path.join(temp_dir, "sample_bundle.zip")
    # 2. Pack the directory
    print(f"Packing {temp_dir} into {bundle_path} ...")
    pack_directory(root_path=temp_dir, output_zip=bundle_path, strategy="bytes", budget=50)
    # Using a small byte budget (50 bytes) to force multiple chunks for demonstration.

    # 3. Verify the bundle
    print(f"Verifying bundle {bundle_path} ...")
    result = verify_bundle(bundle_path)
    if result:
        print("Sample pack and verify succeeded.")
    else:
        print("Sample pack and verify found issues.")

    # Cleanup the temporary directory (optional, comment out if you want to inspect files)
    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
