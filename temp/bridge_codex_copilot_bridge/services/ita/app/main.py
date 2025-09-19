
from fastapi import FastAPI
from .routers import kb, repo, tests, gitops
import os

app = FastAPI(title="Internal Tools API (ITA)")

app.include_router(kb.router)
app.include_router(repo.router)
app.include_router(tests.router)
app.include_router(gitops.router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "env": {"GITHUB_APP_ID": bool(os.getenv("GITHUB_APP_ID"))}}

# Run: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
