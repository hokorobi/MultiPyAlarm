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
        self.maxindex = self.get_maxindex()
        # 起動時に過ぎてしまっているアラームは削除
        # todo? 何を削除したか表示する
        self.delete_timeout()

    def add(self, inputtime, message, noneBaloon=False):
        timer = self.get_timer(inputtime, message, noneBaloon)
        if not timer:
            raise
        self.maxindex = self.maxindex + 1
        self.list[self.maxindex] = timer
        self.file.save(self.list)

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
        self.file.save(self.list)

    def delete_timeout(self):
        for key, timer in self.list.items():
            if timer is None or timer["endtime"] < datetime.datetime.today():
                del self.list[key]
        self.file.save(self.list)

    def refresh_index(self, key, index):
        self.list[key]["index"] = index
        self.file.save(self.list)

    def get_maxindex(self):
        # タイマーインデックスの最大値を返す
        max_index = 0
        if not self.list:
            return max_index
        for key, value in self.list.items():
            if max_index < key:
                max_index = key
        return max_index

    def split_digit_char(self, inputtime):
        """数字と文字を分割してリストとして返す

        split_digit_char('10s 20h 30m') -> ['10', 's', '20', 'h', '30', 'm']
        """
        chars = list(inputtime) # 1 文字ずつのリストへ
        while ' ' in chars: chars.remove(' ') # ' ' 削除

        # 連続した数字を結合する ['1', '2', 'm', '1', 's'] -> ['12', 'm', '1', 's']
        new = []
        for char in chars:
            if char.isdigit() and new and new[-1].isdigit():
                new[-1] = ''.join((new[-1], char))
                continue
            new.append(char)
        return new

    def get_timedelta_map(self, times):
        """時、分、秒のそれぞれの値を合計する"""
        delta = {'h': 0, 'm': 0, 's': 0}
        unit = ''
        for x in times[::-1]:
            if x.isdigit():
                delta[unit] = delta[unit] + int(x)
            else:
                unit = x
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

            hms = self.get_timedelta_map(self.split_digit_char(inputtime))
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
        if self.file.ischanged():
            self.file.load()
            self.list = self.file.get_list()

    def items(self):
        return self.list.items()

    def displayed(self, key):
        self.list[key]["displayed"] = True
        self.file.save(self.list)
