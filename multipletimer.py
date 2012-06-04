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
import win32api

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
        font = wx.Font(32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text = wx.StaticText(panel, wx.ID_ANY, message, style = wx.TE_CENTER)
        text.SetFont(font)
        text.CenterOnParent()
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

        exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
        icon = wx.Icon(exeName + ";0", wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(icon)

        self.frame.CreateStatusBar()
        basepanel = wx.Panel(self.frame, wx.ID_ANY)

        toppanel = wx.Panel(basepanel, wx.ID_ANY, style = wx.BORDER_SUNKEN)

        top1panel = wx.Panel(toppanel, wx.ID_ANY)
        self.message = wx.TextCtrl(top1panel, wx.ID_ANY)

        top2panel = wx.Panel(toppanel, wx.ID_ANY)
        self.count_text = wx.TextCtrl(top2panel, wx.ID_ANY)
        button_add = wx.Button(top2panel, wx.ID_ANY, "add")
        button_add.Bind(wx.EVT_BUTTON, self.addTimer)
        button_del = wx.Button(top2panel, wx.ID_ANY, "del")
        button_del.Bind(wx.EVT_BUTTON, self.delTimer)


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
        layout_top2.Add(button_add)
        layout_top2.Add(button_del)

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
            newindex = self.addListBox(self.listbox, timer)
            self.timerlist.refreshIndex(key, newindex)

        self.frame.Show()

        self.SetTopWindow(self.frame)

    # アラームタイマー追加
    # 追加するのはファイルのみ
    # 画面への反映は、onTimer で
    def addTimer(self, event):
        starttime = datetime.datetime.today()
        remain = TimerList.getRemain(self.count_text.GetValue())
        endtime = starttime + datetime.timedelta(seconds=remain)
        message = self.message.GetValue()
        # index が空のものは画面未反映
        timer = {"index": "", "starttime": starttime, "endtime": endtime, "message": message} # index:0 は仮
        self.timerlist.add(timer)

    def delTimer(self, event):
        # todo ファイルの更新チェック
        num = self.listbox.GetItemCount()
        # range(num) だと削除した timer の分だけ範囲外になるので逆から
        for i in range(num-1, -1, -1):
            if self.listbox.IsChecked(i):
                self.timerlist.deleteIndex(i)
                self.listbox.DeleteItem(i)

    def addListBox(self, listbox, timer):
        remain = timer["endtime"] - datetime.datetime.today()
        index = listbox.InsertStringItem(sys.maxint, timer["endtime"].strftime("%H:%M:%S"))
        listbox.SetStringItem(index, 1, MyApp.ListBoxTime(remain))
        listbox.SetStringItem(index, 2, timer["message"])
        return index


    def onTimer(self, event):
        # 一秒ごとに実行する処理
        # タイマーリストの中から指定時間が経過したもののアラーム表示
        # それ以外は画面の更新

        # ファイルの更新があれば読み込み
        self.timerlist.update()
        # このあと timerlist ファイルが保存されるまでの間にファイルの更新があっても無視。
        # ファイルのロックをした方がよいかも。現実的には大丈夫だろうけど。
        if self.timerlist:
            #print self.timerlist
            for key, timer in self.timerlist.timerlist.items():
                # 画面に追加されていないタイマーを追加
                if timer["index"] == "":
                    index = self.addListBox(self.listbox, timer)
                    self.timerlist.refreshIndex(key, index)
                # 時間になったタイマーをアラーム
                if timer["endtime"] < datetime.datetime.today():
                    self.timerlist.delete(key, timer["index"])
                    self.listbox.DeleteItem(timer["index"])
                    MessageFrame(self.frame, "Alarm", timer["message"])
                # 時間になっていないタイマーの画面更新
                else:
                    remain = timer["endtime"] - datetime.datetime.today()
                    self.listbox.SetStringItem(timer["index"], 1, MyApp.ListBoxTime(remain))

    # リストボックスの remain に表示する時間を生成
    @classmethod
    def ListBoxTime(self, timedelta):
        days = timedelta.days
        hours = timedelta.seconds / 60 / 60
        seconds = timedelta.seconds - hours * 60 * 60
        minutes = seconds / 60
        seconds = seconds - minutes * 60

        time = ""
        if days:
            time = "{0}d ".format(days)
        if hours:
            time = "{0}{1:>02d}:".format(time, hours)
        if minutes:
            time = "{0}{1:>02d}:".format(time, minutes)
        time = "{0}{1:>02d}".format(time, seconds)
        return time

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
            self.mtime = os.path.getmtime(self.timerfile)
        except IOError, (errno, strerror):
            self.data = dict()
            if errno != 2: # not exists
                raise

    def save(self, timerlist):
        yaml.dump(timerlist, file(self.timerfile, 'wb'),
                  default_flow_style=False, encoding='utf8',
                  allow_unicode=True)
        self.mtime = os.path.getmtime(self.timerfile)

    def getTimerList(self):
        return self.data

    def isChanged(self):
        if self.mtime < os.path.getmtime(self.timerfile):
            return True
        else:
            return False

class TimerList(object):
    def __init__(self):
        self.timerfile = TimerFile()
        self.timerlist = self.timerfile.getTimerList()
        self.timernum = self.getTimerNum()
        # 起動時に過ぎてしまっているアラームは削除
        # todo? 何を削除したか表示する
        self.deleteOutside()

    def add(self, timer):
        self.timernum = self.timernum + 1
        self.timerlist[self.timernum] = timer
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

    def deleteIndex(self, index):
        # 画面のリストのインデックスを更新
        # 更新しないとインデックスの場所がずれる
        for key, timer in self.timerlist.items():
            if timer["index"] == index:
                del self.timerlist[key]
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
        self.timerfile.save(self.timerlist)

    def getTimerNum(self):
        num = 0
        if self.timerlist:
            for key, value in self.timerlist.items():
                if num < key:
                    num = key
        return num

    @classmethod
    def getRemain(self, counter):
        if counter.isdigit():
            return int(counter) * 60
        else:
            # todo 指定時刻 hh:mm, hh:mm:ss も扱えるように
            # todo? d で日数も扱えるように
            # todo? yyyy-mm-dd も扱えるように
            # 単位が h で時間。それ以外の数字は分
            p = re.compile(r'([h])')
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
            if num != 0:
                total = num * 60 + total
            #print total
            return total

    def update(self):
        if self.timerfile.isChanged():
            self.timerfile.load()
            self.timerlist = self.timerfile.getTimerList()

# タイマーリストをイテレータとして使いたいけどできていない
#    def next(self):
#        self.timerlist.next()
#
#    def __iter__(self):
#        return self

if __name__ == "__main__":
    # コマンドラインからタイマー追加
    argc = len(sys.argv)
    if argc > 1:
        seconds = TimerList.getRemain(sys.argv[1])
        starttime = datetime.datetime.today()
        endtime = starttime + datetime.timedelta(seconds=seconds)
        if argc > 2:
            message = sys.argv[2]
        else:
            message = ""
        timerlist = TimerList()
        timer = {"index": "", "starttime": starttime, "endtime": endtime, "message": message}
        timerlist.add(timer)

    # 二重起動防止
    mut = NamedMutex("multipletimer", True, 0)
    if not mut.acret:
        exit()

    app = MyApp()
    app.MainLoop()
