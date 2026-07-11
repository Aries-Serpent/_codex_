# TROUBLESHOOTING GUIDE: Common Issues and Solutions
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 1.0.0  
**Last Updated: 2026-07-10
**Audience:** Developers, DevOps, Support  

---

## Quick Diagnostics

Before diving deep, run this diagnostic script:

```bash
#!/bin/bash
# diagnose.sh

echo "=== Codex Diagnostic Report ==="
echo "Time: $(date)"
echo ""

echo "1. PYTHON & ENVIRONMENT"
python3 --version
python3 -c "import codex; print(f'Codex version: {codex.__version__}')" 2>&1

echo ""
echo "2. SYSTEM RESOURCES"
echo "CPU: $(nproc) cores"
free -h
df -h /
lsof | wc -l

echo ""
echo "3. SERVICES"
systemctl status codex-api --no-pager | head -5
systemctl status codex-worker --no-pager | head -5

echo ""
echo "4. CONNECTIVITY"
curl -s -o /dev/null -w "API: %{http_code}\n" http://localhost:8000/health
echo "Database: $(sqlite3 /var/lib/codex/codex.db 'SELECT 1' 2>&1)"

echo ""
echo "5. RECENT ERRORS"
grep "ERROR\|Exception\|Traceback" /var/log/codex/api.log | tail -5

echo ""
echo "6. DISK SPACE DETAILS"
du -sh /var/lib/codex/*
du -sh /var/log/codex/*

echo "=== End Diagnostic Report ==="
```

---

## Problem Categories

