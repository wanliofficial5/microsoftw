import abc as _abc
import threading as _threading
from queue import LifoQueue as _LifoQueue

from PIL import Image as _Image

from enviroment.touchscreen.events import Clicked as _Clicked, \
    SlideY as _SlideY
from enviroment.touchscreen.events import SlideX as _SlideX


class Element:
    def __init__(self, page, location=(0, 0), position="", layout=""):
        self.page = page
        self._location = location
        self._position = position
        self._layout = layout
        self._layer = 0
        self._touch_records = []

    @property
    def layer(self):
        return self._layer

    def set_layer(self, value, update=True):
        self._layer = value
        self.page.resort()
        self.page.update(update)

    @property
    def location(self):
        return self._location

    def set_location(self, value, update=True):
        self._location = value
        self.page.update(update)

    @property
    def position(self):
        return self._location

    def set_position(self, value, update=True):
        self._position = value
        self.page.update(update)

    @property
    def layout(self):
        return self._layer

    def set_layout(self, value, update=True):
        self._layout = value
        self.page.update(update)

    @property
    def touch_records(self):
        return self._touch_records

    @touch_records.setter
    def touch_records(self, value):
        self._touch_records = value
        self.page.create_touch_record()

    @_abc.abstractmethod
    def render(self) -> _Image:
        return None


class Page:
    def __init__(self, book):
        self.book = book
        self._elements = []
        self.touch_records_clicked = []
        self.touch_records_slide_x = []
        self.touch_records_slide_y = []
        self._background = _Image.new("RGB", (296, 128), (255, 255, 255))
        self._elements_rlock = _threading.RLock()
        self.touch_records_rlock = _threading.RLock()
        self.old_render = self._background
        self._update = True
        self._touch_records = []

    @property
    def background(self):
        return self._background

    def set_background(self, value, display=True):
        self._background = value
        self.update(display)

    @property
    def touch_records(self):
        return self._touch_records

    @touch_records.setter
    def touch_records(self, value):
        self._touch_records = value
        self.create_touch_record()

    def touch_records_append(self, value):
        self._touch_records.append(value)
        self.create_touch_record()

    def touch_records_clear(self):
        self._touch_records = []
        self.create_touch_record()

    def touch_records_remove(self, value):
        self._touch_records.remove(value)
        self.create_touch_record()

    @staticmethod
    def _get_sort_key_from(element: Element) -> int:
        return element.layer

    def add_element(self, element: Element):
        self._elements_rlock.acquire()
        self._elements.append(element)
        self.resort()
        self._elements_rlock.release()
        self._update = True

    def resort(self):
        self._elements_rlock.acquire()
        self._elements.sort(key=self._get_sort_key_from, reverse=True)
        self._elements_rlock.release()
        self.create_touch_record()

    def create_touch_record(self):
        self.touch_records_rlock.acquire()
        self.touch_records_clicked = []
        self.touch_records_slide_x = []
        self.touch_records_slide_y = []
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

    def render(self):
        if self._update:
            new_image = self._background.copy()
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

    def update(self, display=True):
        self._update = True
        if display:
            self.book.update(self)


class Book:
    def __init__(self, base):
        self.base = base
        self.Pages = {}
        self.Page = None
        self.now_page = ""
        self.is_active = False

        self.back_stack = _LifoQueue()

    def add_page(self, name, page, as_default=True):
        self.Pages[name] = page
        if as_default:
            self.now_page = name
            self.Page = page

    def change_page(self, target: str, to_stack=True, display=True):
        if target in self.Pages:
            if to_stack:
                self.back_stack.put(self.now_page)
            self.Page.touch_records_rlock.acquire()
            for i in self.Page.touch_records_clicked:
                i.active = False
            for i in self.Page.touch_records_slide_y:
                i.active = False
            for i in self.Page.touch_records_slide_x:
                i.active = False
            self.Page.touch_records_rlock.release()
            self.now_page = target
            self.Page = self.Pages[target]
            if display:
                self.base.display()
        else:
            raise KeyError("The targeted page is not found.")

    def render(self) -> _Image:
        return self.Page.render()

    def update(self, page):
        if page is self.Pages[self.now_page] and self.is_active:
            self.base.display()

    def back(self) -> bool:
        if self.back_stack.empty():
            return False
        else:
            i = self.back_stack.get()
            if callable(i):
                i()
                return True
            elif isinstance(i, str):
                self.change_page(i, False)
                return True
            else:
                return False

    def add_back(self, item):
        self.back_stack.put(item)


class Base:
    def __init__(self, env):
        self.env = env
        self.name = ""
        self.Books = {}
        self.Book = None
        self._now_book = ""
        self.display_lock = _threading.Lock()
        self._active = False

        self.back_stack = _LifoQueue()

    @property
    def now_book(self):
        return self._now_book

    @now_book.setter
    def now_book(self, value):
        self.change_book(value, to_stacks=False)

    def add_book(self, name, book, as_default=True):
        self.Books[name] = book
        if as_default:
            self._now_book = name
            self.Book = book

    @property
    def touch_records_slide_x(self):
        return self.Book.Page.touch_records_slide_x

    @property
    def touch_records_slide_y(self):
        return self.Book.Page.touch_records_slide_y

    @property
    def touch_records_clicked(self):
        return self.Book.Page.touch_records_clicked

    def is_active(self):
        return self._active

    def change_book(self, target: str, display=True, to_stacks=True):
        if target in self.Books:
            if to_stacks:
                self.back_stack.put(self.now_book)
            self.Book.is_active = False
            self._now_book = target
            self.Book = self.Books[target]
            self.Book.is_active = True
            if display:
                self.display()
        else:
            raise KeyError("The targeted book is not found.")

    def display(self, refresh="a") -> None:
        if self._active:
            self.env.display(self.Book.render(), refresh)

    def active(self, refresh="a") -> None:  # This function will be called when this Base is active.
        self._active = True
        self.Book.is_active = True
        self.display(refresh)

    def pause(self) -> None:  # This function will be called when this Base is paused.
        self._active = False
        self.Book.is_active = False

    def shutdown(self) -> None:  # This function will be called when the eInkUI is shutdown.
        # Technically this function should be done within 1s
        self._active = False
        self.Book.is_active = False

    def back(self) -> bool:
        self.env._show_left_back = False
        self.env._show_right_back = False
        if self.back_stack.empty():
            return self.Book.back()
        else:
            i = self.back_stack.get()
            if callable(i):
                i()
                return True
            elif isinstance(i, str):
                if self.Book.back():
                    self.back_stack.put(i)
                else:
                    self.change_book(i, to_stacks=False)
                return True
            else:
                return False

    def add_back(self, item):
        self.back_stack.put(item)


class PluginBase:
    def __init__(self, env):
        self.env = env

    def shutdown(self) -> None:  # This function will be called when the eInkUI is shutdown.
        # Technically this function should be done in 5s
        pass
