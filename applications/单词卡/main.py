from framework import struct
from framework import lib
import time
import json
import random
from queue import LifoQueue
from enviroment.touchscreen.events import SlideX
from threading import Timer

from PIL import Image
import os


class Nexter:
    def __init__(self, func, t):
        self.func = func
        self.t = t
        self.timer = Timer(t, self.repeat)

    def start(self):
        if self.timer.is_alive():
            return
        self.timer.start()

    def repeat(self):
        self.timer = Timer(self.t, self.repeat)
        self.timer.start()
        self.func(False)

    def reset(self):
        try:
            self.timer.cancel()
        except:
            pass
        self.timer = Timer(self.t, self.repeat)
        self.timer.start()

    def cancel(self):
        try:
            self.timer.cancel()
            self.timer = Timer(self.t, self.repeat)
        except:
            pass


class WordsPage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self.words = json.load(open("applications/单词卡/words.json"))
        self.flag = False
        self.clock = self.add_element(lib.Elements.Label(self, (0, 0), size=(296, 30), border=(0, 8), font_size=16,
                                                         align="C"))

        self.word = self.add_element(lib.Elements.Label(self, (0, 40), (296, 50), (0, 0), text="abandon", font_size=36,
                                                        align="C"))
        self.mean = self.add_element(lib.Elements.Label(self, (0, 80), (296, 128), (0, 0), "抛弃", font_size=16,
                                                        align="C"))

        self.touch_records = [SlideX((0, 296, 0, 128), self.slide_handler)]

        self.prev_stack = LifoQueue(maxsize=20)
        self.next_stack = LifoQueue(maxsize=20)

        new = random.choice(self.words)
        self.word.set_text(new[0], False)
        self.mean.set_text(new[1], False)

        self.nexter = Nexter(self.go_next, 60)

    def slide_handler(self, dis):
        if dis > 0:
            self.go_prev()
        else:
            self.go_next()

    def pause(self):
        self.flag = False
        self.nexter.cancel()

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
        self.book.base.env.Pool.add(self.clock_updater)
        self.nexter.start()

    def go_prev(self):
        if self.prev_stack.empty():
            self.book.base.display("t")
        else:
            new = self.prev_stack.get()
            self.word.set_text(new[0], False)
            self.mean.set_text(new[1], False)
            self.update(refresh="t")

        self.nexter.reset()

    def go_next(self, i=True):
        if self.next_stack.empty():
            if self.prev_stack.full():
                self.prev_stack.get()
            self.prev_stack.put(
                (self.word.text,
                 self.mean.text)
            )
            new = random.choice(self.words)
        else:
            new = self.next_stack.get()

        self.word.set_text(new[0], False)
        self.mean.set_text(new[1], False)
        self.update(refresh="t")

        if i:
            self.nexter.reset()


class WordsBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("words", WordsPage(self))
        self.flag = None
        self.last = 0


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.add_book("words", WordsBook(self))
        self.icon = Image.open("applications/单词卡/icon.png")
        self.title = "单词卡"

    def active(self, refresh="a"):
        super().active(refresh)
        if not os.path.exists("applications/单词卡/t"):
            self.env.prompt("欢迎使用单词卡！", "随机显示高考3500词：\n每60秒自动切换单词，也可以左右滑动切换单词", icon=self.icon)
            open("applications/单词卡/t", "w")
