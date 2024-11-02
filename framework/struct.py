import abc
import threading
from queue import LifoQueue

from PIL import Image

from enviroment.touchscreen import Clicked, SlideX, SlideY


class Element:
    def __init__(self, page, location=(0, 0)):
        self.location = location
        self.page = page
        self._layer = 0
        # self._update = False
        # self.last_render = self.background
        self._touch_records = []

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        self._layer = value
        self.page.resort()

    @property
    def touch_records(self):
        return self._touch_records

    @touch_records.setter
    def touch_records(self, value):
        self._touch_records = value
        self.page.create_touch_record()

    @abc.abstractmethod
    def render(self) -> Image:
        return None


class Page:
    def __init__(self, book):
        self.book = book
        self.elements = []
        self.touch_records_clicked = []
        self.touch_records_slide_x = []
        self.touch_records_slide_y = []
        self.background = Image.new("RGB", (296, 128), (255, 255, 255))
        self.elements_rlock = threading.RLock()
        self.touch_records_rlock = threading.RLock()
        self.old_render = self.background
        self._update = True

    @staticmethod
    def _get_sort_key_from(element: Element) -> int:
        return element.layer

    def add_element(self, element: Element):
        self.elements_rlock.acquire()
        self.elements.append(element)
        self.resort()
        self.elements_rlock.release()

    def resort(self):
        self.elements_rlock.acquire()
        self.elements.sort(key=self._get_sort_key_from, reverse=True)
        self.elements_rlock.release()
        self.create_touch_record()

    def create_touch_record(self):
        self.touch_records_rlock.acquire()
        self.touch_records_clicked = []
        self.touch_records_slide_x = []
        self.touch_records_slide_y = []
        for i in self.elements:
            for j in i.touch_records:
                if isinstance(j, Clicked):
                    self.touch_records_clicked.append(j)
                elif isinstance(j, SlideX):
                    self.touch_records_slide_x.append(j)
                elif isinstance(j, SlideY):
                    self.touch_records_slide_y.append(j)
        self.touch_records_rlock.release()

    def render(self):
        if self._update:
            new_image = self.background.copy()
            self.elements_rlock.acquire()
            for i in self.elements:
                j = i.render()
                if j:
                    if j.mode == "RGBA":
                        _, _, _, a = j.split()
                        new_image.paste(j, i.location, mask=a)
                    else:
                        new_image.paste(j, i.location)
            self.elements_rlock.release()
            self.old_render = new_image
            self._update = False
            return new_image.copy()
        else:
            return self.old_render.copy()

    def update(self):
        self._update = True
        self.book.update(self)


class Book:
    def __init__(self, app):
        self.app = app
        self.Pages = {}
        self.Page = None
        self.now_page = ""
        self.is_active = False

        self.back_stack = LifoQueue()

    def change_page(self, target: str, to_stack=True):
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
            self.app.display()
        else:
            raise KeyError("The targeted page is not found.")

    def render(self) -> Image:
        return self.Pages[self.now_page].render()

    def update(self, page):
        if page is self.Pages[self.now_page] and self.is_active:
            self.app.display()

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
        self.now_book = ""
        self.display_lock = threading.Lock()
        self._active = False

        self.back_stack = LifoQueue()

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

    def change_book(self, target: str, to_stacks=True):
        if target in self.Books:
            if to_stacks:
                self.back_stack.put(self.now_book)
            self.Book.is_active = False
            self.now_book = target
            self.Book = self.Books[target]
            self.Book.is_active = True
        else:
            raise KeyError("The targeted book is not found.")

    def display(self) -> None:
        if self._active:
            self.env.display_auto()

    def active(self) -> None:  # This function will be called when this Base is active. But not first started.
        self._active = True
        self.Book.is_active = True
        self.display()

    def pause(self) -> None:  # This function will be called when this Base is paused.
        self._active = False
        self.Book.is_active = False

    def launch(self) -> None:  # This function will be called when the eInkUI is launch.
        self._active = False
        self.Book.is_active = False

    def shutdown(self) -> None:  # This function will be called when the eInkUI is shutdown.
        # Technically this function should be done within 1s
        self._active = False
        self.Book.is_active = False

    def back(self) -> bool:
        if self.Book.back:
            return True
        else:
            if self.back_stack.empty():
                return False
            else:
                i = self.back_stack.get()
                if callable(i):
                    i()
                    return True
                elif isinstance(i, str):
                    self.change_book(i)
                    return True
                else:
                    return False

    def add_back(self, item):
        self.back_stack.put(item)


class Plugin:
    def __init__(self, env):
        self.env = env

    def launch(self) -> None:  # This function will be called when the eInkUI is launch.
        pass

    def shutdown(self) -> None:  # This function will be called when the eInkUI is shutdown.
        # Technically this function should be done in 5s
        pass
