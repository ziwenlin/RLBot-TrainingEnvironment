from math import sin, pi, cos

from util.boolean_signals import BoolEdge
from snapshot.snapshot_structs import StructSnapshot

FIELD_LENGHT = 5120
FIELD_WIDTH = 4096
GOAL_LENGTH = 880
GOAL_WIDTH = 893
CORNER_RADIUS = 1152
ASPECT_RATIO = (FIELD_LENGHT + GOAL_LENGTH) / FIELD_WIDTH

CANVAS_WIDTH = 400
CANVAS_HEIGHT = CANVAS_WIDTH / ASPECT_RATIO
PADDING = 10

"""
Steps from conversion game state data to canvas coordinates:
Raw shape/location  : x {-4096 to 4096}         y {-5120 to 5120}
Map shape/location  : x {-1 to 1}               y {-1 to 1}
Reconvert step      : Swap x with y             (x, y) -> (y, x)
Coords              : x {-400 to 400}           y {-200 to 200}
Canvas coords       : x {0 to 800}              y {0 to 400}
"""


def convert_location_to_coord(location):
    x, y, *_ = location.values()
    loc_map = convert_raw_shape_to_map((-x, y))
    loc = reconvert_map(loc_map)
    return convert_map_to_coord(loc)


def convert_game_location_to_coord(physics: StructSnapshot.vector):
    raw_location: dict = physics.location.data
    return convert_location_to_coord(raw_location)

def convert_game_velocity_to_coord(physics: StructSnapshot.vector):
    raw_velocity: dict = physics.velocity.data
    return convert_location_to_coord(raw_velocity)


def convert_game_rotation_to_coord(physics: StructSnapshot.vector):
    raw_rotation: dict = physics.rotation.data
    return tuple([raw_rotation[i] * pi / 180 for i in raw_rotation])


def orient_shape(rotation, shape):
    pitch, yaw, roll = rotation
    buffer = []
    for i, j in zip(shape[::2], shape[1::2]):
        j *= -1  # Because canvas positive side goes down
        a = (i * cos(roll))  # * 0.5 + 0.5 * i
        b = (j * cos(pitch))  # * 0.5 + 0.5 * j
        x = (-b * sin(yaw) + a * cos(yaw))  # (-cos(pitch) + sin(roll))
        y = (a * sin(yaw) + b * cos(yaw))  # (-sin(pitch) + cos(roll))
        buffer += [x, y]
    return tuple(buffer)


# Swap x, y to b, a so it can be correctly visualize by the canvas
# Do this before giving the positions
def reconvert_map(data):
    buffer = []
    for index in range(0, len(data), 2):
        buffer += [data[index + 1], data[index]]
    return tuple(buffer)


# Take the game X and Y positions and map them to -1, 1
def convert_raw_shape_to_map(raw):
    conversion = (FIELD_WIDTH, FIELD_LENGHT + GOAL_LENGTH) * int(len(raw) / 2)
    return tuple([j / i for i, j in zip(conversion, raw)])


# Set the positions of the object to the canvas
# Remember to rotate the positions
def convert_map_to_coord(map):
    conversion = (CANVAS_WIDTH - PADDING, CANVAS_HEIGHT - PADDING) * int(len(map) / 2)
    # conversion = (CANVAS_WIDTH, CANVAS_HEIGHT) * int(len(map) / 2)
    return tuple([j * i for i, j in zip(conversion, map)])


# Set the positions of the object to the canvas
# Remember to rotate the positions
def convert_coord_to_c_coord(x, y, *coord):
    pos = (CANVAS_WIDTH + x, CANVAS_HEIGHT + y) * int(len(*coord) / 2)
    # pos = (CANVAS_WIDTH + x - PADDING, CANVAS_HEIGHT + y - PADDING) * int(len(*coord) / 2)
    return tuple([i + j for i, j in zip(pos, *coord)])


def get_field_raw_shape():
    field_shape = []
    e1 = BoolEdge()
    e2 = BoolEdge()
    e3 = BoolEdge()
    clock2 = BoolEdge()  # Clock 2, falling edge of clock 1
    for clock in [(i % 2) == 1 for i in range(8)]:  # Clock 1
        c2 = clock2 != clock  # On falling edge of clock 1
        b1 = e1 == clock  # On rising edge of clock 1
        b2 = e2 == c2  # On rising edge of clock 2
        b3 = e3 != c2  # On falling edge of clock 2
        x = (1 if b2 else -1) * (FIELD_WIDTH - (CORNER_RADIUS if b1 else 0))
        y = (1 if b3 else -1) * (FIELD_LENGHT - (CORNER_RADIUS if not b1 else 0))
        field_shape += [x, y]
    field_shape += field_shape[:2]
    return tuple(field_shape)


# Side -1 or 1 for the teams
def get_goal_raw_shape(side):
    corner_ne = 1, 1
    corner_se = 1, 0
    corner_nw = 0, 1
    corner_sw = 0, 0
    rectangle = corner_sw + corner_nw + corner_ne + corner_se
    goal_shape = []
    for i, j in zip(rectangle[::2], rectangle[1::2]):
        x = (1 if i else -1) * GOAL_WIDTH
        y = (GOAL_LENGTH * j + FIELD_LENGHT) * side
        goal_shape += [x, y]
    return goal_shape


def convert_coord_to_raw_shape(x, y):
    x, y = shape_coord = x - CANVAS_WIDTH, y - CANVAS_HEIGHT
    shape_map = x / (CANVAS_WIDTH - PADDING), -y / (CANVAS_HEIGHT - PADDING)
    x, y = reconvert_map(shape_map)  # Setting x and y back to b and a
    return FIELD_WIDTH * x, (FIELD_LENGHT + GOAL_LENGTH) * y


def convert_raw_shape_to_c_coord(shape):
    shape_map = convert_raw_shape_to_map(shape)  # Map is 10k by 8k. Canvas is smaller
    shape_map = reconvert_map(shape_map)  # Getting the axis right
    shape_coord = convert_map_to_coord(shape_map)
    return convert_coord_to_c_coord(0, 0, shape_coord)


def convert_raw_shape_to_coord(shape):
    shape_map = convert_raw_shape_to_map(shape)  # Map is 10k by 8k. Canvas is smaller
    shape_map = reconvert_map(shape_map)  # Getting the axis right
    return convert_map_to_coord(shape_map)
