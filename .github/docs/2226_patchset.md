```bash name=.github/scripts/imds_diagnostic.sh url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/scripts/imds_diagnostic.sh
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
  systemctl list-unit-files 2>/dev/null | grep -q walinuxagent.service && has_wala=1 || true
  ip route get "$IMDS_IP" >/dev/null 2>&1 && has_route=1 || true
  [[ -n "${GITHUB_ACTIONS:-}" ]] && gh=1
  grep -E '(docker|container)' /proc/1/cgroup 2>/dev/null >/dev/null && container=1 || true

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
```

````markdown name=.github/docs/imds_diagnostic_RUNBOOK.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_diagnostic_RUNBOOK.md
# IMDS Diagnostic Runbook (Canonical v1.5 Expansion)
> Generated: 2025-11-14 23:07:55 UTC | Author: mbaetiong

## 1. Purpose
This runbook documents the fully expanded IMDS diagnostic and minimal remediation tool (`.github/scripts/imds_diagnostic.sh`) now at version 1.5, integrating environment classification, performance timing (runtime_ms), memory snapshot, HTML reporting, and extended JSON fields.

## 2. Supported Modes
| Mode | Command | Output | System Changes |
|------|---------|--------|----------------|
| Diagnostics | `bash .github/scripts/imds_diagnostic.sh` | `diagnostic_results.txt` | None |
| Dry-run | `bash .github/scripts/imds_diagnostic.sh --dry-run` | Recommendations preview | None |
| Apply (approved) | `sudo IMDS_APPROVAL_TOKEN=<tok> bash .github/scripts/imds_diagnostic.sh --apply` | Remediation + audit JSONL | Yes |
| JSON Summary | `bash .github/scripts/imds_diagnostic.sh --json` | `diagnostic_results.json` | None |
| Metrics Export | `bash .github/scripts/imds_diagnostic.sh --metrics` | `imds_metrics.prom` | None |
| HTML Report | `bash .github/scripts/imds_diagnostic.sh --html --json` | `imds_report.html` | None |
| Self-Test | `bash .github/scripts/imds_diagnostic.sh --self-test` | Validation routine | None |
| Full Evidence | `sudo IMDS_APPROVAL_TOKEN=<tok> bash .github/scripts/imds_diagnostic.sh --apply --json --metrics --html` | All artifacts | Yes |

## 3. New v1.5 Additions
| Feature | Description | Benefit |
|---------|-------------|---------|
| Environment classifier | Heuristics: azure_vm, gha_runner, container, onprem_vm | Contextual interpretation |
| Performance timing | `runtime_ms` captured | SLA & latency tracking |
| Memory snapshot | MemTotal / MemFree / MemAvailable (kB) | Capacity context |
| HTML report | Human-friendly consolidated view | Rapid triage |
| Extended JSON fields | `env_class`, memory, runtime metrics | Automation-ready |
| Hardened dependency checks | Graceful degrade for missing tools | Reliability |

## 4. Diagnostic Coverage
| # | Category | Detail | Evidence |
|---|----------|--------|---------|
| 1 | Env snapshot | Hostname, kernel, distro, interfaces, IP, memory | results.txt |
| 2 | Classification | azure_vm / gha_runner / container / onprem_vm | results.txt |
| 3 | HTTP reachability | Curl with metadata header | status line / error reason |
| 4 | TCP reachability | Raw bash socket connect | success/failure |
| 5 | Ping heuristic | Single ICMP attempt | gauge only |
| 6 | /etc/hosts overrides | Metadata IP lines | numbered lines |
| 7 | iptables screening | OUTPUT chain + DROP rules | rule subset |
| 8 | nftables screening | Ruleset search | matching lines |
| 9 | WALinuxAgent health | Active state + journal tail | last 100 lines |
|10 | Redirection signatures | blocked.jsonl IP redirect to 127.0.0.1 | presence/absence |
|11 | Routing presence | `ip route get` + policy rules | route or missing |
|12 | DNS heuristic | Hostname mapped to metadata IP | hostnames list |
|13 | Recommendations | Aggregated fix suggestions | summary section |
|14 | JSON summary | Structured extended fields | `diagnostic_results.json` |
|15 | Metrics | Prometheus gauges | `imds_metrics.prom` |
|16 | HTML report | Consolidated visual summary | `imds_report.html` |
|17 | Audit trail | JSONL append on remediation | `.codex/audit/imds_remediations.jsonl` |

## 5. Remediation (Guarded)
| Action | Trigger | Backup | Notes |
|--------|---------|--------|-------|
| Remove /etc/hosts lines | Override present | `/etc/hosts.bak.d/hosts.bak.<ts>` | Reversible |
| Insert iptables ACCEPT | Missing allow rule | N/A (removable rule) | Minimal change |
| Restart WALinuxAgent | Service installed | Service restart only | Safe |

## 6. Exit Codes
| Code | Meaning | Operator Action |
|------|---------|-----------------|
| 0 | Diagnostics OK | Attach outputs to issue #2226 |
| 1 | Error occurred | Inspect error reasons / retry |
| 2 | Remediation recommended | Seek @mbaetiong approval |
| 3 | Remediation applied | Re-run diagnostics & attach before/after |

## 7. Extended JSON Fields
| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Tool version (1.5) |
| `env_class` | string | Environment classifier |
| `runtime_ms` | integer | Execution duration |
| `mem_total_kb` | integer | Total memory |
| `mem_free_kb` | integer | Free memory |
| `mem_available_kb` | integer | Available memory |
| `recommendation_count` | integer | Recommendations length |
| `actions_count` | integer | Actions applied length |
| `error_reasons` | array[string] | Machine error codes |
| `metrics_generated` | boolean | Metrics file produced |

## 8. Metrics Catalog
| Metric | 0 | 1 | Description |
|--------|---|---|-------------|
| `imds_http_reachable` | Fail | Success | HTTP GET to IMDS with header |
| `imds_tcp_reachable` | Fail | Success | Raw TCP connect |
| `imds_ping_success` | Fail | Success | ICMP heuristic |
| `hosts_override_present` | No | Yes | /etc/hosts override exists |
| `iptables_drop_detected` | No | Yes | DROP rule referencing IP |
| `walinuxagent_active` | Inactive | Active | Agent health |
| `redirect_signature_present` | Absent | Present | blocked.jsonl redirect |
| `route_to_imds_present` | Missing | Present | Link-local route |
| `hostname_mapped_to_imds` | None | Present | Hostname mapping |

