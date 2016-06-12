# -*- coding: utf-8 -*-
import wx


class MessageFrame(wx.Frame):
    """アラーム用のメッセージを表示するウィンドウ"""

    def __init__(self, parent, title, message, icon):
        style = wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, parent, title=title, style=style)
        # アイコン設定
        self.SetIcon(icon)
        # キーイベント
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)

        if not message:
            message = "IT'S TIME!"
        panel = wx.Panel(self, wx.ID_ANY)
        font = wx.Font(32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_NORMAL)
        text = wx.StaticText(panel, wx.ID_ANY, message, style=wx.TE_CENTER)
        text.SetFont(font)
        text.CenterOnParent()
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(text, flag=wx.GROW)
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

    def onTimer(self, event):
        """ウィンドウの移動（中心、左、上、下、右、中心）を 2 回"""
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
