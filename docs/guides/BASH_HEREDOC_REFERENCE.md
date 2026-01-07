# Bash Heredoc Reference Guide

> **Purpose**: Resolve escape sequence confusion (CODEX-002, CODEX-009).  
> **References**: Bash reference manual §3.1.7, POSIX Shell Command Language

## Quick Reference Table

| Syntax | Variable Expansion | Command Substitution | Backslash Meaning | Recommended Use |
|--------|--------------------|----------------------|-------------------|-----------------|
| `<<EOF` | ✅ Yes | ✅ Yes | ✅ Special | Dynamic content, templating |
| `<<'EOF'` | ❌ No | ❌ No | ❌ Literal | Configuration files, scripts |
| `<<"EOF"` | ✅ Yes | ✅ Yes | ❌ Literal except `\$` | Rare; when you need expansion but literal quotes |
| `<<-EOF` | Depends on quoting | Depends | Tabs stripped | Indented heredocs |

### Decision Checklist

1. **Need literal `$`, `` ` `` or `\`?** → Use `<<'EOF'`.
2. **Need environment variables substituted?** → Use `<<EOF` (unquoted).
3. **Need indentation removal?** → Use `<<-EOF` with tabs for indent.
4. **Need ANSI-C escapes (`\x`, `\u`)?** → Use `$'string'` or `printf` instead.

## Behavior Examples

### Unquoted Delimiter (`<<EOF`)

Variables, command substitution, and arithmetic expansion are processed.

```bash
name="Codex"
cat <<EOF
Hello $name!
Today is $(date +%F).
The result of 2+2 is $((2 + 2)).
EOF
```text

Output:
```text
Hello Codex!
Today is Previous Cycle-10-30.
The result of 2+2 is 4.
```text
**Backslashes retain special meaning**:

```bash
cat <<EOF
Path: C:\\Temp\\file.txt
Literal dollar: \$HOME
EOF
```text

Produces:
```text
Path: C:\Temp\file.txt
Literal dollar: $HOME
```text
### Single-Quoted Delimiter (`<<'EOF'`)

Content is treated literally—no expansion, no escape interpretation.

```bash
cat <<'EOF'
Path: C:\\Temp\\file.txt
Literal dollar: $HOME
Command: $(uname -s)
EOF
```text

Output (exact match):
```text
Path: C:\\Temp\\file.txt
Literal dollar: $HOME
Command: $(uname -s)
```text
Use this form for scripts, JSON, YAML, and any text where substitutions would be harmful.

### Double-Quoted Delimiter (`<<"EOF"`)

Rarely needed. Double quotes allow variable expansion but treat most other characters literally.

```bash
value="quoted"
cat <<"EOF"
He said "Hello" to $value
EOF
```text

### Indented Heredocs (`<<-EOF`)

The `-` variant removes leading **tabs** (not spaces) from each line.

```bash
cat <<-EOF
	Line 1
	Line 2
EOF
```text

Output:
```text
Line 1
Line 2
```text
Combine with quoting rules for literal vs. expanded content: `<<-'EOF'` or `<<-EOF`.

## Escape Sequence Rules

| Form | `$` needed? | `\` needed? | Notes |
|------|--------------|--------------|-------|
| Literal `$HOME` in `<<EOF` | Yes (`\$HOME`) | – | Because `$` triggers expansion |
| Literal backslash `\` in `<<EOF` | – | Yes (`\\`) | Backslash escapes next char |
| Literal backslash in `<<'EOF'` | – | No | Already literal |
| Literal `"` in `<<EOF` | No | Optional | Unless using `"` pattern |

## ANSI-C Quoting vs. Heredoc

To embed hex or Unicode escapes, prefer `printf` or `$'...'` strings:

```bash
printf '%b\n' "Path\tValue"
cat <<'EOF'
$(printf '%b\n' "Path\tValue")  # Will **not** expand
EOF
```text

If expansion is required inside the heredoc, precompute the string:

```bash
line=$(printf '%b' 'Path\tValue')
cat <<EOF
$line
EOF
```text

## Command Chaining Patterns

### Writing Files Safely

```bash
cat <<'EOF' > config.yaml
name: Codex
version: "1.0"
EOF
```text

### Using Pipelines

```bash
cat <<EOF | grep Codex
Codex
Other
EOF
```text

### Feeding Interactive Commands

```bash
psql <<'EOF'
\dt
SELECT NOW();
EOF
```text

## Common Pitfalls & Solutions

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Forgetting to quote delimiter | `$VAR` unexpectedly expands | Switch to `<<'EOF'` |
| Using spaces with `<<-EOF` | Indentation not removed | Use **tabs** for indentation |
| Including delimiter text in content | Heredoc terminates early | Change delimiter (e.g., `<<'DOC'`) |
| Mixing CRLF files | `git apply` rejects patch | Normalize line endings before heredoc |

## Testing Heredoc Output

Use `cat -vet` or `od -c` to visualize hidden characters:

```bash
cat <<'EOF' > sample.txt
line with space 
EOF
cat -vet sample.txt
```text

Output shows trailing spaces as `^I` or `$` markers.

## Further Reading

- Bash Reference Manual: https://www.gnu.org/software/bash/manual/html_node/Here-Documents.html
- POSIX Shell Command Language §2.7.4
- Greg's Wiki on quoting: http://mywiki.wooledge.org/Quotes
- GNU sed manual for escaping: https://www.gnu.org/software/sed/manual/

---

**Last Updated**: 2024-10-30  
**Author**: Codex Optimization Team  
**Status**: Companion reference for CODEX-002 and CODEX-009
