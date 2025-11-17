# P1 Fix: API Key Check Now Optional Per Configuration

## Issue Description

**Priority:** P1 (Critical)  
**Status:** ✅ Fixed in commit ddf3619

The middleware was always raising `401 Unauthorized` when the `Authorization` header was missing, regardless of the `settings.api_key_required` configuration flag. This prevented:

- Local bootstrapping without pre-existing tenants
- Accessing admin endpoints to create the first tenant  
- Testing public endpoints
- Using the root endpoint (`/`) as documented

## Root Cause

The `TenantContextMiddleware.dispatch()` method did not check `settings.api_key_required` before enforcing authentication. The configuration flag existed but was never consulted.

## Solution

### Changes to `services/msp_gateway/middleware/tenant_context.py`

```python
async def dispatch(self, request: Request, call_next):
    # Define public paths that skip authentication
    public_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/"]
    
    # If API key not required, also allow admin endpoints for bootstrapping
    if not settings.api_key_required:
        public_paths.append("/admin")
    
    # Check if path should skip auth
    if request.url.path in public_paths or any(request.url.path.startswith(p) for p in public_paths if p != "/"):
        return await call_next(request)
    
    # If API key authentication is disabled, skip the check entirely
    if not settings.api_key_required:
        # No tenant context when auth is disabled
        return await call_next(request)
    
    # ... rest of authentication logic ...
```text

### Changes to Routers

Updated `services/msp_gateway/routers/infer.py` and `services/msp_gateway/routers/kb.py` to handle optional tenant context:

```python
# Get tenant from request state (may be None if API key not required)
tenant = getattr(request.state, "tenant", None)

# Determine tenant_id: use from tenant context or from request
if tenant:
    tenant_id = tenant["tenant_id"]
    # Verify tenant_id matches if tenant context exists
    if request.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
else:
    # No tenant context (API key not required), use tenant_id from request
    tenant_id = request.tenant_id
```text

## Behavior

### With API Key Required (Default, Production)
```bash
export MSP_API_KEY_REQUIRED=1  # or True
```text
- ✅ Requires `Authorization: Bearer <api_key>` header
- ✅ Validates API key against tenant registry
- ✅ Sets `request.state.tenant` with tenant context
- ✅ Enforces tenant ID matching
- ✅ Returns 401 for missing/invalid credentials

### Without API Key (Local Development, Bootstrapping)
```bash
export MSP_API_KEY_REQUIRED=0  # or False
```text
- ✅ Skips `Authorization` header requirement
- ✅ No tenant context in `request.state.tenant`
- ✅ Uses `tenant_id` directly from request body
- ✅ Allows admin endpoints without authentication
- ✅ Enables first-tenant creation workflow

## Testing

### Public Endpoints (Always Accessible)
- `/health` - Health check
- `/docs` - OpenAPI documentation
- `/redoc` - ReDoc documentation  
- `/openapi.json` - OpenAPI schema
- `/` - Root endpoint

### Admin Endpoints (Accessible When `api_key_required=False`)
- `POST /admin/tenants` - Create tenant
- `GET /admin/tenants/{tenant_id}` - Get tenant
- `GET /admin/tenants` - List tenants
- `PATCH /admin/tenants/{tenant_id}` - Update tenant
- `DELETE /admin/tenants/{tenant_id}` - Delete tenant

### Protected Endpoints (Behavior Depends on `api_key_required`)
- `POST /v1/infer` - Inference with RAG
- `POST /v1/query_kb` - Knowledge base query

## Example Workflows

### Bootstrap First Tenant (Local Development)
```bash
# 1. Start gateway without requiring API keys
export MSP_API_KEY_REQUIRED=0
scripts/local/serve_local.sh

# 2. Create first tenant via admin API (no auth required)
curl -X POST http://127.0.0.1:8080/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-tenant",
    "name": "My Tenant",
    "api_key": "my-secret-key"
  }'

# 3. Use the tenant for inference
curl -X POST http://127.0.0.1:8080/v1/infer \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-tenant",
    "prompt": "Hello"
  }'
```text

### Production Deployment
```bash
# 1. Require API keys for all endpoints
export MSP_API_KEY_REQUIRED=1
scripts/local/serve_local.sh

# 2. All requests need Authorization header
curl -X POST http://127.0.0.1:8080/v1/infer \
  -H "Authorization: Bearer my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-tenant",
    "prompt": "Hello"
  }'
```text

## Security Considerations

- ✅ **Default is Secure**: `api_key_required` defaults to `True` in production
- ✅ **Explicit Opt-Out**: Must explicitly set to `False` for open access
- ✅ **Documented Behavior**: Configuration matches documented behavior
- ✅ **Audit Trail**: All requests logged regardless of auth mode
- ✅ **Gradual Rollout**: Can start open and add auth later

## Impact

- ✅ **Local Development**: Simplified bootstrapping workflow
- ✅ **Testing**: Easier to write tests without managing API keys
- ✅ **Production**: Unchanged behavior (auth still required by default)
- ✅ **Backward Compatible**: Existing deployments unaffected

## Verification

```bash
# Test with auth disabled
MSP_API_KEY_REQUIRED=0 python3 -m pytest tests/test_msp_infer_api.py::test_root_endpoint -v

# Test with auth enabled (default)
python3 -m pytest tests/test_msp_infer_api.py::test_infer_endpoint_no_auth -v
```text

---

**Fixed By:** @copilot  
**Commit:** ddf3619  
**Date:** 2025-11-01
