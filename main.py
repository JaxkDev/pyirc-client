from App.Application import *
Application()
exit(0)

# Server information
SERVER = 'irc.irchighway.net'  # 'bucharest.ro.eu.undernet.org'  #'irc.irchighway.net' # 'irc.freenode.net'
PORT = 6669

# User information
NICKNAME = "joefromfriends"

from App.Connection.Server import Server, Message
server = Server(SERVER, PORT, NICKNAME)
server.connect()

buffer = b""
while True:
    data = server._socket.receive(2048)
    buffer += data
    lines = buffer.split(b"\r\n")
    buffer = lines.pop()

    for line in lines:
        message = Message(line)
        message.decode()
        server.log(f"Received: {str(message)}")
        # params = " ".join(message.parameters[1:])
        #if message.command.lower() == "notice":
        #    print(f"{message.command} | {params}")
        #elif len(params) > 0:
        #    print(f"{params}")

        print(str(message))
        #print(f"{message.command} | {message.parameters}")

        if message.command == "001":
            server.log("Connected to server")
            #server.send(Message().build("JOIN", ["#general"]))
            server.send(Message().build("JOIN", ["#ebooks"]))
            #server.send(Message().build("JOIN", ["#idle-rpg"]))

            #server.send(Message().build("PRIVMSG", ["#ebooks", "@search Robert Muchamore"]))
            server.send(Message().build("PRIVMSG", ["#ebooks", "!Dumbledore Helena Hunting - [Pucked 05] - Pucked Off (epub).epub"]))
            # DCC SEND <FILE> <IP> <PORT> <SIZE>
            # IP = socket.inet_ntoa(struct.pack('!L', <IP>))
        if message.command == "PING":
            server.send(Message().build("PONG", [message.parameters[0]]))
