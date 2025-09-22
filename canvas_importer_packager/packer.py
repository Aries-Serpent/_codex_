"""
Module: packer.py

Contains functions to ingest files from a repository and split them into chunks ("panels"),
then package these panels into a ZIP file along with manifest and other metadata.
It handles filtering of files, chunking by different strategies, and writing output files (panels, manifest, checksums, etc.).

Main Functions:
- `pack_directory(root_path, output_zip, strategy, budget, model)`: High-level function to package the given directory into a bundle.
- `chunk_file(file_path, strategy, budget, model)`: Read a single file and split its content into chunks according to the strategy.
- `make_panel_filename(file_path, part_index, total_parts)`: Generate a filename for a panel chunk, following the naming convention.
- `build_header(file_path, file_sha, strategy, part_index, total_parts)`: Create the YAML front matter or comment header for a chunk.
- `compute_sha256(data)`: Compute SHA-256 hash for given data (returns hex string).
- Utility functions for filtering files (includes/excludes), text/binary detection, etc.

Chunking Strategies:
- **Bytes**: Maximum chunk size in bytes. Cut at byte boundaries, ideally on newline boundaries if possible.
- **Semantic**: Attempt to split on natural boundaries (paragraphs, sentences). For example, try "\n\n", then "\n", then " " then character[3].
- **Tokens**: Use OpenAI tiktoken to limit chunks by token count for a given model[4][5].

Integrity and Headers:
Each panel file includes a header with metadata (original file path, part number, hash, etc.). For Markdown files, use a YAML front matter block[6]. For code or other text files, use a comment-based header demarcated by SENTINEL lines. These headers are excluded when computing hashes for integrity verification.

Security:
- Only text files are chunked; binary files are skipped (or could be included as single chunk if needed). Binary detection is done by searching for null bytes[2] or by trying to decode as UTF-8.
- Uses `ast.literal_eval` for safe parsing of any config or knowledge file inputs (no `eval` execution)[1].
"""

import hashlib
import os

# If token-based splitting is needed:
try:
    import tiktoken
except ImportError:
    tiktoken = None

# Constants for header sentinel tags:
SENTINEL_HEADER_BEGIN = "SENTINEL_HEADER_BEGIN"
SENTINEL_HEADER_END = "SENTINEL_HEADER_END"


def pack_directory(
    root_path: str,
    output_zip: str = "canvas_bundle.zip",
    strategy: str = "semantic",
    budget: int = None,
    model: str = "gpt-4",
):
    """
    Traverse the directory at root_path, filter files, split each into chunks, and write to a ZIP bundle.

    - root_path: the root directory of the project to package.
    - output_zip: filename for the output bundle (zip file).
    - strategy: chunking strategy - 'bytes', 'semantic', or 'tokens'.
    - budget: chunk size limit according to strategy.
      * For 'bytes', this is max bytes per chunk.
      * For 'semantic', could be max characters or bytes (if None, default like 16KB).
      * For 'tokens', it's max tokens per chunk.
    - model: if strategy is 'tokens', which language model's tokenizer to use (e.g., 'gpt-4', 'gpt-3.5-turbo').

    Steps:
    1. Collect all files under root_path (skip directories). Apply include/exclude filters (e.g., skip .git/, node_modules/, etc.).
    2. Sort files in deterministic order (by depth then lexicographic path) to ensure stable panel ordering.
    3. Initialize data structures for manifest (e.g., list of sources, each with panel info).
    4. Open a new ZIP file for writing. For each file:
       a. Compute the file's SHA-256 hash and size.
       b. Determine if file should be chunked (text vs binary). If binary, perhaps skip or handle differently.
       c. Chunk the file content according to strategy:
          - If 'bytes': chunk into pieces of at most `budget` bytes.
          - If 'semantic': split by newline/paragraph boundaries, ensuring chunks ~<= budget characters (if budget is None, use default).
          - If 'tokens': use tiktoken to count tokens per chunk[4].
       d. For each chunk, generate a panel filename with format "<hash8>__<slug>__part_{####}_of_{####}.ext".
          * hash8 = first 8 hex digits of the file's SHA-256 (or could use path hash for uniqueness).
          * slug = a sanitized identifier from the file path (e.g., filename or path segments).
          * ext = original file extension (for proper syntax highlighting in Canvas).
       e. Create a header (YAML or comment) with metadata: original path, source file hash, chunk strategy, part X of Y.
       f. Write the header + chunk content to the ZIP as a file entry under, e.g., "panels/<panel_filename>".
       g. Record panel metadata (filename, part number, etc.) in the manifest structure.
    5. Write manifest.json to ZIP (at root or a known location) containing strategy, budget, and sources data (with their panels and hashes).
    6. Optionally, write additional files: checksums.csv (each panel's SHA-256), audit.json (detailed mapping of source bytes to parts), IMPORT_ME.md (for Canvas import instructions).
    7. Close the ZIP file.

    The function does not return anything, but on completion the output_zip file is created.
    If any error occurs (e.g., file read issues), it should raise an exception or handle accordingly.

    ChatGPT Implementation Prompt:
    - Implement file traversal using os.walk, filtering out directories like .git or others listed in exclude lists.
    - For each file, use `with open(file, 'rb')` to read content. If content contains b'\x00' early, consider it binary[2] and handle accordingly (skip or mark as single chunk).
    - Implement `chunk_file` (perhaps as an inner helper) to yield (chunk_bytes_list) for the file content:
      * 'bytes': simple slicing of the byte content.
      * 'semantic': find last `\n\n` within budget, or `\n`, or space, etc, to split at a boundary.
      * 'tokens': if tiktoken is available, get encoding for model and count tokens, accumulating tokens until reaching budget[4][5].
    - Generate panel filenames using `make_panel_filename`. Ensure zero-padded indices (####) for correct lexicographic order.
    - Use Python's `zipfile` module (ZipFile) to write files. Use `ZipFile.writestr()` to write in-memory content to the zip[7].
    - Compute SHA-256 using hashlib for original file and for each panel content (excluding header when computing panel hash for manifest).
    - Build the manifest structure as a dict, then serialize to JSON (use json module).
    - Write manifest.json and any other manifest files to the ZIP as well.
    - Ensure that no part of the content is truncated or omitted (split boundaries should be chosen at natural breaks to be human-readable and to avoid breaking context in weird places).

    Note: Be careful to strip or ignore the header in panel content when reconstructing or computing the original file hash for the manifest integrity.
    """
    # Placeholder implementation outline:
    # 1. Gather files
    # 2. Sort files
    # 3. Prepare manifest data structure
    # 4. Open zipfile for writing
    # 5. For each file -> process and write chunks
    # 6. Write manifest and supplementary files
    # 7. Close zip
    raise NotImplementedError("pack_directory functionality not implemented yet.")