- [Environment & Setup Issues](#environment--setup-issues)
- [Data Pipeline Issues](#data-pipeline-issues)
- [Model & Training Issues](#model--training-issues)
- [API & Inference Issues](#api--inference-issues)
- [Database Issues](#database-issues)
- [Performance Issues](#performance-issues)

---

## Environment & Setup Issues

### Issue: "ModuleNotFoundError: No module named 'codex'"

**Cause:** Package not installed or virtual environment not activated

**Solution:**

```bash
# Check if package installed
pip list | grep codex

# If not installed:
cd /opt/codex
pip install -e .

# If pip install fails, check Python version
python3 --version  # Must be 3.12+

# If using virtual env, verify activation
which python  # Should be path to venv

# If not, activate manually
source /opt/codex/venv/bin/activate
```

---

### Issue: "ImportError: cannot import name 'XYZ' from 'codex'"

**Cause:** Module structure changed, or importing from wrong location

**Solution:**

```bash
# 1. Check module exists
python -c "from codex import XYZ; print(XYZ)"

# 2. List available modules
python -c "import codex; print(dir(codex))"

# 3. Check if module is defined in __init__.py
cat src/codex/__init__.py | grep -i xyz

# 4. Reimport might be needed after code changes
# If working on development:
pip install -e . --force-reinstall --no-deps
```

---

### Issue: "CUDA not available" but GPU present

**Cause:** PyTorch not compiled with CUDA support

**Solution:**

```bash
# 1. Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# 2. Check CUDA toolkit installed
nvcc --version
nvidia-smi

# 3. Reinstall PyTorch with CUDA support
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. Verify installation
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
"
```

---

## Data Pipeline Issues

### Issue: "FileNotFoundError: data/train.csv not found"

**Cause:** Data file doesn't exist or path is incorrect

**Solution:**

```bash
# 1. Verify file exists
ls -la data/train.csv

# 2. Check absolute path
pwd
ls -la /full/path/to/data/train.csv

# 3. Check config for correct path
grep "train_path\|data_path" /etc/codex/config.yaml

# 4. If file in different location:
# Option 1: Create symlink
ln -s /actual/path/data.csv data/train.csv

# Option 2: Update config
sed -i 's|data_path:.*|data_path: /actual/path|' /etc/codex/config.yaml

# 3. Test loading
python -c "
from codex.data import DataLoader
data = DataLoader('/actual/path/train.csv')
print(f'Loaded {len(data)} samples')
"
```

---

### Issue: "UnicodeDecodeError: 'utf-8' codec can't decode byte 0x85"

**Cause:** File encoding is not UTF-8

**Solution:**

```bash
# 1. Detect file encoding
file data/train.csv
chardet data/train.csv  # If installed: pip install chardet

# 2. Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 data/train.csv > data/train_utf8.csv

# 3. Or, let Codex auto-detect (if supported)
# In config.yaml:
# data:
#   encoding: auto

# 4. Test conversion
python -c "
import pandas as pd
df = pd.read_csv('data/train_utf8.csv')
print(f'✓ Loaded {len(df)} rows')
"
```

---

### Issue: "Out of memory" during data loading

**Cause:** Dataset too large to fit in RAM

**Solution:**

```bash
# 1. Check dataset size
du -h data/train.csv
wc -l data/train.csv

# 2. Use chunked reading
python -c "
from codex.data import DataLoader
loader = DataLoader('data/train.csv', chunk_size=10000)
for batch in loader:
    print(f'Batch size: {len(batch)}')
    # Process batch
"

# 3. Reduce batch size in config
# config.yaml:
# data:
#   batch_size: 16  # Reduce from 32

# 4. Use streaming/generator approach
# Instead of loading all data, load chunks
```

---

## Model & Training Issues

### Issue: "Shape mismatch: input has 10 features, model expects 768"

**Cause:** Model config doesn't match data features

**Solution:**

```bash
# 1. Check data feature count
python -c "
import pandas as pd
df = pd.read_csv('data/train.csv')
print(f'Features: {len(df.columns) - 1}')  # -1 for target
print(f'Columns: {df.columns.tolist()}')
"

# 2. Check model config
cat /etc/codex/config.yaml | grep -A 5 "model:"

# 3. Update model config to match data
sed -i 's|input_features:.*|input_features: 10|' /etc/codex/config.yaml

# 4. Or, update data to match model
# Might need feature engineering or dimensionality reduction
python -c "
from sklearn.decomposition import PCA
import pandas as pd

df = pd.read_csv('data/train.csv')
features = df.iloc[:, :-1]
target = df.iloc[:, -1]

pca = PCA(n_components=768)
features_pca = pca.fit_transform(features)

print(f'Reduced to {features_pca.shape[1]} dimensions')
"
```

---

### Issue: "NaN values in loss" (loss becomes NaN during training)

**Cause:** Numerical instability, bad learning rate, or bad data

**Solution:**

```bash
# 1. Check learning rate (too high?)
grep "learning_rate" /etc/codex/config.yaml
# If >1e-2, probably too high

# 2. Reduce learning rate
sed -i 's|learning_rate:.*|learning_rate: 1e-5|' /etc/codex/config.yaml

# 3. Check for NaN in data
python -c "
import pandas as pd
import numpy as np

df = pd.read_csv('data/train.csv')
nan_count = df.isna().sum()
print(f'NaN values: {nan_count}')

if nan_count.sum() > 0:
    print('Columns with NaN:')
    print(nan_count[nan_count > 0])
    
    # Drop NaN
    df_clean = df.dropna()
    df_clean.to_csv('data/train_clean.csv', index=False)
    print(f'Saved cleaned data: {len(df_clean)} rows')
"

# 4. Use lower precision (might help or hurt)
# Try mixed precision training in config
# training:
#   mixed_precision: true
```

---

### Issue: "CUDA out of memory" during training

**Cause:** Batch size or model too large for GPU

**Solution:**

```bash
# 1. Check GPU memory
nvidia-smi

# 2. Reduce batch size in config
sed -i 's|batch_size:.*|batch_size: 8|' /etc/codex/config.yaml

# 3. Enable gradient accumulation (simulates larger batches)
# training:
#   gradient_accumulation_steps: 4

# 4. Use model quantization
# model:
#   quantize: true

# 5. Use memory-efficient attention
# model:
#   attention_type: efficient

# 6. If still not enough, use CPU training (slow but works)
# training:
#   device: cpu
```

---

## API & Inference Issues

### Issue: "Connection refused" on API calls

**Cause:** API service not running or listening on different port

**Solution:**

```bash
# 1. Check if service running
systemctl status codex-api

# 2. Check if port listening
sudo netstat -tlnp | grep 8000

# 3. Start service
sudo systemctl start codex-api

# 4. Wait for startup
sleep 5

# 5. Check logs
tail -n 20 /var/log/codex/api.log

# 6. If port already in use
# Find process using port 8000
fuser 8000/tcp
# Kill it
fuser -k 8000/tcp

# 7. If service still won't start, check config
python -m codex.validate_config /etc/codex/config.yaml
```

---

### Issue: "401 Unauthorized" on API requests

**Cause:** Missing or invalid authentication token

**Solution:**

```bash
# 1. Check if auth is required
grep -i "require_auth\|auth_enabled" /etc/codex/config.yaml

# 2. Get valid token
# If testing:
export TOKEN="test-token-12345"

# 3. Include token in request
curl -H "Authorization: ******" \
  http://localhost:8000/api/v1/inference

# 4. If token generation broken:
python -c "
from codex.auth import generate_token
token = generate_token('user@example.com')
print(f'Token: {token}')
"

# 5. If using JWT, check secret
grep "jwt_secret\|JWT_SECRET" /etc/codex/config.yaml
```

---

## Database Issues

### Issue: "sqlite3.DatabaseError: database disk image is malformed"

**Cause:** Database file corrupted (power loss, disk error, concurrent access)

**Solution:**

```bash
# 1. Stop all services
sudo systemctl stop codex-api
sudo systemctl stop codex-worker

# 2. Try repair
sqlite3 /var/lib/codex/codex.db "PRAGMA integrity_check;"

# 3. If repair succeeds, you're done:
sudo systemctl start codex-api

# 4. If repair fails, restore from backup
sqlite3 /var/lib/codex/codex.db < /var/backups/codex_backup_latest.sql

# 5. If no backup, recreate schema
python -m codex.db.init_schema

# 6. Restart
sudo systemctl start codex-api
```

---

### Issue: "database is locked" timeout

**Cause:** Long-running transaction or concurrent access

**Solution:**

```bash
# 1. Find process holding lock
lsof | grep codex.db

# 2. Check running queries
sqlite3 /var/lib/codex/codex.db "PRAGMA database_list;"

# 3. If safe to kill:
kill -9 <PID>

# 4. Or increase lock timeout (in config):
# database:
#   timeout: 30  # seconds

# 5. Or use WAL mode (Write-Ahead Logging):
sqlite3 /var/lib/codex/codex.db "PRAGMA journal_mode=WAL;"
```

---

## Performance Issues

### Issue: High CPU usage (90%+)

**Cause:** CPU-bound operation, inefficient code, or insufficient scaling

**Solution:**

```bash
# 1. Profile which process is consuming CPU
top -p $(pgrep -f 'python -m codex.api')

# 2. Profile with py-spy
pip install py-spy
py-spy record -o profile.svg --pid $(pgrep -f codex.api)

# 3. Reduce number of workers if using multiprocessing
# api:
#   workers: 2  # Reduce from 4

# 4. Scale horizontally (add more instances)
kubectl scale deployment codex-api --replicas=5

# 5. Check for infinite loops or uncached computations
# Add timing to code:
import time
start = time.time()
result = expensive_operation()
print(f'Operation took {time.time() - start:.2f}s')
```

---

### Issue: High memory usage, memory leak

**Cause:** Objects not being freed, growing data structures, model staying in memory

**Solution:**

```bash
# 1. Check memory growth
watch -n 5 'ps aux | grep codex | grep -v grep'

# 2. Use memory profiler
pip install memory-profiler
python -m memory_profiler my_script.py

# 3. Check for circular references
python -c "
import gc
import sys
from codex import SomeClass

obj = SomeClass()
refs = gc.get_referrers(obj)
print(f'Number of references: {len(refs)}')
"

# 4. Force garbage collection periodically
# In code:
import gc
@scheduler.every(1, 'hour').do
def cleanup():
    gc.collect()

# 5. Restart service to clear memory
sudo systemctl restart codex-api
```

---

### Issue: Slow query performance (>1 second)

**Cause:** Missing index, inefficient query, or large dataset

**Solution:**

```bash
# 1. Enable query timing
sqlite3 /var/lib/codex/codex.db ".timer on"

# 2. Analyze query plan
sqlite3 /var/lib/codex/codex.db "EXPLAIN QUERY PLAN SELECT ...;"

# 3. Add index if needed
sqlite3 /var/lib/codex/codex.db "CREATE INDEX idx_model_name ON models(name);"

# 4. Rebuild indexes
sqlite3 /var/lib/codex/codex.db "REINDEX;"

# 5. Analyze and optimize
sqlite3 /var/lib/codex/codex.db "ANALYZE;"
```

---

## Getting Help

**If you can't find the issue:**

1. **Gather diagnostics:**
   ```bash
   bash diagnose.sh > diagnostics.txt
   tail -n 200 /var/log/codex/api.log >> diagnostics.txt
   ```

2. **Search the issue tracker:**
   - https://github.com/Aries-Serpent/_codex_/issues

3. **Ask on discussions:**
   - https://github.com/Aries-Serpent/_codex_/discussions

4. **File a new issue with:**
   - Diagnostics output
   - Last 50 lines of logs
   - Steps to reproduce
   - Expected vs actual behavior

---

**Last updated: 2026-07-10
**Maintained by:** @mbaetiong
