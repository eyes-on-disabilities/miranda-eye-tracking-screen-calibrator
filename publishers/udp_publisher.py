import json
import socket
from datetime import datetime

from publishers.publisher import Publisher
from misc import Vector


class UdpPublisher(Publisher):
    """Pushes the vector as JSON objects over UDP"""

    def __init__(self, host="127.0.0.1", port=9999):
        self.sock = None
        self.server_address = (host, port)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def stop(self):
        self.sock.close()

    def push(self, vector: Vector):
        message = {"x": vector[0], "y": vector[1], "timestamp": str(datetime.now())}
        json_message = json.dumps(message)
        print(json_message)
        self.sock.sendto(json_message.encode(), self.server_address)
