# Matrix: Security Input Validation (v1.2)
> Generated: Previous Cycle-11-02 15:26:48 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Security Matrix Curator], [Secondary: QA] ⚡ Energy: 5

Patterns
| Type | Regex/Method | Applied To | Severity (1–5) | Evidence |
|---|---|---|---:|---|
| SQL Injection | `;\s*(DROP|DELETE|UPDATE)`, `' OR '`, `--`, `/*...*/` | Config keys, CLI strings, loaders | 4 | src/security/core.py |
| XSS | `<script`, `javascript:`, `on\w+=` | HTML output, user content | 4 | src/security/core.py |
| Path Traversal | PurePosixPath, PureWindowsPath + `..` check | Paths (data, checkpoints) | 3 | src/security/core.py |
| JSON Injection | `__proto__`, `constructor`, `prototype` | JSON inputs | 3 | src/security/core.py |

Actions
- Ensure `validate_input()` is used at all entry points.
- Extend tests for unicode/null byte and unusual encodings.
