import time as _time
from math import ceil as _ceil
from math import floor as _floor

from PIL import ImageDraw as _ImageDraw, \
    Image as _Image

from framework.struct import Page as _Page, Element as _Element, Base as _Base
from enviroment.touchscreen.events import Clicked as _Clicked, \
    SlideY as _SlideY, SlideX as _SlideX


class Elements:
    class Image(_Element):
        def __init__(self, page, location, image=None, show=True):
            super().__init__(page, location)
            self._image = image
            self.show = show

        def set_show(self, value, display=True, refresh="a"):
            if value != self.show:
                self.show = value
                self.page.update(display, refresh)

        @property
        def image(self):
            return self._image

        def set_image(self, value, display=True, refresh="a"):
            self._image = value
            self.page.update(display, refresh)

        def render(self):
            if self.show:
                return self._image

    class TextElement(_Element):
        def __init__(self, page, location, text="", font=None, font_size=12, color="black", background=None,
                     show=True):
            super().__init__(page, location)
            self.color = color
            self.background = background if background else _Image.new("RGBA", (296, 128), (255, 255, 255, 0))
            self.text = text
            if font:
                self._font = font
            else:
                self._font = self.page.book.base.env.get_font(font_size)
            self.image = None
            self._image_draw = None
            self.update(False)
            self.show = show

        def set_show(self, value, display=True, refresh="a"):
            if value != self.show:
                self.show = value
                self.page.update(display, refresh)

        def update(self, display=True, refresh="a"):
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            self._image_draw.text((0, 0), self.text, self.color, self._font)
            self.page.update(display, refresh)

        def set_text(self, value, display=True, refresh="a"):
            self.text = value
            self.update(display, refresh)

        def set_color(self, value, display=True, refresh="a"):
            self.color = value
            self.update(display, refresh)

        def set_background(self, value, display=True, refresh="a"):
            self.background = value
            self.update(display, refresh)

        def set_font(self, font=None, font_size=12, display=True, refresh="a"):
            if font:
                self._font = font
            else:
                self._font = self.page.book.base.env.get_font(font_size)
            self.update(display, refresh)

        def render(self) -> _Image:
            return self.image

    class Label(TextElement):
        def __init__(self, page, location, size, border=(0, 0), text="", font_size=12, color="black",
                     background=None, show=True, align="L"):
            """
            相较于TextElement，这个模块不支持自定义字体，但是可以实现文本的左对齐和右对齐和添加边界(border)功能
            """
            self.size = size
            self.border = border
            self.align = align
            super().__init__(page, location, text, font_size=font_size, color=color, background=background, show=show)

        def set_size(self, value, display=True, refresh="a"):
            self.size = value
            self.update(display, refresh)

        def set_border(self, value, display=True, refresh="a"):
            self.border = value
            self.update(display, refresh)

        def set_align(self, value, display=True, refresh="a"):
            self.align = value
            self.update(display, refresh)

        def update(self, display=True, refresh="a"):
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            if self.align == "L":
                x = self.border[0]
            else:
                length = 0
                font_size = self._font.size
                if font_size % 12 == 0:
                    add = font_size * 2 / 3
                else:
                    add = font_size / 2
                for i in self.text:
                    if " " <= i <= "~":
                        length += add
                    else:
                        length += font_size
                if self.align == "C":
                    x = _ceil((self.size[0] - length) / 2)
                elif self.align == "R":
                    x = self.size[0] - 2 * self.border[0] - length
                else:
                    raise ValueError

            self._image_draw.text((x, self.border[1]), self.text, self.color, self._font)
            self.page.update(display, refresh)

    class ImageButton(Image):
        def __init__(self, page, location, size, func, image=None, show=True):
            super().__init__(page, location, image, show)
            self.func = func
            self.size = size
            self.clicked = _Clicked((location[0], location[0] + size[0], location[1], location[1] + size[1]),
                                    self.func)
            if show:
                self.touch_records = [self.clicked]

        def set_show(self, value, display=True, refresh="a"):
            if value != self.show:
                self.show = value
                if value:
                    self.touch_records = [self.clicked]
                else:
                    self.touch_records = []
                self.page.update(display, refresh)

    class TextElementButton(TextElement):
        def __init__(self, page, location, size, func, border=(0, 0), text="", font=None, font_size=12, color="black",
                     background=None, show=True):
            self.size = size
            self.border = border
            self.func = func
            super().__init__(page, location, text, font, font_size, color, background, show)
            self.clicked = _Clicked((location[0], location[0] + size[0], location[1], location[1] + size[1]), self.func)
            if show:
                self.touch_records = [self.clicked]

        def set_show(self, value, display=True, refresh="a"):
            if value != self.show:
                self.show = value
                if value:
                    self.touch_records = [self.clicked]
                else:
                    self.touch_records = []
                self.page.update(display, refresh)

        def set_func(self, func):
            self.touch_records[0].func = func

        def update(self, display=True, refresh="a"):
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            self._image_draw.text((self.border[0], self.border[1]), self.text, self.color, self._font)
            self.page.update(display, refresh)

    class LabelButton(Label):
        def __init__(self, page, size, func=lambda: None, location=(0, 0), border=(0, 0), text="",
                     font_size=12, color="black", border_color="black", border_width=0, background=None, show=True,
                     align="C"):
            self.border_color = border_color
            self.border_width = border_width
            self.func = func
            super().__init__(page, location, size, border, text, font_size, color, background, show, align)
            self.clicked = _Clicked((location[0], location[0] + size[0], location[1], location[1] + size[1]),
                                    self.func)
            if show:
                self.touch_records = [self.clicked]

        def set_show(self, value, display=True, refresh="a"):
            if value != self.show:
                self.show = value
                if value:
                    self.touch_records = [self.clicked]
                else:
                    self.touch_records = []
                self.page.update(display, refresh)

        def update(self, display=True, refresh="a"):
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            font_size = self._font.size
            if self.align == "L":
                x = self.border[0]
            else:
                length = 0
                if font_size % 12 == 0:
                    add = font_size * 2 / 3
                else:
                    add = font_size / 2
                for i in self.text:
                    if " " <= i <= "~":
                        length += add
                    else:
                        length += font_size
                if self.align == "C":
                    x = _ceil((self.size[0] - length) / 2)
                elif self.align == "R":
                    x = self.size[0] - 2 * self.border[0] - length
                else:
                    raise ValueError

            self._image_draw.text((x, _floor((self.size[1] - font_size) / 2)), self.text, self.color, self._font)

            if self.border_width:
                self._image_draw.rectangle((0, 0, self.size[0], self.size[1]),
                                           outline=self.border_color, width=self.border_width)

            self.page.update(display, refresh)

        def set_func(self, func):
            self.touch_records[0].func = func

    class MultipleLinesText(Label):
        def __init__(self, page, location, size, text="", border=(0, 0), font_size=12, color="black", background=None,
                     space=0, show=True):
            self.space = space
            super().__init__(page, location, size, border, text, font_size, color, background=background, show=show)

        def set_text(self, value, display=True, refresh="a"):
            self.text = value
            self.update(display, refresh)

        def update(self, display=True, refresh="a"):
            text = self.text.split("\n")
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
                length = add
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
            self.page.update(display, refresh)

    # 实现一个多页文本element
    class MultiplePagesText(MultipleLinesText):
        def __init__(self, page, location, size, text="", border=(0, 0), font_size=12, color="black", background=None,
                     space=0, show=True, guide_line_width=2, slide=True):
            self.font_size = font_size
            self.at = 0
            self.slide = slide
            self.content = self.text_split(text, (size[0] - 2 * border[0], size[1] - 2 * border[1]), font_size)
            self.guide_line_height = max(10, _ceil(size[1] / len(self.content)))
            self.guide_line_width = guide_line_width
            super().__init__(page, location, size, text, border, font_size, color, background, space, show)

            self.records = [_SlideY((self.location[0], self.location[0]+self.size[0],
                                     self.location[1], self.location[1]+self.size[1]),
                                    self._handler)]
            if self.show and self.slide:
                self.touch_records = self.records
            else:
                self.touch_records = []

        def _handler(self, dis_y):
            if dis_y < 0:
                self.at = min(self.at + 1, len(self.content) - 1)
            else:
                self.at = max(self.at - 1, 0)
            self.update()

        @property
        def page_num(self):
            return len(self.content)

        @staticmethod
        def text_split(text, area_size, font_size) -> list:
            if font_size % 12 == 0:
                add = font_size * 2 / 3
            else:
                add = font_size / 2

            length = add
            height = font_size

            result = []

            start = 0
            cur_text = ""
            last_line = ""
            for t in range(len(text)):
                character = text[t]

                if character == "\n":
                    length = add
                    last_line = text[start: t] + "\n"
                    start = t + 1
                    cur_text += last_line
                    height += font_size
                elif " " <= character <= "~":
                    length += add
                else:
                    length += font_size

                if length > area_size[0]:
                    length = add
                    last_line = text[start: t] + "\n"
                    start = t
                    cur_text += last_line
                    height += font_size
                if height > area_size[1]:
                    height = font_size
                    length = add
                    result.append(cur_text)
                    cur_text = last_line
                    last_line = ""
            cur_text += text[start:]
            result.append(cur_text)
            height += font_size
            if height > area_size[1]:
                result.append(last_line)
            return result

        def set_text(self, value, display=True, refresh="a"):
            self.text = value
            self.content = self.text_split(value, (self.size[0] - 2 * self.border[0], self.size[1] - 2 * self.border[1])
                                           , self.font_size)
            self.guide_line_height = max(10, _ceil(self.size[1] / len(self.content)))
            self.at = 0
            self.update(display, refresh)

        def update(self, display=True, refresh="a"):
            self.image = self.background.copy()
            self._image_draw = _ImageDraw.ImageDraw(self.image)
            self._image_draw.text(self.border, self.content[self.at], self.color, self._font, space=self.space)
            if len(self.content) > 1:
                y = (self.size[1] - self.guide_line_height)*self.at/len(self.content)
                self._image_draw.line((self.size[0], y, self.size[0], y+self.guide_line_height), self.color,
                                      width=self.guide_line_width)
            self.page.update(display, refresh)

        def next_page(self, display=True, refresh="a"):
            if self.at + 1 < len(self.content):
                self.at += 1
                self.update(display, refresh)

        def previous_page(self, display=True, refresh="a"):
            if self.at > 0:
                self.at -= 1
                self.update(display, refresh)

        def go_to_page(self, page, display=True, refresh="a"):
            if page < len(self.content):
                self.at = page
                self.update(display, refresh)

        def set_show(self, value, display=True, refresh="a"):
            if value != self.show:
                self.show = value
                if value and self.slide:
                    self.touch_records = self.records
                else:
                    self.touch_records = []
                self.page.update(display, refresh)