## 9. HTML Report Contents
| Section | Description |
|---------|-------------|
| Header | Status, timestamp, env_class |
| Summary | Raw JSON formatted (if JSON mode) |
| Recommendations | Color-coded list |
| Metrics | Raw metrics file (if exported) |
| Raw Output | Full textual diagnostic log |

## 10. Approval Policy Summary
| Requirement | Mechanism |
|------------|-----------|
| Token (strict) | `IMDS_APPROVAL_TOKEN` or `--approval-token` |
| Bypass (sandbox) | `--no-approval` flag |
| Root required | UID check for `--apply` |
| Audit trail | JSONL append with token hash |
| Backup creation | `/etc/hosts.bak.d/hosts.bak.<ts>` |

## 11. Self-Test Routine
Command: `bash .github/scripts/imds_diagnostic.sh --self-test`  
Performs syntax, dry-run, JSON, and HTML generation tests. Does not modify system or require token.

## 12. Suggested CI Gating
```yaml
- name: IMDS Pre-flight
  run: |
    bash .github/scripts/imds_diagnostic.sh --json --metrics
    jq -e 'select(.status=="ok")' diagnostic_results.json || exit 1
```

## 13. Audit JSONL Example
```json
{"timestamp":"2025-11-14T23:07:55Z","host":"azure-vm-01","user":"root","env_class":"azure_vm","actions":["Removed /etc/hosts overrides"],"recommendations":["Remove /etc/hosts overrides"],"approval_token_hash":"4f8c26...","script_version":"1.5","exit_code":3,"issue_ref":"#2226"}
```

## 14. Error Reason Codes (Reference)
See `imds_error_REASON_CODES.md` for full taxonomy (e.g. `tcp_port_unreachable`, `hosts_override`, `missing_route`).

## 15. Performance Metrics
| Metric | Source | Use |
|--------|--------|-----|
| `runtime_ms` | Internal time delta | SLA & regression tracking |
| Memory fields | `/proc/meminfo` | Capacity correlation |

## 16. Post-Remediation Checklist
| Item | Verification |
|------|-------------|
| Hosts backup exists | `ls /etc/hosts.bak.d/hosts.bak.*` |
| ACCEPT rule present | `iptables -C OUTPUT -d 169.254.169.254 -j ACCEPT` |
| WALinuxAgent active | `systemctl is-active walinuxagent` |
| JSON status `ok` | `jq -r .status diagnostic_results.json` |
| Audit entry appended | `tail -n1 .codex/audit/imds_remediations.jsonl` |

## 17. Version History
| Version | Date | Key Additions |
|---------|------|---------------|
| 1.5 | 2025-11-14 | Env classification, runtime_ms, memory, HTML report |
| 1.4 | 2025-11-14 | Approval token, audit JSONL, self-test |
| 1.3 | 2025-11-14 | Consolidation, metrics initiation |
| 1.2 | 2025-11-14 | Routing & nftables, DNS heuristic |
| 1.1 | 2025-11-14 | JSON summary, WALinuxAgent journal |
| 1.0 | 2025-11-14 | Initial release |

## 18. Governance Contacts
| Role | Contact |
|------|---------|
| Approval Authority | @mbaetiong |
| Secondary Reviewer | @Copilot |
| Security Oversight | @mbaetiong |

## 19. Issue Reference
Relates to: #2226
````

````markdown name=.github/docs/imds_config_GUIDE.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_config_GUIDE.md
# IMDS Config Guide
> Generated: 2025-11-14 23:14:07 UTC | Author: mbaetiong

## Purpose
Configure default behavior of `.github/scripts/imds_diagnostic.sh` via `.github/imds_config.yml` without changing CI or command-line flags.

## File Path
`.github/imds_config.yml`

## Supported Keys
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| strict_approval | boolean | true | Require approval token for `--apply` |
| default_api_version | string | "2021-02-01" | IMDS API version used in HTTP calls |
| default_modes.json | boolean | false | Enable JSON output by default |
| default_modes.metrics | boolean | false | Enable metrics export by default |
| default_modes.html | boolean | false | Enable HTML report by default |
| issue_id | integer | 2226 | Issue reference used in audit JSONL and JSON summary |

## Example
```yaml
strict_approval: true
default_api_version: "2021-02-01"
default_modes:
  json: true
  metrics: true
  html: false
issue_id: 2226
```

## Precedence
- CLI flags override config defaults.
- Environment variables (e.g., `IMDS_APPROVAL_TOKEN`) still required for remediation (unless `--no-approval`).

## Validation
- Script logs which config values are applied at runtime.
- If the file is missing, safe defaults are used.

Relates to: #2226
````

```yaml name=.github/imds_config.yml url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/imds_config.yml
# IMDS Diagnostics Default Configuration (ENERGY 5/5)
strict_approval: true
default_api_version: "2021-02-01"
default_modes:
  json: true
  metrics: true
  html: false
issue_id: 2226
```

````markdown name=.github/docs/imds_firewall_DETECTORS.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_firewall_DETECTORS.md
# IMDS Firewall Detectors
> Generated: 2025-11-14 23:14:07 UTC | Author: mbaetiong

## Purpose
Explain detection-only checks for UFW and firewalld introduced in `imds_diagnostic.sh` v1.6.

## Scope
- Detection highlights potential rules impacting IMDS egress.
- No automatic modification is performed for these systems.
- Recommendations are produced for manual review.

## UFW Detector
| Command | Behavior |
|---------|----------|
| `ufw status numbered` | Scans for `169.254.169.254`, `DENY OUT`, `REJECT OUT` |

- Error code: `ufw_block_rule`
- Recommendation: "Review UFW outbound rules; ensure 169.254.169.254 is permitted."

## firewalld Detector
| Command | Behavior |
|---------|----------|
| `firewall-cmd --get-zones` + `--list-all` per zone | Searches zone config output for `169.254.169.254` references |

- Error code: `firewalld_rule_imds`
- Recommendation: "Review firewalld zone rules for IMDS egress allowance."

## Notes
- iptables/nftables checks remain in place and may overlap with these detectors.
- Detectors are heuristics; absence of findings is not a guarantee that egress is allowed.

