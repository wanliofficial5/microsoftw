from framework import lib
from framework import struct

import time
import random
import json

import websocket
from objprint import objstr

from traceback import format_exc

SERVER = "wss://zzzing.cn/ebox"
ID = "JOCKER"


class Status:
    def __init__(self, status, box: bool, server: bool):
        self.status = status
        self.box = box
        self.server = server


class Data:
    def __init__(self, temp, humi, light, oxygen):
        self.temp = temp
        self.humi = humi
        self.light = light
        self.oxygen = oxygen

    def to_dict(self):
        return {
            "temp": self.temp,
            "humi": self.humi,
            "light": self.light,
            "oxygen": self.oxygen
        }


class EVAL_ENV:
    def __init__(self, env):
        self.env = env

    def run(self, cmd):
        env = self.env
        try:
            return eval(cmd)
        except:
            return format_exc()


class Connector:
    def __init__(self, env, uuid, address, status_callback, data_callback):
        self.eval_env = EVAL_ENV(env)
        self.pool = env.Pool  # 线程池
        self.logger = env.Logger  # 日志
        self.uuid = uuid
        self.address = address
        self.status_callback = status_callback
        self.data_callback = data_callback

        self.running = False

        self.status = False
        self.box = False
        self.server = False

        self.ws = None

        self.data = {}

    def socket_loop(self):
        def on_message(ws, message):
            self.logger.info("[%s] %s" % (self.address, message))
            try:
                data = json.loads(message)
                if data["type"] == "status":
                    ws.send(json.dumps({"type": "status", "data": {"status": self.status, "box": self.box}}))
                if data["type"] == "cmd":
                    cmd = data["data"]
                    if cmd == "start":
                        if self.status:
                            ws.send(json.dumps({"type": "cmd_result", "data": "already running"}))
                            return
                        self.data = {}
                        self.status = True
                        self.status_callback(Status(self.status, self.box, self.server))
                        ws.send(json.dumps({"type": "cmd_result", "data": "started"}))
                    elif cmd == "stop":
                        if not self.status:
                            ws.send(json.dumps({"type": "cmd_result", "data": "already stopped"}))
                            return
                        self.status = False
                        self.status_callback(Status(self.status, self.box, self.server))
                        ws.send(json.dumps({"type": "cmd_result", "data": "stopped"}))
                    elif cmd.startswith("eval:"):
                        cmd = cmd[5:]
                        self.pool.add(lambda : ws.send(json.dumps({"type": "cmd_result", "data": objstr(self.eval_env.run(cmd))})))
                    else:
                        ws.send(json.dumps({"type": "cmd_result", "data": "unknown command"}))
                elif data["type"] == "get_data":
                    if not self.status:
                        ws.send(json.dumps({"type": "get_data", "data": "not running"}))
                        return
                    last_time = int(data["data"]["last_time"])
                    # 返回晚于last_time的数据
                    new_data = {}
                    for record_time in self.data.keys():
                        if record_time > last_time:
                            new_data[record_time] = self.data[record_time].to_dict()
                    ws.send(json.dumps({"type": "get_data", "data": data}))
                elif data["type"] == "get_now":
                    ws.send(json.dumps({"type": "get_now", "data": self.data[sorted(self.data.keys())[-1]].to_dict()}))

            except Exception as e:
                self.logger.error("[%s] %s" % (self.address, e))

        def on_error(ws, error):
            self.logger.info("[%s] %s" % (self.address, error))

        def on_close(ws, *args):
            self.logger.info("[%s] closed" % self.address)
            if self.running:
                self.server = False
                self.status_callback(Status(self.status, self.box, self.server))
                time.sleep(4)
                self.pool.add(self.socket_loop)

        def on_open(ws):
            self.logger.info("[%s] connected" % self.address)
            ws.send(json.dumps({"type": "init", "data": ID}))
            self.server = True
            self.status_callback(Status(self.status, self.box, self.server))

        websocket.enableTrace(True)

        if self.ws:
            self.ws.close()
        self.ws = websocket.WebSocketApp(SERVER,
                                         on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close)
        self.ws.on_open = on_open
        self.ws.run_forever()

    def active(self):
        # 异步连接培养箱和服务器，连接成功后调用status_callback
        self.running = True

        # ...

        self.pool.add(self.mainloop)
        self.pool.add(self.socket_loop)

    def disactive(self):
        # 断开培养箱和服务器，并停止主循环
        self.running = False

        # ...

        self.ws.close()
        self.status_callback(Status(False, False, False))

    def mainloop(self):
        # 主循环，每隔一段时间获取培养箱，调用data_callback
        while self.running:
            # 调用data_callback返回随机的数据
            new_data = Data(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100),
                            random.randint(0, 100))
            self.data_callback(new_data)
            if self.status:
                self.data[time.time()] = new_data

            # 等待随机时间
            time.sleep(5)


class MainPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "培养箱检测")

        # 显示温度
        self.add_element(lib.Elements.TextElement(self, (10, 35), "温度", font_size=16))
        self.temp = self.add_element(lib.Elements.Label(self, (12, 50), (24, 24), text="20℃", font_size=24))
        # 显示湿度
        self.add_element(lib.Elements.TextElement(self, (100, 35), "湿度", font_size=16))
        self.humi = self.add_element(lib.Elements.Label(self, (102, 50), (24, 24), text="70%", font_size=24))
        # 显示光照
        self.add_element(lib.Elements.TextElement(self, (10, 80), "光照", font_size=16))
        self.light = self.add_element(lib.Elements.Label(self, (12, 95), (24, 24), text="1000lx", font_size=24))
        # 显示氧气
        self.add_element(lib.Elements.TextElement(self, (190, 35), "氧气", font_size=16))
        self.oxygen = self.add_element(lib.Elements.Label(self, (192, 50), (24, 24), text="2000", font_size=24))

        self.status = self.add_element(lib.Elements.TextElement(self, (190, 78), "运行状态：空闲"))
        self.box = self.add_element(lib.Elements.TextElement(self, (190, 93), "培养箱：在线"))
        self.server = self.add_element(lib.Elements.TextElement(self, (190, 108), "服务器: 未连接"))

        self.add_element(lib.Elements.LabelButton(self, size=(45, 20), func=self.exit, location=(250, 7), text="退出",
                                                  font_size=16))

        self.connector = Connector(book.base.env, "uuid", "address", self.status_handler, self.data_handler)

    def active(self):
        super().active()
        self.connector.active()

    def status_handler(self, status: Status):
        # 更新运行状态
        if status.status:
            self.status.set_text("运行状态：运行中", False)
        else:
            self.status.set_text("运行状态：空闲", False)
        # 更新培养箱状态
        if status.box:
            self.box.set_text("培养箱：在线", False)
        else:
            self.box.set_text("培养箱：离线", False)
        # 更新服务器状态
        if status.server:
            self.server.set_text("服务器: 已连接")
        else:
            self.server.set_text("服务器: 未连接")

    def data_handler(self, data: Data):
        # 更新温度
        self.temp.set_text(str(data.temp) + "℃", False)
        # 更新湿度
        self.humi.set_text(str(data.humi) + "%", False)
        # 更新氧气含量
        self.oxygen.set_text(str(data.oxygen) + "%", False)
        # 更新光照
        self.light.set_text(str(data.light) + "lx")

    def exit(self):
        self.connector.disactive()
        self.book.base.env.change_theme("默认（黑）")


class MainBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", MainPage(self))


class Theme(lib.ThemeBaseWithoutDocker):
    def __init__(self, env):
        super().__init__(env)
        self.add_book("main", MainBook(self))
