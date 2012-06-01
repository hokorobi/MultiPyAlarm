# -*- coding: utf-8 -*-
import os
import time
import sys
import wx

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

class MyApp(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, wx.ID_ANY, "Multiple Timer", size = (300, 200))
        self.frame.CreateStatusBar()
        basepanel = wx.Panel(self.frame, wx.ID_ANY)

        toppanel = wx.Panel(basepanel, wx.ID_ANY, style = wx.BORDER_SUNKEN)
        message = wx.TextCtrl(toppanel, wx.ID_ANY)
        count_text = wx.TextCtrl(toppanel, wx.ID_ANY)
        button_1 = wx.Button(toppanel, wx.ID_ANY, "add alarm")
        button_1.Bind(wx.EVT_BUTTON, self.startTimer)

        bottompanel = wx.Panel(basepanel, wx.ID_ANY, style = wx.BORDER_SUNKEN)


        layout_top = wx.BoxSizer(wx.HORIZONTAL)
        layout_top.Add(count_text)
        layout_top.Add(button_1)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(toppanel, proportion=1, flag=wx.GROW)
        layout.Add(bottompanel, proportion=1, flag=wx.GROW)
        #layout.Add(button_1)

        basepanel.SetSizer(layout)
        toppanel.SetSizer(layout_top)

        self.frame.Show()

        self.SetTopWindow(self.frame)
        return True

    def startTimer(self, event):
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.timer.Start(3)

    def onTimer(self, event):
        childframe = MessageFrame(self.frame, "Alarm")
        self.timer.Stop()

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
