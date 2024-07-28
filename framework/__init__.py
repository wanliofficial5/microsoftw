from PIL import Image

class Element:
    def __init__(self):
        self.layer = 0


def _get_sort_key(element: Element) -> int:
    return element.layer


class Page:
    def build(self) -> Image:
        pass


class App:
    def __init__(self, env):
        self.env = env
        self.name = ""

        self.Pages = {"main": Page()}
        self.now_page = "main"

    def display(self) -> None:
        self.env.Screen.display_auto(self.Pages[self.now_page].build())

    def start(self) -> None:  # This function will be called when this App is started for the first time.
        pass

    def active(self) -> None:  # This function will be called when this App is active. But not first started.
        pass

    def pause(self) -> None:  # This function will be called when this App is paused.
        pass

    def launch(self) -> None:  # This function will be called when the eInkUI is launch.
        pass

    def shutdown(self) -> None:  # This function will be called when the eInkUI is shutdown.
        # Technically this function should be done in 5s
        pass


class Plugin:
    def __init__(self, name):
        pass

    def launch(self) -> None:  # This function will be called when the eInkUI is launch.
        pass

    def shutdown(self) -> None:  # This function will be called when the eInkUI is shutdown.
        # Technically this function should be done in 5s
        pass
