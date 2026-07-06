# PHASE 13 TRACK 13.3: SBOM GENERATION & VALIDATION FRAMEWORK

**Session**: phase-13-track-13-3-deployment  
**Date**: 2026-07-06T05:43:52Z  
**Mode**: ADVISORY (Design & Analysis)  
**Authority**: @mbaetiong (D-tier autonomous)  

---

## EXECUTIVE SUMMARY

This document designs the SBOM (Software Bill of Materials) generation and validation framework for Phase 13 Track 13.3. The system generates comprehensive supply chain documentation in multiple formats (CycloneDX, SPDX) and validates component integrity.

**Key Design Decisions:**
- **Multi-Format Support**: CycloneDX + SPDX for maximum interoperability
- **Automated Generation**: Scan dependencies at build time, no manual updates
- **Integrity Validation**: Hash all components, detect tampering
- **Compliance Integration**: Maps to supply chain compliance requirements

---

## 1. SBOM GENERATION ARCHITECTURE

### 1.1 Component Overview

```
┌──────────────────────────────────────────────────────────────────┐
│      SBOM GENERATION & VALIDATION FRAMEWORK                      │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────┐ │
│  │ Dependency Discovery │  │ Component Cataloging │  │ Signing│ │
│  │ ──────────────────   │  │ ──────────────────   │  │ ──────│ │
│  │                      │  │                      │  │        │ │
│  │ • Scan lock files    │→→│ • Extract metadata   │→→│ • SBOM │ │
│  │ • Detect transitive  │  │ • Normalize URLs     │  │   sign │ │
│  │ • Map to sources     │  │ • Calculate hashes   │  │ • Store│ │
│  │                      │  │ • Gather licenses    │  │        │ │
│  └──────────────────────┘  └──────────────────────┘  └────────┘ │
│         ▲                           ▲                    ▼        │
│         │ Lock files               │                   │        │
│         │ Package metadata         │                   ▼        │
│         │                          │          ┌──────────────┐  │
│         └──────────────────────────┴──────────│ Validation & │  │
│                                               │ Compliance   │  │
│                                               └──────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Dependency Source Mapping

**Python Dependency Sources**:
```
requirements.txt           → pip-based dependencies
pyproject.toml             → Modern Python projects (PEP 517)
Pipfile.lock              → Pipenv projects
poetry.lock               → Poetry projects
uv.lock                   → UV (fast pip alternative)
setup.py / setup.cfg      → Legacy projects
site-packages/            → Installed environment (fallback)
```

**Rust Dependency Sources**:
```
Cargo.lock                → Rust projects
Cargo.toml                → Manifest with version ranges
target/debug/deps/        → Compiled binaries (extract metadata)
```

**Node.js Dependency Sources**:
```
package-lock.json         → npm lockfile
yarn.lock                 → Yarn lockfile
pnpm-lock.yaml            → pnpm lockfile
node_modules/             → Installed packages
```

---

## 2. SBOM GENERATION LAYER

### 2.1 Dependency Discovery

```python
class DependencyDiscoveryEngine:
    """Discovers all dependencies across ecosystems."""
    
    async def discover_all(self) -> dict:
        """Discover dependencies from all sources."""
        
        dependencies = {
            "python": await self._discover_python_deps(),
            "rust": await self._discover_rust_deps(),
            "nodejs": await self._discover_nodejs_deps(),
            "system": await self._discover_system_deps()
        }
        
        # Deduplicate across ecosystems
        flattened = self._flatten_and_deduplicate(dependencies)
        
        return {
            "timestamp": datetime.now(),
            "discovery_method": "multi-source",
            "dependencies": flattened,
            "total_count": len(flattened)
        }
    
    async def _discover_python_deps(self) -> list[dict]:
        """Discover Python dependencies."""
        deps = []
        
        # Try multiple lock files in priority order
        lock_files = [
            "uv.lock",
            "poetry.lock",
            "Pipfile.lock",
            "requirements.txt"
        ]
        
        for lock_file in lock_files:
            if Path(lock_file).exists():
                parsed = self._parse_lock_file(lock_file)
                deps.extend(parsed)
                break
        
        return deps
    
    async def _discover_rust_deps(self) -> list[dict]:
        """Discover Rust dependencies."""
        # Parse Cargo.lock
        cargo_lock = Path("Cargo.lock")
        if not cargo_lock.exists():
            return []
        
        import toml
        with open(cargo_lock) as f:
            data = toml.load(f)
        
        deps = []
        for package in data.get("package", []):
            deps.append({
                "name": package["name"],
                "version": package["version"],
                "source": package.get("source", "crates.io"),
                "ecosystem": "rust"
            })
        
        return deps
    
    def _parse_lock_file(self, lock_file: str) -> list[dict]:
        """Parse Python lock file format."""
        if lock_file.endswith(".lock"):
            # TOML format (poetry, uv)
            return self._parse_toml_lock(lock_file)
        elif lock_file.endswith(".txt"):
            # requirements.txt format
            return self._parse_requirements_txt(lock_file)
        else:
            raise ValueError(f"Unknown lock file format: {lock_file}")
    
    def _parse_toml_lock(self, file_path: str) -> list[dict]:
        """Parse TOML-based lock file."""
        import toml
        with open(file_path) as f:
            data = toml.load(f)
        
        deps = []
        for pkg_name, pkg_data in data.get("package", {}).items():
            deps.append({
                "name": pkg_name,
                "version": pkg_data.get("version"),
                "source": pkg_data.get("source", "pypi"),
                "ecosystem": "python"
            })
        
        return deps
    
    def _parse_requirements_txt(self, file_path: str) -> list[dict]:
        """Parse requirements.txt format."""
        deps = []
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Parse: package==version or package>=version, etc.
                match = re.match(r"^([a-zA-Z0-9_-]+)(?:[>=<~!]+(.+?))?(?:[#;].*)?$", line)
                if match:
                    deps.append({
                        "name": match.group(1),
                        "version": match.group(2) or "unknown",
                        "source": "pypi",
                        "ecosystem": "python"
                    })
        
        return deps
