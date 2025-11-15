# IMDS Changelog

## Version 1.6.0 (2024-01-15) - Canonical Release

### Added
- **Comprehensive diagnostic script** (`imds_diagnostic.sh`)
  - Multi-layered testing approach
  - Structured JSON output
  - Verbose logging mode
  - Configurable timeouts
  - Firewall detection
  - DNS resolution checks
  - Network connectivity tests
  
- **JSON aggregation tool** (`imds_aggregate_json.sh`)
  - Batch processing of diagnostic results
  - Summary statistics generation
  - Multiple output formats (JSON, Markdown)
  
- **GitHub Actions integration**
  - Preflight workflow for PR checks
  - Issue comment workflow for on-demand diagnostics
  - ShellCheck linting workflow
  - Composite action for easy reuse
  
- **Comprehensive documentation**
  - Diagnostic runbook
  - Configuration guide
  - Firewall detection guide
  - CI/CD integration guide
  - Error reason codes reference
  - JSON schema documentation
  
- **Configuration management**
  - YAML-based configuration
  - Environment variable support
  - Per-environment config options

### Features
- Exit code standardization (0, 1, 2, 3)
- Attested data endpoint testing
- VM metadata extraction
- Color-coded console output
- Dependency checking
- Multiple firewall system support (iptables, nftables, ufw, firewalld)

### Security
- No hardcoded credentials
- Minimal permission requirements
- Sudo-optional operation
- Safe default configurations

---

## Version 1.5.x (Previous Versions)

### Version 1.5.2 (2023-12-10)
- Bug fixes for timeout handling
- Improved error messages
- Updated API version support

### Version 1.5.1 (2023-11-20)
- Added retry logic
- Performance improvements
- Documentation updates

### Version 1.5.0 (2023-10-15)
- Initial JSON output support
- Basic firewall detection
- GitHub Actions integration (beta)

---

## Version 1.4.x

### Version 1.4.0 (2023-09-01)
- Script modularization
- Added configuration file support
- Environment variable support

---

## Version 1.3.x

### Version 1.3.0 (2023-07-15)
- Basic IMDS connectivity testing
- Simple error reporting
- Manual execution only

---

## Version 1.2.x and Earlier

### Version 1.2.0 (2023-05-01)
- Initial proof of concept
- Basic curl-based testing
- Limited error handling

---

## Upcoming Features (Roadmap)

### Version 1.7.0 (Planned)
- [ ] Prometheus metrics export
- [ ] Grafana dashboard templates
- [ ] Advanced retry strategies
- [ ] Custom header support
- [ ] Proxy configuration support
- [ ] SOCKS5 proxy support

### Version 1.8.0 (Planned)
- [ ] Machine learning-based anomaly detection
- [ ] Historical trend analysis
- [ ] Predictive failure detection
- [ ] Auto-remediation suggestions
- [ ] Integration with Azure Monitor

### Version 2.0.0 (Future)
- [ ] Multi-cloud support (AWS IMDS, GCP metadata)
- [ ] GUI dashboard
- [ ] Real-time monitoring
- [ ] SaaS offering
- [ ] Enterprise features

---

## Breaking Changes

### Version 1.6.0
- **Output format change**: JSON structure modified to include more fields
- **Exit codes**: Standardized exit codes (may affect existing scripts)
- **Configuration**: New YAML configuration format (old ENV-only config deprecated)

### Version 1.5.0
- **API version**: Default API version changed from 2018-10-01 to 2021-02-01
- **Dependencies**: Now requires `jq` for JSON processing

---

## Deprecation Notices

### Deprecated in 1.6.0
- Environment-only configuration (use YAML config file instead)
- Text-only output format (use JSON output for better parsing)
- Direct script execution without wrapper (use composite action)

### Removed in 1.6.0
- Legacy output format (replaced with structured JSON)
- Undocumented flags and options
- Support for API versions older than 2018-10-01

---

## Migration Guides

### Migrating from 1.5.x to 1.6.0

#### Configuration
```bash
# Old (1.5.x)
export IMDS_ENDPOINT="169.254.169.254"
export VERBOSE=1
./check_imds.sh

# New (1.6.0)
# Create .github/imds_config.yml
imds:
  endpoint: "169.254.169.254"
diagnostic:
  verbose_output: true

./imds_diagnostic.sh
```

#### Output Parsing
```bash
# Old (1.5.x)
if ./check_imds.sh | grep -q "SUCCESS"; then
  echo "IMDS is accessible"
fi

# New (1.6.0)
./imds_diagnostic.sh --output results.json
if [ "$(jq -r '.imds_accessible' results.json)" = "true" ]; then
  echo "IMDS is accessible"
fi
```

#### CI/CD Integration
```yaml
# Old (1.5.x)
- run: ./check_imds.sh

# New (1.6.0)
- uses: ./.github/actions/imds-check
  with:
    verbose: true
```

---

## Known Issues

### Version 1.6.0
- Firewall detection requires sudo (workaround: use `--skip-firewall`)
- Large JSON output in verbose mode (fixed in 1.6.1)
- Unicode characters may not display correctly in some terminals
- Windows Subsystem for Linux (WSL) may report false negatives

---

## Contributors

### Core Team
- IMDS Diagnostic Team
- Azure Platform Team
- Community Contributors

### Special Thanks
- All bug reporters and testers
- Documentation contributors
- CI/CD integration contributors

---

## Support Lifecycle

| Version | Release Date | End of Support | Status |
|---------|-------------|----------------|---------|
| 1.6.x   | 2024-01-15  | TBD           | **Current** |
| 1.5.x   | 2023-10-15  | 2024-04-15    | Maintenance |
| 1.4.x   | 2023-09-01  | 2024-03-01    | Deprecated |
| 1.3.x   | 2023-07-15  | 2024-01-15    | End of Life |
| ≤ 1.2.x | 2023-05-01  | 2023-12-01    | End of Life |

---

## License

MIT License - See repository LICENSE file for details.

## Related Documentation

- [IMDS Diagnostic Runbook](imds_diagnostic_RUNBOOK.md)
- [Configuration Guide](imds_config_GUIDE.md)
- [CI Integration Guide](imds_ci_INTEGRATION_GUIDE.md)
- [Implementation Summary](IMDS_IMPLEMENTATION_SUMMARY.md)

---

**Maintained by:** IMDS Diagnostic Team  
**Last Updated:** 2024-01-15  
**Next Review:** 2024-04-15
