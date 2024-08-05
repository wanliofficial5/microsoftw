from queue import LifoQueue

from PIL import Image, ImageTk, ImageFont, ImageDraw
from system import threadpool
from .drivers import epd2in9_V2, icnt86
from .touchscreen import Clicked as _Clicked, \
    SlideX as _SlideX, \
    SlideY as _SlideY, \
    TouchHandler as _TouchHandler
import os


class Env:
    def __init__(self):
        # locks

        # fonts
        self.fonts = {"heiti": {}}

        # screen
        self.Screen = epd2in9_V2.Screen()
        self.Screen.initial()

        # threadpool
        self.Pool = threadpool.ThreadPool(20, print)
        self.Pool.start()

        # touchscreen
        self.Touch = icnt86.TouchDriver()
        self.Touch.icnt_init()
        self.TouchHandler = _TouchHandler(self)

        # themes
        self.themes = {}
        self.now_theme = "default"

        # applications
        self.apps = {}

        # plugins
        self.plugins = {}

        self.Now = None

        self.back_stack = LifoQueue()

    def get_font(self, size, font_name="heiti"):
        if size in self.fonts[font_name]:
            return self.fonts[font_name][size]
        else:
            self.fonts[font_name][size] = ImageFont.truetype("resources/fonts/STHeiti_Light.ttc", size)
            return self.fonts[font_name][size]

    def back_home(self):
        self.back_stack.queue.clear()
        if self.Now is not self.themes[self.now_theme]:
            self.Now.pause()
            self.Now = self.themes[self.now_theme]

    def open_app(self, target: str, to_stack=True):
        if target in self.apps:
            self.Now.pause()
            self.Now = self.apps[target]
            self.Now.active()
        else:
            raise KeyError("The targeted application is not found.")

    def back(self) -> bool:
        if not self.Now.back():
            if self.back_stack.empty():
                return False
            else:
                i = self.back_stack.get()
                if callable(i):
                    i()
                elif isinstance(i, str):
                    self.open_app(i)
                else:
                    return False
        return True

    def add_back(self, item):
        self.back_stack.put(item)

    @staticmethod
    def poweroff():
        # TODO: run shutdown
        os.system("sudo poweroff")

    @staticmethod
    def reboot():
        os.system("sudo reboot")
