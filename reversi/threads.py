import time
import threading


class GameThread:
    def __init__(self, owner, game_count=100, tick=0.5):
        self.is_running = True
        self.owner = owner
        self.game_count = game_count
        self.current_count = 0
        self.tick = tick
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.is_running = True
        self.owner.start_game()
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.thread.stop()

    def run(self):
        while self.is_running:
            if self.current_count == self.game_count:
                return
            self.current_count += 1
            time.sleep(self.tick)
            board, result, is_game_over = self.owner.update()
            if is_game_over:
                self.owner.gameover(board, result)
                self.owner.continue_game()
