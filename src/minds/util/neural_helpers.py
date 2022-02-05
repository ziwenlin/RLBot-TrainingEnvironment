import numpy as np
from rlbot.utils.game_state_util import GameState
from rlbot.utils.structures.game_data_struct import Physics

from util.bin.orientation import Orientation, relative_location
from util.bin.vec import Vec3

FIELD_WIDTH = 4096
FIELD_LENGTH = 5120
FIELD_HEIGHT = 2048


def convert_physics_to_state(physics: Physics):
    location = (physics.location.x / FIELD_WIDTH, physics.location.y / FIELD_LENGTH, physics.location.z / FIELD_HEIGHT)
    rotation = (physics.rotation.pitch / np.pi, physics.rotation.yaw / np.pi, physics.rotation.roll / np.pi)
    a_velocity = (
        physics.angular_velocity.x / np.pi, physics.angular_velocity.y / np.pi, physics.angular_velocity.z / np.pi)
    velocity = (physics.velocity.x / 2300, physics.velocity.y / 2300, physics.velocity.z / 2300)
    return location, velocity, rotation, a_velocity


def convert_target_to_state(target: dict):
    location = (target['x'] / FIELD_WIDTH, target['y'] / FIELD_LENGTH, target['z'] / FIELD_HEIGHT)
    dummy = (0, 0, 0)
    return location, dummy, dummy, dummy


def convert_vector_to_state(vector):
    return vector.x / 4000, vector.y / 4000, vector.z / 2000

def convert_rotator_to_state(rotator):
    return rotator.pitch / np.pi, rotator.yaw / np.pi, rotator.roll / np.pi


def convert_game_state_to_3x4x3_state(state: GameState, items):
    ball = convert_physics_to_state(state.ball.physics)
    car = convert_physics_to_state(state.cars[0].physics)
    target = convert_physics_to_state(items['Target'])
    return ball, car, target


def convert_game_state_to_6x3_state(state: GameState, items):
    car = state.cars[0].physics
    angle = state.cars[0].physics.rotation
    orientation = Orientation(angle)
    car_speed = relative_location(Vec3(), orientation, Vec3(car.velocity))
    ball = relative_location(Vec3(car.location), orientation, Vec3(state.ball.physics.location))
    ball_speed = relative_location(Vec3(), orientation, Vec3(state.ball.physics.velocity))
    if 'Target' in items:
        target = relative_location(Vec3(car.location), orientation, Vec3(items['Target'].location))
    else:
        target = Vec3()
    return (
        convert_vector_to_state(car.location),
        convert_vector_to_state(car_speed),
        convert_rotator_to_state(angle),
        convert_vector_to_state(ball),
        convert_vector_to_state(ball_speed),
        convert_vector_to_state(target),
    )


def convert_game_state_to_3x3_state(state: GameState, items):
    car = state.cars[0].physics
    angle = state.cars[0].physics.rotation
    orientation = Orientation(angle)
    car_speed = relative_location(Vec3(), orientation, Vec3(car.velocity))
    ball = relative_location(Vec3(car.location), orientation, Vec3(state.ball.physics.location))
    ball_speed = relative_location(Vec3(), orientation, Vec3(state.ball.physics.velocity))
    if 'Target' in items:
        target = relative_location(Vec3(car.location), orientation, Vec3(items['Target'].location))
    else:
        target = Vec3()
    return (
        # convert_vector_to_state(car.location),
        convert_vector_to_state(car_speed),
        # convert_rotator_to_state(angle),
        convert_vector_to_state(ball),
        # convert_vector_to_state(ball_speed),
        convert_vector_to_state(target),
    )