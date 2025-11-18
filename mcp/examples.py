"""
MCP Examples and Usage Patterns

This module provides practical examples for using MCP capabilities.
All examples are self-contained and demonstrate real-world usage patterns.
"""

from typing import Any, Dict
from mcp.registry import MCPToolRegistry
from mcp.auth import Principal, MCPAuthenticator, MCPAuthorizer
from mcp.rate_limit import MCPRateLimiter
from mcp.errors import ToolNotFound, RateLimitExceeded, Unauthorized
from mcp.versioning import negotiate_version, MCP_VERSIONS
from mcp.config import MCPConfig
from mcp.safeguards import (
    compute_checksum, verify_checksum, confirm_action,
    dry_run_wrapper, safe_seed_rng
)


# Example 1: Basic Tool Registration
def example_basic_tool_registration():
    """
    Example: Register a simple tool with the MCP registry.
    
    This demonstrates the core mcp-tooling-registry capability.
    """
    registry = MCPToolRegistry()
    
    # Define a simple echo tool
    def echo_tool(params: Dict[str, Any]) -> Dict[str, Any]:
        """Echo back the input message."""
        message = params.get("message", "")
        return {"echo": message, "length": len(message)}
    
    # Register the tool with schema and metadata
    registry.register_tool(
        name="echo",
        handler=echo_tool,
        schema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message to echo"}
            },
            "required": ["message"]
        },
        metadata={
            "description": "Echo tool that returns the input message",
            "version": "1.0",
            "category": "utility"
        }
    )
    
    # List all registered tools
    tools = registry.list_tools()
    print(f"Registered tools: {[t['name'] for t in tools]}")
    
    # Get and execute the tool
    handler = registry.get_tool("echo")
    if handler:
        result = handler({"message": "Hello MCP!"})
        print(f"Result: {result}")
    
    return registry


# Example 2: Authentication Workflow
def example_authentication_workflow():
    """
    Example: Complete authentication workflow with credential hashing.
    
    This demonstrates the mcp-authz-authn capability.
    """
    # Create authenticator
    authenticator = MCPAuthenticator()
    
    # Simulate credential from API key header
    api_key = "secret-api-key-123"
    
    # Create principal from credential (SHA-256 hashed)
    principal = Principal.from_credential(api_key)
    print(f"Principal ID (hashed): {principal.principal_id}")
    
    # Generate session token
    session_token = authenticator.generate_session_token(principal)
    print(f"Session token: {session_token[:32]}...")
    
    # Create authorizer
    authorizer = MCPAuthorizer()
    
    # Check authorization for tool access
    tool_name = "kb.search"
    if authorizer.authorize(principal, tool_name):
        print(f"✓ Principal authorized for {tool_name}")
    else:
        print(f"✗ Principal NOT authorized for {tool_name}")
        raise Unauthorized(f"Access denied to {tool_name}")
    
    # Compute permission hash for audit
    perm_hash = authorizer.compute_permission_hash(
        principal.principal_id, 
        tool_name
    )
    print(f"Permission hash: {perm_hash[:32]}...")
    
    return principal


# Example 3: Rate Limiting
def example_rate_limiting():
    """
    Example: Enforce rate limits with token bucket algorithm.
    
    This demonstrates the mcp-rate-limiting capability.
    """
    # Create rate limiter: 2 requests/second, burst of 5
    limiter = MCPRateLimiter(rate=2.0, capacity=5, seed=42)
    
    principal_id = "user123"
    tool_name = "expensive_operation"
    
    # Simulate multiple requests
    requests = []
    for i in range(10):
        allowed = limiter.allow(principal_id, tool_name)
        requests.append(allowed)
        
        if allowed:
            print(f"Request {i+1}: ✓ Allowed")
        else:
            print(f"Request {i+1}: ✗ Rate limited")
            # In real scenario, raise RateLimitExceeded
    
    allowed_count = sum(requests)
    print(f"\nAllowed: {allowed_count}/10 requests")
    print(f"Rate limited: {10 - allowed_count}/10 requests")
    
    # Reset rate limit for testing
    limiter.reset(principal_id, tool_name)
    print("\nRate limit reset - quota restored")
    
    return limiter


