from applications.设置.about import AboutBook
from applications.设置.app import AppSettingsBook
from applications.设置.general import GeneralSettingsBook
from applications.设置.system import SystemSettingsBook
from framework import struct, lib
from framework import lib
import socket

from PIL import Image


class SettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        cb = book.base.change_book
        super().__init__(book, "设置",
                         ["连接APP",
                          "通用",
                          "系统选项",
                          "关于"],
                         funcs=[
                             lambda: cb("app"),
                             lambda: cb("general"),
                             lambda: cb("system"),
                             lambda: cb("about")
                         ],
                         styles=["NEXT"]*4
                         )


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", SettingsPage(self))


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.name = "设置"
        self.icon = Image.open("applications/设置/icon.png")
        self.title = self.name
        self.add_book("main", MainBook(self))
        self.add_book("app", AppSettingsBook(self), False)
        self.add_book("general", GeneralSettingsBook(self), False)
        self.add_book("system", SystemSettingsBook(self), False)
        self.add_book("about", AboutBook(self), False)

        self.show_in_drawer = False
