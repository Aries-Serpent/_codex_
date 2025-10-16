# Patch Debris Guard

The `patch_debris` nox session scans the working tree for stray diff markers such as `*** Begin Patch` or `diff --git`. Use it before committing patches assembled manually.

## Usage

```bash
nox -s patch_debris
```

The task is offline-friendly and only inspects text-like files (Python, Markdown, JSON, YAML, TOML, shell, Makefiles). Build caches, hidden directories, and `patches/` are automatically excluded.

If any markers are detected the session fails and prints the offending paths; otherwise it logs a success message.
