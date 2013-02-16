# -*- coding: utf-8 -*-
import os
import yaml
import sys
import imp

class TimerFile(object):
    # タイマーリストのファイル処理

    def __init__(self):
        self.timerfile = os.path.join(self.get_main_dir(), 'timerlist')
        self.load()

    # exe にした場合も実行ファイルのパスが取得できるように
    def main_is_frozen(self):
        return (hasattr(sys, "frozen") # new py2exe
                or hasattr(sys, "importers") # old py2exe
                or imp.is_frozen("__main__")) # tools/freeze

    def get_main_dir(self):
        if self.main_is_frozen():
            return os.path.abspath(os.path.dirname(sys.executable))
        return os.path.abspath(os.path.dirname(sys.argv[0]))

    def load(self):
        try:
            f = open(self.timerfile, 'r')
            self.data = yaml.load(f)
            f.close()
            self.mtime = os.path.getmtime(self.timerfile)
        except IOError, (errno, strerror):
            self.data = dict()
            if errno != 2: # not exists
                raise

    def save(self, data):
        yaml.dump(data, file(self.timerfile, 'wb'),
                  default_flow_style=False, encoding='utf8',
                  allow_unicode=True)
        self.mtime = os.path.getmtime(self.timerfile)

    def get_list(self):
        return self.data

    def ischanged(self):
        if self.mtime < os.path.getmtime(self.timerfile):
            return True
        else:
            return False
