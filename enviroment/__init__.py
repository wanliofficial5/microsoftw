import threading as _threading
import time as _time
from queue import LifoQueue as _LifoQueue

# 模拟器GUI wxpython
import wx as _wx

from PIL import Image as _Image, \
    ImageFont as _ImageFont, \
    ImageDraw as _ImageDraw

from system import threadpool as _threadpool
from system import logger as _logger
from .touchscreen import Clicked as _Clicked, \
    SlideY as _SlideY, \
    TouchHandler as _TouchHandler, \
    TouchRecoder as _TouchRecoder
from .touchscreen.events import SlideX as _SlideX, Clicked as _Clicked
import os as _os
from framework.struct import Base as _Base
from framework import lib as _lib
from system import configurator

example_config = {
    "theme": "默认（黑）",
    "docker": ["天气"]
}


class Choice:
    def __init__(self, title, text, icon, false_text, true_text):
        self.icon = icon
        self.title = title
        self.text = text
        self.false_text = false_text
        self.true_text = true_text
        self.event_1 = _threading.Event()
        self.result = None
        self.event_2 = _threading.Event()


class Prompt:
    def __init__(self, title, text, icon):
        self.icon = icon
        self.title = title
        self.text = text


class Notice:
    def __init__(self, text, icon, func):
        self.text = text
        self.icon = icon
        self.func = func


# 模拟器屏幕
class Simulator:
    def __init__(self):
        self.env = None
        self.touch_recoder_dev = _TouchRecoder()
        self.touch_recoder_old = _TouchRecoder()
        self.app = _wx.App()
        # 创建窗口(296x128)
        self.frame = _wx.Frame(None, title="水墨屏模拟器 v2.0 by xuanzhi33", size=(296, 155))
        self.frame.SetMaxSize((296, 155))
        self.frame.SetMinSize((296, 155))

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


class FakePage:
    def __init__(self, env):
        self.env = env

    @staticmethod
    def update(*args, **kwargs):
        pass

    def __getattr__(self, _):
        return self


