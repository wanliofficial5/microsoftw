from RPi import GPIO
import time
from enviroment.drivers import epdconfig
import threading


class TapticEngine:
    def __init__(self):
        if not epdconfig.inited:
            raise "GPIO未初始化"
        GPIO.setup(5, GPIO.OUT)
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._handler, daemon=True)
        self.thread.start()
        self.frequency = 180
        self.duty = 15

    def _handler(self):
        while 1:
            self.start_event.wait()  # 等待开始信号
            self.start_event.clear()
            self.stop_event.clear()

            p = GPIO.PWM(5, self.frequency)
            p.start(self.duty)

            self.stop_event.wait(timeout=60)
            self.stop_event.clear()

            p.stop()
            del p

    def shock(self, frequency=180, duty=15, length=0.02):
        self.stop_event.set()
        self.frequency = frequency
        self.duty = duty
        self.start_event.set()
        time.sleep(length)
        self.stop_event.set()

    def __del__(self):
        try:
            GPIO.setup(5, GPIO.IN)
        except RuntimeError:
            pass


if __name__ == "__main__":
    epdconfig.module_init()
    t = TapticEngine()
    t.shock()
    time.sleep(1)
    t.shock()
    epdconfig.module_exit()
