import os
import time
import inspect
import threading

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3


def get_name(index=1):  # 获取上上级调用者的__name__
    frm = inspect.stack()[index]  # 0是本函数，1是上级调用，2是上上级，以此类推
    mod = inspect.getmodule(frm[0])
    try:
        return mod.__name__
    except AttributeError:
        return None


class Logger:
    def __init__(self, level=WARNING):
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        self.name = time.strftime("%Y%m%d-%H:%M", time.localtime())
        self.path = f"logs/{self.name}.txt"
        if os.path.isdir(self.path):
            self.path += "(1)"
            i = 1
            while os.path.isdir(self.path):
                i += 1
                self.path = f"{self.path[:-3]}({i})"
        open(self.path, "w").close()

        self.io_lock = threading.Lock()

        self.level = level

    def debug(self, content):
        if DEBUG >= self.level:
            if content.endswith("\n"):
                content = content[:-1]
            if "\n" in content:
                content = "\n" + content
            line = f'[DEBUG][{get_name(2)}][{time.strftime("%Y%m%d-%H:%M", time.localtime())}]{content}\n'
            f = open(self.path, "a")
            f.write(line)
            f.close()

    def info(self, content):
        if INFO >= self.level:
            if content.endswith("\n"):
                content = content[:-1]
            if "\n" in content:
                content = "\n" + content
            line = f'[INFO][{get_name(2)}][{time.strftime("%Y%m%d-%H:%M", time.localtime())}]{content}\n'
            f = open(self.path, "a")
            f.write(line)
            f.close()

    def warn(self, content):
        if WARNING >= self.level:
            if content.endswith("\n"):
                content = content[:-1]
            if "\n" in content:
                content = "\n" + content
            line = f'[WARNING][{get_name(2)}][{time.strftime("%Y%m%d-%H:%M", time.localtime())}]{content}\n'
            f = open(self.path, "a")
            f.write(line)
            f.close()

    def error(self, content):
        if content.endswith("\n"):
            content = content[:-1]
        if "\n" in content:
            content = "\n" + content
        line = f'[ERROR][{get_name(2)}][{time.strftime("%Y%m%d-%H:%M", time.localtime())}]{content}\n'
        f = open(self.path, "a")
        f.write(line)
        f.close()