# Example 4: Error Handling
def example_error_handling():
    """
    Example: Proper error handling with MCP error types.
    
    This demonstrates the mcp-error-handling capability.
    """
    registry = MCPToolRegistry()
    registry.register_tool("valid_tool", lambda x: {"status": "ok"})
    
    # Case 1: Tool not found
    try:
        handler = registry.get_tool("nonexistent_tool")
        if handler is None:
            raise ToolNotFound("Tool 'nonexistent_tool' not found in registry")
    except ToolNotFound as e:
        print(f"ToolNotFound: {e.message} (HTTP {e.http_status})")
        error_dict = e.to_dict()
        print(f"Error dict: {error_dict}")
    
    # Case 2: Rate limit exceeded
    try:
        limiter = MCPRateLimiter(rate=1.0, capacity=1, seed=42)
        limiter.allow("user", "tool")  # First request ok
        limiter.allow("user", "tool")  # Second request ok (burst)
        if not limiter.allow("user", "tool"):  # Third request limited
            raise RateLimitExceeded("Too many requests - please slow down")
    except RateLimitExceeded as e:
        print(f"\nRateLimitExceeded: {e.message} (HTTP {e.http_status})")
    
    # Case 3: Unauthorized access
    try:
        api_key = None  # Simulating missing API key
        if not api_key:
            raise Unauthorized("Missing or invalid API key")
    except Unauthorized as e:
        print(f"\nUnauthorized: {e.message} (HTTP {e.http_status})")
    
    print("\n✓ All error types handled correctly")


# Example 5: Schema Validation
def example_schema_validation():
    """
    Example: Validate tool requests and responses with Pydantic schemas.
    
    This demonstrates the mcp-schema-validation capability.
    """
    from pydantic import BaseModel, ValidationError
    
    # Define request schema
    class SearchRequest(BaseModel):
        query: str
        limit: int = 10
        filters: Dict[str, Any] = {}
    
    # Define response schema
    class SearchResponse(BaseModel):
        results: list[str]
        total: int
        query: str
    
    # Valid request
    try:
        request = SearchRequest(query="mcp capabilities", limit=5)
        print(f"✓ Valid request: {request.model_dump()}")
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    
    # Invalid request (missing required field)
    try:
        request = SearchRequest(limit=5)  # Missing 'query'
    except ValidationError as e:
        print(f"\n✗ Expected validation error: Missing 'query' field")
        print(f"  Error count: {len(e.errors())}")
    
    # Valid response
    response = SearchResponse(
        results=["doc1", "doc2", "doc3"],
        total=3,
        query="mcp capabilities"
    )
    print(f"\n✓ Valid response: {response.model_dump()}")


# Example 6: Configuration with Checksums
def example_configuration_with_checksums():
    """
    Example: Load and verify configuration with checksum validation.
    
    This demonstrates the mcp configuration and safeguards capabilities.
    """
    # Compute checksum of configuration data
    config_data = '{"name": "mcp-server", "version": "1.0"}'
    checksum = compute_checksum(config_data)
    
    print(f"Configuration data: {config_data}")
    print(f"SHA-256 checksum: {checksum}")
    
    # Verify checksum (simulating integrity check)
    expected_checksum = checksum
    is_valid = verify_checksum(config_data, expected_checksum)
    
    if is_valid:
        print("✓ Configuration checksum verified - integrity intact")
    else:
        print("✗ Configuration checksum mismatch - possible tampering")
    
    # Test with tampered data
    tampered_data = '{"name": "mcp-server", "version": "2.0"}'
    is_valid = verify_checksum(tampered_data, expected_checksum)
    
    if not is_valid:
        print("✓ Tampered data detected correctly")


# Example 7: Version Negotiation
def example_version_negotiation():
    """
    Example: Negotiate MCP protocol version with client.
    
    This demonstrates the mcp-versioning-compat capability.
    """
    print(f"Server supports MCP versions: {MCP_VERSIONS}")
    
    # Client supports matching version
    client_versions = ["1.0", "0.9"]
    try:
        chosen_version = negotiate_version(client_versions)
        print(f"✓ Negotiated version: {chosen_version}")
    except Exception as e:
        print(f"✗ Version negotiation failed: {e}")
    
    # Client supports incompatible versions
    incompatible_versions = ["2.0", "0.5"]
    try:
        chosen_version = negotiate_version(incompatible_versions)
        print(f"Negotiated version: {chosen_version}")
    except Exception as e:
        print(f"\n✓ Expected error for incompatible versions: {e}")


# Example 8: Multi-Tenant Tool Access
def example_multi_tenant_access():
    """
    Example: Tenant-scoped tool access and resource isolation.
    
    This demonstrates the mcp-multi-tenant capability.
    """
    # Create principals for different tenants
    tenant1_user = Principal(principal_id="tenant1:user123")
    tenant2_user = Principal(principal_id="tenant2:user456")
    
    print(f"Tenant 1 principal: {tenant1_user.principal_id}")
    print(f"Tenant 2 principal: {tenant2_user.principal_id}")
    
    # Tenant-scoped data store
    tenant_data = {
        "tenant1": {"resources": ["res1", "res2"]},
        "tenant2": {"resources": ["res3", "res4"]}
    }
    
    def get_tenant_resources(principal: Principal):
        tenant_id = principal.principal_id.split(":")[0]
        return tenant_data.get(tenant_id, {}).get("resources", [])
    
    # Each tenant sees only their resources
    tenant1_resources = get_tenant_resources(tenant1_user)
    tenant2_resources = get_tenant_resources(tenant2_user)
    
    print(f"\nTenant 1 resources: {tenant1_resources}")
    print(f"Tenant 2 resources: {tenant2_resources}")
    print("✓ Tenant isolation maintained")


