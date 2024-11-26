import threading
import time
from datetime import datetime, timedelta

import msgpack
import zmq


class Pupil:
    def __init__(self, ip="127.0.0.1", port=50020, timeout=0.3):
        self.ip = ip
        self.port = port
        self.timeout = timeout

        self.last_2d_data = None
        self.last_3d_data = None

        self._running = False
        self._ctx = None
        self._req_subscriber = None
        self._sub_subscriber = None

    def start(self):
        self._running = True
        self.thread = threading.Thread(target=self._subscribe_and_consume)
        self.thread.start()

    def stop(self):
        self._running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1)

    def get_last_data(self):
        return {
            "2d": self.last_2d_data,
            "3d": self.last_3d_data,
        }

    def _retry(self, func: callable, try_for_seconds=0):
        end_time = datetime.now() + timedelta(seconds=try_for_seconds)
        tried_once = False
        result = None
        error = None
        while not tried_once or (result is None and datetime.now() < end_time):
            try:
                if tried_once:
                    time.sleep(0.1)
                result = func()
            except Exception as e:
                error = e
            finally:
                tried_once = True
        if result is None:
            raise error
        return result

    def _disconnect(self):
        if self._req_subscriber is not None:
            self._req_subscriber.close()
            self._req_subscriber = None

        if self._sub_subscriber is not None:
            self._sub_subscriber.close()
            self._sub_subscriber = None

        if self._ctx is not None:
            self._ctx.term()
            self._ctx = None

        self.last_2d_data = None
        self.last_3d_data = None

    def _connect(self):
        self._ctx = zmq.Context()
        self._req_subscriber = self._ctx.socket(zmq.REQ)
        self._req_subscriber.setsockopt(zmq.LINGER, 1000)
        self._req_subscriber.connect(f"tcp://{self.ip}:{self.port}")

        self._req_subscriber.send_string("SUB_PORT")
        sub_port = self._retry(
            lambda: self._req_subscriber.recv_string(flags=zmq.NOBLOCK), try_for_seconds=self.timeout
        )

        self._sub_subscriber = self._ctx.socket(zmq.SUB)
        self._sub_subscriber.setsockopt(zmq.LINGER, 1000)
        self._sub_subscriber.connect(f"tcp://{self.ip}:{sub_port}")
        self._sub_subscriber.subscribe("gaze.")
        self._sub_subscriber.subscribe("pupil.")

    def _subscribe_and_consume(self):
        while self._running:
            try:
                if not self._sub_subscriber:
                    self._connect()

                topic, payload = self._retry(
                    lambda: self._sub_subscriber.recv_multipart(flags=zmq.NOBLOCK),
                    try_for_seconds=self.timeout,
                )
                message = msgpack.loads(payload)
                print(message)
                if topic == b"pupil.0.2d":
                    self.last_2d_data = message
                if topic == b"pupil.0.3d":
                    self.last_3d_data = message

            except Exception:
                self._disconnect()

        self._disconnect()
