from framework import lib
from framework import struct



class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "植物光合作用探究")


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", MainPage(self))


class Theme(lib.ThemeBaseWithoutDocker):
    def __init__(self, env):
        super().__init__(env)
        self.add_book("main", MainBook(self))
