import os
import time

time.sleep(2)

print("开始更新")

os.system("git checkout .")
os.system("git pull")

os.system("python3 main.py &")
