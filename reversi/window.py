"""オセロ盤面の現在を描画
"""
import wx

from .engine import Engine, EVT_BOARD_EVENT
from .pieces import BLANK, WHITE, BLACK
from .threads import GameThread
from .game_owner import GameOwner


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
PANEL_WIDTH = 500
PANEL_HEIGHT = 500


class GameWindow(wx.Frame):
    title = 'Reversi'

    def __init__(self, brain1, brain2, game_count=100, tick=0.5):
        size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        super(GameWindow, self).__init__(None, title=self.title)
        self.initPanel()
        self.Fit()

        owner = GameOwner(self.engine)
        owner.register(brain1)
        owner.register(brain2)
        self.game_thread = GameThread(owner, game_count=game_count, tick=tick)
        self.game_thread.start()

    def initPanel(self):
        size = (PANEL_WIDTH, PANEL_HEIGHT)
        self.panel = wx.Panel(self, size=size)
        self.panel.SetBackgroundColour('BLACK')
        self.panel.Bind(wx.EVT_PAINT, self.refresh)
        self.panel.Bind(EVT_BOARD_EVENT, self.updateData)
        self.panel.Bind(wx.EVT_CLOSE, self.onClose)
        self.engine = Engine(self.panel)

    def updateData(self, event):
        self.panel.Refresh()

    def refresh(self, event):
        dc = wx.PaintDC(self.panel)
        pw, ph = self.panel.GetSize()

        # background
        dc.SetBrush(wx.Brush('#228b22'))
        dc.DrawRectangle(0, 0, pw, ph)

        # grid
        dc.SetBrush(wx.Brush('BLACK'))
        px, py = pw/8, ph/8
        for i in range(8):
            dc.DrawLine(i*px, 0, i*px, ph)
            dc.DrawLine(0, i*py, pw, i*py)
        dc.DrawLine(pw-1, 0, pw-1, ph-1)
        dc.DrawLine(0, ph-1, pw-1, ph-1)

        # stones
        brushes = {
            WHITE: wx.Brush('WHITE'),
            BLACK: wx.Brush('BLACK')
        }
        margin = 10
        for row in range(self.engine.board.num_rows):
            for col in range(self.engine.board.num_cols):
                c = self.engine.board.get_raw_piece(row, col)
                if c != BLANK:
                    dc.SetBrush(brushes[c])
                    dc.DrawEllipse(col*py+margin/2, row*px+margin/2, px-margin, py-margin)

    def onClose(self, evt):
        self.game_thread.stop()
        self.Destroy()
