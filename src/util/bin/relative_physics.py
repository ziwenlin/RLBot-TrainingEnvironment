import math

from snapshot.snapshot_base import SnapshotPhysics, SnapshotVector, PhysicsData
from snapshot.snapshot_structs import StructPhysics


def list_to_dict(x, y, z):
    return {'x': x, 'y': y, 'z': z}


@DeprecationWarning
def calculate_relative(origin: SnapshotPhysics, target: SnapshotPhysics):
    o = ConvertToRelative(origin, target)
    return o.calculate()


@DeprecationWarning
def calculate_back(origin: SnapshotPhysics, target: SnapshotPhysics):
    o = ConvertToPhysics(origin, target)
    return o.calculate()


class RelativePhysics(SnapshotPhysics):

    def __init__(self, origin: SnapshotPhysics, target: SnapshotPhysics):
        self.origin = origin
        self.target = target
        self.relative = self.get_relative()
        self.normal = self.get_normal()
        super().__init__(self.relative.data)

    def refresh(self, origin: SnapshotPhysics, target: SnapshotPhysics):
        self.origin = origin
        self.target = target
        self.calculate()

    def calculate(self):
        self.relative = self.get_relative()
        self.normal = self.get_normal()
        self.update(self.relative)

    def get_relative(self):
        self.relative = ConvertToRelative(self.origin, self.target).calculate()
        return self.relative

    def get_normal(self):
        self.normal = ConvertToPhysics(self.origin, self.relative).calculate()
        return self.normal


class ConvertToRelative:

    def __init__(self, origin: SnapshotPhysics, target: SnapshotPhysics):
        self.rotations = rotation = origin.data.get(StructPhysics.rotation)
        self.origin = origin
        self.target = target

        self.yaw = float(rotation.get('y') * math.pi / 180)
        self.roll = float(rotation.get('z') * math.pi / 180)
        self.pitch = float(rotation.get('x') * math.pi / 180)

        cr = math.cos(self.roll)
        sr = math.sin(self.roll)
        cp = math.cos(self.pitch)
        sp = math.sin(self.pitch)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)

        self.forward = Vector(cp * cy, cp * sy, sp)
        self.right = Vector(cy * sp * sr - cr * sy, sy * sp * sr + cr * cy, -cp * sr)
        self.up = Vector(-cr * cy * sp - sr * sy, -cr * sy * sp + sr * cy, cp * cr)

    def calculate(self):
        data = {
            StructPhysics.location: self.get_relative_position().data,
            StructPhysics.rotation: self.get_relative_rotation().data,
            StructPhysics.velocity: self.get_relative_velocity().data,
            StructPhysics.angular_velocity: self.get_relative_angular_velocity().data
        }
        return SnapshotPhysics(data)

    def get_relative_position(self):
        center = Vector(self.origin.location)
        target = Vector(self.target.location)
        relative = target - center
        x = relative.dot(self.forward)
        y = relative.dot(self.right)
        z = relative.dot(self.up)
        self.target_position = Vector(x, y, z)
        return self.target_position

    def get_relative_velocity(self):
        center = Vector(self.origin.velocity)
        target = Vector(self.target.velocity)
        relative = target - center
        x = relative.dot(self.forward)
        y = relative.dot(self.right)
        z = relative.dot(self.up)
        self.target_velocity = Vector(x, y, z)
        return self.target_velocity

    def get_relative_rotation(self):
        center = Vector(self.origin.rotation)
        target = Vector(self.target.rotation)
        self.target_rotation = target - center
        return self.target_rotation

    def get_relative_angular_velocity(self):
        center = Vector(self.origin.angular_velocity)
        target = Vector(self.target.angular_velocity)
        self.target_angular_velocity = target - center
        return self.target_angular_velocity


class ConvertToPhysics:

    def __init__(self, origin: SnapshotPhysics, relative: SnapshotPhysics):
        self.rotations = rotation = origin.data.get(StructPhysics.rotation)
        self.origin = origin
        self.relative = relative

        self.yaw = float(rotation.get('y') * math.pi / -180)
        self.roll = float(rotation.get('z') * math.pi / -180)
        self.pitch = float(rotation.get('x') * math.pi / -180)

        cos_roll = math.cos(self.roll)
        sin_roll = math.sin(self.roll)
        cos_pitch = math.cos(self.pitch)
        sin_pitch = math.sin(self.pitch)
        cos_yaw = math.cos(self.yaw)
        sin_yaw = math.sin(self.yaw)

        self.forward = Vector(cos_pitch * cos_yaw, cos_pitch * sin_yaw, sin_pitch)
        self.right = Vector(cos_yaw * sin_pitch * sin_roll - cos_roll * sin_yaw,
                            sin_yaw * sin_pitch * sin_roll + cos_roll * cos_yaw,
                            -cos_pitch * sin_roll)
        self.up = Vector(-cos_roll * cos_yaw * sin_pitch - sin_roll * sin_yaw,
                         -cos_roll * sin_yaw * sin_pitch + sin_roll * cos_yaw,
                         cos_pitch * cos_roll)

    def calculate(self):
        data = {
            StructPhysics.location: self.get_location().data,
            StructPhysics.rotation: self.get_rotation().data,
            StructPhysics.velocity: self.get_velocity().data,
            StructPhysics.angular_velocity: self.get_angular_velocity().data
        }
        return SnapshotPhysics(data)

    def get_location(self):
        center = Vector(self.origin.location)
        target = Vector(self.relative.location)
        x = target.dot(self.forward)
        y = target.dot(self.right)
        z = target.dot(self.up)
        self.target_location = Vector(x, y, z) + center
        return self.target_location

    def get_velocity(self):
        center = Vector(self.origin.velocity)
        target = Vector(self.relative.velocity)
        x = target.dot(self.forward)
        y = target.dot(self.right)
        z = target.dot(self.up)
        self.target_velocity = Vector(x, y, z) + center
        return self.target_velocity

    def get_rotation(self):
        center = Vector(self.origin.rotation)
        target = Vector(self.relative.rotation)
        self.target_rotation = target + center
        return self.target_rotation

    def get_angular_velocity(self):
        center = Vector(self.origin.angular_velocity)
        target = Vector(self.relative.angular_velocity)
        self.target_angular_velocity = target + center
        return self.target_angular_velocity


class Vector(SnapshotVector):

    def __init__(self, x, y=None, z=None):
        if type(x) is SnapshotVector:
            super().__init__(list_to_dict(x.x, x.y, x.z))
        else:
            super().__init__(list_to_dict(x, y, z))

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
