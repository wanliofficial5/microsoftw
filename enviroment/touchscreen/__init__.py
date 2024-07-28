class TouchRecoder:
    def __init__(self):
        self.Touch = 0
        self.TouchGestureId = 0
        self.TouchCount = 0

        self.TouchEvenId = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.P = [0, 1, 2, 3, 4]


class Clicked:  # call the function when the object is clicked.
    def __init__(self, area, func, *args, **kwargs):
        self.area = area
        self.func = func
        self.args = args
        self.kwargs = kwargs


class SlideX:
    def __init__(self, area, func, *args, **kwargs):
        self.area = area
        self.func = func
        self.args = args
        self.kwargs = kwargs


class SlideY:
    def __init__(self, area, func, *args, **kwargs):
        self.area = area
        self.func = func
        self.args = args
        self.kwargs = kwargs
