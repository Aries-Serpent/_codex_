#!/usr/bin/env python3
"""Tkinter UI for multi-speaker audio transcription."""

from __future__ import annotations

import threading
from pathlib import Path
from tkinter import (
    BOTH,
    LEFT,
    RIGHT,
    Button,
    Checkbutton,
    Entry,
    Frame,
    IntVar,
    Label,
    StringVar,
    Text,
    Tk,
    filedialog,
    messagebox,
)

from services.audio.workflow.transcription_workflow import (
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

        self.input_path = StringVar()
        self.output_dir = StringVar()
        self.speaker_map_path = StringVar()
        self.backend = StringVar(value="mock")
        self.model_size = StringVar(value="small")
        self.max_speakers = StringVar(value="4")
        self.max_duration_seconds = StringVar(value=str(4 * 60 * 60))
        self.interactive_speakers = IntVar(value=0)
        self.format_txt = IntVar(value=1)
        self.format_json = IntVar(value=1)
        self.format_srt = IntVar(value=0)
        self.format_vtt = IntVar(value=0)

        self._build_layout()
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
                model_size=self.model_size.get().strip(),
                max_speakers=int(self.max_speakers.get()),
                max_duration_seconds=int(self.max_duration_seconds.get()),
            )

            workflow = AudioTranscriptionWorkflow(config=config)
            result = workflow.process_path(
                input_path=input_path,
                output_dir=output_dir,
                speaker_map=speaker_map,
                interactive_speakers=bool(self.interactive_speakers.get()),
                output_formats=output_formats,
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
                messagebox.showinfo("Transcription complete", "All files were processed successfully.")
            else:
                messagebox.showwarning(
                    "Transcription completed with errors",
                    f"{result.failed_files} file(s) failed. Check log output for details.",
                )
        except Exception as exc:
            self._append_log(f"❌ {exc}")
            messagebox.showerror("Transcription failed", str(exc))

    def _append_log(self, text: str) -> None:
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def _clear_log(self) -> None:
        self.log.delete("1.0", "end")

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
