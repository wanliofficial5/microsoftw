import threading

import bluetooth
import subprocess


class Service:
    def __init__(self, name, uuid, callback, recv_encoding, send_encoding, father, status_callback):
        self.status_callback = status_callback
        self.father = father
        self.pool = father.pool
        self.logger = father.logger
        self.name = name
        self.uuid = uuid
        self.callback = callback
        self.recv_encoding = recv_encoding
        self.send_encoding = send_encoding

        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(1)
        self.port = self.server_sock.getsockname()[1]

        self._connected = False
        self.auto_accept = False

        self.client_sock = None
        self.client_info = None

        self._closed = False

    @property
    def connected(self):
        return self._connected

    @property
    def closed(self):
        return self._closed

    def accept(self, auto_accept=False):
        if self._closed:
            raise RuntimeError("服务已关闭")
        elif self._connected:
            raise RuntimeError("已连接")
        self.info("准备连接")
        self.father.set_discoverable(True)
        bluetooth.advertise_service(self.server_sock, self.name, service_id=self.uuid,
                                    service_classes=[self.uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                    # protocols=[bluetooth.OBEX_UUID]
                                    )
        self.auto_accept = auto_accept
        self.client_sock, self.client_info = self.server_sock.accept()
        self._connected = True
        self.info(f"连接到设备{str(self.client_info)}")
        self.status_callback(True)
        self.father.set_discoverable(False)
        bluetooth.stop_advertising(self.server_sock)
        self.pool.add(self.handler)
        return self.client_info

    def info(self, content):
        self.logger.info(f"蓝牙服务{self.name}(uuid: {self.uuid}): {content}")

    def handler(self):
        try:
            while 1:
                data = self.client_sock.recv(1024).decode(self.recv_encoding) if self.recv_encoding else \
                    self.client_sock.recv(1024)
                if not data:
                    break
                self.pool.add(self.callback, data)
                self.info(f"收到消息: {data}")
        except OSError:
            self._connected = False
            self.client_sock.close()
            self.status_callback(False)
            self.info("断开连接")
            if self.auto_accept:
                self.accept(True)

    def send(self, data: str):
        if self._connected:
            self.client_sock.send(data.encode(self.send_encoding))
            self.info(f"发送消息: {data}")

    def close(self):
        self._closed = True
        self._connected = False
        self.server_sock.close()
        self.client_sock.close()


class Bluetooth:
    def __init__(self, pool, logger):
        self.pool = pool
        self.logger = logger

        self.dis_lock = threading.Lock()
        self.discoverable = 0
        self.discoverable_event1 = threading.Event()
        self.discoverable_event2 = threading.Event()

        self.services = {}

        self._running = True

        subprocess.run(['bluetoothctl', 'power', 'on'])
        subprocess.run(["bluetoothctl", "pairable", "on"])

        threading.Thread(target=self.discoverable_daemon, daemon=True).start()

    def discoverable_daemon(self):
        if self.discoverable > 0:
            last = True
        else:
            last = False
        while self._running:
            self.discoverable_event1.wait(timeout=100)
            if self.discoverable:
                subprocess.run(["bluetoothctl", "discoverable", "on"])
                self.logger.info("启动蓝牙广播")
            elif last and not self.discoverable:
                subprocess.run(["bluetoothctl", "discoverable", "off"])
                self.logger.info("停止蓝牙广播")
            if self.discoverable > 0:
                last = True
            else:
                last = False
            self.discoverable_event1.clear()
            self.discoverable_event2.set()

    def set_discoverable(self, status):
        self.dis_lock.acquire()
        if status:
            self.discoverable += 1
        elif self.discoverable:
            self.discoverable -= 1
        self.discoverable_event2.clear()
        self.discoverable_event1.set()
        if status:
            self.discoverable_event2.wait()
        self.dis_lock.release()

    def new_service(self, name, uuid, callback=lambda *args, **kwargs: None, recv_encoding="utf-8",
                    send_encoding="utf-8", status_callback=lambda *args, **kwargs: None):
        service = Service(name, uuid, callback, recv_encoding, send_encoding, self, status_callback)
        self.logger.info(f'蓝牙服务{name}注册. uuid:{uuid} port:{service.port}')
        self.services[uuid] = service
        return service

    def close_all(self):
        for service in self.services.keys():
            self.services[service].close()
        self.services = {}

    def close(self, uuid):
        self.services[uuid].close()
        del self.services[uuid]

    def stop(self):
        self.close_all()
        self._running = False

    def list(self):
        result = ((service.name, service.uuid, service.connected, service.client_info, service.client_info)
                  for service in self.services.values())
        return result


if __name__ == "__main__":
    import time
    from system import threadpool, logger

    t = threadpool.ThreadPool(10, print)
    t.start()
    lo = logger.Logger(logger.DEBUG)
    b = Bluetooth(t, lo)

    def call(data):
        print("服务:"+data)
        s.send(data)

    def call1(data):
        print("服务1:"+data)
        s.send(data)

    s = b.new_service("测试服务", "94f39d29-7d6d-437d-973b-fba39e49d4ee", call)
    t.add(s.accept, True)

    s1 = b.new_service("测试服务1", "94f39d29-7d6d-437d-973b-fba39e49d4ea", call1)
    t.add(s1.accept, True)

    while 1:
        time.sleep(5)
