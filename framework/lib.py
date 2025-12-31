import time as _time
from math import ceil as _ceil

from PIL import ImageDraw as _ImageDraw, \
    Image as _Image

from framework.struct import Page as _Page, Element as _Element, Base as _Base
from enviroment.touchscreen import Clicked as _Clicked, \
    SlideY as _SlideY


class Elements:
    class Image(_Element):
        def __init__(self, page, location=(0, 0), image=None, show=True):
            super().__init__(page, location)
            self._image = image
            self._show = show

        @property
        def show(self):
            return self._show

        @show.setter
        def show(self, value):
            if value != self._show:
                self._show = value
                self.page.update()

        @property
        def image(self):
            return self._image

        def set_image(self, value, display=True):
            self._image = value
            self.page.update(display)

        def render(self):
            if self._show:
                return self._image

    class TextElement(_Element):
        def __init__(self, page, location=(0, 0), text="", font=None, font_size=12, color="black", background=None,
                     show=True):
            super().__init__(page, location)
            self.color = color
            self._background = background
            self.text = text
            self.background = None
            if font:
                self._font = font
            else:
                self._font = self.page.book.base.env.get_font(font_size)
            self.image = None
            self._image_draw = None
            self.update(False)
            self._show = show

        @property
        def show(self):
            return self._show

        @show.setter
        def show(self, value):
            if value != self._show:
                self._show = value
                self.page.update()

        def update(self, display=True):
            self.background = _Image.new("RGBA", (296, 128), self._background) if self._background else \
                _Image.new("RGBA", (296, 128), (255, 255, 255, 0))
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            self._image_draw.text((0, 0), self.text, self.color, self._font)
            self.page.update(display)

        def set_text(self, value, update=True):
            self.text = value
            self.update(update)

        def set_color(self, value, update=True):
            self.color = value
            self.update(update)

        def set_background(self, value, update=True):
            self._background = value
            self.update(update)

        def set_font(self, font=None, font_size=12, update=True):
            if font:
                self._font = font
            else:
                self._font = self.page.book.base.env.get_font(font_size)
            self.update(update)

        def render(self) -> _Image:
            return self.image

    class Label(TextElement):
        def __init__(self, page, size=(296, 128), location=(0, 0), border=(0, 0), text="", font=None, font_size=12,
                     color="black",
                     border_color=None, background=None, show=True):
            self.size = size
            self.border = border
            self.border_color = border_color
            super().__init__(page, location, text, font, font_size, color, background, show)

        def set_size(self, value, update=True):
            self.size = value
            self.update(update)

        def set_border(self, value, update=True):
            self.border = value
            self.update(update)

        def set_border_color(self, value, update=True):
            self.border_color = value
            self.update(update)

        def update(self, display=True):
            self.background = _Image.new("RGBA", self.size, self._background) if self._background else \
                _Image.new("RGBA", self.size, (255, 255, 255, 0))
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            self._image_draw.text(self.border, self.text, self.color, self._font)
            if self.border_color:
                self._image_draw.rectangle(xy=(0, self.size[0], 0, self.size[1]), fill=None, outline=self.border_color)
            self.page.update(display)

    class Button(Label):
        def __init__(self, page, size, func=lambda: None, location=(0, 0), border=(0, 0), text="", font=None,
                     font_size=12, color="black", border_color="black", background=None, show=True):
            self.border_color = border_color
            super().__init__(page, size, location, border, text, font, font_size, color, background, show)
            self.func = func
            self.touch_records = [(_Clicked((location[0], location[0] + size[0], location[1], location[1] + size[1]),
                                            self.func))]

        def set_func(self, func):
            self.touch_records[0].func = func

    class MultipleLinesLabel(Label):
        def __init__(self, page, size=(296, 128), location=(0, 0), border=(0, 0), text="", font=None, font_size=12,
                     color="black", background=None, space=0, show=True):
            self.space = space
            super().__init__(page, size, location, border, text, font, font_size, color, background, show)

        def set_text(self, value, update=True):
            self.text = value.split("\n")
            self.update(update)

        def update(self, display=True):
            text = self.text.split("\n")
            self.background = _Image.new("RGBA", self.size, self._background) if self._background else \
                _Image.new("RGBA", self.size, (255, 255, 255, 0))
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            line_length = self.size[0] - 2 * self.border[0] - 4
            font_size = self._font.size
            new_text = ""
            if font_size % 12 == 0:
                add = font_size * 2 / 3
            else:
                add = font_size / 2
            for i in text:
                length = 0
                start = 0
                end = 0
                for j in i:
                    if " " <= j <= "~":
                        length += add
                        end += 1
                    else:
                        length += font_size
                        end += 1
                    if length > line_length:
                        length = 0
                        new_text += f"{i[start: end]}\n"
                        start = end
                new_text += f"{i[start: end]}\n"
            self._image_draw.text(self.border, new_text, self.color, self._font, space=self.space)
            self.page.update(display)


