# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src/main.py'],
             pathex=['/home/david/Github/dhis2-pk', 'src', 'src/common'],
             binaries=[],
             datas=[],
             hiddenimports=['dhis2'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='dhis2-pk',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
