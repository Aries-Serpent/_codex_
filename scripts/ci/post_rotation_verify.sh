#!/usr/bin/env bash
# post_rotation_verify.sh — run after every token rotation to confirm alignment
#
# Usage:
#   CODEX_MASTER_KEY=<new_value> ./scripts/ci/post_rotation_verify.sh
#
# Or if already exported in your shell:
#   ./scripts/ci/post_rotation_verify.sh
#
# Checks performed:
#   1. CODEX_MASTER_KEY → Variables API (HTTP 200)
#   2. CODEX_MASTER_KEY OAuth scopes (repo + workflow required)
#   3. Repo variables scan for embedded token values (ghp_/github_pat_/ghs_/gho_)
#   4. .codex/agent_context.json — no live token fields
#   5. .codex/agent_auth_session.json — no live token fields
#   6. detect-secrets scan (if installed)
#   7. Reminder to update CODEX_MASTER_KEY_LAST_VERIFIED variable
#
# Reference: docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md §9.6

set -euo pipefail

# ── colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "   ${GREEN}✅ $*${NC}"; }
fail() { echo -e "   ${RED}❌ $*${NC}"; FAILURES=$((FAILURES+1)); }
warn() { echo -e "   ${YELLOW}⚠️  $*${NC}"; WARNINGS=$((WARNINGS+1)); }

FAILURES=0
WARNINGS=0
REPO="Aries-Serpent/_codex_"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   Post-Rotation Alignment Verification                  ║"
echo "║   docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md §9 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── 1. Variables API access ───────────────────────────────────────────────────
echo "1. Testing CODEX_MASTER_KEY → Variables API..."
if [ -z "${CODEX_MASTER_KEY:-}" ]; then
    warn "CODEX_MASTER_KEY not set in environment — skipping API checks"
