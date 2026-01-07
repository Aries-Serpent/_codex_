# [Doc]: AST CLI — analyze | audit | diff
> Generated: 2024-11-11 07:57:50 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Doc Author], [Secondary: Verifier] ⚡ Energy: 5/5  
⚛️ Physics: Path🛤️ [Command → Output → Exit] Fields🔄 [Typer CLI] Patterns👁️ [Hybrid output, stable exits] Redundancy🔀 [CliRunner tests] Balance⚖️ [Human vs. JSON]

## Usage
- Human-readable by default; `--json` for machine output.

```bash
python -m codex.ast.cli analyze . --json
python -m codex.ast.cli audit .
python -m codex.ast.cli diff pathA pathB --json
```text

| Command | Output | Exit codes |
|--------|--------|------------|
| analyze | files, total_lines for a path | 0 ok, 3 error |
| audit | summary alias of analyze | 0 ok, 3 error |
| diff | deltas between two paths | 0 ok, 3 error |

— End —