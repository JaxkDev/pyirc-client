from math import floor
from os import path, mkdir
from time import time
from App.Connection.Socket import Socket


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
            self.send(Message().build("PASS", [self.password]))

        self.send(Message().build("NICK", [self.nickname]))
        self.send(Message().build("USER", [self.nickname, "0", "*", self.real_name]))
        # can we assume connected after receiving 001?

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
        self.send(Message().build("QUIT", [message]))
        self._socket.close()

        self.log("Disconnected from server - " + message)
        self._log.close()

    def send(self, message):
        self.log("Sent: " + str(message))
        self._socket.send(bytes(message))


class Message:
    def __init__(self, buffer=b""):
        self._buffer = buffer
        self.tags = None
        self.source = None
        self.command = None
        self.parameters = None

    def build(self, command, parameters=None, tags=None, source=None):
        self.command = command
        self.parameters = parameters
        self.tags = tags
        self.source = source
        self.encode()
        return self

    def parse(self, buffer):
        self._buffer = buffer
        self.decode()

    def decode(self, encoding="utf-8"):
        buffer = self._buffer
        self.tags = None
        self.source = None
        self.command = None
        self.parameters = []

        try:
            if buffer.startswith(b'@'):
                self.tags, buffer = buffer[1:].split(b' ', 1)
                self.tags = self.tags.decode(encoding)
            if buffer.startswith(b':'):
                self.source, buffer = buffer[1:].split(b' ', 1)
                self.source = self.source.decode(encoding)
            self.command, buffer = buffer.split(b' ', 1)
            self.command = self.command.decode(encoding)
            params = buffer.split(b' ')
            for i in range(len(params)):
                if params[i].startswith(b':'):
                    self.parameters.append((b" ".join(params[i:]))[1:].decode(encoding))
                    break
                self.parameters.append(params[i].decode(encoding))
        except UnicodeDecodeError:
            #print("UnicodeDecodeError")
            if encoding.lower() != "latin-1":
                # Try latin-1 encoding if all else fails.
                self.decode("Latin-1")
            else:
                raise
        finally:
            self._buffer = buffer

    def encode(self, encoding="utf-8"):
        buffer = b""
        try:
            if self.tags is not None:
                buffer += b"@" + self.tags.encode(encoding) + b" "
            if self.source is not None:
                buffer += b":" + self.source.encode(encoding) + b" "
            buffer += self.command.encode(encoding) + b" "
            if self.parameters is not None:
                if len(self.parameters) > 1:
                    buffer += (" ".join(self.parameters[:-1])).encode(encoding) + b" "
                if len(self.parameters) > 0:
                    buffer += b":" + self.parameters[-1].encode(encoding)
            buffer += b"\r\n"
        except UnicodeEncodeError:
            #print("UnicodeEncodeError")
            if encoding.lower() != "latin-1":
                # Try latin-1 encoding if all else fails.
                self.encode("Latin-1")
            else:
                raise
        finally:
            self._buffer = buffer

    def __bytes__(self):
        return self._buffer

    def __str__(self):
        if self._buffer != b"" and self.command is None:
            self.decode()
        return f"Message(tags={self.tags}, source={self.source}, command={self.command}, parameters={self.parameters})"
