from framework.struct import Book
from framework.lib import AppBase
from framework.lib import Pages

from PIL import Image


class ApplicationList(Pages.ListPage):
    def __init__(self, book):
        super().__init__(book, "应用抽屉", [])

    def update_app_list(self):
        for app in self.book.base.env.apps:
            if app == "应用抽屉":
                continue
            self.items.append(app)
            self.icons.append(self.book.base.env.apps[app].icon)
            self.funcs.append(lambda: self.book.base.env.open_app(app))


class MainBook(Book):
    def init(self):
        self.Page = ApplicationList(self)
        self.Pages["main"] = self.Page
        self.now_page = "main"


class Application(AppBase):
    def init(self):
        self.name = "应用抽屉"
        self.Book = MainBook(self)
        self.Books["main"] = self.Book
        self.icon = Image.open("applications/应用抽屉/icon.png")
        self.now_book = "main"
        self.title = self.name

    def update_app_list(self):
        self.Book.Page.update_app_list()
