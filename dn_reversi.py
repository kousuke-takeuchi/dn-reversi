import wx
from reversi.window import GameWindow


def start_game(brain1, brain2, game_count=100, tick=0.5):
    app = wx.App(False)
    window = GameWindow(brain1, brain2, game_count=game_count, tick=tick)
    window.Show()
    app.MainLoop()
