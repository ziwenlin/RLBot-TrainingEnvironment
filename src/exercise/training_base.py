import time
from typing import List

from rlbot.utils.game_state_util import GameState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from exercise.exercise_base import BaseEpisode, BaseExercise
from util.tick_performance import PerformanceMeter


class BaseTrainingManager:
    # Main data of the training manager
    exercise_list: List[GameState]
    exercise_items: List[dict]
    exercise_index: int = -1
    episode_index: int = 0

    # Manager Flags
    is_ready: bool = False
    is_running: bool = False
    exercise_next: bool = False
    exercise_reset: bool = False
    exercise_reload: bool = False

    # Time tracker of the training
    time_started: time.time()
    time_stopped: time.time()
    time_duration: float = 0
    tick_performance = PerformanceMeter()

    exercise: BaseExercise
    episode: BaseEpisode

    def start_training(self, exercises=None):
        pass

    def stop_training(self):
        pass

    def resume_training(self):
        pass

    def step_training(self, packet: GameTickPacket):
        pass