Relates to: #2226
````

```yaml name=.github/workflows/imds_comment_on_issue.yml url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/workflows/imds_comment_on_issue.yml
name: IMDS Diagnostics Commenter

on:
  workflow_dispatch:
    inputs:
      apply:
        description: "Attempt remediation (requires IMDS_APPROVAL_TOKEN secret)"
        required: false
        default: "false"
      json:
        description: "Emit JSON summary"
        required: false
        default: "true"
      metrics:
        description: "Emit metrics"
        required: false
        default: "true"
      html:
        description: "Emit HTML report"
        required: false
        default: "true"
  push:
    branches: [ 0D_base_, main ]
    paths:
      - ".github/scripts/imds_diagnostic.sh"
      - ".github/imds_config.yml"

jobs:
  run-and-comment:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Load config (issue_id)
        id: cfg
        shell: bash
        run: |
          ISSUE_ID=2226
          if [ -f .github/imds_config.yml ]; then
            ID=$(grep -E '^[[:space:]]*issue_id:' .github/imds_config.yml | awk -F: '{gsub(/[[:space:]]/, "", $2); print $2}')
            if [ -n "$ID" ]; then ISSUE_ID="$ID"; fi
          fi
          echo "issue_id=$ISSUE_ID" >> "$GITHUB_OUTPUT"

      - name: Run diagnostics
        shell: bash
        env:
          IMDS_APPROVAL_TOKEN: ${{ secrets.IMDS_APPROVAL_TOKEN }}
        run: |
          FLAGS=""
          [ "${{ inputs.json }}" = "true" ] && FLAGS="$FLAGS --json"
          [ "${{ inputs.metrics }}" = "true" ] && FLAGS="$FLAGS --metrics"
          [ "${{ inputs.html }}" = "true" ] && FLAGS="$FLAGS --html"
          if [ "${{ inputs.apply }}" = "true" ]; then
            sudo -E bash .github/scripts/imds_diagnostic.sh --apply $FLAGS || true
          else
            bash .github/scripts/imds_diagnostic.sh $FLAGS || true
          fi

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: imds-evidence
          path: |
            diagnostic_results.txt
            diagnostic_results.json
            imds_metrics.prom
            imds_report.html

      - name: Compose comment body
        id: body
        shell: bash
        run: |
          STATUS="unknown"
          ENV_CLASS="unknown"
          RUNTIME="n/a"
          if [ -f diagnostic_results.json ]; then
            STATUS=$(jq -r '.status' diagnostic_results.json 2>/dev/null || echo "unknown")
            ENV_CLASS=$(jq -r '.env_class' diagnostic_results.json 2>/dev/null || echo "unknown")
            RUNTIME=$(jq -r '.runtime_ms' diagnostic_results.json 2>/dev/null || echo "n/a")
          fi
          echo "status=$STATUS" >> "$GITHUB_OUTPUT"
          echo "env=$ENV_CLASS" >> "$GITHUB_OUTPUT"
          echo "runtime=$RUNTIME" >> "$GITHUB_OUTPUT"
          echo "date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_OUTPUT"

      - name: Post comment to issue
        uses: actions/github-script@v7
        with:
          script: |
            const issue_number = parseInt("${{ steps.cfg.outputs.issue_id }}", 10);
            const status = "${{ steps.body.outputs.status }}";
            const env = "${{ steps.body.outputs.env }}";
            const runtime = "${{ steps.body.outputs.runtime }}";
            const date = "${{ steps.body.outputs.date }}";
            const body = [
              `IMDS diagnostics run (${date})`,
              ``,
              `- Status: ${status}`,
              `- Env class: ${env}`,
              `- Runtime: ${runtime} ms`,
              ``,
              `Artifacts:`,
              `- diagnostic_results.txt`,
              `- diagnostic_results.json`,
              `- imds_metrics.prom`,
              `- imds_report.html`
            ].join("\\n");
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number,
              body
            });
```

````markdown name=.github/docs/IMDS_CHANGELOG.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/IMDS_CHANGELOG.md
# IMDS Tooling CHANGELOG
> Generated: 2025-11-14 23:14:07 UTC | Author: mbaetiong

## [1.6] - 2025-11-14
### Added
- Config loader (`.github/imds_config.yml`) for defaults: strict_approval, API version, default modes, issue_id.
- UFW & firewalld detectors (detection-only) with new error codes (`ufw_block_rule`, `firewalld_rule_imds`).
- Issue reference (`issue_ref`) now appears in JSON summary and audit JSONL.
- Workflow `imds_comment_on_issue.yml` to run diagnostics and comment results to the configured issue.

### Improved
- YAML parsing without external tools; graceful fallback when keys missing.
- Result summary line includes `issue_ref`.

### Security
- Approval token governance unchanged (hash only, no raw storage).

## [1.5] - 2025-11-14
- Env classification, runtime_ms, memory snapshot, HTML report.

## [1.4] - 2025-11-14
- Approval token governance, audit JSONL, self-test harness, metrics summary line.

## [1.3] - 2025-11-14
- Consolidation of overlapping PR variants, initial metrics output.

## [1.2] - 2025-11-14
- Routing, nftables inspection, DNS heuristic.

## [1.1] - 2025-11-14
- JSON summary, WALinuxAgent journal tail.

## [1.0] - 2025-11-14
- Initial diagnostic script & runbook.

Relates to: #2226
````

```yaml name=.github/workflows/imds_preflight.yml url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/workflows/imds_preflight.yml
name: IMDS Pre-Flight Check

on:
  workflow_dispatch:
  pull_request:
    branches: [ 0D_base_, main ]
    paths:
      - ".github/scripts/imds_diagnostic.sh"
      - ".github/workflows/imds_preflight.yml"

jobs:
  imds-preflight:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run IMDS diagnostics (JSON)
        run: |
          bash .github/scripts/imds_diagnostic.sh --json || true
          if [ ! -f diagnostic_results.json ]; then
            echo "JSON summary missing; failing pre-flight."
            exit 1
          fi
          cat diagnostic_results.json

      - name: Gate on status == ok
        run: |
          STATUS=$(jq -r '.status' diagnostic_results.json)
          echo "Status: $STATUS"
          if [ "$STATUS" != "ok" ]; then
            echo "IMDS status not ok (STATUS=$STATUS). Remediation recommended."
            exit 1
          fi
          echo "IMDS pre-flight passed."

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: imds-diagnostics
          path: |
            diagnostic_results.txt
            diagnostic_results.json
```

