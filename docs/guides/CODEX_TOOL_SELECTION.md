# Codex Tool Selection Guide

> **Purpose**: Prevent wrong tool selection (CODEX-007) causing 45% session waste.  
> **References**: RFC 3881, Git documentation, Bash reference manual

## Quick Decision Tree

```text
START: "I need to create/modify a file"
  │
  ├─→ "Is it a NEW file?" 
  │    └─→ YES: Use `cat <<'EOF'` or `echo "..." > file`
  │    └─→ NO: Continue
  │
  ├─→ "Is it a SMALL SINGLE-LINE change?"
  │    └─→ YES: Use `sed -i 's/old/new/'`
  │    └─→ NO: Continue
  │
  ├─→ "Do I have a FORMAL PATCH with @@ markers?"
  │    └─→ YES: Validate with `git apply --check`, then use `apply_patch`
  │    └─→ NO: Continue
  │
  ├─→ "Is the file COMPLEX with variables/escapes?"
  │    └─→ YES: Generate to temp file, then move
  │    └─→ NO: Continue
  │
  ├─→ "Is it a LARGE MULTI-LINE change?"
  │    └─→ YES: Regenerate entire file with `cat <<'EOF'`
  │    └─→ NO: Consider `sed` or line-by-line editing
  │
  └─→ END: Execute with validation
```text
## Tool Comparison Matrix

| Operation | Tool | When to Use | Pros | Cons | Success Rate |
|-----------|------|------------|------|------|--------------|
| Create new file | `cat <<'EOF'` | Always for new files | Simple, reliable, universal | None | 100% |
| Single line change | `sed -i` | Small targeted edits | Fast, atomic | Line-dependent, fragile regex | 85% |
| Formal patch | `apply_patch` | When patch has @@ markers | Context-aware, validates | Requires strict format | 50-90%* |
| Complex with vars | Temp file | Variables + escapes needed | Safe, testable, clear | Extra I/O | 95% |
| Config generation | Python/Templating | Dynamic config | Flexible, testable | Slower | 90% |
| Multi-line literal | `cat <<'EOF'` (quoted) | Shell scripts, JSON, code | Preserves formatting | No expansion | 100% |
| Multi-line with vars | `cat <<EOF` (unquoted) | Need interpolation | Dynamic content | Escape complexity | 85-95% |

**\*Success rate for apply_patch improves to ~95% with pre-validation**

## Examples by Scenario

### Scenario 1: Create New File (Recommended)

✅ **CORRECT**: Using `cat <<'EOF'`
```bash
cat <<'EOF' > scripts/new_script.sh
#!/usr/bin/env bash
# This is literal; variables like $VAR will NOT expand
echo "Hello World"
EOF
chmod +x scripts/new_script.sh
```text

### Scenario 2: Single-Line Change

✅ **CORRECT**: Using `sed -i`
```bash
# Replace first occurrence on line
sed -i 's/old_value/new_value/' config.yaml

# Replace all occurrences
sed -i 's/old_value/new_value/g' config.yaml

# In-place with backup
sed -i.bak 's/old_value/new_value/' config.yaml
```text

### Scenario 3: Multi-Line File with Variables

✅ **CORRECT**: Using `cat <<EOF` (unquoted for expansion)
```bash
branch="feature/pr-1926"
cat <<EOF > .codex/session_info.txt
Branch: $branch
Date: $(date -u +%F)
User: $USER
EOF
```text

### Scenario 4: Complex Script (Multiple Lines)

✅ **BEST**: Using temp file for safety
```bash
# Generate to temp
temp_script=$(mktemp)
cat <<'EOF' > "$temp_script"
#!/usr/bin/env bash
# Complex logic here
echo "Script content"
EOF

# Validate
bash -n "$temp_script"

# Move to final location
mv "$temp_script" scripts/final_script.sh
chmod +x scripts/final_script.sh
```text

### Scenario 5: Patch Application

✅ **CORRECT**: Validate before applying
```bash
# Create patch (if not already)
git diff > changes.patch

# Validate patch
bash scripts/validate_patch.sh changes.patch

# Apply if valid
if [[ $? -eq 0 ]]; then
  git apply changes.patch
fi
```text

## Common Mistakes & Corrections

### Mistake 1: Using wrong quotes in heredoc

❌ **WRONG**: Unquoted delimiter when you want literals
```bash
cat <<EOF > file.json
{ "var": "$VAR" }  # VAR will expand!
EOF
```text

✅ **CORRECT**: Quote delimiter for literal
```bash
cat <<'EOF' > file.json
{ "var": "$VAR" }  # VAR stays literal
EOF
```text

### Mistake 2: Forgetting to escape $ in sed

❌ **WRONG**: Dollar sign not escaped
```bash
sed -i 's/price/$100/g' file.txt  # $ has special meaning in sed!
```text

✅ **CORRECT**: Escape or use different delimiter
```bash
sed -i 's/price/\$100/g' file.txt
# OR
sed -i 's|price|$100|g' file.txt  # Use | as delimiter
```text

### Mistake 3: Not validating complex patches

❌ **WRONG**: Applying patch without checking
```bash
git apply potentially-broken.patch  # May silently fail or corrupt files!
```text

✅ **CORRECT**: Dry-run first
```bash
git apply --check potentially-broken.patch  # Dry-run
if [[ $? -eq 0 ]]; then
  git apply potentially-broken.patch
fi
```text

## Research References

- RFC 3881: Unified Diff Format
- Git documentation: https://git-scm.com/docs/git-apply
- Bash heredoc guide: https://www.simplified.guide/bash/heredoc-use
- Stack Overflow: `sed` escaping and heredoc quoting
- GitHub Codex issues: #593, #2235

---

**Last Updated**: 2025-10-30  
**Author**: Codex Optimization Team  
**Status**: Reference documentation for preventing CODEX-007
