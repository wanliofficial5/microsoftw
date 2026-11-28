from framework import struct
from framework import lib
import socket
import os, signal

from PIL import Image, ImageFont



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
                         ["在线配置(beta)",
                          "通用",
                          "设备选项",
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
                         ["主题（未完成）",
                          "Docker（施工中）",
                          "更新",
                          "恢复", ],
                         funcs=[
                             lambda: None,
                             self.docker,
                             self.update_ui,
                             self.fix_up,
                         ])

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
        self.docker_list = []
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

        for app_name, app in self.env.apps.items():
            if app.show_in_drawer:
                self.append(app_name, icon=app.icon, display=False)
        for i in range(len(self.items)):
            if self.items[i] in self.docker_list:
                self.set_style(i, "OK")

        self.inited = True
        self.emulator.update(self.docker_list)


class SystemSettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        env = book.base.env
        super().__init__(book, "系统选项",
                         ["关机",
                          "重启",
                          "切换分支"],
                         funcs=[
                             env.poweroff,
                             env.reboot,
                             self.change_branch
                         ]
                         )

    def change_branch(self):
        self.book.base.env.Screen.display(Image.open("resources/images/raspberry.jpg"))
        self.book.base.env.quit()
        os.popen("git checkout . && git clean -f")
        os.popen("git checkout web")
        os.system("sudo python3 restart.py &")
        os.kill(os.getpid(), signal.SIGKILL)


class AboutPage(struct.Page):
    def __init__(self, book):
        super().__init__(book)
        self.add_element(lib.Elements.Label(self, (292, 24), (0, 0), (4, 4), "关于", font_size=16))
        self.add_element(lib.Elements.MultipleLinesLabel(self, size=(266, 108), location=(15, 20),
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

        # self.show_in_drawer = False

    def active(self, refresh="a"):
        self.Books["online"].Page.ip_text.set_text(get_host_ip(), False)
        self.change_book("main", display=False)
        self.back_stack.queue.clear()
        self.Book.Page.go_to(display=False)
        super().active(refresh)

