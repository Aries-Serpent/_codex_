# Doc-Test-Scribe Action with Security Scan & HTML Index

AI-powered GitHub Action that generates documentation, tests, and security reports with a comprehensive HTML index. Automatically creates @copilot PRs for review.

## Features

- 📚 **Documentation Generation**: Auto-generate docs from code using TF-IDF analysis
- ✅ **Test Generation**: Create comprehensive tests targeting specific coverage goals
- 🔒 **Security Scanning**: Integrated Bandit, Safety, and Semgrep scans
- 🌐 **HTML Index**: Beautiful, searchable documentation index with navigation
- 🤖 **Auto PR Creation**: Creates PRs and tags @copilot for review
- 📊 **Coverage Tracking**: Monitors and reports test coverage
- 🔍 **Semantic Analysis**: Uses TF-IDF for intelligent code understanding

## Usage

### Basic Usage

```yaml
- name: Generate Docs and Tests
  uses: ./.github/actions/doc-test-scribe-action
  with:
    target_path: 'src/codex/rag/'
    mode: 'full'
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Complete Example

```yaml
name: Doc-Test-Scribe Automation

on:
  push:
    paths:
      - 'src/**/*.py'
  workflow_dispatch:
    inputs:
      target:
        description: 'Target path to process'
        required: true
        default: 'src/'

jobs:
  generate-docs-tests:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Run Doc-Test-Scribe with Security Scan
        uses: ./.github/actions/doc-test-scribe-action
        with:
          mode: 'full'
          target_path: ${{ github.event.inputs.target || 'src/' }}
          coverage_target: '90'
          doc_style: 'google'
          generate_html_index: 'true'
          run_security_scan: 'true'
          create_pr: 'true'
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `mode` | Operation mode: `document`, `test`, `both`, `security`, `full`, `index` | No | `full` |
| `target_path` | Target file or directory to process | Yes | - |
| `coverage_target` | Target test coverage percentage | No | `90` |
| `doc_style` | Documentation style: `google`, `numpy`, `sphinx` | No | `google` |
| `generate_html_index` | Generate comprehensive HTML index | No | `true` |
| `run_security_scan` | Run security scans (CodeQL, Bandit, Semgrep) | No | `true` |
| `create_pr` | Create a PR with changes | No | `true` |
| `pr_branch_prefix` | Prefix for PR branch name | No | `scribe-agent` |
| `github_token` | GitHub token for API access and PR creation | Yes | - |

## Outputs

| Output | Description |
|--------|-------------|
| `docs_generated` | Whether documentation was generated |
| `tests_generated` | Whether tests were generated |
| `html_index_generated` | Whether HTML index was generated |
| `security_scan_passed` | Whether security scan passed |
| `coverage_achieved` | Test coverage percentage achieved |
| `pr_number` | PR number if created |
| `pr_url` | PR URL if created |
| `vulnerabilities_found` | Number of vulnerabilities found |

## Operation Modes

### `document`
Generates documentation only.

```yaml
with:
  mode: 'document'
  target_path: 'src/codex/rag/embeddings.py'
  doc_style: 'google'
```

### `test`
Generates tests only.

```yaml
with:
  mode: 'test'
  target_path: 'src/codex/rag/'
  coverage_target: '95'
```

### `both`
Generates both documentation and tests.

```yaml
with:
  mode: 'both'
  target_path: 'src/codex/'
```

### `security`
Runs security scans only.

```yaml
with:
  mode: 'security'
  target_path: 'src/'
  run_security_scan: 'true'
```

### `index`
Generates HTML index only.

```yaml
with:
  mode: 'index'
  target_path: 'docs/'
  generate_html_index: 'true'
```

### `full` (default)
Runs everything: docs, tests, security scan, and HTML index.

```yaml
with:
  mode: 'full'
  target_path: 'src/codex/rag/'
```

## HTML Index Features

The generated HTML index (`docs/html/index.html`) provides:

### 🔍 Search Functionality
- Real-time search across all documentation
- Filter by file type, module, or content
- Instant results with highlighting

### 📊 Statistics Dashboard
- Total files indexed
- Module count
- Test count
- Coverage percentage

### 🧭 Navigation Tree
- Hierarchical navigation
- Quick jump to sections
- Active section highlighting

### 📁 File Catalog
- Complete listing of all files
- File metadata (type, path, coverage)
- Color-coded file types
- Status badges (coverage, security)

### 🔒 Security Reports
- Integrated security scan results
- Vulnerability listings
- Direct links to detailed reports

### 📈 Coverage Visualization
- Test coverage metrics
- Coverage reports accessible via index
- Per-module coverage breakdown

## Security Scanning

The action integrates three security tools:

### Bandit
Python security linter that scans for common security issues.

**Reports**: `security-reports/bandit-report.txt`

### Safety
Dependency vulnerability scanner checking for known CVEs.

**Reports**: `security-reports/safety-report.json`

### Semgrep
Static analysis tool for finding bugs and security issues.

