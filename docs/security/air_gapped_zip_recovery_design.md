# Air-Gapped ZIP Recovery & Encryption Split Design

**Last Updated:** 2026-09-13  
**Status:** Design spec ready for implementation on branch `copilot/develop-air-gapped-key-gen-app`

## 1. Goal and design principle

This project is a recovery-first ZIP password validation system, not a hidden-key derivation engine.

The decryption workflow must operate as follows:

1. Collect archive metadata and recovery clues.
2. Generate a bounded candidate set from wordlists, masks, clues, and mutation rules.
3. Rank candidates with a transparent heuristic.
4. Validate each candidate against the real ZIP archive and real member data.
5. Only unlock and unpack after successful validation.
6. Keep all operations local and air-gapped.

This is deliberately separate from encryption packaging. The encryption path is a packaging concern that can optionally create encrypted archives, store local key material, and verify metadata integrity.

---

## 2. System boundaries

### 2.1 Decryption-first subsystem

The decryption-first stack is the main execution path for recovery tasks:

- `scripts/security/offline_zip_keymaster.py`
  - canonical CLI and library entry point
  - orchestrates recovery flow
- `scripts/security/zip_recovery_engine.py` (new)
  - candidate generation, queueing, ranking, validation loop
- `scripts/security/zip_archive_validator.py` (new)
  - archive structure checks; encryption/member validation
- `scripts/security/zip_safe_unpacker.py` (new)
  - safe extraction and self-titled output folder creation
- `scripts/security/zip_reporting.py` (new)
  - recovery results, stats, and sanitized logs
- `tests/security/test_offline_zip_keymaster.py`
  - functional validation for recovery and unpacking

### 2.2 Encryption-packaging subsystem

This subsystem remains separate and should be implemented as an optional companion layer:

- `scripts/security/token_encryption_tool.py`
  - local key-generation / token-manifest helpers
- `scripts/security/zip_key_manager.py` (new)
  - local key persistence, permissions, and manifest validation
- `scripts/security/zip_encryption_writer.py` (new)
  - packaged encrypted ZIP generation and local metadata signing
- `scripts/security/zip_bundle_verifier.py` (new)
  - verify encrypted archive metadata and payload integrity
- `src/offline_zip_keymaster/cli.py`
  - packaged interface entry point for library users
- `src/offline_zip_keymaster/_impl.py`
  - packaged implementation mirror, if distribution-level compatibility is required

### 2.3 Governance boundary

The encryption layer does not drive the recovery mechanism. Recovery is still performed by testing password candidates against the archive itself.

---

## 3. Module responsibilities

### 3.1 Recovery Engine

Responsibilities:

- load user clues and archive path
- build a `RecoveryPlan`
- initialize candidate queue
- generate dictionary, mask, rule, and variant candidates
- rank candidates with a scoring heuristic
- validate against real ZIP payloads
- stop on success or exhaustion

### 3.2 Archive Validation

Responsibilities:

- confirm archive is readable and structurally valid
- inspect file members and names
- detect whether encrypted payload is present
- confirm member payload is actually protected, not merely metadata-wrapped
- expose validation facts to the recovery engine

### 3.3 Local Key Manager

Responsibilities:

- create local key material securely
- store manifest and metadata in a local, air-gapped path
- enforce restrictive permissions (`0600` / `0700` as applicable)
- avoid any GitHub Secret or network dependency

### 3.4 Encrypted Archive Writer

Responsibilities:

- generate encrypted ZIP bundles
- sign metadata using local HMAC where required
- store the bundle in a controlled archive path
- support packaging for offline use

### 3.5 Safe Unpacker

Responsibilities:

- derive output directory from archive stem
- create `./output/<archive_stem>/`
- validate canonical paths before extraction
- reject absolute paths, traversal attempts, duplicate targets, and suspicious members
- enforce size caps and safe permissioning

### 3.6 Reporting Layer

Responsibilities:

- sanitized summary output
- JSON/text recovery reports
- candidate trace: source, ranking, tested / failed / passed
- success/failure reasons without leaking secrets or raw key bytes

---

## 4. Data contracts

### 4.1 RecoveryPlan

