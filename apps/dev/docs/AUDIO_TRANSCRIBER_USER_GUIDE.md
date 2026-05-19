# Audio Transcriber — User Guide

**Version:** 1.0.0  
**Application:** `audio_transcriber_ui.py`  
**Python:** 3.12+  
**Platform:** Windows · macOS · Linux

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [UI Walkthrough](#ui-walkthrough)
5. [Speaker Labeling Workflow](#speaker-labeling-workflow)
6. [Output Formats](#output-formats)
7. [CLI Usage](#cli-usage)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Overview

The **Audio Transcriber** is a standalone desktop application that converts speech
recordings into structured transcripts with per-speaker attribution. It accepts MP3,
MP4, M4A, and WAV files and produces plain-text, JSON, SRT, and WebVTT outputs — with
no cloud account required.

**Core capabilities:**

| Feature | Detail |
|---|---|
| Input formats | MP3, MP4, M4A, WAV |
| Speaker detection | Lightweight acoustic clustering (CPU-safe, no GPU needed) |
| Speaker labeling | JSON map file **or** interactive naming prompt |
| Output formats | TXT, JSON, SRT, VTT |
| Batch processing | Directory of files in one pass |
| Transcription backend | `mock` (built-in) or `faster-whisper` (optional) |
| Memory limit | Configurable max duration (default 4 h) |

---

## Installation

### Step 1 — Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.12+ | https://python.org/downloads |
| tkinter | Bundled with most Python distributions; on Linux: `sudo apt install python3-tk` |
| ffmpeg | Required **only** for MP3/MP4/M4A input; WAV works without it |

Verify Python:

```bash
python --version   # must be 3.12 or higher
python -c "import tkinter; print('tkinter OK')"
```

Verify ffmpeg (optional but recommended):

```bash
ffmpeg -version
```

### Step 2 — Obtain the package

**Option A — GitHub Actions artifact (recommended):**

1. Go to <https://github.com/Aries-Serpent/_codex_/actions/workflows/app-package-download.yml>
2. Click **Run workflow**
3. Set `app_name` = `audio_transcriber_ui`
4. Choose your branch (e.g., `main` or `copilot/add-transcription-application`)
5. Click **Run workflow** → wait for completion
6. Download the artifact ZIP from the workflow run summary

**Option B — GitHub CLI:**

```bash
gh workflow run app-package-download.yml \
  --repo Aries-Serpent/_codex_ \
  --field app_name=audio_transcriber_ui \
  --field branch=main \
  --field package_format=zip

# After the run completes, download:
gh run download <run_id> --name <artifact_name>
```

### Step 3 — Extract and install

```bash
unzip audio_transcriber_ui_*.zip -d audio_transcriber
cd audio_transcriber

# Install dependencies
pip install -r requirements.txt
```

The `requirements.txt` in the package includes:

```text
numpy>=2.4.5,<3

# Optional transcription backends
faster-whisper==1.1.1
pyannote.audio==3.3.2
ffmpeg-python==0.2.0
```

> **Tip:** For basic demo use with the built-in `mock` backend, only `numpy` is required.
> Install `faster-whisper` for real speech-to-text transcription.

### Step 4 — Launch the application

```bash
python audio_transcriber_ui.py
```

The GUI window opens immediately.

---

## Quick Start

1. Click **Browse** next to **Input file/directory** → select an MP3, MP4, WAV, or M4A file
2. Click **Browse** next to **Output directory** → select where transcripts will be saved
3. Leave **Speaker map JSON** empty for now (automatic speaker IDs will be used)
4. Check ✅ **TXT** and ✅ **JSON** in the output formats row
5. Click **Run Transcription**
6. Watch the log area update; a dialog confirms success

Your output directory will contain:

```
sample.mono16k.transcript.txt
sample.mono16k.transcript.json
```

---

## UI Walkthrough

```
┌─────────────────────────────────────────────────────────────┐
│  Input file/directory  [__________________]  [Browse]        │
│  Output directory      [__________________]  [Browse]        │
│  Speaker map JSON      [__________________]  [Browse]        │
│                                                               │
│  Backend [mock____] Model size [small_] Max speakers [4__]   │
│  Max duration (s) [14400___]  ☐ Interactive speaker naming   │
│                                                               │
│  Output formats:  ☑ TXT  ☑ JSON  ☐ SRT  ☐ VTT               │
│                                                               │
│  [Run Transcription]  [Clear Log]                             │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ ✅ meeting.wav | Speakers: SPEAKER_00, SPEAKER_01   │     │
│  │    Outputs: txt: /out/…txt  json: /out/…json        │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Field reference

| Field | Description |
|---|---|
| **Input file/directory** | Single media file or folder. For folders, all supported files are processed. |
| **Output directory** | Where all transcript files are written. Created automatically if it doesn't exist. |
| **Speaker map JSON** | Optional path to a JSON file mapping speaker IDs to human names (see below). |
| **Backend** | `mock` (no install needed) or `faster-whisper` (requires optional deps). |
| **Model size** | Whisper model: `tiny`, `base`, `small`, `medium`, `large`. Larger = slower but more accurate. |
| **Max speakers** | Upper bound for the number of distinct speakers detected (1–8). |
| **Max duration (s)** | Safety limit; files longer than this are rejected (default 14 400 s = 4 h). |
| **Interactive speaker naming** | When checked, the app prompts you to name each detected speaker before transcribing. |
| **Output formats** | Choose any combination of TXT, JSON, SRT, VTT. |

---

## Speaker Labeling Workflow

### Option A — JSON map file (recommended for repeating participants)

Create a `speakers.json` file:

```json
{
  "SPEAKER_00": "Alice",
  "SPEAKER_01": "Bob",
  "SPEAKER_02": "Carol"
}
```

Select it via the **Speaker map JSON** browse button. The IDs `SPEAKER_00`, `SPEAKER_01`,
etc. are the stable identifiers assigned by the diarization step.

**Unmapped speakers** fall back to their stable ID automatically (no crash, no prompt).

### Option B — Interactive naming

Check **Interactive speaker naming** in the UI. After normalization and diarization,
a dialog will prompt you to enter a name for each detected speaker:

```
Assign a name for SPEAKER_00 (leave blank to keep default): Alice
Assign a name for SPEAKER_01 (leave blank to keep default):
```

Leaving the prompt blank keeps the default ID (`SPEAKER_01`).

### Option C — No labeling (default IDs)

Leave the speaker map empty and uncheck interactive naming.
Transcripts will use stable IDs like `SPEAKER_00`, `SPEAKER_01`.

---

## Output Formats

### TXT — Plain text transcript

```text
[0000.00-0002.00] Alice: Hello, welcome to the meeting.
[0002.00-0005.50] Bob: Thanks for joining everyone.
```

### JSON — Structured segments

```json
[
  {
    "start": 0.0,
    "end": 2.0,
    "speaker_id": "SPEAKER_00",
    "speaker_name": "Alice",
    "text": "Hello, welcome to the meeting."
  },
  {
    "start": 2.0,
    "end": 5.5,
    "speaker_id": "SPEAKER_01",
    "speaker_name": "Bob",
    "text": "Thanks for joining everyone."
  }
]
```

### SRT — SubRip subtitles (MP4 / video)

```srt
1
00:00:00,000 --> 00:00:02,000
Alice: Hello, welcome to the meeting.

2
00:00:02,000 --> 00:00:05,500
Bob: Thanks for joining everyone.
```

### VTT — WebVTT subtitles (HTML5 / streaming)

```vtt
WEBVTT

00:00:00.000 --> 00:00:02.000
Alice: Hello, welcome to the meeting.

00:00:02.000 --> 00:00:05.500
Bob: Thanks for joining everyone.
```

---

## CLI Usage

The transcription workflow is also accessible via the extended audio CLI:

```bash
# Transcribe a single file (mock backend, txt+json output)
python -m src.services.audio.cli.smart_cli transcribe meeting.mp3

# With a speaker map and multiple output formats
python -m src.services.audio.cli.smart_cli transcribe meeting.mp4 \
  --speaker-map speakers.json \
  --formats txt json srt \
  --output-dir ./transcripts

# Batch mode (directory)
python -m src.services.audio.cli.smart_cli transcribe ./recordings/ \
  --output-dir ./out

# Using faster-whisper backend
python -m src.services.audio.cli.smart_cli transcribe meeting.wav \
  --backend faster-whisper \
  --model-size small

# Interactive speaker naming
python -m src.services.audio.cli.smart_cli transcribe meeting.wav \
  --interactive-speakers
```

**Backward compatibility:** Calling the CLI without a subcommand still defaults to `tune`:

```bash
python -m src.services.audio.cli.smart_cli input.wav   # → runs tune
```

---

## Troubleshooting

### `ffmpeg is required to process MP3/MP4/M4A inputs`

**Cause:** ffmpeg is not installed or not on `PATH`.  
**Fix:**

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows — download installer from https://ffmpeg.org/download.html
# and add its bin/ directory to PATH
```

Then restart the application.

---

### `Input duration … exceeds configured memory-safe limit`

**Cause:** The file is longer than `max_duration_seconds` (default 14 400 s = 4 h).  
**Fix:** Increase the **Max duration (s)** field in the UI, or split the file with ffmpeg:

```bash
ffmpeg -i long.mp4 -t 3600 -c copy part1.mp4
```

---

### `transcription_backend='faster-whisper' requires installing faster-whisper`

**Cause:** The `faster-whisper` package is not installed.  
**Fix:**

```bash
pip install faster-whisper==1.1.1
```

---

### `Unsupported media format: .ogg`

**Cause:** `.ogg` and other codec formats are not in the supported input set.  
**Supported:** `.wav`, `.mp3`, `.mp4`, `.m4a`.  
**Fix:** Convert to a supported format first:

```bash
ffmpeg -i recording.ogg recording.mp3
```

---

### `tkinter` not found (Linux)

```bash
sudo apt install python3-tk   # Debian/Ubuntu
sudo dnf install python3-tkinter  # Fedora/RHEL
```

---

### Application window closes on import error

Check the terminal/console window that opened with the app. It will show the full
Python traceback. The most common cause is a missing dependency — run:

```bash
pip install -r requirements.txt
```

---

## FAQ

**Q: Does transcription work without an internet connection?**  
A: Yes. The `mock` backend is fully offline. `faster-whisper` downloads the model on first
use but runs entirely locally after that. No audio data is sent to external servers.

**Q: Can I transcribe video files with background music?**  
A: Yes — the tool will transcribe whatever audio is present. For best results, use files
with predominantly speech. Music-heavy files may produce fragmented speaker assignments.

**Q: How accurate is the diarization?**  
A: The built-in diarization is a lightweight acoustic clusterer designed to work on CPU
without optional ML dependencies. It correctly separates clearly distinct voices in clean
audio. For production-quality diarization, integrate `pyannote.audio`.

**Q: Can I customize the number of detected speakers?**  
A: Yes — set **Max speakers** in the UI (or `--max-speakers` in the CLI). Lowering this
forces the model to merge more segments; raising it allows more distinct voices.

**Q: What happens if a speaker ID in the JSON map doesn't appear in the file?**  
A: Unused entries in the map are silently ignored. Only IDs actually detected are resolved.

**Q: Can I re-run on a file I've already processed?**  
A: Yes. Output files are overwritten if they already exist. The normalized WAV
(`*.mono16k.wav`) is also re-created each run for non-WAV inputs.

**Q: How do I report issues?**  
A: Open an issue at <https://github.com/Aries-Serpent/_codex_/issues> with:
- File format and approximate duration
- OS and Python version
- Full error text from the log panel

---

## Package Contents (downloaded artifact)

```
audio_transcriber_ui.py           ← Main application (run this)
USER_GUIDE.md                     ← This guide
requirements.txt                  ← Python dependencies
PACKAGE_INFO.md                   ← Build metadata
services/
  __init__.py
  audio/
    __init__.py
    workflow/
      __init__.py
      transcription_workflow.py   ← Self-contained pipeline module
docs/
  AUDIO_TRANSCRIBER_USER_GUIDE.md ← Full guide
  USER_GUIDE.md                   ← Zendesk Voice Lines guide
```

Everything needed to run the application is self-contained in this package.
**No repository clone or `src/` path manipulation is required.**

---

*Generated by the Aries-Serpent/\_codex\_ project. MIT License.*
