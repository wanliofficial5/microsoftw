from framework import lib, struct


class AboutPage(lib.Pages.PageWithTitle):
    def __init__(self, book):
        super().__init__(book, "关于")
        self.add_element(lib.Elements.MultipleLinesText(self, location=(15, 35), size=(266, 108),
                                                        text="欢迎使用:\n这是由@fu1fan和@xuanzhi33倾力打造的eInkUI\n仓库地址: "
                                                              "https://gitee.com/fu1fan/e-ink-ui"))


class AboutBook(struct.Book):
    def __init__(self, base):
        super().__init__(base)
        self.add_page("main", AboutPage(self))