from math import floor
from os import path, mkdir
from time import time
from Connection.Socket import Socket


def validateName(name):
    # https://modern.ircdocs.horse/#clients
    if not name:
        raise ValueError('Name cannot be empty.')
    if ' ' in name:
        raise ValueError('Name cannot contain spaces. " "')
    if '.' in name:
        raise ValueError('Name cannot contain periods. "."')
    if ',' in name:
        raise ValueError('Name cannot contain commas. ","')
    if '*' in name:
        raise ValueError('Name cannot contain asterisks. "*"')
    if '?' in name:
        raise ValueError('Name cannot contain question marks. "?"')
    if '!' in name:
        raise ValueError('Name cannot contain exclamation marks. "!"')
    if '@' in name:
        raise ValueError('Name cannot contain at signs. "@"')
    if name[0] in ['#', '&', '~', '@', '%', '+', '-', '!']:
        raise ValueError('Name cannot start with a special character. ( #, &, ~, @, %, +, -, ! )')


class Server:
    def __init__(self, host, port, nickname, real_name=None, password=None):
        self._socket = Socket(host, port)
        self.nickname = nickname
        validateName(nickname)
        if real_name is not None:
            self.real_name = real_name
            validateName(real_name)
        else:
            self.real_name = nickname
        self.password = password

        self._setupLogging()
        self.log("Server setup: " + host + ":" + str(port) + " (" + self.nickname + "!" + self.real_name + ")")

    def _setupLogging(self):
        if not path.exists("logs"):
            mkdir("logs")
        self._log_filename = "logs/" + str(floor(time())) + ".txt"
        self._log = open(self._log_filename, "w")
        self._log.close()
        self._log = open(self._log_filename, "a")
        self._log.write("Log started at " + str(floor(time())) + "\n")
        self._log.flush()

    def log(self, message):
        self._log.write(message + "\n")
        self._log.flush()

    def connect(self):
        self._socket.connect()
        if self.password is not None:
            self._socket.send('PASS {}\r\n'.format(self.password).encode('utf-8'))
        self._socket.send('NICK {}\r\n'.format(self.nickname).encode('utf-8'))
        self._socket.send('USER {} 0 * :{}\r\n'.format(self.nickname, self.real_name).encode('utf-8'))
        # Expect responses 001, 002, 003 and 004 in order.

        # for nickname errors:
        # 433: ERR_NICKNAMEINUSE
        # 431: ERR_NONICKNAMEGIVEN
        # 432: ERR_ERRONEUSNICKNAME
        # 436: ERR_NICKCOLLISION

        # for user errors:
        # 462: ERR_ALREADYREGISTRED

        # for server errors:
        # 463: ERR_NOPRIVILEGES
        # 464: ERR_PASSWDMISMATCH
        # 465: ERR_YOUREBANNEDCREEP
        # 466: ERR_YOUWILLBEBANNED

    def disconnect(self, message='Client closed.'):
        self._socket.send('QUIT :{}\r\n'.format(message).encode('utf-8'))
        self._socket.close()

        self.log("Disconnected from server - " + message)
        self._log.close()


class Message:
    def __init__(self, buffer=b""):
        self._buffer = buffer
        self.x = 1

    def encode(self):
        return self._buffer
