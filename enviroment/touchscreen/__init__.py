import threading


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


class Clicked:  # call the function when the object is clicked.
    def __init__(self, area=(0, 0, 0, 0), func=lambda: None, *arg, **kwargs):
        self.area = area
        self._temp_location = (0, 0)
        self.func = func
        self.active = False
        self.args = arg
        self.kwargs = kwargs

    @property
    def temp_location(self):
        return self._temp_location

    @temp_location.setter
    def temp_location(self, value):
        self._temp_location = value
        self.active = True


class Slide:
    def __init__(self):
        self.area = (0, 0, 0, 0)  # (x1, x2, y1, y2)
        self._temp_location = (0, 0)
        self.active = False
        self.func = None

    @property
    def temp_location(self):
        return self._temp_location

    @temp_location.setter
    def temp_location(self, value):
        self._temp_location = value
        self.active = True


class SlideX(Slide):
    pass


class SlideY(Slide):
    pass


class SlideB(Slide):
    def __init__(self):
        super().__init__()
        self._active = False
        self.showed = False

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        if not value:
            self.showed = False
        self._active = value


class TouchHandler:
    def __init__(self, env):
        self.env = env
        self.pool = env.Pool
        self.clicked = []
        self.slide_x = []
        self.slide_y = []
        self.data_lock = threading.Lock()

        self.back_left = SlideB()
        self.back_right = SlideB()
        self.home_bar = SlideY()

    def add_clicked(self, clicked: Clicked):
        self.data_lock.acquire()
        self.clicked.append(clicked)
        self.data_lock.release()

    def add_slide_x(self, slide: Slide):
        self.data_lock.acquire()
        self.slide_x.append(slide)
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
        o_x = ICNT_Old.X[0]
        o_y = ICNT_Old.Y[0]
        app_slide_x = self.env.Now.touch_records_slide_x
        app_slide_y = self.env.Now.touch_records_slide_y
        app_clicked = self.env.Now.touch_records_clicked

        if d_t and not o_t:  # Start touching
            if ICNT_Dev.X[0] <= 20:
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
            slided = False
            if self.back_left.active:
                if d_x - self.back_left.temp_location[0] > 20:
                    self.pool.add(self.env.back)
                    slided = True
                self.pool.add(self.env.back_left, False)
                self.back_left.active = False
            elif self.back_right.active:
                if self.back_right.temp_location[0] - d_x > 20:
                    self.pool.add(self.env.back)
                    slided = True
                self.pool.add(self.env.back_right, False)
                self.back_left.active = False
            elif self.home_bar.active:
                if self.home_bar.temp_location[1] - d_y > 20 and 100 <= d_x <= 200:
                    self.pool.add(self.env.home_bar)
            if not slided:
                for i in _ReIter(app_slide_y):
                    if i.active:
                        dis_x = d_x - i.temp_location[0]
                        dis_y = d_y - i.temp_location[1]
                        if abs(dis_y) > 20 and abs(dis_x * 10 // dis_y) <= 5:
                            self.pool.add(i.func, dis_x)
                            slided = True
                        i.active = False
                for i in _ReIter(app_slide_x):
                    if i.active:
                        dis_x = d_x - i.temp_location[0]
                        dis_y = d_y - i.temp_location[1]
                        if abs(dis_x) > 20 and abs(dis_y * 10 // dis_x) <= 5:
                            self.pool.add(i.func, dis_x)
                            slided = True
                        i.active = False

            if slided:
                for i in app_clicked:
                    i.active = False
                for i in self.clicked:
                    i.active = False
            else:
                for i in _ReIter(self.clicked):
                    if i.active:
                        self.pool.add(i.func, *i.args, **i.kwargs)
                        i.active = False
                for i in _ReIter(app_clicked):
                    if i.active:
                        self.pool.add(i.func, *i.args, **i.kwargs)
                        i.active = False

        elif d_t and o_t:  # Keep touching
            if not (ICNT_Dev.X[0] == ICNT_Old.X[0] and ICNT_Dev.Y[0] == ICNT_Old.Y[0]):
                if self.back_left.active and not self.back_left.showed:
                    if d_x - self.back_left.temp_location[0] >= 20:
                        self.pool.add(self.env.back_left, True)
                        self.back_left.showed = True
                elif self.back_right.active and not self.back_right.showed:
                    if d_x - self.back_right.temp_location[0] >= 20:
                        self.pool.add(self.env.back_right, True)
                        self.back_right.showed = True

        self.env.Now.Book.Page.touch_records_rlock.release()
        self.data_lock.release()
