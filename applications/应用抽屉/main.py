from framework.struct import Book
from framework.lib import AppBase
from framework.lib import Pages

from PIL import Image


class ApplicationList(Pages.ListPage):
    def __init__(self, book):
        self.env = book.base.env
        super().__init__(book, "应用抽屉", [], func=self.open)

    def open(self, index):
        self.env.open_app(self.items[index])

    def update_app_list(self):
        for app in self.env.apps:
            if app in ["应用抽屉"]:
                continue
            self.items.append(app)
            self.icons.append(self.env.apps[app].icon)


class MainBook(Book):
    def __init__(self, book):
        super().__init__(book)
        self.add_page("main", ApplicationList(self))


class Application(AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.name = "应用抽屉"
        self.icon = Image.open("applications/应用抽屉/icon.png")
        self.title = self.name
        self.add_book("main", MainBook(self))

    def update_app_list(self):
        self.Book.Page.update_app_list()
