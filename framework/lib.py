import threading
import time

from PIL import ImageDraw
from queue import LifoQueue

from framework.struct import Page as _Page, Element as _Element, Book as _Book, Base as _Base
from enviroment.touchscreen import Clicked


class AppList(_Book):
    def __init__(self, base):
        super().__init__(base)
        self.env = base.env
        self.index = 0

    def active(self):
        pass


class ThemeBase(_Base):
    def __init__(self, env):
        super().__init__(env)
        self._docker_image = self.env.images.docker_image
        self._docker_status = False

        self._inactive_clicked = [Clicked((0, 296, 0, 30), self.set_docker, True)]
        self._active_clicked = [Clicked((60, 100, 0, 30), self.open_applist),
                                Clicked((0, 296, 30, 128), self.set_docker, False),
                                Clicked((195, 235, 0, 30), self.open_setting)]

    def open_applist(self):
        pass

    def open_setting(self):
        pass

    def set_docker(self, value: bool):
        self._docker_status = value
        self.display()
        time.sleep(2)
        if self._docker_status:
            self._docker_status = False
            self.display()

    def display(self):
        if self._active:
            if self._docker_status:
                new_image = self.Book.Page.render()
                new_image.paste(self._docker_image, (60, 0))
                self.env.Screen.display_auto(new_image)
            else:
                self.env.Screen.display_auto(self.Book.render())

    @property
    def touch_records_clicked(self):
        if self._docker_status:
            return self.Book.Page.touch_records_clicked + self._active_clicked
        else:
            return self.Book.Page.touch_records_clicked + self._inactive_clicked


class AppBase(_Base):
    def __init__(self, env):
        super().__init__(env)
        self.title = ""
        self._control_bar_image = env.images.app_control
        self.icon = env.images.None20px
        self.clock_font = self.env.fonts.get_heiti(18)
        self.title_font = self.env.fonts.get_heiti(19)
        self._control_bar_status = False
        self._inactive_clicked = [Clicked((266, 296, 0, 30), self.set_control_bar, True)]
        self._active_clicked = [Clicked((266, 296, 0, 30), self.env.back_home),
                                Clicked((0, 296, 30, 128), self.set_control_bar, False)]

    def active(self):
        self._control_bar_status = False

    def display(self):
        if self._active:
            if self._control_bar_status:
                new_image = self.Book.Page.render()
                new_image.paste(self._control_bar_image, (0, 0))
                new_image.paste(self.icon, (4, 4))
                image_draw = ImageDraw.ImageDraw(new_image)
                image_draw.text((30, 5), self.title, fill="black", font=self.title_font)
                image_draw.text((150, 7), time.strftime("%H : %M", time.localtime()), fill="black",
                                font=self.clock_font)
                self.env.Screen.display_auto(new_image)
            else:
                self.env.Screen.display_auto(self.Book.render())

    def set_control_bar(self, value: bool):
        self._control_bar_status = value
        self.display()

    @property
    def touch_records_clicked(self):
        if self._control_bar_status:
            return self.Book.Page.touch_records_clicked + self._active_clicked
        else:
            return self.Book.struct.Page.touch_records_clicked + self._inactive_clicked


class Plugin:
    def __init__(self, env):
        self.env = env

    def launch(self) -> None:  # This function will be called when the eInkUI is launch.
        pass

    def shutdown(self) -> None:  # This function will be called when the eInkUI is shutdown.
        # Technically this function should be done in 5s
        pass
