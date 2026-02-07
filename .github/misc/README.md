# Miscellaneous Workflows

This folder contains deprecated, experimental, low-usage, or utility workflows that are not part of the main CI/CD pipeline.

## Contents

### Phase 1 Moves (4 workflows)
- **aftermath.yml** - Deprecated workflow with empty triggers
- **flatten-repo-download.yml** - One-time repository flattening utility
- **zendesk-quantum-packaging.yml** - Experimental quantum packaging workflow
- **biweekly-research-digest.yml** - Low-priority research digest generator

### Phase 2 Week 3 Moves (7 workflows)
- **genesis-bootstrap.yml** - Genesis Protocol bootstrap template (rarely used)
- **monthly-model-retraining.yml** - Monthly model retraining (low frequency)
- **notebooklm-sync.yml** - NotebookLM synchronization utility
- **zendesk-knowledge-sync.yml** - Zendesk knowledge base sync utility
- **wiki-assemble.yml** - Wiki assembly and documentation generation
- **phase10-automated-secrets-setup.yml** - Phase 10 secrets setup utility
- **phase34-codeql-alert-fetch.yml** - Phase 3/4 CodeQL alert fetching

## Status

**Total**: 11 workflows
- **Phase 1**: 4 workflows (inactive/deprecated)
- **Phase 2 Week 3**: 7 workflows (low-usage utilities, still functional)

All workflows in misc/ remain **functional** and can be triggered manually or via schedule. They are moved here to reduce clutter in the main workflows directory while preserving their functionality.

## Restoration

All workflows can be restored to `.github/workflows/` if needed:
```bash
cp .github/misc/<workflow-name>.yml .github/workflows/
```

See individual `.meta` files for specific restoration instructions.

## Cleanup

Phase 1 workflows (deprecated) may be permanently deleted in a future cleanup phase. Phase 2 workflows remain functional and should not be deleted without review.
