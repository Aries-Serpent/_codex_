# Zendesk Voice Lines GUI - Quick Reference Card

## Launch Application
```bash
cd apps/dev
python zd_voice_lines.py
```

## Connection Setup (First Time)

### 1. Get API Token
Admin Center → Apps and integrations → APIs → Zendesk API → Generate Token

### 2. Create Base64 Auth
```bash
echo -n "your_email@domain.com/token:YOUR_API_TOKEN" | base64
```

### 3. Enter in GUI
- **Subdomain**: `yourcompany` (not `yourcompany.zendesk.com`)
- **Base64 Auth**: Paste the encoded string

### 4. Test Connection
Click **"Test Connection"** → Should see "Connection successful!"

## Common Operations

### Retrieve All Data
1. Click **"Get Voice Lines"**
2. Wait for progress indicator
3. Data appears in preview

### Navigate Pages
- **◄ Previous**: Go back one page
- **Next ►**: Go forward one page
- **Jump to page**: Enter number → Click "Go"

### Search
1. Enter search term
2. Click **"Find"**
3. Choose to jump to first result

### Export Data

| Format | When to Use |
|--------|-------------|
| **JSON** | Archive, API integration, full data structure |
| **CSV** | Spreadsheet analysis, database import |
| **Excel** | Business reports, pivot tables, sharing |

## Keyboard Shortcuts

- `Enter` in subdomain field → Focus auth field
- `Enter` in auth field → Test connection
- `Enter` in search field → Execute search
- `Enter` in jump field → Jump to page

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Connection timeout | Check subdomain (no `.zendesk.com`) |
| Auth failed (401) | Regenerate API token |
| No data loaded | Test connection first |
| Excel export fails | Install: `pip install pandas openpyxl` |

## API Rate Limits

| Plan | Limit | Estimated Time for 10k Lines |
|------|-------|------------------------------|
| Team | 200/min | ~5 min |
| Growth | 400/min | ~2.5 min |
| Enterprise | 700/min | ~1.5 min |
| Enterprise+ | 2500/min | ~30 sec |

## File Locations

```
apps/dev/
├── zd_voice_lines.py      # Main application
├── README.md              # Overview
└── docs/
    ├── USER_GUIDE.md      # Full user guide
    └── DEVELOPMENT.md     # Developer guide
```

## Support

- **Documentation**: `apps/dev/docs/USER_GUIDE.md`
- **Issues**: https://github.com/Aries-Serpent/_codex_/issues
- **Zendesk API**: https://developer.zendesk.com/api-reference/

---

**Quick Tip**: Keep your API token secure! Never commit it to version control.
