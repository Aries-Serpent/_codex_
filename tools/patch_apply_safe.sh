#!/usr/bin/env bash
set -euo pipefail
PATCH="${1:-fallback_patch_4.1-4.8.diff}"

if [[ ! -f "$PATCH" ]]; then
  echo "Patch not found: $PATCH" >&2
  exit 64
fi

echo "==> Inspecting header..."
HEAD1="$(head -n1 "$PATCH" || true)"

# Normalize encoding & line endings
echo "==> Normalizing encoding and EOL..."
if file "$PATCH" | grep -qi 'UTF-16'; then
  iconv -f UTF-16 -t UTF-8 "$PATCH" > "$PATCH.tmp" && mv "$PATCH.tmp" "$PATCH"
fi
# strip BOM
awk 'NR==1{sub(/^\xEF\xBB\xBF/,"")}1' "$PATCH" > "$PATCH.tmp" && mv "$PATCH.tmp" "$PATCH"
# normalize CRLF -> LF if dos2unix exists
command -v dos2unix >/dev/null 2>&1 && dos2unix -q "$PATCH" || true

# If color codes appear, strip them
if grep -Pq "\x1B\[[0-9;]*[mK]" "$PATCH" 2>/dev/null; then
  sed -r 's/\x1B\[[0-9;]*[mK]//g' "$PATCH" > "$PATCH.tmp" && mv "$PATCH.tmp" "$PATCH"
fi

# Already applied?
if git apply --reverse --check "$PATCH" >/dev/null 2>&1; then
  echo "Patch appears already applied. Skipping."
  exit 0
fi

# Choose strategy
if [[ "$HEAD1" =~ ^From[[:space:]]+[0-9a-f]{7,40} ]]; then
  echo "==> Detected email patch; using git am"
  git am --reject --3way --keep-cr "$PATCH"
elif grep -q "^diff --git " "$PATCH"; then
  echo "==> Detected git unified diff; using git apply"
  git apply --index --reject --whitespace=fix --verbose "$PATCH"
elif grep -q "^--- " "$PATCH" && grep -q "^\\*\\*\\* " "$PATCH"; then
  echo "==> Detected context diff; using patch -p1"
  patch --dry-run -p1 < "$PATCH"
  patch -p1 < "$PATCH"
else
  echo "Unrecognized patch format. Try regenerating with:"
  echo "  git diff --binary --no-color <BASE>..<HEAD> > new.patch"
  exit 65
fi

echo "==> Patch applied."
