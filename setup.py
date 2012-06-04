from distutils.core import setup
import py2exe

setup(options = {"py2exe": {
                            'bundle_files': 1,
                            'optimize': 2,
                            'compressed': True}},
      windows = [{'script': 'multipletimer.py',
                  'icon_resources': [(0, 'MultiPyAlarm.ico')]}], zipfile=None)