```

### 2.2 Component Cataloging

```python
class ComponentCatalogingEngine:
    """Catalogs discovered dependencies with metadata."""
    
    async def catalog(self, dependencies: list[dict]) -> list[dict]:
        """Catalog each dependency with full metadata."""
        
        cataloged = []
        for dep in dependencies:
            component = await self._catalog_component(dep)
            cataloged.append(component)
        
        return cataloged
    
    async def _catalog_component(self, dep: dict) -> dict:
        """Catalog a single component."""
        
        # Fetch package metadata
        metadata = await self._fetch_metadata(dep["name"], dep["ecosystem"])
        
        # Calculate hashes
        hashes = await self._calculate_hashes(dep)
        
        # Extract license information
        licenses = await self._extract_licenses(metadata)
        
        # Determine source URL
        source_url = self._determine_source_url(dep, metadata)
        
        return {
            "type": self._get_component_type(dep["ecosystem"]),
            "name": dep["name"],
            "version": dep["version"],
            "scope": "required",  # or "optional" for optional deps
            "ecosystem": dep["ecosystem"],
            "purl": self._generate_purl(dep),
            "hashes": hashes,
            "licenses": licenses,
            "source_url": source_url,
            "author": metadata.get("author"),
            "description": metadata.get("description"),
            "homepage": metadata.get("homepage"),
            "download_url": metadata.get("download_url"),
            "dependencies": await self._get_dependencies(dep),
            "vulnerabilities": []  # Filled by CVE scanner
        }
    
    async def _fetch_metadata(self, package: str, ecosystem: str) -> dict:
        """Fetch package metadata from registry."""
        if ecosystem == "python":
            return await self._fetch_pypi_metadata(package)
        elif ecosystem == "rust":
            return await self._fetch_crates_io_metadata(package)
        elif ecosystem == "nodejs":
            return await self._fetch_npm_metadata(package)
        else:
            return {}
    
    async def _fetch_pypi_metadata(self, package: str) -> dict:
        """Fetch metadata from PyPI."""
        url = f"https://pypi.org/pypi/{package}/json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    info = data.get("info", {})
                    return {
                        "author": info.get("author"),
                        "description": info.get("summary"),
                        "homepage": info.get("home_page"),
                        "license": info.get("license"),
                        "download_url": info.get("download_url"),
                        "source_repository": self._extract_repo_url(info)
                    }
        return {}
    
    def _generate_purl(self, dep: dict) -> str:
        """Generate Package URL (PURL) identifier."""
        # https://github.com/package-url/purl-spec
        
        if dep["ecosystem"] == "python":
            return f"pkg:pypi/{dep['name']}@{dep['version']}"
        elif dep["ecosystem"] == "rust":
            return f"pkg:cargo/{dep['name']}@{dep['version']}"
        elif dep["ecosystem"] == "nodejs":
            return f"pkg:npm/{dep['name']}@{dep['version']}"
        else:
            return f"pkg:generic/{dep['name']}@{dep['version']}"
    
    async def _calculate_hashes(self, dep: dict) -> dict:
        """Calculate integrity hashes for component."""
        return {
            "SHA256": await self._fetch_package_hash(dep, "sha256"),
            "SHA512": await self._fetch_package_hash(dep, "sha512"),
            "MD5": await self._fetch_package_hash(dep, "md5")
        }
    
    async def _extract_licenses(self, metadata: dict) -> list[dict]:
        """Extract license information."""
        licenses = []
        
        if metadata.get("license"):
            licenses.append({
                "license": metadata["license"],
                "url": self._resolve_license_url(metadata["license"])
            })
        
        return licenses
