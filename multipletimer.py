# -*- coding: utf-8 -*-
import os
import time
import sys
import wx
import re
import datetime
from namedmutex import NamedMutex
import yaml

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
        self.timernum = 0
        self.timerlist = TimerList()

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
        self.listbox = wx.ListBox(bottompanel, wx.ID_ANY, style=wx.LB_NEEDED_SB)
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
        #layout.Add(button_1)

        basepanel.SetSizer(layout)
        toppanel.SetSizer(layout_top)
        top1panel.SetSizer(layout_top1)
        top2panel.SetSizer(layout_top2)
        bottompanel.SetSizer(layout_bottom)

        self.frame.Show()

        self.SetTopWindow(self.frame)

        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        return True

    def getCounter(self):
        counter = self.count_text.GetValue()
        if counter.isdigit():
            return int(counter)
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
            return total

    def addTimer(self, event):
        self.timernum = self.timernum + 1
        timer = [self.timernum, datetime.datetime.today(), self.getCounter(), self.message.GetValue()]
        self.timerlist.add(self.timernum, timer)

    def onTimer(self, event):
        if self.timerlist:
            array = list()
            #print self.timerlist
            for key, value in self.timerlist.timerlist.items():
                timeraddtime = value[1]
                timer = value[2]
                endtime = timeraddtime + datetime.timedelta(seconds=timer)
                if endtime < datetime.datetime.today():
                    self.timerlist.delete(key)
                    MessageFrame(self.frame, "Alarm")
                else:
                    delta = endtime - datetime.datetime.today()
                    array.append(endtime.strftime("%H:%M:%S "))
                self.listbox.SetItems(array)

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

class TimerList(object):
    def __init__(self):
        self.timerfile = TimerFile()
        if self.timerfile.data:
            self.timerlist = self.timerfile.data
        else:
            self.timerlist = dict()

    def add(self, num, timer):
        self.timerlist[num] = timer
        self.timerfile.save(self.timerlist)

    def delete(self, num):
        del self.timerlist[num]
        self.timerfile.save(self.timerlist)

# iterater fail
#    def next(self):
#        self.timerlist.next()
#
#    def __iter__(self):
#        return self

if __name__ == "__main__":
    mut = NamedMutex("multipletimer", True, 0)
    if not mut.acret:
        exit()

    app = MyApp()
    app.MainLoop()
