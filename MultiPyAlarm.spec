# -*- mode: python -*-

# workaround pywin32 227
import os
import site
import sys
for maybe in site.getsitepackages():
	pywin32_system32=os.path.join(maybe,"pywin32_system32")
	if os.path.isdir(pywin32_system32):
		sys.path.append(pywin32_system32)

block_cipher = None


a = Analysis(['MultiPyAlarm.py'],
             binaries=None,
             datas=None,
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
