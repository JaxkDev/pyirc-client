from Connection.Server import Server

# Server information
SERVER = 'bucharest.ro.eu.undernet.org'  #'irc.irchighway.net' # 'irc.freenode.net'
PORT = 6669

# User information
NICKNAME = "joefromfriends"

server = Server(SERVER, PORT, NICKNAME)
server.connect()

buffer = b""
while True:
    data = server._socket.receive(512)
    buffer += data
    lines = buffer.split(b"\r\n")
    buffer = lines.pop()

    for line in lines:
        if "PING" in line.decode("utf-8"):
            server._socket.send(b'PONG ' + line.split()[1] + b'\r\n')
        print(f"Received: {line.decode('utf-8')}")