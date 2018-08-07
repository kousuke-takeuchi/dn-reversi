"""オセロの盤面の状態を保持する
"""
import copy

from .pieces import BLACK, WHITE, BLANK


class Board:
    num_rows = 8
    num_cols = 8
    __rows = ['1', '2', '3', '4', '5', '6', '7', '8']
    __cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def __init__(self, raw=None):
        self.__position = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, WHITE, BLACK, 0, 0, 0],
            [0, 0, 0, BLACK, WHITE, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        if raw:
            self.__position = raw

    def pieces_count(self):
        white = 0
        black = 0
        blank = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.__position[row][col] == WHITE:
                    white += 1
                elif self.__position[row][col] == BLACK:
                    black += 1
                else:
                    blank += 1
        return { WHITE: white, BLACK: black, BLANK: blank }

    def is_game_over(self):
        pieces_count = self.pieces_count()
        if pieces_count[BLANK] == 0:
            return True
        if pieces_count[WHITE] == 0 or pieces_count[BLACK] == 0:
            return True
        return False

    def get_position(self):
        position = copy.deepcopy(self.__position)
        for row in range(len(self.__position)):
            for col in range(len(self.__position[0])):
                if self.__position[row][col] == BLACK:
                    position[row][col] = 'BLACK'
                elif self.__position[row][col] == WHITE:
                    position[row][col] = 'WHITE'
                else:
                    position[row][col] = 'BLANK'
        return position

    def get_raw_piece(self, row, col):
        if row < 0 or row >= self.num_rows:
            return None
        if col < 0 or col >= self.num_cols:
            return None
        return self.__position[row][col]

    def set_piece(self, color, row, col):
        self.__position[row][col] = color
