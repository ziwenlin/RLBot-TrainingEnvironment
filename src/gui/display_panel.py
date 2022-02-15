import tkinter as tk

from gui.display_base import CanvasItem
from gui.display_converter import CANVAS_WIDTH, CANVAS_HEIGHT, get_field_raw_shape, \
    get_goal_raw_shape, convert_coord_to_raw_shape, \
    convert_raw_shape_to_coord
from gui.display_functions import BALL_SHAPE, CURSOR_SHAPE, get_closest_item, \
    check_changes_cars, get_selectable_items, calculate_angle, check_changes_items, calculate_distance, CURSOR_R_SHAPE

from gui.gamestate_functions import game_state_update_ui
from gui.gui_base import InterfaceVariables, PHYSICS_PANEL_PRIMARY, PHYSICS_PANEL_SECONDARY


def panel_display(base, agent, interface: InterfaceVariables):
    """TODO add comments"""
    canvas = tk.Canvas(base, width=CANVAS_WIDTH * 2, height=CANVAS_HEIGHT * 2, bg='black')

    shape = convert_raw_shape_to_coord(get_field_raw_shape())
    play_field = CanvasItem(canvas, 'play field', shape, None)
    play_field.create('line', fill='white')
    shape = convert_raw_shape_to_coord(get_goal_raw_shape(-1))
    orange_goal = CanvasItem(canvas, 'orange goal', shape, None)
    orange_goal.create('line', fill='orange')
    shape = convert_raw_shape_to_coord(get_goal_raw_shape(1))
    blue_goal = CanvasItem(canvas, 'blue goal', shape, None)
    blue_goal.create('line', fill='cyan')

    ball = CanvasItem(canvas, 'ball', BALL_SHAPE, agent.snapshot.ball.physics)
    ball.create('oval', fill='#cccccc')
    cursor = CanvasItem(canvas, 'cursor', CURSOR_SHAPE, None)
    cursor.create('oval', outline='yellow')
    cursor.visibility(False)
    cursor_relative = CanvasItem(canvas, 'cursor', CURSOR_R_SHAPE, None)
    cursor_relative.create('oval', outline='lightgreen')
    cursor_relative.visibility(False)

    canvas_items = [
        ball, cursor, cursor_relative, play_field, orange_goal, blue_goal
    ]

    def set_target(event):
        x, y = convert_coord_to_raw_shape(event.x, event.y)
        if 'Target' not in agent.snapshot.items:
            agent.snapshot.create_item('Target')
        agent.snapshot.items['Target'].location.set('x', x)
        agent.snapshot.items['Target'].location.set('y', y)

    # def set_velocity(event):
    #     x1, y1 = convert_coord_to_raw_shape(event.x, event.y)
    #     item = get_selected_item_snapshot(canvas, agent)
    #     x2, y2, _ = item[StructPhysics.location].values()
    #     velocity = item[StructPhysics.velocity]
    #     velocity['x'] = x1 - x2
    #     velocity['y'] = y1 - y2

    def select_item(event):
        x, y = convert_coord_to_raw_shape(event.x, event.y)
        selectable_items = get_selectable_items(canvas_items)
        closest_item = get_closest_item(x, y, selectable_items)
        if calculate_distance(x, y, closest_item.bind.location) < 1000:
            cursor.bind = interface.selector[PHYSICS_PANEL_PRIMARY] = closest_item.bind
        elif not cursor.bind:
            pass
        elif calculate_distance(x, y, cursor.bind.location) > 1000:
            cursor.bind = interface.selector[PHYSICS_PANEL_PRIMARY] = None
        interface.update()

    def select_relative(event):
        x, y = convert_coord_to_raw_shape(event.x, event.y)
        selectable_items = get_selectable_items(canvas_items)
        closest_item = get_closest_item(x, y, selectable_items)
        if calculate_distance(x, y, closest_item.bind.location) < 1000:
            cursor_relative.bind = interface.selector[PHYSICS_PANEL_SECONDARY] = closest_item.bind
        elif not cursor_relative.bind:
            pass
        elif calculate_distance(x, y, cursor_relative.bind.location) > 1000:
            cursor_relative.bind = interface.selector[PHYSICS_PANEL_SECONDARY] = None
        interface.update()

    def drag_rotate(event):
        if not cursor.bind: return
        x, y = convert_coord_to_raw_shape(event.x, event.y)
        angle = calculate_angle(x, y, cursor.bind.location)
        cursor.bind.rotation.set('y', angle)
        interface.update()

    def drag_drop(event):
        if not cursor.bind: return
        x, y = convert_coord_to_raw_shape(event.x, event.y)
        item_location = cursor.bind.location
        item_location.set('x', x)
        item_location.set('y', y)
        interface.update()

    def drag_drop_any(event):
        x, y = convert_coord_to_raw_shape(event.x, event.y)
        selectable_items = get_selectable_items(canvas_items)
        closest_item = get_closest_item(x, y, selectable_items)
        if calculate_distance(x, y, closest_item.bind.location) > 1000: return
        x, y = convert_coord_to_raw_shape(event.x, event.y)
        item_location = closest_item.bind.location
        item_location.set('x', x)
        item_location.set('y', y)
        interface.update()

    canvas.bind('<Button-1>', select_item)
    canvas.bind('<B1-Motion>', drag_drop)
    canvas.bind('<Button-3>', drag_rotate)
    canvas.bind('<B3-Motion>', drag_rotate)
    canvas.bind('<Button-2>', select_relative)
    # canvas.bind('<B2-Motion>', select_relative)
    canvas.bind('<Key-m>', drag_drop_any)
    canvas.bind('<KeyPress-m>', drag_drop_any)
    canvas.bind('<Key-x>', set_target)
    canvas.bind('<KeyPress-x>', set_target)
    canvas.bind('<Enter>', lambda e: canvas.focus_set())
    # canvas.bind('<Key>', print)

    update = build_task_update(interface, agent, canvas, canvas_items)
    draw = build_task_draw(interface, cursor, cursor_relative, canvas_items)
    interface.thread.add_task(update)
    interface.thread.add_task(draw)
    canvas.pack()


def build_task_draw(interface, cursor, cursor_relative, canvas_items):
    def draw():
        for item in canvas_items:
            item.update()
        cursor.bind = interface.selector.get(PHYSICS_PANEL_PRIMARY)
        cursor.visibility(cursor.bind is not None)
        cursor_relative.bind = interface.selector.get(PHYSICS_PANEL_SECONDARY)
        cursor_relative.visibility(cursor_relative.bind is not None)

    return draw


def build_task_update(interface, agent, canvas, canvas_items):
    def update():
        check_changes_cars(canvas, agent, canvas_items)
        check_changes_items(canvas, agent, canvas_items)
        # update_velocity_canvas(canvas, agent)

    return update
