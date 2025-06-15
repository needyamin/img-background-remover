# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\needyamin\\Desktop\\BG Remover\\remove_background_new.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\needyamin\\.u2net', 'u2net'), ('C:\\laragon\\bin\\python\\python-3.10\\lib\\site-packages\\customtkinter', 'customtkinter')],
    hiddenimports=['PIL', 'PIL._tkinter_finder', 'rembg', 'customtkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BG_Remover_Pro',
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