```python
@dataclass(frozen=True)
class RecoveryPlan:
    archive_path: Path
    archive_stem: str
    seed: str | None
    hints: tuple[str, ...]
    wordlist_paths: tuple[Path, ...]
    candidate_file: Path | None
    mask: str | None
    charset: str
    min_length: int
    max_length: int
    brute_force: bool
    rules: tuple[str, ...]
    max_candidates: int
    max_attempts: int
    report_path: Path | None
```

Required invariants:

- `archive_path` must exist and be readable.
- `max_candidates` and `max_attempts` must be bounded.
- `mask` and `charset` are optional but must be consistent with the configured search budget.
- `archive_stem` is derived from the ZIP stem and is used for candidate context and output folder naming.

### 4.2 CandidateRecord

```python
@dataclass(frozen=True)
class CandidateRecord:
    value: str
    source: str  # wordlist, mask, rule, seed, archive_stem, custom, brute_force
    score: float
    stage: str   # exact, mutation, combinator, mask, brute_force
    tried: bool = False
    success: bool = False
    reason: str | None = None
```

### 4.3 ArchiveProbe

```python
@dataclass(frozen=True)
class ArchiveProbe:
    path: Path
    is_valid_zip: bool
    member_count: int
    encrypted_member_count: int
    names: tuple[str, ...]
    archive_stem: str
    detected_hints: tuple[str, ...]
    error: str | None = None
```

### 4.4 ValidationResult

```python
@dataclass(frozen=True)
class ValidationResult:
    candidate: str
    password_accepted: bool
    member_count_verified: int
    extraction_ok: bool
    error: str | None = None
```

### 4.5 UnpackOutcome

```python
@dataclass(frozen=True)
class UnpackOutcome:
    output_dir: Path
    members_written: int
    skipped_members: int
    traversal_blocks: int
    errors: tuple[str, ...]
```

### 4.6 BundleMetadata

```python
@dataclass(frozen=True)
class BundleMetadata:
    bundle_name: str
    archive_stem: str
    key_fingerprint: str
    created_at_utc: str
    integrity_hash: str
    manifest_version: str = "1.0"
```

---

## 5. Formula definitions

The ranking model is heuristic and must not be treated as proof of correctness.

### 5.1 Candidate priority score

Let:

- `c` = candidate string
- `s` = seed clue
- `a` = archive stem / archive-derived hints
- `w` = dictionary wordlist presence
- `m` = mask match
- `r` = rule-generated mutation signal
- `l` = leetspeak / symbol mutation factor
- `L` = length plausibility
- `n` = noise penalty
- `d` = duplicate penalty

Then a practical ranking function is:

```
priority(c) =
    3.0 * seed_match(c, s)
  + 2.5 * archive_match(c, a)
  + 2.0 * dictionary_match(c, w)
  + 1.8 * mask_match(c, m)
  + 1.5 * rule_match(c, r)
  + 1.2 * leet_score(c, l)
  + 1.0 * length_score(c, L)
  + 0.8 * entropy_score(c)
  - 3.0 * noise_penalty(c, n)
  - 2.0 * duplicate_penalty(c, d)
```

### 5.2 Feature mapping

- `seed_match`: candidate contains the seed, a stem fragment, or a transformed family member
- `archive_match`: candidate includes archive stem or context words such as `audit`, `log`, `vault`, `backup`
- `dictionary_match`: candidate is directly taken from a provided wordlist or clue file
- `mask_match`: candidate matches a probable pattern such as `?u?l?l?l?d?d` or `Password?d?d`
- `rule_match`: candidate was generated through a rule-based transformation layer
- `leet_score`: weighted for common substitutions such as `a→@`, `e→3`, `o→0`, `s→$`
- `length_score`: favors realistic lengths, but does not guarantee correctness
- `entropy_score`: small bonus for mixed case + digits + symbols
- `noise_penalty`: penalizes obvious junk like repeated single characters or nonsense strings
- `duplicate_penalty`: prevents re-testing or over-prioritizing duplicates

### 5.3 Physics-inspired interpretation

The earlier implementation style using a phase/amplitude/collapse probability is acceptable as a ranking heuristic, but only if it is explicitly named as a queue-priority model and not as a proof of correctness. It is best treated as a heuristic filter that orders the next candidate attempts.

