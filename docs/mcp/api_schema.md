# MCP HTTP API Schema (Prototype)

The FastAPI prototype in `src/mcp/server/http.py` exposes three endpoints compatible with edge deployments (Cloudflare Workers) and Fly.io containers.

## Endpoints
- `GET /mcp/v1/health` → `{ "status": "healthy", "documents": <int> }`
- `POST /mcp/v1/query`
  - Headers: `X-MCP-API-Key` or `Authorization: Bearer <token>`
  - Body:
    ```json
    { "query": "<text>", "top_k": 5, "filters": {"scope": "repo"} }
    ```
  - Response:
    ```json
    { "results": [{"id": "demo-1", "score": 1.0, "content": "...", "metadata": {"scope": "repo"}}] }
    ```
- `POST /mcp/v1/context`
  - Headers: same as `/query`
  - Body:
    ```json
    { "items": [{"id": "doc-1", "content": "text", "metadata": {"scope": "repo"}}] }
    ```
  - Response: `{ "upserted": 1 }`

## Workers (Node) sketch
```ts
export default {
  async fetch(request: Request): Promise<Response> {
    if (request.method === "GET" && request.url.endsWith("/mcp/v1/health")) {
      return Response.json({ status: "healthy", documents: 0 });
    }
    // Mirror FastAPI payloads for /query and /context
    return new Response("not implemented", { status: 501 });
  }
};
```
