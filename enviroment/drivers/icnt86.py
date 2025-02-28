# 已被fu1fan修改，勿直接应用于生产环境
import time

from enviroment.drivers import epdconfig as config
from enviroment.touchscreen import TouchRecoder


class IcntDevelopment:
    def __init__(self):
        self.Touch = 0
        self.TouchGestureId = 0
        self.TouchCount = 0

        self.TouchEvenId = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.P = [0, 1, 2, 3, 4]


class ICNT86:
    def __init__(self):
        # e-Paper
        self.ERST = config.EPD_RST_PIN
        self.DC = config.EPD_DC_PIN
        self.CS = config.EPD_CS_PIN
        self.BUSY = config.EPD_BUSY_PIN
        # TP
        self.TRST = config.TRST
        self.INT = config.INT

    @staticmethod
    def digital_read(pin):
        return config.digital_read(pin)

    def icnt_reset(self):
        config.digital_write(self.TRST, 1)
        config.delay_ms(100)
        config.digital_write(self.TRST, 0)
        config.delay_ms(100)
        config.digital_write(self.TRST, 1)
        config.delay_ms(100)

    @staticmethod
    def icnt_write(reg, data):
        config.i2c_writebyte(reg, data)

    @staticmethod
    def icnt_read(reg, __len):
        return config.i2c_readbyte(reg, __len)

    def icnt_read_version(self):
        buf = self.icnt_read(0x000a, 4)
        print(buf)

    def icnt_init(self):
        self.icnt_reset()
        self.icnt_read_version()

    def icnt_scan(self, ICNT_Dev, ICNT_Old):
        # buf = []
        mask = 0x00

        if ICNT_Dev.Touch == 1:
            # ICNT_Dev.Touch = 0
            buf = self.icnt_read(0x1001, 1)

            if buf[0] == 0x00:
                self.icnt_write(0x1001, mask)
                config.delay_ms(1)
                # print("buffers status is 0")
                return
            else:
                ICNT_Dev.TouchCount = buf[0]

                if ICNT_Dev.TouchCount > 5 or ICNT_Dev.TouchCount < 1:
                    self.icnt_write(0x1001, mask)
                    ICNT_Dev.TouchCount = 0
                    # print("TouchCount number is wrong")
                    return

                buf = self.icnt_read(0x1002, ICNT_Dev.TouchCount * 7)
                self.icnt_write(0x1001, mask)

                ICNT_Old.X[0] = ICNT_Dev.X[0]
                ICNT_Old.Y[0] = ICNT_Dev.Y[0]
                ICNT_Old.P[0] = ICNT_Dev.P[0]

                for i in range(0, ICNT_Dev.TouchCount, 1):
                    ICNT_Dev.TouchEvenId[i] = buf[6 + 7 * i]
                    ICNT_Dev.X[i] = 295 - ((buf[2 + 7 * i] << 8) + buf[1 + 7 * i])
                    ICNT_Dev.Y[i] = 127 - ((buf[4 + 7 * i] << 8) + buf[3 + 7 * i])
                    ICNT_Dev.P[i] = buf[5 + 7 * i]

                # print(ICNT_Dev.X[0], ICNT_Dev.Y[0], ICNT_Dev.P[0])
                return
        return


class TouchDriver(ICNT86):
    def __init__(self):
        super().__init__()

    def icnt_reset(self):
        super().icnt_reset()

    def icnt_read_version(self):
        buf = self.icnt_read(0x000a, 4)

    def icnt_init(self):
        super().icnt_init()

    def icnt_scan(self, ICNT_Dev: TouchRecoder, ICNT_Old: TouchRecoder):
        mask = 0x00

        ICNT_Old.Touch = ICNT_Dev.Touch
        ICNT_Old.TouchGestureId = ICNT_Dev.TouchGestureId
        ICNT_Old.TouchCount = ICNT_Dev.TouchCount
        ICNT_Old.TouchEvenId = ICNT_Dev.TouchEvenId
        ICNT_Old.X = ICNT_Dev.X.copy()
        ICNT_Old.Y = ICNT_Dev.Y.copy()
        ICNT_Old.P = ICNT_Dev.P.copy()

        n = None
        for _ in range(20):
            n = self.digital_read(self.INT)
            if n == 0:
                break
            time.sleep(0.001)

        if n == 0:  # 检测屏幕是否被点击，不是每次都能扫描出来
            ICNT_Dev.Touch = 1
            buf = self.icnt_read(0x1001, 1)

            if buf[0] == 0x00:
                self.icnt_write(0x1001, mask)
                config.delay_ms(1)
                print("touchpad buffers status is 0!")
                return
            else:
                ICNT_Dev.TouchCount = buf[0]

                if ICNT_Dev.TouchCount > 5 or ICNT_Dev.TouchCount < 1:
                    self.icnt_write(0x1001, mask)
                    ICNT_Dev.TouchCount = 0
                    print("TouchCount number is wrong!")
                    return

                buf = self.icnt_read(0x1002, ICNT_Dev.TouchCount * 7)
                self.icnt_write(0x1001, mask)

                for i in range(0, ICNT_Dev.TouchCount, 1):
                    ICNT_Dev.TouchEvenId[i] = buf[6 + 7 * i]
                    ICNT_Dev.X[i] = 295 - ((buf[2 + 7 * i] << 8) + buf[1 + 7 * i])
                    ICNT_Dev.Y[i] = 127 - ((buf[4 + 7 * i] << 8) + buf[3 + 7 * i])
                    ICNT_Dev.P[i] = buf[5 + 7 * i]

                return
        else:
            ICNT_Dev.Touch = 0
            return
