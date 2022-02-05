import copy
from math import pi

from rlbot.utils.game_state_util import GameState, Physics, Vector3, Rotator, BallState, CarState, GameInfoState
from typing import Dict, Union


class StructPhysics:
    velocity = 'Velocity'
    rotation = 'Rotation'
    location = 'Location'
    angular_velocity = 'Angular Velocity'

    def get_var(self):
        '''Location, Velocity, Rotation, Angular Velocity'''
        return self.location, self.velocity, self.rotation, self.angular_velocity


class StructCar:
    physics = 'Physics'
    boost = 'Boost'
    jumped = 'Jumped'
    double_jumped = 'Double Jumped'

    def get_var(self):
        '''Physics, Boost, Jumped, Double Jumped'''
        return self.physics, self.boost, self.jumped, self.double_jumped


class StructGameInfo:
    gravity = 'Gravity'
    speed = 'Speed'
    paused = 'Paused'
    end_match = 'End Match'

    def get_var(self):
        '''Gravity, Speed, Paused, End Match'''
        return self.gravity, self.speed, self.paused, self.end_match


class StructGameState:
    ball = 'Ball'
    cars = 'Cars'
    info = 'Info'
    boost = 'Boosts'
    cmd = 'Console'


class StructSnapshot:

    @staticmethod
    def vector():
        return {'x': float(), 'y': float(), 'z': float()}

    @staticmethod
    def physics():
        return {
            StructPhysics.velocity: StructSnapshot.vector(),
            StructPhysics.location: StructSnapshot.vector(),
            StructPhysics.angular_velocity: StructSnapshot.vector(),
            StructPhysics.rotation: StructSnapshot.vector(),
        }

    @staticmethod
    def car_state():
        return {
            StructCar.physics: StructSnapshot.physics(),
            StructCar.boost: float(),
            StructCar.jumped: bool(),
            StructCar.double_jumped: bool(),
        }

    @staticmethod
    def car_list():
        return {
            0: StructSnapshot.car_state(),
            # 1: self.car_state(),
            # 2: self.car_state(),
            # 3: self.car_state(),
            # 4: self.car_state(),
            # 5: self.car_state(),
        }

    @staticmethod
    def game_info():
        return {
            StructGameInfo.gravity: float(),
            StructGameInfo.speed: float(),
            StructGameInfo.paused: bool(),
            StructGameInfo.end_match: bool(),
        }

    @staticmethod
    def game_state():
        return {
            StructGameState.ball: StructSnapshot.physics(),
            StructGameState.cars: StructSnapshot.car_list(),
            StructGameState.info: StructSnapshot.game_info(),
            StructGameState.boost: None,  # Info of the boost pads
            StructGameState.cmd: None,  # Extra commands (in bakkesmod?)
        }


def generate_game_state() -> GameState:
    """Generates an empty game_state"""
    car_state = CarState(empty_physics(), 33, True, True)
    ball_state = BallState(empty_physics())
    return GameState(ball_state, {0: car_state})


def empty_physics() -> Physics:
    """Generates an empty game state physics"""
    return Physics(Vector3(0, 0, 0),
                   Rotator(0, 0, 0),
                   Vector3(0, 0, 0),
                   Vector3(0, 0, 0))


def convert_snapshot_to_game_state(data: StructSnapshot.game_state):
    """Convert json data to GameState
    so that the engine can use it"""
    ball = BallState(dict_to_physics(data[StructGameState.ball]))
    cars = dict_to_cars(data[StructGameState.cars])
    info = dict_to_info(data[StructGameState.info])
    return GameState(ball=ball, cars=cars, game_info=info)


def convert_game_state_to_snapshot(game_state: GameState):
    """Convert GameState data to snapshot data
    so the data can be stored"""
    data = StructSnapshot.game_state()
    data[StructGameState.ball] = physics_to_dict(game_state.ball.physics)
    data[StructGameState.cars] = cars_to_dict(game_state.cars)
    data[StructGameState.info] = info_to_dict(game_state.game_info)
    return data.copy()


