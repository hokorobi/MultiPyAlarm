# -*- coding: utf-8 -*-
import os
import pickle
import sys
import imp


class TimerFile(object):
    """タイマーリストのファイル処理"""

    def __init__(self):
        self.timerfile = os.path.join(self._get_main_dir(), 'timerlist')
        self._load()

    def main_is_frozen(self):
        """exe にした場合も実行ファイルのパスが取得できるように"""
        return (hasattr(sys, "frozen")  # new py2exe
                or hasattr(sys, "importers")  # old py2exe
                or imp.is_frozen("__main__"))  # tools/freeze

    def _get_main_dir(self):
        if self.main_is_frozen():
            return os.path.abspath(os.path.dirname(sys.executable))
        return os.path.abspath(os.path.dirname(sys.argv[0]))

    def _load(self):
        try:
            with open(self.timerfile, 'rb') as f:
                self.data = pickle.load(f)
            self.mtime = os.path.getmtime(self.timerfile)
        except (EOFError, KeyError):
            # EOFError ファイルがない場合
            # KeyError YAML のデータが残っていた場合
            self.data = dict()
        except IOError, (errno, strerror):
            self.data = dict()
            if errno != 2:  # not exists
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
        except:
            # ファイルが削除されてしまっても、とりあえずエラーとならないように
            return False
