from framework import struct
from framework import lib

from PIL import Image
from threading import Timer
import time


class CountdownTimer():
    def __init__(self, func):
        self.func = func
        self.start_time = 0
        self.Timer = None
        self.length = 0

    def start(self, length):
        self.length = length
        self.start_time = time.time()
        if self.Timer:
            self.Timer.cancel()
        self.Timer = Timer(length, self.func)
        self.Timer.start()

    def pause(self):
        if self.Timer.is_alive():
            self.length = time.time() - self.start_time
            self.Timer.cancel()

    def continue_(self):
        if not self.Timer.is_alive():
            self.Timer = Timer(self.length, self.func)
            self.Timer.start()

    def cancel(self):
        if self.Timer:
            self.Timer.cancel()


class SetTimePage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "倒计时 - 自定义")
        pass


class ChoicePage(lib.Pages.ListPage):
    def __init__(self, book):
        self.settings = [
            "自定义",
            "1 分钟",
            "3 分钟",
            "5 分中",
            "10 分钟",
            "15 分钟",
            "30 分钟",
            "1 小时",
            "2 小时"
        ]
        self.times = [
            60,
            180,
            300,
            600,
            900,
            1800,
            3600,
            7200
        ]
        self.icons = [Image.open("applications/倒计时/edit.png")] + [Image.open("applications/倒计时/time.png")] * 8
        super().__init__(book, "倒计时 - 选择时间", self.settings, func=self.handler, icons=self.icons)

    def handler(self, index):
        if index == 0:
            pass
        else:
            self.book.start(self.times[index - 1])


class CountPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "倒计时")
        self.last_time = \
            self.add_element(lib.Elements.Label(self, (0, 40), (296, 40), text="00:00", font_size=48, align="C"))
        self.pause_image = Image.open("applications/倒计时/pause.png")
        self.continue_image = Image.open("applications/倒计时/continue.png")
        self.cancel_image = Image.open("applications/倒计时/cancel.png")
        self.control_button = self.add_element(lib.Elements.ImageButton(self, (135, 90), (18, 18),
                                                                        func=self.control,
                                                                        image=self.pause_image))
        self.cancel_button = self.add_element(lib.Elements.ImageButton(self, (165, 90), (18, 18),
                                                                       func=self.book.cancel,
                                                                       image=self.cancel_image,
                                                                       show=False))
        self.length = 0
        self.start_time = 0

        self.flag = False

        self.paused = 0

        self.clock = self.add_element(lib.Elements.Label(self, (0, 0), size=(296, 30), border=(5, 8), font_size=16,
                                                         align="R"))

    def clock_updater(self):
        last_clock = time.strftime("%H:%M", time.localtime())
        while self.flag:
            time.sleep(2)
            now = time.strftime("%H:%M", time.localtime())
            if last_clock != now:
                self.clock.set_text(now)
                last_clock = now

    def time_updater(self):
        time.sleep(2)
        t = self.length - (time.time() - self.start_time) + 1
        h = t // 3600
        m = (t - h * 3600) // 60
        last_text = "%0.2d:%0.2d" % (h, m)
        while self.flag and not self.paused:
            t = self.length - (time.time() - self.start_time) + 1
            if t < 0:
                break
            h = t // 3600
            m = (t - h * 3600) // 60
            text = "%0.2d:%0.2d" % (h, m)
            if text != last_text:
                last_text = text
                self.last_time.set_text(last_text)
            time.sleep(2)

    def set_time(self, length):
        self.control_button.set_image(self.pause_image)
        self.length = length
        self.start_time = time.time()

    def active(self):
        self.flag = True
        t = self.length - (time.time() - self.start_time) + 1
        h = t // 3600
        m = (t - h * 3600) // 60
        text = "%0.2d:%0.2d" % (h, m)
        self.last_time.set_text(text)
        self.book.base.env.Pool.add(self.time_updater)
        self.clock.set_text(time.strftime("%H:%M", time.localtime()), False)
        self.book.base.env.Pool.add(self.clock_updater)
        super().active()

    def pause(self):
        self.flag = False

    def control(self):
        if self.book.cont_down_timer.Timer.is_alive():
            self.control_button.set_image(self.continue_image, False)
            self.cancel_button.set_show(True)
            self.paused = self.length - (time.time() - self.start_time)
            self.book.control(False)
        elif self.paused:
            self.cancel_button.set_show(False)
            self.set_time(self.paused)
            self.paused = 0
            self.book.base.env.Pool.add(self.time_updater)
            self.book.control(True)


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("count", CountPage(self))
        self.add_page("choice", ChoicePage(self))

        self.counting = False

        self.cont_down_timer = CountdownTimer(self.finish)

    def cancel(self):
        self.cont_down_timer.cancel()
        self.counting = False
        self.change_page("choice", False)

    def control(self, m):
        if m:
            self.cont_down_timer.continue_()
        else:
            self.cont_down_timer.pause()

    def finish(self):
        self.base.env.display(refresh="t")
        self.counting = False
        if self._active:
            self.change_page("choice")
            self.base.env.notice("倒计时结束", self.base.icon)
        else:
            self.base.env.notice("倒计时结束", self.base.icon, lambda: self.base.env.change_page("倒计时"))

    def start(self, length):
        self.counting = True
        self.Pages['count'].set_time(length)
        self.change_page("count", to_stack=False)
        self.cont_down_timer.start(length)

    def active(self):
        if self.counting:
            self.change_page("count", to_stack=False)
        else:
            self.change_page("choice", to_stack=False)
        super().active()


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.add_book("main", MainBook(self))
        self.icon = Image.open("applications/倒计时/icon.png")
        self.title = "倒计时"
