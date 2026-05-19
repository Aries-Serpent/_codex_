# App Package Download - Quick Reference Card

## 🚀 Quick Start (1 Minute)

### GitHub UI
1. Go to: **Actions** → **App Package Download**
2. Click: **Run workflow**
3. Select: Application + Branch
4. Click: **Run workflow**
5. Download: Scroll to **Artifacts** section

### GitHub CLI
```bash
gh workflow run app-package-download.yml \
  --field app_name=zd_voice_lines \
  --field branch=copilot/add-zd-voice-lines-console-app

# After run completes:
gh run download <run-id> --name <package-name>
```

## 📋 Input Options

| Input | Options | Default |
|-------|---------|---------|
| **Application** | `zd_voice_lines`, `audio_transcriber_ui`, `all` | `zd_voice_lines` |
| **Branch** | `main`, `0D_base_`, `copilot/add-zd-voice-lines-console-app` | `copilot/add-zd-voice-lines-console-app` |
| **Custom Branch** | _(text field)_ | _(empty)_ |
| **Format** | `zip`, `tar.gz` | `zip` |
| **Dependencies** | ✓ or ✗ | ✓ |

## 📦 Package Contents (Zendesk Voice Lines)

```
zendesk_voice_lines_<branch>_<timestamp>.zip
├── zd_voice_lines.py         # Main app (950 LOC)
├── test_api_client.py        # Tests (7 tests)
├── requirements.txt          # Dependencies
├── PACKAGE_INFO.md           # Installation guide
├── README.md                 # Quick start
├── CHANGELOG.md              # Versions
├── APPLICATION_SPEC.md       # Technical spec
├── QUICK_REFERENCE.md        # Commands
├── UI_MOCKUP.md              # Interface
└── docs/
    ├── USER_GUIDE.md         # Complete manual
    └── DEVELOPMENT.md        # Dev guide
```

## 💻 Installation (After Download)

```bash
# Extract
unzip zendesk_voice_lines_*.zip
cd zendesk_voice_lines_*/

# Install dependencies
pip install -r requirements.txt

# Run application
python zd_voice_lines.py
```

## 🎯 Common Use Cases

### Use Case 1: Download Latest from Feature Branch
```bash
gh workflow run app-package-download.yml \
  --field app_name=zd_voice_lines \
  --field branch=copilot/add-zd-voice-lines-console-app \
  --field package_format=zip
```

### Use Case 2: Download from Custom Branch
```bash
gh workflow run app-package-download.yml \
  --field app_name=zd_voice_lines \
  --field custom_branch=feature/my-custom-branch \
  --field package_format=tar.gz
```

### Use Case 3: Download All Apps
```bash
gh workflow run app-package-download.yml \
  --field app_name=all \
  --field branch=main
```

### Use Case 4: Download Audio Transcriber UI Package
```bash
gh workflow run app-package-download.yml \
  --field app_name=audio_transcriber_ui \
  --field branch=main \
  --field package_format=zip
```

## 📊 Artifacts

- **Package**: 30-day retention (~100-150 KB for zd_voice_lines)
- **Manifest**: 90-day retention (JSON metadata)

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "apps directory not found" | Verify branch has `apps/` directory |
| "Unknown application" | Check app exists in selected branch |
| Download expired | Re-run workflow (30-day limit) |
| Dependencies fail | Verify Python 3.12+, install tkinter |

## 📚 Full Documentation

- **Complete Guide**: `.github/workflows/app-package-download.md`
- **Workflow Index**: `.github/workflows/README.md`
- **User Guide**: `apps/dev/docs/USER_GUIDE.md` (in package)

## 🔗 URLs

- **Workflow**: `https://github.com/Aries-Serpent/_codex_/actions/workflows/app-package-download.yml`
- **Actions Tab**: `https://github.com/Aries-Serpent/_codex_/actions`

## ⚡ Pro Tips

1. **Custom Branches**: Use `custom_branch` field for any unlisted branch
2. **Format Choice**: ZIP for Windows, TAR.GZ for Unix/Linux
3. **Dependencies**: Disable if managing deps separately
4. **Multiple Apps**: Use `app_name=all` to package everything
5. **Quick Download**: Use GitHub CLI for faster downloads

## 📞 Support

- **Issues**: Create GitHub issue
- **Questions**: Contact @mbaetiong
- **Documentation**: See `.github/workflows/app-package-download.md`

---

**Workflow File**: `.github/workflows/app-package-download.yml`  
**Last Updated**: 2026-02-13  
**Version**: 1.0.0
