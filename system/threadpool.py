import ctypes
import inspect
import queue
import threading
import time
import traceback
from queue import Queue


def _async_raise(tid, exc_type):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exc_type):
        exc_type = type(exc_type)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exc_type))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class ThreadPool:
    def __init__(self, thread_num: int, handler=None):
        self.tasks = Queue()
        self.threads = []
        self.running = False
        self.__inited = False
        if handler is None:
            handler = self.__error_handler
        else:
            handler = handler
        self.handler = handler
        self.__lock = threading.Lock()
        self.__lock_wait = threading.Lock()
        self.__running_num = 0
        self.__thread_num = thread_num
        self.succeed = 0
        self.fail = 0
        for _ in range(thread_num):
            self.threads.append(Worker(self.tasks,
                                       self.is_running,
                                       self.handler,
                                       self.__thread_start_work,
                                       self.__thread_finish_work))
            time.sleep(0.01)

    @staticmethod
    def __error_handler(_):
        pass

    def __thread_monitor(self, add=True):
        self.__lock.acquire()
        if add:
            self.__running_num += 1
        else:
            self.__running_num -= 1
        self.__lock.release()
        if self.__running_num == 0:
            try:
                self.__lock_wait.release()
            except RuntimeError:
                pass
        else:
            self.__lock_wait.acquire(blocking=False)

    def __thread_start_work(self):
        self.__lock.acquire()
        self.__running_num += 1
        self.__lock.release()
        self.__lock_wait.acquire(blocking=False)

    def __thread_finish_work(self, succeed=True):
        self.__lock.acquire()
        self.__running_num -= 1
        if succeed:
            self.succeed += 1
        else:
            self.fail += 1
        if self.__running_num == 0:
            try:
                self.__lock_wait.release()
            except RuntimeError:
                pass
        self.__lock.release()

    def is_running(self):
        return self.running

    def start(self):
        if self.__inited:
            raise RuntimeError("A ThreadPool can only be started once!")
        self.__inited = True
        self.running = True
        for i in self.threads:
            i.start()

    def add(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))

    def add_immediately(self, func, *args, **kwargs):
        """
        这种方法添加的线程不受线程池控制
        """
        if self.full():
            new_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            new_thread.start()
            return new_thread
        else:
            self.tasks.put((func, args, kwargs))

    def stop(self):  # TODO: join
        self.running = False

    def stop_immediately(self):  # 不稳定，不建议使用！
        self.running = False
        for i in self.threads:
            try:
                stop_thread(i)
            except (ValueError, SystemError):  # 这行代码有点危
                self.handler(traceback.format_exc())

    def task_qsize(self):
        return self.tasks.qsize()

    def empty_thread(self):
        return self.__thread_num - self.__running_num

    def running_thread(self):
        return self.__running_num

    def clear(self):
        self.tasks.queue.clear()  # TODO:未测试

    def wait(self, timeout=-1):
        self.__lock_wait.acquire(timeout=timeout)

    def full(self):
        if self.__running_num == self.__thread_num:
            return True
        else:
            return False

    def empty(self):
        if self.__running_num == 0:
            return False


class Worker(threading.Thread):
    def __init__(self, tasks: Queue, is_running, handler, start_log, finish_log):
        super().__init__()
        self.setDaemon(True)
        self.tasks = tasks
        self.is_running = is_running
        self.handler = handler
        self.start_log = start_log
        self.finish_log = finish_log

    def run(self):
        while True:
            try:
                task = self.tasks.get(block=True, timeout=2)
                self.start_log()
                task[0](*task[1], **task[2])
                self.finish_log()
            except queue.Empty:
                pass
            except:
                self.handler(traceback.format_exc())
                self.finish_log(False)
            else:
                if not self.is_running():
                    break