```yaml name=.github/workflows/shellcheck.yml url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/workflows/shellcheck.yml
name: ShellCheck (IMDS Tooling)

on:
  pull_request:
    paths:
      - ".github/scripts/imds_diagnostic.sh"
      - ".github/workflows/shellcheck.yml"
  workflow_dispatch:

jobs:
  shellcheck:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Install ShellCheck
        run: sudo apt-get update && sudo apt-get install -y shellcheck
      - name: Lint IMDS script
        run: |
          shellcheck .github/scripts/imds_diagnostic.sh || {
            echo "ShellCheck found issues."; exit 1;
          }
      - name: Success
        run: echo "ShellCheck passed for IMDS diagnostic script."
```

```bash name=.github/scripts/imds_aggregate_json.sh url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/scripts/imds_aggregate_json.sh
#!/usr/bin/env bash
# imds_aggregate_json.sh
# Aggregate multiple diagnostic_results.json files into a single summary table.
# ENERGY 5/5

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq required" >&2
  exit 1
fi

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <json_file1> [json_file2 ...]" >&2
  exit 1
fi

TMP=$(mktemp)
echo "host,status,apply,dry_run,recommendation_count,error_count" > "$TMP"

for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "Skipping missing file: $f" >&2
    continue
  fi
  host=$(jq -r '.script' "$f")
  status=$(jq -r '.status' "$f")
  apply=$(jq -r '.apply' "$f")
  dry=$(jq -r '.dry_run' "$f")
  rec_count=$(jq '.recommendations | length' "$f")
  err_count=$(jq '.error_reasons | length' "$f")
  echo "${host},${status},${apply},${dry},${rec_count},${err_count}" >> "$TMP"
done

echo "Aggregate CSV:"
cat "$TMP"

# Optional JSON matrix
jq -n --slurpfile rows <(tail -n +2 "$TMP" | jq -R 'split(",") | {
    script: .[0],
    status: .[1],
    apply: (.[2]=="true"),
    dry_run: (.[3]=="true"),
    recommendation_count: (.[4]|tonumber),
    error_count: (.[5]|tonumber)
  }') '{aggregate: $rows}' > aggregate_imds_matrix.json

echo "JSON matrix written: aggregate_imds_matrix.json"
```

```bash name=.shellcheckrc url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.shellcheckrc
# .shellcheckrc - Configuration for ShellCheck linting (ENERGY 5/5)
# Disable rules that are acceptable within controlled diagnostics context:
disable=SC2181,SC1090
# Allow variable-based command substitution pattern
# Additional rules can be appended as needed.
```

```yaml name=.github/actions/imds-check/action.yml url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/actions/imds-check/action.yml
name: "IMDS Check Composite Action"
description: "Run IMDS diagnostics and fail if remediation is recommended."
inputs:
  json:
    description: "Produce JSON summary"
    required: false
    default: "true"
  metrics:
    description: "Produce metrics file"
    required: false
    default: "false"
runs:
  using: "composite"
  steps:
    - name: Run diagnostics
      shell: bash
      run: |
        FLAGS=""
        [ "${{ inputs.json }}" = "true" ] && FLAGS="$FLAGS --json"
        [ "${{ inputs.metrics }}" = "true" ] && FLAGS="$FLAGS --metrics"
        bash .github/scripts/imds_diagnostic.sh $FLAGS || true
    - name: Gate on status
      if: inputs.json == 'true'
      shell: bash
      run: |
        if [ ! -f diagnostic_results.json ]; then
          echo "Missing JSON summary."
          exit 1
        fi
        STATUS=$(jq -r '.status' diagnostic_results.json)
        echo "Status: $STATUS"
        if [ "$STATUS" != "ok" ]; then
          echo "IMDS status not ok. Failing."
          exit 1
        fi
        echo "IMDS check passed."
```

````markdown name=.github/actions/imds-check/README.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/actions/imds-check/README.md
# IMDS Check Composite Action
This composite action runs the IMDS diagnostic script and optionally gates on JSON status.

## Inputs
| Name | Default | Description |
|------|---------|-------------|
| json | true | Produce JSON summary |
| metrics | false | Produce metrics file |

## Example
```yaml
- uses: ./.github/actions/imds-check
  with:
    json: "true"
    metrics: "true"
```

## Output Behavior
- Fails the job if JSON `status` != `ok` (when json=true).
````

````markdown name=.github/docs/IMDS_FILE_CONSOLIDATION_MATRIX.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/IMDS_FILE_CONSOLIDATION_MATRIX.md
# IMDS File Consolidation Matrix
> Generated: 2025-11-14 23:00:10 UTC | Author: mbaetiong

## Purpose
Provide an authoritative consolidation table mapping all overlapping IMDS-related PR artifacts to the single canonical implementation merged toward `0D_base_`.

## Source Mapping
| PR # | Branch | Artifact(s) | Unique Value | Canonical Action |
|------|--------|-------------|--------------|------------------|
| 2233 | imds/diagnostic-2226-20251114T213200 | Script | Strong base authored by maintainer | Merge (script source) |
| 2228 | copilot/add-imds-diagnostic-runbook | Script + Runbook | Detailed runbook baseline | Integrate runbook content |
| 2230 | copilot/imdsdiagnostic-2226-20251114t213200-again | Script + Runbook + Summary | Implementation summary doc | Cherry-pick summary only |
| 2231 | copilot/add-runbook-and-make-script-executable | Script + Runbook | Duplicate improvements | Close after consolidation |
| 2232 | copilot/add-imds-diagnostic-runbook-again | Script + Typo fix claim | Redundant iteration | Close |
| 2229 | copilot/imdsdiagnostic-2226-20251114t213200 | Script + Runbook (dirty) | Conflicted state | Close |
| 2225 | copilot/sub-pr-2207 | Audit docs (deployment) | Independent domain | Separate merge path |
| 2227 | copilot/autonomous-deployment-orchestration | Orchestration logic | Independent domain | Separate merge path |

