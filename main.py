from Connection.Server import Server, Message

# Server information
SERVER = 'bucharest.ro.eu.undernet.org'  # 'bucharest.ro.eu.undernet.org'  #'irc.irchighway.net' # 'irc.freenode.net'
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
        message = Message(line)
        message.decode()
        server.log(f"Received: {str(message)}")
        params = " ".join(message.parameters[1:])
        if message.command.lower() == "notice":
            print(f"{message.command} | {params}")
        elif len(params) > 0:
            print(f"{params}")

        if message.command == "PING":
            reply = Message()
            reply.build("PONG", [message.parameters[0]])
            server.send(reply)
