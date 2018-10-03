import random

import numpy as np
from keras.models import Sequential, Model
from keras.layers import Dense, InputLayer, Reshape, Flatten, merge, Input
from keras.layers.convolutional import Conv2D, ZeroPadding1D
from keras.layers.local import LocallyConnected2D
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import ELU
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, TensorBoard

from .brain import MessageProtocol, BrainBase
from .utils import flatten, multiple


class QBrain(BrainBase):
    """Q学習で置く場所を学んでいく
    """
    INF = float('inf')
    DEFAULT_E = 0.2
    INITIAL_Q = 1  # default 1

    def __init__(self, e=DEFAULT_E, alpha=0.3, gamma=0.9):
        self._e = e
        self._alpha = alpha
        self._gamma = gamma
        self._total_game_count = 0
        self._q = {}
        self._last_board = None
        self._last_move = None

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

class DQNBrain(RandomBrain):
    def __init__(self, log_filepath='./log'):
        self.model = generate_model()
        self.callbacks = [TensorBoard(log_dir=log_filepath, histogram_freq=1)]

    def move(self):
        current_board = self.to_board_obj()
        candidate = self.candidate()
        color = self.player_id

        boards = [multiple(current_board) for _ in candidate]
        boards = np.array(current_board).reshape(-1, 8, 8)
        colors = np.array([color]*len(boards)).reshape(-1, 1)
        actions = [multiple(put(current_board, color, c)) for c in candidate]
        actions = np.array(actions).reshape(-1, 8, 8)

        self.model.fit([boards, colors, actions],
                            verbose=1,
                            nb_epoch=24,
                            validation_split=0.2,
                            callbacks=[
                                EarlyStopping(patience=1)
                            ])

        scores = self.model.predict([
            boards,
            colors,
            actions
        ])

        cores = scores.reshape([-1, 4])
        scores = np.max(scores, axis=1)
        max_hand = np.argmax(scores)
        return hands[max_hand]

    def generate_model():
        board_input = Input(shape=[8, 8])
        action_input = Input(shape=[8, 8])
        color_input = Input(shape=[1])

        model_v = Sequential([
            InputLayer([8, 8]),
            Reshape([8, 8, 1]),
            Conv2D(64, 8, 1), # 1x8
            ELU(),
            Conv2D(64, 1, 1),
            ELU(),
            Flatten()
        ])

        model_h = Sequential([
            InputLayer([8, 8]),
            Reshape([8, 8, 1]),
            Conv2D(64, 1, 8), # 8x1
            ELU(),
            Conv2D(64, 1, 1),
            ELU(),
            Flatten()
        ])

        model_dr = Sequential([
            InputLayer([8, 8]),
            Reshape([8*8, 1]),
            ZeroPadding1D(3),
            Reshape([8, 9, 1]),
            LocallyConnected2D(64, 8, 1),
            ELU(),
            LocallyConnected2D(64, 1, 1),
            ELU(),
            Flatten()
        ])

        model_dl = Sequential([
            InputLayer([8, 8]),
            Reshape([8*8, 1]),
            ZeroPadding1D(2),
            Reshape([8, 7, 1]),
            LocallyConnected2D(64, 8, 1),
            ELU(),
            LocallyConnected2D(64, 1, 1),
            ELU(),
            Flatten()
        ])

        color_model = Sequential([
            InputLayer([1]),
            Dense(256),
            ELU(),
            Dense(1024),
            ELU()
        ])

        merge_layer = merge([
            model_v(board_input),
            model_h(board_input),
            model_dl(board_input),
            model_dr(board_input),
            color_model(color_input),
            model_v(action_input),
            model_h(action_input),
            model_dl(action_input),
            model_dr(action_input),
        ], mode="concat", concat_axis=-1)

        x = Dense(2048)(merge_layer)
        x = BatchNormalization()(x)
        x = ELU()(x)
        x = Dense(512)(x)
        x = BatchNormalization()(x)
        x = ELU()(x)
        x = Dense(128)(x)
        x = BatchNormalization()(x)
        x = ELU()(x)
        output = Dense(1, activation="tanh")(x)

        model = Model(input=[board_input, color_input, action_input], output=[output])

        adam = Adam(lr=1e-4)
        model.compile(optimizer=adam, loss="mse")

        return model
