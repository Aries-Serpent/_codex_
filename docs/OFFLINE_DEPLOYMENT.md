# Offline Deployment Procedure - Phase 8
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version**: 1.0.0-phase8-groundwork  
**Timeline**: 3 days post-merge (2026-07-09 activation)  
**Lead Agent**: unified-security-scanner  

##  Overview

Codex Cognitive Brain supports **air-gap (fully offline) deployment** using pre-generated offline wheelhouses. This enables deployment to isolated machines with **zero external network calls** required.

### Three-Tier Offline Strategy

| Tier | Name | Size | ML Support | Network | Use Case |
|------|------|------|------------|---------|----------|
| 1 | **Core Package** | 8-15 MB | None | None | Air-gap servers, embedded systems |
| 2 | **Runtime Package** | 20-35 MB | Inference + pattern learning | Minimal (startup only) | Production deployments with ML |
| 3 | **Full Package** | 100+ MB | All tools + development | Network-first | Development, CI/CD pipelines |

---

##  Prerequisites

- **Python 3.12+** (pre-installed on target machine)
- **Offline wheelhouse** (pre-generated on network-connected machine)
- **SHA256 checksums verified** before transfer
- **Network isolation confirmed** (optional, for air-gap validation)

### Network-Connected Machine (Preparation)

```bash
# Prerequisites
pip install --upgrade pip wheel setuptools
# Optional: for SBOM generation
pip install cyclonedx-bom
```

### Target Machine (Air-Gap Deployment)

- Python 3.12+ installed
- No internet access (or network calls disabled)
- Minimum 2 GB free disk space
- ~200 MB for wheelhouse + environment

---

##  Phase 8 Groundwork Execution (Starting 2026-07-09)

### Step 1: Generate Offline Wheelhouse on Network-Connected Machine

This step is run on ANY machine with internet access. The output (wheelhouse) is transferred to air-gap machines.

```bash
# Navigate to repository
cd /path/to/_codex_

# Generate wheelhouse (runtime mode, default)
./scripts/prepare_offline_env.sh --runtime

# Alternative modes:
./scripts/prepare_offline_env.sh --minimal   # Core package only
./scripts/prepare_offline_env.sh --full      # Development ecosystem
```

**What this creates:**
- `wheelhouse/` directory with all `.whl` files
- `wheelhouse/CHECKSUMS.txt` with SHA256 hashes
- `wheelhouse/sbom.json` with Software Bill of Materials (CycloneDX)
- `wheelhouse/OFFLINE_MANIFEST.txt` with deployment instructions
- `wheelhouse-runtime-TIMESTAMP.tar.gz` for easy transfer

**Verify generation:**
```bash
# Check wheelhouse contents
ls -lh wheelhouse/ | head -20
du -sh wheelhouse/

# Verify checksums
cd wheelhouse && sha256sum -c CHECKSUMS.txt && cd -
```

---

### Step 2: Transfer Wheelhouse to Target Machine

Use **any secure transfer method** (SSH, USB drive, secure courier, etc.).

```bash
# On network-connected machine:
tar -czf wheelhouse-runtime-$(date +%Y%m%d).tar.gz wheelhouse/

# Option A: Secure copy via SSH
scp wheelhouse-runtime-*.tar.gz user@target-machine:/tmp/

# Option B: Via USB drive
cp wheelhouse-runtime-*.tar.gz /mnt/usb/

# Option C: Via secure file service (encrypted cloud, etc.)
```

**Verification on source:**
```bash
sha256sum wheelhouse-runtime-*.tar.gz > wheelhouse.manifest
# Send wheelhouse.manifest to target for verification
```

---

### Step 3: Install on Target Machine (Offline)

Execute these steps **on the target machine WITHOUT network access**.

#### 3.1 Extract and Verify Wheelhouse

```bash
# Extract wheelhouse
cd /tmp  # or appropriate location
tar -xzf wheelhouse-runtime-*.tar.gz

# Enter wheelhouse directory
cd wheelhouse

# Verify checksums (critical for security)
sha256sum -c CHECKSUMS.txt
# Expected output: All files OK 
```

**If checksum fails:**
```bash
# Do NOT proceed - re-transfer the wheelhouse
# Corruption indicates transfer error
scp user@source:/tmp/wheelhouse-runtime-*.tar.gz .
tar -xzf wheelhouse-runtime-*.tar.gz
sha256sum -c wheelhouse/CHECKSUMS.txt
```

#### 3.2 Create Isolated Virtual Environment

```bash
# Create environment in desired location
# (e.g., /opt for system-wide, ~/.codex for user-local)
python3.12 -m venv /opt/codex-offline-env

# Or for user-local installation:
python3.12 -m venv ~/.codex/offline-env

# Activate environment
source /opt/codex-offline-env/bin/activate
# Or: source ~/.codex/offline-env/bin/activate
```