class Env:
    def __init__(self, simulator):
        self.config = configurator.Configurator()
        self.config.check(example_config, True)

        # locks
        self.display_lock = _threading.Lock()

        # fonts
        self.fonts = {}

        # screen
        self.Screen = simulator

        # logger
        self.Logger = _logger.Logger(0)

        # threadpool
        self.Pool = _threadpool.ThreadPool(20, self.Logger.warn)
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
        self._update_temp = False
        self._home_bar = False
        self._home_bar_temp = 0

        # images
        self.none18px_img = _Image.open("resources/images/None18px.jpg")
        self.none20px_img = _Image.open("resources/images/None20px.jpg")
        self.docker_img = _Image.open("resources/images/docker.jpg")
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
        self.page_with_title_img = _Image.open("resources/images/page_with_title.png")
        self.ok_img = _Image.open("resources/images/ok.png")
        self.ok_alpha = self.ok_img.split()[3]
        self.prompt_img = _Image.open("resources/images/prompt.png")
        self.prompt_alpha = self.prompt_img.split()[3]
        self.choice_img = _Image.open("resources/images/choice.png")
        self.choice_alpha = self.choice_img.split()[3]
        self.notice_img = _Image.open("resources/images/notice.png")
        self.notice_alpha = self.notice_img.split()[3]
        self.on_img = _Image.open("resources/images/on.png").convert("RGBA")
        self.on_alpha = self.on_img.split()[3]
        self.off_img = _Image.open("resources/images/off.png").convert("RGBA")
        self.off_alpha = self.off_img.split()[3]

        # choice
        self._events_stack = []

        self._fake = FakePage(self)
        self._label_left = _lib.Elements.Label(self._fake, size=(85, 12), align="C", location=(0, 0))
        self._label_right = _lib.Elements.Label(self._fake, size=(85, 12), align="C", location=(0, 0))
        self._multiple_text = _lib.Elements.MultipleLinesLabel(self._fake, location=(0, 0), size=(0, 0), border=(3, 0))

        self._event_close_clicked = _Clicked((210, 235, 28, 53), self._close_event)
        self._false_clicked = _Clicked((59, 147, 82, 102), self._choice_handler, False)
        self._true_clicked = _Clicked((147, 237, 82, 102), self._choice_handler, True)

        # notice
        self._notices = []
        self._notice_clicked_s = [_Clicked((0, 296, 0, 36), self._notice_handler, True),
                                  _Clicked((0, 296, 36, 128), self._notice_handler, False)]

    def __getattr__(self, name):
        if name in self.plugins:
            return self.plugins[name]
        else:
            raise AttributeError("plugins no found.")

    def display(self, image=None, refresh="a"):
        if not image:
            image = self.Now.Book.render()
        if self.display_lock.acquire(blocking=False):
            self.Screen.wait_busy()
            self.display_lock.release()

            self._update_temp = False

            draw = _ImageDraw.ImageDraw(image)
            if self._events_stack:
                handling = self._events_stack[-1]
                if isinstance(handling, Choice):
                    image.paste(self.choice_img, mask=self.choice_alpha)
                    self._multiple_text.set_size((174, 30))
                    self._label_left.set_text(handling.false_text)
                    temp = self._label_left.render()
                    a = temp.split()[3]
                    image.paste(temp, (61, 86), mask=a)
                    self._label_right.set_text(handling.true_text)
                    temp = self._label_right.render()
                    a = temp.split()[3]
                    image.paste(temp, (148, 86), mask=a)
                else:
                    image.paste(self.prompt_img, mask=self.prompt_alpha)
                    self._multiple_text.set_size((174, 48))
                if handling.icon:
                    image.paste(handling.icon, (65, 32))
                    draw.text((88, 34), handling.title, "black", font=self.get_font(16))
                else:
                    draw.text((65, 34), handling.title, "black", font=self.get_font(16))
                self._multiple_text.set_text(handling.text)
                temp = self._multiple_text.render()
                a = temp.split()[3]
                image.paste(self._multiple_text.render(), (61, 53), mask=a)

            if self._notices:
                handling = self._notices[-1]
                image.paste(self.notice_img, (0, 0), mask=self.notice_alpha)
                if handling.icon:
                    image.paste(handling.icon, (10, 9))
                    draw.text((34, 10), handling.text, "black", font=self.get_font(16))
                else:
                    draw.text((10, 10), handling.text, "black", font=self.get_font(16))

            if self._show_left_back:
                image.paste(self.left_img, mask=self.left_img_alpha)
            if self._show_right_back:
                image.paste(self.right_img, mask=self.right_img_alpha)
            if self._home_bar:
                image.paste(self.bar_img, mask=self.bar_img_alpha)

            if refresh == "a":
                self.Screen.display_auto(image)
            elif refresh == "t":
                self.Screen.display(image)
            elif refresh == "f":
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
        flag = False
        if self._notices:
            self._notices = []
            flag = True
        while self._events_stack:
            self._close_event()
            flag = True
        if flag:
            self.TouchHandler.clear_clicked()
        if self.Now is not self.themes[self.now_theme]:
            self.Now.pause()
            self.Now = self.themes[self.now_theme]
            self.Now.active("t")
            return True

    def open_app(self, target: str, to_stack=True):
        if target in self.apps:
            if self.apps[target] is not self.Now:
                self.Now.pause()
                if to_stack:  # TODO:在这里添加异常处理
                    self.back_stack.put(self.Now)
                self.Now = self.apps[target]
                self.Now.active("t")
        else:
            raise KeyError("The targeted application is not found.")

    def back(self) -> bool:
        self._update_temp = self._show_left_back or self._show_right_back
        self._show_left_back = False
        self._show_right_back = False
        if self._notices:
            self._notice_handler(False)
            return True
        if self._events_stack:
            self._close_event()
            return True
        if self.back_stack.empty():
            if self._update_temp:
                self.display()
            return self.Now.back()
        else:
            i = self.back_stack.get()
            if callable(i):
                i()
                if self._update_temp:
                    self.display()
                return True
            elif isinstance(i, _Base):
                if self.Now.back():
                    self.back_stack.put(i)
                else:
                    self.Now.pause()
                    self.Now = i
                    self.Now.active()
                if self._update_temp:
                    self.display()
                return True
            else:
                if self._update_temp:
                    self.display()
                return False

    def add_back(self, item):
        self.back_stack.put(item)

    def back_left(self, show: bool):
        if show:
            self._show_left_back = True
            self.display(refresh="f")
        else:
            self._show_left_back = False
            self.display(refresh="f")

    def back_right(self, show: bool):
        if show:
            self._show_right_back = True
            self.display(refresh="f")
        else:
            self._show_right_back = False
            self.display(refresh="f")

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

    def start(self):
        self.now_theme = self.config.read("theme")
        try:
            self.Now = self.themes[self.now_theme]
        except KeyError:
            self.now_theme = "默认（黑）"
            self.Now = self.themes["默认（黑）"]
            self.config.set("theme", "默认（黑）")
        self.Now.active()
        self.notice("欢迎使用!beta版不代表成品质量。")

    def poweroff(self):
        self.Logger.info("关机")
        self.Screen.display(_Image.open("resources/images/raspberry.jpg"))
        self.quit()
        _os.system("sudo poweroff")

    def reboot(self):
        self.Logger.info("重启")
        self.Screen.display(_Image.open("resources/images/raspberry.jpg"))
        self.quit()
        _os.system("sudo reboot")

    @staticmethod
    def clean_logs():
        _os.system("rm -f logs/*")

    def screenshot(self):
        return self.Now.Book.render()

    def _touch_setter(self):
        if self._notices:
            self.TouchHandler.set_clicked(self._notice_clicked_s)
        elif self._events_stack:
            if isinstance(self._events_stack[-1], Choice):
                self.TouchHandler.set_clicked([self._event_close_clicked, self._true_clicked, self._false_clicked])
            else:
                self.TouchHandler.set_clicked([self._event_close_clicked])
        else:
            self.TouchHandler.clear_clicked()

    def _close_event(self):
        handling = self._events_stack[-1]
        if isinstance(handling, Choice):
            handling.result = False
            handling.event_1.set()
            handling.event_2.wait()
            handling.event_1.set()
        del self._events_stack[-1]
        self._touch_setter()
        self.display()

    def _choice_handler(self, result):
        handling = self._events_stack[-1]
        handling.result = result
        handling.event_1.set()
        handling.event_2.wait()
        del self._events_stack[-1]
        handling.event_1.set()
        self._touch_setter()
        self.display()

    def _notice_handler(self, result):
        if result:
            func = self._notices[-1].func
            del self._notices[-1]
            self._update_temp = True
            self._touch_setter()
            func()
            if self._update_temp:
                self.display()
        else:
            del self._notices[-1]
            self._touch_setter()
            self.display()

    def choice(self, title, text="", icon=None, false_text="取消", true_text="确认") -> bool:
        c = Choice(title, text, icon, false_text, true_text)
        self._events_stack.append(c)
        self._touch_setter()
        self.display()
        c.event_1.wait()
        c.event_1.clear()
        r = c.result
        c.event_2.set()
        c.event_1.wait()
        return r

    def prompt(self, title, text="", icon=None):
        p = Prompt(title, text, icon)
        self._events_stack.append(p)
        self._touch_setter()
        self.display()

    def notice(self, text="", icon=None, func=lambda: None):
        self._notices.append(Notice(text, icon, func))
        self._touch_setter()
        self.display()