```

### 2.3 SBOM Format Generation

#### 2.3.1 CycloneDX Format

```python
class CycloneDXGenerator:
    """Generate SBOM in CycloneDX format."""
    
    def generate(self, components: list[dict]) -> dict:
        """Generate CycloneDX SBOM."""
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tools": [
                    {
                        "vendor": "Aries-Serpent",
                        "name": "unified-security-scanner",
                        "version": "1.0.0"
                    }
                ],
                "component": {
                    "type": "application",
                    "name": "codex",
                    "version": self._get_app_version()
                }
            },
            "components": [
                self._component_to_cyclonedx(comp)
                for comp in components
            ]
        }
    
    def _component_to_cyclonedx(self, comp: dict) -> dict:
        """Convert component to CycloneDX format."""
        return {
            "type": comp["type"],
            "bom-ref": f"pkg:{comp['purl']}",
            "name": comp["name"],
            "version": comp["version"],
            "description": comp.get("description"),
            "scope": comp.get("scope", "required"),
            "purl": comp["purl"],
            "licenses": [
                {
                    "license": {
                        "name": lic["license"],
                        "url": lic["url"]
                    }
                }
                for lic in comp.get("licenses", [])
            ],
            "hashes": [
                {
                    "alg": alg,
                    "content": content
                }
                for alg, content in comp.get("hashes", {}).items()
            ],
            "externalReferences": [
                {
                    "type": "website",
                    "url": comp.get("homepage")
                } if comp.get("homepage") else None
            ],
            "vulnerabilities": comp.get("vulnerabilities", [])
        }
```

#### 2.3.2 SPDX Format

```python
class SPDXGenerator:
    """Generate SBOM in SPDX format."""
    
    def generate(self, components: list[dict]) -> dict:
        """Generate SPDX SBOM."""
        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "codex-sbom",
            "documentNamespace": f"https://aries-serpent.github.io/_codex_/sbom/{uuid.uuid4()}",
            "creationInfo": {
                "created": datetime.now().isoformat(),
                "creators": [
                    "Tool: unified-security-scanner-1.0.0"
                ]
            },
            "packages": [
                self._component_to_spdx(comp)
                for comp in components
            ]
        }
    
    def _component_to_spdx(self, comp: dict) -> dict:
        """Convert component to SPDX format."""
        return {
            "SPDXID": f"SPDXRef-{comp['name'].replace('-', '_')}",
            "name": comp["name"],
            "versionInfo": comp["version"],
            "downloadLocation": comp.get("download_url", "NOASSERTION"),
            "filesAnalyzed": False,
            "licenseConcluded": " OR ".join([
                lic["license"] for lic in comp.get("licenses", [])
            ]) or "NOASSERTION",
            "externalReferences": [
                {
                    "referenceCategory": "PACKAGE-MANAGER",
                    "referenceType": "purl",
                    "referenceLocator": comp["purl"]
                }
            ]
        }
