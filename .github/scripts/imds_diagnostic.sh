#!/usr/bin/env bash
# imds_diagnostic.sh
# Safe IMDS diagnostic and optional remediation script
#
# Usage:
#   ./imds_diagnostic.sh           # read-only diagnostics (default)
#   ./imds_diagnostic.sh --dry-run # diagnostics + simulate remediation
#   sudo ./imds_diagnostic.sh --apply  # perform remediation (requires root)
#   ./imds_diagnostic.sh --help    # show help
#
# Exit codes:
#   0 = diagnostics ran; no remediation required
#   2 = remediation recommended but not applied
#   3 = remediation applied successfully
#   1 = error / unexpected failure
#
set -euo pipefail

SCRIPT_NAME="$(basename \"$0\")"
OUT="diagnostic_results.txt"
IMDS_URL='http://169.254.169.254/metadata/instance?api-version=2021-02-01'
IMDS_HEADER='Metadata: true'
TIMESTAMP="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

DRY_RUN=false
APPLY=false
SHOW_HELP=false

# Helper
log() { printf '%s %s\n' "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')]" "$*"; }
sep() { printf '\n%s\n\n' "------------------------------------------------------------"; }

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [--dry-run] [--apply] [--help]

Default: read-only diagnostics (no changes).
--dry-run: show remediation steps that would be applied (no changes).
--apply: apply safe remediation (requires root).
--help: show this message.

Exit codes:
 0 = diagnostics ran; no remediation required
 2 = remediation recommended but not applied
 3 = remediation applied successfully
 1 = error / unexpected failure
EOF
}

# Parse args
while (( "$#" )); do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;; 
    --apply) APPLY=true; shift ;;
    -h|--help) SHOW_HELP=true; shift ;;  
    *) echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if [ "$SHOW_HELP" = true ]; then
  usage
  exit 0
fi

# Prepare output file
echo "IMDS Diagnostic Results - $TIMESTAMP" > "$OUT"
echo "Branch/Script run by: $(whoami)@$(hostname) on $(date -u)" >> "$OUT"
echo "Args: APPLY=$APPLY DRY_RUN=$DRY_RUN" >> "$OUT"
echo >> "$OUT"

# Diagnostics counters / flags
remediation_needed=false
remediation_actions=()

sep | tee -a "$OUT"
log "1) Checking IMDS connectivity (read-only)..."
{
  if curl -sS -H "$IMDS_HEADER" "$IMDS_URL" >/dev/null 2>&1; then
    log "IMDS: reachable"
    echo "IMDS: reachable" >> "$OUT"
  else
    log "IMDS: unreachable (curl failed)"
    echo "IMDS: unreachable (curl failed)" >> "$OUT"
    remediation_needed=true
    remediation_actions+=("IMDS unreachable (check firewall/NSG/hosts/proxy)")
  fi
} 2>&1 | tee -a "$OUT"

sep | tee -a "$OUT"
log "2) Checking /etc/hosts for mappings to 169.254.169.254"
if grep -Hn "169\.254\.169\.254" /etc/hosts >/dev/null 2>&1; then
  log "/etc/hosts contains mapping(s) to 169.254.169.254"
  grep -n "169\.254\.169\.254" /etc/hosts || true | tee -a "$OUT"
  remediation_needed=true
  remediation_actions+=("Remove /etc/hosts lines mapping 169.254.169.254")
else
  log "No /etc/hosts mapping for IMDS"
  echo "No /etc/hosts mapping for IMDS" >> "$OUT"
fi

sep | tee -a "$OUT"
log "3) Inspecting iptables OUTPUT chain for IMDS rules"
if command -v iptables >/dev/null 2>&1; then
  if sudo iptables -L OUTPUT -n -v 2>/dev/null | grep -E "169\.254\.169\.254" >/dev/null 2>&1; then
    log "iptables has rules referencing 169.254.169.254"
    sudo iptables -L OUTPUT -n -v | sed -n '1,200p' | grep -E "169\.254\.169\.254" | tee -a "$OUT" || true
    remediation_needed=true
    remediation_actions+=("Ensure iptables OUTPUT allows 169.254.169.254 (insert ACCEPT if needed)")
  else
    log "No specific iptables OUTPUT rule found for IMDS"
    echo "No specific iptables OUTPUT rule found for IMDS" >> "$OUT"
  fi
else
  log "iptables not available"
  echo "iptables not available" >> "$OUT"
fi

sep | tee -a "$OUT"
log "4) Inspecting nftables ruleset for IMDS (if nft exists)"
if command -v nft >/dev/null 2>&1; then
  if sudo nft list ruleset 2>/dev/null | grep -E "169\.254\.169\.254" >/dev/null 2>&1; then
    log "nftables contains references to 169.254.169.254"
    sudo nft list ruleset | sed -n '1,200p' | grep -n "169.254.169.254" | tee -a "$OUT" || true
    remediation_needed=true
    remediation_actions+=("Ensure nftables doesn't block 169.254.169.254 (adjust rules)")
  else
    log "No nftables rules referencing IMDS"
    echo "No nftables rules referencing IMDS" >> "$OUT"
  fi
