# NotebookLM PRO Features Integration Guide

## 🌟 NotebookLM PRO Subscription Benefits

### Available PRO Features (as of 2026)

| Feature | Free Tier | PRO Tier |
|---------|-----------|----------|
| **Source Uploads** | 20 sources per notebook | Unlimited sources |
| **Source Size** | 500KB per source | 10MB per source |
| **Audio Overviews** | ❌ Not available | ✅ Up to 20min episodes |
| **Shared Notebooks** | ❌ Not available | ✅ Unlimited sharing |
| **Inline Citations** | Basic | ✅ Advanced with page numbers |
| **Export Formats** | ❌ Not available | ✅ PDF, DOCX, Markdown, HTML |
| **API Access** | ❌ Not available | ✅ Full API access |
| **Custom Voices** | ❌ Not available | ✅ Multiple voice styles |
| **Collaboration** | ❌ Not available | ✅ Real-time editing |
| **Version History** | ❌ Not available | ✅ 30-day history |
| **Priority Support** | ❌ Not available | ✅ 24/7 support |

## 🎙️ Audio Overview Generation (PRO)

### What It Does
Generates podcast-style audio summaries of your notebook sources with AI hosts discussing the content.

### Implementation

```python
from architect import ProjectArchitect

architect = ProjectArchitect(api_key="your_notebooklm_api_key")

# Generate 10-minute audio overview
audio_url = architect.nlm_api.generate_audio_overview(
    notebook_id="nb_abc123",
    duration="medium",  # short=5min, medium=10min, long=20min
)

print(f"Listen at: {audio_url}")
```

### CLI Usage

```bash
# Generate audio overview
python architect.py generate-audio \
  --notebook-id nb_abc123 \
  --api-key $NOTEBOOKLM_API_KEY \
  --duration long

# Output: 🎙️ Audio generated: https://notebooklm.google.com/audio/abc123.mp3
```

### Voice Styles (PRO)
- **Conversational**: Casual, engaging tone
- **Formal**: Professional, structured discussion
- **Technical**: Deep-dive with technical terminology
- **Educational**: Teaching-focused with explanations

### Use Cases
1. **Onboarding**: Generate audio intro for new team members
2. **Commute Learning**: Listen to project updates while driving
3. **Accessibility**: Provide audio version of documentation
4. **Executive Summaries**: Quick audio brief for stakeholders

## 🔗 Shared Notebooks (PRO)

### What It Does
Create shareable links to notebooks with customizable permissions.

### Implementation

```python
# Create shareable link
share_url = architect.nlm_api.create_shared_link(
    notebook_id="nb_abc123",
    permissions="view"  # view, comment, edit
)

print(f"Share with team: {share_url}")
```

### CLI Usage

```bash
# Create share link
python architect.py share \
  --notebook-id nb_abc123 \
  --permissions view \
  --api-key $NOTEBOOKLM_API_KEY

# Output: 🔗 Share URL: https://notebooklm.google.com/s/abc123
```

### Permission Levels
- **View**: Read-only access, can query AI
- **Comment**: Can add comments and suggestions
- **Edit**: Full editing rights, can add/remove sources

### Security Options (PRO)
- Password protection
- Expiration dates (7, 30, 90 days, never)
- IP whitelisting
- Domain restrictions

### Use Cases
1. **Client Reviews**: Share project documentation with clients
2. **Stakeholder Updates**: Give execs read-only access
3. **Team Collaboration**: Edit permissions for active contributors
4. **Public Documentation**: Share knowledge base publicly

## 📑 Inline Citations (PRO)

### What It Does
AI responses include precise citations with page/line numbers pointing to source documents.

### Implementation

```python
# Enable advanced citations
architect.nlm_api.add_inline_citations(
    notebook_id="nb_abc123",
    source_ids=["src_1", "src_2", "src_3"]
)
```

### Citation Styles (PRO)
- **Inline**: `[1: project_plan.md, p.5]`
- **Footnote**: Numbered footnotes at bottom
- **Endnote**: All citations at document end
- **Hover**: Tooltip with citation details

### Example Output

**Query**: "What are the key risks for Phase 2?"