class Pages:
    class ListPage(_Page):
        def __init__(self, book, title, items: [str], icons=None, funcs=None, func=None):
            super().__init__(book)
            self._background = book.base.env.list_img
            self.more_img = book.base.env.list_more_img
            self.old_render = self.background
            self.title = title
            self.items = items
            self.font = book.base.env.get_font(16)
            self.icons = icons if icons else [None] * len(items)
            self.funcs = funcs if funcs else [lambda: None] * len(items)
            self.func = func
            self.at = 0
            if not len(items) == len(self.icons) == len(self.funcs):
                raise ValueError("Quantity asymmetry!")
            self.touch_records = [
                _Clicked((0, 296, 31, 60), self._handler, 0),
                _Clicked((0, 296, 61, 90), self._handler, 1),
                _Clicked((0, 296, 91, 120), self._handler, 2),
                _SlideY((0, 296, 0, 128), self._slide)
            ]

        def add_element(self, element):
            raise Exception("No support.")

        def append(self, item, icon=None, func=lambda: None, display=True):
            self.items.append(item)
            self.icons.append(icon)
            self.funcs.append(func)
            self.update(display)

        def remove(self, item, display=True):
            for i in range(len(self.items)):
                if self.items[i] == item:
                    del self.items[i]
                    del self.icons[i]
                    del self.funcs[i]
                    self.at = 0
                    break
            else:
                raise ValueError("Item not found!")
            self._update = True
            self.update(display)

        def insert(self, index, item, icon=None, func=lambda: None, display=True):
            self.items.insert(index, item)
            self.icons.insert(index, icon)
            self.funcs.insert(index, func)
            self._update = True
            self.update(display)

        def clear(self, display=True):
            self.items = []
            self.icons = []
            self.funcs = []
            self.at = 0
            self._update = True
            self.update(display)

        def set_items(self, items: [str], icons=None, funcs=None, display=True):
            self.items = items
            self.icons = icons if icons else [None] * len(items)
            self.funcs = funcs if funcs else [lambda: None] * len(items)
            self.at = 0
            if not len(items) == len(self.icons) == len(self.funcs):
                raise ValueError("Quantity asymmetry!")
            self._update = True
            self.update(display)

        def _handler(self, index):
            if index >= len(self.items):
                return
            if self.func:
                self.func(index)
            else:
                self.funcs[self.at * 3 + index]()

        def _slide(self, dis):
            if dis < 0:
                self.go_next()
            else:
                self.go_prev()

        def go_next(self, display=True):
            if (self.at + 2) * 3 - len(self.items) < 3:
                self.at += 1
                self._update = True
                self.update(display)

        def go_prev(self, display=True):
            if self.at > 0:
                self.at -= 1
                self._update = True
                self.update(display)

        def go_to(self, index=0, display=True):
            self.at = index
            self._update = True
            self.update(display)

        def render(self):
            if self._update:
                new_image = self.background.copy()
                draw = _ImageDraw.ImageDraw(new_image)
                draw.text((10, 8), self.title, "black", self.font)
                draw.text((254, 8), f"{self.at + 1}/{_ceil(len(self.items) / 3)}", "black", self.font)
                for i in range(3):
                    index = self.at * 3 + i
                    if index + 1 > len(self.items):
                        break
                    y = 37 + i * 30
                    if self.icons[index]:
                        new_image.paste(self.icons[index], (8, y))
                        draw.text((35, y + 2), self.items[index], "black", self.font)
                    else:
                        draw.text((8, y + 2), self.items[index], "black", self.font)
                if self.at * 3 + 3 < len(self.items):
                    new_image.paste(self.more_img, (105, 122))
                self.old_render = new_image
                self._update = False
                return new_image.copy()
            else:
                return self.old_render.copy()


