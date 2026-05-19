# Zendesk Voice Lines GUI Application

A comprehensive Python GUI application for interacting with the Zendesk Voice Lines API.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

## Quick Start

```bash
# Navigate to the application directory
cd apps/dev

# Run the application
python zd_voice_lines.py

# Or run the multi-speaker transcription desktop UI
python audio_transcriber_ui.py
```

## Features

✨ **Core Features:**
- 🔌 Connection testing with Zendesk API
- 📊 Paginated data retrieval from Voice Lines endpoint
- 📄 Export to JSON, CSV, and Excel formats
- 🔍 Search functionality across all pages
- ⏭️ Page navigation (Previous/Next, Jump to page)
- 📈 Real-time progress tracking
- ⚡ Automatic rate limit handling
- 🎵 **Download greeting files (MP3, WAV, etc.)**

🎁 **Bonus Features:**
- Preview data in formatted JSON
- Navigate between pages with visual controls
- Jump to specific pages
- Search across all retrieved data with result navigation
- Multiple export format options
- Professional GUI with intuitive controls
- Download voice greeting files from Zendesk
- Local multi-speaker transcription UI for MP3/MP4/WAV/M4A

## Audio Transcriber UI (Standalone Packaging Ready)

`audio_transcriber_ui.py` provides a local desktop workflow for:
- MP3/MP4 ingestion and WAV normalization
- speaker diarization with stable IDs (`SPEAKER_00`, etc.)
- optional speaker-name mapping (`.json`) and interactive naming
- transcript export as TXT/JSON/SRT/VTT

### Run

```bash
python audio_transcriber_ui.py
```

### Download as standalone package

Use the GitHub Actions workflow:

`https://github.com/Aries-Serpent/_codex_/actions/workflows/app-package-download.yml`

Select:
- `app_name=audio_transcriber_ui`
- your target branch
- preferred package format (`zip` or `tar.gz`)

## Installation

### Prerequisites

- Python 3.12 or higher
- `requests` library

### Required Dependencies

```bash
pip install requests
```

### Optional Dependencies (for Excel export)

```bash
pip install pandas openpyxl
```

## Usage

### 1. Launch the Application

```bash
python zd_voice_lines.py
```

### 2. Configure Connection

1. **Enter Subdomain**: Your Zendesk subdomain (e.g., `mycompany` for `mycompany.zendesk.com`)
2. **Enter Base64 Auth**: Your base64-encoded authentication string
3. **Test Connection**: Click to verify credentials

### 3. Retrieve Data

1. Click **"Get Voice Lines"** to fetch all pages
2. Monitor progress in the status bar
3. View data in the preview panel

### 4. Navigate and Search

- Use **Previous/Next** buttons to navigate
- **Jump to page**: Enter page number and click "Go"
- **Search**: Enter search term and click "Find"

### 5. Export Data

Choose your preferred format:
- **JSON**: Full structured data with metadata
- **CSV**: Flattened data for spreadsheet analysis
- **Excel**: Professional spreadsheet format (.xlsx)

### 6. Download Greeting Files

1. Ensure connection is tested (Download button enabled)
2. Enter greeting file path in the "Greeting Path" field
   - Example: `29136121135501/74a7c698af52a08dc12eaa7b1c5dc31b.mp3`
3. Click **"Download File"**
4. Choose save location
5. File is downloaded with original filename

**API Endpoint:** `/api/v2/channels/voice/greetings/{path}`

**Supported Formats:**
- MP3 (audio)
- WAV (audio)
- OGG (audio)
- Any file stored in voice greetings

## Authentication

### Generate Base64 Auth Key

```bash
# Format: email/token:api_token
echo -n "admin@example.com/token:your_api_token_here" | base64
```

### Example

```bash
echo -n "admin@mycompany.com/token:abcd1234efgh5678" | base64
# Output: YWRtaW5AbXljb21wYW55LmNvbS90b2tlbjphYmNkMTIzNGVmZ2g1Njc4
```

Use the output as your Base64 Auth key in the application.

## API Endpoint

The application interacts with:

```
GET https://{{subdomain}}.zendesk.com/api/v2/channels/voice/lines.json
```

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `page` | 1-N | Page number (1-indexed) |
| `per_page` | 100 | Results per page (max 100) |
| `include_talk_embeddables` | true | Include Talk embeddables |
| `include_digital_lines` | true | Include digital lines |
| `minimal_mode` | true | Minimize response size |

## Rate Limits

Zendesk API rate limits by plan:

| Plan | Requests/Minute |
|------|-----------------|
| Team | 200 |
| Growth/Professional | 400 |
| Enterprise | 700 |
| Enterprise Plus | 2500 |

The application automatically handles rate limits with retry logic.

## Documentation

- **[User Guide](docs/USER_GUIDE.md)**: Complete user documentation
- **[Development Guide](docs/DEVELOPMENT.md)**: Architecture and development details

## Project Structure

```
apps/dev/
├── zd_voice_lines.py      # Main application
├── README.md              # This file
└── docs/
    ├── USER_GUIDE.md      # User documentation
    └── DEVELOPMENT.md     # Developer documentation
```

## Screenshots

### Main Interface
The application features:
- Configuration panel for subdomain and authentication
- Connection testing with status feedback
- Data preview with scrollable JSON display
- Navigation controls (Previous, Next, Jump to page)
- Search functionality
- Export options (JSON, CSV, Excel)

## Troubleshooting

### Common Issues

**Connection Failed**
- Verify subdomain is correct (without `.zendesk.com`)
- Check base64 auth key is properly encoded
- Ensure internet connection is active

**Authentication Failed**
- Regenerate API token in Zendesk Admin Center
- Verify email and token format: `email/token:api_token`
- Re-encode with base64

**Excel Export Not Working**
- Install pandas: `pip install pandas openpyxl`
- Use JSON or CSV export as alternative

For more troubleshooting, see [User Guide](docs/USER_GUIDE.md#troubleshooting).

## FAQ

**Q: How much data can I retrieve?**  
A: All available pages until `next_page` is null. Typically unlimited with pagination.

**Q: How long does retrieval take?**  
A: Depends on data volume and rate limits. Approximately:
- 100 lines: ~1 second
- 1,000 lines: ~10 seconds
- 10,000 lines: ~2 minutes

**Q: Is my API key stored?**  
A: No. Credentials are only held in memory during the session.

**Q: Can I cancel mid-retrieval?**  
A: Currently no cancel button. Close the window to stop (data will be lost).

For more FAQs, see [User Guide](docs/USER_GUIDE.md#faq).

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

See [Development Guide](docs/DEVELOPMENT.md#contributing) for details.

## License

MIT License - See [LICENSE](../../LICENSE) file for details.

## Support

- **Issues**: https://github.com/Aries-Serpent/_codex_/issues
- **Documentation**: See `docs/` directory
- **Zendesk API**: https://developer.zendesk.com/api-reference/

## Acknowledgments

- Built for the Codex project
- Uses Zendesk Voice Lines API
- Inspired by existing Zendesk integrations in the codebase

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-13  
**Status:** ✅ Production Ready
