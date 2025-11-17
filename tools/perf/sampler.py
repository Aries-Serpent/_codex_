import json
import time
from pathlib import Path

try:
    import psutil
except Exception:
    psutil = None
try:
    import pynvml as nvml
except Exception:
    nvml = None


class PerfSampler:
    def __init__(self, out="artifacts/logs/perf.ndjson", interval=2.0):
        self.out = Path(out)
        self.out.parent.mkdir(parents=True, exist_ok=True)
        self.interval = interval
        if nvml:
            try:
                nvml.nvmlInit()
            except Exception:
                # GPU not available or NVML initialization failed
                pass

    def sample_once(self):
        row = {"ts": time.time()}
        if psutil:
            row.update(cpu=psutil.cpu_percent(), mem=psutil.virtual_memory()._asdict())
        if nvml:
            try:
                dev = nvml.nvmlDeviceGetHandleByIndex(0)
                row["gpu"] = {
                    "util": nvml.nvmlDeviceGetUtilizationRates(dev).gpu,
                    "mem_used": nvml.nvmlDeviceGetMemoryInfo(dev).used,
                }
            except Exception:
                # GPU metrics not available or device error
                pass
        with self.out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    def run(self, steps=5):
        for _ in range(steps):
            self.sample_once()
            time.sleep(self.interval)