class Pages:
    class ListPage(_Page):
        def __init__(self, book, title, items: [str], icons=None, styles=None, funcs=None, func=None):
            super().__init__(book)
            self.env = book.base.env
            self.styles_img = {
                "OK": [self.env.ok_img, self.env.ok_alpha, 253, -2],
                "ON": [self.env.on_img, self.env.on_alpha, 242, 0],
                "OFF": [self.env.off_img, self.env.off_alpha, 242, 0],
                "NEXT": [self.env.next_img, self.env.next_alpha, 266, -2]
            }
            self._background = book.base.env.list_img
            self.more_img = book.base.env.list_more_img
            self.old_render = self.background
            self.title = title
            self.items = items
            self.font = book.base.env.get_font(16)
            self.icons = icons if icons else [None] * len(items)
            self.funcs = funcs if funcs else [lambda: None] * len(items)
            self.styles = styles if styles else [None] * len(items)
            self.func = func
            self.at = 0
            if not len(items) == len(self.icons) == len(self.funcs):
                raise ValueError("Quantity asymmetry!")
            self.list_clicked = [
                _Clicked((0, 296, 31, 60), self._handler, 0),
                _Clicked((0, 296, 61, 90), self._handler, 1),
                _Clicked((0, 296, 91, 120), self._handler, 2),
            ]
            self.list_slide_y = [
                _SlideY((0, 296, 0, 128), self._slide)
            ]
            self.create_touch_record()

        def create_touch_record(self):
            self.touch_records_rlock.acquire()
            self.touch_records_clicked = self.list_clicked.copy()
            self.touch_records_slide_x = []
            self.touch_records_slide_y = self.list_slide_y.copy()
            for i in self._elements:
                for j in i.touch_records:
                    if isinstance(j, _Clicked):
                        self.touch_records_clicked.append(j)
                    elif isinstance(j, _SlideX):
                        self.touch_records_slide_x.append(j)
                    elif isinstance(j, _SlideY):
                        self.touch_records_slide_y.append(j)
            for j in self._touch_records:
                if isinstance(j, _Clicked):
                    self.touch_records_clicked.append(j)
                elif isinstance(j, _SlideX):
                    self.touch_records_slide_x.append(j)
                elif isinstance(j, _SlideY):
                    self.touch_records_slide_y.append(j)
            self.touch_records_rlock.release()

        def set_style(self, index, style=None, display=True):
            if self.styles[index] != style:
                self.styles[index] = style
                if index // 3 == self.at:
                    self.update(display)

        def append(self, item, icon=None, func=lambda: None, style=None, display=True):
            self.items.append(item)
            self.icons.append(icon)
            self.funcs.append(func)
            self.styles.append(style)
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
            index_ = self.at * 3 + index
            if index_ >= len(self.items):
                return
            if self.func:
                self.func(index_)
            else:
                self.funcs[index_]()

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
                for i in range(1, 3):
                    self.list_clicked[i].vibrate = True
                self.update(display)

        def go_to(self, index=0, display=True):
            self.at = index
            self._update = True
            self.update(display)

        def render(self):
            if self._update:
                new_image = self.background.copy()
                draw = _ImageDraw.ImageDraw(new_image)
                draw.text((10, 7), self.title, "black", self.font)
                draw.text((256, 8), f"{self.at + 1}/{_ceil(len(self.items) / 3)}", "black", self.font)
                for i in range(3):
                    index = self.at * 3 + i
                    if index + 1 > len(self.items):
                        # 处理震动
                        for j in range(i, 3):
                            self.list_clicked[j].vibrate = False
                        break
                    y = 37 + i * 30
                    if self.icons[index]:
                        new_image.paste(self.icons[index], (8, y))
                        draw.text((35, y + 2), self.items[index], "black", self.font)
                    else:
                        draw.text((8, y + 2), self.items[index], "black", self.font)
                    if self.styles[index]:
                        img = self.styles_img[self.styles[index]]
                        new_image.paste(img[0], (img[-2], y + img[-1]), mask=img[1])
                if self.at * 3 + 3 < len(self.items):
                    new_image.paste(self.more_img, (105, 122))

                self._elements_rlock.acquire()
                for i in self._elements:
                    j = i.render()
                    if j:
                        if j.mode == "RGBA":
                            _, _, _, a = j.split()
                            new_image.paste(j, i.location, mask=a)
                        else:
                            new_image.paste(j, i.location)
                self._elements_rlock.release()

                self.old_render = new_image
                self._update = False
                return new_image.copy()
            else:
                return self.old_render.copy()

    class PageWithTitle(_Page):
        def __init__(self, book, title):
            super().__init__(book)
            self._background = book.base.env.page_with_title_img

            self.title = Elements.TextElement(self, (7, 7), title, font_size=16)
            self.add_element(self.title)


