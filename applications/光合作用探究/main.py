from framework import lib
from framework import struct
import time


class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        self.env = book.base.env
        super().__init__(book, "光合作用探究启动器")

    def question(self):
        time.sleep(0.1)
        if self.env.choice("切换", "是否切换到光合作用探究模式？"):
            self.env.change_theme("光合作用探究")
        self.env.back_home()

    def active(self):
        self.env.Pool.add(self.question)


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", MainPage(self))


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.add_book("main", MainBook(self))
