**Question 1 (Critical): Off-Limits Files & Folders**
Answer with patterns:
- Production code: src/codex_ml/, src/codex/, src/training/, src/tokenization/
- Package metadata: pyproject.toml, setup.py, MANIFEST.in (all at root)
- System: .git/, .github/, .gitignore, .env*, .pre-commit-config.yaml
- Data/Models: data/, models/, torch/, transformers/ (loaded dependencies)
- Infrastructure: Dockerfile*, docker-compose*.yml, docker/, deploy/
- Testing: tests/, noxfile.py, pytest.ini, conftest.py, tox.ini
- Core configs: requirements*.txt, .codex/, .venv/

**Question 2 (Critical): Archival Location & Convention**
Recommend based on existing structure:
- Location: `.archived/<YYYY-MM-DD>-<component>/`
- Structure: manifest.json, checksum.sha256, metadata.json, README.md, files/
- Example: `.archived/2025-10-24-root-files-migration/`
- Reasoning: Mirrors existing .codex/ structure; append-only JSONL in .codex/evidence/

**Question 3 (High): Testing Requirements**
Based on AGENTS.md and current state:
- Minimum: pre-commit all hooks + PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
- Recommended: Add smoke tests in tests/test_smoke.py if CI unavailable
- Note: pytest_cov missing; recommend installing before full coverage gates

**Question 4 (High): Reviewers & Approvers**
Propose CODEOWNERS by category:
- Documentation: @docs-lead @mbaetiong
- Scripts/Tools: @automation-lead @mbaetiong
- Archive/Policy: @compliance-officer
- Default: @mbaetiong (primary)

**Question 5 (Medium): Root-Only Files**
Must stay at root:
- pyproject.toml, setup.py, MANIFEST.in (Python packaging)
- LICENSE (legal)
- .gitignore, .git* (git)
- Dockerfile*, docker-compose.yml (default build)
- README.md (GitHub display)
- Can move with updates: requirements*.txt → requirements/

**Question 6 (Medium): Content-Preserving Moves**
Recommend: Strategy B (Archive Backup + git mv)
- Phase 1: Create .archived/ backup (separate commit)
- Phase 2: git mv to new location (preserves history)
- Benefit: Full history + recovery capability

**Question 7 (Low): Timeline/Cadence**
Recommend: Atomic Incremental (3-5 PRs, 2-3 weeks)
- PR 1: Documentation (1-2 days)
- PR 2: Configuration (1 day)
- PR 3: Scripts/Tools (1-2 days)
- PR 4: Deployment (1 day)
- PR 5: Cleanup & Summary (1 day)