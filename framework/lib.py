import threading
import time

from PIL import ImageDraw, Image
from queue import LifoQueue

from framework.struct import Page as _Page, Element as _Element, Book as _Book, Base as _Base
from enviroment.touchscreen import Clicked


class Elements:
    class Image(_Element):
        def __init__(self, page, location=(0, 0), image=None):
            super().__init__(page, location)
            self._image = image

        @property
        def image(self):
            return self._image

        @image.setter
        def image(self, value, update=True):
            self._image = value
            if update:
                self.page.update()

        def render(self):
            return self._image

    class TextElement(_Element):
        def __init__(self, page, location=(0, 0), text="", font_size=13, color="black", background=None):
            super().__init__(page, location)
            self.background = Image.new("RGBA", (296, 128), background) if background else \
                self.background = Image.new("RGBA", (296, 128), (255, 255, 255, 0))
            self._font = self.page.book.env.get_font(font_size)
            self._font_size = font_size
            self._color = color
            self._background = background
            self._text = text
            self._image = self.background.copy()
            self._image_draw = ImageDraw.ImageDraw(self._image)
            self._image_draw.text((0, 0), text, color, self._font)

        def update(self, update=True):
            self._image = self.background.copy()
            self._image_draw = ImageDraw.ImageDraw(self._image)
            self._image_draw.text((0, 0), self._text, self._color, self._font)

        # FIXME: 使用函数而非属性

        @property
        def text(self):
            return self._text

        @text.setter
        def text(self, value):
            self._text = value
            self.update()

        @property
        def color(self):
            return self._color

        @color.setter
        def color(self, value):
            self._color = value
            self.update()

        @property
        def background(self):
            return self._background

        @background.setter
        def background(self, value):
            self._background = value
            self.update()

        @property
        def font_size(self):
            return self._font_size

        @font_size.setter
        def font_size(self, value, update=True):
            self._font_size = value
            self._font = self.page.book.get_font(value)
            self.update(update)

        def render(self) -> Image:
            pass

    class Label(TextElement):
        pass

    class Button(TextElement):
        pass

    class MutiLineLabel(TextElement):
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