class ThemeBase(_Base):
    def __init__(self, env):
        super().__init__(env)
        self._docker_image = self.env.images.docker_image
        self._docker_status = False
        self._docker_temp = 0

        self._inactive_clicked = [_Clicked((0, 296, 0, 30), self.set_docker, True)]
        self._active_clicked = [_Clicked((60, 100, 0, 30), self.open_applist),
                                _Clicked((0, 296, 30, 128), self.set_docker, False),
                                _Clicked((195, 235, 0, 30), self.open_setting)]

    def active(self, refresh=True):
        self._docker_status = False
        super().active(refresh)

    def open_applist(self):
        self.env.open_app("应用抽屉")

    def open_setting(self):
        self.env.open_app("设置")

    def set_docker(self, value: bool):
        self._docker_status = value
        self.display()
        if value:
            self._docker_temp = _time.time()
            _time.sleep(2)
            if _time.time() - self._docker_temp >= 2:
                self._docker_status = False
                self.display()

    def display(self, refresh="auto"):
        if self._active:
            if self._docker_status:
                new_image = self.Book.render()
                new_image.paste(self._docker_image, (60, 0))
                self.env.display(new_image, refresh)
            else:
                self.env.display(self.Book.render(), refresh)

    @property
    def touch_records_clicked(self):
        if self._docker_status:
            return self.Book.Page.touch_records_clicked + self._active_clicked
        else:
            return self.Book.Page.touch_records_clicked + self._inactive_clicked


class AppBase(_Base):
    def __init__(self, env):
        self.title = ""
        self.icon = env.images.None20px
        self.name = ""

        super().__init__(env)

        self._control_bar_font = self.env.get_font(16)
        self._control_bar_image = env.app_control_img
        self._control_bar_mask = env.app_control_alpha
        self._control_bar_status = False
        self._control_bar_temp = 0
        self._inactive_clicked = [_Clicked((266, 296, 0, 30), self.set_control_bar, True)]
        self._active_clicked = [_Clicked((266, 296, 0, 30), self.env.back_home),
                                _Clicked((0, 296, 30, 128), self.set_control_bar, False)]

    def active(self, refresh=True):
        self._control_bar_status = False
        super().active(refresh)

    def display(self, refresh="auto"):
        if self._active:
            if self._control_bar_status:
                new_image = self.Book.render()
                new_image.paste(self._control_bar_image, (0, 0), mask=self._control_bar_mask)
                new_image.paste(self.icon, (6, 6))
                image_draw = _ImageDraw.ImageDraw(new_image)
                image_draw.text((30, 7), self.title, fill="black", font=self._control_bar_font)
                image_draw.text((224, 7), _time.strftime("%H:%M", _time.localtime()), fill="black",
                                font=self._control_bar_font)
                self.env.display(new_image, refresh)
            else:
                self.env.display(self.Book.render(), refresh)

    def set_control_bar(self, value: bool):
        self._control_bar_status = value
        self.display()
        if value:
            self._control_bar_temp = _time.time()
            _time.sleep(8)
            if _time.time() - self._control_bar_status >= 2:
                self._control_bar_status = False
                self.display()

    @property
    def touch_records_clicked(self):
        if self._control_bar_status:
            return self.Book.Page.touch_records_clicked + self._active_clicked
        else:
            return self.Book.Page.touch_records_clicked + self._inactive_clicked
