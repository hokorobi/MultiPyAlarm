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
import win32gui
import imp

# exe にした場合も実行ファイルのパスが取得できるように
def main_is_frozen():
    return (hasattr(sys, "frozen") # new py2exe
            or hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
    if main_is_frozen():
        return os.path.abspath(os.path.dirname(sys.executable))
    return os.path.abspath(os.path.dirname(sys.argv[0]))

# アラームリストの画面表示
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

# 時間が来たらメッセージ用のウィンドウを表示
class MessageFrame(wx.Frame):
    def __init__(self, parent, title, message, icon):
        style = wx.STAY_ON_TOP|wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, parent, title=title, style=style)
        # アイコン設定
        self.SetIcon(icon)
        # キーイベント
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        if not message:
            message = "IT'S TIME!"
        panel = wx.Panel(self, wx.ID_ANY)
        font = wx.Font(32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text = wx.StaticText(panel, wx.ID_ANY, message, style = wx.TE_CENTER)
        text.SetFont(font)
        text.CenterOnParent()
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(text, flag = wx.GROW)
        panel.SetSizer(layout)
        # 画面から文字がはみ出ないように折り返し
        # 全角文字がつながっていると単語として扱われて折り返しできない
        text.Wrap(self.GetSize().width)
        self.Show(True)

        # ウィンドウ表示時の位置
        self.pos = self.GetPosition()

        # 0.1 秒ごとにウィンドウを移動させて目立たせる
        self.movecount = 0
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        # ESC でウィンドウクローズ
        if key == wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()


    # ウィンドウの移動（中心、左、上、下、右、中心）を 2 回
    def onTimer(self, event):
        if self.movecount > 10:
            self.timer.Stop()
        self.movecount = self.movecount + 1
        pos = self.GetPosition()
        if self.pos[0] == pos[0]:
            if self.pos[1] == pos[1]:
                self.Move((self.pos[0] - 50, self.pos[1]))
            elif self.pos[1] + 50 == pos[1]:
                self.Move((self.pos[0], self.pos[1] - 50))
            elif self.pos[1] - 50 == pos[1]:
                self.Move((self.pos[0] + 50, self.pos[1]))
            else:
                self.Move((self.pos[0], self.pos[1]))
        elif self.pos[0] + 50 == pos[0]:
            self.Move((self.pos[0], self.pos[1]))
        elif self.pos[0] - 50 == pos[0]:
            self.Move((self.pos[0], self.pos[1] - 50))

class ListFrame(wx.Frame):
    def __init__(self, parent, timerlist, icon):
        wx.Frame.__init__(self, parent, title='MultiPyAlarm', size=(300, 200))
        self.timerlist = timerlist

        self.SetIcon(icon)

        self.CreateStatusBar()
        basepanel = wx.Panel(self, wx.ID_ANY)

        toppanel = wx.Panel(basepanel, wx.ID_ANY, style = wx.BORDER_SUNKEN)

        top1panel = wx.Panel(toppanel, wx.ID_ANY)
        self.count_text = wx.TextCtrl(top1panel, wx.ID_ANY)
        button_add = wx.Button(top1panel, wx.ID_ANY, "&add")
        button_add.Bind(wx.EVT_BUTTON, self.add_timer)
        button_del = wx.Button(top1panel, wx.ID_ANY, "&del")
        button_del.Bind(wx.EVT_BUTTON, self.del_checkeditem)

        top2panel = wx.Panel(toppanel, wx.ID_ANY)
        self.message = wx.TextCtrl(top2panel, wx.ID_ANY)


        bottompanel = wx.Panel(basepanel, wx.ID_ANY, style = wx.BORDER_SUNKEN)
        self.listbox = CheckListCtrl(bottompanel)
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.listbox.InsertColumn(0, 'alarm', width=80)
        self.listbox.InsertColumn(1, 'left')
        self.listbox.InsertColumn(2, 'message')

        layout_bottom = wx.BoxSizer(wx.HORIZONTAL)
        layout_bottom.Add(self.listbox, proportion=1, flag=wx.GROW|wx.ALL, border=3)

        layout_top1 = wx.BoxSizer(wx.HORIZONTAL)
        layout_top1.Add(self.count_text)
        layout_top1.Add(button_add)
        layout_top1.Add(button_del)

        layout_top2 = wx.BoxSizer(wx.HORIZONTAL)
        layout_top2.Add(self.message, proportion=1, flag=wx.GROW)

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
        for key, timer in self.timerlist.items():
            newindex = self.add_item(self.listbox, timer)
            self.timerlist.refresh_index(key, newindex)
            if not timer["displayed"]:
                self.timerlist.displayed(key)

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        # listbox のスペースでチェックの切り替え（複数選択可）
        if key == wx.WXK_SPACE:
            index = self.listbox.GetFirstSelected()
            while index != -1:
                if self.listbox.IsChecked(index):
                    self.listbox.CheckItem(index, check=False)
                else:
                    self.listbox.CheckItem(index, check=True)
                index = self.listbox.GetNextSelected(index)
        else:
            event.Skip()

    # アラームタイマー追加
    # 追加するのはファイルのみ
    # 画面への反映は、onTimer で
    def add_timer(self, event):
        timer = TimerList.get_timer(self.count_text.GetValue(), self.message.GetValue())
        if timer:
            timer['displayed'] = True
            self.timerlist.add(timer)
        else:
            wx.MessageBox('invalid time', 'Error', wx.OK | wx.ICON_INFORMATION)

    def del_checkeditem(self, event):
        # todo ファイルの更新チェック
        num = self.listbox.GetItemCount()
        # range(num) だと削除した timer の分だけ範囲外になるので逆から
        for i in range(num-1, -1, -1):
            if self.listbox.IsChecked(i):
                self.timerlist.delete(i)
                self.listbox.DeleteItem(i)

    def add_item(self, listbox, timer):
        left = timer["endtime"] - datetime.datetime.today()
        index = self.listbox.InsertStringItem(sys.maxint, timer["endtime"].strftime("%H:%M:%S"))
        self.listbox.SetStringItem(index, 1, self.get_listbox_left(left))
        self.listbox.SetStringItem(index, 2, timer["message"])
        return index

    def del_item(self, index):
        self.listbox.DeleteItem(index)

    # listbox の更新
    def update_items(self):
        if self.timerlist:
            for key, timer in self.timerlist.items():
                # 画面に追加されていないタイマーを追加
                if timer["index"] is None or timer["index"] == "":
                    index = self.add_item(self.listbox, timer)
                    self.timerlist.refresh_index(key, index)
                    if not timer["displayed"]:
                        self.timerlist.displayed(key)
                # タイマーの画面更新
                left = timer["endtime"] - datetime.datetime.today()
                self.listbox.SetStringItem(timer["index"], 1, self.get_listbox_left(left))

    # リストボックスの left に表示する時間を生成
    @classmethod
    def get_listbox_left(self, timedelta):
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
            for key, timer in self.timerlist.timerlist.items():
                # 時間になったタイマーをアラーム
                if timer["endtime"] < datetime.datetime.today():
                    # listframe が表示されていたら
                    if self.listframe:
                        self.listframe.del_item(timer["index"])
                    self.timerlist.delete(timer["index"])
                    MessageFrame(None, "Alarm", timer["message"], self.icon)
                if not self.listframe:
                    if not timer["displayed"]:
                        balloonmessage = '{0} {1}'.format(timer["endtime"].strftime("%H:%M:%S"), timer["message"])
                        self.tb_ico.ShowBalloonTip('add alarm', balloonmessage)
                        self.timerlist.displayed(key)
            # listframe が表示されていたら
            if self.listframe:
                self.listframe.update_items()

# タイマーリストのファイル処理
class TimerFile(object):
    def __init__(self):
        self.timerfile = os.path.join(get_main_dir(), 'timerlist')
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

    def get_timerlist(self):
        return self.data

    def ischanged(self):
        if self.mtime < os.path.getmtime(self.timerfile):
            return True
        else:
            return False

class TimerList(object):
    def __init__(self):
        self.timerfile = TimerFile()
        self.timerlist = self.timerfile.get_timerlist()
        self.timernum = self.get_timernum()
        # 起動時に過ぎてしまっているアラームは削除
        # todo? 何を削除したか表示する
        self.delete_outside()

    def add(self, timer):
        self.timernum = self.timernum + 1
        self.timerlist[self.timernum] = timer
        self.timerfile.save(self.timerlist)

    def delete(self, index):
        for key, timer in self.timerlist.items():
            if timer["index"] == index:
                del self.timerlist[key]
            # 画面のリストのインデックスを更新
            # 更新しないと画面の listbox とずれる
            if timer["index"] > index:
                timer["index"] = timer["index"] - 1
                self.timerlist[key] = timer
        self.timerfile.save(self.timerlist)

    def delete_outside(self):
        for key, timer in self.timerlist.items():
            if timer is None or timer["endtime"] < datetime.datetime.today():
                del self.timerlist[key]
        self.timerfile.save(self.timerlist)

    def refresh_index(self, key, index):
        self.timerlist[key]["index"] = index
        self.timerfile.save(self.timerlist)

    def get_timernum(self):
        num = 0
        if self.timerlist:
            for key, value in self.timerlist.items():
                if num < key:
                    num = key
        return num

    @classmethod
    def get_timer(self, inputtime, message):
        try:
            starttime = datetime.datetime.now()
            inputtime = inputtime.strip()
            if inputtime.isdigit():
                # 数字だけ
                m = int(inputtime)
                endtime = starttime + datetime.timedelta(seconds=m * 60)
            elif re.match('[0-9hms ]+$', inputtime):
                # 1h, 1m, 1s など
                def divlist(inputtime):
                    # 数字と文字を分割してリストとして返す
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

                def get_timedelta_map(times):
                    delta = {'h':0, 'm':0, 's':0}
                    t = ''
                    for x in times[::-1]:
                        if x.isdigit():
                            delta[t] = delta[t] + int(x)
                        else:
                            t = x
                    return delta

                hms = get_timedelta_map(divlist(inputtime))
                endtime = starttime + datetime.timedelta(hours=hms['h'], minutes=hms['m'], seconds=hms['s'])
            elif re.match('[0-9]+:[0-9]+$', inputtime):
                hm = [0 if x == '' else int(x) for x in inputtime.split(':', 1)]
                endtime = starttime.replace(hour=hm[0], minute=hm[1], second=0)
                if starttime > endtime:
                    endtime = endtime + datetime.timedelta(days=1)
            else:
                # todo? d で日数も扱えるように
                # todo? yyyy-mm-dd も扱えるように
                raise 'invalid time'
            return {'index': '', 'starttime': starttime, 'endtime': endtime, 'message': message, 'displayed': False}
        except:
            return None

    def update(self):
        if self.timerfile.ischanged():
            self.timerfile.load()
            self.timerlist = self.timerfile.get_timerlist()

    def items(self):
        return self.timerlist.items()

    def displayed(self, key):
        self.timerlist[key]["displayed"] = True
        self.timerfile.save(self.timerlist)

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
        if not self.parent.listframe:
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
        timer = TimerList.get_timer(sys.argv[1], message)
        if timer:
            timerlist = TimerList()
            timerlist.add(timer)
        else:
            ex = wx.App()
            wx.MessageBox('invalid time', 'Error', wx.OK | wx.ICON_INFORMATION)
            ex.Destroy()

    # 二重起動防止
    mut = NamedMutex("MultiPyAlarm", True, 0)
    if not mut.acret:
        sys.exit()

    app = MyApp()
    app.MainLoop()
