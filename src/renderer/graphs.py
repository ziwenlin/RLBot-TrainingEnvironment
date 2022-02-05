from rlbot.utils.rendering.rendering_manager import RenderingManager

LINE_WIDTH = 5
BUFFER = 300



class Graph1D:
    """Better to not use this code
    This was a test if rendering graphs in game is viable
    TODO ask community for better options"""

    def __init__(self, position: tuple):
        self.position = position
        self.data = [0, 0]

    def new_data(self, v):
        self.data.append(v)
        if len(self.data) > BUFFER*2:
            self.data = self.data[-BUFFER:]

    def render(self, renderer: RenderingManager):
        data = self.data[-BUFFER:]
        lowest = min(data)
        highest = max(data)
        average = sum(data) / len(data)
        # if highest - average == 0:
        #     lowest -= highest - lowest
        # else:
        #     lowest -= 1
        # if average - lowest == 0:
        #     highest += highest - lowest
        # else:
        #     highest += 1
        if highest == lowest or highest - lowest < 1:
            highest += 1
            lowest -= 1
        x, y, width, height = self.position[:4]
        renderer.begin_rendering('Graph')
        renderer.draw_rect_2d(x, y, LINE_WIDTH, height-LINE_WIDTH, False, renderer.white())
        renderer.draw_rect_2d(x+width, y, LINE_WIDTH, height-LINE_WIDTH, False, renderer.white())
        renderer.draw_rect_2d(x, y, width-LINE_WIDTH, LINE_WIDTH, False, renderer.white())
        renderer.draw_rect_2d(x, y+height, width-LINE_WIDTH, LINE_WIDTH, False, renderer.white())
        renderer.draw_string_2d(x-50, y, 2, 2, f'{highest:.1f}', renderer.red())
        renderer.draw_string_2d(x-50, y+height, 2, 2, f'{lowest:.1f}', renderer.red())
        renderer.draw_string_2d(x-50, y+height/2, 2, 2, f'{average:.1f}', renderer.red())
        renderer.end_rendering()
        renderer.begin_rendering('Graph_Line')
        prev_i, prev_v = x + 10, y + 10
        for i, v in enumerate(data):
            scr_i = (i * width // BUFFER) + x
            scr_v = ((v - average) / (highest - lowest) + 1) * (height / 2)
            if scr_i != prev_i:
                renderer.draw_rect_2d(scr_i, height + y - scr_v, LINE_WIDTH, LINE_WIDTH, False, renderer.red())
                # renderer.end_rendering()
                # renderer.begin_rendering('Graph_Line'+str(scr_i))
            prev_i = scr_i
        renderer.end_rendering()
