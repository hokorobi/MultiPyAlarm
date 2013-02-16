# -*- coding: utf-8 -*-
import os
import time
import sys
import wx
import datetime
from namedmutex import NamedMutex
import win32api
import win32gui
from messageframe import MessageFrame
from listframe import ListFrame
from timerlist import TimerList

class MyApp(wx.App):
    #def __init__(self):
    #    wx.App.__init__(self,False)

    def OnInit(self):
        # アイコン取得
        exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
        self.icon = wx.Icon(exeName, wx.BITMAP_TYPE_ICO)

        # タスクトレイにアイコン表示
        self.tb_ico = MyTaskBar(self, self.icon)

        # アラームタイマーのリスト
        self.timerlist = TimerList()

        # 不可視のトップウィンドウ
        frame = wx.Frame(None)
        self.SetTopWindow(frame)

        # メインウィンドウ描画
        self.listframe = ListFrame(None, self.timerlist, self.icon)
        self.listframe.Show()

        #タイマースタート
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        return True

    def onTimer(self, event):
        # 一秒ごとに実行する処理
        # タイマーリストの中から指定時間が経過したもののアラーム表示
        # ListFrame があれば、その画面の更新

        # ファイルの更新があれば読み込み
        self.timerlist.update()
        # このあと timerlist ファイルが保存されるまでの間にファイルの更新があっても無視。
        # ファイルのロックをした方がよいかも。現実的には大丈夫だろうけど。
        if self.timerlist:
            #print self.timerlist
            for key, timer in self.timerlist.items():
                # 時間になったタイマーをアラーム
                if timer["endtime"] < datetime.datetime.today():
                    # listframe が表示されていたら
                    if self.listframe:
                        self.listframe.del_item(timer["index"])
                    self.timerlist.delete(key)
                    MessageFrame(None, "Alarm", timer["message"], self.icon)
                if not self.listframe:
                    if not timer["displayed"]:
                        balloonmessage = '{0} {1}'.format(timer["endtime"].strftime("%H:%M:%S"), timer["message"])
                        self.tb_ico.ShowBalloonTip('add alarm', balloonmessage)
                        self.timerlist.displayed(key)
            # listframe が表示されていたら
            if self.listframe:
                self.listframe.update_items()

class MyTaskBar(wx.TaskBarIcon):
    def __init__(self, parent, icon):
        wx.TaskBarIcon.__init__(self)
        self.parent = parent
        self.icon = icon

        self.SetIcon(self.icon, 'MultiPyAlarm')
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTbiLeftDoubleClicked)

    def CreatePopupMenu(self):
        traymenu = wx.Menu()
        id = wx.NewId()
        item = wx.MenuItem(traymenu, id=id, text=u'&Quit')
        self.Bind(wx.EVT_MENU, self.OnQuit, id=id)
        traymenu.AppendItem(item)
        return traymenu

    def OnTbiLeftDoubleClicked(self, evt):
        if self.parent.listframe:
            self.parent.listframe.Raise()
        else:
            self.parent.listframe = ListFrame(None, self.parent.timerlist, self.icon)
            self.parent.listframe.Show()

    def OnQuit(self, evt):
        self.RemoveIcon()
        sys.exit(0)

    def ShowBalloonTip(self, title, msg):
        """
        Show Balloon tooltip
         @param title The title of the balloon
         @param msg   The tooltip message
        """
        if os.name == 'nt':
            try:
                self.SetBalloonTip(self.parent.icon.GetHandle(), title, msg)
                self.SetIcon(self.icon, 'MultiPyAlarm')
            except Exception, e:
                print e

    def SetBalloonTip(self, hicon, title, msg):
        """
        Don't call this method, call ShowBalloonTip instead
        """
        lpdata = (self.GetIconHandle(),
                  99,
                  win32gui.NIF_MESSAGE | win32gui.NIF_ICON | win32gui.NIF_INFO,
                  0,
                  hicon,
                  '', msg, 0, title, win32gui.NIIF_INFO)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, lpdata)

    def GetIconHandle(self):
        """
        Find the icon window.
        this is ugly but for now there is no way
        to find this window directly from wx
        """
        if not hasattr(self, "_chwnd"):
            try:
                for handle in wx.GetTopLevelWindows():
                    handle = handle.GetHandle()
                    if len(win32gui.GetWindowText(handle)) == 0 and \
                       win32gui.GetWindowRect(handle) == (0,0,400,250):
                        self._chwnd = handle
                        break
                if not hasattr(self, "_chwnd"):
                    raise Exception
            except:
                raise Exception, "Icon window not found"
        return self._chwnd


if __name__ == "__main__":
    # コマンドラインからタイマー追加
    argc = len(sys.argv)
    if argc > 1:
        if argc > 2:
            message = " ".join(sys.argv[2:])
        else:
            message = ""
        try:
            timerlist = TimerList()
            timerlist.add(sys.argv[1], message)
            del timerlist
        except:
            ex = wx.App()
            wx.MessageBox('invalid time', 'Error', wx.OK | wx.ICON_INFORMATION)
            ex.Destroy()

    # 二重起動防止
    mut = NamedMutex("MultiPyAlarm", True, 0)
    if not mut.acret:
        sys.exit()

    app = MyApp()
    app.MainLoop()