# Example 9: Safeguards - Confirmation and Dry Run
def example_safeguards_confirm_dry_run():
    """
    Example: Use confirmation prompts and dry-run mode for safety.
    
    This demonstrates the mcp safeguards capability.
    """
    # Confirmation for critical action
    action_description = "Delete all user data"
    confirmed = confirm_action(
        prompt=f"Are you sure you want to: {action_description}?",
        default=False,
        require_confirm=True,
        offline=True  # In offline mode, uses default
    )
    
    if confirmed:
        print("✓ Action confirmed (offline mode used default)")
    else:
        print("✗ Action cancelled")
    
    # Dry run wrapper
    def dangerous_operation(data):
        print(f"EXECUTING: Deleting {len(data)} items")
        return {"deleted": len(data)}
    
    # Wrap function for dry run
    dry_run_func = dry_run_wrapper(dangerous_operation, dry_run=True)
    result = dry_run_func(["item1", "item2", "item3"])
    print(f"Dry run result: {result} (None = not executed)")
    
    # Execute for real
    real_func = dry_run_wrapper(dangerous_operation, dry_run=False)
    result = real_func(["item1", "item2"])
    print(f"Real execution result: {result}")


# Example 10: Complete Integration Workflow
def example_complete_integration():
    """
    Example: Complete end-to-end MCP integration workflow.
    
    This demonstrates integration of all MCP capabilities.
    """
    print("=== MCP Complete Integration Example ===\n")
    
    # 1. Initialize components
    registry = MCPToolRegistry()
    authenticator = MCPAuthenticator()
    authorizer = MCPAuthorizer()
    limiter = MCPRateLimiter(rate=5.0, capacity=20, seed=42)
    
    # 2. Register tool
    def search_tool(params):
        return {"results": [f"match: {params['query']}"]}
    
    registry.register_tool(
        "kb.search",
        search_tool,
        schema={"type": "object", "properties": {"query": {"type": "string"}}},
        metadata={"description": "Search knowledge base"}
    )
    print("✓ Tool registered")
    
    # 3. Authenticate user
    principal = Principal.from_credential("api-key-xyz")
    session_token = authenticator.generate_session_token(principal)
    print(f"✓ User authenticated: {principal.principal_id[:16]}...")
    print(f"✓ Session token: {session_token[:16]}...")
    # 4. Authorize access
    tool_name = "kb.search"
    if not authorizer.authorize(principal, tool_name):
        raise Unauthorized(f"Access denied to {tool_name}")
    print(f"✓ User authorized for {tool_name}")
    
    # 5. Check rate limit
    if not limiter.allow(principal.principal_id, tool_name):
        raise RateLimitExceeded("Rate limit exceeded")
    print("✓ Rate limit check passed")
    
    # 6. Execute tool
    handler = registry.get_tool(tool_name)
    if not handler:
        raise ToolNotFound(f"Tool '{tool_name}' not found")
    
    result = handler({"query": "mcp integration"})
    print(f"✓ Tool executed: {result}")
    
    # 7. Verify checksum (optional)
    result_str = str(result)
    checksum = compute_checksum(result_str)
    print(f"✓ Result checksum: {checksum[:32]}...")
    
    print("\n=== Integration Complete ===")
    return result


# Run all examples
if __name__ == "__main__":
    print("MCP Examples - Demonstrating All Capabilities\n")
    print("=" * 60)
    
    examples = [
        ("Basic Tool Registration", example_basic_tool_registration),
        ("Authentication Workflow", example_authentication_workflow),
        ("Rate Limiting", example_rate_limiting),
        ("Error Handling", example_error_handling),
        ("Schema Validation", example_schema_validation),
        ("Configuration with Checksums", example_configuration_with_checksums),
        ("Version Negotiation", example_version_negotiation),
        ("Multi-Tenant Access", example_multi_tenant_access),
        ("Safeguards - Confirm & Dry Run", example_safeguards_confirm_dry_run),
        ("Complete Integration", example_complete_integration),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'=' * 60}")
        print(f"Example {i}: {name}")
        print('=' * 60)
        try:
            func()
        except Exception as e:
            print(f"Error in example: {e}")
    
    print(f"\n{'=' * 60}")
    print("All examples completed!")
    print('=' * 60)
