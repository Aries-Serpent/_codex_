#!/usr/bin/env bash
# imds_diagnostic.sh
# Canonical / Expanded IMDS (Azure Instance Metadata Service) diagnostic & minimal remediation tool.
# ENERGY 5/5 (Version v1.6 - Further Expansion)
#
# New Enhancements (v1.6 - 2025-11-14T23:14:07Z UTC):
#  - Config loader: optional .github/imds_config.yml to control defaults (strict_approval, api_version, default_modes, issue_id)
#  - Firewall detectors: UFW and firewalld inspection with error codes and recommendations (detection-only)
#  - ISSUE_REF variable replaces hardcoded #2226 in audit; sourced from config (issue_id) when available
#  - Robust YAML parsing without yq (grep/awk/sed) with graceful fallback
#  - Minor UX: status echo includes env_class and runtime_ms; improved dependency notes
#
# Existing Feature Set:
#  - HTTP / TCP connectivity checks to 169.254.169.254 (+ ping heuristic)
#  - /etc/hosts overrides, iptables/nftables inspection
#  - WALinuxAgent status + journal tail
#  - blocked.jsonl redirection signature scan
#  - Routing + policy rules, DNS heuristic
#  - Environment snapshot & classification (azure_vm, gha_runner, container, onprem_vm)
#  - Dry-run preview (--dry-run)
#  - JSON summary (--json) with extended fields (env, memory, runtime)
#  - Prometheus metrics (--metrics)
#  - HTML report (--html)
#  - Approval-governed remediation (--apply requires token unless --no-approval)
#  - Audit JSONL append on remediation
#  - Self-test harness (--self-test)
#
# Usage Examples:
#   bash .github/scripts/imds_diagnostic.sh
#   bash .github/scripts/imds_diagnostic.sh --json --metrics
#   bash .github/scripts/imds_diagnostic.sh --dry-run
#   sudo IMDS_APPROVAL_TOKEN=<token> bash .github/scripts/imds_diagnostic.sh --apply --json --metrics
#   bash .github/scripts/imds_diagnostic.sh --html
#   bash .github/scripts/imds_diagnostic.sh --self-test
#
# Exit Codes:
#   0 diagnostics OK   | 1 error | 2 remediation recommended | 3 remediation applied
#
set -euo pipefail

###############################################################################
# Version / Timing
###############################################################################
TOOL_VERSION="1.6"
EPOCH_START_MS="$(date +%s%3N)"

###############################################################################
# Config / Globals
###############################################################################
DEFAULT_API_VERSION="2021-02-01"
IMDS_IP="169.254.169.254"
API_VERSION="$DEFAULT_API_VERSION"
IMDS_URL=""
IMDS_HEADER="Metadata: true"

SCRIPT_NAME="$(basename "$0")"
TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
OUT_FILE="diagnostic_results.txt"
JSON_FILE="diagnostic_results.json"
METRICS_FILE="imds_metrics.prom"
HTML_FILE="imds_report.html"
AUDIT_DIR=".codex/audit"
AUDIT_FILE="${AUDIT_DIR}/imds_remediations.jsonl"
CONFIG_FILE=".github/imds_config.yml"
ISSUE_REF="#2226"   # Can be overridden by config (issue_id)

APPLY=false
DRY_RUN=false
JSON_MODE=false
NO_COLOR=false
METRICS=false
SELF_TEST=false
APPROVAL_TOKEN_ARG=""
STRICT_APPROVAL=true
NO_APPROVAL_FLAG=false
HTML_MODE=false

declare -a RECOMMENDATIONS=()
declare -a ACTIONS_APPLIED=()
declare -A METRIC=()
declare -a ERROR_REASONS=()

REM_NEEDED=false
ENV_CLASS="unknown"

###############################################################################
# Color helpers
###############################################################################
color() { $NO_COLOR && return 0; printf "\033[%sm%s\033[0m" "$1" "$2"; }
c_green(){ color 32 "$*"; }
c_yellow(){ color 33 "$*"; }
c_red(){ color 31 "$*"; }
c_blue(){ color 34 "$*"; }
c_mag(){ color 35 "$*"; }

