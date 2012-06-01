# -*- coding: utf-8 -*-
import os
import time
import sys
import wx

class MessageFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
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
        frame = wx.Frame(None, wx.ID_ANY, "Multiple Timer", size = (300, 200))
        frame.CreateStatusBar()
        panel = wx.Panel(frame, wx.ID_ANY)

        button_1 = wx.Button(panel, wx.ID_ANY, "alarm")
        button_1.Bind(wx.EVT_BUTTON, alarm)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(button_1)

        panel.SetSizer(layout)

        self.SetTopWindow(frame)
        return True

    def alarm(event):
        childframe = MessageFrame(topframe, "Alarm")

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