else
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "Authorization: Bearer $CODEX_MASTER_KEY" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "https://api.github.com/repos/${REPO}/actions/variables")
    if [ "$STATUS" = "200" ]; then
        ok "Variables API: HTTP 200"
    else
        fail "Variables API: HTTP $STATUS  (expected 200 — key may be expired/wrong scope)"
    fi

    # ── 2. Scope check ────────────────────────────────────────────────────────
    echo "2. Checking CODEX_MASTER_KEY scopes..."
    SCOPES_HEADER=$(curl -sI \
      -H "Authorization: Bearer $CODEX_MASTER_KEY" \
      https://api.github.com/user | grep -i "x-oauth-scopes:" | tr -d '\r' || true)

    if [ -z "$SCOPES_HEADER" ]; then
        warn "Could not read x-oauth-scopes header — may be fine-grained PAT (scopes work differently)"
    else
        SCOPE_VALUE=$(echo "$SCOPES_HEADER" | sed 's/x-oauth-scopes://I' | xargs)
        echo "   Scopes: $SCOPE_VALUE"
        echo "$SCOPE_VALUE" | grep -qi "repo"     && ok "repo scope: present"     || fail "repo scope: MISSING"
        echo "$SCOPE_VALUE" | grep -qi "workflow"  && ok "workflow scope: present"  || fail "workflow scope: MISSING"
        echo "$SCOPE_VALUE" | grep -qi "security_events" \
            && ok "security_events scope: present (CodeQL access enabled)" \
            || warn "security_events scope: absent — CodeQL alert fetching requires this scope (see §3.6)"
    fi

    # ── 3. Repo variables scan ────────────────────────────────────────────────
    echo "3. Scanning repo variables for embedded token values..."
    VARS=$(curl -s \
      -H "Authorization: Bearer $CODEX_MASTER_KEY" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "https://api.github.com/repos/${REPO}/actions/variables?per_page=100" \
      | python3 -c "
import json, sys
data = json.load(sys.stdin)
for v in data.get('variables', []):
    val = v.get('value','')
    if any(val.startswith(p) for p in ['ghp_','github_pat_','ghs_','gho_','v1.']):
        print(f\"STALE_TOKEN_VAR: {v['name']}  ← token-like value detected (value redacted)\")
" 2>/dev/null || true)
    if [ -z "$VARS" ]; then
        ok "No embedded token values in repo variables"
    else
        while IFS= read -r line; do
            fail "$line  ← UPDATE THIS VARIABLE IMMEDIATELY"
        done <<< "$VARS"
    fi
fi

# ── 4. agent_context.json check ───────────────────────────────────────────────
echo "4. Checking .codex/agent_context.json for live token fields..."
if [ -f ".codex/agent_context.json" ]; then
    LEAKED=$(python3 -c "
import json, sys
try:
    d = json.load(open('.codex/agent_context.json'))
    tok_keys = [k for k,v in d.items()
                if isinstance(v,str) and any(v.startswith(p)
                   for p in ['ghp_','github_pat_','ghs_','gho_'])]
    if tok_keys:
        print('LEAKED:' + ','.join(tok_keys))
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null || true)
    if echo "$LEAKED" | grep -q "LEAKED:"; then
        KEYS=$(echo "$LEAKED" | sed 's/LEAKED://')
        fail "Token-like values found in agent_context.json keys: $KEYS"
        echo "      Fix: remove these keys or replace their values with placeholder strings"
    elif echo "$LEAKED" | grep -q "ERROR:"; then
        warn "Could not parse .codex/agent_context.json: $LEAKED"
    else
        ok "No token values in .codex/agent_context.json"
    fi
else
    warn ".codex/agent_context.json not found — skipping"
fi

# ── 5. agent_auth_session.json check ─────────────────────────────────────────
echo "5. Checking .codex/agent_auth_session.json for live token fields..."
if [ -f ".codex/agent_auth_session.json" ]; then
    SESSION_CHECK=$(python3 -c "
import json, sys
try:
    d = json.load(open('.codex/agent_auth_session.json'))
    tok_keys = [k for k,v in d.items()
                if isinstance(v,str) and any(v.startswith(p)
                   for p in ['ghp_','github_pat_','ghs_','gho_'])]
    if tok_keys:
        print('LEAKED:' + ','.join(tok_keys))
    else:
        print('OK')
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null || true)
    if echo "$SESSION_CHECK" | grep -q "LEAKED:"; then
        KEYS=$(echo "$SESSION_CHECK" | sed 's/LEAKED://')
        fail "Token-like values found in agent_auth_session.json keys: $KEYS"
        echo "      Fix: python scripts/ci/write_agent_auth_session.py"
    elif echo "$SESSION_CHECK" | grep -q "ERROR:"; then
        warn "Could not parse agent_auth_session.json: $SESSION_CHECK"
    else
        ok "No token values in .codex/agent_auth_session.json"
    fi
else
    warn ".codex/agent_auth_session.json not found — skipping"
fi

# ── 6. detect-secrets ─────────────────────────────────────────────────────────
echo "6. Running detect-secrets scan..."
if command -v detect-secrets &>/dev/null; then
    if detect-secrets scan --baseline .secrets.baseline > /dev/null 2>&1; then
        ok "detect-secrets: no new secrets detected"
    else
        warn "detect-secrets found new high-entropy strings — run:"
        echo "      python scripts/ci/sync_tracked_files.py --fix"
        echo "      git add .secrets.baseline && git commit -m 'fix(ci): update secrets baseline after token rotation'"
        WARNINGS=$((WARNINGS+1))
    fi
else
    warn "detect-secrets not installed — skipping (install: pip install detect-secrets)"
fi

# ── 7. Reminder ───────────────────────────────────────────────────────────────
echo "7. Post-rotation variable update reminder..."
echo "   Run this command to timestamp the rotation:"
echo ""
echo "   GH_TOKEN=\$CODEX_MASTER_KEY gh api \\"
echo "     --method PATCH \\"
echo "     /repos/${REPO}/actions/variables/CODEX_MASTER_KEY_LAST_VERIFIED \\"
echo "     -f name=CODEX_MASTER_KEY_LAST_VERIFIED \\"
echo "     -f value=\"\$(date -u +%Y-%m-%dT%H:%M:%SZ):ok\""
echo ""
warn "Remember to run the above command after this verification passes"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
if [ "$FAILURES" -eq 0 ] && [ "$WARNINGS" -le 2 ]; then
    echo -e "${GREEN}✅ Verification PASSED — $FAILURES failures, $WARNINGS warnings${NC}"
    echo "   Token rotation is complete and aligned."
elif [ "$FAILURES" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Verification passed with warnings — $FAILURES failures, $WARNINGS warnings${NC}"
    echo "   Address warnings before considering rotation complete."
else
    echo -e "${RED}❌ Verification FAILED — $FAILURES failures, $WARNINGS warnings${NC}"
    echo "   Fix all ❌ items before proceeding."
    exit 1
fi
echo "══════════════════════════════════════════════════════════"
echo ""
echo "Reference: docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md §9"
