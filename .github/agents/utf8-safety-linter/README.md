# UTF-8 String Safety Linter

Validates JavaScript/TypeScript/YAML string operations for UTF-8 safety, preventing corruption from unsafe truncation.

## Mission
Detect unsafe string truncation operations that could split UTF-8 multi-byte characters or surrogate pairs.

## Quick Start
```bash
cd .github/agents/utf8-safety-linter
pip install -r requirements.txt
python linter.py scan --file .github/workflows/semgrep_sarif.yml
```

## Detection Patterns
- `string.slice(start, end)` without boundary checks
- `string.substring()` on user input
- Direct indexing in loops

## Safe Pattern
```javascript
function safeTruncate(str, maxLength) {
  if (str.length <= maxLength) return str;
  let safeCut = str.lastIndexOf('\n', maxLength);
  if (safeCut === -1) safeCut = maxLength;
  // Check surrogate pairs
  if (safeCut > 0) {
    const code = str.charCodeAt(safeCut - 1);
    if (code >= 0xDC00 && code <= 0xDFFF) safeCut -= 1;
  }
  return str.slice(0, safeCut) + '...';
}
```
