# ChatGPT Canvas Importer/Packager

**Project Goal:** Facilitate the export of a codebase or document repository into a format that can be copy-pasted into ChatGPT *Canvas* as multiple panels, and verify that this process is lossless and secure. This tool splits files into manageable chunks with metadata, packages them into a ZIP bundle, and provides means to validate the integrity of the content after transfer.

## Features

- **Chunking Strategies:** Supports splitting files by fixed byte size, by semantic boundaries (paragraphs/newlines), or by token count (using OpenAI tiktoken) to fit AI model context limits[4].
- **Deterministic Packaging:** Preserves file structure order (sorted by folder depth and name) so panel numbering is stable across runs. Each chunk panel is given a unique name with a hash prefix and index.
- **Integrity Verification:** A manifest with SHA-256 hashes ensures that concatenating all panels reproduces the original file exactly. The verify command checks for mismatches, missing panels, or any truncation.
- **Canvas Optimization:** An `IMPORT_ME.md` template is generated to allow one-shot copying of all panels into ChatGPT Canvas with proper code fences and no content loss (per **NO_BREVITY_POLICY.md**).
- **Security Measures:** No code execution on target files, safe parsing of inputs (`ast.literal_eval`)[1], and binary content detection[2] to skip or handle binaries appropriately (see **SECURITY.md**).

## Quickstart

1. **Packing a Project:**
```bash
   python canvas_importer_packager.py pack --root /path/to/your/project --strategy tokens --budget 8192 --output my_project_bundle.zip
```

This will produce `my_project_bundle.zip` containing all panels, `manifest.json`, checksums, etc. Default strategy is `semantic` if not specified.

2. **Import to Canvas:** Open the ZIP, copy the content of `IMPORT_ME.md`, and paste into ChatGPT Canvas. Follow instructions there for a smooth import.

3. **Verification:** After pasting, or on the bundle file:

   ```bash
   python canvas_importer_packager.py verify --bundle my_project_bundle.zip
   ```

   This will print out verification results (should say PASSED if everything is correct).

## Repository Structure

* **Core Scripts:** `canvas_importer_packager.py` (CLI entry), `packer.py`, `verifier.py`
* **Test Suite:** `test_packer.py`, `test_verifier.py` (ensure all components function as intended)
* **Schemas & Samples:** JSON schema files and example manifest/audit for reference.
* **Docs:**

  * `IMPORT_ME.template.md` (template for import markdown),
  * `NO_BREVITY_POLICY.md`, `VERIFY_GUIDE.md`, `SECURITY.md` for guidelines and explanations,
  * `README.md` (this file).

Refer to the **VERIFY_GUIDE.md** and **INTEGRITY_MODEL.md** (if provided) for details on the theory of operation and integrity guarantees.

## References

This design draws on known patterns for text splitting and integrity:

* LangChain's RecursiveCharacterTextSplitter for semantic chunking\[3].
* OpenAI's tiktoken for token-aware splitting\[4].
* Jekyll-style front matter for panel metadata\[6].
* Binary file detection similar to GNU grep's null-byte check\[2].
* Hash-based verification inspired by AWS S3 ETag and CloudTrail digest approaches.

Each panel file name includes a hash of the path to minimize collisions and to trace provenance. By following the provided workflow, you can safely bring an entire project into ChatGPT for deep analysis or refactoring, and be confident nothing was lost or altered in transit.
