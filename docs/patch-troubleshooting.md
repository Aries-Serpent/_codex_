# Handling "patch with only garbage" Errors

When applying patches, you may see errors like:

```
patch: **** Only garbage was found in the patch input.
```

This usually indicates that Git or `patch` cannot parse the patch file.

## Common Causes

- Patch lacks proper Git diff headers (`diff --git`, `index`, `@@` hunks).
- Patch is an email/mbox patch (`From <sha>`) that should be applied with `git am`.
- Encoding or line-ending issues (e.g., UTF-16, BOM, or CRLF line endings).
- Patch was generated without `--binary` when binary changes are present.
- Patch is in a different format (e.g., `diff -ruN`) meant for the `patch` tool.
- Color codes, HTML, or other noise in the patch file.

## Recovery Checklist

1. **Inspect the header** to determine the patch type:
   ```bash
   head -20 your_patch.diff
   ```
2. **Normalize encoding and line endings** using tools like `iconv` or `dos2unix`.
3. **Strip color codes or HTML** if the patch was copied from a web page or generated with color.
4. **Apply with the correct tool**:
   - `git am` for email patches.
   - `git apply` for Git diffs.
   - `patch -p1` for generic unified diffs.
5. **Regenerate the patch with `--binary`** if it includes binary files.
6. **Check if changes are already applied** using `git apply --reverse --check`.

## Automated Helper Script

The repository includes a helper script to automate these steps:

```bash
./tools/patch_apply_safe.sh path/to/patch.diff
```

The script normalizes the patch and chooses the appropriate application method (`git apply`, `git am`, or `patch`).
