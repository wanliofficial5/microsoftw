from RPi import GPIO
import time
from enviroment.drivers import epdconfig


class TapticEngine:
    def __init__(self):
        if not epdconfig.inited:
            raise "GPIO未初始化"
        GPIO.setup(5, GPIO.OUT)

    def shock(self, frequency=180, duty=15, t=0.03):
        p = GPIO.PWM(5, frequency)
        p.start(duty)
        time.sleep(t)
        p.stop()

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

