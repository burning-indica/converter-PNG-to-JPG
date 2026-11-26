# -*- mode: python ; coding: utf-8 -*-
#
# Build: pyinstaller --noconfirm PNG2JPG.spec
# Result: dist/PNG2JPG.exe (single file, ~18 MB)
#
# The excludes below remove modules the app never uses. Without them
# PyInstaller pulls in numpy (~26 MB) and OpenSSL (~7 MB) through Pillow,
# making the build roughly four times larger.
#
# upx=True is kept: PyInstaller uses UPX when upx.exe is on PATH. A one-file
# build is already zlib-compressed, so the gain is small, and UPX-packed
# executables are more likely to trigger antivirus heuristics.
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('tkinterdnd2')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

EXCLUDES = [
    'numpy',
    'matplotlib',
    'scipy',
    'pandas',
    'IPython',
    'pytest',
    '_pytest',
    'setuptools',
    'pkg_resources',
    'pip',
    'wheel',
    'pydoc_data',
    'unittest',
    'email',
    'http',
    'xmlrpc',
    'ssl',
    '_ssl',
    '_hashlib',
    'test',
    'tests',
    'idlelib',
    'turtle',
    'turtledemo',
    'lib2to3',
]

a = Analysis(
    ['png_to_jpg.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
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
    name='PNG2JPG',
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

