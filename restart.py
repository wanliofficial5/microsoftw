import os
import time

time.sleep(2)

os.system("git checkout . && git clean -f")
os.system("git pull")

os.system("python3 main.py &")