def chunk_file(file_path: str, content_bytes: bytes, strategy: str, budget: int, model: str):
    """
    Split the given file content into chunks according to the specified strategy.

    Returns a list of chunk byte strings (without headers, just the raw content for each panel).

    - file_path: used for context (could influence splitting strategy if needed, e.g., treat .md differently?).
    - content_bytes: the full content of the file as bytes.
    - strategy: 'bytes', 'semantic', or 'tokens'.
    - budget: maximum size of each chunk (in bytes for 'bytes', in characters for 'semantic' (approx.), in tokens for 'tokens').
    - model: if strategy='tokens', the model name for tokenizer.

    Strategy implementations:
    - bytes: straightforward slicing of content_bytes into chunks of length <= budget.
      Ensure that budget is set (if None, could default to e.g. 16000 bytes).
    - semantic: attempt to break at natural boundaries:
      * Define a list of separators, e.g. ["\n\n", "\n", " ", ""] (fallback to character)[3].
      * Recursively try to split the content: e.g., if content > budget, try finding the last double-newline within first budget chars; if found, split there. If not, try single newline, etc.
      * This mimics LangChain's RecursiveCharacterTextSplitter approach for more coherent chunks.
    - tokens: requires tiktoken.
      * If tiktoken is not available, fallback to a rough character count or raise error.
      * Use tiktoken.encoding_for_model(model) to get tokenizer[8].
      * Encode the content to tokens. Then iterate through token list, grouping into chunks of <= budget tokens[5].
      * Decode each chunk of tokens back to text. Possibly trim or strip spaces at edges if needed.
      * Ensure no token limit overflow (each chunk's token count <= budget).

    The output chunks should be raw text bytes ready to be prefixed with headers and written as panel files.
    For binary or very small files, the function may return just [content_bytes] as one chunk.

    ChatGPT Implementation Prompt:
    - Implement for 'bytes': simple loop slicing content_bytes[0:budget], [budget:2*budget], etc.
    - Implement for 'semantic': you may convert content_bytes to text (utf-8) for easier splitting by newline.
      Use a loop: while remaining text > budget length, find rightmost separator within budget and split.
    - Implement for 'tokens': as described, using tiktoken if available[9]. Handle if not installed.
    - Make sure to handle edge cases: e.g., if a single line is longer than budget (no separator found) then split at budget position.
    - The function should return a list of `bytes` objects (each chunk encoded in UTF-8).
    """
    # Not implemented in skeleton.
    raise NotImplementedError


