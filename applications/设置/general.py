import os
import signal

from PIL import Image

from enviroment.touchscreen.events import SlideX
from framework import lib, struct


class GeneralSettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        super().__init__(book, "通用",
                         ["主题",
                          "Docker",
                          "震动",
                          "更新",
                         ],
                         funcs=[
                             self.theme,
                             self.docker,
                             self.taptic,
                             self.update_ui,
                         ],
                         styles=["NEXT", "NEXT", "NEXT", None])

    def theme(self):
        self.book.change_page("theme")

    def docker(self):
        self.book.change_page("docker")

    def taptic(self):
        self.book.change_page("taptic")

    def update_ui(self):
        if self.book.base.env.choice("即将更新...", "请不要断开电源或网络"):
            self.book.base.env.Screen.display(Image.open("resources/images/raspberry.jpg"))
            self.book.base.env.quit()
            os.system("sudo python3 updater.py &")
            os.kill(os.getpid(), signal.SIGTERM)


class TapticSettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        self.env = book.base.env
        style1 = "ON" if self.env.Config.read("vibrate") else "OFF"
        style2 = "ON" if self.env.Config.read("feedback_vibrate") else "OFF"
        style3 = "ON" if self.env.Config.read("notice_vibrate") else "OFF"
        style4 = "ON" if self.env.Config.read("other_vibrate") else "OFF"
        super().__init__(book, "震动",
                         ["总开关",
                          "反馈震动",
                          "通知震动",
                          "其他震动"
                          ],
                         funcs=[
                             self.set_vibrate,
                             self.set_feedback_vibrate,
                             self.set_notice_vibrate,
                             self.set_other_vibrate
                         ],
                         styles=[
                             style1, style2, style3, style4
                         ])

    def set_vibrate(self):
        if self.env.Config.read("vibrate"):
            self.env.Config.set("vibrate", False)
            self.set_style(0, "OFF")
        else:
            self.env.Config.set("vibrate", True)
            self.set_style(0, "ON")

    def set_feedback_vibrate(self):
        if self.env.Config.read("feedback_vibrate"):
            self.env.Config.set("feedback_vibrate", False)
            self.set_style(1, "OFF")
        else:
            self.env.Config.set("feedback_vibrate", True)
            self.set_style(1, "ON")

    def set_notice_vibrate(self):
        if self.env.Config.read("notice_vibrate"):
            self.env.Config.set("notice_vibrate", False)
            self.set_style(2, "OFF")
        else:
            self.env.Config.set("notice_vibrate", True)
            self.set_style(2, "ON")

    def set_other_vibrate(self):
        if self.env.Config.read("other_vibrate"):
            self.env.Config.set("other_vibrate", False)
            self.set_style(3, "OFF")
        else:
            self.env.Config.set("other_vibrate", True)
            self.set_style(3, "ON")


class DockerEmulator(struct.Element):
    def __init__(self, page):
        super().__init__(page)
        self.env = page.book.base.env
        self._location = (60, 0)
        self._background = self.env.docker_img
        self.img = self._background

    def update(self, docker_list):
        self.img = self._background.copy()
        x = 52
        for i in docker_list:
            self.img.paste(self.env.apps[i].icon, (x, 5))
            x += 30

    def render(self):
        return self.img


class DockerSettingPage(lib.Pages.ListPage):
    def __init__(self, book):
        super().__init__(book, "编辑", [], func=self.select)
        self.docker_list = self.env.Config.read("docker")
        self.env = book.base.env
        self.emulator = DockerEmulator(self)
        self.add_element(self.emulator)
        self.inited = False

    def select(self, index):
        if not self.inited:
            return
        if self.items[index] in self.docker_list:
            self.docker_list.remove(self.items[index])
            self.env.Config.set("docker", self.docker_list)
            self.emulator.update(self.docker_list)
            self.set_style(index)
        else:
            if len(self.docker_list) < 3:
                self.docker_list.append(self.items[index])
                self.env.Config.set("docker", self.docker_list)
                self.emulator.update(self.docker_list)
                self.set_style(index, "OK")

    def active(self):
        self.docker_list = self.env.Config.read("docker")
        flag = False
        for i in self.docker_list.copy():
            if i not in self.env.apps:
                self.docker_list.remove(i)
                flag = True
        if flag:
            self.env.Config.set("docker", self.docker_list)

        self.clear(False)
        for app_name, app in self.env.apps.items():
            if app.show_in_drawer:
                self.append(app_name, icon=app.icon, display=False)
        for i in range(len(self.items)):
            if self.items[i] in self.docker_list:
                self.set_style(i, "OK")

        self.inited = True
        self.emulator.update(self.docker_list)


