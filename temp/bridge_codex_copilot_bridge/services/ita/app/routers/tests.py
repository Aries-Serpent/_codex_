
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import random, time
from ..auth import require_api_key, require_request_id

router = APIRouter(prefix="/tests", tags=["tests"])

class TestsRunIn(BaseModel):
    targets: list[str]
    timeout_s: int = 300

@router.post("/run")
async def tests_run(payload: TestsRunIn, _=Depends(require_api_key), __=Depends(require_request_id)):
    # Simulated test run
    total = max(1, len(payload.targets) * 3)
    failed = random.choice([0, 1])
    passed = total - failed
    duration = round(random.uniform(1.5, 5.0), 2)
    failures = []
    if failed:
        failures.append({"name": "tests/test_example.py::test_edge", "message": "Edge case failed"})
    time.sleep(0.05)
    return {"summary": {"total": total, "passed": passed, "failed": failed, "duration_s": duration}, "failures": failures}
