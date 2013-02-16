from distutils.core import setup
import py2exe

target = py2exe.build_exe.Target(script='MultiPyAlarm.py',
                                 icon_resources=[(0, 'MultiPyAlarm.ico')])
setup(options={"py2exe":
               {'bundle_files': 1,
                'optimize': 2,
                'compressed': True
                }
               },
      windows=[target],
      zipfile=None
      )
