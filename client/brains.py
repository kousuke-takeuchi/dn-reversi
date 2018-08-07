import math
import copy
import random

from server.engine import will_rotated_cells, can_put
from server.board import Board


class BrainBase:
    player_id = None
    next_player = None
    current_board = None
    current_game = 0
    win = 0
    lose = 0

    def on_update(self):
        pass

    def on_error(self, error):
        if not error.endswith('is invalid'):
            return
        if self.player_id == self.next_player:
            return self.move()

    def on_another_player_exit(self):
        return 'exit'

    def on_gamestart(self):
        pass

    def move_format(self, cell):
        return '{}:{}'.format(cell[0], cell[1])

    def candidate(self):
        # 石が置かれてないものだけに絞る
        blanks = []
        for row in range(8):
            for col in range(8):
                if self.current_board[row][col] == 'BLANK':
                    blanks.append((row, col))
        # 周りに石があるものだけに絞る
        board = self.to_board_obj()
        results = []
        for cell in blanks:
            row, col = cell
            # 一つ以上返せるものだけに絞る
            rotate_cells = will_rotated_cells(board, self.player_id, row, col)
            if can_put(board, self.player_id, row, col) and len(rotate_cells) > 0:
                results.append(cell)
        return results

    def calculate_score(self):
        raise NotImplementedError()

    def select(self, scores):
        raise NotImplementedError()

    def move(self):
        scores = self.calculate_score()
        selection = self.select(scores)
        return self.move_format(selection)

    def on_gameover(self, result):
        self.current_board = None
        self.next_player = None

    def on_receive(self, data):
        if data.status == 'entered':
            self.player_id = data.player_id
        elif data.status == 'start':
            self.current_game = 1
            self.on_gamestart()
            self.next_player = data.next_player
            self.current_board = data.board
            if self.next_player == self.player_id:
                return self.move()
        elif data.status == 'update':
            self.next_player = data.next_player
            self.current_board = data.board
            self.on_update()
            if self.next_player == self.player_id:
                return self.move()
        elif data.status == 'error':
            return self.on_error(data.error)
        elif data.status == 'exit':
            return self.on_another_player_exit()
        elif data.status == 'end':
            self.next_player = None
            self.current_board = data.board
            self.on_gameover(data.result)
            me = data.result[str(self.player_id)]
            enemy = data.result[str(-1*self.player_id)]
            self.win = self.win + 1 if me > enemy else self.win
            self.lose = self.lose + 1 if me < enemy else self.lose
            print(data.result)
            print(self.win)
            print(self.lose)
        elif data.status == 'continue':
            self.current_game += 1
            self.next_player = data.next_player
            self.current_board = data.board
            if self.next_player == self.player_id:
                return self.move()

    def convert_cell(self, value):
        if value == 'WHITE':
            return -1
        elif value == 'BLANK':
            return 0
        elif value == 'BLACK':
            return 1

    def to_board_obj(self):
        raw_board = copy.deepcopy(self.current_board)
        for ridx, row in enumerate(self.current_board):
            for cidx, value in enumerate(row):
                raw_board[ridx][cidx] = self.convert_cell(value)
        return Board(raw=raw_board)


class RandomBrain(BrainBase):
    """おける場所からランダムに選択して適当に置く
    -> 勝率50%
    """
    def normalize_score(self, scores):
        # 正規化する
        result = dict()
        total_score = sum(scores.values())
        for cell, score in scores.items():
            result[cell] = score / total_score
        return result

    def calculate_score(self):
        # すべて同じスコアにする
        candidate = self.candidate()
        scores = dict([(place, 1) for place in candidate])
        return self.normalize_score(scores)

    def select(self, scores):
        # 同じスコアなので、ランダムに選択する
        candidate = list(scores.keys())
        return candidate[random.randrange(len(candidate))]


class ScoreBrainAlpha(RandomBrain):
    """おける場所候補から敵石をたくさん取れる置く場所を優先する
    -> 勝率60%
    """
    def calculate_score(self):
        # 候補の石から、返せる敵石の数をスコアとする
        scores = super(ScoreBrainAlpha, self).calculate_score()
        candidate = list(scores.keys())
        board = self.to_board_obj()
        color = self.player_id
        for cell in candidate:
            row, col = cell
            # 返せる敵石の数を追加
            rotate_cells = will_rotated_cells(board, color, row, col)
            scores[cell] += len(rotate_cells)
        return self.normalize_score(scores)

    def select(self, scores):
        # スコアが一番高いものを返す
        score_values = list(scores.values())
        select_index = score_values.index(max(score_values))
        return list(scores.keys())[select_index]


class ScoreBrainBeta(ScoreBrainAlpha):
    """端を優先してとるようにする
    -> 勝率72%
    """
    def calculate_score(self):
        scores = super(ScoreBrainBeta, self).calculate_score()
        candidate = list(scores.keys())
        for cell in candidate:
            row, col = cell
            current_score = scores[cell]
            # 端の場合は、若干スコアを上げる
            if row == 0 or row == 7 or col == 0 or col == 7:
                plus = math.sqrt(1 - current_score)
                scores[cell] = current_score + plus
        return self.normalize_score(scores)
