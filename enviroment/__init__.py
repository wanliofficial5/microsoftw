import threading as _threading
import time
from queue import LifoQueue as _LifoQueue

from PIL import Image, ImageTk, ImageFont as _Image, _ImageFont, ImageDraw
from system import threadpool as _threadpool
from .drivers import epd2in9_V2, icnt86
from .touchscreen import Clicked as _Clicked, \
    SlideX as _SlideX, \
    SlideY as _SlideY, \
    TouchHandler as _TouchHandler
import os as _os


class Images:
    def __init__(self):
        self.app_control = Image.open("resources/images/app_control.jpg")
        self.None18px = Image.open("resources/images/None18px.jpg")
        self.None20px = Image.open("resources/images/None20px.jpg")


class Env:
    def __init__(self):
        # locks
        self.display_lock = _threading.Lock()

        # fonts
        self.fonts = {"heiti": {}}

        # screen
        self.Screen = epd2in9_V2.Screen()
        self.Screen.initial()

        # threadpool
        self.Pool = _threadpool.ThreadPool(20, print)
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

        self.back_stack = _LifoQueue()

        # show
        self._show_left_back = False
        self._show_right_back = False
        self._show_home_bar = False
        self._home_bar = False

        # images
        self.images = Images()

    def display_auto(self):
        if self.display_lock.acquire(blocking=False):
            self.Screen.wait_busy()
            self.display_lock.release()
            image = self.Now.render()

            self.Screen.display_auto(image)

    def get_font(self, size, font_name="heiti"):
        if size in self.fonts[font_name]:
            return self.fonts[font_name][size]
        else:
            self.fonts[font_name][size] = _ImageFont.truetype("resources/fonts/STHeiti_Light.ttc", size)
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

    def left_back(self, show: bool):
        if show != self._show_left_back:
            self._show_left_back = show
            self.display_auto()

    def right_back(self, show: bool):
        if show != self._show_right_back:
            self._show_right_back = show
            self.display_auto()

    def home_bar(self):
        if self._home_bar:
            self.back_home()
            self._home_bar = False
        else:
            self._home_bar = True
            self.display_auto()
            time.sleep(1)
            if self._home_bar:
                self._home_bar = False
                self.display_auto()

    @staticmethod
    def poweroff():
        # TODO: run shutdown
        _os.system("sudo poweroff")

    @staticmethod
    def reboot():
        _os.system("sudo reboot")
