# MCP Integration Getting Started Guide

> Consolidated guide to Model Context Protocol (MCP) integration and usage  
> **Level**: Beginner to Intermediate | **Prerequisites**: Basic GitHub knowledge  
> **Last Updated**: 2026-06-22 | **Version**: 2.0

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Quick Start](#quick-start)
3. [Setting Up MCP](#setting-up-mcp)
4. [Basic Usage](#basic-usage)
5. [Working with Tools](#working-with-tools)
6. [Integration Examples](#integration-examples)
7. [Troubleshooting](#troubleshooting)

---

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol for AI applications to interact with external tools and data sources through a unified interface.

### Key Concepts

**MCP Server**: Exposes capabilities (tools, resources, prompts)
```
┌─────────────────┐
│   MCP Server    │
│  (Your App)     │
│                 │
│  - Tools        │
│  - Resources    │
│  - Prompts      │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│   MCP Client    │
│ (GitHub Copilot)│
└─────────────────┘
```

### Capabilities

1. **Tools**: Functions the client can call
   - Example: "fetch_data", "save_file"
   - Sync or async execution
   - Input validation and typing

2. **Resources**: Data the server can expose
   - Example: Configuration files, documents
   - Versioning and change tracking
   - Read-only or read-write

3. **Prompts**: Pre-built conversation starters
   - Example: "code review template"
   - Context-aware content
   - Reusable workflows

### Benefits

✅ **Standardization**: One protocol for all integrations
✅ **Flexibility**: Define custom tools and resources
✅ **Scalability**: Works with any MCP-compatible client
✅ **Type Safety**: Built-in input/output validation
✅ **Security**: Isolated execution, permission controls

---

## Quick Start

### 1. Installation

```bash
# Install MCP SDK for Python
pip install mcp

# Install MCP for Node.js
npm install @modelcontextprotocol/sdk
```

## 2. Simple Server (Python)

```python
# mcp_server.py
from mcp.server.models import Implementation, InitializationOptions
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult
import asyncio

# Create server
server = Server("my-app")

# Define a tool
@server.call_tool()
async def get_user_info(user_id: str) -> ToolResult:
    """Get information about a user"""
    # Your logic here
    user_data = {"id": user_id, "name": "John Doe", "email": "john@example.com"}
    return ToolResult(content=[TextContent(type="text", text=str(user_data))])

# Start server
if __name__ == "__main__":
    server.run()
```

## 3. Connect Client

```bash
# Configure in GitHub Copilot or client
mcp_servers:
  my-app:
    command: python mcp_server.py
```

## 4. Use in AI Chat

```
User: "Can you fetch user info for user123?"
→ Client calls MCP tool: get_user_info("user123")
→ Server responds with user data
→ AI uses data in response
```

---

## Setting Up MCP

### 1. Server Configuration

```python
# server_config.py
from mcp.server import Server
from mcp.server.stdio_server import stdio_server

class MyMCPServer:
    def __init__(self):
        self.server = Server("my-application")
        self.setup_tools()
        self.setup_resources()
        self.setup_prompts()

    def setup_tools(self):
        """Register available tools"""
        @self.server.call_tool()
        async def process_data(data: str) -> ToolResult:
            """Process data and return result"""
            result = process_logic(data)
            return ToolResult(
                content=[TextContent(type="text", text=result)]
            )

    def setup_resources(self):
        """Register available resources"""
        @self.server.list_resources()
        async def list_resources():
            return [
                Resource(
                    uri="config://app.yaml",
                    name="Application Config",
                    mimeType="text/yaml"
                )
            ]

    def setup_prompts(self):
        """Register available prompts"""
        @self.server.list_prompts()
        async def list_prompts():
            return [
                Prompt(
                    name="code_review",
                    description="Code review template",
                    arguments=[]
                )
            ]

    def run(self):
        """Start server"""
        stdio_server(self.server).run_in_thread()
```

## 2. Client Configuration

```yaml
# .copilot/mcp.yaml
mcp_servers:
  # Local server
  my_server:
    command: python
    args: [mcp_server.py]
    env:
      DEBUG: "false"
  
  # Remote server
  remote_service:
    url: "http://localhost:3000"
    auth:
      type: bearer
      token: ${MCP_TOKEN}

# Server-specific options
server_options:
  timeout: 30
  max_retries: 3
  retry_delay: 1
```

## 3. Environment Variables

```bash
# .env
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO
MCP_TIMEOUT=30
MCP_TOKEN=your_secret_token
MCP_SERVER_PORT=3000
```

---

## Basic Usage

### 1. Calling Tools

**Define tool**:
```python
@server.call_tool()
async def fetch_data(source: str, limit: int = 10) -> ToolResult:
    """
    Fetch data from source

    Args:
        source: Data source name
        limit: Maximum records to fetch
    """
    data = await fetch_from_source(source, limit)

    return ToolResult(
        content=[TextContent(type="text", text=json.dumps(data))]
    )
```

**Client calls**:
```
User: "Fetch 20 records from production database"
→ Tool: fetch_data(source="production", limit=20)
→ Result: [list of 20 records]
```

### 2. Accessing Resources

**Define resource**:
```python
@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI"""
    if uri == "config://database.yaml":
        return read_config_file("database.yaml")
    elif uri == "docs://api.md":
        return read_docs_file("api.md")
    else:
        raise ValueError(f"Unknown resource: {uri}")
```

**Client uses**:
```
User: "What's in the database config?"
→ Client reads: config://database.yaml
→ Server returns config content
→ AI uses in response
```

### 3. Using Prompts

**Define prompt**:
```python
@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Get a prompt template"""
    if name == "code_review":
        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=PromptContent(
                        type="text",
                        text="""Please review this code:

{code}

Focus on:
1. Security issues
2. Performance problems
3. Best practices
4. Testing coverage"""
                    )
                )
            ]
        )
```

**Client uses**:
```
User: "Review my code"
→ Client fetches: code_review prompt
→ Prompt template applied to code
→ AI performs structured review
```

---

## Working with Tools

### Input Validation

```python
from pydantic import BaseModel, Field

class ProcessDataInput(BaseModel):
    data: str = Field(..., description="Input data to process")
    format: str = Field("json", description="Output format")
    timeout: int = Field(30, ge=1, le=300, description="Timeout in seconds")

@server.call_tool()
async def process_data(input: ProcessDataInput) -> ToolResult:
    """Process data with validation"""
    # Input is automatically validated
    result = process_logic(input.data, input.format)
    return ToolResult(
        content=[TextContent(type="text", text=result)]
    )
```

### Error Handling

```python
@server.call_tool()
async def risky_operation(item_id: str) -> ToolResult:
    """Handle errors gracefully"""
    try:
        result = await fetch_item(item_id)
        if not result:
            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Item {item_id} not found"
                )],
                isError=True
            )

        return ToolResult(
            content=[TextContent(type="text", text=str(result))]
        )

    except Exception as e:
        return ToolResult(
            content=[TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )],
            isError=True
        )
```

### Async Operations

```python
import asyncio

@server.call_tool()
async def parallel_processing(items: list) -> ToolResult:
    """Process multiple items concurrently"""
    # Run operations in parallel
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)

    return ToolResult(
        content=[TextContent(type="text", text=json.dumps(results))]
    )
```

---

## Integration Examples

### Example 1: Database Query Tool

```python
import sqlite3

@server.call_tool()
async def query_database(sql: str, params: list = None) -> ToolResult:
    """Execute a database query safely"""
    # Validate SQL to prevent injection
    if not is_safe_query(sql):
        return ToolResult(
            content=[TextContent(type="text", text="Invalid query")],
            isError=True
        )

    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        cursor.execute(sql, params or [])
        results = cursor.fetchall()
        conn.close()

        return ToolResult(
            content=[TextContent(type="text", text=json.dumps(results))]
        )

    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Query error: {e}")],
            isError=True
        )
```

### Example 2: File Operations Tool

```python
from pathlib import Path

@server.call_tool()
async def read_file(path: str, encoding: str = "utf-8") -> ToolResult:
    """Read file contents safely"""
    # Prevent directory traversal
    safe_path = Path(path).resolve()
    if not is_in_allowed_directory(safe_path):
        return ToolResult(
            content=[TextContent(type="text", text="Access denied")],
            isError=True
        )

    try:
        content = safe_path.read_text(encoding=encoding)
        return ToolResult(
            content=[TextContent(type="text", text=content)]
        )
    except FileNotFoundError:
        return ToolResult(
            content=[TextContent(type="text", text=f"File not found: {path}")],
            isError=True
        )
```

### Example 3: API Integration Tool

```python
import aiohttp

@server.call_tool()
async def call_api(endpoint: str, method: str = "GET", data: dict = None) -> ToolResult:
    """Call external API safely"""
    # Validate endpoint
    if not is_allowed_endpoint(endpoint):
        return ToolResult(
            content=[TextContent(type="text", text="Endpoint not allowed")],
            isError=True
        )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=endpoint,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result = await response.json()

                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(result)
                    )]
                )

    except asyncio.TimeoutError:
        return ToolResult(
            content=[TextContent(type="text", text="API request timeout")],
            isError=True
        )
```

---

## Troubleshooting

### Issue: Connection Failed

**Error**: `Failed to connect to MCP server`

**Diagnosis**:
```bash
# Check if server is running
ps aux | grep mcp_server

# Check logs
tail -f logs/mcp_server.log

# Test connection
python -c "import socket; s = socket.socket(); s.connect(('localhost', 3000))"
```

**Solutions**:
```bash
# Start server
python mcp_server.py

# Or with debug output
MCP_DEBUG=true python mcp_server.py

# Check port availability
lsof -i :3000
```

## Issue: Tool Not Found

**Error**: `Tool 'my_tool' not found`

**Diagnosis**:
```python
# List available tools
@server.list_tools()
async def list_tools():
    # Check what tools are registered
    return server.tools
```

**Solution**: Ensure tool is decorated with `@server.call_tool()`

## Issue: Input Validation Failed

**Error**: `Invalid input: missing required field 'data'`

**Solution**: Check tool signature and provide all required inputs

```python
# Correct
call_tool("my_tool", {"data": "value", "limit": 10})

# Wrong - missing required field
call_tool("my_tool", {"limit": 10})
```

## Issue: Timeout

**Error**: `Tool execution timed out`

**Solution**: Increase timeout or optimize tool

```yaml
server_options:
  timeout: 60  # Increase from default 30
```

---

## Quick Reference

### Common Tool Pattern

```python
@server.call_tool()
async def my_tool(required_param: str, optional_param: str = "default") -> ToolResult:
    """
    Tool description

    Args:
        required_param: Description
        optional_param: Description with default
    """
    try:
        result = do_work(required_param, optional_param)
        return ToolResult(
            content=[TextContent(type="text", text=result)]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            isError=True
        )
```

### Common Resource Pattern

```python
@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource by URI"""
    if uri.startswith("config://"):
        return read_config(uri.replace("config://", ""))
    elif uri.startswith("docs://"):
        return read_docs(uri.replace("docs://", ""))
    else:
        raise ValueError(f"Unknown resource: {uri}")
```

### Common Prompt Pattern

```python
@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Get prompt template"""
    templates = {
        "review": "Please review this: {code}",
        "explain": "Explain this code: {code}",
    }

    template = templates.get(name)
    if not template:
        raise ValueError(f"Unknown prompt: {name}")

    return GetPromptResult(
        messages=[PromptMessage(role="user", content=template)]
    )
```

---

## Cross-References

- [MCP Security Guide](../mcp/MCP_SECURITY_GUIDE.md)
- [MCP FAQ](../mcp/MCP_FAQ.md)
- [GitHub MCP Integration](../admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md)

---

**Word Count**: 2,124 | **Examples**: 18 | **Patterns**: 8
**Last Updated**: 2026-06-22 | **Status**: ✅ Complete
