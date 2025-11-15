# IMDS Host Environment Matrix

## Supported Operating Systems

| OS | Version | Status | Notes |
|----|---------|--------|-------|
| Ubuntu | 22.04 LTS | ✅ Supported | Recommended |
| Ubuntu | 20.04 LTS | ✅ Supported | Fully tested |
| Ubuntu | 18.04 LTS | ⚠️ Limited | EOL soon |
| Debian | 11 (Bullseye) | ✅ Supported | Tested |
| Debian | 10 (Buster) | ✅ Supported | Tested |
| RHEL | 9 | ✅ Supported | Tested |
| RHEL | 8 | ✅ Supported | Fully tested |
| RHEL | 7 | ⚠️ Limited | Legacy support |
| CentOS | 8 Stream | ✅ Supported | Tested |
| CentOS | 7 | ⚠️ Limited | Legacy support |
| Rocky Linux | 9 | ✅ Supported | Tested |
| Rocky Linux | 8 | ✅ Supported | Tested |
| AlmaLinux | 9 | ✅ Supported | Tested |
| AlmaLinux | 8 | ✅ Supported | Tested |
| Fedora | 38 | ✅ Supported | Tested |
| Fedora | 37 | ✅ Supported | Tested |
| SUSE Linux | 15 SP4 | ✅ Supported | Tested |
| openSUSE | Leap 15.4 | ✅ Supported | Tested |
| Windows Server | 2022 | 🔄 Planned | Future support |
| Windows Server | 2019 | 🔄 Planned | Future support |

## Shell Requirements

| Shell | Version | Status |
|-------|---------|--------|
| Bash | 4.0+ | ✅ Required |
| Bash | 5.0+ | ✅ Recommended |
| sh | POSIX | ⚠️ Limited |
| zsh | Any | ❌ Not supported |
| fish | Any | ❌ Not supported |

## Azure VM Sizes

Tested and verified on:
- Standard_B1s
- Standard_B2s
- Standard_D2s_v3
- Standard_D4s_v3
- Standard_E2s_v3
- Standard_F2s_v2

## Dependency Versions

| Dependency | Minimum Version | Recommended |
|------------|----------------|-------------|
| curl | 7.0 | 7.68+ |
| jq | 1.5 | 1.6+ |
| bash | 4.0 | 5.0+ |
| coreutils | 8.0 | 8.30+ |

## CI/CD Runners

| Platform | Runner Type | Status |
|----------|-------------|--------|
| GitHub Actions | Ubuntu latest | ✅ Tested |
| GitHub Actions | Self-hosted (Azure) | ✅ Tested |
| Azure DevOps | Microsoft-hosted | ✅ Tested |
| Azure DevOps | Self-hosted | ✅ Tested |
| GitLab CI | Docker | ✅ Tested |
| GitLab CI | Shell | ✅ Tested |
| Jenkins | Docker | ✅ Tested |
| CircleCI | Machine | ✅ Tested |

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15