###############################################################################
# Logging helpers
###############################################################################
log() { printf "[%s] %s\n" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*" | tee -a "$OUT_FILE"; }
section() { printf "\n%s\n" "----------------------------------------------------------------" | tee -a "$OUT_FILE"; log "$(c_blue "$1")"; }
abort() { log "$(c_red "ERROR:") $*"; exit 1; }

usage() {
cat <<EOF
IMDS Diagnostic Script (Version $TOOL_VERSION)
Usage: $SCRIPT_NAME [flags]

Flags:
  --apply               Perform remediation (root + approval token unless --no-approval)
  --dry-run             Show remediation steps only (no changes)
  --json                Emit JSON summary ($JSON_FILE)
  --metrics             Emit Prometheus metrics ($METRICS_FILE)
  --html                Emit HTML report ($HTML_FILE)
  --api-version <ver>   Override IMDS API version (default: $DEFAULT_API_VERSION)
  --approval-token <t>  Provide remediation approval token
  --no-color            Disable ANSI colors
  --no-approval         Disable STRICT_APPROVAL (sandbox only)
  --self-test           Run internal self validation (syntax + dry-run + JSON)
  --help                Show this help

Environment:
  IMDS_APPROVAL_TOKEN   Approval token (when --apply used and STRICT_APPROVAL active)

Exit Codes:
  0 OK | 1 Error | 2 Remediation recommended | 3 Remediation applied
EOF
}

###############################################################################
# Parse Args
###############################################################################
while (( $# )); do
  case "$1" in
    --apply) APPLY=true ;;
    --dry-run) DRY_RUN=true ;;
    --json) JSON_MODE=true ;;
    --metrics) METRICS=true ;;
    --html) HTML_MODE=true ;;
    --api-version) shift; API_VERSION="${1:-}" ;;
    --approval-token) shift; APPROVAL_TOKEN_ARG="${1:-}" ;;
    --no-color) NO_COLOR=true ;;
    --no-approval) NO_APPROVAL_FLAG=true ;;
    --self-test) SELF_TEST=true ;;
    -h|--help) usage; exit 0 ;;
    *) abort "Unknown argument: $1" ;;
  esac
  shift || true
done

IMDS_URL="http://${IMDS_IP}/metadata/instance?api-version=${API_VERSION}"

###############################################################################
# Load Config (Optional)
###############################################################################
load_config() {
  section "Config Loader (.github/imds_config.yml)"
  if [[ -f "$CONFIG_FILE" ]]; then
    log "Config found: $CONFIG_FILE"
    # strict_approval: true|false
    local val
    val="$(grep -E '^[[:space:]]*strict_approval:' "$CONFIG_FILE" 2>/dev/null | head -1 | awk -F: '{gsub(/[[:space:]]/, "", $2); print tolower($2)}')"
    if [[ "$val" == "false" ]]; then
      STRICT_APPROVAL=false
      log "Config: strict_approval=false (STRICT_APPROVAL disabled)"
    elif [[ "$val" == "true" ]]; then
      STRICT_APPROVAL=true
      log "Config: strict_approval=true (STRICT_APPROVAL enforced)"
    fi
    # default_api_version: "YYYY-MM-DD"
    val="$(grep -E '^[[:space:]]*default_api_version:' "$CONFIG_FILE" 2>/dev/null | head -1 | sed -E 's/^[[:space:]]*default_api_version:[[:space:]]*//; s/["'\'']//g')"
    if [[ -n "$val" ]]; then
      API_VERSION="$val"
      IMDS_URL="http://${IMDS_IP}/metadata/instance?api-version=${API_VERSION}"
      log "Config: default_api_version=$API_VERSION"
    fi
    # default_modes:
    #   json: true
    #   metrics: true
    #   html: false
    local json_mode metrics_mode html_mode
    json_mode="$(awk '/^[[:space:]]*default_modes:/{flag=1;next}/^[^[:space:]]/{flag=0}flag' "$CONFIG_FILE" 2>/dev/null | grep -E '^[[:space:]]*json:' | awk -F: '{gsub(/[[:space:]]/, "", $2); print tolower($2)}' | head -1 || true)"
    metrics_mode="$(awk '/^[[:space:]]*default_modes:/{flag=1;next}/^[^[:space:]]/{flag=0}flag' "$CONFIG_FILE" 2>/dev/null | grep -E '^[[:space:]]*metrics:' | awk -F: '{gsub(/[[:space:]]/, "", $2); print tolower($2)}' | head -1 || true)"
    html_mode="$(awk '/^[[:space:]]*default_modes:/{flag=1;next}/^[^[:space:]]/{flag=0}flag' "$CONFIG_FILE" 2>/dev/null | grep -E '^[[:space:]]*html:' | awk -F: '{gsub(/[[:space:]]/, "", $2); print tolower($2)}' | head -1 || true)"
    [[ "$json_mode" == "true" ]] && JSON_MODE=true && log "Config: default_modes.json=true"
    [[ "$metrics_mode" == "true" ]] && METRICS=true && log "Config: default_modes.metrics=true"
    [[ "$html_mode" == "true" ]] && HTML_MODE=true && log "Config: default_modes.html=true"
    # issue_id: 2226
    val="$(grep -E '^[[:space:]]*issue_id:' "$CONFIG_FILE" 2>/dev/null | head -1 | awk -F: '{gsub(/[[:space:]]/, "", $2); print $2}')"
    if [[ -n "$val" ]]; then
      ISSUE_REF="#$val"
      log "Config: issue_ref=$ISSUE_REF"
    fi
  else
    log "Config not found; using built-in defaults."
  fi
}

