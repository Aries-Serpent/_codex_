# RAG Module Device Placement Best Practices

**Module**: `src/codex/rag/`  
**Last Updated**: 2026-06-22  
**Status**: Production Guidelines  

---

## Overview

This document provides best practices for device placement in RAG (Retrieval-Augmented Generation) modules to ensure PyTorch 2.0+ compatibility and prevent meta tensor errors.

---

## ⚠️ Critical: Meta Tensor Compatibility

### The Problem

PyTorch 2.0+ introduced **meta tensors** for memory-efficient model initialization. Direct `.to(device)` calls on models with meta tensors raise:

```text
NotImplementedError: Cannot copy out of meta tensor; no data!
```

### The Solution

**ALWAYS use `safe_model_to_device()`** for all model device placement.

For complete documentation, see: `.codex/CODING_STANDARDS_ML_DEVICE_PLACEMENT.md`

---

**Enforcement**: MANDATORY for all RAG modules  
**Linter**: `scripts/lint/check_device_placement.py`  
**Tests**: `tests/rag/test_device_placement.py`

Last updated: 2026-06-22
