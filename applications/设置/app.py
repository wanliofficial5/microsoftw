from framework import lib, struct
import socket
import qrcode

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = None

    return ip


class BluetoothSettingPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "蓝牙配网")
        self.add_element(lib.Elements.MultipleLinesLabel(self, location=(4, 35), size=(292, 128),
                                                         text='当前无网络\n'
                                                              '（蓝牙配网开发尚未完成，若需连网络请切换至web分支）\n'))


class FlaskSettingPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        self.env = book.base.env
        self.api = self.env.API
        super().__init__(book, "连接APP")

        self.qr_img = self.add_element(lib.Elements.Image(self, (15, 42)))
        self.add_element(lib.Elements.TextElement(self, (100, 46), "扫描左侧二维码", font_size=16))
        self.add_element(lib.Elements.MultipleLinesLabel(self, (84, 60), (212, 68),
                                                         "-请确保您的手机和树莓派在统一局域网下\n"
                                                         "-暂不支持iOS设备，敬请谅解",
                                                         border=(18, 5)))

    def active(self):
        ip = get_host_ip()
        port = self.api.port
        token = self.api.token
        link = f"http://{ip}:{port}?token={token}"
        img = qrcode.make(link, border=1, box_size=2)
        self.qr_img.set_image(img, False)


class AppSettingsBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("bluetooth", BluetoothSettingPage(self))
        self.add_page("flask", FlaskSettingPage(self), False)

    def active(self):
        ip = get_host_ip()
        if ip:
            self.change_page("flask", False, False)
        else:
            self.change_page("bluetooth", False, False)
        super().active()
