# -*- coding: utf-8 -*-
import datetime
import re
from timerfile import TimerFile


class TimerList(object):
    """タイマーのリスト

    timer = {
    'index': int or str,
        # リストフレームで表示しているリストのインデックス。
        # 未表示の場合は空文字列
    'starttime': datetime,
        # タイマーを開始した時間
    'endtime': datetime,
        # アラームの時間
    'message': str,
        # アラームで表示するメッセージ
    'displayed': True or False
        # 画面表示したか否か。
        # リストフレームが表示されていない状態でコマンドラインからタイマーが追
        # 加された場合にバルーンを表示をするので、その判断に使う。
    }
    """
    def __init__(self):
        self.file = TimerFile()
        self.list = self.file.get_list()
        if not self.list:
            self.maxindex = 0
            return
        self.maxindex = self._get_maxindex(self.list)
        # 起動時に過ぎてしまっているアラームは削除
        # todo? 何を削除したか表示する
        self._delete_timeout(self.list)

    def add(self, inputtime, message, noneBaloon=False):
        timer = self.get_timer(inputtime, message, noneBaloon)
        if not timer:
            raise
        self.maxindex = self.maxindex + 1
        self.list[self.maxindex] = timer
        self._save(self.list)

    def delete_from_listbox(self, index):
        # リストボックスのインデックスで削除するタイマーを指定
        listindex = [k for k, t in self.list.items() if t["index"] == index]
        self.delete(listindex[0])  # 一つだけのはずなので

    def delete(self, index):
        delete_listbox_index = self.list[index]["index"]
        del self.list[index]

        # 画面のリストのインデックスを更新
        # 更新しないと画面の listbox とずれる
        for key, timer in self.list.items():
            if not isinstance(timer["index"], int):
                continue
            if timer["index"] > delete_listbox_index:
                timer["index"] = timer["index"] - 1
                self.list[key] = timer
        self._save(self.list)

    def _delete_timeout(self, timerlist):
        temp_timerlist = [k for k, t in timerlist.items() if t is not None and t["endtime"] >= datetime.datetime.today()]
        self._save(temp_timerlist)

    def refresh_index(self, key, index):
        self.list[key]["index"] = index
        self._save(self.list)

    def _get_maxindex(self, timerlist):
        # タイマーインデックスの最大値を返す
        try:
            return 0 if max(timerlist.keys()) == '' else max(timerlist.keys())
        except:
            return 0

    def _get_timedelta_dict(self, inputtime):
        """文字列を単位毎に合計した数値の dict として返す

        _get_timedelta_dict('10s 20h 30m') -> {'h': 10, 'm': 20, 's': 30}
        """
        # ' ' を除いた 1 文字ずつのタプルへ
        chars = (x for x in inputtime if x != ' ')

        # 連続した数字を結合して、単位毎に合計して dict へ
        # ('1', 'm', '1', 's', '3', '2', 's') -> {'h': 0, 'm': 1, 's': 33}
        tempnum = ''
        delta = {'h': 0, 'm': 0, 's': 0}
        for char in chars:
            if char.isdigit():  # 連続した数字を結合
                tempnum = ''.join((tempnum, char))
                continue
            delta[char] = delta[char] + int(tempnum)
            tempnum = ''
        return delta

    def get_timer(self, inputtime, message, noneBaloon=False):

        starttime = datetime.datetime.now()
        inputtime = inputtime.strip()
        if inputtime.isdigit():
            # 数字だけなら分として扱う
            sec = int(inputtime) * 60
            endtime = starttime + datetime.timedelta(seconds=sec)
        elif re.match('[0-9hms ]+$', inputtime):
            # 1h, 1m, 1s などはそれぞれ時間、分、秒として扱う

            hms = self._get_timedelta_dict(inputtime)
            endtime = starttime + datetime.timedelta(
                hours=hms['h'], minutes=hms['m'], seconds=hms['s'])
        elif re.match('[0-9]+:[0-9]+$', inputtime):
            # 23:36 などはその時間にアラーム
            hm = [0 if x == '' else int(x) for x in inputtime.split(':', 1)]
            endtime = starttime.replace(hour=hm[0], minute=hm[1], second=0)
            if starttime > endtime:
                endtime = endtime + datetime.timedelta(days=1)
        else:
            # todo? d で日数も扱えるように
            # todo? yyyy-mm-dd も扱えるように
            return None
        return {'index': '', 'starttime': starttime, 'endtime': endtime,
                'message': message, 'displayed': noneBaloon}

    def update(self):
        self.list = self.file.get_list()

    def items(self):
        return self.list.items()

    def keys(self):
        return self.list.keys()

    def displayed(self, key):
        self.list[key]["displayed"] = True
        self._save(self.list)

    def _save(self, timerlist):
        self.file.save(timerlist)