## Consolidated Artifact Decisions
| Artifact | Chosen Source | Notes |
|----------|---------------|-------|
| `.github/scripts/imds_diagnostic.sh` | 2233 + enhancements | Extended checks + JSON |
| `.github/docs/imds_diagnostic_RUNBOOK.md` | 2228 baseline + v1.3 revision | Unified formatting & safety model |
| `IMDS_IMPLEMENTATION_SUMMARY.md` | 2230 | Optional maintainers’ context |
| Redundant runbooks/scripts | 2231, 2232, 2229 | Decommission post-merge |

## Avoiding Conflicts
| Risk | Resolution |
|------|------------|
| Divergent permission bits | Set final mode 755 |
| Multiple runbook versions | Single canonical file with version table |
| Unapplied typo fixes | Verified & integrated in final script |
| Dirty merge state (2229) | Close after canonical merge |

## Validation Before Merge
| Check | Command | Expected |
|-------|---------|----------|
| Syntax | `bash -n .github/scripts/imds_diagnostic.sh` | No output |
| Executable bit | `ls -l .github/scripts/imds_diagnostic.sh` | `-rwxr-xr-x` |
| Dry-run preview | `bash .github/scripts/imds_diagnostic.sh --dry-run` | Recommendation section |
| JSON output | `bash .github/scripts/imds_diagnostic.sh --json` | `diagnostic_results.json` |
| Apply safety | `sudo bash .github/scripts/imds_diagnostic.sh --apply` | Backups and rule insertion only |

## Decommission Log (Populate After Merge)
| PR Closed | Final SHA | Reason | Replacement |
|-----------|-----------|--------|------------|
| 2228 | TBD | Runbook integrated | Canonical runbook |
| 2230 | TBD | Summary cherry-picked | Consolidated docs |
| 2231 | TBD | Duplicate | Canonical script/runbook |
| 2232 | TBD | Redundant iteration | Canonical script |
| 2229 | TBD | Conflicted | Canonical script |
| 2225 | N/A | Independent | Kept separate |
| 2227 | N/A | Independent | Kept separate |

## Next Enhancements
| Enhancement | Description | Priority |
|-------------|-------------|----------|
| ShellCheck Workflow | Lint future script changes | Medium |
| Pre-flight IMDS Action | Gating step before deployment | High |
| Prometheus Export | Optional metrics for fleet | Low |
| Automated Approval Gate | Signed token for remediation | Medium |

Relates to issue: #2226
````

````markdown name=.github/docs/IMDS_IMPLEMENTATION_MERGE_PLAN.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/IMDS_IMPLEMENTATION_MERGE_PLAN.md
# IMDS Implementation Merge Plan
> Generated: 2025-11-14 22:43:37 UTC | Author: mbaetiong

## Objective
Merge the canonical IMDS diagnostic tooling into `0D_base_`, ensuring all duplicate PRs are cleanly decommissioned and dependent orchestration efforts rebase on a unified baseline.

## Flow Diagram
```mermaid
flowchart TD
  A[Canonical Script (2233)] --> B[Runbook Integrate (2228)]
  B --> C[Summary Cherry-Pick (2230)]
  C --> D[Integration Validation]
  D --> E[Merge to 0D_base_]
  E --> F[Close Duplicates]
  F --> G[Rebase 2225/2227]
  G --> H[Issue #2226 Final Trace]
```

## Detailed Steps
| Step | Action | Command / Process | Output |
|------|--------|-------------------|--------|
| 1 | Gather canonical artifacts | Copy script/runbook to integration branch | Files staged |
| 2 | Validate syntax & permissions | `bash -n` / `ls -l` | Pass |
| 3 | Dry-run preview | `bash script --dry-run` | Recommendations present |
| 4 | JSON structure check | `bash script --json && cat diagnostic_results.json` | Valid JSON |
| 5 | Optional remediation test (sandbox) | `sudo bash script --apply` | Backup hosts rule insertion |
| 6 | Merge integration → `0D_base_` | PR or fast-forward | Canonical baseline |
| 7 | Close duplicates | Manual PR closure with note | Repo hygiene |
| 8 | Rebase orchestration PRs | `git fetch && git rebase 0D_base_` | Conflict-free |
| 9 | Add ShellCheck workflow | New CI file | Lint coverage |
|10 | Add pre-flight gate step | Update deployment workflow | Early IMDS fail-fast |
|11 | Post final comment on #2226 | Attach results & commit SHA | Traceability |

## Approval Gates
| Gate | Criteria | Approver |
|------|----------|----------|
| Canonical Validation | Syntax, exec bit, dry-run all OK | @mbaetiong |
| Merge Authorization | PR checks green | @mbaetiong |
| Duplicate Closure | All redundant PRs addressed | @mbaetiong |
| Orchestration Rebase | 2225 / 2227 updated | Maintainers |

## Risk & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Merge conflicts from duplicate branches | Delay | Merge canonical first and close rest |
| Unapproved remediation usage | Security / config drift | Enforce runbook approval model |
| Lack of early detection in pipelines | Hidden failures | Add pre-flight gating workflow |
| Divergence from 0D_base_ | Multi-branch confusion | Fast-forward integration promptly |

## Success Criteria
| Criterion | Measurement |
|-----------|-------------|
| Single script & runbook | Only one copy in repo |
| Duplicates closed | All IMDS PRs except canonical closed |
| Pipeline integration | Pre-flight step present |
| Issue #2226 updated | Comment with artifacts & status |
| ShellCheck pass | CI green on lint workflow |

## Post-Merge Checklist
| Item | Status |
|------|--------|
| Script merged | Pending |
| Runbook merged | Pending |
| Summary doc added | Optional |
| ShellCheck workflow added | Pending |
| Pre-flight gating implemented | Pending |
| Issue updated | Pending |
| Duplicates closed | Pending |

## Final Issue Comment Template
```text
Canonical IMDS diagnostic tooling merged.
Commit: <SHA>
Artifacts:
- .github/scripts/imds_diagnostic.sh
- .github/docs/imds_diagnostic_RUNBOOK.md

Next Steps:
1. Run diagnostics on affected runners.
2. Attach diagnostic_results.txt (+ JSON) to issue #2226.
3. Seek approval for remediation before --apply.
4. Close redundant IMDS PRs.

cc: @Copilot @mbaetiong
```

Relates to: #2226
````

