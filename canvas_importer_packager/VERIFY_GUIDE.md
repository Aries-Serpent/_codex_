````markdown
# Verification Guide

After importing a bundle into Canvas or whenever you want to validate integrity, run the verification routine (via CLI or in-code) to ensure everything is consistent. The verification process checks several invariants:

1. **Manifest Presence:** The bundle must contain a `manifest.json` describing all sources and panels. If missing, the bundle is incomplete.
2. **Panel Presence:** For each source file listed in the manifest, all corresponding `part_x_of_y` panel files must exist in the ZIP. If any listed panel is missing, or if there are extra panel files not referenced (orphans), the verification will flag an error.
3. **Hash Integrity:** The SHA-256 hash of each original source file (stored in manifest as `source.sha256`) is compared to the hash of the concatenation of its panel contents.
4. The verifier strips out the panel headers (YAML or SENTINEL comments) and concatenates the raw content of all parts in order.
5. It then computes SHA-256 on this reconstructed content and compares it to the manifest's hash for that source. They must match exactly (i.e., **SHA256(concat(parts)) == SHA256(source)**).
6. If any mismatch occurs, it indicates content loss or modification (verification fails for that file).
7. **Panel Order & Count:** The manifest specifies `part: i of n` for each panel. The verifier ensures it has exactly *n* panels for that file and that each panel from 1 to n is present. Any gap or count mismatch causes failure.
8. **Panel Hashes (Optional):** If the manifest records each panel's `sha256`, those are also computed and cross-checked. Any discrepancy means the panel content was altered.
9. **No Truncation:** The reassembled file length should equal the `size_bytes` in manifest. This double-checks that no bytes were dropped. Adherence to **NO_BREVITY_POLICY.md** during creation typically guarantees this.
10. **Output:** On success, the verifier will output a confirmation (e.g., "Verification PASSED"). On failure, it will list errors for each issue (e.g., missing panel file, hash mismatch for a file, etc.) and typically a "FAILED" summary.

**Usage Example:**
```bash
$ python canvas_importer_packager.py verify --bundle my_project_bundle.zip

Reading manifest... OK
Verifying 10 source files...
- src/app.py: OK
- src/utils/helpers.py: OK
- README.md: OK
...
Verification PASSED for bundle my_project_bundle.zip
````

If an error occurs, e.g., if one panel was manually edited or lost:

```
- src/config.yaml: [Error] Reconstructed file hash mismatch (expected abc123..., got def456...)
Verification FAILED for bundle my_project_bundle.zip (see errors above).
```

**Troubleshooting:**

* If you see a hash mismatch, do **not edit panels manually**; regenerate the bundle instead. Manual changes will break integrity.
* "Orphan panel" warnings mean the ZIP had extra files not in manifest; consider removing them to clean the bundle.
* Always ensure the **IMPORT_ME.md** was pasted fully (no panels omitted) if verifying a Canvas copy.

By following this guide and using the provided verification tool, you can trust the contents of your ChatGPT Canvas project bundle with high confidence.
