from framework.struct import PluginBase
import requests

class Plugin(PluginBase):
    def is_online(self):
        try:
            requests.get("https://www.baidu.com").raise_for_status()
            return True
        except:
            return False