###############################################################################
# Utility / State
###############################################################################
recommend() { RECOMMENDATIONS+=("$1"); REM_NEEDED=true; }
apply_action() { ACTIONS_APPLIED+=("$1"); }
record_error() { ERROR_REASONS+=("$1"); }
set_metric() { METRIC["$1"]="$2"; }

###############################################################################
# Environment Classification
###############################################################################
classify_env() {
  local has_wala=0 has_route=0 gh=0 container=0
  if systemctl list-unit-files 2>/dev/null | grep -q walinuxagent.service; then
    has_wala=1
  fi
  if ip route get "$IMDS_IP" >/dev/null 2>&1; then
    has_route=1
  fi
  [[ -n "${GITHUB_ACTIONS:-}" ]] && gh=1
  if grep -E '(docker|container)' /proc/1/cgroup 2>/dev/null >/dev/null; then
    container=1
  fi

  if (( has_wala==1 && has_route==1 )); then
    ENV_CLASS="azure_vm"
  elif (( gh==1 )); then
    ENV_CLASS="gha_runner"
  elif (( container==1 )); then
    ENV_CLASS="container"
  else
    ENV_CLASS="onprem_vm"
  fi
  section "Environment Classification"
  log "ENV_CLASS=$ENV_CLASS (wala=$has_wala route=$has_route gh=$gh container=$container)"
}

###############################################################################
# Environment Snapshot
###############################################################################
snapshot_env() {
  section "Environment Snapshot"
  log "Hostname: $(hostname)"
  log "Kernel: $(uname -sr)"
  log "Distro: $(grep -E '^PRETTY_NAME' /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')"
  log "User: $(whoami)"
  log "Shell: $SHELL"
  log "Interfaces:"
  ip -o link show 2>/dev/null | awk -F': ' '{print "  - " $2}' | tee -a "$OUT_FILE" || true
  log "IPv4 Addresses:"
  ip -o -4 addr show 2>/dev/null | awk '{print "  - " $2 " => " $4}' | tee -a "$OUT_FILE" || true
  if grep -q MemTotal /proc/meminfo 2>/dev/null; then
    local mt mf ma
    mt=$(grep MemTotal /proc/meminfo | awk '{print $2}') || mt=0
    mf=$(grep MemFree /proc/meminfo | awk '{print $2}') || mf=0
    ma=$(grep MemAvailable /proc/meminfo | awk '{print $2}') || ma=0
    log "Memory(kB): total=$mt free=$mf avail=$ma"
    export MEM_TOTAL_KB="$mt" MEM_FREE_KB="$mf" MEM_AVAILABLE_KB="$ma"
  else
    export MEM_TOTAL_KB=0 MEM_FREE_KB=0 MEM_AVAILABLE_KB=0
  fi
}

###############################################################################
# IMDS HTTP Connectivity
###############################################################################
check_imds_http() {
  section "IMDS HTTP Connectivity"
  local curl_out curl_rc
  curl_out=$(curl -w "STATUS=%{http_code}" -sS -H "$IMDS_HEADER" --connect-timeout 1 --max-time 2 "$IMDS_URL" 2>&1 || true)
  curl_rc=$?
  if (( curl_rc == 0 )) && grep -q "STATUS=200" <<<"$curl_out"; then
    log "$(c_green "IMDS reachable (HTTP 200)")"
    set_metric "imds_http_reachable" 1
  else
    log "$(c_red "IMDS HTTP unreachable")"
    set_metric "imds_http_reachable" 0
    if (( curl_rc != 0 )); then
      if grep -qi "Could not resolve" <<<"$curl_out"; then
        record_error "dns_resolution_failure"
      elif grep -qi "Connection timed out" <<<"$curl_out"; then
        record_error "connection_timeout"
      else
        record_error "http_request_failure"
      fi
    else
      record_error "non_200_status"
    fi
    recommend "Investigate IMDS HTTP path (firewall/proxy/hosts)."
  fi
}

