import os
import time

time.sleep(2)

os.system("git checkout . && git clean -f")
os.system("git checkout web")

os.system("python3 main.py &")
