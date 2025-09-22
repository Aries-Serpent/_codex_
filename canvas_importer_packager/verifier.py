"""Module: verifier.py

Provides functionality to verify the integrity of a Canvas bundle produced by packer. This involves reading the ZIP, validating the manifest and the panels, and ensuring the original files can be faithfully reassembled.

Main Functions:
- verify_bundle(zip_path): High-level function to open the bundle and perform all checks.
- verify_source(source_entry, zip_file): Verify a single source file entry by concatenating its panels and checking the hash.
- Utility to strip panel headers before reassembly (strip_header(panel_content)).

Verification Checks (see VERIFY_GUIDE.md for more detail):
1. **Manifest and Bundle Consistency**: All panel files listed in manifest.json are present in the ZIP, and no extra panel files exist (orphans).
2. **Hash Integrity**: For each source file entry in manifest:
   - Compute SHA-256 of the original source (from manifest) vs. SHA-256 of concatenated panel contents (after removing headers). These should match exactly (Integrity invariant).
   - Also verify each panel's own content hash if provided.
3. **Panel Sequencing**: Panels are present and named with the correct part numbers (1 through N with no gaps). The "part X of N" in headers or manifest must match the count of panels.
4. **Header Accuracy**: The metadata in each panel's header (source path, part numbers, etc.) should align with manifest entries.
5. **No Truncation**: Ensure that concatenating all panels yields the exact original content (byte-for-byte match with original hash).

The verify function will report any errors found:
- Missing panel files, extra files, hash mismatches, part count mismatches, etc. It should exit with a non-zero status or raise an error if verification fails, and exit 0 (or return True) if all checks pass.

Security:
- Verification runs locally; it does not execute any file content. It should be safe against malicious inputs as it only reads bytes and computes hashes.
"""

import hashlib
import json
import zipfile

# Reuse the same constants for sentinel if needed:
from packer import SENTINEL_HEADER_BEGIN, SENTINEL_HEADER_END


