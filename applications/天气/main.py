from framework import lib
from framework import struct

from PIL import Image


class TodayPage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self._background = Image.open("applications/天气/background.png")
        self.forcast = book.base.env.qweather
        self.title = lib.Elements.TextElement(self, (11, 9), "天气")
        self.add_element(self.title)
        self.weather_icon = lib.Elements.Image(self, (25, 45), Image.open("applications/天气/res/100-44px.png"))
        self.add_element(self.weather_icon)
        self.text = lib.Elements.TextElement(self, (35, 95), "...")
        self.add_element(self.text)
        self.now_temp = lib.Elements.TextElement(self, (88, 51), "0℃", font_size=24)
        self.add_element(self.now_temp)
        self.temp_range = lib.Elements.TextElement(self, (90, 75), "0-0℃", font_size=16)
        self.add_element(self.temp_range)
        self.summary_text = lib.Elements.TextElement(self, (89, 92), "加载中")
        self.add_element(self.summary_text)

    def get_weather(self):
        if self.forcast.is_inited():
            self.title.set_text(self.forcast.city)
            realtime = self.forcast.get_realtime()
            self.now_temp.set_text(realtime.temp + "℃", False)
            self.text.set_text(realtime.text, False)
            self.weather_icon.set_image(self.forcast.get_image(realtime.icon_id, 44), True)
            more = self.forcast.get_more()
            self.temp_range.set_text(f"{more[0].temp_min}-{more[0].temp_max}℃")
            self.summary_text.set_text(self.forcast.get_summary())
        else:
            self.title.set_text("网络错误")


class MorePage(struct.Page):
    def __init__(self, book):
        super().__init__(book)


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("today", TodayPage(self))
        self.add_page("more", MorePage(self), False)


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.icon = Image.open("applications/天气/icon.png")
        self.name = "天气"
        self.title = "天气"
        self.add_book("main", MainBook(self))

    def active(self, refresh="a"):
        super().active(refresh)
        self.env.Pool.add(self.Book.Pages["today"].get_weather)
