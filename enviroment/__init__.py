import threading as _threading
import time
from queue import LifoQueue as _LifoQueue

# 模拟器GUI wxpython
import wx

from PIL import Image as _Image, \
    ImageFont as _ImageFont, \
    ImageDraw as _ImageDraw
from system import threadpool as _threadpool
from .touchscreen import Clicked as _Clicked, \
    SlideX as _SlideX, \
    SlideY as _SlideY, \
    TouchHandler as _TouchHandler, \
    TouchRecoder as _TouchRecoder
import os as _os


# 模拟器屏幕
class Simulator:
    def start(self, env):
        self.env = env
        self.touch_recoder_dev = _TouchRecoder()
        self.touch_recoder_old = _TouchRecoder()
        # 创建窗口(296x128)
        self.app = wx.App()
        self.frame = wx.Frame(None, title="水墨屏模拟器 v2.0 by xuanzhi33", size=(296, 160))

        # 背景为黑色图片
        bmp = wx.Bitmap("resources/images/simplebytes.jpg")

        self.staticbit = wx.StaticBitmap(self.frame, -1, bmp)

        # 绑定按下鼠标
        self.frame.Bind(wx.EVT_LEFT_DOWN, self.mouseDown)
        # 绑定松开鼠标
        self.frame.Bind(wx.EVT_LEFT_UP, self.mouseUp)

        self.frame.Show()

        self.app.MainLoop()

    def mouseDown(self, event):
        x = event.GetX()
        y = event.GetY()
        self.touch_recoder_old.Touch = False
        self.touch_recoder_dev.Touch = True
        self.touch_recoder_dev.X[0] = x
        self.touch_recoder_dev.Y[0] = y
        self.env.TouchHandler.handle(self.touch_recoder_dev, self.touch_recoder_old)

    def mouseUp(self, event):
        x = event.GetX()
        y = event.GetY()
        self.touch_recoder_old.Touch = True
        self.touch_recoder_dev.Touch = False
        self.touch_recoder_dev.X[0] = x
        self.touch_recoder_dev.Y[0] = y
        self.env.TouchHandler.handle(self.touch_recoder_dev, self.touch_recoder_old)

    def updateImage(self, image: _Image):

        def bitmapThreading():
            wximg = wx.Image(296, 128, image.convert("RGB").tobytes())
            bmp = wx.Bitmap(wximg)
            self.staticbit.SetBitmap(bmp)
        _threading.Thread(target=bitmapThreading).start()

    def display(self, image: _Image):
        self.updateImage(image)

    def display_patial(self, image: _Image):
        self.updateImage(image)

    def display_auto(self, image: _Image):
        self.updateImage(image)

    def wait_busy(self):
        pass

    def quit(self):
        pass


class Images:
    def __init__(self):
        self.app_control = _Image.open("resources/images/app_control.jpg")
        self.None18px = _Image.open("resources/images/None18px.jpg")
        self.None20px = _Image.open("resources/images/None20px.jpg")
        self.docker_image = _Image.open("resources/images/docker.jpg")


class Env:
    def __init__(self, simulator):
        # locks
        self.display_lock = _threading.Lock()

        # fonts
        self.fonts = {"heiti": {}}

        # screen
        self.Screen = simulator

        # threadpool
        self.Pool = _threadpool.ThreadPool(20, print)
        self.Pool.start()

        """
        
        # touchscreen
        self.Touch = self.simulator

        self.Touch.icnt_init()
        """

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

    def poweroff(self):
        # TODO: run shutdown
        _os.system("sudo poweroff")
        self.Screen.quit()

    def reboot(self):
        _os.system("sudo reboot")
        self.Screen.quit()
