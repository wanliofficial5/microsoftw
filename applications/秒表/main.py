from framework import struct
from framework import lib


class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "秒表")


class MainBook(struct.Book):
    def __init__(self, app):
        super().__init__(app)
        self.add_page("main", MainPage(self))


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.name = '秒表'
        self.add_book("main", MainBook(self))
