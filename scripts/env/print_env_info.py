#!/usr/bin/env python3
import platform
import sys

print(f"OS: {platform.platform()}")
print(f"Python: {sys.version.split()[0]}")
try:
    import torch

    print(
        f"CUDA: {getattr(torch.version, 'cuda', 'unknown')} (available: {torch.cuda.is_available()})"
    )
except Exception:
    print("CUDA: not installed")
