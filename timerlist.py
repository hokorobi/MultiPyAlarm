# -*- coding: utf-8 -*-
import datetime
import re
from timerfile import TimerFile


class TimerList(object):
    """
    タイマーのリスト

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
        for key, timer in self.list.items():
            if timer["index"] == index:
                delete_timerlist_index = key
                break
        self.delete(delete_timerlist_index)

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
        num = 0
        if self.list:
            for key, value in self.list.items():
                if num < key:
                    num = key
        return num

    def divlist(self, inputtime):
        """数字と文字を分割してリストとして返す"""
        org = list(inputtime)
        new = []
        n = ''
        for x in org:
            if x.isdigit():
                n = ''.join((n, x))
            elif x == ' ':
                continue
            else:
                if n == '':
                    new.append(x)
                else:
                    new.append(n)
                    new.append(x)
                    n = ''
        return new

    def get_timedelta_map(self, times):
        """時、分、秒のそれぞれの値を合計する"""
        delta = {'h': 0, 'm': 0, 's': 0}
        t = ''
        for x in times[::-1]:
            if x.isdigit():
                delta[t] = delta[t] + int(x)
            else:
                t = x
        return delta

    def get_timer(self, inputtime, message, noneBaloon=False):
        try:
            starttime = datetime.datetime.now()
            inputtime = inputtime.strip()
            if inputtime.isdigit():
                # 数字だけ
                m = int(inputtime)
                endtime = starttime + datetime.timedelta(seconds=m * 60)
            elif re.match('[0-9hms ]+$', inputtime):
                # 1h, 1m, 1s など

                hms = self.get_timedelta_map(self.divlist(inputtime))
                endtime = starttime + datetime.timedelta(
                    hours=hms['h'], minutes=hms['m'], seconds=hms['s'])
            elif re.match('[0-9]+:[0-9]+$', inputtime):
                hm = [0 if x == '' else int(x) for x in inputtime.split(':', 1)]
                endtime = starttime.replace(hour=hm[0], minute=hm[1], second=0)
                if starttime > endtime:
                    endtime = endtime + datetime.timedelta(days=1)
            else:
                # todo? d で日数も扱えるように
                # todo? yyyy-mm-dd も扱えるように
                raise 'invalid time'
            return {'index': '', 'starttime': starttime, 'endtime': endtime,
                    'message': message, 'displayed': noneBaloon}
        except:
            return None

    def update(self):
        if self.file.ischanged():
            self.file.load()
            self.list = self.file.get_list()

    def items(self):
        return self.list.items()

    def displayed(self, key):
        self.list[key]["displayed"] = True
        self.file.save(self.list)
