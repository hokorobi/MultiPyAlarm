# -*- coding: utf-8 -*-
import imp
import os
import pickle
import sys
from pathlib import Path


class TimerFile(object):
    """タイマーリストのファイル処理"""

    def __init__(self):
        self.timerfile = Path(sys.argv[0]).resolve().parent / 'timerlist'
        self._load()

    def _load(self):
        try:
            with open(self.timerfile, 'rb') as f:
                self.data = pickle.load(f)
            self.mtime = os.path.getmtime(self.timerfile)
        except (EOFError, KeyError):
            # EOFError ファイルがない場合
            # KeyError YAML のデータが残っていた場合
            self.data = dict()
        except (IOError) as e:
            self.data = dict()
            if e.errno != 2:  # not exists
                raise

    def save(self, data):
        with open(self.timerfile, 'wb') as f:
            pickle.dump(data, f)
        self.mtime = os.path.getmtime(self.timerfile)

    def get_list(self):
        if self._ischanged():
            self._load()
        return self.data

    def _ischanged(self):
        try:
            if self.mtime < os.path.getmtime(self.timerfile):
                return True
            else:
                return False
        except Exception:
            # ファイルが削除されてしまっても、とりあえずエラーとならないように
            return False
