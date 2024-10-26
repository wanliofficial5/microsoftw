import threading
import time

from PIL import ImageFont, ImageDraw, Image

from framework import ThemeBase
from framework.struct import Book, Element
from framework.struct import Page


class TextClock(Element):
    def __init__(self, page):
        super().__init__(page)
        self.background = Image.new("RGB", (296, 128), (0, 0, 0))
        self.font25 = ImageFont.truetype(
            "resources/fonts/PTSerifCaption.ttc", 53)

    def render(self):
        new_image = self.background.copy()
        now_time = time.strftime("%H : %M", time.localtime())
        draw_image = ImageDraw.Draw(new_image)
        draw_image.text((58, 32), now_time, font=self.font25)
        return new_image


class MainPage(Page):
    def __init__(self, book):
        super().__init__(book)
        self.elements.append(TextClock(self))


class MainBook(Book):
    def __init__(self, base):
        super().__init__(base)
        self.Page = MainPage(self)
        self.Pages["main"] = self.Page
        self.now_page = "main"


class Theme(ThemeBase):
    def __init__(self, env):
        super().__init__(env)
        self.Book = MainBook(self)
        self.Books["main"] = self.Book
        self.now_book = "main"
        self.flag = False
        self.last_update = -1

    def updater(self):
        while 1:
            if self.flag:
                if self.last_update != time.localtime(time.time()).tm_min:
                    self.last_update = time.localtime(time.time()).tm_min
                    self.Book.Page.update()
            else:
                return
            time.sleep(2)

    def active(self):
        super().active()
        self.flag = True
        threading.Thread(target=self.updater, daemon=True).start()

    def pause(self):
        super().pause()
        self.flag = False
