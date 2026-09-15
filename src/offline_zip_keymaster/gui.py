from __future__ import annotations

import importlib
import sys
import tkinter as tk
from pathlib import Path

try:
    from ._impl import decrypt_and_unpack, encrypt_directory, generate_local_key
    from .cli import DEFAULT_APP_WORKSPACE
except ImportError:  # pragma: no cover - fallback for PyInstaller and direct script execution
    base_dir = Path(__file__).resolve()
    search_roots: list[Path] = []
    for parent in (base_dir.parent, base_dir.parents[1], base_dir.parents[2], Path.cwd()):
        if parent.exists():
            search_roots.append(parent)
            search_roots.append(parent / "src")
    seen: set[str] = set()
    for root in search_roots:
        root_str = str(root)
        if root_str and root.exists() and root_str not in seen:
            seen.add(root_str)
            sys.path.insert(0, root_str)

    DEFAULT_APP_WORKSPACE = None
    for module_name in ("offline_zip_keymaster.cli", "cli"):
        try:
            DEFAULT_APP_WORKSPACE = importlib.import_module(module_name).DEFAULT_APP_WORKSPACE
            break
        except ModuleNotFoundError:
            continue
    if DEFAULT_APP_WORKSPACE is None:
        raise

    try:
        from offline_zip_keymaster._impl import decrypt_and_unpack, encrypt_directory, generate_local_key
    except ImportError:
        decrypt_and_unpack = None
        encrypt_directory = None
        generate_local_key = None


def _runtime_resource_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parent


def resolve_runtime_path(filename: str) -> Path:
    candidates = [
        _runtime_resource_dir() / filename,
        _runtime_resource_dir().parent / filename,
        Path.cwd() / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return _runtime_resource_dir() / filename


class OfflineZipKeymasterGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Offline ZIP Keymaster")
        self.root.geometry("520x360")

        workspace = Path(DEFAULT_APP_WORKSPACE).expanduser().resolve()
        self.action_var = tk.StringVar(value="generate-key")
        self.key_var = tk.StringVar(value=str(workspace / "offline_key.key"))
        self.input_var = tk.StringVar(value=str(workspace / "source_data"))
        self.output_var = tk.StringVar(value=str(workspace))
        self.zip_var = tk.StringVar(value=str(workspace / "payloads" / "archive.zip"))

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
        if getattr(sys, "frozen", False):
            return []
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
        try:
            action = self.action_var.get()
            if action == "generate-key":
                if generate_local_key is None:
                    raise RuntimeError("offline_zip_keymaster backend is unavailable")
                result = generate_local_key(self.key_var.get())
                self.status.set(f"Generated key manifest: {result['key_path']}")
                return
            if action == "encrypt":
                if encrypt_directory is None:
                    raise RuntimeError("offline_zip_keymaster backend is unavailable")
                result = encrypt_directory(self.input_var.get(), self.zip_var.get(), self.key_var.get())
                self.status.set(f"Encrypted archive created: {result['zip_path']}")
                return
            if decrypt_and_unpack is None:
                raise RuntimeError("offline_zip_keymaster backend is unavailable")
            extracted = decrypt_and_unpack(self.zip_var.get(), self.key_var.get(), output_dir=self.output_var.get())
            self.status.set(f"Extracted archive into: {extracted}")
        except Exception as exc:  # pragma: no cover - GUI safety surface
            self.status.set(f"Error: {exc}")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if any(arg in {"-h", "--help", "/?"} for arg in args):
        print("Offline ZIP Keymaster GUI")
        print("Usage: run_offline_zip_keymaster.exe [--help]")
        print("Default behavior launches the GUI window.")
        return 0

    root = tk.Tk()
    OfflineZipKeymasterGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
