# -*- coding: utf-8 -*-
import os
import time
import sys
import wx
import re
import datetime
from namedmutex import NamedMutex
import yaml
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

# アラームリストの画面表示
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

# 時間が来たらメッセージ用のウィンドウを表示
class MessageFrame(wx.Frame):
    def __init__(self, parent, title, message):
        wx.Frame.__init__(self, parent, title=title)

        if not message:
            message = "UP ON TIME"
        panel = wx.Panel(self, wx.ID_ANY)
        text = wx.StaticText(panel, wx.ID_ANY, message, style = wx.TE_CENTER)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(text, flag = wx.GROW)
        panel.SetSizer(layout)
        self.Show(True)

        self.alarm_move_window(self)

    # ウィンドウを動かして目立たせる
    def alarm_move_window(self, event):
        pos = self.GetPosition()
        self.Move((pos[0] - 50, pos[1]))
        time.sleep(0.1)
        self.Move((pos[0], pos[1] - 50))
        time.sleep(0.1)
        self.Move((pos[0], pos[1] + 50))
        time.sleep(0.1)
        self.Move((pos[0] + 50, pos[1]))
        time.sleep(0.1)
        self.Move((pos[0], pos[1]))
        time.sleep(0.1)
        self.Move((pos[0] - 50, pos[1]))
        time.sleep(0.1)
        self.Move((pos[0], pos[1] - 50))
        time.sleep(0.1)
        self.Move((pos[0], pos[1] + 50))
        time.sleep(0.1)
        self.Move((pos[0] + 50, pos[1]))
        time.sleep(0.1)
        self.Move((pos[0], pos[1]))

class MyApp(wx.App):

    def OnInit(self):
        self.timernum = 0 # アラームタイマーの数
        self.timerlist = TimerList() # アラームタイマーのリスト

        # メインウィンドウ描画
        self.drawInit()

        #タイマースタート
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        return True

    # メインウィンドウ描画
    def drawInit(self):
        self.frame = wx.Frame(None, wx.ID_ANY, "Multiple Timer", size = (300, 200))
        self.frame.CreateStatusBar()
        basepanel = wx.Panel(self.frame, wx.ID_ANY)

        toppanel = wx.Panel(basepanel, wx.ID_ANY, style = wx.BORDER_SUNKEN)

        top1panel = wx.Panel(toppanel, wx.ID_ANY)
        self.message = wx.TextCtrl(top1panel, wx.ID_ANY)

        top2panel = wx.Panel(toppanel, wx.ID_ANY)
        self.count_text = wx.TextCtrl(top2panel, wx.ID_ANY)
        button_1 = wx.Button(top2panel, wx.ID_ANY, "add alarm")
        button_1.Bind(wx.EVT_BUTTON, self.addTimer)


        bottompanel = wx.Panel(basepanel, wx.ID_ANY, style = wx.BORDER_SUNKEN)
        self.listbox = CheckListCtrl(bottompanel)
        self.listbox.InsertColumn(0, 'alarm', width=80)
        self.listbox.InsertColumn(1, 'remain')
        self.listbox.InsertColumn(2, 'message')
        
        layout_bottom = wx.BoxSizer(wx.HORIZONTAL)
        layout_bottom.Add(self.listbox, proportion=1, flag=wx.GROW|wx.ALL, border=3)

        layout_top1 = wx.BoxSizer(wx.HORIZONTAL)
        layout_top1.Add(self.message, proportion=1, flag=wx.GROW)

        layout_top2 = wx.BoxSizer(wx.HORIZONTAL)
        layout_top2.Add(self.count_text)
        layout_top2.Add(button_1)

        layout_top = wx.BoxSizer(wx.VERTICAL)
        layout_top.Add(top1panel, flag=wx.GROW)
        layout_top.Add(top2panel, flag=wx.GROW)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(toppanel, flag=wx.GROW)
        layout.Add(bottompanel, proportion=1, flag=wx.GROW)

        basepanel.SetSizer(layout)
        toppanel.SetSizer(layout_top)
        top1panel.SetSizer(layout_top1)
        top2panel.SetSizer(layout_top2)
        bottompanel.SetSizer(layout_bottom)

        # タイマーリストを画面のリストに追加
        for key, timer in self.timerlist.timerlist.items():
            if self.timernum < key:
                self.timernum = key
            newindex = self.addListBox(self.listbox, timer)
            self.timerlist.refreshIndex(key, newindex)

        self.frame.Show()

        self.SetTopWindow(self.frame)

    # 画面の入力からアラームの時間を取得
    def getCounter(self):
        counter = self.count_text.GetValue()
        # 単行がなかったら秒扱い。
        # todo 分にする
        if counter.isdigit():
            return int(counter)
        else:
            # 単位が h で時間 m で分
            p = re.compile(r'([hm])')
            items = p.split(counter)
            #print items
            num = 0
            total = 0
            for s in items:
                if s.isdigit():
                    num = int(s)
                elif s == 'h':
                    total = num * 60 * 60 + total
                    num = 0
                elif s == 'm':
                    total = num * 60 + total
                    num = 0
            if num != 0:
                total = num + total
            #print total
            return total

    # アラームタイマー追加
    def addTimer(self, event):
        self.timernum = self.timernum + 1
        starttime = datetime.datetime.today()
        remain = self.getCounter()
        endtime = starttime + datetime.timedelta(seconds=remain)
        message = self.message.GetValue()
        timer = {"index": 0, "starttime": starttime, "endtime": endtime, "message": message} # index:0 は仮

        #画面に追加
        index = self.addListBox(self.listbox, timer)
        timer["index"] = index

        self.timerlist.add(self.timernum, timer)

    def addListBox(self, listbox, timer):
        remain = timer["endtime"] - datetime.datetime.today()
        index = listbox.InsertStringItem(sys.maxint, timer["endtime"].strftime("%H:%M:%S"))
        listbox.SetStringItem(index, 1, str(remain.seconds))
        listbox.SetStringItem(index, 2, timer["message"])
        return index


    def onTimer(self, event):
        # 一秒ごとに実行する処理
        # タイマーリストの中から指定時間が経過したもののアラーム表示
        # それ以外は画面の更新
        if self.timerlist:
            #print self.timerlist
            for key, timer in self.timerlist.timerlist.items():
                if timer["endtime"] < datetime.datetime.today():
                    self.timerlist.delete(key, timer["index"])
                    self.listbox.DeleteItem(timer["index"])
                    MessageFrame(self.frame, "Alarm", timer["message"])
                else:
                    remain = timer["endtime"] - datetime.datetime.today()
                    self.listbox.SetStringItem(timer["index"], 1, str(remain.seconds))