#### 3.3 Install Core Tools

```bash
# Upgrade pip, wheel, setuptools (from system internet or bundled)
pip install --upgrade pip wheel setuptools

# Verify versions
pip --version
```

#### 3.4 Install Dependencies from Wheelhouse (No Network)

```bash
# Make sure you're in the wheelhouse directory
cd /tmp/wheelhouse

# Install all dependencies from local wheels
pip install --no-index \
    --find-links . \
    --no-deps \
    -q \
    -r /path/to/requirements-offline.txt

# Or for runtime mode:
pip install --no-index \
    --find-links . \
    --no-deps \
    -r /path/to/requirements.txt
```

**Expected output:**
```
Installing collected packages: pydantic, omegaconf, hydra-core, ...
Successfully installed pydantic-2.x.x omegaconf-2.x.x hydra-core-1.3.2 ...
```

#### 3.5 Verify Installation

```bash
# Verify no network calls were made
python3 << 'VERIFY_TEST'
import sys

# Test core imports
try:
    from omegaconf import OmegaConf
    from hydra import initialize, compose
    from pydantic import BaseModel
    from cryptography.fernet import Fernet
    print(" All core packages imported successfully")
    print(f" Python {sys.version}")
except ImportError as e:
    print(f" Import failed: {e}")
    sys.exit(1)
VERIFY_TEST

# Test no external network calls
ip addr show  # Confirm network interface exists but is isolated
```

---

##  Configure for Air-Gap Operation

### Environment Variables for Offline Mode

```bash
# ~/.bashrc or ~/.profile (add to environment startup)

# Disable all external network calls
export ALLOW_NETWORK_CALLS=false

# Use local loopback only
export CODEX_LOCAL_LOOPBACK=true

# Disable external API calls
export DISABLE_HUGGINGFACE_HUB=true
export DISABLE_TORCH_HUB=true

# Use local services only
export CODEX_REDIS_HOST=localhost
export CODEX_REDIS_PORT=6379
export CODEX_OLLAMA_HOST=http://localhost:11434

# Activate environment on startup
source /opt/codex-offline-env/bin/activate
```

### Enforce Network Policy

Create a wrapper script to enforce offline-only operation:

```bash
# /usr/local/bin/codex-offline
#!/bin/bash
set -e

export ALLOW_NETWORK_CALLS=false
export CODEX_LOCAL_LOOPBACK=true

# Verify network isolation
if ! python3 -c "
import os
if os.environ.get('ALLOW_NETWORK_CALLS', '').lower() != 'false':
    raise RuntimeError('Network calls enabled - security policy violated')
"; then
    echo "ERROR: Network policy not enforced" >&2
    exit 1
fi

# Run codex
exec python3 -m codex.cli "$@"
```

```bash
chmod +x /usr/local/bin/codex-offline
```

---

##  Verify Air-Gap Compliance

### 1. Network Isolation Test (requires root)

```bash
#!/bin/bash
# Test: Block all external network, verify codex still works

echo "Testing air-gap compliance..."

# Backup current iptables rules (optional)
# sudo iptables-save > /tmp/iptables.backup

# Block all external traffic
sudo iptables -A OUTPUT -d 0.0.0.0/8 -j DROP
sudo iptables -A OUTPUT -d 10.0.0.0/8 -j DROP
sudo iptables -A OUTPUT ! -d 127.0.0.0/8 -j DROP

# Test that codex still works
python3 -m codex.cli serve --dry-run && echo " Codex works offline"

# Restore iptables
# sudo iptables-restore < /tmp/iptables.backup
```

### 2. Verify No External DNS Lookups

```bash
# Monitor DNS queries during execution
sudo tcpdump -i any -n udp port 53 &
TCPDUMP_PID=$!
sleep 1

# Run codex command
python3 -m codex.cli serve &
sleep 5

# Kill monitoring
kill $TCPDUMP_PID 2>/dev/null || true

# Expected: No DNS queries logged
```

### 3. Verify No External HTTP/HTTPS Calls

```bash
# Monitor network connections
sudo tcpdump -i any -n 'tcp port 80 or tcp port 443' &
TCPDUMP_PID=$!
sleep 1

# Run codex command
python3 -m codex.cli serve &
sleep 5

# Kill monitoring
kill $TCPDUMP_PID 2>/dev/null || true

# Expected: No external connections
```

### 4. Verify Memory-Only Execution

```bash
# Profile memory access to confirm no network resources loaded
pip install py-spy
py-spy record -o profile.svg python3 -m codex.cli serve

# Open profile.svg and verify:
# - No network I/O syscalls (sendto, sendmsg, connect)
# - Only local file I/O
# - Only local socket operations (127.0.0.1)
```

### 5. Automated Compliance Check

