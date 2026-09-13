# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_submodules

ROOT = os.getcwd()

block_cipher = None

hiddenimports = collect_submodules("offline_zip_keymaster")
hiddenimports.extend(["offline_zip_keymaster", "offline_zip_keymaster.cli", "offline_zip_keymaster.gui"])

analysis = Analysis(
    [os.path.join(ROOT, "src", "offline_zip_keymaster", "gui.py")],
    pathex=[ROOT, os.path.join(ROOT, "src")],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "src", "offline_zip_keymaster"), "offline_zip_keymaster"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch",
        "uvicorn",
        "starlette",
        "httpx",
        "libcst",
        "anyio",
        "pandas",
        "numpy",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="run_offline_zip_keymaster",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="run_offline_zip_keymaster",
)
