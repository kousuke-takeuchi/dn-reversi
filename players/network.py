import numpy as np
from keras.models import Sequential, Model
from keras.layers import Dense, InputLayer, Reshape, Flatten, Input, Concatenate
from keras.layers.convolutional import Conv2D, ZeroPadding1D
from keras.layers.local import LocallyConnected2D
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import ELU
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, TensorBoard


def create_model():
    board_input = Input(shape=[8, 8])
    action_input = Input(shape=[8, 8])
    color_input = Input(shape=[1])

    model_c = Sequential([
        InputLayer([8, 8]),
        Reshape([8, 8, 1]),
        Conv2D(128, 8, 1, name="model_c_conv1"), # 1x8
        ELU(),
        Conv2D(128, 1, 1, name="model_c_conv2"), # 1x8
        ELU(),
        Flatten()
    ], name="model_c")

    model_r = Sequential([
        InputLayer([8, 8]),
        Reshape([8, 8, 1]),
        Conv2D(128, 1, 8, name="model_r_conv1"), # 8x1
        ELU(),
        Conv2D(128, 1, 1, name="model_r_conv2"), # 8x1
        ELU(),
        Flatten()
    ], name="model_r")

    model_dr = Sequential([
        InputLayer([8, 8]),
        Reshape([8*8, 1]),
        ZeroPadding1D(4),
        Reshape([8, 9, 1]),
        LocallyConnected2D(96, 8, 1, name="model_dr_lc1"), # 1x9
        ELU(),
        LocallyConnected2D(64, 1, 1, name="model_dr_lc2"), # 1x9
        ELU(),
        Flatten()
    ], name="model_dr")

    model_dl = Sequential([
        InputLayer([8, 8]),
        Reshape([8*8, 1]),
        ZeroPadding1D(3),
        Reshape([10, 7, 1]),
        LocallyConnected2D(96, 10, 1, name="model_dl_lc1"), # 1x7
        ELU(),
        LocallyConnected2D(64, 1, 1, name="model_dl_lc2"), # 1x7
        ELU(),
        Flatten()
    ], name="model_dl")

    merge_layer = Concatenate()([
        model_c(board_input),
        model_r(board_input),
        model_dl(board_input),
        model_dr(board_input),
        color_input,
        model_c(action_input),
        model_r(action_input),
        model_dl(action_input),
        model_dr(action_input),
    ])

    x = Dense(2048, name="fc_1")(merge_layer)
    x = ELU()(x)
    x = Dense(512, name="fc_2")(x)
    x = ELU()(x)
    output = Dense(1, activation="tanh", name="fc_3")(x)

    model = Model(input=[board_input, color_input, action_input], output=[output])

    adam = Adam(lr=1e-5)
    model.compile(optimizer=adam, loss="mse")

    print(model.summary())

    return model
