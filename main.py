from Connection.Server import Server

# Server information
SERVER = '82.76.255.62'  # 'irc.irchighway.net'
PORT = 6669

# User information
NICKNAME = "BooksWithJoe"

server = Server(SERVER, PORT)
server.connect(NICKNAME)

buffer = b""
while True:
    data = server.socket.receive(512)
    buffer += data
    lines = buffer.split(b"\r\n")
    buffer = lines.pop()

    for line in lines:
        if "PING" in line.decode("utf-8"):
            server.socket.send(b'PONG ' + line.split()[1] + b'\r\n')
        print(f"Received: {line!r}")