**Response**:
```
The main risks for Phase 2 include:

1. Dependency conflicts with external libraries [1: architecture.md, line 45]
2. Potential performance bottlenecks in data processing [2: research.md, p.12]
3. Integration challenges with legacy systems [1: architecture.md, line 78]

Mitigation strategies have been documented [3: risk_analysis.md, section 2.3].
```

### Use Cases
1. **Research Verification**: Validate AI responses against sources
2. **Compliance**: Track information provenance for audits
3. **Academic Work**: Proper attribution for research
4. **Legal Review**: Evidence trail for decisions

## 📥 Export Formats (PRO)

### Available Formats
- **PDF**: Print-ready with formatting
- **DOCX**: Editable Microsoft Word
- **Markdown**: Plain text with formatting
- **HTML**: Web-ready with CSS

### Implementation

```python
# Export notebook
download_url = architect.nlm_api.export_notebook(
    notebook_id="nb_abc123",
    format="pdf"
)

# Download file
import requests
response = requests.get(download_url)
with open("project_docs.pdf", "wb") as f:
    f.write(response.content)
```

### CLI Usage

```bash
# Export as PDF
python architect.py export \
  --notebook-id nb_abc123 \
  --format pdf \
  --api-key $NOTEBOOKLM_API_KEY

# Output: 📥 Download: https://notebooklm.google.com/exports/abc123.pdf
```

### Use Cases
1. **Archiving**: Preserve project documentation
2. **Distribution**: Share formatted docs offline
3. **Integration**: Import into other tools
4. **Compliance**: Generate audit-ready reports

## 🔄 Complete Workflow with PRO Features

### Scenario: Launch New Project with Full PRO Integration

```bash
#!/bin/bash
# complete_project_setup.sh

# Step 1: Generate NotebookLM sources
python architect.py export-notebooklm \
  --project .codex/plans/new_project.yaml \
  --output .codex/artifacts/notebooklm/ \
  --api-key $NOTEBOOKLM_API_KEY \
  --upload \
  --generate-audio \
  --create-share-link

# This creates:
# - Notebook with all sources uploaded
# - Audio overview (10 min podcast)
# - Shareable link for team

# Step 2: Enable advanced citations
NOTEBOOK_ID=$(cat .codex/artifacts/notebooklm/notebook_id.txt)
python architect.py enable-citations \
  --notebook-id $NOTEBOOK_ID \
  --style inline \
  --api-key $NOTEBOOKLM_API_KEY

# Step 3: Share with stakeholders
python architect.py share \
  --notebook-id $NOTEBOOK_ID \
  --permissions view \
  --expires-in-days 30 \
  --api-key $NOTEBOOKLM_API_KEY

# Step 4: Export baseline documentation
python architect.py export \
  --notebook-id $NOTEBOOK_ID \
  --format pdf \
  --output docs/project_baseline.pdf \
  --api-key $NOTEBOOKLM_API_KEY

echo "✅ Project setup complete!"
echo "�� Notebook: https://notebooklm.google.com/n/$NOTEBOOK_ID"
echo "🎙️ Audio: Generated and available in notebook"
echo "🔗 Share: Link copied to clipboard"
```

## 🎯 PRO Feature Decision Tree

```
Start: Do you have NotebookLM PRO?
│
├─ NO → Use free tier
│   ├─ Generate sources locally
│   ├─ Upload manually (limit: 20 sources)
│   └─ Basic queries only
│
└─ YES → Use PRO features
    │
    ├─ Need audio? → generate_audio_overview()
    │
    ├─ Need sharing? → create_shared_link()
    │
    ├─ Need citations? → add_inline_citations()
    │
    ├─ Need export? → export_notebook()
    │
    └─ Need API automation? → Use full API integration
```

## 💡 Best Practices with PRO

### 1. Audio Overviews
- Generate for each major milestone
- Use "technical" voice for engineering docs
- Create "short" versions for quick updates
- Embed audio links in Notion/Slack

### 2. Shared Links
- Set expiration dates for security
- Use "view" permissions by default
- Create separate notebooks for different audiences
- Track usage via analytics (PRO dashboard)

### 3. Citations
- Enable for all research-heavy projects
- Use "inline" style for technical docs
- Export citation report for audits
- Cross-reference with cognitive brain

