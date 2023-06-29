# -*- mode: python ; coding: utf-8 -*-
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

import os
from shutil import which
from warnings import warn

block_cipher = None

DEFAULT_JACK_PATH = 'C:/Program Files (x86)/Jack'
DEFAULT_JACKTRIP_PATH = 'C:/jacktrip'

bundled = ("jackd", "jack_connect", "jack_disconnect", "jacktrip")
path = os.environ["PATH"]
if sys.platform == "win32":
    path = f"{DEFAULT_JACK_PATH};{DEFAULT_JACKTRIP_PATH};{path}"

binaries = []
for prog in bundled:
    prog_path = which(prog, path=path)
    if prog_path:
        binaries.append((prog_path, "bin/"))
    else:
        warn(f"Could not find {prog}; it will not be bundled")

datas=[
    ("jacktripcontrol/config_default.yaml", "jacktripcontrol"),
    ("jacktripcontrol/init_env.ps1", "jacktripcontrol"),
    ("avrenderercontrol/config_default.yaml", "avrenderercontrol"),
]

hidden_imports=[
    "avrenderercontrol.av_renderer_control",
    "avrenderercontrol.lep_tascar_osc",
    "avrenderercontrol.mha_cli",
    "avrenderercontrol.osc_tascar_wsl",
    "avrenderercontrol.tascar_cli",
    "probestrategy.adaptive_track",
    "probestrategy.fixed_probe_level",
    "probestrategy.probestrategy",
    "probestrategy.psychometric_function",
    "responsemode.response_mode",
    "responsemode.signal_detection",
    "responsemode.speech_intelligibility",
]

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "seaborn"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='seat-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='seat-gui',
)
