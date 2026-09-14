import threading
import time

from framework import lib
from framework import struct

from PIL import ImageFont, Image, ImageDraw

"""
status = {
    0: "开始计时",
    1: "暂停",
    2: "继续",
    3: "休息一下",
    4: "暂停",
    5: "继续"
}
"""


class Time(lib.Elements.TextElement):
    def update(self, display=True):
        self.background = Image.new("RGBA", (296, 128), self._background) if self._background else \
            Image.new("RGBA", (296, 128), (255, 255, 255, 0))
        self.image = self.background.copy()
        self._image_draw = ImageDraw.ImageDraw(self.image)
        if len(self.text) == 1:
            self.text = "0" + self.text
        self._image_draw.text((0, 0), self.text, self.color, self._font)
        self.page.update(display)


class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        self.env = book.base.env
        self.work_time = 25
        self.break_time = 5
        super().__init__(book, "番茄钟")
        try:
            file = open(f"applications/番茄钟/record.txt", "r")
            self.tomato = int(file.readline())
            file.close()
        except:
            file = open(f"applications/番茄钟/record.txt", "w")
            file.write("0")
            file.close()
            self.tomato = 0
        self._background = Image.open("applications/番茄钟/background.png")
        self.time = Time(self, text=str(self.work_time), location=(30, 43),
                         font=ImageFont.truetype("resources/fonts/PTSerifCaption.ttc", 40))
        self.add_element(self.time)
        self.add_element(lib.Elements.TextElement(self, (77, 70), "分", font_size=16))
        self.status_text = lib.Elements.Label(self, (114, 12), (0, 90), text="开始计时", align="C")
        self.add_element(self.status_text)
        self.add_element(lib.Elements.ImageButton(self, self.control, (114, 266), (0, 30)))
        self.clock = lib.Elements.Label(self, (182, 36), (114, 58), text="00:00", font_size=36, align="C")
        self.add_element(self.clock)
        self.text_count = lib.Elements.Label(self, (182, 12), (114, 112), text=f"共获得{self.tomato}个番茄", align="C")
        self.add_element(self.text_count)
        self.reset_button = lib.Elements.ImageButton(self, self.reset, (182, 84), (114, 30))
        self.add_element(self.reset_button)

        self.status = 0
        self.flag = False
        self.last_clock = 0
        self.count_down = 25
        self.timer_flag = False
        self.last = 25

        self.timer = None

    def reset(self):
        self.timer_flag = False
        self.status = 0
        self.status_text.set_text("开始计时", False)
        self.time.set_text(str(self.work_time))

    def clock_updater(self):
        while self.flag:
            time.sleep(2)
            now = time.strftime("%H:%M", time.localtime())
            if self.last_clock != now:
                self.last_clock = now
                self.clock.set_text(self.last_clock)

    def timer_func(self, long):
        self.last = long

        def timer_func_func():
            if self.last == 0:
                self.time.set_text(str(self.last))
                if self.status == 1:
                    self.status = 3
                    self.tomato += 1
                    self.status_text.set_text("休息一下", False)
                    self.text_count.set_text(f"共获得{self.tomato}个番茄", False)
                    self.time.set_text(str(self.break_time))
                    file = open(f"applications/番茄钟/record.txt", "w")
                    file.write(str(self.tomato))
                    file.close()
                elif self.status == 4:
                    self.status = 0
                    self.status_text.set_text("开始计时", False)
                    self.time.set_text(str(self.work_time))
                if self.env.Now is not self.book.base:
                    self.env.open_app("番茄钟")
                time.sleep(0.5)
                self.env.display(refresh="t")
            else:
                self.last -= 1
                self.timer = threading.Timer(60, timer_func_func)
                self.timer.start()
                self.time.set_text(str(self.last))
                self.last -= 1

        self.last += 1
        timer_func_func()

    def control(self):
        if self.status == 0:
            self.status = 1
            self.status_text.set_text("暂停", False)
            self.timer_func(self.work_time)
        elif self.status == 1:
            self.status = 2
            self.status_text.set_text("继续", True)
            self.timer.cancel()
        elif self.status == 2:
            self.status = 1
            self.status_text.set_text("暂停", False)
            self.timer_func(self.last)
        elif self.status == 3:
            self.status = 4
            self.status_text.set_text("暂停", False)
            self.timer_func(self.break_time)
        elif self.status == 4:
            self.status = 5
            self.status_text.set_text("继续", True)
            self.timer.cancel()
        elif self.status == 5:
            self.status = 4
            self.status_text.set_text("暂停", False)
            self.timer_func(self.last)

    def active(self):
        self.last_clock = time.strftime("%H:%M", time.localtime())
        self.clock.set_text(self.last_clock, False)
        self.flag = True
        self.env.Pool.add(self.clock_updater)

    def pause(self):
        self.flag = False

    def start(self):
        pass


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", MainPage(self))


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.add_book("main", MainBook(self))
        self.title = "番茄时钟"

    def active(self, refresh="a"):
        self.Book.Page.active()
        super().active(refresh=refresh)

    def pause(self):
        super().pause()
        self.Book.Page.pause()
