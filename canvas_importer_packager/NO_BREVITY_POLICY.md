# No Brevity / No Truncation Policy

**Purpose:** Ensure that **no content is ever truncated or summarized** when copying into or out of ChatGPT Canvas. All panels and documentation must be transferred in full, preserving every character of the source.

- The assistant **must not** abbreviate or omit code or text. Every panel file should be pasted entirely, even if very large, by splitting into multiple panels rather than truncating.
- When exporting or copying, use the provided panel structure to guarantee **lossless transfer**. If any response shows "`...`" or appears cut off, it should be re-generated or split to avoid loss of data.
- **"No brevity"** means do not shorten variable names, not remove comments, and do not summarize text. The integrity of the original content is paramount.
- All Markdown code blocks (especially in **IMPORT_ME.md**) are designed to avoid triggering any token limit issues by chunking the content. Copy each block fully. The receiving Canvas will reconstruct the exact originals.
- This policy ensures that the verification step passes: any truncation would break the SHA-256 integrity checks.

By following this policy, users can trust that the Canvas content is a **verbatim, faithful representation** of the source project with no accidental omissions.