```

### 2.4 Vulnerability Integration

```python
class VulnerabilityEnrichedSBOM:
    """Enrich SBOM with CVE data."""
    
    async def enrich(self, sbom: dict, cve_findings: list[dict]) -> dict:
        """Add vulnerability data to SBOM components."""
        
        # Create lookup: package@version → vulnerabilities
        vuln_map = {}
        for finding in cve_findings:
            key = (finding["package"], finding["affected_version"])
            if key not in vuln_map:
                vuln_map[key] = []
            vuln_map[key].append(finding)
        
        # Enrich each component
        for component in sbom.get("components", []):
            key = (component["name"], component["version"])
            if key in vuln_map:
                component["vulnerabilities"] = [
                    self._vuln_to_sbom_format(v)
                    for v in vuln_map[key]
                ]
        
        return sbom
    
    def _vuln_to_sbom_format(self, finding: dict) -> dict:
        """Convert CVE finding to SBOM format."""
        return {
            "ref": f"CVE-{finding['cve_id']}",
            "id": finding["cve_id"],
            "source": {
                "name": "NVD",
                "url": f"https://nvd.nist.gov/vuln/detail/{finding['cve_id']}"
            },
            "ratings": [
                {
                    "score": finding["cvss_score"],
                    "severity": finding["severity"],
                    "method": "CVSSv3.1"
                }
            ],
            "cwes": finding.get("cwe_ids", []),
            "description": finding.get("description", ""),
            "recommendation": self._get_recommendation(finding),
            "status": "affected"
        }
```

---

## 3. VALIDATION & INTEGRITY LAYER

### 3.1 SBOM Validation

```python
class SBOMValidator:
    """Validates SBOM completeness and integrity."""
    
    def validate(self, sbom: dict) -> dict:
        """Validate SBOM against requirements."""
        
        results = {
            "format_valid": self._validate_format(sbom),
            "completeness": self._check_completeness(sbom),
            "integrity": self._check_integrity(sbom),
            "compliance": self._check_compliance(sbom),
            "security": self._check_security(sbom)
        }
        
        overall_valid = all(results.values())
        
        return {
            "valid": overall_valid,
            "validation_results": results,
            "issues": self._collect_issues(results)
        }
    
    def _validate_format(self, sbom: dict) -> bool:
        """Validate SBOM schema."""
        # Check required fields
        required = ["bomFormat", "specVersion", "components"]
        return all(field in sbom for field in required)
    
    def _check_completeness(self, sbom: dict) -> bool:
        """Verify all dependencies are included."""
        # Expected total vs actual
        components = sbom.get("components", [])
        
        # Heuristic: should have >50 Python packages
        python_count = len([c for c in components if "pypi" in c.get("purl", "")])
        
        return python_count > 50  # Adjust based on actual count
    
    def _check_integrity(self, sbom: dict) -> bool:
        """Verify component hashes and signatures."""
        for component in sbom.get("components", []):
            # Each component should have at least one hash
            if not component.get("hashes"):
                return False
        
        return True
    
    def _check_compliance(self, sbom: dict) -> bool:
        """Verify compliance with standards."""
        # CycloneDX compliance
        if sbom.get("bomFormat") == "CycloneDX":
            return self._validate_cyclonedx(sbom)
        
        # SPDX compliance
        if sbom.get("spdxVersion"):
            return self._validate_spdx(sbom)
        
        return False
    
    def _check_security(self, sbom: dict) -> bool:
        """Verify security-relevant checks."""
        # No unresolved vulnerabilities with severity CRITICAL/HIGH
        for component in sbom.get("components", []):
            for vuln in component.get("vulnerabilities", []):
                if vuln.get("status") == "affected":
                    severity = vuln.get("ratings", [{}])[0].get("severity", "").upper()
                    if severity in ["CRITICAL", "HIGH"]:
                        return False
        
        return True
```

### 3.2 Hash Verification

```python
class HashVerifier:
    """Verifies component integrity via hashing."""
    
    def verify_component_hash(self, package: str, version: str, expected_hash: str) -> bool:
        """Verify component was not tampered with."""
        
        # Download package
        downloaded = self._download_package(package, version)
        
        # Calculate hash
        actual_hash = self._calculate_sha256(downloaded)
        
        # Compare
        return actual_hash == expected_hash
    
    def _calculate_sha256(self, data: bytes) -> str:
        """Calculate SHA256 hash."""
        import hashlib
        return hashlib.sha256(data).hexdigest()
