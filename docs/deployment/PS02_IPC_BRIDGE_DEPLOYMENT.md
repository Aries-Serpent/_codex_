# PS-02: IPC Bridge Hardening Deployment Guide

## Prerequisites
- Linux OS (named pipes/Unix sockets)
- Python 3.9+
- CODEX_BRIDGE_TOKEN environment variable

## Deployment Steps

### Step 1: Generate Authentication Token
```bash
export CODEX_BRIDGE_TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "CODEX_BRIDGE_TOKEN=$CODEX_BRIDGE_TOKEN" >> .env
```

### Step 2: Verify Bridge Implementation
```bash
python3 -c "from src.bridge_manager import SecureBridge; print('✅ Bridge available')"
```

### Step 3: Test Bridge Security
```bash
pytest tests/integration/test_bridge_security.py -v
```

### Step 4: Deploy Bridge Service
```python
from src.bridge_manager import SecureBridge, BridgeMode

bridge = SecureBridge(
    mode=BridgeMode.UNIX_SOCKET,
    socket_path="/tmp/cognitive_bridge.sock",
    auth_token=os.getenv("CODEX_BRIDGE_TOKEN")
)
```

### Step 5: Verify Permissions
```bash
ls -la /tmp/cognitive_bridge.sock
# Should show: srw------- (0600)
```

## Rollback Procedure
```bash
# Stop bridge service
pkill -f "bridge_manager"

# Remove socket file
rm -f /tmp/cognitive_bridge.sock

# Revert to legacy TCP (emergency only)
git checkout HEAD~5 -- src/bridge_manager.py
```

## Verification
- [ ] Socket created with 0600 permissions
- [ ] Authentication working
- [ ] Audit trail logging
- [ ] Latency <10ms

**Status:** ✅ Production Ready
**Last Updated:** 2026-01-09
