```markdown
# Security Posture

This project is designed with a careful approach to security and data integrity. Key considerations include:

- **No Arbitrary Code Execution:** The packager will not execute or evaluate the content of project files. It treats files as data, reading bytes and writing chunks. Any evaluation of input lists (e.g., knowledge files lists) uses `ast.literal_eval` for safe parsing[1], preventing malicious code execution that could occur with `eval`.
- **Binary File Handling:** Binary files are detected (by presence of null byte in content[2] or other heuristics) and are either skipped or handled in a safe manner (e.g., not splitting in the middle of binary data). This avoids unintentionally printing binary gibberish to ChatGPT which could be large or unsafe.
- **UTF-8 Decoding:** Text files are decoded in UTF-8. If a file contains invalid UTF-8 sequences (possibly indicating binary content), the tool treats it as binary to avoid exceptions. Non-UTF8 text is thus handled cautiously.
- **Header Integrity:** The inserted panel headers do not affect execution of code (they are comments or YAML). During verification, these headers are stripped out before hashing to ensure original file integrity checks are valid. The use of sentinel markers ensures we remove precisely the intended lines and nothing more.
- **No External Connections:** The packaging and verification processes run entirely offline on local files. No data is sent to external APIs or the internet. (Tokenization with tiktoken is local; if the encoding model is not available, the user must install the library – no runtime calls to OpenAI API are made.)
- **Deterministic Outputs:** The same input project will always produce the same panel breakdown (order and content), ensuring reproducibility. This determinism is important for verifying that no unintended changes occur between runs.
- **Large File Handling:** Extremely large files are chunked to fit within memory constraints by streaming through them if necessary (to be implemented). This prevents memory exhaustion or crashes when dealing with big data files.
- **Hashing and Verification:** Using SHA-256 cryptographic hashes ensures any change in content is detected with very high probability. The verification step is read-only and does not modify files, making it safe to run on untrusted bundles to check their integrity.
- **Dependency Safety:** Only standard library modules and `tiktoken` (for token counting) are used. `tiktoken` is an OpenAI-supported library for encoding, and it does not execute untrusted code (it only performs tokenization).
- **Ast.literal_eval for Configs:** If the tool reads a list of files from a user-provided Python file (the `--from-knowledge` input), it will use `ast.literal_eval` on that file's content to extract the data structure. This means only Python literals (dict, list, strings, numbers, etc.) are allowed[1]. No function calls or arbitrary code in that file will run, mitigating a common security risk.
- **Path Traversal Mitigation:** When writing files into the ZIP, we ensure the archive paths are relative and do not contain `..` or absolute path prefixes. This prevents a malicious file path from causing files to be written outside the intended archive structure.

By adhering to these practices, the Canvas Importer/Packager maintains a robust security posture appropriate for handling potentially untrusted project data.
```
