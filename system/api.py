import threading
import os
import time
import traceback

from flask import Flask, request, abort


class API:
    def __init__(self, env, debug=False):
        self.env = env
        self.logger = env.Logger
        self.debug = debug
        self.port = 5050

        self.thread = None

        self.app = Flask(__name__)

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
            self.logger.info(f"API请求:\nurl:{request.url}\n"
                             f"args:{str(request.args)}\ndata:{request.data.decode('utf-8')}")
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
            self.logger.warn(f"EVAL远程执行:{cmd}")
            if self.debug:
                try:
                    r = eval(cmd)
                except Exception as e:
                    self.logger.error(traceback.format_exc())
                    raise e
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
        self.thread = threading.Thread(target=self.app.run, kwargs={"host": "0.0.0.0", "port": self.port,
                                                                    "debug": self.debug, "use_reloader": False})
        self.logger.info(f"flask_api启动, port:{self.port}, token:{self.token}")
        self.thread.start()
