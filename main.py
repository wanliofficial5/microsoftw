import os
import threading
import importlib
from pathlib import Path

from PIL import Image

import enviroment
from system import configurator


'''
PaperTheme and PaperApp
Back
Home
AppController
Docker
'''


example_config = {
    "theme": "default",
    "update_tdduudf7": 1
}

if __name__ == "__main__":
    print("Running In Develop Mode")

    configurator_main = configurator.Configurator()
    configurator_main.check(example_config, True)

    env = enviroment.Env()

    load_lock = threading.Barrier(2)


    def opening():
        opening_image_paths = ["resources/images/raspberry.jpg", ]
        opening_images = []
        for path in opening_image_paths:
            opening_images.append(Image.open(Path(path)))
        for i in opening_images:
            env.Screen.display_auto(i)
            env.Screen.wait_busy()
        if load_lock.n_waiting == 0:
            env.Screen.display_auto(Image.open(Path(configurator_main.read("loading_image"))))
        load_lock.wait()


    env.Pool.add(opening)
    touch_recoder_dev = enviroment.touchscreen.TouchRecoder()
    touch_recoder_old = enviroment.touchscreen.TouchRecoder()

    # plugins
    for plugin_dir in os.listdir("plugins"):
        env.plugins[plugin_dir] = importlib.import_module(f"plugins.{plugin_dir}.main").Plugin(env)

    # apps
    for app_dir in os.listdir("applications"):
        env.apps[app_dir] = importlib.import_module(f"applications.{app_dir}.main").App(env)

    # themes
    for theme_dir in os.listdir("theme"):
        env.themes[theme_dir] = importlib.import_module(f"themes.{theme_dir}.main").Theme(env)

    env.now_theme = configurator_main.read("theme")
    env.Now = env.themes[env.now_theme]
    env.Now.active()

    while 1:  # 据说 while 1 的效率比 while True 高
        env.Touch.icnt_scan(touch_recoder_dev, touch_recoder_dev)
        env.TouchHandler.handle(touch_recoder_dev, touch_recoder_old)
