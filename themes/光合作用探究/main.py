from framework import lib
from framework import struct


class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "培养箱检测")
        self.add_element(lib.Elements.TextElement(self, (10, 35), "温度", font_size=16))
        self.temp = self.add_element(lib.Elements.Label(self, (12, 50), (24, 24), text="20℃", font_size=24))
        self.add_element(lib.Elements.TextElement(self, (100, 35), "湿度", font_size=16))
        self.wet = self.add_element(lib.Elements.Label(self, (102, 50), (24, 24), text="70%", font_size=24))
        self.add_element(lib.Elements.TextElement(self, (190, 35), "氧气", font_size=16))
        self.oxy = self.add_element(lib.Elements.Label(self, (192, 50), (24, 24), text="2000", font_size=24))

        self.status = self.add_element(lib.Elements.TextElement(self, (10, 78), "运行状态：空闲"))
        self.box_status = self.add_element(lib.Elements.TextElement(self, (10, 93), "培养箱：在线"))
        self.server_status = self.add_element(lib.Elements.TextElement(self, (10, 108), "服务器: 已连接"))

        self.add_element(lib.Elements.LabelButton(self, size=(48, 16), func=self.exit, location=(250, 7), text="退出", font_size=16))

    def exit(self):
        self.book.base.env.change_theme("默认（黑）")

class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", MainPage(self))


class Theme(lib.ThemeBaseWithoutDocker):
    def __init__(self, env):
        super().__init__(env)
        self.add_book("main", MainBook(self))