Recommended rationale:

- ranking score answers “what should we try next?”
- validation result answers “did this candidate actually unlock the archive?”

The final proof is always the archive-validation result.

---

## 6. Candidate generation model

### 6.1 Candidate generation stages

1. Exact clue entries
   - archive stem
   - seed
   - direct wordlist entries
   - direct clue-file entries

2. Case and punctuation mutations
   - `Password`, `PASSWORD`, `password`
   - `password!`, `password_2026`, `password-2026`

3. Leetspeak and symbol variants
   - `P@$$w0rd`
   - `p@ssw0rd`
   - `P@ssw0rd!`
   - `Pa$$word`
   - `P@$$w0rd123`

4. Context combinations
   - `seed + archive_stem`
   - `archive_stem + seed`
   - `word + year`
   - `word + punctuation + year`

5. Mask expansions
   - `?u?l?l?l?d?d`
   - `Password?d?d`
   - `?u?l?l?l?l?d?d`

6. Bounded brute-force fallback
   - only after staged search is exhausted or configured to run under a cap

### 6.2 Candidate generation table

| Base word | Common variants to generate | Notes |
|---|---|---|
| `password` | `Password`, `PASSWORD`, `p@ssword`, `P@$$w0rd`, `p@$$w0rd`, `password123`, `Password123`, `password!`, `Password2026` | Highest-priority mutation family |
| `admin` | `Admin`, `ADMIN`, `@dmin`, `admin123`, `Admin123`, `admin!`, `admin2026` | Common credential family |
| `welcome` | `Welcome`, `WELCOME`, `w3lc0me`, `W3lc0me`, `welcome123`, `welcome!` | Common root word |
| `secret` | `Secret`, `SECRET`, `s3cret`, `S3cret`, `secret123`, `secret!` | High-value wordlist family |
| `letmein` | `LetMeIn`, `letmein123`, `L3tm31n`, `letmein!` | Common password pattern |
| `dragon` | `Dragon`, `DRAGON`, `dr4g0n`, `dragon123`, `Dragon!` | Common password family |
| `sunshine` | `Sunshine`, `SUNSHINE`, `sunsh1ne`, `sunshine123`, `sunshine!` | Common wordlist seed |
| `master` | `Master`, `MASTER`, `m@ster`, `master123`, `Master2026` | Common site/backup naming pattern |
| `login` | `Login`, `LOGIN`, `l0gin`, `login123`, `login!` | Frequently derived from archive names |
| `backup` | `Backup`, `BACKUP`, `b@ckup`, `backup123`, `Backup2026` | Relevant for archive contexts |
| `vault` | `Vault`, `VAULT`, `v@ult`, `vault123`, `Vault2026` | Common archive semantic term |
| `audit` | `Audit`, `AUDIT`, `@udit`, `audit123`, `audit2026` | Strong archive-name clue |
| `log` | `Log`, `LOG`, `l0g`, `log123`, `log2026` | Archive naming clue |
| `recovery` | `Recovery`, `RECOVERY`, `r3cov3ry`, `recovery123`, `recovery!` | Strong recovery-specific term |
| `archive` | `Archive`, `ARCHIVE`, `@rchive`, `archive123`, `archive2026` | Practical bundle naming clue |

Generation should be bounded by `max_candidates` and deduplicated before validation.

---

## 7. Recovery flow and implementation order

### Phase 1: Canonical contract

1. Define `RecoveryPlan` and the validation contracts.
2. Centralize CLI behavior in `scripts/security/offline_zip_keymaster.py`.
3. Ensure the CLI and library entry points share the same values and semantics.

### Phase 2: Archive inspection and clue building

1. Read archive path and derive `archive_stem`.
2. Open the zip and inspect members.
3. Record member names, entry count, and whether there are encrypted members.
4. Populate `ArchiveProbe` and `RecoveryPlan.hints`.

### Phase 3: Candidate generation

1. Add direct clues.
2. Add wordlist-derived clusters.
3. Add case and leet mutations.
4. Add seed + archive-stem combinations.
5. Add mask expansions.
6. Enforce dedupe and bounded generation.

### Phase 4: Ranked validation loop

1. Rank candidates by queue priority.
2. Validate each candidate against the ZIP.
3. Stop on the first success.
4. Log failure reasons and continue until the max budget is exhausted.

