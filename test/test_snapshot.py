import ctypes
import random, math
from unittest import TestCase

from rlbot.utils.structures.game_data_struct import GameTickPacket, BallInfo, GameInfo, Physics, Vector3, Rotator, \
    PlayerInfo

from snapshot.snapshot_base import Snapshot


def generate_physics(seed, value):
    random.seed(seed)
    radian = 2 * math.pi
    return Physics(
        Vector3(random.random() * value, random.random() * value, random.random() * value),
        Rotator(random.random() * radian, random.random() * radian, random.random() * radian),
        Vector3(random.random() * value, random.random() * value, random.random() * value),
        Vector3(random.random() * value, random.random() * value, random.random() * value)
    )


class Test(TestCase):
    def test_snapshot_update_ball(self):
        physics = generate_physics(10, 300)
        game_state = GameTickPacket(
            game_ball=BallInfo(
                physics
            )
        )
        snapshot = Snapshot()
        self.assertNotEqual(
            snapshot.ball.physics.velocity.x, physics.velocity.x,
            'Snapshot did something weird tested with game_state'
        )
        snapshot.update(game_state)
        self.assertEqual(
            snapshot.ball.physics.velocity.x, physics.velocity.x,
            'Snapshot did not update tested with game_state'
        )

    def test_snapshot_update_cars(self):
        game_state = GameTickPacket()
        physics = generate_physics(12, 10)
        game_state.game_cars[0] = PlayerInfo(
            physics
        )
        snapshot = Snapshot()
        bind = snapshot.cars[0].physics
        self.assertNotEqual(
            snapshot.cars[0].physics.velocity.x, physics.velocity.x,
            'Snapshot did something weird'
        )
        self.assertEqual(
            snapshot.cars[0].physics, bind,
            'Snapshot binding changed'
        )
        snapshot.update(game_state)
        self.assertEqual(
            snapshot.cars[0].physics.velocity.x, physics.velocity.x,
            'Snapshot did not update'
        )
        self.assertEqual(
            snapshot.cars[0].physics, bind,
            'Snapshot binding changed'
        )