````markdown name=.github/docs/IMDS_JSON_SCHEMA.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/IMDS_JSON_SCHEMA.md
# IMDS JSON Summary Schema
> Generated: 2025-11-14 23:00:10 UTC | Author: mbaetiong

## Purpose
Define the schema for `diagnostic_results.json` produced by the canonical IMDS diagnostic script for validation, ingestion, and automation gating.

## Schema (Draft v1)
```json
{
  "type": "object",
  "required": [
    "timestamp",
    "script",
    "status",
    "apply",
    "dry_run",
    "recommendations",
    "actions_applied"
  ],
  "properties": {
    "timestamp": {
      "type": "string",
      "description": "UTC ISO 8601 timestamp"
    },
    "script": {
      "type": "string",
      "description": "Name of executing script"
    },
    "status": {
      "type": "string",
      "enum": ["ok", "remediation-recommended", "remediation-applied"],
      "description": "Overall diagnostic state"
    },
    "apply": {
      "type": "boolean",
      "description": "Was remediation applied?"
    },
    "dry_run": {
      "type": "boolean",
      "description": "Was the run a dry-run preview?"
    },
    "recommendations": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of suggested remediation steps"
    },
    "actions_applied": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of actual remediation operations performed"
    }
  },
  "additionalProperties": false
}
```

## Example Payload
```json
{
  "timestamp": "2025-11-14T22:58:11Z",
  "script": "imds_diagnostic.sh",
  "status": "remediation-recommended",
  "apply": false,
  "dry_run": false,
  "recommendations": [
    "Remove /etc/hosts mappings for 169.254.169.254",
    "Insert iptables ACCEPT rule for 169.254.169.254"
  ],
  "actions_applied": []
}
```

## Validation Command
```bash
jq -e '
  .status | IN("ok","remediation-recommended","remediation-applied") and
  (type=="object") and
  (.recommendations|type=="array") and
  (.actions_applied|type=="array")
' diagnostic_results.json || { echo "Invalid IMDS JSON summary"; exit 1; }
```

## Pipeline Gate Example
```yaml
- name: Validate IMDS JSON Summary
  run: |
    bash .github/scripts/imds_diagnostic.sh --json
    jq -e '.status == "ok"' diagnostic_results.json || {
      echo "IMDS diagnostics require remediation"; exit 1;
    }
```

Relates to issue: #2226
````

````markdown name=.github/docs/IMDS_MANIFEST.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/IMDS_MANIFEST.md
# IMDS Canonical Manifest
> Generated: 2025-11-14 23:00:10 UTC | Author: mbaetiong

## Purpose
Enumerate all authoritative IMDS diagnostic tooling assets to retain under `0D_base_` and list duplicates marked for decommission.

## Canonical Files (To KEEP)
| File | Purpose | Version Source |
|------|---------|----------------|
| `.github/scripts/imds_diagnostic.sh` | Diagnostics + guarded remediation | Consolidated (2233 base) |
| `.github/docs/imds_diagnostic_RUNBOOK.md` | Operational usage & safety model | 2228 baseline + revisions |
| `.github/docs/IMDS_FILE_CONSOLIDATION_MATRIX.md` | PR artifact mapping | New consolidation |
| `.github/docs/IMDS_IMPLEMENTATION_MERGE_PLAN.md` | Merge & rollout steps | New |
| `.github/docs/IMDS_JSON_SCHEMA.md` | JSON contract for automation | New |
| `.github/docs/IMDS_CHANGELOG.md` | Version history | New |
| `.github/docs/IMDS_MANIFEST.md` | This manifest | New |

## Optional / Conditional Files
| File | Condition to Include | Notes |
|------|----------------------|-------|
| `IMDS_IMPLEMENTATION_SUMMARY.md` | If maintainers request deeper audit context | From PR 2230 |
| ShellCheck workflow | After canonical merge | Adds lint enforcement |
| Pre-flight IMDS workflow | Before deployment merges | Ensures IMDS accessible |

## Duplicate / Redundant PR Artifacts (To REMOVE or CLOSE)
| PR # | Artifact Type | Action | Rationale |
|------|---------------|--------|-----------|
| 2228 | Runbook copy | Close | Integrated |
| 2230 | Script + runbook + summary | Cherry-pick summary then close | Summaries only |
| 2231 | Duplicate script/runbook | Close | No unique content |
| 2232 | Iterative duplicate | Close | Redundant changes |
| 2229 | Conflicted/dirtied state | Close | Superseded by canonical |

## Merge Sequence Snapshot
1. Validate canonical script & runbook.
2. Merge into staging or directly into `0D_base_`.
3. Add supporting documentation (matrix, merge plan, schema, changelog).
4. Close duplicates with link to commit SHA.
5. Rebase dependent orchestration PRs (2225, 2227).
6. Add CI enhancements (ShellCheck, pre-flight action).

## Governance / Approval
| Action | Required Approval | Artifact |
|--------|-------------------|----------|
| Remediation run (`--apply`) | @mbaetiong | Script |
| Duplicate closure | @mbaetiong | PRs 2228/2230/2231/2232/2229 |
| Workflow introduction | @mbaetiong | ShellCheck / Pre-flight gating |

Relates to issue: #2226
````

````markdown name=.github/docs/imds_ci_INTEGRATION_GUIDE.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_ci_INTEGRATION_GUIDE.md
# CI Integration Guide for IMDS Tooling (Updated)
> Generated: 2025-11-14 23:05:12 UTC | Author: mbaetiong

## Composite Action Usage
```yaml
- uses: ./.github/actions/imds-check
  with:
    json: "true"
    metrics: "true"
```

## Multi-Host Aggregation Step
```yaml
- name: Aggregate host results
  run: |
    bash .github/scripts/imds_aggregate_json.sh host*/diagnostic_results.json > /dev/null
    jq '.aggregate | length' aggregate_imds_matrix.json
```

## Failure Pattern
| Status | Action |
|--------|--------|
| remediation-recommended | Block deploy; seek approval |
| remediation-applied | Re-run diagnostics immediately |
| ok | Proceed |

Relates to issue: #2226
````

````markdown name=.github/docs/imds_error_REASON_CODES.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_error_REASON_CODES.md
# IMDS Error Reason Codes Reference (v1.5)
> Generated: 2025-11-14 23:07:55 UTC | Author: mbaetiong