def convert_json_to_snapshot(json_data):
    """Converts json data to snapshot"""
    def convert_json_physics(json_physics):
        return {
            physics_key: {
                axis: value for axis, value in physics_item.items()
            } for physics_key, physics_item in json_physics.items()}

    converted_data = {
        StructGameState.ball: convert_json_physics(json_data[StructGameState.ball]),
        StructGameState.cars: {
            int(car_index): {
                StructCar.physics: convert_json_physics(car_data[StructCar.physics]),
                StructCar.boost: car_data[StructCar.boost],
                StructCar.jumped: car_data[StructCar.jumped],
                StructCar.double_jumped: car_data[StructCar.double_jumped],
            } for car_index, car_data in json_data[StructGameState.cars].items()
        },
        StructGameState.info: None,
        # StructGameState.boost: StructJSON.
    }
    return converted_data


def car_to_dict(car: CarState) -> StructSnapshot.car_state:
    data = StructSnapshot.car_state()
    data[StructCar.physics] = physics_to_dict(car.physics)
    data[StructCar.boost] = car.boost_amount
    data[StructCar.jumped] = car.jumped not in (None, False)
    data[StructCar.double_jumped] = car.double_jumped not in (None, False)
    return data


def dict_to_car(data: StructSnapshot.car_state):
    physics = dict_to_physics(data[StructCar.physics])
    boost = data[StructCar.boost]
    # TODO Jumped and double jumped can't be used yet
    # jumped = data[CAR.jumped]
    # double_jumped = data[CAR.double_jumped]
    # return CarState(physics, boost, jumped, double_jumped)
    return CarState(physics, boost, None, None)


def cars_to_dict(cars: Dict[int, CarState]):
    data = StructSnapshot.car_list()
    for index, car_state in cars.items():
        data[index] = car_to_dict(car_state)
    return data


def dict_to_cars(data: StructSnapshot.car_list):
    cars = {0: CarState()}
    for index, car_state in data.items():
        cars[index] = dict_to_car(car_state)
    return cars


def info_to_dict(info: GameInfoState):
    if not info:
        return
    data = StructSnapshot.game_info()
    data[StructGameInfo.gravity] = info.world_gravity_z
    data[StructGameInfo.speed] = info.game_speed
    data[StructGameInfo.paused] = info.paused
    data[StructGameInfo.end_match] = info.end_match
    return data


def dict_to_info(data: StructSnapshot.game_info):
    if not data or data:
        return
    gravity = data[StructGameInfo.gravity]
    speed = data[StructGameInfo.speed]
    paused = data[StructGameInfo.paused]
    end_match = data[StructGameInfo.end_match]
    return GameInfoState(world_gravity_z=gravity, game_speed=speed, paused=paused, end_match=end_match)


def physics_to_dict(physics: Physics):
    data = StructSnapshot.physics()
    data[StructPhysics.velocity] = vector3_to_dict(physics.velocity)
    data[StructPhysics.location] = vector3_to_dict(physics.location)
    temp_angular_velocity = vector3_to_dict(physics.angular_velocity)
    data[StructPhysics.angular_velocity] = rads_to_degree(temp_angular_velocity)
    data[StructPhysics.rotation] = rotator_to_dict(physics.rotation)
    return data


def dict_to_physics(data: StructSnapshot.physics):
    rot = dict_to_rotator(data[StructPhysics.rotation])
    vel = dict_to_vector3(data[StructPhysics.velocity])
    loc = dict_to_vector3(data[StructPhysics.location])
    temp_angular_velocity = degree_to_rads(data[StructPhysics.angular_velocity])
    angular_velocity = dict_to_vector3(temp_angular_velocity)
    return Physics(location=loc, rotation=rot, velocity=vel, angular_velocity=angular_velocity)


def rads_to_degree(vec: StructSnapshot.vector):
    return {a: b * 180 / pi for a, b in vec.items()}


def degree_to_rads(vec: StructSnapshot.vector):
    return {a: b * pi / 180 for a, b in vec.items()}


def vector3_to_dict(vec: Vector3) -> StructSnapshot.vector:
    return {'x': vec.x, 'y': vec.y, 'z': vec.z}


def rotator_to_dict(vec: Rotator) -> StructSnapshot.vector:
    data = {'x': vec.pitch, 'y': vec.yaw, 'z': vec.roll}
    return {a: b * 180 / pi for a, b in data.items()}


def dict_to_vector3(data: StructSnapshot.vector):
    return Vector3(data['x'], data['y'], data['z'])


def dict_to_rotator(data: StructSnapshot.vector):
    d = {a: b * pi / 180 for a, b in data.items()}
    return Rotator(d['x'], d['y'], d['z'])
