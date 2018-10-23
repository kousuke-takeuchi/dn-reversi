from players.brain import RandomBrain, ExpertBrain
from players.qlearn import QBrain, DQNBrain
from players import network


# me = QBrain(alpha=0.3, gamma=0.9)
model = network.create_model()
me = DQNBrain(model)
enemy = RandomBrain()


from dn_reversi import start_game
start_game(me, enemy, game_count=1000, tick=0.001)
