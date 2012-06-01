# -*- coding: utf-8 -*-
import os
import time
import sys
import wx
import re
import datetime

class MessageFrame(wx.Frame):
    def __init__(self, parent, title, message="UP ON TIME"):
        wx.Frame.__init__(self, parent, title=title)

        panel = wx.Panel(self, wx.ID_ANY)
        text = wx.StaticText(panel, wx.ID_ANY, message, style = wx.TE_CENTER)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(text, flag = wx.GROW)
        panel.SetSizer(layout)
        self.Show(True)

        self.alarm_move_window(self)

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

class MyTimer(wx.Timer):
    def __init__(self, num, datetimeadd, second, message="UP ON TIME"):
        wx.Timer.__init__(self)
        self.num = num
        self.datetimeadd = datetimeadd
        self.second = second
        self.message = message


class MyApp(wx.App):
    self.timernum = 0

    def OnInit(self):
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
        #layout.Add(button_1)

        basepanel.SetSizer(layout)
        toppanel.SetSizer(layout_top)
        top1panel.SetSizer(layout_top1)
        top2panel.SetSizer(layout_top2)

        self.frame.Show()

        self.SetTopWindow(self.frame)
        return True

    def addTimer(self, event):
        self.timernum = self.timernum + 1
        timer = MyTimer(self, self.timernum, datetime.datetime.today(), self.message.getValue())
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        counter = self.count_text.GetValue()
        if counter.isdigit():
            self.timer.Start(int(counter) * 1000)
        else:
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
            if total != 0:
                self.timer.Start(total * 1000)

    def onTimer(self, event):
        childframe = MessageFrame(self.frame, "Alarm")
        self.timer.Stop()

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
