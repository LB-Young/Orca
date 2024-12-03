class Painter:
    def __init__(self, canvas):
        self.canvas = canvas

    def paint(self, x, y, color):
        self.canvas[x][y] = color

    def clear(self):
        pass