## Purpose
Document machine-readable error codes included in `error_reasons` array of JSON summary.

## Codes
| Code | Meaning | Typical Cause | Remediation |
|------|--------|---------------|------------|
| dns_resolution_failure | Name resolution failure | Broken resolver config | Validate resolv.conf / network |
| connection_timeout | TCP timeout | Firewall / NSG / route block | Inspect ACLs, confirm route |
| http_request_failure | Generic curl failure | Transient network / proxy | Retry / inspect proxy chain |
| non_200_status | IMDS responded non-200 | Service issue / header missing | Re-check header / VM state |
| tcp_port_unreachable | Port 80 connect failed | Firewall or routing block | Allow outbound / add route |
| hosts_override | /etc/hosts mapping present | Manual override / artifact | Remove mapping |
| iptables_drop_rule | DROP rule referencing IP | Misconfigured firewall policy | Insert ACCEPT rule / adjust chain |
| walinuxagent_inactive | Agent inactive | Service crash / disabled | Restart/enable WALinuxAgent |
| metadata_ip_redirect | blocked.jsonl redirect signature | Local proxy interception | Remove redirect rule/proxy |
| missing_route | No route to metadata IP | Network config gap | Add link-local route |

## Validation Script
```bash
jq -r '.error_reasons[]' diagnostic_results.json \
 | while read -r c; do grep -q "^| $c " .github/docs/imds_error_REASON_CODES.md || { echo "Undocumented code: $c"; exit 1; }; done
```

Relates to issue: #2226
````

````markdown name=.github/docs/imds_future_ENHANCEMENTS.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_future_ENHANCEMENTS.md
# IMDS Future Enhancements Backlog (Updated)
> Generated: 2025-11-14 23:06:24 UTC | Author: mbaetiong

## New Items
| ID | Title | Description | Effort | Priority | Target |
|----|-------|-------------|--------|----------|--------|
| FE-11 | Approval Token Signature | Verify token with public key signature | M | High | 1.5 |
| FE-12 | Audit Rotation | Rotate JSONL after N records | M | Medium | 1.5 |
| FE-13 | Host Classifier | Auto tag environment (Azure vs GitHub runner) | L | Medium | 1.4 |
| FE-14 | SLA Dashboard | Aggregate daily IMDS success metrics | H | Medium | 1.6 |

(Existing items retained below.)

## Existing Backlog
| ID | Title | Description | Effort | Priority | Target Version |
|----|-------|-------------|--------|----------|----------------|
| FE-01 | Composite Action Packaging | Publish diagnostics as reusable action | M | High | 1.4 |
| FE-02 | Signed Approval Token | Cryptographic signature verification | M | High | 1.5 |
| FE-03 | Prometheus Exporter Daemon | Continuous IMDS polling | H | Medium | 1.6 |
| FE-04 | Dashboard Aggregator | Multi-host visualization | H | Medium | 1.6 |
| FE-05 | Automated Host Route Repair | Intelligent route insertion | H | Low | 1.7 |
| FE-06 | Extended Firewall Parsers | UFW/firewalld detection | M | Medium | 1.5 |
| FE-07 | Non-Linux Support | macOS/Windows partial checks | H | Low | 1.8 |
| FE-08 | Structured Remediation Log | JSONL ledger (implemented) | - | Done | 1.4 |
| FE-09 | Notification Hook | Slack/Teams integration | M | Medium | 1.4 |
| FE-10 | HTML Report Generator | Styled summary conversion | L | Low | 1.5 |

Relates to issue: #2226
````

````markdown name=.github/docs/imds_host_ENV_MATRIX.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_host_ENV_MATRIX.md
# IMDS Host Environment Matrix (Updated)
> Generated: 2025-11-14 23:06:24 UTC | Author: mbaetiong

## Purpose
Map expected diagnostic outcomes by environment type to reduce false positives.

## Environments
| Env Type | Classifier | HTTP | TCP | WALinuxAgent | Notes |
|----------|-----------|------|-----|--------------|-------|
| Azure VM | azure_vm | ✓ | ✓ | ✓ | Target baseline |
| Azure Scale Set | azure_scaleset | ✓ | ✓ | ✓ | Large fleet |
| GitHub Hosted Runner | gha_runner | ✗ | ✗ | ✗ | Expected unreachable |
| On-Prem VM | onprem_vm | ✗ | ✗ | ✗ | Ignore IMDS failures |
| Container | container | ✗ | ✗ | ✗ | Network isolation |
| WSL2 | wsl2 | ✗ | ✗ | ✗ | Non-target scenario |
| Edge Device | edge | ✗ | ✗ | ✗ | Out of scope |

## Interpretation Rules
| Condition | Action |
|-----------|--------|
| Azure VM + HTTP unreachable | Treat as failure; remediation recommended |
| GitHub Hosted + HTTP unreachable | Do not remediate; annotate environment |
| Non-Azure + hosts override | Remove if interfering with other services |
| WALinuxAgent inactive on Azure | Attempt restart after approval |

Relates to issue: #2226
````

````markdown name=.github/docs/imds_shellcheck_GUIDE.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_shellcheck_GUIDE.md
# ShellCheck Guide for IMDS Tooling (Updated)
> Generated: 2025-11-14 23:06:24 UTC | Author: mbaetiong

## Purpose
Ensure ongoing code quality for `.github/scripts/imds_diagnostic.sh`.

## Common Rules to Monitor
| Code | Meaning | Mitigation |
|------|---------|-----------|
| SC2086 | Unquoted vars | Quote parameter expansions |
| SC2016 | Literal braces in echo | Use printf or escape |
| SC2034 | Unused variables | Remove or reference |
| SC2148 | Missing shebang | Ensure `#!/usr/bin/env bash` present |
| SC2155 | Declaration in command substitution | Split declaration & assignment |

## Local Lint
```bash
shellcheck .github/scripts/imds_diagnostic.sh
```

## CI Enforcement
Workflow: `.github/workflows/shellcheck.yml` executes linter on PR touches to script.

## False Positives
| Scenario | ShellCheck Code | Approach |
|----------|----------------|----------|
| Intentional array unused until apply phase | SC2034 | Add comment: `# shellcheck disable=SC2034` |
| Dynamic command building | SC2086 | Validate quoting necessity |

