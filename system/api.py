import threading
import os
import time

from flask import Flask, request, abort


class API:
    def __init__(self, env, debug=False):
        self.env = env
        self.debug = debug
        self.port = 5050

        self.app = Flask(__name__)

        self.thread = threading.Thread(target=self.app.run, kwargs={"host": "0.0.0.0", "port": self.port,
                                                                    "debug": self.debug, "use_reloader": False})
        # 通过设置use_reloader防止出现signal报错

        self.gets = {}
        self.posts = {}

        if os.path.isfile("system/token.txt"):
            file = open("system/token.txt", "r")
            self.token = file.read()
        else:
            file = open("system/token.txt", "w")
            self.token = str(hash(hash(time.time())))
            file.write(self.token)
        file.close()

        @self.app.route("/api/<name>", methods=["GET", "POST"])
        def handler(name):
            try:
                if request.args["token"] != self.token:
                    raise PermissionError
            except (KeyError, PermissionError):
                abort(403)
            if request.method == "GET":
                if name in self.gets:
                    return self.gets[name](request.args, request.data)
                else:
                    abort(404)
            else:
                if name in self.posts:
                    return self.posts[name](request.args, request.data)
                else:
                    abort(404)

        @self.app.route("/debug/<cmd>", methods=["GET", "POST"])
        def debug(cmd):
            if self.debug:
                r = eval(cmd)
                if r:
                    return r
                else:
                    return "1"
            else:
                abort(404)

    def post_api(self, name):
        if name in self.posts:
            raise ValueError("API exists.")

        def decorator(func):
            self.posts[name] = func
            return func

        return decorator

    def get_api(self, name):
        if name in self.gets:
            raise ValueError("API exists.")

        def decorator(func):
            self.gets[name] = func
            return func

        return decorator

    def start(self, port=5050):
        self.port = port
        print(f"flask_token:{self.token}")
        self.thread.start()
