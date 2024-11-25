import socket
import struct


class Opentrack:
    def __init__(self, ip="127.0.0.1", port=4242, socket_timeout=0.1):
        self.socket = None
        self.last_position = None
        self.ip = ip
        self.port = port
        self.socket_timeout = socket_timeout

    def update_last_position(self, new_values):
        assert len(new_values) == 6
        self.last_position = {
            "x": new_values[0],
            "y": new_values[1],
            "z": new_values[2],
            "yaw": new_values[3],
            "pitch": new_values[4],
            "roll": new_values[5],
        }

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5)
        self.socket.bind((self.ip, self.port))
        self.socket.settimeout(self.socket_timeout)
        self.buffer_size = 6 * 8  # Size of one message
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size)

    def stop(self):
        self.socket.close()

    def get_last_position(self):
        try:
            data, addr = self.socket.recvfrom(self.buffer_size)
            if len(data) == self.buffer_size:
                new_values = struct.unpack("6d", data)
                self.update_last_position(new_values)
            else:
                self.last_position = None
        except Exception:
            self.last_position = None
        finally:
            return self.last_position
