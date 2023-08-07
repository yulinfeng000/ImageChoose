# -*- mode: python -*-
# vim: ft=python

import sys


sys.setrecursionlimit(5000)  # required on Windows


a = Analysis(
    ['imagechoose/__main__.py'],
    pathex=[''],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='imagechoose',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
)
app = BUNDLE(
    exe,
    name='ImageChoose.app',
    bundle_identifier=None,
    info_plist={'NSHighResolutionCapable': 'True'},
)