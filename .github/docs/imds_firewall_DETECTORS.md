# IMDS Firewall Detectors

## Overview

This document describes the firewall detection mechanisms used by the IMDS diagnostic tool to identify firewall rules that may be blocking access to the Azure Instance Metadata Service.

## Supported Firewalls

The diagnostic tool can detect the following firewall systems:

1. **iptables** - Linux kernel firewall (netfilter)
2. **nftables** - Modern replacement for iptables
3. **ufw** - Uncomplicated Firewall (Ubuntu/Debian)
4. **firewalld** - Dynamic firewall manager (RHEL/CentOS)

## Detection Methods

### iptables Detection

#### How It Works

The tool checks iptables rules for any rules affecting the IMDS endpoint (169.254.169.254):

```bash
sudo iptables -L -n -v | grep 169.254.169.254
```

#### Checked Chains

- **INPUT**: Incoming traffic rules
- **OUTPUT**: Outgoing traffic rules
- **FORWARD**: Forwarded traffic rules

#### Example Rules That Block IMDS

```bash
# Block all OUTPUT to IMDS
iptables -A OUTPUT -d 169.254.169.254 -j REJECT

# Drop packets to IMDS
iptables -A OUTPUT -d 169.254.169.254 -j DROP

# Block specific port
iptables -A OUTPUT -d 169.254.169.254 -p tcp --dport 80 -j REJECT
```

#### Detection Output

```json
{
  "firewall_iptables": "detected",
  "firewall_rule_details": "OUTPUT chain has REJECT rule for 169.254.169.254"
}
```

### nftables Detection

#### How It Works

Checks nftables ruleset for rules affecting IMDS:

```bash
sudo nft list ruleset | grep 169.254.169.254
```

#### Example Rules That Block IMDS

```bash
# Drop packets to IMDS
nft add rule ip filter output ip daddr 169.254.169.254 drop

# Reject connections
nft add rule ip filter output ip daddr 169.254.169.254 reject
```

#### Detection Output

```json
{
  "firewall_nftables": "detected",
  "nftables_rules": ["ip daddr 169.254.169.254 drop"]
}
```

### ufw Detection

#### How It Works

Checks UFW status and rules:

```bash
sudo ufw status verbose
sudo grep 169.254.169.254 /etc/ufw/*.rules
```

#### Example Rules That Block IMDS

```bash
# Deny outgoing to IMDS
sudo ufw deny out to 169.254.169.254

# Deny specific port
sudo ufw deny out to 169.254.169.254 port 80
```

#### Detection Output

```json
{
  "firewall_ufw": "detected",
  "ufw_status": "active",
  "ufw_rules": ["DENY OUT 169.254.169.254"]
}
```

### firewalld Detection

#### How It Works

Checks firewalld zones and rich rules:

```bash
sudo firewall-cmd --list-all
sudo firewall-cmd --list-rich-rules | grep 169.254.169.254
```

#### Example Rules That Block IMDS

```bash
# Add rich rule to block IMDS
firewall-cmd --add-rich-rule='rule family="ipv4" destination address="169.254.169.254" reject'

# Block in specific zone
firewall-cmd --zone=public --add-rich-rule='rule family="ipv4" destination address="169.254.169.254" drop'
```

#### Detection Output

```json
{
  "firewall_firewalld": "detected",
  "firewalld_zone": "public",
  "firewalld_rules": ["destination address=169.254.169.254 reject"]
}
```

## Permission Requirements

### Minimal Mode (No sudo)

Without sudo privileges, the tool can:
- Check if firewall tools are installed
- Read some basic firewall status
- **Cannot** inspect detailed firewall rules

```bash
# Run without firewall checks
./.github/scripts/imds_diagnostic.sh --skip-firewall
```

### Full Mode (With sudo)

With sudo privileges, the tool can:
- List all firewall rules
- Detect IMDS-specific blocks
- Provide detailed diagnostics

```bash
# Run with full firewall detection
sudo ./.github/scripts/imds_diagnostic.sh
```

## Common Firewall Configurations

### Allow IMDS (Recommended)

#### iptables
```bash
# Ensure IMDS is accessible
sudo iptables -I OUTPUT -d 169.254.169.254 -p tcp --dport 80 -j ACCEPT
```

#### nftables
```bash
# Allow IMDS
sudo nft add rule ip filter output ip daddr 169.254.169.254 tcp dport 80 accept
```

#### ufw
```bash
# Allow outgoing to IMDS
sudo ufw allow out to 169.254.169.254 port 80
```

#### firewalld
```bash
# Add rich rule to allow IMDS
sudo firewall-cmd --add-rich-rule='rule family="ipv4" destination address="169.254.169.254" port protocol="tcp" port="80" accept'
sudo firewall-cmd --runtime-to-permanent
```