def make_panel_filename(file_path: str, part_index: int, total_parts: int) -> str:
    """
    Construct a filename for a panel (chunk) file.

    Format: "<prefix>__<slug>__part_{XXXX}_of_{XXXX}.<ext>"

    - prefix: an 8-character hash (hex) derived from the file path (or file content hash for uniqueness).
    - slug: a sanitized version of the file name or path (alphanumeric and underscores, no spaces).
    - part_index: 1-based index of this chunk.
    - total_parts: total number of chunks for this file.
    - ext: original file extension (including the dot).

    The zero-padded indices ensure proper lexicographic ordering. For example:
    For file "docs/README.md" split into 2 parts, prefix might be "5d41402a", slug "docs_README",
    and filenames:
    "5d41402a__docs_README__part_0001_of_0002.md"
    "5d41402a__docs_README__part_0002_of_0002.md"

    ChatGPT Implementation Prompt:
    - Use hashlib.sha256 on the file path (encode UTF-8) or on the file's content to get a unique hash.
      Take first 8 hex chars of it as prefix for brevity.
    - Derive slug from file_path: replace os.sep with "_" for nested paths, remove or replace any characters not alphanumeric or '_' or '.'.
      (Goal is to human-identify the file in the name, while prefix avoids collisions.)
    - Use str.zfill(4) or f-string with :04d to pad part numbers.
    - Return the formatted string.
    """
    base_name = os.path.basename(file_path)
    ext = ""
    if "." in base_name:
        # ext includes the dot
        ext = "." + base_name.split(".")[-1]
    # Create slug from path (replace separators with '_')
    slug = file_path.replace(os.sep, "_").replace(" ", "_")
    # Simple alphanumeric filter for slug:
    slug = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in slug)
    # Compute prefix hash of path
    prefix_hash = hashlib.sha256(file_path.encode("utf-8")).hexdigest()[:8]
    return f"{prefix_hash}__{slug}__part_{part_index:04d}_of_{total_parts:04d}{ext}"


def build_header(
    file_path: str, file_sha: str, strategy: str, part_index: int, total_parts: int
) -> str:
    """
    Build a header string to prepend to a panel chunk.

    If the file is Markdown (.md or .mdx), returns a YAML front matter block:
    ---
    source_path: <file_path>
    source_sha256: <hash_of_full_file>
    chunk_strategy: <strategy>
    part: <part_index> of <total_parts>
    ---

    For code or other text files, returns a comment-based header using SENTINEL markers:
    e.g., for a Python file:
    # SENTINEL_HEADER_BEGIN
    # source_path: <file_path>
    # source_sha256: <hash_of_full_file>
    # chunk_strategy: <strategy>
    # part: <part_index> of <total_parts>
    # SENTINEL_HEADER_END

    These headers allow tracing each panel back to the original source and are stripped out during verification hashing.

    ChatGPT Implementation Prompt:
    - Determine file type by extension. If ext in {'.md', '.mdx'}, use YAML format.
    - Else, choose an appropriate single-line comment prefix based on extension:
      e.g., '#' for .py, .sh; '//' for .js, .java; '%' for .ipynb (if exporting as code); etc.
      (As a simplification, default to '#' for any code for now.)
    - Construct header lines accordingly. Ensure the header is followed by a newline after END marker.
    - Return the header string (encoded to match file encoding if needed).
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".md", ".mdx"):
        header = (
            "---\n"
            f"source_path: {file_path}\n"
            f"source_sha256: {file_sha}\n"
            f"chunk_strategy: {strategy}\n"
            f"part: {part_index} of {total_parts}\n"
            "---\n"
        )
    else:
        comment_prefix = "#"  # default comment char
        header_lines = [
            f"{comment_prefix} {SENTINEL_HEADER_BEGIN}",
            f"{comment_prefix} source_path: {file_path}",
            f"{comment_prefix} source_sha256: {file_sha}",
            f"{comment_prefix} chunk_strategy: {strategy}",
            f"{comment_prefix} part: {part_index} of {total_parts}",
            f"{comment_prefix} {SENTINEL_HEADER_END}",
        ]
        header = "\n".join(header_lines) + "\n"
    return header


def compute_sha256(data: bytes) -> str:
    """Return the SHA-256 hex digest of the given bytes."""
    return hashlib.sha256(data).hexdigest()


# Additional utility functions (file filtering, binary detection) could be here:


def is_binary_content(content_bytes: bytes) -> bool:
    """
    Heuristic check if content_bytes represents binary data (non-text).

    Strategy:
    - If a NUL (0x00) byte is found in the first chunk of data, consider it binary[2].
    - Optionally, check the ratio of non-printable characters if needed (e.g., using a threshold).
    - Empty file is not binary (return False).

    This is a simplistic check; it may mis-classify UTF-16 as binary due to null bytes in encoding,
    but it's a common practical heuristic (used by grep, diff, etc.).

    Returns True if likely binary, False if likely text.
    """
    if not content_bytes:
        return False
    # Check for null byte in initial portion:
    if b"\x00" in content_bytes[:1024]:
        return True
    # (Could add more heuristics, e.g., check non-ASCII character proportion)
    return False
