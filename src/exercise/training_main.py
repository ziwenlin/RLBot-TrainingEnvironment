import copy
import random

import time

from rlbot.utils.structures.game_data_struct import GameTickPacket

from exercise.training_base import BaseTrainingManager
from exercise.exercise_base import BaseExercise, EpisodeManager
from util.bin.console_helper import display_episode
from snapshot.snapshot_structs import convert_snapshot_to_game_state
from snapshot.file_functions import load_snapshot

NEXT_EPISODE_ACCURACY = 0.8
NEXT_EPISODE_MAX = 50


def load_exercises(agent, exercise_names):
    exercises, items = [], []
    if not exercise_names:
        # When no exercises are supplied
        exercise_names = ['Exercise 1', 'Exercise 2', 'Exercise 3']
    for name in exercise_names:
        # Loading exercise into the agent
        load_snapshot(name, agent)
        # Retrieving game state from the agent
        snapshot = agent.snapshot.data.copy()
        exercises.append(convert_snapshot_to_game_state(snapshot))
        items.append(copy.deepcopy(agent.snapshot.items))
    # Prevent the game state from loading because it will get messy
    agent.snapshot_load_flag = False
    return exercises, items


def randomness_exercise(agent):
    """Sometimes the ball hit won't get registered
    Using a bit of randomness every hit becomes unique"""
    rotation = agent.game_state.ball.physics.rotation
    rotation.x += random.uniform(-0.1, 0.1)
    rotation.y += random.uniform(-0.1, 0.1)
    agent.game_state.ball.physics.rotation = rotation


class TrainingManager(BaseTrainingManager):
    def __init__(self, agent):
        self.agent = agent
        self.is_running = False

    def reload_exercises(self, exercises):
        exercises_list, items = load_exercises(self.agent, exercises)
        self.exercise_list = exercises_list
        self.exercise_items = items

    def start_training(self, exercises=None):
        # Prepare training
        self.reload_exercises(exercises)

        if self.is_running:
            # Don't reset the training we just want to update the exercises
            return
        self.is_running = True

        # Start exercise # Start timers
        self.time_started = time.time()
        display_episode('Started training')
        self.next_exercise()
        self.is_ready = True

    def resume_training(self):
        """Canceled training can be resumed"""
        if self.is_running:
            # No double firing
            return
        self.is_running = True
        # Resume timer and training
        display_episode('Resuming training')
        self.reset_exercise()

    def stop_training(self):
        """TODO this function is probably going to be for storing statistics"""
        if not self.is_running:
            return
        self.is_running = False

        # Calculate time and stop timer
        self.time_stopped = time.time()
        display_episode('Stopped training')

    def next_exercise(self):
        # Increasing exercise index and check if it still is valid
        self.exercise_index = index = self.exercise_index + 1
        if index >= len(self.exercise_list):
            self.exercise_index = 0

        # Setting exercise game state and items
        game_state = self.exercise_list[self.exercise_index]
        item_state = self.exercise_items[self.exercise_index].copy()
        self.exercise = BaseExercise(game_state, item_state)
        self.exercise.episode_start = self.episode_index

        # Additional starting variables
        display_episode('Next exercise')
        self.reset_exercise()

    def reset_exercise(self):
        # Setting exercise game state and items
        self.agent.game_state = self.exercise.game_state
        self.agent.game_items = self.exercise.item_state.copy()
        self.agent.snapshot_override_flag = True
        randomness_exercise(self.agent)

        # Reset variables
        self.agent.restore_agent()
        self.episode = EpisodeManager(self.exercise)
        self.episode.index = self.episode_index

    def end_exercise(self):
        exercise_next = self.episode.index % NEXT_EPISODE_MAX == NEXT_EPISODE_MAX - 1 or self.exercise_next
        exercise_next = self.episode.data['accuracy'] >= NEXT_EPISODE_ACCURACY or exercise_next

        # Calculating times of the exercise
        self.time_duration += self.episode.time_duration
        self.episode_index += 1

        if not exercise_next:
            self.reset_exercise()
        else:  # Next exercise will also call reset exercise
            self.next_exercise()
        self.exercise_next = False

    def step_training(self, packet: GameTickPacket):
        if not self.is_running:
            return
        if not self.is_ready:
            return
        self.is_ready = False
        try:
            reset_checks = self.episode.step(packet, self.agent)
        except AttributeError:
            display_episode('Episode not initialised')
            self.is_running = False
            reset_checks = {}

        for name, check in reset_checks.items():
            if not check:
                continue
            self.episode.data['name'] = name
            self.episode.data['episode'] = self.episode_index
            # if name in ['Ball was close']:
            #     history_index = self.episode_index - self.episode_start
            #     history_index = 10 if history_index > 10 else history_index
            #     closest_data = [d['closest'] for d in self.data_episode.values()][-history_index:]
            #     data['accuracy'] = 100 / (100 + (sum(closest_data) / len(closest_data)))
            display_episode(self.episode.data)
            self.end_exercise()
            break
        self.is_ready = True
        self.tick_performance.step()