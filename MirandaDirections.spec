# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('assets', includes=['*.png', '*.ico'])

a = Analysis(
    ['main_directions.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    # there is a problem with Tk not finding some dynamically loaded modules,
    # which is why we need to manually add them.
    # https://stackoverflow.com/questions/52675162/pyinstaller-doesnt-play-well-with-imagetk-and-tkinter
    hiddenimports=['PIL._tkinter_finder'],
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
    [],
    exclude_binaries=True,
    name='Miranda Directions',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Miranda Directions',
)
