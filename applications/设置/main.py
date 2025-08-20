from framework.struct import Book, Page
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


class OnlineSettingsPage(Page):
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
                          "导航栏（未完成）",
                          "更新（未完成）",
                          "重置（未完成）", ])


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
        os.popen("git checkout web")
        os.system("python3 main.py &")
        os.kill(os.getpid(), signal.SIGKILL)


class AboutPage(Page):
    def __init__(self, book):
        super().__init__(book)
        self.add_element(lib.Elements.Label(self, (292, 24), (0, 0), (4, 4), "关于", font_size=16))
        self.add_element(lib.Elements.MultipleLinesLabel(self, size=(266, 108), location=(15, 20),
                                                         text="欢迎使用:\n这是由@fu1fan和@xuanzhi33倾力打造的eInkUI\n仓库地址: "
                                                              "https://gitee.com/fu1fan/e-ink-ui"))


class OnlineSettingsBook(Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", OnlineSettingsPage(self))


class GeneralSettingsBook(Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", GeneralSettingsPage(self))


class SystemSettingsBook(Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", SystemSettingsPage(self))


class AboutBook(Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", AboutPage(self))


class MainBook(Book):
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

    def active(self):
        self.Books["online"].Page.ip_text.set_text(get_host_ip(), False)
        super().active()

