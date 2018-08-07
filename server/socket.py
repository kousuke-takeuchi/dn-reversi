"""オセロゲームのコントローラとの接続ポートを管理
"""
from twisted.internet import wxreactor
from twisted.internet.error import ReactorAlreadyInstalledError

try:
    wxreactor.install()
except ReactorAlreadyInstalledError:
    pass

# import twisted reactor *only after* installing wxreactor
from twisted.internet import reactor
from twisted.protocols import basic
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

from serializer import StatusSerializer


class MessageProtocol(WebSocketServerProtocol):
    player_id = None

    def sendFormatMessage(self, status, **kwargs):
        serializer = StatusSerializer(status=status, **kwargs)
        self.sendMessage(serializer.serialize, False)

    def broadcastFormatMessage(self, status, **kwargs):
        serializer = StatusSerializer(status=status, **kwargs)
        self.factory.broadcast(serializer.serialize, False)

    def onOpen(self):
        self.factory.register(self)
        # 参加可能かどうかチェック
        try:
            self.player_id = self.factory.engine.enter_player()
            self.sendFormatMessage('entered', player_id=self.player_id)
        except Exception as exc:
            self.sendFormatMessage('error', error=exc)
            self.transport.loseConnection()
        waiting_player = self.factory.engine.waiting_player
        if waiting_player:
            board = self.factory.engine.current_board()
            self.broadcastFormatMessage('start', next_player=waiting_player, board=board)
        print('Connection from: {}'.format(self.transport.getPeer().host))

    def onMessage(self, payload, isBinary):
        # データの処理
        if payload == 'exit' or payload == b'exit':
            self.broadcastFormatMessage('exit')
            self.transport.loseConnection()
            return
        try:
            row, col = payload.decode('utf-8').split(':')
            row = int(row)
            col = int(col)
            board, result, next_player, is_game_over = self.factory.engine.put_piece(self.player_id, row, col)
            if is_game_over:
                self.broadcastFormatMessage('end', board=board, result=result)
                waiting_player = self.factory.engine.waiting_player
                board = self.factory.engine.current_board()
                self.broadcastFormatMessage('continue', next_player=waiting_player, board=board)
            else:
                self.broadcastFormatMessage('update', next_player=next_player, board=board)
        except Exception as exc:
            self.sendFormatMessage('error', error=exc)

    def onClose(self, wasClean, code, reason):
        print('Connection lost')
        print(reason)
        self.factory.engine.exit_player(self.player_id)
        self.factory.unregister(self)
        self.broadcastFormatMessage('exit')

# class MessageServerFactory(protocol.ServerFactory):
class MessageServerFactory(WebSocketServerFactory):
    protocol  = MessageProtocol
    clients = []

    def __init__(self, url, window):
        super(MessageServerFactory, self).__init__(url)
        self.clients = []
        self.window = window
        self.engine = window.engine

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)
            print("registered client {}".format(client.peer))

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)
            print("unregistered client {}".format(client.peer))

    def broadcast(self, payload, isBinary):
        for c in self.clients:
            c.sendMessage(payload, isBinary)

    def buildProtocol(self, *args, **kwargs):
        protocol = self.protocol()
        protocol.factory = self
        return protocol