### 4. Exports
- Schedule weekly PDF exports for archiving
- Use Markdown for version control integration
- DOCX for stakeholder editing
- HTML for internal wikis

## 🔐 API Authentication Setup

### Get Your API Key

1. Go to: https://notebooklm.google.com/settings/api
2. Click "Generate API Key"
3. Copy key (starts with `nlm_`)

### Store Securely

```bash
# .env file
NOTEBOOKLM_API_KEY=nlm_abc123def456ghi789

# Or use GitHub Secrets for CI/CD
gh secret set NOTEBOOKLM_API_KEY --body "nlm_abc123def456ghi789"
```

### Verify PRO Status

```bash
python architect.py check-pro \
  --api-key $NOTEBOOKLM_API_KEY

# Output:
# ✅ NotebookLM PRO subscription active
# 🎙️ Audio overviews: Enabled
# 🔗 Shared notebooks: Enabled
# 📥 Exports: Enabled
# 📊 API quota: 1000 calls/day remaining
```

## 📊 PRO Feature Usage Tracking

```python
# Track PRO feature usage
usage = architect.nlm_api.get_usage_stats()

print(f"Audio generated this month: {usage['audio_count']}")
print(f"Shares created: {usage['share_count']}")
print(f"Exports: {usage['export_count']}")
print(f"API calls remaining: {usage['api_quota_remaining']}")
```

## 🎓 Training: Maximizing PRO Value

### Week 1: Basic Setup
- [ ] Activate PRO subscription
- [ ] Generate API key
- [ ] Create first notebook via API
- [ ] Upload 5 sources

### Week 2: Audio Overviews
- [ ] Generate first audio overview
- [ ] Test different voice styles
- [ ] Share audio with team
- [ ] Collect feedback

### Week 3: Collaboration
- [ ] Create shared notebooks
- [ ] Test permission levels
- [ ] Enable inline citations
- [ ] Track usage patterns

### Week 4: Automation
- [ ] Set up CI/CD integration
- [ ] Automate source generation
- [ ] Schedule weekly exports
- [ ] Monitor API quota

## 🚀 Advanced: CI/CD Integration

```yaml
# .github/workflows/notebooklm_sync.yml
name: Sync to NotebookLM

on:
  push:
    paths:
      - '.codex/plans/**'
      - '.codex/research/**'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install architect
        run: |
          cd .github/agents/project-architect-researcher
          pip install -r requirements.txt
      
      - name: Sync to NotebookLM
        env:
          NOTEBOOKLM_API_KEY: ${{ secrets.NOTEBOOKLM_API_KEY }}
        run: |
          python architect.py export-notebooklm \
            --project .codex/plans/master_plan.yaml \
            --output /tmp/notebooklm/ \
            --upload \
            --generate-audio \
            --create-share-link
      
      - name: Post to Slack
        run: |
          SHARE_URL=$(cat /tmp/notebooklm/share_url.txt)
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d "{\"text\": \"📖 NotebookLM updated: $SHARE_URL\"}"
```

## 💰 Cost Considerations

### PRO Subscription Pricing (Estimated)
- **Individual**: $10-15/month
- **Team** (5 users): $50-75/month
- **Enterprise**: Custom pricing

### API Quotas (PRO)
- **Free Tier**: 100 calls/day
- **PRO Tier**: 1000 calls/day
- **Enterprise**: 10,000+ calls/day

### Cost Optimization
1. Cache generated artifacts locally
2. Batch source uploads
3. Reuse existing notebooks
4. Monitor quota usage

## 📞 Support

### PRO Support Channels
- **Priority Email**: pro-support@notebooklm.google.com
- **Chat**: 24/7 in-app support
- **Phone**: Business hours (Enterprise only)
- **Slack**: Private PRO user community

### Resources
- [PRO User Guide](https://support.google.com/notebooklm/pro)
- [API Documentation](https://developers.google.com/notebooklm/api)
- [Community Forum](https://community.notebooklm.com)
- [Video Tutorials](https://youtube.com/notebooklm)

---

**Last Updated**: 2026-01-11
**Agent Version**: 1.0.0
**Requires**: NotebookLM PRO subscription
