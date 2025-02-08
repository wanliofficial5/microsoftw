from framework.struct import Book
from framework.lib import AppBase
from framework.lib import Pages


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
    def init(self):
        self.Page = ApplicationList(self)
        self.Pages["main"] = self.Page
        self.now_page = "main"


class Application(AppBase):
    def init(self):
        self.Book = MainBook(self)
        self.Books["main"] = self.Book
        self.now_book = "main"
