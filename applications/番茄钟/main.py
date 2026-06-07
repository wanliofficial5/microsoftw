from framework import lib
from framework import struct

from PIL import ImageFont, Image


class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "番茄钟")
        self._background = Image.open("applications/番茄钟/background.png")
        self.start_button = lib.Elements.TextElementButton(self, size=(50, 50), text="25", location=(30, 43),
                                                           font=ImageFont.truetype("resources/fonts/PTSerifCaption.ttc",
                                                                                   40))
        self.add_element(self.start_button)
        self.add_element(lib.Elements.TextElement(self, (77, 70), "分", font_size=16))
        self.status_text = lib.Elements.TextElement(self, (30, 90), "开始计时")
        self.add_element(self.status_text)

    def start(self):
        pass


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", MainPage(self))


class Application(lib.AppBase):
    def __init__(self,env):
        super().__init__(env)
        self.add_book("main", MainBook(self))
