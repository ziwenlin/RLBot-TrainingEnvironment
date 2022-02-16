import tkinter as tk

from gui.display_convert import convert_coord_to_c_coord, convert_game_location_to_coord, \
    convert_game_rotation_to_coord, orient_shape

CAR_NAMES = [
    'body', 'arrow'
]

EXTRA_ITEMS = [
    'target',
]

SELECTABLE_ITEMS = [
    'arrow', 'ball', 'target',
]


class CanvasItem:
    def __init__(self, canvas, name: str, shape, bind=None):
        self.canvas: tk.Canvas = canvas
        self.shape = shape
        self.name = name
        self.bind = bind
        self.index = None
        self.structure = None

        self.selectable = any(check in name.lower() for check in SELECTABLE_ITEMS)
        self.is_car = any(check in name.lower() for check in CAR_NAMES)
        self.is_extra = name.lower() in EXTRA_ITEMS

    def create(self, structure, fill=None, outline=None):
        if not self.bind:
            canvas_coord = convert_coord_to_c_coord(0, 0, self.shape)
        else:
            x, y = convert_game_location_to_coord(self.bind)
            canvas_coord = convert_coord_to_c_coord(x, y, self.shape)
        if structure == 'poly':
            index = self.canvas.create_polygon(canvas_coord)
        elif structure == 'line':
            index = self.canvas.create_line(canvas_coord)
        elif structure == 'oval':
            a, b, c, d = canvas_coord
            index = self.canvas.create_oval(a, b, c, d)
        else:
            index = self.canvas.create_polygon(canvas_coord)
        self.canvas.itemconfigure(index, fill=fill, outline=outline)
        self.index = index
        self.structure = structure
        return self

    def visibility(self, toggle=None):
        if toggle is True:
            self.canvas.itemconfigure(self.index, state=tk.NORMAL)
        elif toggle is False:
            self.canvas.itemconfigure(self.index, state=tk.HIDDEN)
        else:
            code = self.canvas.cget('state')
            if code == tk.NORMAL:
                self.canvas.itemconfigure(self.index, state=tk.HIDDEN)
            else:
                self.canvas.itemconfigure(self.index, state=tk.NORMAL)

    def update_position(self):
        x, y = convert_game_location_to_coord(self.bind)
        coord = convert_coord_to_c_coord(x, y, self.shape)
        self.update_canvas(coord)

    def update_position_yaw(self):
        x, y = convert_game_location_to_coord(self.bind)
        rotations = convert_game_rotation_to_coord(self.bind)
        shape = orient_shape((0, rotations[1], 0), self.shape)
        coord = convert_coord_to_c_coord(x, y, shape)
        self.update_canvas(coord)

    def update_orientation(self):
        x, y = convert_game_location_to_coord(self.bind)
        rotations = convert_game_rotation_to_coord(self.bind)
        shape = orient_shape(rotations, self.shape)
        coord = convert_coord_to_c_coord(x, y, shape)
        self.update_canvas(coord)

    def update_canvas(self, coord):
        if self.structure == 'Oval':
            a, b, c, d = coord
            self.canvas.coords(self.index, a, b, c, d)
            return
        self.canvas.coords(self.index, coord)

    def update(self):
        if not self.bind:
            return
        if 'body' in self.name:
            self.update_position_yaw()
        elif 'arrow' in self.name:
            self.update_orientation()
        else:
            self.update_position()

    def destroy(self):
        self.canvas.delete(self.index)
        del self