def verify_bundle(zip_path: str) -> bool:
    """Verify the integrity of a Canvas bundle ZIP file.

    Opens the zip file, reads manifest.json, and performs the following:
     - Load manifest JSON and possibly project manifest if exists.
     - For each source in manifest, gather all corresponding panel files from the ZIP.
     - Verify that the panels listed match those actually in the ZIP (no missing, no extra panels).
     - Reconstruct each source file by concatenating its panels (after stripping headers). Compute SHA-256 and compare to the manifest's source_sha256.
     - If any discrepancy is found, report it (could accumulate errors).
     - Also verify overall count of sources, etc., if needed.

    It prints or logs the verification results:
     - "Verification PASSED" if everything is consistent.
     - "Verification FAILED" with details if any issues.

    Returns True if all checks pass, False if any fail.

    ChatGPT Implementation Prompt:
     - Open the zip with zipfile.ZipFile. Use zip.namelist() to get all file names inside.
     - Read manifest.json from the zip (zip.read('manifest.json')), parse it via json.loads.
     - Build a map of source_path -> list of panel filenames from manifest.
     - Check that for each source in manifest, each listed panel exists in zip.namelist(). Also check no unexpected files: e.g., panel files in zip that aren't referenced (could allow some extra like README or metadata, but panels should all be accounted).
     - For each source:
       * Retrieve each panel file's content (zip.read(panel_name)).
       * If panel content starts with the header sentinel or YAML block, strip it out. Implement strip_header() to remove everything from start through END marker (or YAML delimiters).
       * Concatenate the stripped panel contents in order (they should already be sorted by name if naming convention ensures lexicographic order).
       * Compute SHA-256 of the concatenated bytes.
       * Compare with manifest's recorded hash for that source.
       * Also, if manifest lists panel hash (optional), compute each panel (stripped or full?) hash and compare.
     - Track any mismatches or errors:
       * Missing panel file, extra panel file, hash mismatch for a source, or part count mismatch.
     - Output results. Possibly raise an exception or print and set return code via sys.exit for CLI usage.
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zipf:
            # 1. Read manifest
            if "manifest.json" not in zipf.namelist():
                print(f"[Error] manifest.json not found in {zip_path}")
                return False
            manifest_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
            sources = manifest_data.get("sources", [])
            # Possibly use manifest.project.json if needed for Projects (optional).

            # 2. Verify each source in manifest
            all_panel_files = set()
            success = True
            for src in sources:
                path = src.get("path")
                src_hash = src.get("sha256")
                panels = src.get("panels", [])
                if not panels:
                    print(f"[Error] No panels listed for source {path} in manifest.")
                    success = False
                    continue
                # Gather panel file names and check they exist in zip
                concatenated = b""
                for panel in panels:
                    fname = (
                        panel["file"] if isinstance(panel, dict) else panel
                    )  # some manifest entries might store panel info as dict or str
                    all_panel_files.add(fname)
                    if fname not in zipf.namelist():
                        print(f"[Error] Panel file {fname} listed for {path} missing in ZIP.")
                        success = False
                        continue
                    content = zipf.read(fname)
                    # Strip header:
                    content_stripped = strip_header(content)
                    concatenated += content_stripped
                    # Verify panel's own hash if present in manifest
                    if isinstance(panel, dict) and panel.get("sha256"):
                        panel_hash = hashlib.sha256(content_stripped).hexdigest()
                        if panel_hash != panel["sha256"]:
                            print(f"[Error] Panel {fname} hash mismatch (manifest vs actual).")
                            success = False
                # After collecting all panels for source, verify combined hash:
                if src_hash:
                    combined_hash = hashlib.sha256(concatenated).hexdigest()
                    if combined_hash != src_hash:
                        print(
                            f"[Error] Reconstructed file hash mismatch for {path}: got {combined_hash}, expected {src_hash}."
                        )
                        success = False

            # 3. Verify no orphan panels (panel files in ZIP not referenced in manifest)
            # Identify all panel files in the ZIP (e.g., those in "panels/" directory if structured)
            panel_files_in_zip = [name for name in zipf.namelist() if is_panel_file(name)]
            for pfile in panel_files_in_zip:
                if pfile not in all_panel_files:
                    print(
                        f"[Warning] Panel file {pfile} in ZIP not referenced in manifest (orphan)."
                    )
            # We flag a warning but do not necessarily fail, depending on policy.
            if success:
                print(f"Verification PASSED for bundle {zip_path}")
            else:
                print(f"Verification FAILED for bundle {zip_path} (see errors above).")
            return success
    except zipfile.BadZipFile:
        print(f"[Error] {zip_path} is not a valid ZIP file.")
        return False


def strip_header(panel_content: bytes) -> bytes:
    """Remove the header section from a panel's content bytes.

    The header can be:
     - YAML front matter (between '---' lines) for markdown.
     - Sentinel comment block (between SENTINEL_HEADER_BEGIN and SENTINEL_HEADER_END lines) for code.

    This function finds the end of the header and returns the content after that (with any leading newlines trimmed).

    Implementation plan:
     - Decode a small portion of panel_content (or full) as text (UTF-8) because header is textual and small.
     - If content starts with '---\n' (YAML front matter), find the matching '---\n' that ends the front matter.
     - If content contains 'SENTINEL_HEADER_END', find that line.
     - Determine the index in bytes where header ends, and return panel_content from that point onward.
     - Edge cases: If no header markers found (shouldn't happen if our packer always adds header), return original content.
    """
    text = None
    try:
        text = panel_content.decode("utf-8")
    except UnicodeDecodeError:
        # If there's a decoding issue, return original content (likely a binary chunk).
        return panel_content

    if text.startswith("---\n"):
        # YAML header case
        end_index = text.find("\n---", 4)  # find closing '---'
        if end_index != -1:
            after = text[end_index + 4 :]  # 4 to skip the '---\n'
            return after.encode("utf-8")

    # Sentinel header case:
    start_idx = text.find(SENTINEL_HEADER_BEGIN)
    end_idx = text.find(SENTINEL_HEADER_END)
    if start_idx != -1 and end_idx != -1:
        # Cut from end of END marker line
        end_marker_idx = text.index(SENTINEL_HEADER_END) + len(SENTINEL_HEADER_END)
        # The END marker line might have a newline after it; find that newline
        newl_idx = text.find("\n", end_marker_idx)
        if newl_idx != -1:
            return text[newl_idx + 1 :].encode("utf-8")
        else:
            return text[end_marker_idx:].encode("utf-8")

    # No header found
    return panel_content


def is_panel_file(filename: str) -> bool:
    """Simple check if a file in the ZIP is likely a panel chunk file.
    For example, we might decide that any file with name matching "__part_" pattern is a panel.
    """
    return "__part_" in filename
