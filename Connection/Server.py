from Connection.Socket import Socket


class Server:
    def __init__(self, host, port):
        self.socket = Socket(host, port)
        self.buffer = b""

    def connect(self, nickname, real_name = None, server_password = None):
        self.socket.connect()
        if not real_name:
            real_name = nickname
        if server_password:
            self.socket.send('PASS {}\r\n'.format(server_password).encode('utf-8'))
        self.socket.send('NICK {}\r\n'.format(nickname).encode('utf-8'))
        self.socket.send('USER {} 0 * :{}\r\n'.format(nickname, real_name).encode('utf-8'))

    def disconnect(self, message = 'Client closed.'):
        self.socket.send('QUIT :{}\r\n'.format(message).encode('utf-8'))
        self.socket.close()
        del self.socket
