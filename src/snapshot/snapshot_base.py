from __future__ import annotations
import math

from rlbot.utils.game_state_util import GameState
from typing import Dict, Union

from rlbot.utils.structures.game_data_struct import GameTickPacket, PlayerInfo, Physics, BallInfo, Vector3, Rotator
from rlbot.utils.game_state_util import Rotator as SRotator, Vector3 as SVector3

from snapshot.snapshot_structs import StructSnapshot, StructGameState, StructPhysics, StructCar

VectorData = Dict[str, float]
PhysicsData = Dict[str, VectorData]
ItemData = PhysicsData
BallData = PhysicsData
CarData = Dict[str, Union[PhysicsData, any]]
CarsData = Dict[int, CarData]
ItemsData = Dict[str, ItemData]
SnapshotData = Dict[str, Union[CarsData, BallData, any]]


class SnapshotVector:
    pitch: float = 0
    yaw: float = 0
    roll: float = 0

    def __init__(self, data: VectorData):
        self.data = data
        self.x = data['x']
        self.y = data['y']
        self.z = data['z']

    def get(self, axis):
        if axis == 'x': return self.x
        if axis == 'y': return self.y
        if axis == 'z': return self.z

    def set(self, axis, value):
        if axis == 'x': self.data['x'] = self.x = value
        if axis == 'y': self.data['y'] = self.y = value
        if axis == 'z': self.data['z'] = self.z = value

    def update(self, vector: Union[SnapshotVector, SVector3, Vector3]):
        self.data['x'] = self.x = vector.x
        self.data['y'] = self.y = vector.y
        self.data['z'] = self.z = vector.z

    def update_rotator(self, rotator: Union[Rotator, SnapshotVector]):
        if type(rotator) is Rotator or type(rotator) is SRotator:
            self.data['x'] = self.x = self.pitch = rotator.pitch * 180 / math.pi
            self.data['y'] = self.y = self.yaw = rotator.yaw * 180 / math.pi
            self.data['z'] = self.z = self.roll = rotator.roll * 180 / math.pi
        elif type(rotator) is SnapshotVector:
            self.update(rotator)

    def update_angular(self, rotator):
        self.data['x'] = self.x = rotator.x * 180 / math.pi
        self.data['y'] = self.y = rotator.y * 180 / math.pi
        self.data['z'] = self.z = rotator.z * 180 / math.pi

    def update_dict(self, data):
        self.data['x'] = self.x = data['x']
        self.data['y'] = self.y = data['y']
        self.data['z'] = self.z = data['z']


class SnapshotPhysics:

    def __init__(self, data: PhysicsData):
        self.data = data
        self.location = SnapshotVector(data[StructPhysics.location])
        self.velocity = SnapshotVector(data[StructPhysics.velocity])
        self.rotation = SnapshotVector(data[StructPhysics.rotation])
        self.angular_velocity = SnapshotVector(data[StructPhysics.angular_velocity])

    def update(self, physics: Union[SnapshotPhysics, Physics]):
        self.location.update(physics.location)
        self.velocity.update(physics.velocity)
        self.rotation.update_rotator(physics.rotation)
        self.angular_velocity.update_angular(physics.angular_velocity)

    def update_dict(self, physics):
        self.location.update_dict(physics[StructPhysics.location])
        self.velocity.update_dict(physics[StructPhysics.velocity])
        self.rotation.update_dict(physics[StructPhysics.rotation])
        self.angular_velocity.update_dict(physics[StructPhysics.angular_velocity])

    def get(self, vector: str, axis: str = None) -> Union[SnapshotVector, float]:
        if axis:
            if vector == StructPhysics.location: return self.location.get(axis)
            if vector == StructPhysics.velocity: return self.velocity.get(axis)
            if vector == StructPhysics.rotation: return self.rotation.get(axis)
            if vector == StructPhysics.angular_velocity: return self.angular_velocity.get(axis)
        if vector == StructPhysics.location: return self.location
        if vector == StructPhysics.velocity: return self.velocity
        if vector == StructPhysics.rotation: return self.rotation
        if vector == StructPhysics.angular_velocity: return self.angular_velocity


class SnapshotBall:

    def __init__(self, data: BallData):
        self.data = data
        self.physics = SnapshotPhysics(data)

    def update(self, ball):
        if type(ball) is dict:
            self.update_dict(ball)
        elif type(ball) is BallInfo:
            self.physics.update(ball.physics)
        else:
            self.physics.update(ball.physics)

    def update_dict(self, ball):
        self.physics.update_dict(ball)

    def get(self, vector):
        return self.physics.get(vector)


class SnapshotCar:

    def __init__(self, data: CarData):
        self.data = data
        self.physics = SnapshotPhysics(data[StructCar.physics])
        # TODO the other variables

    def update(self, car):
        if type(car) is dict:
            self.update_dict(car)
        # elif type(car) is PlayerInfo:
        #     self.physics
        else:
            self.physics.update(car.physics)

    def update_dict(self, car):
        self.physics.update_dict(car[StructCar.physics])


class Snapshot:

    def __init__(self):
        self.data: SnapshotData = StructSnapshot.game_state()
        self.ball: SnapshotBall = SnapshotBall(self.data[StructGameState.ball])
        self.cars: Dict[int, SnapshotCar] = {num: SnapshotCar(car) for num, car in
                                             self.data[StructGameState.cars].items()}
        self.items_data = {}
        self.items: Dict[str, SnapshotPhysics] = {}

    def create_item(self, name):
        self.items_data[name] = data = StructSnapshot.physics()
        self.items[name] = SnapshotPhysics(data)

    def create_car(self, index: int):
        self.data[StructGameState.cars][int(index)] = data = StructSnapshot.car_state()
        self.cars[int(index)] = SnapshotCar(data)

    def update_items(self, items):
        for name, item in items.items():
            if name not in self.items:
                self.create_item(name)
            if type(item) is SnapshotPhysics:
                self.items[name].update(item)
            elif type(item) is dict:
                self.items[name].update_dict(item)
            # else:
            #     print('Probably a hot reload error, please ignore this error/message.')
            #     print(type(item), type(item) is SnapshotPhysics)  # Strange
        for name in self.items.copy():
            if name in items: continue
            self.items.pop(name)
            self.items_data.pop(name)

    def update(self, game_state: Union[GameState, SnapshotData, GameTickPacket]):
        if type(game_state) is dict:
            ball = game_state[StructGameState.ball]
            cars = {int(i): d for i, d in game_state[StructGameState.cars].items()}
        elif type(game_state) is GameState:
            ball = game_state.ball
            cars = game_state.cars
        elif type(game_state) is GameTickPacket:
            ball = game_state.game_ball
            cars = {i: d for i, d in enumerate(game_state.game_cars)}
        else:
            return
        # Conversion above deals with different data types
        self.ball.update(ball)
        for index, car in cars.items():
            if index not in self.cars:
                self.create_car(index)
            self.cars[index].update(car)
        for index in self.cars.copy():
            if index in cars: continue
            self.remove_car(index)

    def remove_car(self, index):
        if index in self.cars:
            self.data[StructGameState.cars].pop(index)
            self.cars.pop(index)
