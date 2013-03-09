# -*- coding: utf-8 -*-
import wx
import datetime
import sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from timerlist import TimerList


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)


class ListFrame(wx.Frame):
    """タイマーリストウィンドウ"""

    def __init__(self, parent, timerlist, icon):
        wx.Frame.__init__(self, parent, title='MultiPyAlarm', size=(300, 200))
        self.timerlist = timerlist

        self.SetIcon(icon)

        self.CreateStatusBar()
        basepanel = wx.Panel(self, wx.ID_ANY)

        toppanel = wx.Panel(basepanel, wx.ID_ANY, style=wx.BORDER_SUNKEN)

        top1panel = wx.Panel(toppanel, wx.ID_ANY)
        self.count_text = wx.TextCtrl(top1panel, wx.ID_ANY)
        button_add = wx.Button(top1panel, wx.ID_ANY, "&add")
        button_add.Bind(wx.EVT_BUTTON, self._add_timer)
        button_del = wx.Button(top1panel, wx.ID_ANY, "&del")
        button_del.Bind(wx.EVT_BUTTON, self._del_checkeditem)

        top2panel = wx.Panel(toppanel, wx.ID_ANY)
        self.message = wx.TextCtrl(top2panel, wx.ID_ANY)

        bottompanel = wx.Panel(basepanel, wx.ID_ANY, style=wx.BORDER_SUNKEN)
        self.listbox = CheckListCtrl(bottompanel)
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.listbox.InsertColumn(0, 'alarm', width=80)
        self.listbox.InsertColumn(1, 'left')
        self.listbox.InsertColumn(2, 'message')

        layout_bottom = wx.BoxSizer(wx.HORIZONTAL)
        layout_bottom.Add(self.listbox, proportion=1, flag=wx.GROW | wx.ALL,
                          border=3)

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
            newindex = self._add_item(self.listbox, timer)
            self.timerlist.refresh_index(key, newindex)
            if not timer["displayed"]:
                self.timerlist.displayed(key)

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        # listbox のスペースでチェックの切り替え（複数選択可）
        if key != wx.WXK_SPACE:
            event.Skip()
            return
        index = self.listbox.GetFirstSelected()
        while index != -1:
            if self.listbox.IsChecked(index):
                self.listbox.CheckItem(index, check=False)
            else:
                self.listbox.CheckItem(index, check=True)
            index = self.listbox.GetNextSelected(index)

    def _add_timer(self, event):
        """アラームタイマー追加

        ファイルに対してタイマーを追加し、onTimer で画面へ反映する。
        """
        try:
            self.timerlist.add(self.count_text.GetValue(),
                               self.message.GetValue(), True)
        except:
            wx.MessageBox('invalid time', 'Error', wx.OK | wx.ICON_INFORMATION)

    def _del_checkeditem(self, event):
        """todo ファイルの更新チェック"""
        num = self.listbox.GetItemCount()
        # range(num) だと削除した timer の分だけ範囲外になるので逆から
        for i in range(num-1, -1, -1):
            if self.listbox.IsChecked(i):
                self.timerlist.delete_from_listbox(i)
                self.listbox.DeleteItem(i)

    def _add_item(self, listbox, timer):
        left = timer["endtime"] - datetime.datetime.today()
        index = self.listbox.InsertStringItem(
            sys.maxint, timer["endtime"].strftime("%H:%M:%S"))
        self.listbox.SetStringItem(index, 1, self._get_listbox_left(left))
        self.listbox.SetStringItem(index, 2, timer["message"])
        return index

    def del_item(self, index):
        self.listbox.DeleteItem(index)

    def update_items(self):
        """listbox の更新"""
        if not self.timerlist:
            return
        for key, timer in self.timerlist.items():
            # 画面に追加されていないタイマーを追加
            if timer["index"] is None or timer["index"] == "":
                index = self._add_item(self.listbox, timer)
                self.timerlist.refresh_index(key, index)
                if not timer["displayed"]:
                    self.timerlist.displayed(key)
            # タイマーの画面更新
            left = timer["endtime"] - datetime.datetime.today()
            self.listbox.SetStringItem(timer["index"], 1,
                                           self._get_listbox_left(left))

    def _get_listbox_left(self, timedelta):
        """リストボックスの left に表示する時間を生成"""
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
