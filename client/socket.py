from twisted.internet import reactor, protocol
from twisted.protocols import basic
import websocket

from .brain import Brain


class DataForwardingProtocol(basic.LineReceiver):
    def __init__(self):
        self.brain = Brain()

    def dataReceived(self, data):
        serializer = Serializer.deserialize(data)
        # brainにデータを渡して、処理したデータをサーバーに送る
        self.brain.set_board(serializer.board)

    def connectionMade(self):
        print('connected')


class MessageClientFactory(protocol.ClientFactory):
    def __init__(self):
        self.protocol = DataForwardingProtocol

    def clientConnectionLost(self, transport, reason):
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()
