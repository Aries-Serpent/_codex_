#!/usr/bin/env python3
"""Tkinter UI for multi-speaker audio transcription."""

from __future__ import annotations

import queue
import sys
import threading
from pathlib import Path
from tkinter import (
    BOTH,
    LEFT,
    RIGHT,
    Button,
    Checkbutton,
    DoubleVar,
    Entry,
    Frame,
    IntVar,
    Label,
    StringVar,
    Text,
    Tk,
    filedialog,
    messagebox,
    simpledialog,
)
from tkinter.ttk import Progressbar

# ---------------------------------------------------------------------------
# Resolve import search paths so the app works in both execution layouts:
#   1. Standalone package (extracted artifact):
#      services/ is a direct sibling of this file → importable by default.
#   2. Repository layout (apps/dev/audio_transcriber_ui.py):
#      src/ and root-level services/ live two directories above apps/dev/.
# ---------------------------------------------------------------------------
_here = Path(__file__).resolve().parent          # directory containing this file
_repo_root = _here.parent.parent                 # _codex_/ root when run from apps/dev/
for _candidate in (str(_here), str(_repo_root)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

try:
    # Preferred path for standalone packaged app.
    from services.audio.workflow.transcription_workflow import (
        AudioTranscriptionWorkflow,
        TranscriptionConfig,
        load_speaker_map,
    )
except ImportError:  # pragma: no cover - fallback path for src-layout execution
    from src.services.audio.workflow.transcription_workflow import (  # type: ignore[no-redef]
        AudioTranscriptionWorkflow,
        TranscriptionConfig,
        load_speaker_map,
    )


class AudioTranscriberUI:
    """Desktop UI for transcription workflow."""

    def __init__(self):
        self.root = Tk()
        self.root.title("Audio Transcriber UI")
        self.root.geometry("980x700")
        self.worker_thread: threading.Thread | None = None
        self._ui_queue: queue.Queue[tuple[str, str | float]] = queue.Queue()
        self.speaker_name_timeout_seconds = 30.0

        self.input_path = StringVar()
        self.output_dir = StringVar()
        self.speaker_map_path = StringVar()
        self.backend = StringVar(value="mock")
        self.diarization_backend = StringVar(value="acoustic-clustering")
        self.model_size = StringVar(value="small")
        self.max_speakers = StringVar(value="4")
        self.max_duration_seconds = StringVar(value=str(4 * 60 * 60))
        self.interactive_speakers = IntVar(value=0)
        self.format_txt = IntVar(value=1)
        self.format_json = IntVar(value=1)
        self.format_srt = IntVar(value=0)
        self.format_vtt = IntVar(value=0)
        self.progress_value = DoubleVar(value=0.0)
        self.progress_status = StringVar(value="Idle")

        self._build_layout()
        self._start_log_poll()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self) -> None:
        main = Frame(self.root)
        main.pack(fill=BOTH, expand=True, padx=12, pady=12)

        self._row_with_browse(main, "Input file/directory", self.input_path, self._choose_input)
        self._row_with_browse(main, "Output directory", self.output_dir, self._choose_output)
        self._row_with_browse(main, "Speaker map JSON", self.speaker_map_path, self._choose_speaker_map)

        config_row = Frame(main)
        config_row.pack(fill=BOTH, pady=4)
        Label(config_row, text="Backend").pack(side=LEFT)
        Entry(config_row, textvariable=self.backend, width=18).pack(side=LEFT, padx=8)
        Label(config_row, text="Diarization").pack(side=LEFT)
        Entry(config_row, textvariable=self.diarization_backend, width=18).pack(side=LEFT, padx=8)
        Label(config_row, text="Model size").pack(side=LEFT)
        Entry(config_row, textvariable=self.model_size, width=12).pack(side=LEFT, padx=8)
        Label(config_row, text="Max speakers").pack(side=LEFT)
        Entry(config_row, textvariable=self.max_speakers, width=6).pack(side=LEFT, padx=8)

        limits_row = Frame(main)
        limits_row.pack(fill=BOTH, pady=4)
        Label(limits_row, text="Max duration (s)").pack(side=LEFT)
        Entry(limits_row, textvariable=self.max_duration_seconds, width=10).pack(side=LEFT, padx=8)
        Checkbutton(
            limits_row,
            text="Interactive speaker naming",
            variable=self.interactive_speakers,
        ).pack(side=LEFT, padx=8)

        format_row = Frame(main)
        format_row.pack(fill=BOTH, pady=4)
        Label(format_row, text="Output formats:").pack(side=LEFT)
        Checkbutton(format_row, text="TXT", variable=self.format_txt).pack(side=LEFT)
        Checkbutton(format_row, text="JSON", variable=self.format_json).pack(side=LEFT)
        Checkbutton(format_row, text="SRT", variable=self.format_srt).pack(side=LEFT)
        Checkbutton(format_row, text="VTT", variable=self.format_vtt).pack(side=LEFT)

        action_row = Frame(main)
        action_row.pack(fill=BOTH, pady=10)
        Button(action_row, text="Run Transcription", command=self._run_transcription_async).pack(
            side=LEFT, padx=4
        )
        Button(action_row, text="Clear Log", command=self._clear_log).pack(side=LEFT, padx=4)

        progress_row = Frame(main)
        progress_row.pack(fill=BOTH, pady=4)
        Label(progress_row, textvariable=self.progress_status, width=28, anchor="w").pack(
            side=LEFT, padx=4
        )
        Progressbar(
            progress_row,
            variable=self.progress_value,
            maximum=100.0,
            mode="determinate",
            length=520,
        ).pack(side=LEFT, fill=BOTH, expand=True, padx=4)

        self.log = Text(main, wrap="word", height=25)
        self.log.pack(fill=BOTH, expand=True)

    def _row_with_browse(self, parent: Frame, label: str, var: StringVar, callback) -> None:
        row = Frame(parent)
        row.pack(fill=BOTH, pady=4)
        Label(row, text=label, width=20, anchor="w").pack(side=LEFT)
        Entry(row, textvariable=var).pack(side=LEFT, fill=BOTH, expand=True, padx=6)
        Button(row, text="Browse", command=callback, width=10).pack(side=RIGHT)

    def _choose_input(self) -> None:
        choice = filedialog.askopenfilename(
            title="Select media file",
            filetypes=[("Media files", "*.mp3 *.mp4 *.wav *.m4a"), ("All files", "*.*")],
        )
        if not choice:
            choice = filedialog.askdirectory(title="Select directory with media files")
        if choice:
            self.input_path.set(choice)
            if not self.output_dir.get():
                self.output_dir.set(str(Path(choice).parent if Path(choice).is_file() else Path(choice)))

    def _choose_output(self) -> None:
        choice = filedialog.askdirectory(title="Select output directory")
        if choice:
            self.output_dir.set(choice)

    def _choose_speaker_map(self) -> None:
        choice = filedialog.askopenfilename(
            title="Select speaker map JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if choice:
            self.speaker_map_path.set(choice)

    def _selected_formats(self) -> list[str]:
        formats: list[str] = []
        if self.format_txt.get():
            formats.append("txt")
        if self.format_json.get():
            formats.append("json")
        if self.format_srt.get():
            formats.append("srt")
        if self.format_vtt.get():
            formats.append("vtt")
        return formats

    def _run_transcription_async(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Transcription in progress", "Please wait for the current job to finish.")
            return
        self._set_progress(0.0, "Starting…")
        self.worker_thread = threading.Thread(target=self._run_transcription)
        self.worker_thread.start()

    def _run_transcription(self) -> None:
        try:
            input_path = self.input_path.get().strip()
            output_dir = self.output_dir.get().strip()
            if not input_path:
                raise ValueError("Input path is required")
            if not output_dir:
                raise ValueError("Output directory is required")

            output_formats = self._selected_formats()
            if not output_formats:
                raise ValueError("Select at least one output format")

            speaker_map = load_speaker_map(self.speaker_map_path.get().strip() or None)
            config = TranscriptionConfig(
                transcription_backend=self.backend.get().strip(),
                diarization_backend=self.diarization_backend.get().strip(),
                model_size=self.model_size.get().strip(),
                max_speakers=int(self.max_speakers.get()),
                max_duration_seconds=int(self.max_duration_seconds.get()),
            )

            # Use a GUI-backed input function so interactive speaker naming shows
            # a dialog on the main thread instead of blocking stdin.
            use_interactive = bool(self.interactive_speakers.get())
            input_func = self._gui_input_func if use_interactive else input

            def _progress_callback(payload: dict[str, object]) -> None:
                progress = payload.get("progress")
                message = str(payload.get("message", "")).strip()
                if isinstance(progress, (int, float)):
                    self._set_progress(float(progress) * 100.0, message or "Working…")
                if message:
                    self._append_log(message)

            workflow = AudioTranscriptionWorkflow(config=config)
            result = workflow.process_path(
                input_path=input_path,
                output_dir=output_dir,
                speaker_map=speaker_map,
                interactive_speakers=use_interactive,
                output_formats=output_formats,
                input_func=input_func,
                progress_callback=_progress_callback,
            )

            self._append_log("=" * 70)
            self._append_log(
                f"Processed={result.processed_files} Failed={result.failed_files} Success={result.success}"
            )
            for item in result.results:
                if item.success:
                    outputs = ", ".join(f"{name}: {path}" for name, path in item.output_files.items())
                    speakers = ", ".join(item.detected_speakers)
                    self._append_log(
                        f"✅ {item.input_path.name} | Speakers: {speakers or 'none'} | Outputs: {outputs}"
                    )
                else:
                    self._append_log(f"❌ {item.input_path.name} | Error: {item.error}")

            if result.failed_files == 0:
                self._set_progress(100.0, "Completed")
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Transcription complete", "All files were processed successfully."
                    ),
                )
            else:
                self._set_progress(100.0, "Completed with errors")
                msg = f"{result.failed_files} file(s) failed. Check log output for details."
                self.root.after(
                    0,
                    lambda m=msg: messagebox.showwarning("Transcription completed with errors", m),
                )
        except Exception as exc:
            err = str(exc)
            self._set_progress(100.0, "Failed")
            self._append_log(f"❌ {err}")
            self.root.after(0, lambda e=err: messagebox.showerror("Transcription failed", e))

    def _append_log(self, text: str) -> None:
        """Thread-safe: enqueue message; the main-thread poll loop drains it."""
        self._ui_queue.put(("log", text))

    def _set_progress(self, percent: float, status: str) -> None:
        bounded = min(max(percent, 0.0), 100.0)
        self._ui_queue.put(("progress", bounded))
        self._ui_queue.put(("status", status))

    def _clear_log(self) -> None:
        # Called from the Clear Log button (main thread only) — direct write is safe.
        self.log.delete("1.0", "end")

    def _start_log_poll(self) -> None:
        """Kick off the periodic log-queue drain loop on the main thread."""
        self._poll_log_queue()

    def _poll_log_queue(self) -> None:
        """Drain all pending log messages and reschedule itself every 50 ms."""
        try:
            while True:
                item_type, payload = self._ui_queue.get_nowait()
                if item_type == "log":
                    self.log.insert("end", str(payload) + "\n")
                    self.log.see("end")
                elif item_type == "progress":
                    self.progress_value.set(float(payload))
                elif item_type == "status":
                    self.progress_status.set(str(payload))
        except queue.Empty:
            pass
        self.root.after(50, self._poll_log_queue)

    def _gui_input_func(self, prompt: str) -> str:
        """Thread-safe input callback for interactive speaker naming in the GUI.

        The worker thread blocks here while the main thread shows a dialog.
        A configurable timeout prevents the worker from hanging if the main
        thread is unresponsive; an empty string is returned on timeout.
        """
        result: list[str] = []
        done = threading.Event()

        def ask_on_main_thread() -> None:
            answer = simpledialog.askstring("Speaker Name", prompt, parent=self.root)
            result.append(answer or "")
            done.set()

        self.root.after(0, ask_on_main_thread)
        if not done.wait(timeout=self.speaker_name_timeout_seconds):
            return ""  # Main thread unresponsive; use default speaker ID.
        return result[0] if result else ""

    def _on_close(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning(
                "Transcription running",
                "A transcription job is still running. Please wait for it to finish before closing.",
            )
            return
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    app = AudioTranscriberUI()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
