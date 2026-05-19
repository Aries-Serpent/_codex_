# App Package Download Workflow

## Overview

The **App Package Download** workflow provides a convenient way to download packaged applications from the `apps/` directory as ready-to-use ZIP or TAR.GZ archives. This workflow is designed for end users who want to download and run applications without cloning the entire repository.

## Features

- **Dropdown Selection**: Choose from available applications via dropdown menu
- **Branch Selection**: Select from common branches or specify a custom branch
- **Multiple Formats**: Download as ZIP or TAR.GZ
- **Complete Packages**: Includes application code, documentation, tests, and dependencies
- **Automatic Manifest**: JSON manifest with package metadata
- **30-Day Retention**: Artifacts stored for 30 days

## Usage

### Starting the Workflow

1. Navigate to [Actions](../../actions) in GitHub
2. Select **App Package Download** from the workflow list
3. Click **Run workflow** button
4. Configure the workflow inputs (see below)
5. Click **Run workflow** to start

### Workflow Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `app_name` | Choice | Yes | `zd_voice_lines` | Application to package |
| `branch` | Choice | Yes | `copilot/add-zd-voice-lines-console-app` | Branch to package from |
| `custom_branch` | String | No | _(empty)_ | Custom branch name (overrides dropdown) |
| `include_dependencies` | Boolean | No | `true` | Include requirements.txt |
| `package_format` | Choice | Yes | `zip` | Package format (zip or tar.gz) |

### Available Applications

Current applications available for packaging:

- **zd_voice_lines**: Zendesk Voice Lines GUI application
- **audio_transcriber_ui**: Multi-speaker MP3/MP4 transcription desktop UI
- **all**: Package all applications in the `apps/` directory

### Available Branches

Preset branch options:

- **main**: Main production branch
- **0D_base_**: Base branch for stacked PRs
- **copilot/add-zd-voice-lines-console-app**: Feature branch with Zendesk Voice Lines app

For branches not in the list, use the `custom_branch` input field.

## Package Contents

### Zendesk Voice Lines Package

When you select `zd_voice_lines`, the package includes:

```
zendesk_voice_lines_<branch>_<timestamp>/
├── zd_voice_lines.py          # Main application (950 LOC)
├── test_api_client.py         # Component tests (7 tests)
├── __init__.py                # Python package marker
├── requirements.txt           # Dependencies (if enabled)
├── PACKAGE_INFO.md            # Package information and quick start
├── README.md                  # Quick start guide
├── QUICK_REFERENCE.md         # Command reference
├── APPLICATION_SPEC.md        # Technical specification
├── UI_MOCKUP.md               # Interface layout
├── CHANGELOG.md               # Version history
└── docs/
    ├── USER_GUIDE.md          # Complete user manual
    └── DEVELOPMENT.md         # Developer documentation
```

### Audio Transcriber UI Package

When you select `audio_transcriber_ui`, the package includes:

```
audio_transcriber_ui_<branch>_<timestamp>/
├── audio_transcriber_ui.py               # Main desktop transcription UI
├── requirements.txt                      # Runtime deps
├── requirements-audio-transcription.txt  # Optional model deps
├── PACKAGE_INFO.md                       # Installation and run guide
├── USER_GUIDE.md                         # Full production user guide (promoted from docs/)
├── README.md                             # App documentation
└── services/
    └── audio/
        └── workflow/
            ├── __init__.py
            └── transcription_workflow.py
```

### Package Manifest

Each package includes a JSON manifest (`<package>-manifest.json`) with metadata:

```json
{
  "package_name": "zendesk_voice_lines_copilot_add-zd-voice-lines-console-app_20260213_180000",
  "application": "zd_voice_lines",
  "source_branch": "copilot/add-zd-voice-lines-console-app",
  "repository": "Aries-Serpent/_codex_",
  "workflow_run_id": "123456789",
  "workflow_run_number": "42",
  "generated_at": "2026-02-13T18:00:00Z",
  "format": "zip",
  "include_dependencies": true,
  "sha": "abc123def456...",
  "ref": "refs/heads/copilot/add-zd-voice-lines-console-app",
  "actor": "username"
}
```

## Downloading Packages

### Method 1: GitHub UI (Recommended)

1. After the workflow completes, scroll to the **Artifacts** section at the bottom of the workflow run page
2. Click on the package name (e.g., `zendesk_voice_lines_copilot_add-zd-voice-lines-console-app_20260213_180000`)
3. The package will download automatically

### Method 2: GitHub CLI

```bash
# List artifacts for the workflow run
gh run view <run-id> --json artifacts

# Download specific artifact
gh run download <run-id> --name <package-name>

# Example
gh run download 123456789 --name zendesk_voice_lines_copilot_add-zd-voice-lines-console-app_20260213_180000
```

### Method 3: Direct Link

Visit the workflow run page:
```
https://github.com/Aries-Serpent/_codex_/actions/runs/<run-id>
```

## Installation and Usage

### Prerequisites

- Python 3.12 or higher
- tkinter (usually included with Python)
- pip (Python package manager)

### Installation Steps

1. **Download and Extract**
   ```bash
   # For ZIP
   unzip zendesk_voice_lines_*.zip
   cd zendesk_voice_lines_*/

   # For TAR.GZ
   tar -xzf zendesk_voice_lines_*.tar.gz
   cd zendesk_voice_lines_*/
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python zd_voice_lines.py
   ```

4. **Verify Installation (Optional)**
   ```bash
   python test_api_client.py
   # Expected: 7 passed, 0 failed
   ```

