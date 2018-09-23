import wx

from server.window import GameWindow
from server.socket import MessageServerFactory, reactor as server_reactor


if __name__ == '__main__':
    host = '127.0.0.1'
    port = '5001'
    tick = 1000

    # Open reversi GUI Windown
    app = wx.App(False)
    window = GameWindow()
    window.Show()
    # run socket server
    server_reactor.registerWxApp(app)
    url = 'ws://{}:{}'.format(host, port)
    factory = MessageServerFactory(url, window)
    server_reactor.listenTCP(int(port), factory)
    server_reactor.run()
