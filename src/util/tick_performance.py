import time


class PerformanceMeter:
    def __init__(self):
        self.ticks_per_seconds = 120
        self.now_time = time.time()
        self.last_time = self.now_time + 1 / 120

    def step(self):
        last = self.last_time = self.now_time
        now = self.now_time = time.time()
        self.ticks_per_seconds = 1 / (now - last)

    def get_tps(self):
        return self.ticks_per_seconds