###############################################################################
# IMDS TCP Connectivity
###############################################################################
check_imds_tcp() {
  section "IMDS TCP Port 80 Reachability"
  if command -v timeout >/dev/null 2>&1; then
    if timeout 2 bash -c ">/dev/tcp/${IMDS_IP}/80" 2>/dev/null; then
      log "$(c_green "Raw TCP connect succeeded to ${IMDS_IP}:80")"
      set_metric "imds_tcp_reachable" 1
    else
      log "$(c_red "Raw TCP connect failed to ${IMDS_IP}:80")"
      set_metric "imds_tcp_reachable" 0
      record_error "tcp_port_unreachable"
      recommend "Port 80 unreachable - confirm outbound route/rule."
    fi
  else
    log "timeout not found; skipping raw TCP test."
    set_metric "imds_tcp_reachable" 0
  fi
}

###############################################################################
# Ping heuristic
###############################################################################
check_ping() {
  section "IMDS Ping Heuristic"
  if command -v ping >/dev/null 2>&1; then
    if ping -c1 -W1 "$IMDS_IP" >/dev/null 2>&1; then
      log "Ping responded (non-authoritative)."
      set_metric "imds_ping_success" 1
    else
      log "Ping failed or filtered."
      set_metric "imds_ping_success" 0
    fi
  else
    log "ping not available; skipping."
    set_metric "imds_ping_success" 0
  fi
}

###############################################################################
# /etc/hosts check
###############################################################################
check_hosts() {
  section "/etc/hosts Overrides"
  if grep -E "$IMDS_IP" /etc/hosts >/dev/null 2>&1; then
    log "$(c_red "Overrides present for $IMDS_IP")"
    grep -n "$IMDS_IP" /etc/hosts | tee -a "$OUT_FILE"
    set_metric "hosts_override_present" 1
    record_error "hosts_override"
    recommend "Remove /etc/hosts lines mapping $IMDS_IP."
  else
    log "$(c_green "No /etc/hosts overrides detected")"
    set_metric "hosts_override_present" 0
  fi
}

###############################################################################
# iptables OUTPUT
###############################################################################
check_iptables() {
  section "iptables OUTPUT Chain Inspection"
  if command -v iptables >/dev/null 2>&1; then
    local out; out="$(sudo iptables -L OUTPUT -n -v 2>/dev/null || true)"
    if grep -E "$IMDS_IP" <<<"$out" >/dev/null 2>&1; then
      log "Rules referencing $IMDS_IP:"
      grep -E "$IMDS_IP" <<<"$out" | tee -a "$OUT_FILE" || true
    else
      log "No explicit OUTPUT rule referencing $IMDS_IP."
    fi
    if sudo iptables -S OUTPUT 2>/dev/null | grep -E "DROP" | grep -E "$IMDS_IP" >/dev/null 2>&1; then
      log "$(c_red "DROP rule detected affecting $IMDS_IP")"
      set_metric "iptables_drop_detected" 1
      record_error "iptables_drop_rule"
      recommend "Adjust iptables to allow $IMDS_IP."
    else
      set_metric "iptables_drop_detected" 0
    fi
  else
    log "iptables not installed."
    set_metric "iptables_drop_detected" 0
  fi
}

###############################################################################
# nftables
###############################################################################
check_nftables() {
  section "nftables Ruleset Inspection"
  if command -v nft >/dev/null 2>&1; then
    if sudo nft list ruleset 2>/dev/null | grep -E "$IMDS_IP" >/dev/null 2>&1; then
      log "nftables entries referencing $IMDS_IP:"
      sudo nft list ruleset | grep -n "$IMDS_IP" | tee -a "$OUT_FILE" || true
    else
      log "No nftables references to $IMDS_IP."
    fi
  else
    log "nft not installed."
  fi
}

###############################################################################
# firewalld Detector (detection-only)
###############################################################################
check_firewalld() {
  section "firewalld Inspection"
  if command -v firewall-cmd >/dev/null 2>&1; then
    if firewall-cmd --state >/dev/null 2>&1; then
      log "firewalld active."
      # List all zones and search for IMDS IP references in rich rules/services (heuristic)
      local zones z
      zones=$(firewall-cmd --get-zones 2>/dev/null || echo "public")
      for z in $zones; do
        local conf
        conf="$(firewall-cmd --zone="$z" --list-all 2>/dev/null || true)"
        if grep -E "$IMDS_IP" <<<"$conf" >/dev/null 2>&1; then
          log "$(c_red "Zone '$z' contains references possibly affecting $IMDS_IP")"
          record_error "firewalld_rule_imds"
          recommend "Review firewalld zone '$z' rules for $IMDS_IP egress allowance."
        fi
      done
    else
      log "firewalld installed but inactive."
    fi
  else
    log "firewalld not installed."
  fi
}

