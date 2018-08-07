import random


class Brain:
    player_id = None
    next_player = None
    current_board = None

    def on_update(self):
        pass

    def move(self):
        raise NotImplementedError()

    def on_error(self, error):
        print(error)

    def on_another_player_exit(self):
        return 'exit'

    def on_receive(self, data):
        print(data.status)
        print(data.player_id)
        print(data.next_player)
        if data.status == 'entered':
            self.player_id = data.player_id
        elif data.status == 'start':
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
        elif data.status == 'continue':
            self.next_player = data.next_player
            self.current_board = data.board
            if self.next_player == self.player_id:
                return self.move()


class RandomPutBrain(Brain):
    def on_receive(self, data):
        return super(RandomPutBrain, self).on_receive(data)

    def on_error(self, error):
        print(error)
        if not error.endswith('is invalid'):
            return
        if self.player_id == self.next_player:
            return self.move()

    def move(self):
        return '{}:{}'.format(random.randint(0, 8), random.randint(0, 8))