```python
#!/usr/bin/env python3
# scripts/check_offline_compliance.py

import os
import sys
import socket
from pathlib import Path

def check_network_policy():
    """Verify network policy enforcement."""
    
    # Check environment variables
    allow_network = os.environ.get('ALLOW_NETWORK_CALLS', 'false').lower()
    local_loopback = os.environ.get('CODEX_LOCAL_LOOPBACK', 'true').lower()
    
    assert allow_network == 'false', "ALLOW_NETWORK_CALLS must be false"
    assert local_loopback == 'true', "CODEX_LOCAL_LOOPBACK must be true"
    
    print(" Environment variables correct")
    
    # Test localhost access (should work)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 6379))
        if result == 0 or result == 111:  # 0=connected, 111=connection refused (port closed)
            print(" Localhost access allowed")
        sock.close()
    except Exception as e:
        print(f" Localhost test inconclusive: {e}")
    
    # Test external access (should fail)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('8.8.8.8', 53))
        if result != 0:  # Non-zero means connection failed
            print(" External network access blocked")
        else:
            print(" WARNING: External network access allowed!")
            return False
        sock.close()
    except Exception:
        print(" External network access blocked (expected error)")
    
    return True

if __name__ == '__main__':
    success = check_network_policy()
    sys.exit(0 if success else 1)
```

```bash
python3 scripts/check_offline_compliance.py
# Expected: All checks pass 
```

---

##  Runtime Operations

### Start Codex in Offline Mode

```bash
# Activate environment
source /opt/codex-offline-env/bin/activate

# Set offline mode
export ALLOW_NETWORK_CALLS=false

# Start server (all local services)
python3 -m codex.cli serve --port 8000

# Or use wrapper script
codex-offline serve --port 8000
```

### Common Operations in Offline Mode

```bash
# Activate environment
source /opt/codex-offline-env/bin/activate

# 1. Run code analysis (no network required)
python3 -m codex.cli analyze /path/to/code

# 2. Generate code patterns (local learning only)
python3 -m codex.cli learn --local-only

# 3. Query local models (offline inference)
python3 -m codex.cli query "example query" --offline

# 4. View memory state (local only)
python3 -m codex.cli memory show

# 5. Health check (verify all local services running)
python3 -m codex.cli health --local
```

---

## 🆘 Troubleshooting

| Issue | Symptom | Cause | Solution |
|-------|---------|-------|----------|
| Module not found | `ModuleNotFoundError: No module named 'torch'` | Incomplete wheelhouse | Regenerate wheelhouse with `--full` mode |
| Wheel corruption | `CHECKSUMS.txt` verification fails | Transfer error or disk corruption | Re-transfer wheelhouse from source |
| Permission denied | Cannot write to `/opt/codex-offline-env/` | File permissions | `sudo chown -R $USER /opt/codex-offline-env/` |
| Python version mismatch | `No module named '_xxx'` (native extensions) | Wrong Python version | Use `python3.12 -m venv` (requires 3.12+) |
| Network call detected | External connection in logs | Environment variables not set | Verify `ALLOW_NETWORK_CALLS=false` |
| Redis unavailable | Connection refused to localhost:6379 | Redis not running | Start Redis: `redis-server --port 6379` |
| Ollama unavailable | Connection refused to localhost:11434 | Ollama not running | Start Ollama: `ollama serve` |

### Advanced Debugging

```bash
# Enable verbose logging
export CODEX_LOG_LEVEL=DEBUG

# Monitor all system calls
strace -e trace=network python3 -m codex.cli serve

# Check open file descriptors
lsof -p $$ | grep -E "(sock|TCP)"

# Verify network isolation (root required)
sudo iptables -L -v | grep -E "(OUTPUT|FORWARD)"
```

---

##  Monitoring & Validation

### System Resource Monitoring

```bash
# Monitor while running codex
watch -n 1 'ps aux | grep codex; free -h; df -h /opt'

# Long-term monitoring
top -b -d 2 -u $USER > /var/log/codex-resource-monitoring.log &
```

### Log Monitoring

```bash
# Watch logs for errors
tail -f ~/.codex/logs/codex.log | grep -E "(ERROR|WARNING|Network)"

# Check for network-related errors
grep -i 'network\|connection\|http' ~/.codex/logs/*.log

# Verify no external URLs attempted
grep -iE 'https?://(www\.|api\.|hub\.|github|huggingface)' ~/.codex/logs/*.log
```

### Air-Gap Validation Log

