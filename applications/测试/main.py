from framework.struct import Book
from framework.lib import AppBase
from framework.lib import Pages

from PIL import Image


class ApplicationList(Pages.ListPage):
    def __init__(self, book):
        super().__init__(book, "应用抽屉", [])
        for app in self.book.base.env.apps:
            if app == "应用抽屉":
                continue
            self.items.append(app)
            self.icons.append(self.book.env.apps[app].icon)
            self.funcs.append(lambda: self.book.env.open_app(app))


class MainBook(Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", ApplicationList(self))


class Application(AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.name = "假的应用抽屉"
        self.icon = Image.open("applications/应用抽屉/icon.png")
        self.title = self.name
        self.add_book("main", MainBook(self))
