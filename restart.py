import os
import time

print("restart.py 已启动")
time.sleep(3)
print("restart.py 正在重新运行main.py")
os.system("sudo python3 main.py &")

print("restart.py 已完成使命")