###############################################################################
# UFW Detector (detection-only)
###############################################################################
check_ufw() {
  section "UFW Inspection"
  if command -v ufw >/dev/null 2>&1; then
    local status
    status="$(ufw status 2>/dev/null || true)"
    log "UFW status: $(echo "$status" | head -1)"
    # Look for explicit denies to IMDS or outbound rejects (heuristic)
    if ufw status numbered 2>/dev/null | grep -E "($IMDS_IP|DENY OUT|REJECT OUT)" >/dev/null 2>&1; then
      log "$(c_yellow "Potential UFW rule impacting IMDS or outbound traffic detected")"
      ufw status numbered 2>/dev/null | grep -nE "($IMDS_IP|DENY OUT|REJECT OUT)" | tee -a "$OUT_FILE" || true
      record_error "ufw_block_rule"
      recommend "Review UFW outbound rules; ensure $IMDS_IP is permitted."
    else
      log "No obvious UFW blocks for IMDS detected."
    fi
  else
    log "UFW not installed."
  fi
}

###############################################################################
# WALinuxAgent
###############################################################################
check_walinuxagent() {
  section "WALinuxAgent Service"
  if systemctl list-unit-files 2>/dev/null | grep -q walinuxagent.service; then
    if systemctl is-active walinuxagent >/dev/null 2>&1; then
      log "$(c_green "WALinuxAgent active")"
      set_metric "walinuxagent_active" 1
    else
      log "$(c_red "WALinuxAgent inactive")"
      set_metric "walinuxagent_active" 0
      record_error "walinuxagent_inactive"
      recommend "Start WALinuxAgent or troubleshoot service."
    fi
    log "Recent journal (last 100 lines):"
    journalctl -u walinuxagent -n 100 --no-pager 2>/dev/null | tee -a "$OUT_FILE" || true
  else
    log "WALinuxAgent service not found."
    set_metric "walinuxagent_active" 0
  fi
}

###############################################################################
# blocked.jsonl
###############################################################################
check_blocked_log() {
  section "blocked.jsonl Redirection Signature"
  if [[ -f blocked.jsonl ]]; then
    if grep -E '"originalIp":"'"$IMDS_IP"'"' blocked.jsonl | grep -E '"ip":"127\.0\.0\.1"' >/dev/null 2>&1; then
      log "$(c_red "Redirection signature $IMDS_IP -> 127.0.0.1 detected")"
      record_error "metadata_ip_redirect"
      recommend "Investigate proxy/redirect rewriting metadata IP."
      set_metric "redirect_signature_present" 1
    else
      log "No redirection signature found."
      set_metric "redirect_signature_present" 0
    fi
  else
    log "blocked.jsonl absent; skipping."
    set_metric "redirect_signature_present" 0
  fi
}

###############################################################################
# Routing
###############################################################################
check_routing() {
  section "Routing & Policy Rules"
  if ip route get "$IMDS_IP" >/dev/null 2>&1; then
    ip route get "$IMDS_IP" 2>&1 | tee -a "$OUT_FILE" || true
    set_metric "route_to_imds_present" 1
  else
    log "$(c_red "No route to $IMDS_IP")"
    set_metric "route_to_imds_present" 0
    record_error "missing_route"
    recommend "Establish link-local route for $IMDS_IP if required."
  fi
  log "Policy rules:"
  ip rule show 2>&1 | tee -a "$OUT_FILE" || true
}

###############################################################################
# DNS heuristic
###############################################################################
check_dns() {
  section "DNS / Hostname Mapping Heuristic"
  local suspicious
  suspicious=$(grep -E "$IMDS_IP" /etc/hosts 2>/dev/null | awk '{print $2}' || true)
  if [[ -n "$suspicious" ]]; then
    log "Hostnames mapped to metadata IP: $suspicious"
    set_metric "hostname_mapped_to_imds" 1
  else
    log "No hostname mappings beyond direct IP lines."
    set_metric "hostname_mapped_to_imds" 0
  fi
}