### Block IMDS (Not Recommended)

⚠️ **Warning**: Blocking IMDS will prevent many Azure services from functioning correctly.

#### iptables
```bash
sudo iptables -A OUTPUT -d 169.254.169.254 -j REJECT
```

#### nftables
```bash
sudo nft add rule ip filter output ip daddr 169.254.169.254 drop
```

## Detection Algorithm

### Detection Flow

```
1. Check if firewall tools are installed
   ├─ iptables --version
   ├─ nft --version
   ├─ ufw --version
   └─ firewall-cmd --version

2. For each installed tool:
   ├─ Attempt to list rules (requires sudo)
   ├─ Search for IMDS IP (169.254.169.254)
   └─ Parse and categorize rules

3. Categorize results:
   ├─ "none" - No blocking rules found
   ├─ "detected" - Blocking rules found
   ├─ "unavailable" - Tool not installed
   └─ "permission_denied" - Cannot check (no sudo)

4. Aggregate findings:
   └─ Overall firewall_check status
```

### Pseudo-code

```python
def detect_firewall_rules():
    results = {}
    
    # Check iptables
    if command_exists('iptables'):
        if has_sudo():
            rules = run('iptables -L -n')
            if '169.254.169.254' in rules:
                results['iptables'] = 'detected'
            else:
                results['iptables'] = 'none'
        else:
            results['iptables'] = 'permission_denied'
    else:
        results['iptables'] = 'unavailable'
    
    # Check nftables
    if command_exists('nft'):
        if has_sudo():
            rules = run('nft list ruleset')
            if '169.254.169.254' in rules:
                results['nftables'] = 'detected'
            else:
                results['nftables'] = 'none'
        else:
            results['nftables'] = 'permission_denied'
    else:
        results['nftables'] = 'unavailable'
    
    return results
```

## False Positives

### Allow Rules

The detector may flag ALLOW rules as "detected" since it searches for any mention of the IMDS IP. Review the actual rules to determine if they're blocking or allowing traffic.

```bash
# This ALLOWS IMDS but will be "detected"
iptables -A OUTPUT -d 169.254.169.254 -j ACCEPT
```

**Solution**: Manually inspect rules when "detected" is returned.

### Commented Rules

Some firewall configurations store commented-out rules that won't actually affect traffic:

```bash
# iptables -A OUTPUT -d 169.254.169.254 -j REJECT  # Disabled
```

**Solution**: The detection tool should be updated to ignore comments.

## Troubleshooting

### Firewall Check Skipped

```json
{
  "firewall_check": "skipped"
}
```

**Cause**: `--skip-firewall` flag was used

**Solution**: Run without the flag for full diagnostics

### Permission Denied

```json
{
  "firewall_iptables": "permission_denied"
}
```

**Cause**: No sudo access

**Solution**: Run with sudo or configure passwordless sudo for diagnostic commands

### Firewall Not Detected

```json
{
  "firewall_check": "passed",
  "firewall_iptables": "none"
}
```

**Cause**: Either no firewall is installed or no blocking rules exist

**Solution**: This is the desired state for IMDS access

## Best Practices

1. **Don't Block IMDS**: Avoid blocking 169.254.169.254 as it breaks Azure services
2. **Use Allow Rules**: If using a default-deny policy, explicitly allow IMDS
3. **Test After Changes**: Always test IMDS access after firewall changes
4. **Document Rules**: Document why IMDS rules exist
5. **Audit Regularly**: Regularly audit firewall rules

## Integration with CI/CD

### Skip Firewall Checks in CI

```yaml
- uses: ./.github/actions/imds-check
  with:
    skip-firewall: true  # CI runners typically don't have sudo
```

### Conditional Firewall Checks

```yaml
- name: Check firewall (if sudo available)
  run: |
    if sudo -n true 2>/dev/null; then
      ./.github/scripts/imds_diagnostic.sh
    else
      ./.github/scripts/imds_diagnostic.sh --skip-firewall
    fi
```

## Related Documentation

- [IMDS Diagnostic Runbook](imds_diagnostic_RUNBOOK.md)
- [Configuration Guide](imds_config_GUIDE.md)
- [Error Reason Codes](imds_error_REASON_CODES.md)

## References

- [iptables Documentation](https://netfilter.org/documentation/)
- [nftables Wiki](https://wiki.nftables.org/)
- [UFW Documentation](https://help.ubuntu.com/community/UFW)
- [firewalld Documentation](https://firewalld.org/documentation/)

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Maintainer:** IMDS Diagnostic Team
