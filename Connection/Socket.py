import socket as slib


class Socket:

    def __init__(self, host, port, sock_family=slib.AF_INET, sock_type=slib.SOCK_STREAM):
        self.host = host
        self.port = port
        self.sock_family = sock_family
        self.sock_type = sock_type
        self.sock = slib.socket(self.sock_family, self.sock_type)

    def connect(self) -> None:
        self.sock.connect((self.host, self.port))

    def send(self, data) -> None:
        self.sock.sendall(data)

    def receive(self, buffer_size=512) -> bytes:
        return self.sock.recv(buffer_size)

    def close(self) -> None:
        self.sock.close()