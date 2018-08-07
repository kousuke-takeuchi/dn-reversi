"""オセロゲームの盤面に石を置いたり、挟まれた石の処理を行う
"""
import random
import uuid

import wx
import wx.lib.newevent

from .board import Board
from .pieces import BLANK, BLACK, WHITE


BoardEvent, EVT_BOARD_EVENT = wx.lib.newevent.NewEvent()


def nearest_pieces(board, color, row, col):
    # 置いた箇所から縦方向を確認
    upper, lower = None, None
    for seek_row in range(board.num_rows):
        # 下方向へ
        piece = board.get_raw_piece(seek_row, col)
        if piece == color and seek_row < row:
            upper = (seek_row, col)
        elif piece == color and seek_row > row:
            lower = (seek_row, col)
    # 置いた箇所から横方向を確認
    left, right = None, None
    for seek_col in range(board.num_cols):
        # 右方向へ
        piece = board.get_raw_piece(row, seek_col)
        if piece == color and seek_col < col:
            left = (row, seek_col)
        elif piece == color and seek_col > col:
            right = (row, seek_col)
    # 置いた箇所から斜め方向を確認
    ur, ul, ll, lr = None, None, None, None
    for d in range(-board.num_rows, board.num_rows):
        # 左上から右下方向へ
        sr, sc = row+d, col+d # ↘
        piece = board.get_raw_piece(sr, sc)
        if piece == color and sr < row:
            ul = (sr, sc)
        elif piece == color and sr > row and not lr:
            lr = (sr, sc)
        # 右上から左下方向へ
        rsr, rsc = row+d, col-d # ↙
        piece = board.get_raw_piece(rsr, rsc)
        if piece == color and rsr < row:
            ur = (rsr, rsc)
        elif piece == color and rsr > row and not ll:
            ll = (rsr, rsc)
    return upper, lower, left, right, ur, ul, ll, lr

def find_rotatable_cells(row, col, upper, lower, left, right, ur, ul, ll, lr):
    pieces = []
    # 下方向へ
    if upper is not None:
        for r in range(row-upper[0]-1):
            pieces.append((row-r-1, col))
    if lower is not None:
        for r in range(lower[0]-row-1):
            pieces.append((row+r+1, col))
    # 右方向へ
    if left is not None:
        for c in range(col-left[1]-1):
            pieces.append((row, col-c-1))
    if right is not None:
        for c in range(right[1]-col-1):
            pieces.append((row, col+c+1))
    # 左上から右下方向へ
    if ul:
        for d in range(row-ul[0]-1):
            pieces.append((row-d-1, col-d-1))
    if lr:
        for d in range(lr[0]-row-1):
            pieces.append((row+d+1, col+d+1))
    # 右上から左下方向へ
    if ur:
        for d in range(row-ur[0]-1):
            pieces.append((row-d-1, col+d+1))
    if ll:
        for d in range(ll[0]-row-1):
            pieces.append((row+d+1, col-d-1))
    return pieces

def will_rotated_cells(board, color, row, col):
    results = []
    if board.get_raw_piece(row, col) != BLANK:
        return results
    pieces = nearest_pieces(board, color, row, col)
    cells = find_rotatable_cells(row, col, *pieces)
    another_color = BLACK if color == WHITE else WHITE
    for cell in cells:
        row, col = cell
        piece = board.get_raw_piece(row, col)
        if piece == another_color and piece != BLANK:
            results.append(cell)
    return results

def can_put(board, color, row, col):
    if board.get_raw_piece(row, col) != BLANK:
        return False
    # 周りに違う色の石があるか
    another_color = BLACK if color == WHITE else WHITE
    seeks = [
        (-1, 0), (1, 0), # 縦
        (0, 1), (0, -1), # 横
        (-1, -1), (1, -1), (-1, 1), (1, 1), # 斜め
    ]
    for seek in seeks:
        pr, pc = seek
        piece = board.get_raw_piece(row+pr, col+pc)
        if piece is not None and piece == another_color:
            return True
    return False

class Engine:
    def __init__(self, frame):
        self.frame = frame
        self.reset()

    @property
    def is_playing(self):
        return self.player1 is not None and self.player2 is not None

    @property
    def is_game_over(self):
        # 白/黒のみ、もしくは置ける場所がなくなったかどうか
        game_over = self.board.is_game_over()
        # お互いおける場所があるかどうか
        can_put = self.can_put_anywhere(BLACK) or self.can_put_anywhere(WHITE)
        game_over = game_over or not can_put
        if game_over:
            self.continue_game()
        return game_over

    def continue_game(self):
        self.board = Board()
        self.waiting_player = random.choice([self.player1, self.player2])
        self.update_window()

    @property
    def result(self):
        return self.board.pieces_count()

    def reset(self):
        self.board = Board()
        self.player1 = None
        self.player2 = None

    def enter_player(self):
        if self.is_playing:
            raise Exception('The game has already started.')
        if not self.player1:
            self.player1 = random.choice([BLACK, WHITE])
            return self.player1
        self.player2 = BLACK if self.player1 == WHITE else WHITE
        self.waiting_player = random.choice([self.player1, self.player2])
        return self.player2

    def exit_player(self, player):
        if self.player1 == player:
            self.player1 = None
        elif self.player2 == player:
            self.player2 = None

    def can_put(self, color, row, col):
        return can_put(self.board, color, row, col)

    def can_put_anywhere(self, color):
        for row in range(self.board.num_rows):
            for col in range(self.board.num_cols):
                if self.can_put(color, row, col) and self.will_rotated_cells(color, row, col):
                    return True
        return False

    def switch_player(self, player):
        next_player = self.player2 if self.player1 == player else self.player1
        if self.can_put_anywhere(next_player):
            self.waiting_player = next_player

    def put_piece(self, player, row, col):
        if not self.is_playing:
            raise Exception('The game does not start.')
        if self.is_game_over:
            raise Exception('The game was gone.')
        if self.waiting_player != player:
            raise Exception('Not your turn.')
        color = player
        # 周りにひっくり返せる石があるかどうか
        if not self.can_put(color, row, col):
            # なければ不正な石と判定
            raise Exception('{}:{} is invalid'.format(row, col))
        cells = self.will_rotated_cells(color, row, col)
        if len(cells) == 0:
            # なければ不正な石と判定
            raise Exception('{}:{} is invalid'.format(row, col))
        # 石をおく
        self.board.set_piece(color, row, col)
        # おいたあとのボード計算
        self.update_board(cells, color)
        self.switch_player(player)
        # 画面の再描画
        self.update_window()
        # 現在のボードの状態を返す
        return self.board.get_position(), self.result, self.waiting_player, self.is_game_over

    def will_rotated_cells(self, color, row, col):
        # 返せる石の一覧を取得
        return will_rotated_cells(self.board, color, row, col)

    def update_board(self, cells, color):
        # 挟まれた石をひっくり返す処理
        for cell in cells:
            row, col = cell
            self.board.set_piece(color, row, col)

    def update_window(self):
        evt = BoardEvent()
        wx.PostEvent(self.frame, evt)

    def current_board(self):
        return self.board.get_position()