### Quick Start

See `PACKAGE_INFO.md` in the extracted package for detailed quick start instructions.

## Workflow Architecture

### Jobs

1. **package-app**: Main job that handles packaging

### Key Steps

1. **Determine Target Branch**: Resolves custom or selected branch
2. **Checkout Repository**: Clones the specified branch
3. **Verify Apps Directory**: Ensures `apps/` exists
4. **Discover Applications**: Lists available applications
5. **Package Application**: Copies files to staging area
6. **Generate Dependencies**: Creates `requirements.txt` if enabled
7. **Generate Package Info**: Creates `PACKAGE_INFO.md` with instructions
8. **Create Archive**: Packages as ZIP or TAR.GZ
9. **Upload Artifacts**: Uploads package and manifest
10. **Generate Instructions**: Provides download instructions in summary

### Artifact Retention

- **Packages**: 30 days
- **Manifests**: 90 days

## Advanced Usage

### Packaging Custom Branch

To package from a branch not in the dropdown:

1. Select any option in the `branch` dropdown (it will be ignored)
2. Enter your branch name in the `custom_branch` field
3. Run the workflow

Example: To package from branch `feature/new-zendesk-feature`:
- `branch`: _(any)_
- `custom_branch`: `feature/new-zendesk-feature`

### Packaging Without Dependencies

If you want to manage dependencies separately:

1. Set `include_dependencies` to `false`
2. The package will not include `requirements.txt`

### Different Archive Formats

Choose between:
- **ZIP**: Better for Windows users, smaller size
- **TAR.GZ**: Better for Unix/Linux users, better compression

## Troubleshooting

### "apps directory not found"

**Cause**: The selected branch doesn't have an `apps/` directory.

**Solution**:
- Verify the branch name is correct
- Check that the branch contains the application you're trying to package
- Use a different branch that has the `apps/` directory

### "Unknown application name"

**Cause**: The selected application doesn't exist or isn't supported yet.

**Solution**:
- Choose a different application from the dropdown
- Contact repository maintainers to add support for the desired application

### Package Download Fails

**Cause**: Artifact may have expired (30-day retention).

**Solution**:
- Re-run the workflow to generate a new package
- Download packages within 30 days of creation

### Dependencies Installation Fails

**Cause**: Python version mismatch or missing system packages.

**Solution**:
- Ensure Python 3.12+ is installed
- On Linux: Install tkinter with `sudo apt-get install python3-tk`
- On macOS: tkinter is usually included
- On Windows: Reinstall Python with tkinter option enabled

## Adding New Applications

To add a new application to the packaging workflow:

1. Place your application in `apps/<category>/`
2. Update the workflow file (`.github/workflows/app-package-download.yml`)
3. Add the application name to the `app_name` dropdown:
   ```yaml
   app_name:
     type: choice
     options:
       - 'zd_voice_lines'
       - 'your_new_app'  # Add here
       - 'all'
   ```
4. Add packaging logic in the "Package selected application" step

## Security Considerations

### Safe Downloads

- All packages are built from repository code only
- No external dependencies are executed during packaging
- Packages are scanned by GitHub's security systems

### Credentials

- **Never** include credentials in packaged applications
- Use environment variables or configuration files for sensitive data
- Review `PACKAGE_INFO.md` for secure configuration instructions

## Workflow Permissions

The workflow requires minimal permissions:

- `contents: read` - Read repository contents
- `actions: read` - Read workflow information

No write permissions are required or granted.

## Monitoring and Logs

### Workflow Summary

After each run, the workflow generates a comprehensive summary including:

- Available applications discovered
- Packaged files list
- Package size and format
- Download instructions
- Package manifest

### Logs

Access detailed logs:
1. Navigate to the workflow run
2. Click on the **package-app** job
3. Expand each step to view detailed logs

## Performance

### Typical Execution Times

- **Checkout**: 5-10 seconds
- **Package Creation**: 1-2 seconds
- **Upload**: 2-5 seconds (depends on package size)
- **Total**: ~10-20 seconds

### Package Sizes

- **Zendesk Voice Lines**: ~100-150 KB (ZIP)
- **All Applications**: Varies based on `apps/` contents

## Technical Notes

### Artifact Upload Version

This workflow uses `actions/upload-artifact@v4` instead of v6 for the following reasons:

- **Compatibility**: v4 has stable, proven behavior with pre-compressed files
- **No Double-Wrapping**: v4 doesn't re-wrap artifacts, preventing extraction issues
- **No Password Issues**: v6 has known issues where downloaded artifacts appear password-protected due to double-compression
- **Consistency**: Most workflows in this repository use v4 for binary artifacts

If you experience any download or extraction issues, this is why the workflow explicitly uses v4.

## Related Documentation

- [Zendesk Voice Lines User Guide](../../apps/dev/docs/USER_GUIDE.md)
- [Zendesk Voice Lines Development Guide](../../apps/dev/docs/DEVELOPMENT.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub CLI Documentation](https://cli.github.com/manual/)

## Support

For issues or questions:

1. Check the workflow logs for error details
2. Review the troubleshooting section above
3. Create an issue in the repository
4. Contact @mbaetiong for workflow-specific questions

## License

This workflow is part of the _codex_ repository and follows the repository's MIT license.

---

**Workflow File**: `.github/workflows/app-package-download.yml`  
**Documentation Version**: 1.0.0  
**Last Updated**: 2026-02-13
