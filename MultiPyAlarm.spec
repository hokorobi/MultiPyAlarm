block_cipher = None

a = Analysis(['MultiPyAlarm.py'],
             binaries=None,
             datas=[('alarm.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='MultiPyAlarm',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='MultiPyAlarm.ico')

