import requests
import json
import re

from framework import lib
from framework import struct

from PIL import Image


class Weather:
    def __init__(self, temp_max, temp_min, text, icon):
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.text = text
        # self.icon16 = Image.open(f"applications/天气/res/{icon}-16px.png")
        self.icon36 = Image.open(f"applications/天气/res/{icon}-36px.png")
        self.icon44 = Image.open(f"applications/天气/res/{icon}-44px.png")


class WeatherForecast:
    def __init__(self):
        self.KEY = "59b00c1051db4109b017c26c8fe8dfaf"
        self.city_name = None
        self.city_id = None
        self.city_lat = None
        self.city_lon = None

    def get_city(self):
        city_name = re.findall('省(.+?)市', requests.get("https://pv.sohu.com/cityjson?ie=utf-8").text)[-1]
        lookup = json.loads(requests.get(f"https://geoapi.qweather.com/v2/city/lookup?"
                                         f"location={city_name}&key={self.KEY}").text)["location"][0]
        self.city_name = lookup["name"]
        self.city_id = lookup["id"]
        self.city_lat = lookup["lat"]
        self.city_lon = lookup["lon"]

    def get_summary(self):
        result = json.loads(requests.get(f"https://devapi.qweather.com/v7/minutely/5m?"
                                         f"location={self.city_lat},{self.city_lon}&key={self.KEY}").text)["summary"]
        return result

    def get_now(self):
        now = json.loads(requests.get(f"https://devapi.qweather.com/v7/weather/now?"
                                      f"location={self.city_id}&key={self.KEY}").text)["now"]
        temp = now["temp"]
        text = now["text"]
        return text, temp

    def get_weather(self):
        weather = json.loads(
            requests.get(f"https://devapi.qweather.com/v7/weather/3d?location={self.city_id}&key={self.KEY}").text)[
            "daily"]
        result = []
        for i in range(len(weather)):
            w = weather[i]
            result.append(Weather(w["tempMax"], w["tempMin"], w["textDay"], w["iconDay"]))
        return result


class TodayPage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self.city = book.base.city
        self._background = book.background
        self.title = lib.Elements.TextElement(self, (11, 9), "天气")
        self.add_element(self.title)
        self.weather_icon = lib.Elements.Image(self, (25, 51), Image.open("applications/天气/res/100-44px.png"))
        self.add_element(self.weather_icon)
        self.text = lib.Elements.TextElement(self, (35, 98), "...")
        self.add_element(self.text)
        self.city_text = lib.Elements.TextElement(self, (88, 46), self.city)
        self.add_element(self.city_text)
        self.now_temp = lib.Elements.TextElement(self, (88, 61), "0℃", font_size=24)
        self.add_element(self.now_temp)
        self.temp_range = lib.Elements.TextElement(self, (90, 85), "0-0℃", font_size=16)
        self.add_element(self.temp_range)
        self.summary_text = lib.Elements.TextElement(self, (89, 102), "API失效啦，晚点再来试试吧～")
        self.add_element(self.summary_text)


class MorePage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self._background = book.background


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.background = Image.open("applications/天气/background.png")
        self.add_page("today", TodayPage(self))
        self.add_page("more", MorePage(self), False)

    def updating(self):
        pass

    def show_today(self):
        weather = self.base.weather
        now = self.base.now_weather
        page = self.Pages["today"]
        page.weather_icon.set_image(weather[0].icon44, False)
        page.text.set_text(now[0], False)
        page.now_temp.set_text(now[1]+"℃", False)
        page.temp_range.set_text(f"{weather[0].temp_min}-{weather[0].temp_max}℃")


    def show_more(self):
        pass

class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.forcast = WeatherForecast()
        self.forcast.get_city()
        self.city = self.forcast.city_name
        self.add_book("main", MainBook(self))
        self.now_weather = None
        self.weather = None
        self.icon = Image.open("applications/天气/icon.png")
        self.name = "天气"
        self.title = "天气"

    def active(self, refresh=True):
        self.Book.updating()
        super().active(refresh)
        self.now_weather = self.forcast.get_now()
        self.weather = self.forcast.get_weather()
        self.Book.show_today()
        self.Book.show_more()