### Phase 5: Safe unpacking

1. Derive output directory from archive stem.
2. Validate every member path before writing.
3. Reject traversal and duplicate targets.
4. Extract to `./<archive_stem>/` only.

### Phase 6: Reporting and sanitization

1. Store JSON/text reports.
2. Emit sanitized stdout to avoid leaking raw passwords or key material.
3. Ensure the CLI only prints safe summaries.

### Phase 7: Encryption split implementation

1. Add `zip_key_manager.py` for local key lifecycle
2. Add `zip_encryption_writer.py` for archive packaging and metadata signing
3. Add `zip_bundle_verifier.py` for bundle verification and key validation
4. Keep encryption packaging isolated from recovery validation

---

## 8. Test matrix

| Area | File(s) | What to test | Expected outcome |
|---|---|---|---|
| Archive probe | `tests/security/test_offline_zip_keymaster.py` | valid ZIP, invalid ZIP, corrupted names | correct flags and error handling |
| Candidate generation | same | direct wordlist, archive stem, seed expansion, leetspeak, case mutation | bounded and deduped candidate set |
| Recovery ranking | same | ranking order with seed/hints | likely candidates are prioritized |
| Password validation | same | real ZIP with known password | password accepted only on actual archive read |
| Negative validation | same | wrong password and malformed archive | no false success |
| Self-titled unpack | same | archive named `audit_logs_2026.zip` unpacks to `./audit_logs_2026/` | exact output folder naming |
| Traversal protection | same | malicious names like `../../evil.txt` | rejected before writing |
| Duplicate target guard | same | repeated target names across members | duplicate names rejected |
| Size caps | same | oversized archive or file members | extraction aborted safely |
| Sanitization | same | logs with candidate words, keys, metadata | raw secret-like material not exposed |
| Encryption split | new tests | key manager permissions, bundle signing, verifier checks | packaging path remains isolated |

### Suggested pytest coverage goals

- `recover_archive_password` with real password-protected archive
- `generate_password_candidates` with wordlist + leet + seed + stem mixing
- `unpack_archive` with malicious path traversal attempt
- `safe_write` permission checks and canonicalization
- `mask` and `rule` generation under budgets
- `reporting/logging` sanitize outputs

---

## 9. Encryption split design

The encryption subsystem should be treated as a subcomponent, not a primary recovery engine.

### 9.1 Planned split

The split should preserve a clean boundary:

- Recovery subsystem: tries candidates against the archive.
- Encryption subsystem: creates and verifies packages using local key material.

### 9.2 Encryption module responsibilities

- `zip_key_manager.py`
  - generate key material locally
  - persist `.key` / manifest files under safe permissions
  - validate key material before archive creation or unpacking

- `zip_encryption_writer.py`
  - create the encrypted archive payload
  - produce local metadata signatures (HMAC or equivalent)
  - verify manifest structure before writing bundle

- `zip_bundle_verifier.py`
  - validate metadata bundle
  - verify file integrity and signing
  - reject corrupt or partially written bundles

### 9.3 Boundary rules

1. Recovery never depends on hidden key derivation.
2. Encryption does not perform candidate validation by itself.
3. Both systems may share a common local key model, but they must not blur into one subsystem.
4. The recovery engine remains the proving system for actual password success.
5. Encryption remains optional packaging logic for offline bundle creation.

---

## 10. Execution readiness

This design is ready to execute in the next Copilot session because it provides:

- exact module names
- a bounded architecture
- canonical data contracts
- explicit formula definitions
- a concrete generation table for real-world candidate families
- a phased implementation order
- a clear separation between recovery and encryption concerns
- direct testing hooks aligned with the repository’s existing security script and pytest layout

The next implementation step should focus on the recovery engine first, then the encryption split, then the reporting and safety layer.

---

## 11. Implementation recommendation

The first implementation milestone should be:

1. `RecoveryPlan`
2. `ArchiveProbe`
3. `generate_password_candidates()` mutation rules
4. `recover_archive_password()` validation loop
5. `safe_unpack_archive()` path enforcement
6. recovery reporting

Only after that should the encryption packaging components be filled in as a separate subsystem.