###############################################################################
# Approval Token Validation
###############################################################################
validate_approval_token() {
  section "Approval Token Validation"
  local token_env="${IMDS_APPROVAL_TOKEN:-}"
  local token="${APPROVAL_TOKEN_ARG:-$token_env}"
  if $NO_APPROVAL_FLAG; then
    STRICT_APPROVAL=false
    log "STRICT_APPROVAL disabled (sandbox)."
  fi
  if $APPLY && ! $DRY_RUN; then
    if $STRICT_APPROVAL; then
      if [[ -z "$token" ]]; then
        abort "Remediation requires approval token (env IMDS_APPROVAL_TOKEN or --approval-token)."
      fi
      local token_hash
      token_hash=$(echo -n "$token" | sha256sum | awk '{print $1}')
      log "Approval token accepted (SHA256=$token_hash)"
      export IMDS_TOKEN_HASH="$token_hash"
    else
      log "Approval token bypassed."
    fi
  else
    log "Token validation skipped (apply not requested or dry-run)."
  fi
}

###############################################################################
# Remediation
###############################################################################
perform_remediation() {
  section "Remediation Phase"
  if ! $APPLY; then
    log "Remediation not requested."
    return 0
  fi
  if $DRY_RUN; then
    log "Dry-run: no changes applied."
    return 2
  fi
  if (( EUID != 0 )); then
    abort "Remediation requires root."
  fi

  local changed=false

  if grep -q "$IMDS_IP" /etc/hosts 2>/dev/null; then
    mkdir -p /etc/hosts.bak.d || true
    cp /etc/hosts "/etc/hosts.bak.d/hosts.bak.$TS"
    sed -i "/$IMDS_IP/d" /etc/hosts
    log "$(c_green "Removed /etc/hosts entries for $IMDS_IP (backup created)")"
    apply_action "Removed /etc/hosts overrides"
    changed=true
  fi

  if command -v iptables >/dev/null 2>&1; then
    if ! iptables -C OUTPUT -d "$IMDS_IP" -j ACCEPT >/dev/null 2>&1; then
      iptables -I OUTPUT -d "$IMDS_IP" -j ACCEPT
      log "$(c_green "Inserted iptables ACCEPT rule for $IMDS_IP")"
      apply_action "Inserted iptables ACCEPT rule"
      changed=true
    else
      log "ACCEPT rule for $IMDS_IP already present."
    fi
  fi

  if systemctl list-unit-files 2>/dev/null | grep -q walinuxagent.service; then
    systemctl restart walinuxagent || log "WALinuxAgent restart failed (non-critical)."
    log "WALinuxAgent restarted."
    apply_action "Restarted WALinuxAgent"
    changed=true
  fi

  if $changed; then
    write_audit_record 3
    return 0
  else
    log "No remediation actions necessary."
    write_audit_record 0
    return 2
  fi
}

###############################################################################
# Audit Record
###############################################################################
write_audit_record() {
  local exit_code="$1"
  mkdir -p "$AUDIT_DIR"
  local rec_json act_json
  if command -v jq >/dev/null 2>&1; then
    rec_json=$(printf '%s\n' "${RECOMMENDATIONS[@]}" | jq -R . | jq -s .)
    act_json=$(printf '%s\n' "${ACTIONS_APPLIED[@]}" | jq -R . | jq -s .)
  else
    rec_json="[]"; act_json="[]"
  fi
  {
    echo -n '{"timestamp":"'"$TS"'","host":"'"$(hostname)"'","user":"'"$(whoami)"'","env_class":"'"$ENV_CLASS"'","actions":'
    echo -n "$act_json"
    echo -n ',"recommendations":'
    echo -n "$rec_json"
    echo -n ',"approval_token_hash":"'"${IMDS_TOKEN_HASH:-none}"'","script_version":"'"$TOOL_VERSION"'","exit_code":'"$exit_code"',"issue_ref":"'"$ISSUE_REF"'"}'
    echo
  } >> "$AUDIT_FILE"
  log "Audit record appended to $AUDIT_FILE"
}

