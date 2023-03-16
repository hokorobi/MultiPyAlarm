# -*- coding: utf-8 -*-
import datetime
import sys

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


class CheckListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        ListCtrlAutoWidthMixin.__init__(self)


def _get_listbox_left(timedelta):
    """リストボックスの left に表示する時間を生成"""
    days = timedelta.days
    hours = timedelta.seconds // 60 // 60
    minutes = (timedelta.seconds - hours * 60 * 60) // 60
    seconds = timedelta.seconds - hours * 60 * 60 - minutes * 60

    days_str = ""
    hours_str = ""
    minutes_str = "00:"
    seconds_str = "00"

    if days:
        days_str = "{0}d ".format(days)
    if hours:
        hours_str = "{0:>02d}:".format(hours)
    if minutes:
        minutes_str = "{0:>02d}:".format(minutes)
    if seconds:
        seconds_str = "{0:>02d}".format(seconds)
    return "".join((days_str, hours_str, minutes_str, seconds_str))


class ListFrame(wx.Frame):
    """タイマーリストウィンドウ"""

    def __init__(self, parent, timerlist, icon):
        wx.Frame.__init__(self, parent, title="MultiPyAlarm", size=(300, 200))
        self.timerlist = timerlist

        self.SetIcon(icon)

        self.CreateStatusBar()
        basepanel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)

        self.count_text = wx.TextCtrl(basepanel, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.count_text.Bind(wx.EVT_TEXT_ENTER, self._add_timer)

        button_add = wx.Button(basepanel, wx.ID_ANY, "&add")
        button_add.Bind(wx.EVT_BUTTON, self._add_timer)

        self.listbox = CheckListCtrl(basepanel)
        self.listbox.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.listbox.InsertColumn(0, "alarm", width=80)
        self.listbox.InsertColumn(1, "left")
        self.listbox.InsertColumn(2, "message")

        # FIXME: 起動時に listbox の alarm にゴミが表示される
        sizer = wx.FlexGridSizer(3, 1, gap=wx.Size(0,0))
        sizer.Add(self.count_text, flag=wx.GROW)
        sizer.Add(button_add, flag=wx.GROW)
        sizer.Add(self.listbox, flag=wx.GROW)
        sizer.AddGrowableRow(2)
        sizer.AddGrowableCol(0)
        basepanel.SetSizer(sizer)

        # タイマーリストを画面のリストに追加
        for key, timer in self.timerlist.items():
            newindex = self._add_item(self.listbox, timer)
            self.timerlist.refresh_index(key, newindex)
            if not timer["displayed"]:
                self.timerlist.displayed(key)

    def OnDoubleClick(self, event):
        index = self.listbox.GetFirstSelected()
        self.timerlist.delete_from_listbox(index)
        self.listbox.DeleteItem(index)

    def _add_timer(self, event):
        """アラームタイマー追加

        ファイルに対してタイマーを追加し、onTimer で画面へ反映する。
        """
        try:
            strings = self.count_text.GetValue().split(' ', 1)
            if len(strings) == 1:
                countText = strings[0]
                message = ''
            else:
                countText = strings[0]
                message = strings[1]
            self.timerlist.add(countText, message, True)
        except Exception:
            wx.MessageBox("invalid time", "Error", wx.OK | wx.ICON_INFORMATION)

    def _add_item(self, listbox, timer):
        left = timer["endtime"] - datetime.datetime.today()
        index = self.listbox.InsertItem(
            2147483647, timer["endtime"].strftime("%H:%M:%S")
        )
        self.listbox.SetItem(index, 1, _get_listbox_left(left))
        self.listbox.SetItem(index, 2, timer["message"])
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
            self.listbox.SetItem(timer["index"], 1, _get_listbox_left(left))
