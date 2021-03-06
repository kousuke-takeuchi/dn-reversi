import random

import numpy as np
import tensorflow as tf

from .brain import MessageProtocol, BrainBase
from .utils import flatten, multiple, put


class QBrain(BrainBase):
    """Q学習で置く場所を学んでいく
    """
    INF = float('inf')
    DEFAULT_E = 0.2
    INITIAL_Q = 1  # default 1
    _total_game_count = 0
    _q = {}
    _last_board = None
    _last_move = None
    _alpha = 0.3
    _gamma = 0.9

    def __init__(self, e=DEFAULT_E, alpha=0.3, gamma=0.9):
        self._e = e
        self._alpha = alpha
        self._gamma = gamma

    def random_select(self, candidate):
        return candidate[random.randrange(len(candidate))]

    def move(self):
        move_cell = None
        self._last_board = self.current_board
        candidate = self.candidate()

        # if random.random() < (self._e / (self._total_game_count // 10000 + 1)):
        #     move_cell = self.random_select(candidate)
        # else:
        qs = []
        for cell in candidate:
            qs.append(self.get_q(self.current_board, cell))

        max_q = max(qs)
        # print("Q値: ", self._q.values())

        if qs.count(max_q) > 1:
            # more than 1 best option; choose among them randomly
            best_options = [i for i in range(len(candidate)) if qs[i] == max_q]
            i = random.choice(best_options)
        else:
            i = qs.index(max_q)
        move_cell = candidate[i]

        self._last_cell = move_cell
        return move_cell


    def get_q(self, state, cell):
        # encourage exploration; "optimistic" 1.0 initial values
        state = flatten(state)
        if self._q.get((state, cell)) is None:
            self._q[(state, cell)] = self.INITIAL_Q
        return self._q.get((state, cell))

    def before_update(self, board):
        if self._last_board:
            self.learn(0)

    def on_gameover(self, board, result):
        super(QBrain, self).on_gameover(board, result)
        me = result[self.player_id]
        enemy = result[-1*self.player_id]
        if me > enemy:
            reward = 2.0
        elif me < enemy:
            reward = -2.0
        else:
            reward = 0.1

        self.learn(reward)

        self._total_game_count += 1
        self._last_move = None
        self._last_board = None

        print("勝ち: ", self.win)
        print("負け: ", self.lose)
        # print("Qテーブル: ", [q for q in self._q.values() if q != 1])

    def learn(self, reward):
        last_state = flatten(self._last_board)
        current_board = self.current_board
        pQ = self.get_q(last_state, self._last_move)

        qs = []
        for cell in self.candidate():
            qs.append(self.get_q(current_board, cell))

        if reward or len(qs) == 0:
            max_q_new = 0
        else:
            max_q_new = max(qs)
        # Qテーブルの再計算
        self._q[(last_state, self._last_move)] = pQ + self._alpha * ((reward + self._gamma * max_q_new) - pQ)

class DQNBrain(BrainBase):
    def __init__(self, model):
        self.model = model
        self.graph = tf.get_default_graph()

    def move(self):
        current_board = self.to_board_obj()
        current_board = current_board.position
        candidate = self.candidate()
        color = self.player_id

        boards = [multiple(current_board) for _ in candidate]
        boards = np.array(current_board).reshape(-1, 8, 8)
        colors = np.array([color]*len(boards)).reshape(-1, 1)
        actions = [multiple(put(current_board, color, c)) for c in candidate]
        actions = np.array(actions).reshape(-1, 8, 8)

        with self.graph.as_default():
            scores = self.model.predict([
                boards,
                colors,
                actions
            ])

        scores = scores.reshape([-1, 1])
        scores = np.max(scores, axis=1)
        max_hand = np.argmax(scores)
        return candidate[max_hand]

    def on_gameover(self, board, result):
        super(DQNBrain, self).on_gameover(board, result)
        current_board = self.to_board_obj()
        current_board = current_board.position
        color = self.player_id
        boards = [multiple(current_board)]
        boards = np.array(current_board).reshape(-1, 8, 8)
        colors = np.array([color]*len(boards)).reshape(-1, 1)

        me = result[self.player_id]
        enemy = result[-1*self.player_id]
        score = 1 if me > enemy else -1
        score = np.array([score])

        with self.graph.as_default():
            self.model.fit([boards, colors, boards], score,
                           verbose=1,
                           epochs=1)
        print("勝ち: ", self.win)
        print("負け: ", self.lose)
