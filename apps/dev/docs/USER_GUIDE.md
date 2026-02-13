# Zendesk Voice Lines GUI Application - User Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Features](#features)
5. [Usage Instructions](#usage-instructions)
6. [Export Formats](#export-formats)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

The Zendesk Voice Lines GUI Application is a powerful desktop tool designed to interact with the Zendesk Voice Lines API. It provides an intuitive graphical interface for:

- Testing API connections
- Retrieving voice lines data with automatic pagination
- Previewing data in a user-friendly format
- Navigating through multiple pages of results
- Searching across all retrieved data
- Exporting data to JSON, CSV, or Excel formats

**Key Benefits:**
- No command-line experience required
- Automatic handling of pagination
- Built-in rate limit management
- Multiple export formats for data analysis
- Search functionality for quick data lookup

---

## Installation

### Prerequisites

1. **Python 3.12+** installed on your system
   - Download from: https://www.python.org/downloads/

2. **Required Python packages:**
   ```bash
   pip install requests
   ```

3. **Optional (for Excel export):**
   ```bash
   pip install pandas openpyxl
   ```

### Installation Steps

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/Aries-Serpent/_codex_.git
   cd _codex_/apps/dev
   ```

2. **Verify the application file:**
   ```bash
   ls -la zd_voice_lines.py
   ```

3. **Test the installation:**
   ```bash
   python zd_voice_lines.py
   ```

The GUI window should appear, indicating successful installation.

---

## Getting Started

### Step 1: Obtain Zendesk API Credentials

Before using the application, you need:

1. **Subdomain**: Your Zendesk subdomain (e.g., `mycompany` for `mycompany.zendesk.com`)

2. **API Token**: Generate from Zendesk Admin Center:
   - Go to Admin Center → Apps and integrations → APIs → Zendesk API
   - Enable token access
   - Generate a new API token
   - Save the token securely

3. **Base64 Authentication Key**: Create from your credentials:
   ```bash
   # Format: email/token:api_key
   echo -n "user@example.com/token:your_api_token_here" | base64
   ```

   Example:
   ```bash
   echo -n "admin@mycompany.com/token:abcd1234efgh5678" | base64
   ```
   
   Result: `YWRtaW5AbXljb21wYW55LmNvbS90b2tlbjphYmNkMTIzNGVmZ2g1Njc4`

### Step 2: Launch the Application

```bash
cd /path/to/_codex_/apps/dev
python zd_voice_lines.py
```

---

## Features

### 1. Connection Testing
- Test your Zendesk API credentials before retrieving data
- Receive immediate feedback on connection status
- View HTTP status codes for debugging

### 2. Data Retrieval
- Automatic pagination through all available pages
- Real-time progress updates during data fetching
- Handles up to 100 records per page (Zendesk API limit)
- Automatic rate limit detection and handling

### 3. Data Preview
- View formatted JSON data in a scrollable text area
- Horizontal and vertical scrolling for large datasets
- Clear, readable formatting with indentation

### 4. Page Navigation
- **Previous/Next buttons**: Navigate sequentially through pages
- **Jump to page**: Enter a specific page number to jump directly
- **Page indicator**: Shows current page and total pages

### 5. Search Functionality
- Search across all retrieved pages
- Case-insensitive search
- Jump to first result automatically
- View total number of matches

### 6. Export Options
- **JSON**: Full structured data with metadata
- **CSV**: Flattened data for spreadsheet analysis
- **Excel**: Professional spreadsheet format (requires pandas)

### 7. Menu Bar
- **File Menu**: Quick access to export functions
- **Help Menu**: Access documentation and about information

### 8. Greeting File Download (NEW)
- Download voice greeting files (MP3, WAV, etc.)
- Enter file path from Zendesk Voice API
- Automatic filename detection
- Custom save location
- Error handling for missing files

---

## Usage Instructions

### Connection Setup

1. **Enter Subdomain:**
   - Type your Zendesk subdomain (without `.zendesk.com`)
   - Example: `mycompany`

2. **Enter Base64 Auth Key:**
   - Paste your base64-encoded authentication string
   - The field is masked for security

3. **Test Connection:**
   - Click "Test Connection" button
   - Wait for confirmation dialog
   - Status will update to "Connected" on success

### Retrieving Voice Lines Data

1. **Ensure Connection is Tested:**
   - Connection must be successful before retrieving data

2. **Click "Get Voice Lines":**
   - Application will start fetching data
   - Progress indicator shows current page and total items
   - Status updates as pages are retrieved

3. **Wait for Completion:**
   - Depending on data volume, this may take several seconds to minutes
   - A success message will appear when complete

### Navigating Data

**Using Buttons:**
- Click "◄ Previous" to go to the previous page
- Click "Next ►" to go to the next page
- Page indicator updates automatically

**Jumping to a Specific Page:**
1. Enter page number in "Jump to page" field
2. Click "Go" button
3. View updates to show the requested page

### Searching Data

1. Enter search term in "Search" field
2. Click "Find" button
3. View results summary
4. Choose to jump to first result
5. Navigate between search results manually

### Exporting Data

**Export as JSON:**
1. Click "Export as JSON" button
2. Choose save location and filename
3. Click "Save"
4. Confirmation message appears on success

**Export as CSV:**
1. Click "Export as CSV" button
2. Choose save location and filename
3. Click "Save"
4. CSV file contains flattened data with all unique fields as columns

**Export as Excel:**
1. Ensure pandas and openpyxl are installed
2. Click "Export as Excel" button
3. Choose save location and filename
4. Click "Save"
5. Excel file (.xlsx) is created with formatted data

### Downloading Greeting Files (NEW)

The application now supports downloading voice greeting files from Zendesk.

**Steps:**

1. **Ensure Connection is Tested:**
   - Connection must be successful before downloading

2. **Enter Greeting File Path:**
   - Locate the "Download Greeting File" section
   - Enter the path in the format: `{greeting_id}/{filename}.ext`
   - Example: `29136121135501/74a7c698af52a08dc12eaa7b1c5dc31b.mp3`

3. **Click "Download File":**
   - Pink "Download File" button
   - Wait for download to complete

4. **Choose Save Location:**
   - File dialog appears
   - Choose where to save the file
   - Original filename is suggested
   - Click "Save"

5. **Confirmation:**
   - Success message shows file location and size
   - File is ready to use

**API Endpoint:**
```
GET https://{subdomain}.zendesk.com/api/v2/channels/voice/greetings/{path}
```

**Supported File Types:**
- MP3 (audio)
- WAV (audio)
- OGG (audio)
- Any file stored in Zendesk Voice greetings

**Example Paths:**
- `29136121135501/greeting.mp3`
- `12345678901234/custom_message.wav`
- `98765432109876/hold_music.ogg`

---

## Export Formats

### JSON Format

```json
{
  "metadata": {
    "total_pages": 3,
    "export_timestamp": "2026-02-13 17:00:00"
  },
  "pages": [
    {
      "lines": [...],
      "next_page": "...",
      "count": 100
    },
    ...
  ]
}
```

**Use Cases:**
- Data archival
- Integration with other systems
- Programmatic processing

### CSV Format

```csv
id,name,phone_number,enabled,created_at,updated_at,...
1234,"Main Line","+1-555-0100",true,"2024-01-01","2026-02-13",...
1235,"Support Line","+1-555-0101",true,"2024-01-02","2026-02-13",...
```

**Use Cases:**
- Spreadsheet analysis
- Importing into databases
- Data visualization tools

### Excel Format

- Professional spreadsheet with headers
- Data types preserved
- Easy filtering and sorting
- Compatible with Microsoft Excel, LibreOffice, Google Sheets

**Use Cases:**
- Business reporting
- Data analysis with pivot tables
- Sharing with non-technical stakeholders

---

## Troubleshooting

### Connection Issues

**Problem:** "Connection timeout. Check your subdomain."

**Solution:**
- Verify subdomain is correct (no `.zendesk.com` suffix)
- Check internet connection
- Verify Zendesk service status

**Problem:** "Authentication failed. Check your credentials."

**Solution:**
- Regenerate API token in Zendesk Admin Center
- Verify base64 encoding is correct
- Ensure email and token are in correct format

**Problem:** "Access forbidden. Check your API permissions."

**Solution:**
- Verify your Zendesk account has API access enabled
- Check that your role has permission to access Voice Lines API
- Contact your Zendesk administrator

### Data Retrieval Issues

**Problem:** "Rate limit exceeded."

**Solution:**
- Wait for the specified retry period (shown in error message)
- The application will automatically retry after the wait period
- Consider upgrading your Zendesk plan for higher rate limits

**Problem:** "No data loaded to search."

**Solution:**
- Click "Get Voice Lines" button first to retrieve data
- Wait for data retrieval to complete
- Verify connection is successful

### Download Issues

**Problem:** "File Not Found (404)"

**Solution:**
- Verify the greeting file path is correct
- Check that the file exists in Zendesk Voice greetings
- Ensure you have the complete path including greeting ID and filename

**Problem:** "Access Forbidden (403)" on file download

**Solution:**
- Verify your API token has access to voice greetings
- Check Zendesk permissions for your user role
- Contact your Zendesk administrator

**Problem:** Download button is disabled

**Solution:**
- Test connection first to enable the download button
- Ensure connection is successful before attempting download

### Export Issues

**Problem:** "pandas is required for Excel export."

**Solution:**
```bash
pip install pandas openpyxl
```

**Problem:** Excel export fails with encoding error.

**Solution:**
- Use JSON or CSV export instead
- Check for special characters in data
- Update pandas to latest version

---

## FAQ

### Q: How much data can I retrieve?

**A:** The application will retrieve all available pages until `next_page` is `null`. Zendesk's pagination system typically allows up to 100 records per page with no practical limit on total pages.

### Q: How long does it take to retrieve all data?

**A:** This depends on:
- Total number of voice lines in your Zendesk account
- Your Zendesk plan's API rate limits
- Network speed

Typical retrieval times:
- 100 lines: ~1 second
- 1,000 lines: ~10 seconds
- 10,000 lines: ~2 minutes

### Q: Can I cancel data retrieval mid-process?

**A:** Currently, there is no cancel button. Closing the application window will stop the retrieval, but already-fetched data will not be saved. This feature may be added in future versions.

### Q: Is my API key stored anywhere?

**A:** No. The application does not store or log your API credentials. They are only held in memory during the session and are cleared when you close the application.

### Q: Can I use this with Zendesk Sell or other Zendesk products?

**A:** This application is specifically designed for Zendesk Support Voice Lines API. Other Zendesk products have different API endpoints and would require a different implementation.

### Q: What are the Zendesk API rate limits?

**A:** Zendesk API rate limits depend on your plan:
- **Team**: 200 requests/minute
- **Growth/Professional**: 400 requests/minute
- **Enterprise**: 700 requests/minute
- **Enterprise Plus/High Volume**: 2,500 requests/minute

The application automatically handles rate limits with retry logic.

### Q: Can I download voice greeting files?

**A:** Yes! As of version 1.1.0, you can download greeting files (MP3, WAV, etc.) from Zendesk Voice API. Enter the greeting file path in the "Download Greeting File" section and click "Download File".

### Q: How do I find greeting file paths?

**A:** Greeting file paths are typically found in:
- Zendesk Voice line configurations
- Voice greeting settings
- Format: `{greeting_id}/{filename}.ext`
- Example: `29136121135501/greeting.mp3`

### Q: What file types can I download?

**A:** The application supports downloading any file type stored in Zendesk Voice greetings:
- MP3 (most common)
- WAV
- OGG
- Other audio formats

The file type is determined by the file extension in the path.

**A:** Currently, exports combine all pages. To export individual pages:
1. Navigate to desired page
2. Copy JSON from preview window
3. Paste into a text editor and save

A future version may include per-page export options.

### Q: How do I report bugs or request features?

**A:** Please create an issue in the GitHub repository:
https://github.com/Aries-Serpent/_codex_/issues

Include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

---

## Additional Resources

- **Zendesk API Documentation**: https://developer.zendesk.com/api-reference/
- **Rate Limits Guide**: https://developer.zendesk.com/api-reference/introduction/rate-limits/
- **Pagination Guide**: https://developer.zendesk.com/api-reference/introduction/pagination/
- **Voice API Reference**: https://developer.zendesk.com/api-reference/voice/talk-api/

---

## Support

For technical support:
- Check the [Troubleshooting](#troubleshooting) section
- Review the [FAQ](#faq)
- Contact the repository maintainers via GitHub issues

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-13  
**License:** MIT
