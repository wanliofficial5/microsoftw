from framework import struct
from framework import lib
import socket
import os, signal

from PIL import Image, ImageFont

from enviroment.touchscreen.events import SlideX


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "Unknown"

    return ip


class SettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        cb = book.base.change_book
        super().__init__(book, "设置",
                         ["在线配置(暂不开放)",
                          "通用",
                          "系统选项",
                          "关于"],
                         funcs=[
                             lambda: cb("online"),
                             lambda: cb("general"),
                             lambda: cb("system"),
                             lambda: cb("about")
                         ]
                         )


class OnlineSettingsPage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self.ip_font = ImageFont.truetype("resources/fonts/PTSerifCaption.ttc", 30)
        self.ip_text = lib.Elements.TextElement(self, (26, 60), "IP:", self.ip_font)
        self.add_element(self.ip_text)
        self.add_element(lib.Elements.Label(self, (292, 24), (0, 0), (4, 4), "网络设置工具", font_size=16))
        self.add_element(lib.Elements.MultipleLinesLabel(self, size=(292, 128), location=(4, 25),
                                                         text="提示：在和树莓派同一局域网下用浏览器访问如下ip地址即可打开设置页面。（当前尚未完工）"))


class GeneralSettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        super().__init__(book, "通用",
                         ["主题",
                          "Docker",
                          "更新",
                          "恢复", ],
                         funcs=[
                             self.theme,
                             self.docker,
                             self.update_ui,
                             self.fix_up,
                         ])

    def theme(self):
        self.book.Pages["theme"].active()
        self.book.change_page("theme")

    def docker(self):
        self.book.Pages["docker"].active()
        self.book.change_page("docker")

    def update_ui(self):
        self.book.base.env.Screen.display(Image.open("resources/images/raspberry.jpg"))
        self.book.base.env.quit()
        os.popen("git checkout . && git clean -f")
        os.popen("git pull")
        os.system("sudo python3 restart.py &")
        os.kill(os.getpid(), signal.SIGTERM)

    def fix_up(self):
        self.book.base.env.Screen.display(Image.open("resources/images/raspberry.jpg"))
        self.book.base.env.quit()
        os.popen("git checkout . && git clean -f")
        os.system("sudo python3 restart.py &")
        os.kill(os.getpid(), signal.SIGTERM)


class DockerEmulator(struct.Element):
    def __init__(self, page):
        super().__init__(page)
        self.env = page.book.base.env
        self._location = (60, 1)
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
        self.env = book.base.env
        self.emulator = DockerEmulator(self)
        self.add_element(self.emulator)
        self.inited = False

    def select(self, index):
        if not self.inited:
            return
        if self.items[index] in self.docker_list:
            self.docker_list.remove(self.items[index])
            self.env.config.set("docker", self.docker_list)
            self.emulator.update(self.docker_list)
            self.set_style(index)
        else:
            if len(self.docker_list) < 3:
                self.docker_list.append(self.items[index])
                self.env.config.set("docker", self.docker_list)
                self.emulator.update(self.docker_list)
                self.set_style(index, "OK")

    def active(self):
        self.docker_list = self.env.config.read("docker")
        flag = False
        for i in self.docker_list.copy():
            if i not in self.env.apps:
                self.docker_list.remove(i)
                flag = True
        if flag:
            self.env.config.set("docker", self.docker_list)

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
        self.theme_show = lib.Elements.Image(self)
        self.add_element(self.theme_show)

        self.next_button = lib.Elements.ImageButton(
            self, self.go_next, (24, 24), (233, 100), Image.open("applications/设置/resources/right.png"), False)
        self.add_element(self.next_button)

        self.prev_button = lib.Elements.ImageButton(
            self, self.go_prev, (24, 24), (39, 100), Image.open("applications/设置/resources/left.png"), False)
        self.add_element(self.prev_button)

        self.add_element(lib.Elements.LabelButton(
            self, (160, 28), self.select,  (68, 100),
            background=Image.open("applications/设置/resources/title_blank.png"), border=(8, 2)))

        self.title_text = lib.Elements.Label(self, (133, 28), (92, 100), font_size=16, border=(0, 4), align="C")
        self.add_element(self.title_text)

        self.index_show = lib.Elements.Label(
            self, (60, 18), (230, 5), background=Image.open("applications/设置/resources/index_blank.png"),
            border=(0, 4), align="C")
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
            self.env.config.set("theme", self.now_theme)


class SystemSettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        env = book.base.env
        super().__init__(book, "系统选项",
                         ["关机",
                          "重启",
                          "切换分支",
                          "清空日志"],
                         funcs=[
                             env.poweroff,
                             env.reboot,
                             self.change_branch,
                             env.clean_logs
                         ]
                         )

    def change_branch(self):
        self.book.base.env.Screen.display(Image.open("resources/images/raspberry.jpg"))
        self.book.base.env.quit()
        os.popen("git checkout . && git clean -f")
        os.popen("git checkout web")
        os.system("sudo python3 restart.py &")
        os.kill(os.getpid(), signal.SIGKILL)


class AboutPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "关于")
        self.add_element(lib.Elements.MultipleLinesLabel(self, size=(266, 108), location=(15, 35),
                                                         text="欢迎使用:\n这是由@fu1fan和@xuanzhi33倾力打造的eInkUI\n仓库地址: "
                                                              "https://gitee.com/fu1fan/e-ink-ui"))


class OnlineSettingsBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", OnlineSettingsPage(self))


class GeneralSettingsBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", GeneralSettingsPage(self))
        self.add_page("docker", DockerSettingPage(self), False)
        self.add_page("theme", ThemeSelectPage(self), False)


class SystemSettingsBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", SystemSettingsPage(self))


class AboutBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", AboutPage(self))


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", SettingsPage(self))


class Application(lib.AppBase):
    def __init__(self, env):
        super().__init__(env)
        self.name = "设置"
        self.icon = Image.open("applications/设置/icon.png")
        self.title = self.name
        self.add_book("main", MainBook(self))
        self.add_book("online", OnlineSettingsBook(self), False)
        self.add_book("general", GeneralSettingsBook(self), False)
        self.add_book("system", SystemSettingsBook(self), False)
        self.add_book("about", AboutBook(self), False)

        self.show_in_drawer = False
