from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path

from .cli import DEFAULT_APP_WORKSPACE


class OfflineZipKeymasterGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Offline ZIP Keymaster")
        self.root.geometry("520x360")

        self.action_var = tk.StringVar(value="generate-key")
        self.key_var = tk.StringVar(value=str(Path.cwd() / "offline_key.key"))
        self.input_var = tk.StringVar(value=str(Path.cwd() / "source_data"))
        self.output_var = tk.StringVar(value=str(Path.cwd() / "offline_zip_keymaster_app"))
        self.zip_var = tk.StringVar(value=str(Path.cwd() / "payloads" / "archive.zip"))

        frame = tk.Frame(root, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Action").grid(row=0, column=0, sticky="w")
        action_menu = tk.OptionMenu(frame, self.action_var, "generate-key", "encrypt", "unpack")
        action_menu.grid(row=0, column=1, sticky="ew", columnspan=2)

        tk.Label(frame, text="Key file").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.key_var).grid(row=1, column=1, sticky="ew", columnspan=2)

        tk.Label(frame, text="Input dir").grid(row=2, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.input_var).grid(row=2, column=1, sticky="ew", columnspan=2)

        tk.Label(frame, text="Archive path").grid(row=3, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.zip_var).grid(row=3, column=1, sticky="ew", columnspan=2)

        tk.Label(frame, text="Output dir").grid(row=4, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.output_var).grid(row=4, column=1, sticky="ew", columnspan=2)

        tk.Button(frame, text="Run", command=self.run_action).grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        self.status = tk.StringVar(value="Ready")
        tk.Label(frame, textvariable=self.status, justify="left", wraplength=460).grid(row=6, column=0, columnspan=3, sticky="ew")

        frame.columnconfigure(1, weight=1)

    def _command_for_action(self) -> list[str]:
        action = self.action_var.get()
        if action == "generate-key":
            return [sys.executable, "-m", "offline_zip_keymaster", "generate-key", "--key-out", self.key_var.get()]
        if action == "encrypt":
            return [
                sys.executable,
                "-m",
                "offline_zip_keymaster",
                "encrypt",
                "--input-dir",
                self.input_var.get(),
                "--zip-out",
                self.zip_var.get(),
                "--key-file",
                self.key_var.get(),
            ]
        return [
            sys.executable,
            "-m",
            "offline_zip_keymaster",
            "unpack",
            "--zip-path",
            self.zip_var.get(),
            "--key-file",
            self.key_var.get(),
            "--output-dir",
            self.output_var.get(),
        ]

    def run_action(self) -> None:
        command = self._command_for_action()
        try:
            self.status.set(f"Running: {' '.join(command)}")
            self.root.update_idletasks()
            proc = subprocess.run(command, capture_output=True, text=True, cwd=str(Path.cwd()))
            if proc.stdout:
                self.status.set(proc.stdout.strip() or proc.stderr.strip() or "Completed")
            elif proc.stderr:
                self.status.set(proc.stderr.strip())
            else:
                self.status.set("Completed")
            if proc.returncode != 0:
                self.status.set(f"Failed: {self.status.get()}")
        except Exception as exc:  # pragma: no cover - GUI safety surface
            self.status.set(f"Error: {exc}")


def main() -> int:
    root = tk.Tk()
    app = OfflineZipKeymasterGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
