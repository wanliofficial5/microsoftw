from framework import struct
from framework import lib

import time


class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "Hello World")
        self.add_element(lib.Elements.MultipleLinesLabel(self, location=(15, 35), size=(266, 108),
                                                         text="   这个程序源自于我们对创造的热爱，源自于最初的梦想，"
                                                              "其中必然有许多缺憾等待补全，但：\n"
                                                              "   这世界上最美不过的景致，是那些最初的心动不为人知...\n"
                                                              "   祝：在追逐热爱的路上越走越远！\n"
                                                              "             傅逸凡-2022-2-2 11:52"))

        self.clock = lib.Elements.Label(self, size=(296, 30), border=(4, 8), font_size=16, align="R")
        self.add_element(self.clock)

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


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)

        self.add_page("main", MainPage(self))


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)  # 重写每个函数都必须调用父方法
        self.title = "Hello World"  # 设置标题
        # self.icon = Image.open(...) 不设置，使用默认图标（none18px.jpg）

        self.add_book("main", MainBook(self))  # 添加主书页并命名为 "main"

    def active(self, refresh="a"):
        self.Book.Page.active()
        super().active(refresh)

    def pause(self):
        self.Book.Page.pause()
        super().pause()
