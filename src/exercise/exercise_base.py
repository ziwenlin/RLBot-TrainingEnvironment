import time
from typing import Dict

from rlbot.utils.game_state_util import GameState

from snapshot.snapshot_base import SnapshotPhysics
from util.remove.vec import Vec3


class BaseExercise:

    def __init__(self, game_state: GameState, item_state: Dict[str, SnapshotPhysics]):
        # Speak for it self
        self.game_state = game_state
        self.item_state = item_state
        # Timers
        self.time_start = time.time()
        self.time_duration = 0

        # Exercise description
        self.time_out = 5
        self.episode_start = 0
        self.start_positions = {}
        self.start_distance = 0

        # Exercise statistics
        self.accuracy = 0
        self.success_ratio = 0

        # Calculating starting variables TODO
        target = Vec3(item_state['Target'].location if 'Target' in item_state else 0)
        ball = Vec3(game_state.ball.physics.location)
        car = Vec3(game_state.cars[0].physics.location)
        self.start_distance = car.dist(ball) + ball.dist(target)
        self.start_positions = {'Ball': ball, 'Target': target, 'Car': car}


class BaseEpisode:
    def __init__(self, exercise: BaseExercise):
        self.time_start = time.time()
        self.time_duration = 0
        self.index = 0
        self.data = {}

        self.exercise = exercise
        self.latest_touch = Vec3()

        self.closest = None
        self.score = 0
        self.phase = 0

    def step(self, packet, agent):
        pass


class PhaseBase:
    def __init__(self):
        self.reward_max = 0
        self.reward = 0
        self.target = 'Target'
        self.rules = ''
        self.mutator = None

    def get_reward(self):
        pass
    def get_done(self):
        pass
    pass


class EpisodeManager(BaseEpisode):
    """
    TODO way to many things
    """

    def step(self, packet, agent):
        self.time_duration = time.time() - self.time_start
        items = agent.snapshot.items

        # Get the duration of this episode
        duration = self.time_duration

        # Gather information to process
        target = Vec3(items['Target'].location if 'Target' in items else 0)
        # ball = Vec3(self.agent.game_state.ball.physics.location)
        # car = Vec3(self.agent.game_state.cars[self.agent.index].physics.location)
        ball = Vec3(agent.game_state.ball.physics.location)
        car = Vec3(agent.game_state.cars[agent.index].physics.location)
        distance = (car.dist(ball) + ball.dist(target)) if self.phase == 0 else ball.dist(target)
        distance_traveled = self.exercise.start_distance - distance

        # Get best closest distance from episode
        if not self.closest or self.closest > distance:
            self.closest = distance
        closest = self.closest

        # Check for if the ball is touched by the bot
        latest_touch = Vec3(packet.game_ball.latest_touch.hit_location)
        phases = [latest_touch.dist(self.latest_touch) != 0
                  and packet.game_ball.latest_touch.player_index == agent.index
                  and self.latest_touch.dist(Vec3()) != 0]
        self.latest_touch = latest_touch

        # Check for distance ball to target
        phases += [1000 / (1 + i) > target.dist(ball) for i in range(20)]
        if phases[self.phase]:
            self.phase += 1
            agent.agent_is_driving = False
        phase = self.phase

        # Get score from the first phase when the car has not touched the ball
        scores = [1 - (car.dist(ball) + ball.dist(target)) / (1 + self.exercise.start_distance)]

        # Get the score from how close the ball went to the target
        scores += [1 + i / 2 - ball.dist(target) / (1 + self.exercise.start_distance) for i in range(20)]
        score = scores[phase]

        # Get the highest score the bot has gotten
        if self.score < score:
            self.score = score
        best_score = self.score

        # Calculate the reward the bot will get from this state
        time_penalty = duration / self.exercise.time_out * 0.3  # Last number is the severeness
        reward = -2 + score * 2 - time_penalty
        # reward *= 100

        # Store the data of the exercise so the agent can access it
        self.data = {
            'name': 'None yet', 'episode': self.index, 'duration': duration, 'reward': reward, 'score': score,
            'penalty': time_penalty, 'phase': phase, 'accuracy': 0,
            'distance': distance, 'closest': closest,
        }

        # Reset requirements only 1 need to be true
        reset_checks = {
            'Best score': score < 0.9 * best_score and best_score > 0.1,
            'Ball was close': distance > 1.25 * closest,
            'No movements': duration >= 1 and 10 > car.dist(
                self.exercise.start_positions['Car']) > -10,
            'Exercise timed out': duration > self.exercise.time_out,
        }
        if score < 0.8 * best_score and best_score > 0.1:
            print(score, best_score, self.score)

        return reset_checks
