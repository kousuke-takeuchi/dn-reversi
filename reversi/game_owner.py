import multiprocessing


class GameOwner:
    player_1 = None
    player_2 = None

    def __init__(self, engine):
        self.engine = engine

    def format_message(self, status, **kwargs):
        serializer = StatusSerializer(status=status, **kwargs)
        return serializer.serialize

    def register(self, player):
        if self.player_1 and self.player_2:
            raise Exception('over player limit')
        player_id = self.engine.enter_player()
        player.player_id = player_id
        if not self.player_1:
            self.player_1 = player
        elif not self.player_2:
            self.player_2 = player

    def start_game(self):
        board = self.engine.current_board()
        self.broadcast('on_start', board)

    def update(self):
        player_id = self.engine.waiting_player
        board = self.engine.current_board()
        player = self.get_player(player_id)
        row, col = player.on_update(board)
        board, result, next_player, is_game_over = self.engine.put_piece(player_id, row, col)
        return board, result, is_game_over

    def gameover(self, board, result):
        self.broadcast('on_gameover', board, result)

    def continue_game(self):
        board = self.engine.current_board()
        self.broadcast('on_continue', board)

    def broadcast(self, method, *args, **kwargs):
        getattr(self.player_1, method)(*args, **kwargs)
        getattr(self.player_2, method)(*args, **kwargs)

    def get_player(self, player_id):
        if self.player_1.player_id == player_id:
            return self.player_1
        else:
            return self.player_2
