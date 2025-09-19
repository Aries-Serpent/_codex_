
import os, json, asyncio, httpx
from .openai_wrapper import stream

ITA_URL = os.getenv("ITA_URL", "http://localhost:8080")
API_KEY = os.getenv("ITA_API_KEY", "")

def _headers():
    return {"X-API-Key": API_KEY, "X-Request-Id": "codex-demo-1"}

async def call_tool(name: str, args: dict):
    async with httpx.AsyncClient(timeout=60) as client:
        if name == "kb_search":
            r = await client.post(f"{ITA_URL}/kb/search", headers=_headers(), json={"query": args["query"], "top_k": args.get("top_k",5)})
            return r.json()
        if name == "repo_hygiene":
            r = await client.post(f"{ITA_URL}/repo/hygiene", headers=_headers(), json={"diff": args["diff"], "checks": args.get("checks")})
            return r.json()
        if name == "tests_run":
            r = await client.post(f"{ITA_URL}/tests/run", headers=_headers(), json={"targets": args["targets"], "timeout_s": args.get("timeout_s",300)})
            return r.json()
        if name == "git_create_pr":
            params = {"confirm": bool(args.get("confirm", False)), "dry_run": bool(args.get("dry_run", True))}
            body = {k: v for k, v in args.items() if k in ["repo","title","body","base","head","labels"]}
            r = await client.post(f"{ITA_URL}/git/create-pr", headers=_headers(), params=params, json=body)
            return r.json()
        raise ValueError(f"unknown tool {name}")

async def main():
    system = {"role":"system","content":"You are a senior engineer. Plan the smallest next step and then suggest a tool call."}
    user = {"role":"user","content":"We need guidance on risky refactor; search our KB and create a dry-run PR template."}
    print("=== LLM planning (simulated streaming) ===")
    async for delta in stream([system, user]):
        print(delta, end="")

    print("\n\n=== Tool: kb_search ===")
    kb = await call_tool("kb_search", {"query": "risky refactor checklist", "top_k": 3})
    print(json.dumps(kb, indent=2))

    print("\n=== Tool: git_create_pr (dry-run) ===")
    pr = await call_tool("git_create_pr", {
        "repo":"org/repo","title":"Refactor: step 1 (scoped)","body":"See checklist & plan",
        "base":"main","head":"refactor/step-1","labels":["codex","proposal"],
        "dry_run": True, "confirm": False
    })
    print(json.dumps(pr, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
