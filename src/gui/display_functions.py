import math
from typing import List

from gui.display_converter import convert_game_location_to_coord, convert_coord_to_c_coord, \
    convert_location_to_coord, convert_game_velocity_to_coord
from snapshot.snapshot_structs import StructGameState, StructCar

from gui.display_base import CanvasItem

CAR_ARROW_SHAPE = (0, -5, 18, -14, 0, 25, -18, -14)
CAR_BODY_SHAPE = (6, 8, 6, -8, -6, -8, -6, 8)
BALL_SHAPE = (-10, -10, 10, 10)
CURSOR_SHAPE = (20, 20, -20, -20)
CURSOR_R_SHAPE = (25, 25, -25, -25)
ITEM_SHAPE = (10, 0, 0, 10, -10, 0, 0, -10)
CAR_CANVAS_ITEMS = 2


# TODO
def check_changes_items(canvas, agent, items):
    snapshot_items = agent.snapshot.items
    canvas_items: List[CanvasItem] = [item for item in items if item.is_extra]
    if len(canvas_items) == len(snapshot_items):
        return  # No changes detected
    elif len(canvas_items) > len(snapshot_items):
        for item in canvas_items:
            if item.name in snapshot_items: continue
            items.remove(item)
            item.destroy()
        return  # Detected a change. An items was removed
    existing_item_names = [item.name for item in canvas_items]
    for item_name, physics in snapshot_items.items():
        # Detected a change. A car has appeared
        if item_name in existing_item_names: continue
        item = CanvasItem(canvas, item_name, ITEM_SHAPE, physics)
        item.create('poly', 'purple')
        items.append(item)


def check_changes_cars(canvas, agent, items):
    snapshot_cars = agent.snapshot.cars
    car_items: List[CanvasItem] = [item for item in items if item.is_car]
    if len(car_items) == len(snapshot_cars) * CAR_CANVAS_ITEMS:
        return  # No changes detected
    elif len(car_items) > len(snapshot_cars) * CAR_CANVAS_ITEMS:
        for item in car_items:
            if get_car_id(item) in snapshot_cars: continue
            items.remove(item)
            item.destroy()
        return  # Detected a change. A car has vanished
    existing_cars_indices = [get_car_id(car) for car in car_items]
    for index, car in snapshot_cars.items():
        # Detected a change. A car has appeared
        if index in existing_cars_indices: continue
        arrow = CanvasItem(canvas, f'arrow {index + 1}', CAR_ARROW_SHAPE, car.physics)
        body = CanvasItem(canvas, f'body {index + 1}', CAR_BODY_SHAPE, car.physics)
        try:
            if agent.game_packet.game_cars[index].team == 0:
                color = '#34d5eb'
            elif agent.game_packet.game_cars[index].team == 1:
                color = '#ebb434'
            else:  # When car does not belong to both teams
                color = '#eeeeee'
        except IndexError:
            color = '#888888'  # Car not registered to any team
        arrow.create('poly', color, '#444444')
        body.create('poly', color, '#444444')
        items.extend([arrow, body])


def update_item_canvas(canvas, agent, items_canvas):
    check_changes_items(canvas, agent, items_canvas)
    for name, location in agent.snapshot_items.items():
        x, y = convert_location_to_coord(location)
        coord = convert_coord_to_c_coord(x, y, ITEM_SHAPE)
        canvas.coords(items_canvas[name], coord)


# TODO
def update_velocity_canvas(canvas, agent):
    for index, car in agent.snapshot[StructGameState.cars].items():
        x, y = convert_game_location_to_coord(car[StructCar.physics])
        dx, dy = convert_game_velocity_to_coord(car[StructCar.physics])


# TODO
def calculate_angle(x, y, location):
    # do = calculate_distances(x, y, {0: location})[0]
    dx = location.x - x
    dy = location.y - y
    angle = -math.atan2(dx, dy)
    return angle * 180 / math.pi - 90


def calculate_distance(x, y, vector):
    a = vector.x
    b = vector.y
    dx = a - x
    dy = b - y
    distance = dx ** 2 + dy ** 2
    return distance ** 0.5


def calculate_distances(x, y, data):
    '''Takes dictionary {any: vector} and returns {any: distance}'''
    distances = {}
    for key, item in data.items():
        distances[key] = calculate_distance(x, y, item)
    return distances


def get_car_id(item):
    return int(item.name.split(' ')[1]) - 1


def get_selectable_items(items):
    return [item for item in items if item.bind and item.selectable]


def get_closest_item(x, y, items):
    items_location = {item: item.bind.location for item in items}
    items_distances = calculate_distances(x, y, items_location)
    return min(items_distances, key=items_distances.get)
