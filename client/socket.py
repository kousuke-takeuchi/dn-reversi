from serializer import StatusSerializer

import websocket


"""自作のプレイヤーを設定したプロトコルを作成
"""
class BrainMessageReceiver:
    def __init__(self, brain):
        self.brain = brain

    def on_message(self, ws, message):
        try:
            serializer = StatusSerializer.deserialize(data=message)
            response = self.brain.on_receive(serializer)
            if response:
                self.send_message(response)
        except Exception as exc:
            self.on_error(ws, exc)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        pass

    def on_open(self, ws):
        pass


class MesssageClientReactor:
    def connectTCP(self, host, port, protocol):
        self.host = host
        self.port = port
        self.protocol = protocol

    def connect(self):
        url = 'ws://{}:{}'.format(self.host, self.port)
        handlers = dict(
            on_message=self.protocol.on_message,
            on_error=self.protocol.on_error,
            on_close=self.protocol.on_close,
        )
        self.ws = websocket.WebSocketApp(url, **handlers)
        self.ws.on_open = self.protocol.on_open
        setattr(self.protocol, 'send_message', self.send_message)

    def send_message(self, message):
        self.ws.send(message)

    def run(self):
        self.connect()
        self.ws.run_forever()

reactor = MesssageClientReactor()
