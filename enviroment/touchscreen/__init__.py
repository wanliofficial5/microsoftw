import threading as _threading
import time
import time as _time

from enviroment.touchscreen.events import Clicked, Slide, SlideY, SlideB


class _ReIter:  # 反向迭代器
    def __init__(self, content):
        self.content = content
        self.index = None

    def __iter__(self):
        self.index = len(self.content)
        return self

    def __next__(self):
        if self.index <= 0:
            self.index = len(self.content)
            raise StopIteration
        else:
            self.index -= 1
            return self.content[self.index]


class TouchRecoder:
    def __init__(self):
        self.Touch = 0
        self.TouchGestureId = 0
        self.TouchCount = 0

        self.TouchEvenId = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.P = [0, 1, 2, 3, 4]


class TouchHandler:
    def __init__(self, env):
        self.env = env
        self.pool = env.Pool
        self.taptic = env.Taptic
        self.clicked = []
        self.slide_x = []
        self.slide_y = []
        self.data_lock = _threading.Lock()

        self.back_left = SlideB()
        self.back_right = SlideB()
        self.home_bar = SlideY()

        self.double_clicked_flag = 0

    def set_clicked(self, content):
        self.data_lock.acquire()
        self.clicked = content
        self.data_lock.release()

    def add_clicked(self, clicked: Clicked):
        self.data_lock.acquire()
        self.clicked.append(clicked)
        self.data_lock.release()

    def set_slide_x(self, content):
        self.data_lock.acquire()
        self.slide_x = content
        self.data_lock.release()

    def add_slide_x(self, slide: Slide):
        self.data_lock.acquire()
        self.slide_x.append(slide)
        self.data_lock.release()

    def set_slide_y(self, content):
        self.data_lock.acquire()
        self.slide_y = content
        self.data_lock.release()

    def add_slide_y(self, slide: Slide):
        self.data_lock.acquire()
        self.slide_y.append(slide)
        self.data_lock.release()

    def remove_clicked(self, clicked: Clicked):
        self.data_lock.acquire()
        self.clicked.remove(clicked)
        self.data_lock.release()

    def remove_slide_x(self, slide: Slide):
        self.data_lock.acquire()
        self.slide_x.remove(slide)
        self.data_lock.release()

    def remove_slide_y(self, slide: Slide):
        self.data_lock.acquire()
        self.slide_y.remove(slide)
        self.data_lock.release()

    def clear_clicked(self):
        self.data_lock.acquire()
        self.clicked = []
        self.data_lock.release()

    def clear_slide_x(self):
        self.data_lock.acquire()
        self.slide_x = []
        self.data_lock.release()

    def clear_slide_y(self):
        self.data_lock.acquire()
        self.slide_y = []
        self.data_lock.release()

    def handle(self, ICNT_Dev: TouchRecoder, ICNT_Old: TouchRecoder):
        self.env.Now.Book.Page.touch_records_rlock.acquire()
        self.data_lock.acquire()
        d_t = ICNT_Dev.Touch
        o_t = ICNT_Old.Touch
        d_x = ICNT_Dev.X[0]
        d_y = ICNT_Dev.Y[0]
        app_slide_x = self.env.Now.touch_records_slide_x
        app_slide_y = self.env.Now.touch_records_slide_y
        app_clicked = self.env.Now.touch_records_clicked

        if self.env.screen_reversed:
            d_x = 296 - d_x
            d_y = 128 - d_y

        if d_t and not o_t:  # Start touching
            print(f"Start Touch: [{d_x}, {d_y}]")
            if d_x <= 20:
                self.back_left.temp_location = (d_x, d_y)
            elif d_x >= 276:
                self.back_right.temp_location = (d_x, d_y)
            elif d_y >= 108 and 100 <= d_x <= 200:
                self.home_bar.temp_location = (d_x, d_y)

            for i in _ReIter(app_slide_x):
                if i.area[0] <= d_x <= i.area[1] and i.area[2] <= d_y <= i.area[3]:
                    i.temp_location = (d_x, d_y)
            for i in _ReIter(app_slide_y):
                if i.area[0] <= d_x <= i.area[1] and i.area[2] <= d_y <= i.area[3]:
                    i.temp_location = (d_x, d_y)
            for i in _ReIter(self.clicked):
                if i.area[0] <= d_x <= i.area[1] and i.area[2] <= d_y <= i.area[3]:
                    i.temp_location = (d_x, d_y)
            for i in _ReIter(app_clicked):
                if i.area[0] <= d_x <= i.area[1] and i.area[2] <= d_y <= i.area[3]:
                    i.temp_location = (d_x, d_y)

        elif not d_t and o_t:  # Stop touching
            if time.time() - self.double_clicked_flag < 0.4:
                self.pool.add(self.env.display, refresh="t")
                self.env.feedback_vibrate_async()
                self.double_clicked_flag = 0

                self.env.show_left_back = False
                self.back_left.active = False
                self.env.show_right_back = False
                self.back_right.active = False
                self.home_bar.active = False
                for i in self.clicked:
                    i.active = False
                for i in self.slide_x:
                    i.active = False
                for i in self.slide_y:
                    i.active = False
                for i in app_clicked:
                    i.active = False
                for i in app_slide_x:
                    i.active = False
                for i in app_slide_y:
                    i.active = False
                self.env.Now.Book.Page.touch_records_rlock.release()
                self.data_lock.release()
                return
            print(f"Stop Touch: [{d_x}, {d_y}]")
            slided = False
            if self.back_left.active:
                if d_x - self.back_left.temp_location[0] > 20:
                    self.pool.add(self.env.back)
                    self.env.feedback_vibrate_async()
                    slided = True
                elif self.back_left.showed:
                    self.pool.add(self.env.back_left, False)
                self.back_left.active = False
            elif self.back_right.active:
                if self.back_right.temp_location[0] - d_x > 20:
                    self.pool.add(self.env.back)
                    self.env.feedback_vibrate_async()
                    slided = True
                elif self.back_right.showed:
                    self.pool.add(self.env.back_right, False)
                self.back_right.active = False
            elif self.home_bar.active:
                if self.home_bar.temp_location[1] - d_y > 20 and 100 <= d_x <= 200:
                    self.pool.add(self.env.home_bar)
                    slided = True
                self.home_bar.active = False
            if slided:
                for i in app_slide_y:
                    i.active = False
                for i in app_slide_x:
                    i.active = False
            else:
                for i in _ReIter(app_slide_y):
                    if i.active:
                        i.active = False
                        dis_y = d_y - i.temp_location[1]
                        if i.limit == "+" and dis_y <= 0:
                            continue
                        elif i.limit == "-" and dis_y >= 0:
                            continue
                        dis_x = d_x - i.temp_location[0]
                        if abs(dis_y) > 20 and abs(dis_x * 10 // dis_y) <= 5:
                            self.pool.add(i.func, dis_y)
                            slided = True

                for i in _ReIter(app_slide_x):
                    if i.active:
                        i.active = False
                        dis_x = d_x - i.temp_location[0]
                        if i.limit == "+" and dis_x <= 0:
                            continue
                        elif i.limit == "-" and dis_x >= 0:
                            continue
                        dis_y = d_y - i.temp_location[1]
                        if abs(dis_x) > 20 and abs(dis_y * 10 // dis_x) <= 5:
                            self.pool.add(i.func, dis_x)
                            slided = True

            if slided:
                for i in app_clicked:
                    i.active = False
                for i in self.clicked:
                    i.active = False
            else:
                for i in _ReIter(self.clicked):
                    if i.active:
                        i.active = False
                        if i.area[0] <= d_x <= i.area[1] and i.area[2] <= d_y <= i.area[3]:
                            self.pool.add(i.func, *i.args, **i.kwargs)
                            if i.vibrate:
                                self.env.feedback_vibrate_async()
                            break
                else:
                    for i in _ReIter(app_clicked):
                        if i.active:
                            i.active = False
                            if i.area[0] <= d_x <= i.area[1] and i.area[2] <= d_y <= i.area[3]:
                                self.pool.add(i.func, *i.args, **i.kwargs)
                                if i.vibrate:
                                    self.env.feedback_vibrate_async()
                                break

        elif d_t and o_t:  # Keep touching
            if ICNT_Dev.TouchCount >= 2:
                self.double_clicked_flag = _time.time()

            if not (ICNT_Dev.X[0] == ICNT_Old.X[0] and ICNT_Dev.Y[0] == ICNT_Old.Y[0]):
                if self.back_left.active and not self.back_left.showed:
                    if d_x - self.back_left.temp_location[0] >= 20:
                        self.pool.add(self.env.back_left, True)
                        self.back_left.showed = True
                elif self.back_right.active and not self.back_right.showed:
                    if self.back_right.temp_location[0] - d_x >= 20:
                        self.pool.add(self.env.back_right, True)
                        self.back_right.showed = True

        self.env.Now.Book.Page.touch_records_rlock.release()
        self.data_lock.release()
