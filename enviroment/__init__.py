import threading as _threading
import time as _time
from queue import LifoQueue as _LifoQueue

# 模拟器GUI wxpython
import wx as _wx

from PIL import Image as _Image, \
    ImageFont as _ImageFont

from system import threadpool as _threadpool
from .touchscreen import Clicked as _Clicked, \
    SlideX as _SlideX, \
    SlideY as _SlideY, \
    TouchHandler as _TouchHandler, \
    TouchRecoder as _TouchRecoder
import os as _os
from framework.struct import Base as _Base


# 模拟器屏幕
class Simulator:
    def __init__(self):
        self.env = None
        self.touch_recoder_dev = _TouchRecoder()
        self.touch_recoder_old = _TouchRecoder()
        self.app = _wx.App()
        # 创建窗口(296x128)
        self.frame = _wx.Frame(None, title="水墨屏模拟器 v2.0 by xuanzhi33", size=(296, 160))

        self.static_bit = None

        self.touched = False

    def start(self, env):
        self.env = env

        # 背景为黑色图片
        bmp = _wx.Bitmap("resources/images/simplebytes.jpg")

        self.static_bit = _wx.StaticBitmap(self.frame, -1, bmp)

        # 绑定按下鼠标
        self.frame.Bind(_wx.EVT_LEFT_DOWN, self.mouse_down)
        # 绑定松开鼠标
        self.frame.Bind(_wx.EVT_LEFT_UP, self.mouse_up)
        # 绑定移动鼠标
        self.frame.Bind(_wx.EVT_MOTION, self.on_move)

        self.frame.Show()

        self.app.MainLoop()

    def on_move(self, event):
        if self.touched:
            x = event.GetX()
            y = event.GetY()
            self.touch_recoder_old.Touch = True
            self.touch_recoder_dev.Touch = True
            self.touch_recoder_dev.X[0] = x
            self.touch_recoder_dev.Y[0] = y
            self.env.TouchHandler.handle(self.touch_recoder_dev, self.touch_recoder_old)

    def mouse_down(self, event):
        x = event.GetX()
        y = event.GetY()
        self.touched = True
        self.touch_recoder_old.Touch = False
        self.touch_recoder_dev.Touch = True
        self.touch_recoder_dev.X[0] = x
        self.touch_recoder_dev.Y[0] = y
        self.env.TouchHandler.handle(self.touch_recoder_dev, self.touch_recoder_old)

    def mouse_up(self, event):
        x = event.GetX()
        y = event.GetY()
        self.touched = False
        self.touch_recoder_old.Touch = True
        self.touch_recoder_dev.Touch = False
        self.touch_recoder_dev.X[0] = x
        self.touch_recoder_dev.Y[0] = y
        self.env.TouchHandler.handle(self.touch_recoder_dev, self.touch_recoder_old)

    def updateImage(self, image: _Image):

        def bitmapThreading():
            wximg = _wx.Image(296, 128, image.convert("RGB").tobytes())
            bmp = _wx.Bitmap(wximg)
            self.static_bit.SetBitmap(bmp)
        _threading.Thread(target=bitmapThreading).start()

    def display(self, image: _Image):
        self.updateImage(image)

    def display_partial(self, image: _Image):
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
        self.fonts = {}

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
        self._home_bar = False
        self._home_bar_temp = 0

        # images
        self.images = Images()
        self.left_img = _Image.open("resources/images/back_left.png").convert("RGBA")
        self.left_img_alpha = self.left_img.split()[3]
        self.right_img = _Image.open("resources/images/back_right.png").convert("RGBA")
        self.right_img_alpha = self.right_img.split()[3]
        self.bar_img = _Image.open("resources/images/home_bar.png").convert("RGBA")
        self.bar_img_alpha = self.bar_img.split()[3]
        self.list_img = _Image.open("resources/images/list.png")
        self.list_more_img = _Image.open("resources/images/more_items_dots.jpg")
        self.app_control_img = _Image.open("resources/images/app_control.png")
        self.app_control_alpha = self.app_control_img.split()[3]

    def display(self, image=None, refresh="auto"):
        if not image:
            self.Now.display()
            return
        if self.display_lock.acquire(blocking=False):
            self.Screen.wait_busy()
            self.display_lock.release()

            if self._show_left_back:
                image.paste(self.left_img, mask=self.left_img_alpha)
            if self._show_right_back:
                image.paste(self.right_img, mask=self.right_img_alpha)
            if self._home_bar:
                image.paste(self.bar_img, mask=self.bar_img_alpha)

            if refresh == "auto":
                self.Screen.display_auto(image)
            elif refresh:
                self.Screen.display(image)
            else:
                self.Screen.display_partial(image)

    def get_font(self, size=12):
        if size in self.fonts:
            return self.fonts[size]
        elif not size % 12:
            self.fonts[size] = _ImageFont.truetype("resources/fonts/VonwaonBitmap-12px.ttf", size)
        elif not size % 16:
            self.fonts[size] = _ImageFont.truetype("resources/fonts/VonwaonBitmap-16px.ttf", size)
        else:
            raise ValueError("It can only be a multiple of 12 or 16.")
        return self.fonts[size]

    def back_home(self) -> bool:
        self.back_stack.queue.clear()
        if self.Now is not self.themes[self.now_theme]:
            self.Now.pause()
            self.Now = self.themes[self.now_theme]
            self.Now.active()
            return True

    def open_app(self, target: str, to_stack=True):
        if target in self.apps:
            self.Now.pause()
            if to_stack:  # TODO:在这里添加异常处理
                self.back_stack.put(self.Now)
            self.Now = self.apps[target]
            self.Now.active()
        else:
            raise KeyError("The targeted application is not found.")

    def back(self) -> bool:
        self._show_left_back = False
        self._show_right_back = False
        if self.back_stack.empty():
            return self.Now.back()
        else:
            i = self.back_stack.get()
            if callable(i):
                i()
                return True
            elif isinstance(i, _Base):
                if self.Now.back():
                    self.back_stack.put(i)
                else:
                    self.Now.pause()
                    self.Now = i
                    self.Now.active()
                return True
            else:
                return False

    def add_back(self, item):
        self.back_stack.put(item)

    def back_left(self, show: bool):
        if show:
            self._show_left_back = True
            self._left_temp = True
            self.display(refresh=False)
        else:
            self._show_left_back = False
            if self._right_temp:
                self.display(refresh=False)

    def back_right(self, show: bool):
        if show:
            self._show_right_back = True
            self._right_temp = True
            self.display(refresh=False)
        else:
            self._show_right_back = False
            if self._right_temp:
                self.display(refresh=False)

    def home_bar(self):
        if self._home_bar:
            self._home_bar = False
            if not self.back_home():
                self.display()
        else:
            self._home_bar = True
            self._home_bar_temp = _time.time()
            self.display()
            _time.sleep(1.5)
            if self._home_bar and _time.time() - self._home_bar_temp >= 1:
                self._home_bar = False
                self.display()

    def quit(self):
        for i in self.apps.values():
            self.Pool.add(i.shutdown)
        for i in self.plugins.values():
            self.Pool.add(i.shutdown)
        for i in self.themes.values():
            self.Pool.add(i.shutdown)
        _time.sleep(2)
        self.Screen.quit()

    def poweroff(self):
        self.Screen.display(_Image.open("resources/images/raspberry.jpg"))
        self.quit()
        _os.system("sudo poweroff")

    def reboot(self):
        self.Screen.display(_Image.open("resources/images/raspberry.jpg"))
        self.quit()
        _os.system("sudo reboot")