class ThemeBaseWithoutDocker(_Base):
    def __init__(self, env):
        super().__init__(env)
        self.show_in_settings = True

    @property
    def preview(self):
        return self.Book.render()


class ThemeBase(_Base):
    def __init__(self, env):
        super().__init__(env)
        self.show_in_settings = True
        self._docker_image = self.env.docker_img
        self._docker_status = False
        self._docker_temp = 0

        self._inactive_records = [_SlideY((0, 296, 0, 30), self.active_docker, limit="+")]
        self._active_records = [_Clicked((60, 100, 0, 30), self.open_applist),
                                _Clicked((0, 296, 30, 128), self.close_docker),
                                _Clicked((195, 235, 0, 30), self.open_setting),
                                _Clicked((112, 142, 0, 30), self.open_app, 0),
                                _Clicked((142, 172, 0, 30), self.open_app, 1),
                                _Clicked((172, 202, 0, 30), self.open_app, 2),
                                ]

        self.docker_list = []

    @property
    def preview(self):
        return self.Book.render()

    def open_app(self, index):
        try:
            self.env.open_app(self.docker_list[index])
        except IndexError:
            pass

    def active(self, refresh="a"):
        self._docker_status = False

        self.docker_list = self.env.Config.read("docker")
        flag = False
        for i in self.docker_list.copy():
            if i not in self.env.apps:
                self.docker_list.remove(i)
                flag = True
        if flag:
            self.env.Config.set("docker", self.docker_list)

        super().active(refresh)

    def open_applist(self):
        self.env.open_app("应用抽屉")

    def open_setting(self):
        self.env.open_app("设置")

    def active_docker(self, _):
        self._docker_status = True
        self.display()
        self._docker_temp = _time.time()
        _time.sleep(2)
        if _time.time() - self._docker_temp >= 2:
            self._docker_status = False
            self.display()

    def close_docker(self):
        self._docker_status = False
        self.display()

    def render(self) -> _Image:
        if self._docker_status:
            new_image = self.Book.render()
            new_image.paste(self._docker_image, (60, 0))
            x = 112
            for i in self.docker_list:
                new_image.paste(self.env.apps[i].icon, (x, 5))
                x += 30
            return new_image
        else:
            return self.Book.render()

    @property
    def touch_records_clicked(self):
        if self._docker_status:
            return self.Book.Page.touch_records_clicked + self._active_records
        else:
            return self.Book.Page.touch_records_clicked

    @property
    def touch_records_slide_y(self):
        if self._docker_status:
            return self.Book.Page.touch_records_slide_y
        else:
            return self.Book.Page.touch_records_slide_y + self._inactive_records


