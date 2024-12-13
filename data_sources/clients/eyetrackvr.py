import threading

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class EyeTrackVR:
    def __init__(self, ip="127.0.0.1", port=9000, timeout=0.3):
        self.ip = ip
        self.port = port
        self.timeout = timeout

        dispatcher = Dispatcher()
        dispatcher.map("/tracking/eye/LeftRightVec", lambda addr, *args: self._update_data(args[0], args[1]))
        self.osc_server = BlockingOSCUDPServer((self.ip, self.port), dispatcher)

        self.last_x = None
        self.last_y = None

    def start(self):
        self.thread = threading.Thread(target=self._serve)
        self.thread.start()

    def stop(self):
        self.osc_server.shutdown()
        self.osc_server.server_close()
        if self.thread.is_alive():
            self.thread.join(timeout=1)

    def get_last_data(self):
        return (self.last_x, self.last_y)

    def _update_data(self, new_x: float, new_y: float):
        self.last_x = new_x
        self.last_y = new_y

    def _serve(self):
        self.osc_server.serve_forever(self.timeout)
