import os
import signal

from PIL import Image

from framework import lib, struct


class SystemSettingsPage(lib.Pages.ListPage):
    def __init__(self, book):
        self.env = book.base.env
        super().__init__(book, "系统选项",
                         ["关机",
                          "重启",
                          "切换分支",
                          "清空日志",
                          "反转屏幕"],
                         funcs=[
                             self.poweroff,
                             self.reboot,
                             self.change_branch,
                             self.clean_logs,
                             self.screen_reverse
                         ]
                         )

    def poweroff(self):
        if self.env.choice("关机", "确认关闭电源?"):
            self.env.poweroff()

    def reboot(self):
        if self.env.choice("重启", "是否重启？\n预计耗时30秒，期间屏幕会未响应。"):
            self.env.reboot()

    def clean_logs(self):
        if self.env.choice("清空日志", "是否清空日志？\nlogs文件夹内所有文件将被删除！", display=True):
            self.env.clean_logs()

    def change_branch(self):
        if self.env.choice("切换分支", "即将重启到@xuanzhi33编写的web分支"):
            self.book.base.env.Screen.display(Image.open("resources/images/raspberry.jpg"))
            self.book.base.env.quit()
            os.system("sudo python3 change_branch.py &")
            os.kill(os.getpid(), signal.SIGTERM)

    def screen_reverse(self):
        if self.env.choice("反转屏幕", "是否反转屏幕?\n该操作将立即生效"):
            self.env.screen_reverse()


class SystemSettingsBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", SystemSettingsPage(self))