class ThemeSelectPage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self.env = book.base.env
        self.themes = []
        self.now_theme = None

        # 界面
        self.theme_show = lib.Elements.Image(self, (0, 0))
        self.add_element(self.theme_show)

        self.next_button = lib.Elements.ImageButton(self, (233, 100), (24, 24), self.go_next,
                                                    Image.open("applications/设置/resources/right.png"), False)
        self.add_element(self.next_button)

        self.prev_button = lib.Elements.ImageButton(self, (39, 100), (24, 24), self.go_prev,
                                                    Image.open("applications/设置/resources/left.png"), False)
        self.add_element(self.prev_button)

        self.add_element(lib.Elements.LabelButton(
            self, (160, 28), self.select,  (68, 100),
            background=Image.open("applications/设置/resources/title_blank.png"), border=(8, 2)))

        self.title_text = lib.Elements.Label(self, (92, 100), (133, 28), border=(0, 4), font_size=16, align="C")
        self.add_element(self.title_text)

        self.index_show = lib.Elements.Label(self, (230, 5), (60, 18), border=(0, 4),
                                             background=Image.open("applications/设置/resources/index_blank.png"),
                                             align="C")
        self.add_element(self.index_show)

        self.tick = lib.Elements.Image(self, (73, 100), image=Image.open("resources/images/ok.png"), show=False)
        self.add_element(self.tick)

        self.at = 0

        self.touch_records = [SlideX((0, 296, 0, 128), self.slide_handler)]

    def slide_handler(self, dis):
        if dis > 0:
            self.go_prev()
        else:
            self.go_next()

    def active(self):
        self.themes = list(self.env.themes.keys())
        self.now_theme = self.env.now_theme
        self.at = self.themes.index(self.now_theme)
        self.prev_button.set_show(self.at > 0, False)
        self.next_button.set_show(self.at < len(self.themes) - 1, False)
        self.index_show.set_text(f"{self.at+1}/{len(self.themes)}", False)
        self.theme_show.set_image(self.env.themes[self.now_theme].preview, False)
        self.title_text.set_text(self.now_theme, False)
        self.tick.set_show(True, False)

    def go_next(self):
        if self.at < len(self.themes) - 1:
            self.at += 1
            self.prev_button.set_show(self.at > 0, False)
            self.next_button.set_show(self.at < len(self.themes) - 1, False)
            self.index_show.set_text(f"{self.at + 1}/{len(self.themes)}", False)
            self.theme_show.set_image(self.env.themes[self.themes[self.at]].preview, False)
            self.title_text.set_text(self.themes[self.at], False)
            self.tick.set_show(self.themes[self.at] == self.now_theme, True)

    def go_prev(self):
        if self.at > 0:
            self.at -= 1
            self.prev_button.set_show(self.at > 0, False)
            self.next_button.set_show(self.at < len(self.themes) - 1, False)
            self.index_show.set_text(f"{self.at + 1}/{len(self.themes)}", False)
            self.theme_show.set_image(self.env.themes[self.themes[self.at]].preview, False)
            self.title_text.set_text(self.themes[self.at], False)
            self.tick.set_show(self.themes[self.at] == self.now_theme, True)

    def select(self):
        if self.themes[self.at] != self.now_theme:
            self.env.now_theme = self.now_theme = self.themes[self.at]
            self.tick.set_show(True, True)
            self.env.Config.set("theme", self.now_theme)


class GeneralSettingsBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", GeneralSettingsPage(self))
        self.add_page("docker", DockerSettingPage(self), False)
        self.add_page("theme", ThemeSelectPage(self), False)
        self.add_page("taptic", TapticSettingsPage(self), False)
