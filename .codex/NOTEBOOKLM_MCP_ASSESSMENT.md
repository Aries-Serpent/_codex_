# Assessment: PleasePrompto/notebooklm-mcp

**Repository**: https://github.com/PleasePrompto/notebooklm-mcp  
**Assessment Date**: 2026-01-11  
**Stars**: 387 | **Forks**: 50 | **Language**: TypeScript

## Overview

`notebooklm-mcp` is an MCP (Model Context Protocol) server that allows AI agents (Claude Code, Codex, Cursor, etc.) to query NotebookLM directly for **zero-hallucination answers** based on user-uploaded documentation.

## Key Features

### Core Capabilities
- **Zero Hallucinations**: NotebookLM only answers from uploaded sources; refuses if info isn't present
- **Autonomous Research**: Claude/agents ask follow-up questions automatically
- **Smart Library Management**: Save notebooks with tags, auto-select based on task
- **Cross-Tool Sharing**: Works with Claude Code, Codex, Cursor, VS Code, amp, Gemini

### Architecture
```
Your Task → Local Agent → MCP Server → Chrome Automation → NotebookLM → Gemini 2.5 → Your Docs
```

### Tool Profiles (Token Optimization)
| Profile | Tools | Use Case |
|---------|-------|----------|
| minimal | 5 | Query-only |
| standard | 10 | + Library management |
| full | 16 | All tools including cleanup |

## Integration with _codex_

### Relevance to Project Architect Researcher
Our `.github/agents/project-architect-researcher/` agent already implements NotebookLM integration concepts. The `notebooklm-mcp` provides a **complementary MCP server approach** that could:

1. **Enhance automation**: Instead of browser automation via Python, use the TypeScript MCP server
2. **Simplify setup**: `npx notebooklm-mcp@latest` vs custom script deployment
3. **Cross-client support**: Works natively with multiple agents

### Recommended Integration Path

#### Option A: Direct Adoption
```bash
# Add to Codex
codex mcp add notebooklm -- npx notebooklm-mcp@latest
```
- **Pros**: Immediate zero-hallucination research capability
- **Cons**: Depends on external npm package

#### Option B: Hybrid Approach
Keep our Project Architect Researcher for artifact generation, use notebooklm-mcp for live queries:
- Use `project-architect-researcher` for structured documentation artifacts
- Use `notebooklm-mcp` for interactive Q&A during development

#### Option C: Contribute Back
Consider contributing our PRO features (audio overview prompts, structured source generation) to notebooklm-mcp as enhancements.

## Technical Assessment

### Strengths
- ✅ **Zero hallucination guarantee** via NotebookLM's source-grounded design
- ✅ **Mature TypeScript codebase** with comprehensive documentation
- ✅ **Active maintenance** (updated Jan 11, 2026)
- ✅ **Multi-client support** (Claude Code, Codex, Cursor, VS Code)
- ✅ **Profile system** for token optimization

### Considerations
- ⚠️ Uses Chrome automation (Puppeteer) - requires browser environment
- ⚠️ Google account authentication required
- ⚠️ Rate limits apply to free tier
- ⚠️ External dependency on npm package

### Security
- Credentials stay local (never transmitted)
- Browser runs locally
- Recommendation: Use dedicated Google account for automation

## Recommendation

**Strong recommendation to integrate** `notebooklm-mcp` into the _codex_ development workflow:

1. **Immediate**: Add MCP server to agent configurations
2. **Short-term**: Create NotebookLM notebook with _codex_ documentation
3. **Medium-term**: Document workflow in `.github/agents/` for team adoption
4. **Long-term**: Consider contributing PRO features back to the project

## Installation Commands

### For Codex
```bash
codex mcp add notebooklm -- npx notebooklm-mcp@latest
```

### For Claude Code
```bash
claude mcp add notebooklm npx notebooklm-mcp@latest
```

### For Cursor
Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "npx",
      "args": ["-y", "notebooklm-mcp@latest"]
    }
  }
}
```

## Links
- **GitHub**: https://github.com/PleasePrompto/notebooklm-mcp
- **npm**: https://www.npmjs.com/package/notebooklm-mcp
- **Claude Code Skill**: https://github.com/PleasePrompto/notebooklm-skill
- **Documentation**: https://github.com/PleasePrompto/notebooklm-mcp/blob/main/docs

---

**Assessment Status**: ✅ Recommended for adoption  
**Priority**: High  
**Effort**: Low (5-minute setup)
