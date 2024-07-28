from PIL import Image, ImageTk, ImageFont, ImageDraw
from .drivers import epd2in9_V2, icnt86
from .touchscreen import Clicked as _Clicked \
    , SlideX as _SlideX \
    , SlideY as _SlideY


class _ReIter:  # 反向迭代器
    def __init__(self, content):
        self.content = content
        self.index = None

    def __iter__(self):
        self.index = len(self.content)
        return self

    def __next__(self):
        if self.index <= 0:
            self.index = len(self.content)
            raise StopIteration
        else:
            self.index -= 1
            return self.content[self.index]


class Env:
    def __init__(self):
        # locks

        # fonts
        self.fonts = {"heiti": {}}

        # screen
        self.Screen = epd2in9_V2.Screen()
        self.Screen.initial()

        # touchscreen
        self.Touch = icnt86.TouchDriver()
        self.Touch.icnt_init()

    def get_font(self, size, font_name="heiti"):
        if size in self.fonts[font_name]:
            return self.fonts[font_name][size]
        else:
            self.fonts[font_name][size] = ImageFont.truetype("resources/fonts/STHeiti_Light.ttc", size)
            return self.fonts[font_name][size]
