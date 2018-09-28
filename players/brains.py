import math
import copy
import random

from reversi.engine import will_rotated_cells, can_put
from reversi.board import Board


class MessageProtocol:
    player_id = None

    def on_start(self, board):
        pass
    def on_update(self, board):
        pass
    def on_failure(self, board):
        pass
    def on_gameover(self, board, result):
        pass
    def on_continue(self, board):
        pass

class BrainBase(MessageProtocol):
    next_player = None
    current_board = None
    current_game = 0
    win = 0
    lose = 0

    def on_start(self, board):
        self.current_game = 1
        self.current_board = board

    def on_update(self, board):
        self.current_board = board
        return self.move()

    def on_failure(self):
        return self.move()

    def on_gameover(self, board, result):
        self.current_board = board
        me = result[self.player_id]
        enemy = result[-1*self.player_id]
        self.win = self.win + 1 if me > enemy else self.win
        self.lose = self.lose + 1 if me < enemy else self.lose
        print(result)
        print(self.win)
        print(self.lose)

    def on_continue(self, board):
        self.current_game += 1
        self.current_board = board
        return self.move()

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
        return selection[0], selection[1]

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


class ExpertBrainAlpha(RandomBrain):
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


class ExpertBrain(ExpertBrainAlpha):
    """端を優先してとるようにする
    -> 勝率72%
    """
    def calculate_score(self):
        scores = super(ExpertBrainAlpha, self).calculate_score()
        candidate = list(scores.keys())
        for cell in candidate:
            row, col = cell
            current_score = scores[cell]
            # 端の場合は、若干スコアを上げる
            if row == 0 or row == 7 or col == 0 or col == 7:
                plus = math.sqrt(1 - current_score)
                scores[cell] = current_score + plus
        return self.normalize_score(scores)