###############################################################################
# Emit JSON Summary
###############################################################################
emit_json() {
  $JSON_MODE || return 0
  section "Emit JSON Summary"

  local status
  if $REM_NEEDED && ! $APPLY; then
    status="remediation-recommended"
  elif $APPLY && ((${#ACTIONS_APPLIED[@]} > 0)); then
    status="remediation-applied"
  else
    status="ok"
  fi

  if ! command -v jq >/dev/null 2>&1; then
    log "jq not installed; skipping JSON emission."
    return 0
  fi

  local rec_json act_json err_json metrics_flag
  rec_json=$(printf '%s\n' "${RECOMMENDATIONS[@]}" | jq -R . | jq -s .)
  act_json=$(printf '%s\n' "${ACTIONS_APPLIED[@]}" | jq -R . | jq -s .)
  err_json=$(printf '%s\n' "${ERROR_REASONS[@]}" | jq -R . | jq -s .)
  metrics_flag=false
  $METRICS && metrics_flag=true
  local runtime_ms
  runtime_ms="$(( $(date +%s%3N) - EPOCH_START_MS ))"

  jq -n \
    --arg ts "$TS" \
    --arg script "$SCRIPT_NAME" \
    --arg version "$TOOL_VERSION" \
    --arg status "$status" \
    --arg apply "$APPLY" \
    --arg dry "$DRY_RUN" \
    --arg apiVersion "$API_VERSION" \
    --arg envClass "$ENV_CLASS" \
    --argjson recommendations "$rec_json" \
    --argjson actions "$act_json" \
    --argjson errors "$err_json" \
    --arg metricsGenerated "$metrics_flag" \
    --arg recCount "${#RECOMMENDATIONS[@]}" \
    --arg actCount "${#ACTIONS_APPLIED[@]}" \
    --arg runtimeMs "$runtime_ms" \
    --arg memTotal "${MEM_TOTAL_KB:-0}" \
    --arg memFree "${MEM_FREE_KB:-0}" \
    --arg memAvail "${MEM_AVAILABLE_KB:-0}" \
    --arg issueRef "$ISSUE_REF" \
    '{
       timestamp: $ts,
       script: $script,
       version: $version,
       status: $status,
       apply: ($apply=="true"),
       dry_run: ($dry=="true"),
       api_version: $apiVersion,
       env_class: $envClass,
       recommendations: $recommendations,
       recommendation_count: ($recCount|tonumber),
       actions_applied: $actions,
       actions_count: ($actCount|tonumber),
       error_reasons: $errors,
       metrics_generated: ($metricsGenerated=="true"),
       runtime_ms: ($runtimeMs|tonumber),
       mem_total_kb: ($memTotal|tonumber),
       mem_free_kb: ($memFree|tonumber),
       mem_available_kb: ($memAvail|tonumber),
       issue_ref: $issueRef
     }' > "$JSON_FILE"

  log "JSON summary written: $JSON_FILE"
}

###############################################################################
# Emit Metrics
###############################################################################
emit_metrics() {
  $METRICS || return 0
  section "Emit Prometheus Metrics"
  : > "$METRICS_FILE"
  {
    echo "# IMDS diagnostics metrics"
    echo "# Timestamp: $TS"
    echo "# Version: $TOOL_VERSION"
    for k in "${!METRIC[@]}"; do
      echo "${k} ${METRIC[$k]}"
    done
    echo "# End"
  } >> "$METRICS_FILE"
  log "Metrics written to $METRICS_FILE"
}

###############################################################################
# HTML Report
###############################################################################
emit_html() {
  $HTML_MODE || return 0
  section "Emit HTML Report"
  local status_line="unknown"
  if [[ -f "$JSON_FILE" ]]; then
    status_line=$(jq -r '.status' "$JSON_FILE" 2>/dev/null || echo "unknown")
  fi
  local color="gray"
  case "$status_line" in
    ok) color="green" ;;
    remediation-recommended) color="orange" ;;
    remediation-applied) color="blue" ;;
    *) color="red" ;;
  esac
  {
    echo "<!doctype html><html><head><meta charset='utf-8'><title>IMDS Diagnostic Report</title>"
    echo "<style>body{font-family:Arial,Helvetica,sans-serif;margin:1.2rem;}h1{color:$color;}code{background:#f5f5f5;padding:2px 4px;border-radius:3px;}table{border-collapse:collapse;}td,th{border:1px solid #ddd;padding:4px 8px;} .fail{color:#c00;} .ok{color:#080;}</style>"
    echo "</head><body>"
    echo "<h1>IMDS Diagnostic Report - Status: $status_line</h1>"
    echo "<p><strong>Timestamp:</strong> $TS<br><strong>Version:</strong> $TOOL_VERSION<br><strong>Env Class:</strong> $ENV_CLASS<br><strong>Issue Ref:</strong> $ISSUE_REF</p>"
    if [[ -f "$JSON_FILE" ]]; then
      echo "<h2>Summary</h2><pre>"
      jq '.' "$JSON_FILE"
      echo "</pre>"
    fi
    echo "<h2>Recommendations</h2><ul>"
    if ((${#RECOMMENDATIONS[@]}==0)); then
      echo "<li class='ok'>None</li>"
    else
      for r in "${RECOMMENDATIONS[@]}"; do
        echo "<li class='fail'>$r</li>"
      done
    fi
    echo "</ul>"
    echo "<h2>Metrics</h2>"
    if $METRICS && [[ -f "$METRICS_FILE" ]]; then
      echo "<pre>"
      sed 's/$/<br>/' "$METRICS_FILE"
      echo "</pre>"
    else
      echo "<p>No metrics exported.</p>"
    fi
    echo "<h2>Raw Text Output</h2><pre>"
    sed 's/&/&amp;/g;s/</&lt;/g;s/>/&gt;/g' "$OUT_FILE"
    echo "</pre>"
    echo "<hr><p>Generated by $SCRIPT_NAME v$TOOL_VERSION</p>"
    echo "</body></html>"
  } > "$HTML_FILE"
  log "HTML report written: $HTML_FILE"
}

###############################################################################
# Self-Test Harness
###############################################################################
self_test() {
  section "Self Test Harness"
  log "Syntax check..."
  bash -n "$0"
  log "Dry-run..."
  bash "$0" --dry-run || true
  log "JSON test..."
  bash "$0" --json || true
  [[ -f "$JSON_FILE" ]] && log "JSON produced."
  log "HTML test..."
  bash "$0" --json --html || true
  [[ -f "$HTML_FILE" ]] && log "HTML produced."
  log "Self-test complete."
  exit 0
}

# Early self-test exit
$SELF_TEST && self_test

###############################################################################
# Execution Flow
###############################################################################
: > "$OUT_FILE"
log "START :: $TS"
log "Version=$TOOL_VERSION Flags => APPLY=$APPLY DRY_RUN=$DRY_RUN JSON=$JSON_MODE METRICS=$METRICS HTML=$HTML_MODE API_VERSION=$API_VERSION NO_COLOR=$NO_COLOR STRICT_APPROVAL=$STRICT_APPROVAL NO_APPROVAL_FLAG=$NO_APPROVAL_FLAG SELF_TEST=$SELF_TEST"
load_config
classify_env
snapshot_env
validate_approval_token
check_imds_http
check_imds_tcp
check_ping
check_hosts
check_iptables
check_nftables
check_firewalld
check_ufw
check_walinuxagent
check_blocked_log
check_routing
check_dns

section "Recommendation Summary"
if $REM_NEEDED; then
  log "$(c_yellow "Remediation recommended:")"
  for r in "${RECOMMENDATIONS[@]}"; do log "  - $r"; done
else
  log "$(c_green "No remediation required")"
fi

if $DRY_RUN; then
  section "Dry-Run Preview"
  if $REM_NEEDED; then
    log "Would remove /etc/hosts overrides"
    log "Would add iptables ACCEPT rule if missing"
    log "Would restart WALinuxAgent if present"
  else
    log "No remediation actions would be taken."
  fi
fi

REM_EXIT=0
if $APPLY && ! $DRY_RUN; then
  perform_remediation || REM_EXIT=$?
fi

emit_json
emit_metrics
emit_html

section "Result"
runtime_ms="$(( $(date +%s%3N) - EPOCH_START_MS ))"
if $APPLY && ! $DRY_RUN; then
  case "$REM_EXIT" in
    0) log "$(c_green "Remediation applied successfully")"; echo "SUMMARY:exit=3 status=remediation-applied recs=${#RECOMMENDATIONS[@]} actions=${#ACTIONS_APPLIED[@]} runtime_ms=$runtime_ms env_class=$ENV_CLASS issue_ref=$ISSUE_REF" >> "$OUT_FILE"; exit 3 ;;
    2) log "Nothing to remediate; treating as diagnostics."; echo "SUMMARY:exit=0 status=ok recs=${#RECOMMENDATIONS[@]} actions=0 runtime_ms=$runtime_ms env_class=$ENV_CLASS issue_ref=$ISSUE_REF" >> "$OUT_FILE"; $REM_NEEDED && exit 2 || exit 0 ;;
    *) abort "Remediation encountered an error" ;;
  esac
else
  if $REM_NEEDED; then
    log "$(c_yellow "Remediation recommended (exit 2)")"
    echo "SUMMARY:exit=2 status=remediation-recommended recs=${#RECOMMENDATIONS[@]} actions=0 runtime_ms=$runtime_ms env_class=$ENV_CLASS issue_ref=$ISSUE_REF" >> "$OUT_FILE"
    exit 2
  else
    log "$(c_green "Diagnostics complete (exit 0)")"
    echo "SUMMARY:exit=0 status=ok recs=0 actions=0 runtime_ms=$runtime_ms env_class=$ENV_CLASS issue_ref=$ISSUE_REF" >> "$OUT_FILE"
    exit 0
  fi
fi