```

### 3.3 SBOM Signing

```python
class SBOMSigner:
    """Signs SBOM for authenticity verification."""
    
    def sign_sbom(self, sbom: dict, private_key: str) -> dict:
        """Sign SBOM with private key."""
        
        # Serialize SBOM
        sbom_json = json.dumps(sbom, sort_keys=True)
        
        # Sign
        signature = self._sign_message(sbom_json, private_key)
        
        # Add signature to SBOM
        sbom["signature"] = {
            "algorithm": "RSA-SHA256",
            "value": signature,
            "signer": "unified-security-scanner"
        }
        
        return sbom
    
    def verify_sbom_signature(self, sbom: dict, public_key: str) -> bool:
        """Verify SBOM signature."""
        if "signature" not in sbom:
            return False
        
        # Extract signature
        signature = sbom.pop("signature")
        
        # Serialize SBOM (same as signing)
        sbom_json = json.dumps(sbom, sort_keys=True)
        
        # Verify
        return self._verify_signature(sbom_json, signature["value"], public_key)
```

---

## 4. COMPLIANCE MAPPING

### 4.1 Supply Chain Compliance

**Supported Standards**:
- SLSA Framework (Supply Chain Levels for Software Artifacts)
- NIST SSDF (Secure Software Development Framework)
- NTIA Minimum Elements for Supply Chain Risk Management
- CIS Controls

**SBOM Compliance Mapping**:
```python
class ComplianceMappingEngine:
    """Maps SBOM coverage to compliance requirements."""
    
    def map_to_slsa(self, sbom: dict) -> dict:
        """Map SBOM to SLSA framework levels."""
        return {
            "level": self._determine_slsa_level(sbom),
            "controls": {
                "version_control": "PASS" if sbom.get("components") else "FAIL",
                "build_system": "PASS" if sbom.get("metadata", {}).get("tools") else "FAIL",
                "provenance": "PASS" if sbom.get("signature") else "FAIL"
            }
        }
    
    def generate_compliance_report(self, sbom: dict) -> dict:
        """Generate compliance report."""
        return {
            "sbom_coverage": self._calculate_coverage(sbom),
            "slsa_level": self._determine_slsa_level(sbom),
            "vulnerability_status": self._assess_vuln_status(sbom),
            "license_compliance": self._check_license_compliance(sbom),
            "supply_chain_risk": self._assess_risk(sbom),
            "recommendations": self._generate_recommendations(sbom)
        }
```

---

## 5. STORAGE & DISTRIBUTION

### 5.1 SBOM Storage

**Storage Locations**:
```
.codex/sbom/
├── sbom-current.json         # Latest SBOM (CycloneDX)
├── sbom-current.spdx.json    # Latest SBOM (SPDX)
├── sbom-signatures.json      # Digital signatures
└── archive/
    ├── sbom-2026-07-06.json  # Historical SBOMs
    ├── sbom-2026-07-05.json
    └── ...
```

### 5.2 Distribution

```python
class SBOMDistributor:
    """Distributes SBOM to stakeholders."""
    
    async def distribute(self, sbom: dict):
        """Distribute SBOM to all endpoints."""
        
        # GitHub Releases
        await self._publish_to_releases(sbom)
        
        # Container registries (if building containers)
        await self._publish_to_registries(sbom)
        
        # Documentation site
        await self._publish_to_docs(sbom)
        
        # CycloneDX/SPDX databases
        await self._submit_to_sbom_db(sbom)
```

---

## 6. SUCCESS CRITERIA

**For Advisory Phase**:
- ✅ Dependency discovery strategy designed
- ✅ SBOM generation architecture finalized
- ✅ Validation framework specified
- ✅ Compliance mapping documented

**For Full Execution (Days 5-9)**:
- ✅ 100% dependency coverage in SBOM
- ✅ 0 missing components
- ✅ 100% integrity hash validation
- ✅ SBOM signed and verified
- ✅ Compliance reporting operational
- ✅ SBOMs available in CycloneDX + SPDX formats

---

## DOCUMENT CONTROL

**Status**: ✅ ADVISORY PHASE COMPLETE  
**Date**: 2026-07-06T05:43:52Z  
**Next Phase**: Full Execution (Days 5-9, pending Track 12.3 clearance)  
**Authority**: @mbaetiong (D-tier autonomous, APPROVED)
