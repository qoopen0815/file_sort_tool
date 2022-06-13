# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['scripts\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'sklearn.utils._typedefs',
        'sklearn.utils._heap',
        'sklearn.utils._sorting',
        'sklearn.utils._vector_sentinel',
        'sklearn.neighbors._partition_nodes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
a.datas += [
    (
        '07YasashisaAntique.otf',
        '.\\scripts\\interface\\font\\YasashisaAntiqueFont\\07YasashisaAntique.otf',
        'DATA'
    ),
    (
        'icon.ico',
        '.\\icon.ico',
        'DATA'
    ),
]
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='File Sort Tool',
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
    icon='icon.ico'
)