else
  log "nft binary not found"
  echo "nft not present" >> "$OUT"
fi

sep | tee -a "$OUT"
log "5) Checking WALinuxAgent status and logs"
if systemctl status walinuxagent >/dev/null 2>&1; then
  sudo systemctl status walinuxagent --no-pager | sed -n '1,200p' | tee -a "$OUT" || true
  echo >> "$OUT"
  echo "Recent WALinuxAgent journal entries (last 200 lines):" >> "$OUT"
  sudo journalctl -u walinuxagent -n 200 --no-pager | tail -n 200 | tee -a "$OUT" || true
else
  log "walinuxagent service not present or not running"
  echo "walinuxagent service not present or not running" >> "$OUT"
fi

sep | tee -a "$OUT"
log "6) Detecting redirection signatures in provided blocked logs (optional check)"
# Look for local indications (this is a safe check only if blocked.jsonl available)
if [ -f blocked.jsonl ]; then
  if grep -E '"originalIp":"169\.254\.169\.254".*"ip":"127\.0\.0.1"' blocked.jsonl >/dev/null 2>&1; then
    log "Blocked logs show redirection of 169.254.169.254 -> 127.0.0.1"
    echo "Blocked logs show redirection of 169.254.169.254 -> 127.0.0.1" >> "$OUT"
    remediation_needed=true
    remediation_actions+=("Investigate host-level proxy/redirect mapping 169.254.169.254 -> 127.0.0.1")
  else
    log "No direct redirection signatures found in blocked.jsonl (or file absent)"
    echo "No direct redirection signatures found in blocked.jsonl (or file absent)" >> "$OUT"
  fi
else
  echo "blocked.jsonl not present locally; skipped redirection signature check" >> "$OUT"
f  
sep | tee -a "$OUT"
log "Summary of remediation recommendations:"
if [ "$remediation_needed" = true ]; then
  echo "REMEDIATION RECOMMENDED" | tee -a "$OUT"
  for a in "${remediation_actions[@]}"; do
    echo "- $a" | tee -a "$OUT"
  done
else
  echo "No remediation required based on checks." | tee -a "$OUT"
fi

# If APPLY requested, perform safe remediation
if [ "$APPLY" = true ]; then
  # Must be run as root for remediation
  if [ "$(id -u)" -ne 0 ]; then
    log "Remediation requested but not running as root. Exiting with error."
    echo "ERROR: remediation requires root. Re-run with sudo or as root." | tee -a "$OUT"
    exit 1
  fi

  applied_any=false

  # Remove /etc/hosts mappings (backup)
  if grep -q "169\.254\.169\.254" /etc/hosts 2>/dev/null; then
    cp /etc/hosts /etc/hosts.bak."$TIMESTAMP" || true
    sed -i '/169\.254\.169\.254/d' /etc/hosts || true
    log "Removed /etc/hosts mapping(s) for 169.254.169.254 (backup created)"
    echo "/etc/hosts mapping removed (backup: /etc/hosts.bak.$TIMESTAMP)" >> "$OUT"
    applied_any=true
  fi

  # Add iptables rule if iptables exists
  if command -v iptables >/dev/null 2>&1; then
    if ! iptables -C OUTPUT -d 169.254.169.254 -j ACCEPT >/dev/null 2>&1; then
      iptables -I OUTPUT -d 169.254.169.254 -j ACCEPT || true
      log "Inserted iptables OUTPUT ACCEPT for 169.254.169.254"
      echo "Inserted iptables OUTPUT ACCEPT for 169.254.169.254" >> "$OUT"
      applied_any=true
    else
      log "iptables ACCEPT rule already present"
      echo "iptables ACCEPT rule already present" >> "$OUT"
    fi
  fi

  # Restart WALinuxAgent
  if systemctl status walinuxagent >/dev/null 2>&1; then
    systemctl restart walinuxagent || true
    log "walinuxagent restarted"
    echo "walinuxagent restarted" >> "$OUT"
    applied_any=true
  fi

  if [ "$applied_any" = true ]; then
    log "Remediation actions applied"
    echo "Remediation actions applied" >> "$OUT"
    exit 3
  else
    log "No remediation actions were necessary or applicable"
    echo "No remediation actions were necessary or applicable" >> "$OUT"
    exit 0
  fi
else
  # Not applying remediation: exit with code 2 if remediation recommended
  if [ "$remediation_needed" = true ]; then
    log "Remediation recommended but not applied (exit code 2)"
    exit 2
  else
    log "Diagnostics complete; no remediation required (exit code 0)"
    exit 0
  fi
fi
