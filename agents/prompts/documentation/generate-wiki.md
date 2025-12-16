# Generate Wiki and Documentation Bundle

## Purpose
Generate comprehensive wiki pages, documentation hub, and deployment bundles for GitHub Wiki and static documentation sites.

## Prerequisites
- Python 3.9+ installed
- Repository access
- GitHub Wiki enabled (for deployment)

## Commands

### 1. Generate Complete Wiki Bundle
```bash
cd /home/runner/work/_codex_/_codex_
python -m scripts.space_traversal.audit_runner wiki --output wiki_bundle.zip
```

### 2. Generate Documentation Hub
```bash
python -m scripts.space_traversal.audit_runner docs-hub --output docs_hub.html
```

### 3. Generate Individual Components

#### Agent Interface
```bash
python -m scripts.space_traversal.audit_runner agent-interface --output agent_interface.html
```

#### CLI Builder
```bash
python -c "
from scripts.space_traversal.viz_cli_builder import generate_cli_builder
from pathlib import Path
generate_cli_builder(Path('cli_builder.html'), repo_name='_codex_')
"
```

#### API Collection
```bash
python -c "
from scripts.space_traversal.viz_api_collection import generate_api_collection
from pathlib import Path
generate_api_collection(Path('api_collection.html'), repo_name='_codex_', version='1.5.5')
"
```

#### Swagger Documentation
```bash
python -c "
from scripts.space_traversal.viz_swagger import generate_swagger_docs
from pathlib import Path
generate_swagger_docs(Path('swagger.html'), repo_name='_codex_')
"
```

### 4. Deploy to GitHub Wiki
```bash
# Clone wiki repository
git clone https://github.com/Aries-Serpent/_codex_.wiki.git wiki_repo

# Extract wiki bundle
unzip wiki_bundle.zip -d wiki_repo/

# Commit and push
cd wiki_repo
git add .
git commit -m "docs: Update wiki from automated generation"
git push origin master
```

## Validation

1. **Check Generated Files**:
   ```bash
   ls -lh *.html wiki_bundle.zip
   ```

2. **Verify Bundle Contents**:
   ```bash
   unzip -l wiki_bundle.zip
   ```

3. **Test HTML Files**: Open in browser
   ```bash
   python -m http.server 8000
   # Visit http://localhost:8000/docs_hub.html
   ```

4. **Validate Wiki Deployment**: Visit GitHub Wiki page

## Expected Output

### Generated Files
```
agent_interface.html      # Interactive agent control panel
cli_builder.html          # CLI command builder
api_collection.html       # API reference collection
swagger.html              # Swagger/OpenAPI documentation
docs_hub.html             # Central documentation hub
wiki_bundle.zip           # Complete wiki deployment bundle
```

### Wiki Bundle Structure
```
wiki_bundle.zip
├── Home.md                    # Wiki home page
├── Quick-Start.md             # Quick start guide
├── Architecture.md            # Architecture overview
├── API-Reference.md           # API documentation
├── Configuration.md           # Configuration guide
├── Troubleshooting.md         # Troubleshooting guide
├── Agent-Guide.md             # AI Agent guide
├── images/                    # Diagrams and screenshots
└── _Sidebar.md               # Wiki sidebar navigation
```

### Documentation Hub Features
- 📊 **Interactive Dashboard**: Capability overview with charts
- 🔍 **Search Functionality**: Find documentation quickly
- 🤖 **Agent Integration**: Direct links to agent interfaces
- 📚 **API Reference**: Complete API documentation
- 🎨 **Responsive Design**: Works on desktop and mobile
- 🔗 **Cross-References**: Linked documentation structure

## Wiki Content Sections

### 1. Architecture Documentation
```markdown
# Architecture Overview

## System Components
- Audit Pipeline (v1.5.x)
- Trend Database (SQLite)
- Visualization Layer
- CI/CD Integration

## Data Flow
[Mermaid diagram here]
```

### 2. API Documentation
```markdown
# API Reference

## Audit Runner API
\```python
from scripts.space_traversal.audit_runner import run_audit
results = run_audit(output_dir=Path('./results'))
\```
```

### 3. Configuration Guide
```markdown
# Configuration

## Workflow Configuration
Edit `.copilot-space/workflow.yaml`:
\```yaml
version: "1.5.0"
capabilities: 39
\```
```

## Customization

### Custom Branding
```python
from scripts.space_traversal.viz_docs_hub import generate_docs_hub
from pathlib import Path

generate_docs_hub(
    Path('custom_docs.html'),
    repo_name='My Custom Repo',
    version='2.0.0'
)
```

### Additional Pages
```python
# Add custom wiki pages
custom_pages = {
    'Custom-Guide.md': custom_content,
    'Advanced-Topics.md': advanced_content,
}

# Generate with custom pages
python -m scripts.space_traversal.audit_runner wiki \
    --output wiki_bundle.zip \
    --custom-pages custom_pages.json
```

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Install dependencies
```bash
pip install -e .
```

### Issue: Wiki repository not found
**Solution**: Enable GitHub Wiki in repository settings
1. Go to repository Settings
2. Scroll to "Features"
3. Check "Wikis"
4. Initialize wiki with first page

### Issue: Large bundle size
**Solution**: Optimize images and content
```bash
# Compress images before bundling
find images/ -name "*.png" -exec pngcrush -ow {} \;
```

### Issue: Deployment fails
**Solution**: Check permissions
```bash
# Ensure GitHub token has wiki access
gh auth status
gh auth refresh -h github.com -s wiki
```

## Integration with GitHub Actions

Automate wiki generation on releases:

```yaml
name: Generate Wiki

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  generate-wiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Dependencies
        run: pip install -e .
      
      - name: Generate Wiki Bundle
        run: |
          python -m scripts.space_traversal.audit_runner wiki --output wiki_bundle.zip
      
      - name: Deploy to Wiki
        run: |
          git clone https://${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}.wiki.git wiki
          unzip wiki_bundle.zip -d wiki/
          cd wiki
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .
          git commit -m "docs: Update wiki (automated)" || echo "No changes"
          git push
      
      - name: Upload Bundle as Asset
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./wiki_bundle.zip
          asset_name: wiki-documentation-bundle.zip
          asset_content_type: application/zip
```

## Mermaid Diagram Integration

Wiki pages include Mermaid diagrams for visual documentation:

```markdown
## Architecture Diagram

\```mermaid
flowchart TB
    subgraph Pipeline["Audit Pipeline"]
        Runner[Audit Runner]
        DB[(SQLite DB)]
        Viz[Visualization]
    end
    
    subgraph Outputs["Outputs"]
        HTML[HTML Dashboard]
        Wiki[GitHub Wiki]
        Reports[Markdown Reports]
    end
    
    Runner --> DB
    Runner --> Viz
    Viz --> HTML
    Viz --> Wiki
    Viz --> Reports
\```
```

## Related Prompts
- [update-agents-md.md](update-agents-md.md) - Update AGENTS.md
- [generate-api-docs.md](generate-api-docs.md) - API documentation
- [deploy-github-pages.md](deploy-github-pages.md) - GitHub Pages deployment