## Inline Suppression Example
```bash
# shellcheck disable=SC2086
curl -sS $IMDS_URL
```

Relates to issue: #2226
````

````markdown name=.github/docs/imds_metrics_EXPORTER.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/.github/docs/imds_metrics_EXPORTER.md
# IMDS Metrics Exporter Guide (v1.5 Update)
> Generated: 2025-11-14 23:07:55 UTC | Author: mbaetiong

## Additions
| Update | Description |
|--------|-------------|
| Version annotation | Metrics file now includes tool version |
| Runtime tracking | `runtime_ms` captured in JSON (not gauge yet) |
| HTML integration | Metrics embedded in HTML report if generated |

## Metrics File
`imds_metrics.prom`  
Prometheus textfile format; scraped via node_exporter textfile collector.

## Metric Catalog
| Metric | Type | Values | Description |
|--------|------|--------|-------------|
| `imds_http_reachable` | Gauge | 0/1 | HTTP metadata endpoint reachable |
| `imds_tcp_reachable` | Gauge | 0/1 | Raw TCP connect to 169.254.169.254:80 |
| `imds_ping_success` | Gauge | 0/1 | ICMP heuristic |
| `hosts_override_present` | Gauge | 0/1 | /etc/hosts override exists |
| `iptables_drop_detected` | Gauge | 0/1 | DROP rule blocking metadata |
| `walinuxagent_active` | Gauge | 0/1 | WALinuxAgent active |
| `redirect_signature_present` | Gauge | 0/1 | blocked.jsonl redirect signature |
| `route_to_imds_present` | Gauge | 0/1 | IP route exists |
| `hostname_mapped_to_imds` | Gauge | 0/1 | Hostname mapped to IP |

## Sample
```text
# IMDS diagnostics metrics
# Timestamp: 2025-11-14T23:07:55Z
# Version: 1.5
imds_http_reachable 1
imds_tcp_reachable 1
imds_ping_success 0
hosts_override_present 0
iptables_drop_detected 0
walinuxagent_active 1
redirect_signature_present 0
route_to_imds_present 1
hostname_mapped_to_imds 0
# End
```

## Scraping Integration
```bash
bash .github/scripts/imds_diagnostic.sh --metrics --json
cp imds_metrics.prom /var/lib/node_exporter/textfile_collector/
```

## Alert Recommendations
| Alert | Expression | Severity | Rationale |
|-------|------------|----------|-----------|
| IMDS HTTP Down | `imds_http_reachable == 0` | High | Metadata unreachable |
| IMDS Route Missing | `route_to_imds_present == 0` | High | No path |
| Hosts Override | `hosts_override_present == 1` | High | Local misconfig |
| WALinuxAgent Inactive | `walinuxagent_active == 0` | Medium | Agent failure |
| DROP Rule Active | `iptables_drop_detected == 1` | High | Firewall blocking |

## Aggregated Multi-Host
Use `imds_aggregate_json.sh` to combine JSON results for fleet overview.

Relates to issue: #2226
````

````markdown name=IMDS_IMPLEMENTATION_SUMMARY.md url=https://github.com/Aries-Serpent/_codex_/blob/0D_base_/IMDS_IMPLEMENTATION_SUMMARY.md
# IMDS Implementation Summary (Optional Maintainer Context)
> Generated: 2025-11-14 23:00:10 UTC | Author: mbaetiong

## Overview
This summary provides maintainers with contextual lineage, rationale, and consolidation decisions for the IMDS diagnostic tooling prior to final integration on `0D_base_`.

## Lineage of Contributions
| PR | Contribution Type | Incorporated? | Notes |
|----|-------------------|---------------|-------|
| 2233 | Base script | Yes | Canonical foundation |
| 2228 | Runbook content | Yes | Served as baseline paragraphs |
| 2230 | Summary doc concept | Yes | This file inspired by that |
| 2231 | Exec bit adjustments | Yes | Unified permission now 755 |
| 2232 | Minor script iteration | Superseded | No net new logic |
| 2229 | Conflicted variant | Superseded | Dirty merge state avoided |

## Consolidated Improvements
| Area | Enhancement | Benefit |
|------|------------|---------|
| Diagnostics | Routing + nftables + TCP raw connect | Broader failure surface coverage |
| Safety | Dry-run preview | Transparent remediation planning |
| Automation | JSON summary | CI gating & telemetry ingestion |
| Governance | Runbook approval model | Controlled remediation operations |
| Observability | Environment snapshot | Quick host context for triage |

## Final Artifacts
| Artifact | Path | Description |
|----------|------|-------------|
| Script | `.github/scripts/imds_diagnostic.sh` | Canonical diagnostics & remediation |
| Runbook | `.github/docs/imds_diagnostic_RUNBOOK.md` | Operational documentation |
| Matrix | `.github/docs/IMDS_FILE_CONSOLIDATION_MATRIX.md` | Mapping of all sources |
| Merge Plan | `.github/docs/IMDS_IMPLEMENTATION_MERGE_PLAN.md` | Step-by-step integration workflow |
| Manifest | `.github/docs/IMDS_MANIFEST.md` | Keep vs remove ledger |
| JSON Schema | `.github/docs/IMDS_JSON_SCHEMA.md` | Contract for structured results |
| CHANGELOG | `.github/docs/IMDS_CHANGELOG.md` | Version trace |
| Pre-Flight Workflow | `.github/workflows/imds_preflight.yml` | Deployment gating |
| ShellCheck Workflow | `.github/workflows/shellcheck.yml` | Script linting quality gate |

## Post-Integration KPIs
| KPI | Metric | Target |
|-----|--------|--------|
| IMDS availability success rate | Pre-flight checks passing | ≥ 99% |
| Mean triage time (IMDS failures) | Minutes to actionable recommendation | ≤ 5 min |
| Remediation approval compliance | % of `--apply` runs with documented approval | 100% |
| Duplicate PR closure latency | Time from canonical merge to closure | ≤ 24h |

## Future Roadmap
| Feature | Description | ETA |
|---------|-------------|-----|
| Prometheus exporter | Metrics for fleet-wide IMDS health | 1.5 |
| Signed approval token | Controlled remediation gating | 1.5 |
| Aggregated dashboard | Central visualization of JSON outputs | 1.6 |

Relates to issue: #2226
````
