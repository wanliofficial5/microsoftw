class Bluetooth:
    def __init__(self, pool, logger):
        self.pool = pool
        self.logger = logger

        self.discoverable = 0

        self.services = {}

        self._running = True

    def discoverable_daemon(self):
        pass

    def set_discoverable(self, status):
        pass

    def new_service(self, name, uuid, callback=lambda *args, **kwargs: None, recv_encoding="utf-8",
                    send_encoding="utf-8", status_callback=lambda *args, **kwargs: None):
        return None

    def close_all(self):
        pass

    def close(self, uuid):
        pass

    def stop(self):
        pass

    def list(self):
        return ()
