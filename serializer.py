"""サーバーからコントローラへ現在の状態を渡す際のデータフォーマット
"""
import json


class StatusSerializer:
    def __init__(self, status=None, player_id=None, next_player=None, board=None, error=None):
        self.status = status
        self.player_id = player_id
        self.next_player = next_player
        self.board = board
        self.error = error

    @property
    def serialize(self):
        data = dict(
            status=self.status,
            player_id=self.player_id,
            next_player=self.next_player,
            board=self.board,
            error=self.error and str(self.error)
        )
        return json.dumps(data).encode('utf-8')

    @classmethod
    def deserialize(cls, message):
        data = json.loads(message)
        return Serializer(**data)
