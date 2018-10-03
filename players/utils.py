import numpy as np


def flatten(board):
    result = []
    for row in board:
        for col in row:
            result.append(col)
    return tuple(result)

def multiple(board):
    b_t = np.transpose(board) # transpose
    b_r = np.rot90(board, 2) # rotate
    b_rt = np.rot90(b_t, 2) # transpose and rotate

    boards = np.array([[board], [b_t], [b_r], [b_rt]])
    return boards

def put(board, position):
    board = np.copy(board)
    board[position[0], position[1]] = color
    return board