# タイマーリストのファイル処理
class TimerFile(object):
    def __init__(self):
        self.timerfile = 'timerlist'
        self.load()

    def load(self):
        try:
            f = open(self.timerfile, 'r')
            self.data = yaml.load(f)
            f.close()
        except IOError, (errno, strerror):
            if errno != 2: # not exists
                raise

    def save(self, timerlist):
        yaml.dump(timerlist, file(self.timerfile, 'wb'),
                  default_flow_style=False, encoding='utf8',
                  allow_unicode=True)

    def getTimerList(self):
        if self.data:
            return self.data
        else:
            return dict()

class TimerList(object):
    def __init__(self):
        self.timerfile = TimerFile()
        self.timerlist = self.timerfile.getTimerList()
        # 起動時に過ぎてしまっているアラームは削除
        # todo? 何を削除したか表示する
        self.deleteOutside()

    def add(self, num, timer):
        self.timerlist[num] = timer
        self.timerfile.save(self.timerlist)

    def delete(self, num, index):
        del self.timerlist[num]
        # 画面のリストのインデックスを更新
        # 更新しないとインデックスの場所がずれる
        for key, timer in self.timerlist.items():
            if timer["index"] > index:
                timer["index"] = timer["index"] - 1
                self.timerlist[key] = timer
        self.timerfile.save(self.timerlist)

    def deleteOutside(self):
        for key, timer in self.timerlist.items():
            if timer["endtime"] < datetime.datetime.today():
                del self.timerlist[key]
        self.timerfile.save(self.timerlist)

    def refreshIndex(self, key, index):
        self.timerlist[key]["index"] = index

# タイマーリストをイテレータとして使いたいけどできていない
#    def next(self):
#        self.timerlist.next()
#
#    def __iter__(self):
#        return self

if __name__ == "__main__":
    # 二重起動防止
    mut = NamedMutex("multipletimer", True, 0)
    if not mut.acret:
        exit()

    app = MyApp()
    app.MainLoop()