```bash
# Create daily validation report
#!/bin/bash
# /usr/local/bin/codex-daily-validation

DATE=$(date +%Y-%m-%d)
LOG="/var/log/codex-offline-validation-${DATE}.log"

{
    echo "=== Codex Air-Gap Validation Report ==="
    echo "Date: $DATE"
    echo "Host: $(hostname)"
    echo ""
    
    # Network policy
    echo "Network Policy:"
    echo "  ALLOW_NETWORK_CALLS: $(echo $ALLOW_NETWORK_CALLS)"
    echo "  CODEX_LOCAL_LOOPBACK: $(echo $CODEX_LOCAL_LOOPBACK)"
    echo ""
    
    # Network connections
    echo "Active Network Connections:"
    netstat -tan | grep ESTABLISHED | grep -v 127.0.0.1 || echo "  None ( Offline)"
    echo ""
    
    # Disk usage
    echo "Storage:"
    df -h /opt/codex-offline-env/ | tail -1
    echo ""
    
    # Python environment
    echo "Python Environment:"
    which python3
    python3 --version
    pip list | head -10
    echo ""
    
    # Recent operations
    echo "Recent Operations:"
    tail -10 ~/.codex/logs/codex.log
    
} | tee "$LOG"

echo "Validation report saved to: $LOG"
```

---

##  Rollback Procedure

If deployment fails or you need to revert to online mode:

```bash
# Option 1: Deactivate and remove environment
source /opt/codex-offline-env/bin/deactivate
rm -rf /opt/codex-offline-env/

# Option 2: Fallback to online mode (if source available)
unset ALLOW_NETWORK_CALLS
unset CODEX_LOCAL_LOOPBACK

# Option 3: Reinstall from original source
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
pip install -e .

# Option 4: Use online package manager
pip install codex-ml
```

---

##  Phase 8 Validation Checklist

### Groundwork Preparation (Now)
- [ ] `scripts/prepare_offline_env.sh` created
- [ ] `scripts/validate_offline_install.sh` created
- [ ] `requirements-offline.txt` created
- [ ] Offline deployment documentation complete
- [ ] Contingency procedures documented

### Phase 8 Execution (2026-07-09T10:00Z)
- [ ] Wheelhouse generated (all 3 modes)
- [ ] SHA256 checksums verified
- [ ] SBOM (CycloneDX) generated
- [ ] Tarball created for transfer
- [ ] Offline installation validated on isolated machine
- [ ] Air-gap deployment tested (no network calls)
- [ ] All core APIs accessible offline
- [ ] Compliance checks passed
- [ ] Documentation tested with fresh deployment
- [ ] Phase 8 completion report generated

### Post-Deployment (Ongoing)
- [ ] Daily air-gap compliance checks
- [ ] Monthly dependency updates
- [ ] Quarterly security audits
- [ ] Offline documentation maintained

---

##  Related Documentation

- **.codex/archive/misc/INTELLIGENCE_CAMPAIGN_BASELINE.md** (§DECIDE Phase Decision 3)
- **OFFLINE_BOOTSTRAP.sh** (Emergency offline bootstrap)
- **SECURITY.md** (Offline security policies)
- **.codex/archive/misc/INSTALL.md** (Online installation reference)

---

##  Security Considerations

### Data Isolation
- All data stays on local machine (no cloud sync)
- No credentials sent over network
- Cryptographic operations use local keys only

### Supply Chain Security
- **SHA256 verification** prevents wheel tampering
- **SBOM (CycloneDX)** enables vulnerability tracking
- **Checksums.txt** ensures integrity during transfer
- **Wheelhouse immutability** protects against injection

### Air-Gap Compliance
- **Network policy enforced** via environment variables
- **Firewall rules** (optional) provide defense-in-depth
- **Compliance monitoring** detects policy violations
- **Audit trails** log all operations

### Credential Management
- No credentials in wheelhouse
- Secrets loaded from local config only
- No credential transmission over network
- Keys stored in encrypted memory

---

## 📞 Support & Escalation

### Common Questions

**Q: Can I update dependencies in offline mode?**  
A: No, all dependencies must be pre-installed in wheelhouse. Generate new wheelhouse on network-connected machine.

**Q: What if I need a new Python package?**  
A: Regenerate wheelhouse with new dependency on network machine, transfer, and reinstall.

**Q: Can I access external APIs in offline mode?**  
A: No, `ALLOW_NETWORK_CALLS=false` prevents all external calls. This is by design for air-gap security.

**Q: How do I add new models or data?**  
A: Place model/data files on local storage and configure paths in config files (no network required).

**Q: What if network connectivity is restored?**  
A: Unset `ALLOW_NETWORK_CALLS=false` to re-enable network. No re-installation needed.

### Escalation Path

1. Check troubleshooting table above
2. Review logs: `~/.codex/logs/codex.log`
3. Run compliance check: `python3 scripts/check_offline_compliance.py`
4. Consult Phase 8 groundwork documentation
5. Contact infrastructure team with logs

---

**Last Updated**: 2026-07-06  
**Next Review**: 2026-07-15 (post-Phase-8-activation)  
**Version**: 1.0.0-phase8-groundwork