class AppBase(_Base):
    def __init__(self, env):
        self.show_in_drawer = True
        self.title = ""
        self.icon = env.none18px_img
        self.name = ""

        super().__init__(env)

        self._control_bar_font = self.env.get_font(16)
        self._control_bar_image = env.app_control_img
        self._control_bar_mask = env.app_control_alpha
        self._control_bar_status = False
        self._control_bar_temp = 0
        self._inactive_records = [_SlideY((0, 296, 0, 20), self.active_control_bar, limit="+")]
        self._active_records = [_Clicked((266, 296, 0, 30), self.env.back_home),
                                _Clicked((0, 296, 30, 128), self.close_control_bar),
                                _Clicked((112, 142, 0, 30), self.open_app, 0),
                                _Clicked((142, 172, 0, 30), self.open_app, 1),
                                _Clicked((172, 202, 0, 30), self.open_app, 2),
                                ]

        self.docker_list = []

    def open_app(self, index):
        try:
            self.env.open_app(self.docker_list[index])
        except IndexError:
            pass

    def active(self, refresh="a"):
        self._control_bar_status = False
        self.docker_list = self.env.Config.read("docker")
        flag = False
        for i in self.docker_list.copy():
            if i not in self.env.apps:
                self.docker_list.remove(i)
                flag = True
        if flag:
            self.env.Config.set("docker", self.docker_list)
        super().active(refresh)

    def render(self):
        if self._control_bar_status:
            new_image = self.Book.render()
            new_image.paste(self._control_bar_image, (0, 0), mask=self._control_bar_mask)
            new_image.paste(self.icon, (6, 6))
            image_draw = _ImageDraw.ImageDraw(new_image)
            title = f"{self.title[:5]}..." if len(self.title) > 4 and self.docker_list else self.title
            image_draw.text((30, 7), title, fill="black", font=self._control_bar_font)
            image_draw.text((224, 7), _time.strftime("%H:%M", _time.localtime()), fill="black",
                            font=self._control_bar_font)

            x = 112
            for i in self.docker_list:
                new_image.paste(self.env.apps[i].icon, (x, 5))
                x += 30

            return new_image
        else:
            return self.Book.render()

    def active_control_bar(self, _):
        self._control_bar_temp = _time.time()
        self._control_bar_status = True
        self.display()
        _time.sleep(8)
        if _time.time() - self._control_bar_status >= 8:
            self._control_bar_status = False
            self.display()

    def close_control_bar(self):
        self._control_bar_status = False
        self.display()

    @property
    def touch_records_clicked(self):
        if self._control_bar_status:
            return self.Book.Page.touch_records_clicked + self._active_records
        else:
            return self.Book.Page.touch_records_clicked

    @property
    def touch_records_slide_y(self):
        if self._control_bar_status:
            return self.Book.Page.touch_records_slide_y
        else:
            return self.Book.Page.touch_records_slide_y + self._inactive_records