**Reports**: `security-reports/semgrep-report.json`

## Generated PR Structure

When `create_pr: true`, the action creates a PR with:

### PR Title
```
🤖 [Doc-Test-Scribe] Auto-generate for `target_path`
```

### PR Body Includes
- **Summary Table**: Results for each task
- **HTML Index Link**: Direct link to generated index
- **Security Scan Details**: Vulnerabilities found and reports
- **Changes Made**: List of generated files
- **Review Instructions**: Guidance for @copilot
- **Related Links**: Links to scribe agent, action, and commit

### PR Labels
- `automated`
- `scribe-agent`
- `documentation`
- `tests`
- `html-index`
- `security` (if vulnerabilities found)

## Directory Structure

After running the action, your repository will have:

```
.
├── docs/
│   ├── api/                    # API documentation
│   ├── modules/                # Module documentation
│   └── html/
│       ├── index.html          # Comprehensive HTML index
│       ├── security/           # Security reports (HTML accessible)
│       └── coverage/           # Coverage reports (HTML accessible)
├── tests/
│   └── test_*.py               # Generated tests
└── security-reports/
    ├── bandit-report.txt       # Bandit findings
    ├── bandit-report.json
    ├── safety-report.json      # Safety findings
    └── semgrep-report.json     # Semgrep findings
```

## Integration with Doc-Test-Scribe Agent

This action integrates with the `doc-test-scribe` agent:

**Agent Location**: `.github/agents/doc-test-scribe/`

The action uses:
- `tools/analyzer.py` - TF-IDF code analysis
- `tools/quantum_tokenizer.py` - Advanced tokenization
- `agent.yml` - Agent configuration

## Workflow Examples

### Auto-Generate on File Changes

```yaml
name: Auto Doc-Test on Changes

on:
  push:
    paths:
      - 'src/**/*.py'

jobs:
  auto-generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate Docs and Tests
        uses: ./.github/actions/doc-test-scribe-action
        with:
          mode: 'full'
          target_path: 'src/'
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Manual Trigger with Custom Target

```yaml
name: Manual Doc-Test Generation

on:
  workflow_dispatch:
    inputs:
      target:
        description: 'Target path'
        required: true
      mode:
        description: 'Operation mode'
        required: true
        type: choice
        options:
          - document
          - test
          - both
          - security
          - full
          - index

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Scribe Agent
        uses: ./.github/actions/doc-test-scribe-action
        with:
          mode: ${{ github.event.inputs.mode }}
          target_path: ${{ github.event.inputs.target }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Security Scan on Schedule

```yaml
name: Weekly Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Security Scan
        uses: ./.github/actions/doc-test-scribe-action
        with:
          mode: 'security'
          target_path: 'src/'
          run_security_scan: 'true'
          create_pr: 'true'
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### Action Fails with "Target path does not exist"

**Cause**: The specified `target_path` doesn't exist in the repository.

**Solution**: Verify the path and ensure it exists:
```bash
ls -la src/codex/rag/
```

### No PR Created

**Cause**: Either `create_pr: false` or no changes were generated.

**Solution**: Check action outputs and ensure there are changes to commit.

### Security Scan Fails

**Cause**: Security tools not installed or configuration issues.

**Solution**: The action auto-installs tools, but ensure pip and Python are available.

### HTML Index Not Generated

**Cause**: `generate_html_index: false` or documentation generation failed.

**Solution**: Set `generate_html_index: true` and check logs for errors.

## Best Practices

### 1. Use Appropriate Modes

- `document` - When only docs are needed
- `test` - When focusing on test coverage
- `full` - For comprehensive updates
- `index` - After manual documentation changes

### 2. Set Realistic Coverage Targets

```yaml
coverage_target: '90'  # Good for new modules
coverage_target: '70'  # Realistic for legacy code
coverage_target: '95'  # Strict for critical modules
```

### 3. Review Generated Content

Always review generated docs and tests before merging. The @copilot tag ensures review.

### 4. Monitor Security Scans

Address security vulnerabilities promptly. Set `run_security_scan: true` for production code.

### 5. Deploy HTML Index

Deploy the HTML index to GitHub Pages for easy access:

```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs/html
```

## Related Documentation

- **Scribe Agent**: [.github/agents/doc-test-scribe/](../agents/doc-test-scribe/)
- **Testing Conventions**: [TESTING_CONVENTIONS.md](/TESTING_CONVENTIONS.md)
- **Custom Actions**: [.github/actions/setup-python-cached/](../setup-python-cached/)

## Contributing

When contributing to this action:

1. Test with various `mode` values
2. Verify HTML index generation
3. Ensure security scans run correctly
4. Test PR creation and @copilot tagging
5. Update this README with new features

## License

Part of the Codex project. See repository LICENSE for details.

---

**Generated by**: Codex Automation  
**Maintained by**: AI Agent (@copilot) + Human Admin  
**Last Updated**: 2026-01-17
