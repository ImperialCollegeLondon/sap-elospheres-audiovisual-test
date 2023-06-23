# -*- mode: python ; coding: utf-8 -*-
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

block_cipher = None

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
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='seat-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
