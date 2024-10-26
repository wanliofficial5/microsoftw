import threading as _threading
import time
from queue import LifoQueue as _LifoQueue

# 模拟器GUI wxpython
import wx

from PIL import Image as _Image, \
    ImageFont as _ImageFont, \
    ImageDraw as _ImageDraw

import framework.struct
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
        screenshotImg = image
        image.show()

        wximg = wx.Image(296, 128)

        wximg.SetData(screenshotImg.convert("RGB").tobytes())

        self.staticbit.SetBitmap(wx.Bitmap(wximg))

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
        self.left_img = _Image.open("resources/images/back_left.png").convert("RGBA")
        self.left_img_alpha = self.left_img.split()[3]
        self.right_img = _Image.open("resources/images/back_right.png").convert("RGBA")
        self.right_img_alpha = self.right_img.split()[3]
        self.bar_img = _Image.open("resources/images/home_bar.png").convert("RGBA")
        self.bar_img_alpha = self.bar_img.split()[3]

    def display_auto(self, image=None):
        if self.display_lock.acquire(blocking=False):
            self.Screen.wait_busy()
            self.display_lock.release()
            if not image:
                image = framework.struct.Page.render()

            if self._show_left_back:
                image.paste(self.left_img, mask=self.left_img_alpha)
            if self._show_right_back:
                image.paste(self.right_img, mask=self.right_img_alpha)
            if self._show_home_bar:
                image.paste(self.bar_img, mask=self.bar_img_alpha)

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

    def _shutdown(self):
        for i in self.apps.values():
            self.Pool.add(i.shutdown)
        for i in self.plugins.values():
            self.Pool.add(i.shutdown)
        for i in self.themes.values():
            self.Pool.add(i.shutdown)
        time.sleep(2)
        self.Screen.quit()

    def poweroff(self):
        self._shutdown()
        _os.system("sudo poweroff")

    def reboot(self):
        self._shutdown()
        _os.system("sudo reboot")

