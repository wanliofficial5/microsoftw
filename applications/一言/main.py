from framework import struct
from framework import lib

from enviroment.touchscreen import events

from PIL import Image

import requests
import json
import time


def get_yiyan():
    yiyan = requests.get("https://v1.hitokoto.cn/").text
    yiyan = f'    {json.loads(yiyan)["hitokoto"]}\n--{json.loads(yiyan)["from"]}'
    return yiyan


class MainPage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self._background = book.base.env.page_with_title_img

        self.clock = lib.Elements.Label(self, (0, 0), size=(296, 30), border=(0, 8), font_size=16, align="C")
        self.add_element(self.clock)

        self.add_element(lib.Elements.TextElement(self, (10, 40), "一言说:", font_size=16))

        self.text = lib.Elements.MultipleLinesLabel(self, location=(0, 45), size=(296, 266), text="加载中",
                                                    border=(20, 20))
        self.add_element(self.text)

        self.touch_records_clicked = [events.Clicked((0, 128, 20, 128), self.next)]

        self.flag = False

    def pause(self):
        self.flag = False

    def clock_updater(self):
        last_clock = time.strftime("%H:%M", time.localtime())
        while self.flag:
            time.sleep(2)
            now = time.strftime("%H:%M", time.localtime())
            if last_clock != now:
                self.clock.set_text(now)
                last_clock = now

    def active(self):
        self.flag = True
        self.clock.set_text(time.strftime("%H:%M", time.localtime()), False)
        self.book.base.env.Pool.add(self.next)
        self.book.base.env.Pool.add(self.clock_updater)

    def next(self):
        self.text.set_text(get_yiyan())


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", MainPage(self))


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.icon = Image.open("applications/一言/icon.png")
        self.title = "一言"

        self.add_book("main", MainBook(self))

    def active(self, refresh="a"):
        self.Book.Page.active()
        super().active(refresh)

    def pause(self):
        self.Book.Page.pause()
        super().pause()
