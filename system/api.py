import threading

from flask import Flask, request, abort


class API:
    def __init__(self, env, debug=False):
        self.env = env
        self.debug = debug
        self.port = 5000

        self.app = Flask(__name__)

        self.thread = threading.Thread(target=self._run)

        self.gets = {}
        self.posts = {}

        @self.app.route("/api/<name>", methods=["GET", "POST"])
        def handler(name):
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

    def _run(self):
        self.app.run(port=self.port, debug=self.debug)

    def post_api(self, name):
        if name in self.posts:
            raise ValueError("Api exists.")

        def decorator(func):
            self.posts[name] = func
            return func

        return decorator

    def run(self, port=5000):
        self.port = port
        self.thread.run()
